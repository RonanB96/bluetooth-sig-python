"""UUID registry loading from Bluetooth SIG YAML files."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

import yaml

from bluetooth_sig.types.uuid import BluetoothUUID


class UuidOrigin(Enum):
    """Origin of UUID information."""

    BLUETOOTH_SIG = "bluetooth_sig"
    RUNTIME = "runtime"


@dataclass(frozen=True)
class UuidInfo:
    """Information about a UUID."""

    uuid: BluetoothUUID
    name: str
    id: str
    summary: str = ""
    unit: str | None = None
    value_type: str | None = None
    origin: UuidOrigin = UuidOrigin.BLUETOOTH_SIG


@dataclass(frozen=True)
class CustomUuidEntry:
    """Entry for custom UUID registration."""

    uuid: BluetoothUUID
    name: str
    id: str | None = None
    summary: str | None = None
    unit: str | None = None
    value_type: str | None = None


class UuidRegistry:
    """Registry for Bluetooth SIG UUIDs with canonical storage + alias indices."""

    def __init__(self) -> None:
        """Initialize the UUID registry."""
        self._lock = threading.RLock()

        # Canonical storage: normalized_uuid -> UuidInfo (single source of truth)
        self._services: dict[str, UuidInfo] = {}
        self._characteristics: dict[str, UuidInfo] = {}

        # Lightweight alias indices: alias -> normalized_uuid
        self._service_aliases: dict[str, str] = {}
        self._characteristic_aliases: dict[str, str] = {}

        # Preserve SIG entries overridden at runtime so we can restore them
        self._service_overrides: dict[str, UuidInfo] = {}
        self._characteristic_overrides: dict[str, UuidInfo] = {}

        # Unit mappings
        self._unit_mappings: dict[str, str] = {}

        try:
            self._load_uuids()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _store_service(self, info: UuidInfo) -> None:
        """Store service info with canonical storage + aliases."""
        canonical_key = info.uuid.normalized

        # Store once in canonical location
        self._services[canonical_key] = info

        # Create lightweight alias mappings (normalized to lowercase)
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._service_aliases[alias.lower()] = canonical_key

    def _store_characteristic(self, info: UuidInfo) -> None:
        """Store characteristic info with canonical storage + aliases."""
        canonical_key = info.uuid.normalized

        # Store once in canonical location
        self._characteristics[canonical_key] = info

        # Create lightweight alias mappings (normalized to lowercase)
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._characteristic_aliases[alias.lower()] = canonical_key

    def _generate_aliases(self, info: UuidInfo) -> set[str]:
        """Generate name/ID-based alias keys for a UuidInfo (UUID variations handled by BluetoothUUID)."""
        aliases: set[str] = {
            # Name variations
            info.name.lower(),  # Lowercase name
            info.id,  # Full ID
        }

        # Add service/characteristic-specific name variations
        if "service" in info.id:
            service_name = info.id.replace("org.bluetooth.service.", "")
            if service_name.endswith("_service"):
                service_name = service_name[:-8]  # Remove _service
            service_name = service_name.replace("_", " ").title()
            aliases.add(service_name)
        elif "characteristic" in info.id:
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

    def _load_yaml(self, file_path: Path) -> list[dict[str, Any]]:
        """Load UUID entries from a YAML file."""
        if not file_path.exists():
            return []

        with file_path.open("r", encoding="utf-8") as file_handle:
            data = yaml.safe_load(file_handle)

        if not isinstance(data, dict):
            return []

        data_dict = cast(dict[str, Any], data)
        uuid_entries = data_dict.get("uuids")
        if not isinstance(uuid_entries, list):
            return []

        typed_entries: list[dict[str, Any]] = []
        for entry in uuid_entries:
            if isinstance(entry, dict):
                typed_entries.append(cast(dict[str, Any], entry))

        return typed_entries

    def _load_uuids(self) -> None:
        """Load all UUIDs from YAML files."""
        # Try development location first (git submodule)
        project_root = Path(__file__).parent.parent.parent.parent
        base_path = project_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

        if not base_path.exists():
            # Try installed package location
            pkg_root = Path(__file__).parent.parent
            base_path = pkg_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

        if not base_path.exists():
            return

        # Load service UUIDs
        service_yaml = base_path / "service_uuids.yaml"
        if service_yaml.exists():
            for uuid_info in self._load_yaml(service_yaml):
                uuid = uuid_info["uuid"]
                if isinstance(uuid, str):
                    uuid = uuid.replace("0x", "")
                else:
                    uuid = hex(uuid)[2:].upper()

                bt_uuid = BluetoothUUID(uuid)
                info = UuidInfo(
                    uuid=bt_uuid, name=uuid_info["name"], id=uuid_info["id"], origin=UuidOrigin.BLUETOOTH_SIG
                )
                self._store_service(info)

        # Load characteristic UUIDs
        characteristic_yaml = base_path / "characteristic_uuids.yaml"
        if characteristic_yaml.exists():
            for uuid_info in self._load_yaml(characteristic_yaml):
                uuid = uuid_info["uuid"]
                if isinstance(uuid, str):
                    uuid = uuid.replace("0x", "")
                else:
                    uuid = hex(uuid)[2:].upper()

                bt_uuid = BluetoothUUID(uuid)
                info = UuidInfo(
                    uuid=bt_uuid, name=uuid_info["name"], id=uuid_info["id"], origin=UuidOrigin.BLUETOOTH_SIG
                )
                self._store_characteristic(info)

        # Load unit mappings and GSS specifications
        self._load_unit_mappings(base_path)
        self._load_gss_specifications()

    def _load_unit_mappings(self, base_path: Path) -> None:
        """Load unit symbol mappings from units.yaml file."""
        units_yaml = base_path / "units.yaml"
        if not units_yaml.exists():
            return

        try:
            units_data = self._load_yaml(units_yaml)
            for unit_info in units_data:
                unit_id = unit_info.get("id", "")
                unit_name = unit_info.get("name", "")

                if not unit_id or not unit_name:
                    continue

                unit_symbol = self._extract_unit_symbol_from_name(unit_name)
                if unit_symbol:
                    unit_key = unit_id.replace("org.bluetooth.unit.", "").lower()
                    self._unit_mappings[unit_key] = unit_symbol

        except (yaml.YAMLError, OSError, KeyError):
            pass

    # pylint: disable=duplicate-code
    # NOTE: Unit symbol extraction logic is shared with YAMLCrossReferenceSystem._extract_unit_symbol_from_name.
    # Both need to parse Bluetooth SIG unit specifications identically. Consolidation would require shared utility
    # module, but these are in different architectural layers (GATT registry vs YAML cross-reference system).
    # TODO: Consider extracting to shared bluetooth_sig.registry.unit_utils module if more duplication emerges.
    def _extract_unit_symbol_from_name(self, unit_name: str) -> str | None:
        """Extract unit symbol from unit name."""
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

        return unit_name

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
                data = yaml.safe_load(f)

            if not data or "characteristic" not in data:
                return

            char_data = data["characteristic"]
            char_name = char_data.get("name")
            char_id = char_data.get("identifier")

            if not char_name or not char_id:
                return

            unit, value_type = self._extract_info_from_gss(char_data)

            if unit or value_type:
                self._update_characteristic_with_gss_info(char_name, char_id, unit, value_type)

        except (yaml.YAMLError, OSError, KeyError) as e:
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
            updated_info = UuidInfo(
                uuid=existing_info.uuid,
                name=existing_info.name,
                id=existing_info.id,
                summary=existing_info.summary,
                unit=unit or existing_info.unit,
                value_type=value_type or existing_info.value_type,
                origin=existing_info.origin,
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

            if "Base Unit:" in description_value and not unit:
                unit_line = None
                for line in description_value.split("\n"):
                    if "Base Unit:" in line:
                        unit_line = line.strip()
                        break

                if unit_line and "org.bluetooth.unit." in unit_line:
                    unit_spec = unit_line.split("org.bluetooth.unit.")[1].strip()
                    unit = self._convert_bluetooth_unit_to_readable(unit_spec)

        return unit, value_type

    def _convert_yaml_type_to_python_type(self, yaml_type: str) -> str:
        """Convert YAML type to Python type string."""
        type_mapping = {
            # Integer types
            "uint8": "int",
            "uint16": "int",
            "uint24": "int",
            "uint32": "int",
            "uint64": "int",
            "sint8": "int",
            "sint16": "int",
            "sint24": "int",
            "sint32": "int",
            "sint64": "int",
            # Float types
            "float32": "float",
            "float64": "float",
            "sfloat": "float",
            "float": "float",
            "medfloat16": "float",
            # String types
            "utf8s": "string",
            "utf16s": "string",
            # Boolean type
            "boolean": "boolean",
            # Struct/opaque data
            "struct": "bytes",
            "variable": "bytes",
        }
        return type_mapping.get(yaml_type.lower(), "bytes")

    def _convert_bluetooth_unit_to_readable(self, unit_spec: str) -> str:
        """Convert Bluetooth SIG unit specification to human-readable format."""
        unit_spec = unit_spec.rstrip(".").lower()
        return self._unit_mappings.get(unit_spec, unit_spec)

    def register_characteristic(
        self,
        entry: CustomUuidEntry,
        override: bool = False,
    ) -> None:
        """Register a custom characteristic at runtime."""
        with self._lock:
            canonical_key = entry.uuid.normalized

            # Check for conflicts with existing entries
            if canonical_key in self._characteristics:
                existing = self._characteristics[canonical_key]
                if existing.origin == UuidOrigin.BLUETOOTH_SIG:
                    if not override:
                        raise ValueError(
                            f"UUID {entry.uuid} conflicts with existing SIG "
                            "characteristic entry. Use override=True to replace."
                        )
                    # Preserve original SIG entry for restoration
                    self._characteristic_overrides.setdefault(canonical_key, existing)
                elif existing.origin == UuidOrigin.RUNTIME and not override:
                    raise ValueError(
                        f"UUID {entry.uuid} already registered as runtime characteristic. Use override=True to replace."
                    )

            info = UuidInfo(
                uuid=entry.uuid,
                name=entry.name,
                id=entry.id or f"runtime.characteristic.{entry.name.lower().replace(' ', '_')}",
                summary=entry.summary or "",
                unit=entry.unit,
                value_type=entry.value_type,
                origin=UuidOrigin.RUNTIME,
            )

            self._store_characteristic(info)

    def register_service(self, entry: CustomUuidEntry, override: bool = False) -> None:
        """Register a custom service at runtime."""
        with self._lock:
            canonical_key = entry.uuid.normalized

            # Check for conflicts with existing entries
            if canonical_key in self._services:
                existing = self._services[canonical_key]
                if existing.origin == UuidOrigin.BLUETOOTH_SIG:
                    if not override:
                        raise ValueError(
                            f"UUID {entry.uuid} conflicts with existing SIG service entry. "
                            "Use override=True to replace."
                        )
                    # Preserve original SIG entry for restoration
                    self._service_overrides.setdefault(canonical_key, existing)
                elif existing.origin == UuidOrigin.RUNTIME and not override:
                    raise ValueError(
                        f"UUID {entry.uuid} already registered as runtime service. Use override=True to replace."
                    )

            info = UuidInfo(
                uuid=entry.uuid,
                name=entry.name,
                id=entry.id or f"runtime.service.{entry.name.lower().replace(' ', '_')}",
                summary=entry.summary or "",
                origin=UuidOrigin.RUNTIME,
            )

            self._store_service(info)

    def get_service_info(self, key: str | BluetoothUUID) -> UuidInfo | None:
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

    def get_characteristic_info(self, identifier: str | BluetoothUUID) -> UuidInfo | None:
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

    def clear_custom_registrations(self) -> None:
        """Clear all custom registrations (for testing)."""
        with self._lock:
            # Remove runtime entries from canonical stores
            runtime_service_keys = [k for k, v in self._services.items() if v.origin == UuidOrigin.RUNTIME]
            runtime_char_keys = [k for k, v in self._characteristics.items() if v.origin == UuidOrigin.RUNTIME]

            for key in runtime_service_keys:
                del self._services[key]
            for key in runtime_char_keys:
                del self._characteristics[key]

            # Remove corresponding aliases (alias -> canonical_key where canonical_key is runtime)
            runtime_service_aliases = [
                alias for alias, canonical in self._service_aliases.items() if canonical in runtime_service_keys
            ]
            runtime_char_aliases = [
                alias for alias, canonical in self._characteristic_aliases.items() if canonical in runtime_char_keys
            ]

            for alias in runtime_service_aliases:
                del self._service_aliases[alias]
            for alias in runtime_char_aliases:
                del self._characteristic_aliases[alias]

            # Restore any preserved SIG entries that were overridden
            for key in runtime_service_keys:
                original = self._service_overrides.pop(key, None)
                if original is not None:
                    self._store_service(original)
            for key in runtime_char_keys:
                original = self._characteristic_overrides.pop(key, None)
                if original is not None:
                    self._store_characteristic(original)


# Global instance
uuid_registry = UuidRegistry()
