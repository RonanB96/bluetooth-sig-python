"""UUID registry loading from Bluetooth SIG YAML files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


@dataclass
class UuidInfo:
    """Information about a UUID."""

    uuid: str
    name: str
    id: str
    summary: str = ""


class UuidRegistry:
    """Registry for Bluetooth SIG UUIDs."""

    def __init__(self):
        """Initialize the UUID registry."""
        self._services: dict[str, UuidInfo] = {}
        self._characteristics: dict[str, UuidInfo] = {}
        if YAML_AVAILABLE:
            try:
                self._load_uuids()
            except (FileNotFoundError, Exception):
                # If YAML loading fails, use fallback
                self._load_fallback_uuids()
        else:
            # Use fallback UUIDs when YAML not available
            self._load_fallback_uuids()

    def _load_yaml(self, file_path: Path) -> list[dict]:
        """Load UUIDs from a YAML file."""
        if not YAML_AVAILABLE or not file_path.exists():
            return []

        with file_path.open("r") as f:
            data = yaml.safe_load(f)
            return data.get("uuids", [])

    def _load_uuids(self):
        """Load all UUIDs from YAML files."""
        if not YAML_AVAILABLE:
            return
            
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

    def _load_fallback_uuids(self):
        """Load essential fallback UUIDs when YAML is not available."""
        # Common characteristics - essential for basic functionality
        fallback_characteristics = {
            # Battery Service
            "2A19": UuidInfo("2A19", "Battery Level", "org.bluetooth.characteristic.battery_level"),
            "2A1A": UuidInfo("2A1A", "Battery Power State", "org.bluetooth.characteristic.battery_power_state"),
            
            # Environmental Sensing
            "2A1C": UuidInfo("2A1C", "Temperature Measurement", "org.bluetooth.characteristic.temperature_measurement"),
            "2A6E": UuidInfo("2A6E", "Temperature", "org.bluetooth.characteristic.temperature"),
            "2A6F": UuidInfo("2A6F", "Humidity", "org.bluetooth.characteristic.humidity"),
            "2A6D": UuidInfo("2A6D", "Pressure", "org.bluetooth.characteristic.pressure"),
            "2A76": UuidInfo("2A76", "UV Index", "org.bluetooth.characteristic.uv_index"),
            "2A77": UuidInfo("2A77", "Irradiance", "org.bluetooth.characteristic.irradiance"),
            
            # Device Information
            "2A29": UuidInfo("2A29", "Manufacturer Name String", "org.bluetooth.characteristic.manufacturer_name_string"),
            "2A24": UuidInfo("2A24", "Model Number String", "org.bluetooth.characteristic.model_number_string"),
            "2A25": UuidInfo("2A25", "Serial Number String", "org.bluetooth.characteristic.serial_number_string"),
            "2A26": UuidInfo("2A26", "Firmware Revision String", "org.bluetooth.characteristic.firmware_revision_string"),
            "2A27": UuidInfo("2A27", "Hardware Revision String", "org.bluetooth.characteristic.hardware_revision_string"),
            "2A28": UuidInfo("2A28", "Software Revision String", "org.bluetooth.characteristic.software_revision_string"),
            
            # Generic Access
            "2A00": UuidInfo("2A00", "Device Name", "org.bluetooth.characteristic.gap.device_name"),
            "2A01": UuidInfo("2A01", "Appearance", "org.bluetooth.characteristic.gap.appearance"),
            
            # Heart Rate
            "2A37": UuidInfo("2A37", "Heart Rate Measurement", "org.bluetooth.characteristic.heart_rate_measurement"),
            
            # Blood Pressure
            "2A35": UuidInfo("2A35", "Blood Pressure Measurement", "org.bluetooth.characteristic.blood_pressure_measurement"),
            
            # Cycling Power
            "2A63": UuidInfo("2A63", "Cycling Power Measurement", "org.bluetooth.characteristic.cycling_power_measurement"),
            "2A65": UuidInfo("2A65", "Cycling Power Feature", "org.bluetooth.characteristic.cycling_power_feature"),
            "2A64": UuidInfo("2A64", "Cycling Power Vector", "org.bluetooth.characteristic.cycling_power_vector"),
            "2A66": UuidInfo("2A66", "Cycling Power Control Point", "org.bluetooth.characteristic.cycling_power_control_point"),
            
            # Cycling Speed and Cadence
            "2A5B": UuidInfo("2A5B", "CSC Measurement", "org.bluetooth.characteristic.csc_measurement"),
            
            # Running Speed and Cadence  
            "2A53": UuidInfo("2A53", "RSC Measurement", "org.bluetooth.characteristic.rsc_measurement"),
            
            # Weight Scale
            "2A9D": UuidInfo("2A9D", "Weight Measurement", "org.bluetooth.characteristic.weight_measurement"),
            "2A9E": UuidInfo("2A9E", "Weight Scale Feature", "org.bluetooth.characteristic.weight_scale_feature"),
            
            # Body Composition
            "2A9B": UuidInfo("2A9B", "Body Composition Feature", "org.bluetooth.characteristic.body_composition_feature"),
            "2A9C": UuidInfo("2A9C", "Body Composition Measurement", "org.bluetooth.characteristic.body_composition_measurement"),
        }
        
        # Load characteristics with multiple key formats
        for uuid, info in fallback_characteristics.items():
            self._characteristics[uuid] = info
            self._characteristics[info.name] = info
            self._characteristics[info.id] = info
            # Add common name variations
            if info.name:
                self._characteristics[info.name.lower()] = info
                
        # Common services
        fallback_services = {
            "180F": UuidInfo("180F", "Battery Service", "org.bluetooth.service.battery_service"),
            "181A": UuidInfo("181A", "Environmental Sensing", "org.bluetooth.service.environmental_sensing"),
            "180A": UuidInfo("180A", "Device Information", "org.bluetooth.service.device_information"),
            "1800": UuidInfo("1800", "Generic Access", "org.bluetooth.service.generic_access"),
            "180D": UuidInfo("180D", "Heart Rate", "org.bluetooth.service.heart_rate"),
            "1810": UuidInfo("1810", "Blood Pressure", "org.bluetooth.service.blood_pressure"),
            "1818": UuidInfo("1818", "Cycling Power", "org.bluetooth.service.cycling_power"),
            "1816": UuidInfo("1816", "Cycling Speed and Cadence", "org.bluetooth.service.cycling_speed_and_cadence"),
            "1814": UuidInfo("1814", "Running Speed and Cadence", "org.bluetooth.service.running_speed_and_cadence"),
            "181D": UuidInfo("181D", "Weight Scale", "org.bluetooth.service.weight_scale"),
            "181B": UuidInfo("181B", "Body Composition", "org.bluetooth.service.body_composition"),
        }
        
        # Load services with multiple key formats
        for uuid, info in fallback_services.items():
            self._services[uuid] = info
            self._services[info.name] = info
            self._services[info.id] = info
            # Add common name variations
            if info.name:
                self._services[info.name.lower()] = info
                # Add with "Service" suffix
                self._services[info.name + " Service"] = info
                self._services[info.name.lower() + " service"] = info


# Global instance
uuid_registry = UuidRegistry()
