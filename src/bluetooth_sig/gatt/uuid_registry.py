"""UUID registry loading from Bluetooth SIG YAML files."""

from __future__ import annotations

from bluetooth_sig.types.base_types import SIGInfo

__all__ = [
    "UuidRegistry",
    "uuid_registry",
    "CharacteristicSpec",
    "FieldInfo",
    "UnitMetadata",
]

import logging
import threading
from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.types import CharacteristicInfo, ServiceInfo
from bluetooth_sig.types.gatt_enums import DataType, ValueType
from bluetooth_sig.types.registry.descriptor_types import DescriptorInfo
from bluetooth_sig.types.uuid import BluetoothUUID

from ..registry.utils import find_bluetooth_sig_path, load_yaml_uuids, normalize_uuid_string
from ..types.registry import CharacteristicSpec, FieldInfo, UnitMetadata


class UuidRegistry:  # pylint: disable=too-many-instance-attributes
    """Registry for Bluetooth SIG UUIDs with canonical storage + alias indices.

    This registry stores a number of internal caches and mappings which
    legitimately exceed the default pylint instance attribute limit. The
    complexity is intentional and centralised; an inline disable is used to
    avoid noisy global configuration changes.
    """

    def __init__(self) -> None:
        """Initialize the UUID registry."""
        self._lock = threading.RLock()

        # Canonical storage: normalized_uuid -> domain types (single source of truth)
        self._services: dict[str, ServiceInfo] = {}
        self._characteristics: dict[str, CharacteristicInfo] = {}
        self._descriptors: dict[str, DescriptorInfo] = {}

        # Lightweight alias indices: alias -> normalized_uuid
        self._service_aliases: dict[str, str] = {}
        self._characteristic_aliases: dict[str, str] = {}
        self._descriptor_aliases: dict[str, str] = {}

        # Preserve SIG entries overridden at runtime so we can restore them
        self._service_overrides: dict[str, ServiceInfo] = {}
        self._characteristic_overrides: dict[str, CharacteristicInfo] = {}
        self._descriptor_overrides: dict[str, DescriptorInfo] = {}

        # Track runtime-registered UUIDs (replaces origin field checks)
        self._runtime_uuids: set[str] = set()

        # Unit mappings
        self._unit_mappings: dict[str, str] = {}

        # GSS specifications storage (for resolve_characteristic_spec)
        self._gss_specs: dict[str, dict[str, Any]] = {}

        try:
            self._load_uuids()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _store_service(self, info: ServiceInfo) -> None:
        """Store service info with canonical storage + aliases."""
        canonical_key = info.uuid.normalized

        # Store once in canonical location
        self._services[canonical_key] = info

        # Create lightweight alias mappings (normalized to lowercase)
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._service_aliases[alias.lower()] = canonical_key

    def _store_characteristic(self, info: CharacteristicInfo) -> None:
        """Store characteristic info with canonical storage + aliases."""
        canonical_key = info.uuid.normalized

        # Store once in canonical location
        self._characteristics[canonical_key] = info

        # Create lightweight alias mappings (normalized to lowercase)
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._characteristic_aliases[alias.lower()] = canonical_key

    def _store_descriptor(self, info: DescriptorInfo) -> None:
        """Store descriptor info with canonical storage + aliases."""
        canonical_key = info.uuid.normalized

        # Store once in canonical location
        self._descriptors[canonical_key] = info

        # Create lightweight alias mappings (normalized to lowercase)
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._descriptor_aliases[alias.lower()] = canonical_key

    def _generate_aliases(self, info: SIGInfo) -> set[str]:
        """Generate name/ID-based alias keys for domain info types (UUID variations handled by BluetoothUUID)."""
        aliases: set[str] = {
            info.name.lower(),
        }

        if info.id:
            aliases.add(info.id)

        if info.id and "service" in info.id:
            service_name = info.id.replace("org.bluetooth.service.", "")
            if service_name.endswith("_service"):
                service_name = service_name[:-8]  # Remove _service
            service_name = service_name.replace("_", " ").title()
            aliases.add(service_name)
            # Also add "Service" suffix if not present
            if not service_name.endswith(" Service"):
                aliases.add(service_name + " Service")
        elif info.id and "characteristic" in info.id:
            char_name = info.id.replace("org.bluetooth.characteristic.", "")
            char_name = char_name.replace("_", " ").title()
            aliases.add(char_name)

        # Add space-separated words from name
        name_words = info.name.replace("_", " ").replace("-", " ")
        if " " in name_words:
            aliases.add(name_words.title())
            aliases.add(name_words.lower())

        # Remove empty strings, None values, and the canonical key itself
        canonical_key = info.uuid.normalized
        return {alias for alias in aliases if alias and alias.strip() and alias != canonical_key}

    def _load_uuids(self) -> None:  # pylint: disable=too-many-branches
        """Load all UUIDs from YAML files."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load service UUIDs
        service_yaml = base_path / "service_uuids.yaml"
        if service_yaml.exists():
            for uuid_info in load_yaml_uuids(service_yaml):
                uuid = normalize_uuid_string(uuid_info["uuid"])

                bt_uuid = BluetoothUUID(uuid)
                info = ServiceInfo(
                    uuid=bt_uuid,
                    name=uuid_info["name"],
                    id=uuid_info.get("id", ""),
                )
                self._store_service(info)

        # Load characteristic UUIDs
        characteristic_yaml = base_path / "characteristic_uuids.yaml"
        if characteristic_yaml.exists():
            for uuid_info in load_yaml_uuids(characteristic_yaml):
                uuid = normalize_uuid_string(uuid_info["uuid"])

                bt_uuid = BluetoothUUID(uuid)
                char_info = CharacteristicInfo(
                    uuid=bt_uuid,
                    name=uuid_info["name"],
                    id=uuid_info.get("id", ""),
                    unit="",  # Will be set from unit mappings if available
                    value_type=ValueType.UNKNOWN,
                )
                self._store_characteristic(char_info)

        # Load descriptor UUIDs
        descriptor_yaml = base_path / "descriptors.yaml"
        if descriptor_yaml.exists():
            for uuid_info in load_yaml_uuids(descriptor_yaml):
                uuid = normalize_uuid_string(uuid_info["uuid"])

                bt_uuid = BluetoothUUID(uuid)
                desc_info = DescriptorInfo(
                    uuid=bt_uuid,
                    name=uuid_info["name"],
                    id=uuid_info.get("id", ""),
                )
                self._store_descriptor(desc_info)

        # Load unit mappings and GSS specifications
        self._load_unit_mappings(base_path)
        self._load_gss_specifications()

    def _load_unit_mappings(self, base_path: Path) -> None:
        """Load unit symbol mappings from units.yaml file."""
        units_yaml = base_path / "units.yaml"
        if not units_yaml.exists():
            return

        try:
            units_data = load_yaml_uuids(units_yaml)
            for unit_info in units_data:
                unit_id = unit_info.get("id", "")
                unit_name = unit_info.get("name", "")

                if not unit_id or not unit_name:
                    continue

                unit_symbol = self._extract_unit_symbol_from_name(unit_name)
                if unit_symbol:
                    unit_key = unit_id.replace("org.bluetooth.unit.", "").lower()
                    self._unit_mappings[unit_key] = unit_symbol

        except (msgspec.DecodeError, OSError, KeyError):
            pass

    def _extract_unit_symbol_from_name(self, unit_name: str) -> str:
        """Extract unit symbol from unit name.

        Args:
            unit_name: The unit name from units.yaml (e.g., "pressure (pascal)")

        Returns:
            Unit symbol string (e.g., "Pa"), or empty string if no symbol can be extracted

        """
        # Handle common unit names that map to symbols
        unit_symbol_map = {
            "percentage": "%",
            "per mille": "‰",
            "unitless": "",
        }

        if unit_name.lower() in unit_symbol_map:
            return unit_symbol_map[unit_name.lower()]

        # Extract symbol from parentheses if present
        if "(" in unit_name and ")" in unit_name:
            start = unit_name.find("(") + 1
            end = unit_name.find(")", start)
            if 0 < start < end:
                symbol_candidate = unit_name[start:end].strip()

                # Map common symbols
                symbol_mapping = {
                    "degree celsius": "°C",
                    "degree fahrenheit": "°F",
                    "kelvin": "K",
                    "pascal": "Pa",
                    "bar": "bar",
                    "millimetre of mercury": "mmHg",
                    "ampere": "A",
                    "volt": "V",
                    "joule": "J",
                    "watt": "W",
                    "hertz": "Hz",
                    "metre": "m",
                    "kilogram": "kg",
                    "second": "s",
                    "metre per second": "m/s",
                    "metre per second squared": "m/s²",
                    "radian per second": "rad/s",
                    "candela": "cd",
                    "lux": "lux",
                    "newton": "N",
                    "coulomb": "C",
                    "farad": "F",
                    "ohm": "Ω",
                    "siemens": "S",
                    "weber": "Wb",
                    "tesla": "T",
                    "henry": "H",
                    "lumen": "lm",
                    "becquerel": "Bq",
                    "gray": "Gy",
                    "sievert": "Sv",
                    "katal": "kat",
                    "degree": "°",
                    "radian": "rad",
                    "steradian": "sr",
                }

                return symbol_mapping.get(symbol_candidate.lower(), symbol_candidate)

        # For units without parentheses, try to map common ones
        common_units = {
            "frequency": "Hz",
            "force": "N",
            "pressure": "Pa",
            "energy": "J",
            "power": "W",
            "mass": "kg",
            "length": "m",
            "time": "s",
        }

        for unit_type, symbol in common_units.items():
            if unit_name.lower().startswith(unit_type):
                return symbol

        # Handle thermodynamic temperature specially (from yaml_cross_reference)
        if "celsius temperature" in unit_name.lower():
            return "°C"
        if "fahrenheit temperature" in unit_name.lower():
            return "°F"

        # Return empty string if no symbol can be extracted (API compatibility)
        return ""

    def _load_gss_specifications(self) -> None:
        """Load detailed specifications from GSS YAML files."""
        gss_path = self._find_gss_path()
        if not gss_path:
            return

        for yaml_file in gss_path.glob("org.bluetooth.characteristic.*.yaml"):
            self._process_gss_file(yaml_file)

    def _find_gss_path(self) -> Path | None:
        """Find the GSS specifications directory."""
        project_root = Path(__file__).parent.parent.parent.parent
        gss_path = project_root / "bluetooth_sig" / "gss"

        if gss_path.exists():
            return gss_path

        pkg_root = Path(__file__).parent.parent
        gss_path = pkg_root / "bluetooth_sig" / "gss"

        return gss_path if gss_path.exists() else None

    def _process_gss_file(self, yaml_file: Path) -> None:
        """Process a single GSS YAML file."""
        try:
            with yaml_file.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "characteristic" not in data:
                return

            char_data = data["characteristic"]
            char_name = char_data.get("name")
            char_id = char_data.get("identifier")

            if not char_name or not char_id:
                return

            # Store full GSS spec for resolve_characteristic_spec method
            # Store by both ID and name for lookup flexibility
            if char_id:
                self._gss_specs[char_id] = char_data
            if char_name:
                self._gss_specs[char_name] = char_data

            unit, value_type = self._extract_info_from_gss(char_data)

            if unit or value_type:
                self._update_characteristic_with_gss_info(char_name, char_id, unit, value_type)

        except (msgspec.DecodeError, OSError, KeyError) as e:
            logging.warning("Failed to parse GSS YAML file %s: %s", yaml_file, e)

    def _update_characteristic_with_gss_info(
        self, char_name: str, char_id: str, unit: str | None, value_type: str | None
    ) -> None:
        """Update existing characteristic with GSS info."""
        with self._lock:
            # Find the canonical entry by checking aliases (normalized to lowercase)
            canonical_uuid = None
            for search_key in [char_name, char_id]:
                canonical_uuid = self._characteristic_aliases.get(search_key.lower())
                if canonical_uuid:
                    break

            if not canonical_uuid or canonical_uuid not in self._characteristics:
                return

            # Get existing info and create updated version
            existing_info = self._characteristics[canonical_uuid]

            # Convert value_type string to ValueType enum if provided
            new_value_type = existing_info.value_type
            if value_type:
                try:
                    new_value_type = ValueType(value_type)
                except (ValueError, KeyError):
                    new_value_type = existing_info.value_type

            # Create updated CharacteristicInfo (immutable, so create new instance)
            updated_info = CharacteristicInfo(
                uuid=existing_info.uuid,
                name=existing_info.name,
                id=existing_info.id,
                unit=unit or existing_info.unit,
                value_type=new_value_type,
            )

            # Update canonical store (aliases remain the same since UUID/name/id unchanged)
            self._characteristics[canonical_uuid] = updated_info

    def _extract_info_from_gss(self, char_data: dict[str, Any]) -> tuple[str | None, str | None]:
        """Extract unit and value_type from GSS characteristic structure."""
        structure = char_data.get("structure", [])
        if not isinstance(structure, list) or not structure:
            return None, None

        typed_structure: list[dict[str, Any]] = []
        for raw_field in structure:
            if isinstance(raw_field, dict):
                typed_structure.append(cast(dict[str, Any], raw_field))

        if not typed_structure:
            return None, None

        unit = None
        value_type = None

        for field in typed_structure:
            field_dict: dict[str, Any] = field

            if not value_type and isinstance(field_dict.get("type"), str):
                yaml_type_value = cast(str, field_dict["type"])
                value_type = self._convert_yaml_type_to_python_type(yaml_type_value)

            description_value = field_dict.get("description", "")
            if not isinstance(description_value, str):
                continue

            # Extract unit from either "Base Unit:" or "Unit:" format
            if not unit and ("Base Unit:" in description_value or "Unit:" in description_value):
                unit = self._extract_unit_from_description(description_value)

        return unit, value_type

    def _extract_unit_from_description(self, description: str) -> str | None:
        """Extract unit symbol from GSS field description.

        Handles both "Base Unit:" (unit on next line) and "Unit:" (inline) formats.
        Strips all spaces from unit IDs to handle YAML formatting issues.

        Args:
            description: Field description text from GSS YAML

        Returns:
            Human-readable unit symbol, or None if no unit found
        """
        unit_id, _ = self._extract_unit_id_and_line(description)
        if unit_id:
            return self._convert_bluetooth_unit_to_readable(unit_id)
        return None

    def _extract_unit_id_and_line(self, description: str) -> tuple[str | None, str | None]:
        """Extract raw unit ID and line from GSS field description.

        Handles both "Base Unit:" (unit on next line) and "Unit:" (inline) formats.
        Strips all spaces from unit IDs to handle YAML formatting issues.

        Args:
            description: Field description text from GSS YAML

        Returns:
            Tuple of (unit_id without org.bluetooth.unit prefix, full unit line with spaces removed)
            Returns (None, None) if no unit found
        """
        unit_line = None

        if "Base Unit:" in description:
            # Format: "Base Unit:\norg.bluetooth.unit.xxx" or "Base Unit: org.bluetooth.unit.xxx"
            parts = description.split("Base Unit:")[1].split("\n")
            unit_line = parts[0].strip()
            if not unit_line and len(parts) > 1:  # Unit is on next line
                unit_line = parts[1].strip()
        elif "Unit:" in description:
            # Format: "Unit: org.bluetooth.unit.xxx" (inline)
            unit_line = description.split("Unit:")[1].split("\n")[0].strip()

        if unit_line and "org.bluetooth.unit." in unit_line:
            # Remove all spaces (handles YAML formatting issues like "org.bluetooth.unit. electrical_...")
            cleaned_line = unit_line.replace(" ", "")
            unit_spec = cleaned_line.split("org.bluetooth.unit.")[1].strip()
            return unit_spec, cleaned_line

        return None, None

    def _convert_yaml_type_to_python_type(self, yaml_type: str) -> str:
        """Convert YAML type to Python type string."""
        return DataType.from_string(yaml_type).to_python_type()

    def _convert_bluetooth_unit_to_readable(self, unit_spec: str) -> str:
        """Convert Bluetooth SIG unit specification to human-readable format."""
        unit_spec = unit_spec.rstrip(".").lower()
        return self._unit_mappings.get(unit_spec, unit_spec)

    def register_characteristic(
        self,
        uuid: BluetoothUUID,
        name: str,
        identifier: str | None = None,
        unit: str | None = None,
        value_type: ValueType | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom characteristic at runtime.

        Args:
            uuid: The Bluetooth UUID for the characteristic
            name: Human-readable name
            identifier: Optional identifier (auto-generated if not provided)
            unit: Optional unit of measurement
            value_type: Optional value type
            override: If True, allow overriding existing entries
        """
        with self._lock:
            canonical_key = uuid.normalized

            # Check for conflicts with existing entries
            if canonical_key in self._characteristics:
                # Check if it's a SIG characteristic (not in runtime set)
                if canonical_key not in self._runtime_uuids:
                    if not override:
                        raise ValueError(
                            f"UUID {uuid} conflicts with existing SIG "
                            "characteristic entry. Use override=True to replace."
                        )
                    # Preserve original SIG entry for restoration
                    self._characteristic_overrides.setdefault(canonical_key, self._characteristics[canonical_key])
                elif not override:
                    # Runtime entry already exists
                    raise ValueError(
                        f"UUID {uuid} already registered as runtime characteristic. Use override=True to replace."
                    )

            info = CharacteristicInfo(
                uuid=uuid,
                name=name,
                id=identifier or f"runtime.characteristic.{name.lower().replace(' ', '_')}",
                unit=unit or "",
                value_type=value_type or ValueType.UNKNOWN,
            )

            # Track as runtime-registered UUID
            self._runtime_uuids.add(canonical_key)

            self._store_characteristic(info)

    def register_service(
        self,
        uuid: BluetoothUUID,
        name: str,
        identifier: str | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom service at runtime.

        Args:
            uuid: The Bluetooth UUID for the service
            name: Human-readable name
            identifier: Optional identifier (auto-generated if not provided)
            override: If True, allow overriding existing entries
        """
        with self._lock:
            canonical_key = uuid.normalized

            # Check for conflicts with existing entries
            if canonical_key in self._services:
                # Check if it's a SIG service (not in runtime set)
                if canonical_key not in self._runtime_uuids:
                    if not override:
                        raise ValueError(
                            f"UUID {uuid} conflicts with existing SIG service entry. Use override=True to replace."
                        )
                    # Preserve original SIG entry for restoration
                    self._service_overrides.setdefault(canonical_key, self._services[canonical_key])
                elif not override:
                    # Runtime entry already exists
                    raise ValueError(
                        f"UUID {uuid} already registered as runtime service. Use override=True to replace."
                    )

            info = ServiceInfo(
                uuid=uuid,
                name=name,
                id=identifier or f"runtime.service.{name.lower().replace(' ', '_')}",
            )

            # Track as runtime-registered UUID
            self._runtime_uuids.add(canonical_key)

            self._store_service(info)

    def get_service_info(self, key: str | BluetoothUUID) -> ServiceInfo | None:
        """Get information about a service by UUID, name, or ID."""
        with self._lock:
            # Convert BluetoothUUID to canonical key
            if isinstance(key, BluetoothUUID):
                canonical_key = key.normalized
                # Direct canonical lookup
                if canonical_key in self._services:
                    return self._services[canonical_key]
            else:
                search_key = str(key).strip()

                # Try UUID normalization first
                try:
                    bt_uuid = BluetoothUUID(search_key)
                    canonical_key = bt_uuid.normalized
                    if canonical_key in self._services:
                        return self._services[canonical_key]
                except ValueError:
                    pass

                # Check alias index (normalized to lowercase)
                alias_key = self._service_aliases.get(search_key.lower())
                if alias_key and alias_key in self._services:
                    return self._services[alias_key]

            return None

    def get_characteristic_info(self, identifier: str | BluetoothUUID) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID, name, or ID."""
        with self._lock:
            # Convert BluetoothUUID to canonical key
            if isinstance(identifier, BluetoothUUID):
                canonical_key = identifier.normalized
                # Direct canonical lookup
                if canonical_key in self._characteristics:
                    return self._characteristics[canonical_key]
            else:
                search_key = str(identifier).strip()

                # Try UUID normalization first
                try:
                    bt_uuid = BluetoothUUID(search_key)
                    canonical_key = bt_uuid.normalized
                    if canonical_key in self._characteristics:
                        return self._characteristics[canonical_key]
                except ValueError:
                    pass

                # Check alias index (normalized to lowercase)
                alias_key = self._characteristic_aliases.get(search_key.lower())
                if alias_key and alias_key in self._characteristics:
                    return self._characteristics[alias_key]

            return None

    def get_descriptor_info(self, identifier: str | BluetoothUUID) -> DescriptorInfo | None:
        """Get information about a descriptor by UUID, name, or ID."""
        with self._lock:
            # Convert BluetoothUUID to canonical key
            if isinstance(identifier, BluetoothUUID):
                canonical_key = identifier.normalized
                # Direct canonical lookup
                if canonical_key in self._descriptors:
                    return self._descriptors[canonical_key]
            else:
                search_key = str(identifier).strip()

                # Try UUID normalization first
                try:
                    bt_uuid = BluetoothUUID(search_key)
                    canonical_key = bt_uuid.normalized
                    if canonical_key in self._descriptors:
                        return self._descriptors[canonical_key]
                except ValueError:
                    pass

                # Check alias index (normalized to lowercase)
                alias_key = self._descriptor_aliases.get(search_key.lower())
                if alias_key and alias_key in self._descriptors:
                    return self._descriptors[alias_key]

            return None

    def resolve_characteristic_spec(self, characteristic_name: str) -> CharacteristicSpec | None:  # pylint: disable=too-many-locals
        """Resolve characteristic specification with rich YAML metadata.

        This method provides detailed characteristic information including data types,
        field sizes, units, and descriptions by cross-referencing multiple YAML sources.

        Args:
            characteristic_name: Name of the characteristic (e.g., "Temperature", "Battery Level")

        Returns:
            CharacteristicSpec with full metadata, or None if not found

        Example:
            spec = uuid_registry.resolve_characteristic_spec("Temperature")
            if spec:
                print(f"UUID: {spec.uuid}, Unit: {spec.unit_symbol}, Type: {spec.data_type}")

        """
        with self._lock:
            # 1. Get UUID from characteristic registry
            char_info = self.get_characteristic_info(characteristic_name)
            if not char_info:
                return None

            # 2. Get GSS specification if available
            gss_spec = None
            for search_key in [characteristic_name, char_info.id]:
                # Load GSS specs on-demand (already loaded in __init__)
                if hasattr(self, "_gss_specs"):
                    gss_spec = getattr(self, "_gss_specs", {}).get(search_key)
                    if gss_spec:
                        break

            # 3. Extract metadata from GSS specification
            data_type = None
            field_size = None
            unit_id = None
            unit_symbol = None
            base_unit = None
            resolution_text = None
            description = None

            if gss_spec:
                description = gss_spec.get("description", "")
                structure = gss_spec.get("structure", [])

                if structure and len(structure) > 0:
                    first_field = structure[0]
                    data_type = first_field.get("type")
                    field_size = first_field.get("size")
                    field_description = first_field.get("description", "")

                    # Extract unit from description using helper method
                    if "Base Unit:" in field_description or "Unit:" in field_description:
                        unit_spec, base_unit = self._extract_unit_id_and_line(field_description)
                        if unit_spec:
                            unit_symbol = self._convert_bluetooth_unit_to_readable(unit_spec)
                            unit_id = base_unit

                    # Extract resolution information
                    if "resolution of" in field_description.lower():
                        resolution_text = field_description

            # 4. Use existing unit/value_type from CharacteristicInfo if GSS didn't provide them
            if not unit_symbol and char_info.unit:
                unit_symbol = char_info.unit

            return CharacteristicSpec(
                uuid=char_info.uuid,
                name=char_info.name,
                field_info=FieldInfo(data_type=data_type, field_size=field_size),
                unit_info=UnitMetadata(
                    unit_id=unit_id,
                    unit_symbol=unit_symbol,
                    base_unit=base_unit,
                    resolution_text=resolution_text,
                ),
                description=description,
            )

    def get_signed_from_data_type(self, data_type: str | None) -> bool:
        """Determine if data type is signed from GSS data type.

        Args:
            data_type: GSS data type string (e.g., "sint16", "float32", "uint8")

        Returns:
            True if the type represents signed values, False otherwise

        """
        if not data_type:
            return False
        # Comprehensive signed type detection
        signed_types = {"float32", "float64", "medfloat16", "medfloat32"}
        return data_type.startswith("sint") or data_type in signed_types

    @staticmethod
    def get_byte_order_hint() -> str:
        """Get byte order hint for Bluetooth SIG specifications.

        Returns:
            "little" - Bluetooth SIG uses little-endian by convention

        """
        return "little"

    def clear_custom_registrations(self) -> None:
        """Clear all custom registrations (for testing)."""
        with self._lock:
            # Use runtime_uuids set to identify what to remove
            runtime_keys = list(self._runtime_uuids)

            # Remove runtime entries from canonical stores
            for key in runtime_keys:
                self._services.pop(key, None)
                self._characteristics.pop(key, None)
                self._descriptors.pop(key, None)

            # Remove corresponding aliases (alias -> canonical_key where canonical_key is runtime)
            runtime_service_aliases = [
                alias for alias, canonical in self._service_aliases.items() if canonical in runtime_keys
            ]
            runtime_char_aliases = [
                alias for alias, canonical in self._characteristic_aliases.items() if canonical in runtime_keys
            ]
            runtime_desc_aliases = [
                alias for alias, canonical in self._descriptor_aliases.items() if canonical in runtime_keys
            ]

            for alias in runtime_service_aliases:
                del self._service_aliases[alias]
            for alias in runtime_char_aliases:
                del self._characteristic_aliases[alias]
            for alias in runtime_desc_aliases:
                del self._descriptor_aliases[alias]

            # Restore any preserved SIG entries that were overridden
            for key in runtime_keys:
                original = self._service_overrides.pop(key, None)
                if original is not None:
                    self._store_service(original)
                original = self._characteristic_overrides.pop(key, None)
                if original is not None:
                    self._store_characteristic(original)
                original = self._descriptor_overrides.pop(key, None)
                if original is not None:
                    self._store_descriptor(original)

            # Clear the runtime tracking set
            self._runtime_uuids.clear()


# Global instance
uuid_registry = UuidRegistry()
