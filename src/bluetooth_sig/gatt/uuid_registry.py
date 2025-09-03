"""UUID registry loading from Bluetooth SIG YAML files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class UuidInfo:
    """Information about a UUID."""

    uuid: str
    name: str
    id: str
    summary: str = ""
    unit: str | None = None


class UuidRegistry:
    """Registry for Bluetooth SIG UUIDs."""

    def __init__(self):
        """Initialize the UUID registry."""
        self._services: dict[str, UuidInfo] = {}
        self._characteristics: dict[str, UuidInfo] = {}
        self._unit_mappings: dict[str, str] = {}
        try:
            self._load_uuids()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _load_yaml(self, file_path: Path) -> list[dict]:
        """Load UUIDs from a YAML file."""
        if not file_path.exists():
            return []

        with file_path.open("r") as f:
            data = yaml.safe_load(f)
            return data.get("uuids", [])

    def _load_uuids(self):
        """Load all UUIDs from YAML files."""
        # Try development location first (git submodule)
        # From src/bluetooth_sig/gatt/uuid_registry.py, go up 4 levels to project root
        project_root = Path(__file__).parent.parent.parent.parent
        base_path = project_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

        if not base_path.exists():
            # Try installed package location
            pkg_root = Path(__file__).parent.parent
            base_path = pkg_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

        if not base_path.exists():
            # Don't raise error, just return with empty registry
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

                info = UuidInfo(uuid=uuid, name=uuid_info["name"], id=uuid_info["id"])
                self._services[uuid] = info
                # Index by all possible lookups
                self._services[uuid_info["name"]] = info  # Exact name
                self._services[uuid_info["name"].lower()] = info  # Lowercase
                self._services[uuid_info["id"]] = info  # Full ID
                # Service-specific format
                service_name = uuid_info["id"].replace("org.bluetooth.service.", "")
                if service_name.endswith("_service"):
                    service_name = service_name[:-8]  # Remove _service
                service_name = service_name.replace("_", " ").title()
                self._services[service_name] = info  # Add name as key

        # Load characteristic UUIDs
        characteristic_yaml = base_path / "characteristic_uuids.yaml"
        if characteristic_yaml.exists():
            for uuid_info in self._load_yaml(characteristic_yaml):
                uuid = uuid_info["uuid"]
                if isinstance(uuid, str):
                    uuid = uuid.replace("0x", "")
                else:
                    uuid = hex(uuid)[2:].upper()

                info = UuidInfo(uuid=uuid, name=uuid_info["name"], id=uuid_info["id"])
                self._characteristics[uuid] = info
                # Also index by name for characteristic lookup
                self._characteristics[uuid_info["name"]] = info
                self._characteristics[uuid_info["id"]] = info

        # Load unit mappings from units.yaml
        self._load_unit_mappings(base_path)

        # Load detailed specifications from GSS YAML files to extract units
        self._load_gss_specifications()

    def _load_unit_mappings(self, base_path: Path):
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

                # Extract unit symbol from name
                unit_symbol = self._extract_unit_symbol_from_name(unit_name)
                if unit_symbol:
                    # Map from the ID (e.g., org.bluetooth.unit.percentage) to symbol (%)
                    # Remove org.bluetooth.unit. prefix for the key
                    unit_key = unit_id.replace("org.bluetooth.unit.", "").lower()
                    self._unit_mappings[unit_key] = unit_symbol

        except (yaml.YAMLError, OSError, KeyError):
            # Skip unit loading if there's an error, continue without units
            pass

    def _extract_unit_symbol_from_name(self, unit_name: str) -> str | None:
        """Extract unit symbol from unit name.

        Args:
            unit_name: Unit name like "percentage" or "Celsius temperature (degree Celsius)"

        Returns:
            Unit symbol like "%" or "°C", or the unit name if no symbol can be extracted
        """
        # Handle common unit names that map to symbols
        unit_symbol_map = {
            "percentage": "%",
            "per mille": "‰",
            "unitless": "",
        }

        # Check for direct symbol mapping first
        if unit_name.lower() in unit_symbol_map:
            return unit_symbol_map[unit_name.lower()]

        # Extract symbol from parentheses if present (e.g., "pressure (pascal)" -> "Pa")
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

        # Check if unit name starts with a common unit type
        for unit_type, symbol in common_units.items():
            if unit_name.lower().startswith(unit_type):
                return symbol

        # If no symbol extraction is possible, return the name itself
        return unit_name

    def _load_gss_specifications(self):
        """Load detailed specifications from GSS YAML files to extract unit information."""
        # From src/bluetooth_sig/gatt/uuid_registry.py, go up 4 levels to project root
        project_root = Path(__file__).parent.parent.parent.parent
        gss_path = project_root / "bluetooth_sig" / "gss"

        if not gss_path.exists():
            # Try installed package location
            pkg_root = Path(__file__).parent.parent
            gss_path = pkg_root / "bluetooth_sig" / "gss"

        if not gss_path.exists():
            # GSS files not available, skip unit loading
            return

        # Process all characteristic GSS YAML files
        for yaml_file in gss_path.glob("org.bluetooth.characteristic.*.yaml"):
            try:
                with yaml_file.open("r") as f:
                    data = yaml.safe_load(f)

                if not data or "characteristic" not in data:
                    continue

                char_data = data["characteristic"]
                char_name = char_data.get("name")
                char_id = char_data.get("identifier")

                if not char_name or not char_id:
                    continue

                # Extract unit from structure fields
                unit = self._extract_unit_from_gss(char_data)

                if unit:
                    # Update existing UuidInfo entries with unit information
                    for key, uuid_info in self._characteristics.items():
                        if (
                            uuid_info.name == char_name
                            or uuid_info.id == char_id
                            or key == char_name
                            or key == char_id
                        ):
                            # Create new UuidInfo with unit
                            updated_info = UuidInfo(
                                uuid=uuid_info.uuid,
                                name=uuid_info.name,
                                id=uuid_info.id,
                                summary=uuid_info.summary,
                                unit=unit,
                            )
                            self._characteristics[key] = updated_info

            except (yaml.YAMLError, OSError, KeyError):
                # Skip problematic files, continue with others
                continue

    def _extract_unit_from_gss(self, char_data: dict) -> str | None:
        """Extract unit from GSS characteristic structure.

        Args:
            char_data: Dictionary containing characteristic data from GSS YAML

        Returns:
            Human-readable unit string or None if not found
        """
        structure = char_data.get("structure", [])
        if not structure:
            return None

        for field in structure:
            if not isinstance(field, dict):
                continue

            description = field.get("description", "")
            if "Base Unit:" in description:
                # Extract the unit after "Base Unit:"
                unit_line = None
                for line in description.split("\n"):
                    if "Base Unit:" in line:
                        unit_line = line.strip()
                        break

                if unit_line:
                    # Parse "Base Unit: org.bluetooth.unit.X" format
                    if "org.bluetooth.unit." in unit_line:
                        unit_spec = unit_line.split("org.bluetooth.unit.")[1].strip()
                        return self._convert_bluetooth_unit_to_readable(unit_spec)

        return None

    def _convert_bluetooth_unit_to_readable(self, unit_spec: str) -> str:
        """Convert Bluetooth SIG unit specification to human-readable format.

        Args:
            unit_spec: Unit specification like "thermodynamic_temperature.degree_celsius"

        Returns:
            Human-readable unit like "°C"
        """
        # Remove trailing dots and clean up
        unit_spec = unit_spec.rstrip(".").lower()

        # Use dynamically loaded unit mappings from units.yaml
        return self._unit_mappings.get(unit_spec, unit_spec)

    def get_service_info(self, key: str) -> UuidInfo | None:
        """Get information about a service.

        Args:
            key: Can be a UUID, name, or service ID
        """
        # Try direct lookup first
        if info := self._services.get(key):
            return info

        # Try normalized UUID
        if len(key) >= 4:  # Might be a UUID
            normalized = key.replace("0x", "").replace("-", "").upper()
            if len(normalized) == 32:  # Full UUID
                normalized = normalized[4:8]
            if info := self._services.get(normalized):
                return info

        # Try name variations
        key = key.replace("_", " ").title()  # Convert snake_case to Title Case
        lower_key = key.lower()

        # Try with 'Service' suffix variations
        variations = [
            key,  # Original with spaces
            lower_key,  # Lowercase
            key + " Service",  # With Service suffix
            lower_key + " service",  # Lowercase with service
        ]

        for k in variations:
            if info := self._services.get(k):
                return info

        return None

    def get_characteristic_info(self, identifier: str) -> UuidInfo | None:
        """Get information about a characteristic UUID or name."""
        # First try direct lookup (for names and IDs)
        if identifier in self._characteristics:
            return self._characteristics[identifier]

        # Try case-insensitive lookup
        if identifier.lower() in self._characteristics:
            return self._characteristics[identifier.lower()]

        # If it looks like a UUID, do UUID transformations
        if all(c in "0123456789ABCDEFabcdef-x" for c in identifier):
            uuid = identifier.replace("0x", "").replace("-", "").upper()
            if len(uuid) == 32:  # Full UUID
                uuid = uuid[4:8]
            return self._characteristics.get(uuid)

        return None


# Global instance
uuid_registry = UuidRegistry()
