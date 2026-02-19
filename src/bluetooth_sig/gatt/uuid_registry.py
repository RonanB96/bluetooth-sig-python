"""UUID registry loading from Bluetooth SIG YAML files."""

from __future__ import annotations

import contextlib
import logging
import threading

from bluetooth_sig.registry.gss import GssRegistry
from bluetooth_sig.registry.uuids.units import UnitsRegistry
from bluetooth_sig.types import CharacteristicInfo, ServiceInfo
from bluetooth_sig.types.base_types import SIGInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.registry.descriptor_types import DescriptorInfo
from bluetooth_sig.types.registry.gss_characteristic import GssCharacteristicSpec
from bluetooth_sig.types.uuid import BluetoothUUID

from ..registry.utils import find_bluetooth_sig_path, load_yaml_uuids, normalize_uuid_string
from ..types.registry import CharacteristicSpec, FieldInfo, UnitMetadata

__all__ = [
    "UuidRegistry",
    "uuid_registry",
]

logger = logging.getLogger(__name__)


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

        self._gss_registry: GssRegistry | None = None

        with contextlib.suppress(FileNotFoundError, Exception):
            # If YAML loading fails, continue with empty registry
            self._load_uuids()

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

        # Load GSS specifications
        self._gss_registry = GssRegistry.get_instance()
        self._load_gss_characteristic_info()

    def _load_gss_characteristic_info(self) -> None:
        """Load GSS specs and update characteristics with extracted info."""
        if self._gss_registry is None:
            return

        all_specs = self._gss_registry.get_all_specs()

        # Group by identifier to avoid duplicate processing
        processed_ids: set[str] = set()
        for spec in all_specs.values():
            if spec.identifier in processed_ids:
                continue
            processed_ids.add(spec.identifier)

            # Extract unit and value_type from structure
            char_data = {
                "structure": [
                    {
                        "field": f.field,
                        "type": f.type,
                        "size": f.size,
                        "description": f.description,
                    }
                    for f in spec.structure
                ]
            }
            unit, value_type = self._gss_registry.extract_info_from_gss(char_data)

            if unit or value_type:
                self._update_characteristic_with_gss_info(spec.name, spec.identifier, unit, value_type)

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

    def _convert_bluetooth_unit_to_readable(self, unit_spec: str) -> str:
        """Convert Bluetooth SIG unit specification to human-readable symbol.

        Args:
            unit_spec: Unit specification (e.g., "thermodynamic_temperature.degree_celsius")

        Returns:
            Human-readable symbol (e.g., "°C"), or unit_spec if no mapping found
        """
        unit_spec = unit_spec.rstrip(".").lower()
        unit_id = f"org.bluetooth.unit.{unit_spec}"

        units_registry = UnitsRegistry.get_instance()
        unit_info = units_registry.get_info(unit_id)
        if unit_info and unit_info.symbol:
            return unit_info.symbol

        return unit_spec

    def register_characteristic(  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
                    logger.warning("UUID normalization failed for service lookup: %s", search_key)

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
                    logger.warning("UUID normalization failed for characteristic lookup: %s", search_key)

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
                    logger.warning("UUID normalization failed for descriptor lookup: %s", search_key)

                # Check alias index (normalized to lowercase)
                alias_key = self._descriptor_aliases.get(search_key.lower())
                if alias_key and alias_key in self._descriptors:
                    return self._descriptors[alias_key]

            return None

    def get_gss_spec(self, identifier: str | BluetoothUUID) -> GssCharacteristicSpec | None:
        """Get the full GSS characteristic specification with all field metadata.

        This provides access to the complete YAML structure including all fields,
        their units, resolutions, ranges, and presence conditions.

        Args:
            identifier: Characteristic name, ID, or UUID

        Returns:
            GssCharacteristicSpec with full field structure, or None if not found

        Example::
            gss = uuid_registry.get_gss_spec("Location and Speed")
            if gss:
                for field in gss.structure:
                    print(f"{field.python_name}: unit={field.unit_id}, resolution={field.resolution}")

        """
        if self._gss_registry is None:
            return None

        with self._lock:
            # Try direct lookup by name or ID
            if isinstance(identifier, str):
                spec = self._gss_registry.get_spec(identifier)
                if spec:
                    return spec

                # Try to get CharacteristicInfo to find the ID
                char_info = self.get_characteristic_info(identifier)
                if char_info:
                    spec = self._gss_registry.get_spec(char_info.id)
                    if spec:
                        return spec
            elif isinstance(identifier, BluetoothUUID):
                # Look up by UUID
                char_info = self.get_characteristic_info(identifier)
                if char_info:
                    spec = self._gss_registry.get_spec(char_info.name)
                    if spec:
                        return spec
                    spec = self._gss_registry.get_spec(char_info.id)
                    if spec:
                        return spec

            return None

    def resolve_characteristic_spec(self, characteristic_name: str) -> CharacteristicSpec | None:  # pylint: disable=too-many-locals
        """Resolve characteristic specification with rich YAML metadata.

        This method provides detailed characteristic information including data types,
        field sizes, units, and descriptions by cross-referencing multiple YAML sources.

        Args:
            characteristic_name: Name of the characteristic (e.g., "Temperature", "Battery Level")

        Returns:
            CharacteristicSpec with full metadata, or None if not found

        Example::
            spec = uuid_registry.resolve_characteristic_spec("Temperature")
            if spec:
                print(f"UUID: {spec.uuid}, Unit: {spec.unit_symbol}, Type: {spec.data_type}")

        """
        with self._lock:
            # 1. Get UUID from characteristic registry
            char_info = self.get_characteristic_info(characteristic_name)
            if not char_info:
                return None

            # 2. Get typed GSS specification if available
            gss_spec = self.get_gss_spec(characteristic_name)

            # 3. Extract metadata from GSS specification
            data_type = None
            field_size = None
            unit_id = None
            unit_symbol = None
            base_unit = None
            resolution_text = None
            description = None

            if gss_spec:
                description = gss_spec.description

                # Only set data_type for single-field characteristics
                # Multi-field characteristics have complex structures and no single data type
                if len(gss_spec.structure) == 1:
                    # Use primary field for metadata extraction
                    primary = gss_spec.primary_field
                    if primary:
                        data_type = primary.type
                        field_size = str(primary.fixed_size) if primary.fixed_size else primary.size

                        # Use FieldSpec's unit_id property (auto-parsed from description)
                        if primary.unit_id:
                            unit_id = f"org.bluetooth.unit.{primary.unit_id}"
                            unit_symbol = self._convert_bluetooth_unit_to_readable(primary.unit_id)
                            base_unit = unit_id

                        # Get resolution from FieldSpec
                        if primary.resolution is not None:
                            resolution_text = f"Resolution: {primary.resolution}"

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
                structure=gss_spec.structure if gss_spec else [],
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
