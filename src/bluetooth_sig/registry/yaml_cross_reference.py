"""Enhanced YAML cross-reference system for maximum metadata automation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EnhancedCharacteristicSpec:
    """Enhanced characteristic specification from cross-file YAML references."""
    
    uuid: str
    name: str
    data_type: str | None = None
    field_size: str | None = None
    unit_id: str | None = None
    unit_symbol: str | None = None
    base_unit: str | None = None
    resolution_text: str | None = None
    description: str | None = None


class YAMLCrossReferenceResolver:
    """Enhanced YAML resolver with cross-file references for maximum automation."""
    
    def __init__(self, bluetooth_sig_path: Path | None = None):
        """Initialize with path to bluetooth_sig submodule."""
        self.bluetooth_sig_path = bluetooth_sig_path or self._find_bluetooth_sig_path()
        self._gss_specs: dict[str, dict[str, Any]] = {}
        self._unit_mappings: dict[str, str] = {}
        self._characteristic_uuids: dict[str, str] = {}
        
        try:
            self._load_all_yaml_data()
        except Exception as e:
            logging.warning(f"YAML cross-reference loading failed: {e}")
    
    def _find_bluetooth_sig_path(self) -> Path:
        """Find bluetooth_sig submodule path relative to this file."""
        # From src/bluetooth_sig/registry/yaml_cross_reference.py
        # Go up to project root and find bluetooth_sig submodule
        current = Path(__file__).parent
        for _ in range(4):  # Go up 4 levels to project root
            current = current.parent
            bluetooth_sig = current / "bluetooth_sig"
            if bluetooth_sig.exists() and (bluetooth_sig / "assigned_numbers").exists():
                return bluetooth_sig
        
        # Fallback paths for development/testing
        fallbacks = [
            Path(__file__).parent.parent.parent.parent / "bluetooth_sig",
            Path.cwd() / "bluetooth_sig",
        ]
        
        for path in fallbacks:
            if path.exists() and (path / "assigned_numbers").exists():
                return path
                
        # Return the first fallback even if it doesn't exist (for error handling)
        return fallbacks[0]
    
    def _load_all_yaml_data(self):
        """Load all YAML data for cross-referencing."""
        self._load_characteristic_uuids()
        self._load_gss_specifications() 
        self._load_unit_mappings()
    
    def _load_characteristic_uuids(self):
        """Load characteristic UUID mappings."""
        uuid_file = self.bluetooth_sig_path / "assigned_numbers" / "uuids" / "characteristic_uuids.yaml"
        if not uuid_file.exists():
            return
            
        try:
            with uuid_file.open("r") as f:
                data = yaml.safe_load(f)
                for uuid_info in data.get("uuids", []):
                    name = uuid_info.get("name", "")
                    uuid_raw = uuid_info.get("uuid", "")
                    if name and uuid_raw:
                        # Handle both string and integer UUIDs
                        if isinstance(uuid_raw, int):
                            uuid = f"{uuid_raw:04X}"
                        else:
                            uuid = str(uuid_raw).replace("0x", "").upper()
                        self._characteristic_uuids[name] = uuid
        except Exception as e:
            logging.warning(f"Failed to load characteristic UUIDs: {e}")
    
    def _load_gss_specifications(self):
        """Load GSS YAML files for data types, field sizes, and unit references."""
        gss_dir = self.bluetooth_sig_path / "gss"
        if not gss_dir.exists():
            return
            
        for gss_file in gss_dir.glob("org.bluetooth.characteristic.*.yaml"):
            try:
                with gss_file.open("r") as f:
                    data = yaml.safe_load(f)
                    if "characteristic" in data:
                        char_data = data["characteristic"]
                        char_id = char_data.get("identifier", "")
                        char_name = char_data.get("name", "")
                        
                        # Store by both ID and name for lookup flexibility
                        if char_id:
                            self._gss_specs[char_id] = char_data
                        if char_name:
                            self._gss_specs[char_name] = char_data
                            
            except Exception as e:
                logging.debug(f"Failed to load GSS file {gss_file}: {e}")
    
    def _load_unit_mappings(self):
        """Load unit symbol mappings from units.yaml."""
        units_file = self.bluetooth_sig_path / "assigned_numbers" / "uuids" / "units.yaml"
        if not units_file.exists():
            return
            
        try:
            with units_file.open("r") as f:
                data = yaml.safe_load(f)
                for unit_info in data.get("uuids", []):
                    unit_id = unit_info.get("id", "")
                    unit_name = unit_info.get("name", "")
                    if unit_id and unit_name:
                        # Extract symbol from unit name
                        symbol = self._extract_unit_symbol(unit_name)
                        if symbol:
                            self._unit_mappings[unit_id] = symbol
        except Exception as e:
            logging.warning(f"Failed to load unit mappings: {e}")
    
    def _extract_unit_symbol(self, unit_name: str) -> str:
        """Extract unit symbol from units.yaml name field."""
        # Handle common unit names that map to symbols
        unit_symbol_map = {
            "percentage": "%",
            "per mille": "‰",
            "unitless": "",
        }
        
        # Check for direct symbol mapping first
        if unit_name.lower() in unit_symbol_map:
            return unit_symbol_map[unit_name.lower()]
        
        # Extract symbol from parentheses (e.g., "pressure (pascal)" -> "Pa")
        if "(" in unit_name and ")" in unit_name:
            start = unit_name.find("(") + 1
            end = unit_name.find(")", start)
            if 0 < start < end:
                symbol_candidate = unit_name[start:end].strip()
                
                # Map common unit types to symbols
                symbol_mapping = {
                    "degree celsius": "°C",
                    "celsius": "°C",
                    "fahrenheit": "°F",
                    "kelvin": "K",
                    "pascal": "Pa",
                    "hectopascal": "hPa",
                    "bar": "bar",
                    "volt": "V",
                    "ampere": "A",
                    "watt": "W",
                    "joule": "J",
                    "hertz": "Hz",
                    "metre": "m",
                    "meter": "m",
                    "kilogram": "kg",
                    "second": "s",
                    "lux": "lx",
                    "gram": "g",
                    "degree": "°",
                }
                
                return symbol_mapping.get(symbol_candidate.lower(), symbol_candidate)
        
        # Handle thermodynamic temperature specially
        if "celsius temperature" in unit_name.lower():
            return "°C"
        if "fahrenheit temperature" in unit_name.lower():
            return "°F"
            
        # Return empty string if no symbol can be extracted
        return ""
    
    def resolve_characteristic_spec(self, characteristic_name: str) -> EnhancedCharacteristicSpec | None:
        """Enhanced characteristic resolution with cross-file YAML references."""
        # 1. Get UUID from characteristic_uuids.yaml
        uuid = self._characteristic_uuids.get(characteristic_name)
        if not uuid:
            return None
            
        # 2. Get specification from GSS YAML files
        gss_spec = self._gss_specs.get(characteristic_name)
        
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
                
                # Extract base unit from description
                if "Base Unit:" in field_description:
                    base_unit_line = field_description.split("Base Unit:")[1].split("\n")[0].strip()
                    base_unit = base_unit_line
                    unit_id = base_unit_line
                    
                    # 4. Cross-reference unit_id with units.yaml to get symbol
                    unit_symbol = self._unit_mappings.get(unit_id, "")
                
                # Extract resolution information  
                if "resolution of" in field_description.lower():
                    resolution_text = field_description
        
        return EnhancedCharacteristicSpec(
            uuid=uuid,
            name=characteristic_name,
            data_type=data_type,
            field_size=field_size,
            unit_id=unit_id,
            unit_symbol=unit_symbol,
            base_unit=base_unit,
            resolution_text=resolution_text,
            description=description
        )
    
    def get_signed_from_data_type(self, data_type: str | None) -> bool:
        """Determine if data type is signed from GSS data type."""
        if not data_type:
            return False
        return data_type.startswith("sint")
    
    def get_byte_order_hint(self) -> str:
        """Get byte order hint (Bluetooth SIG uses little-endian by convention)."""
        return "little"


# Global instance for easy access
yaml_cross_reference = YAMLCrossReferenceResolver()