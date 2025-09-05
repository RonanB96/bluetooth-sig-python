"""Enhanced Temperature characteristic demonstrating maximum YAML automation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class EnhancedTemperatureCharacteristic(BaseCharacteristic):
    """Enhanced Temperature characteristic with maximum YAML automation.
    
    This demonstrates the new Phase 1.2 enhanced YAML automation capabilities:
    - UUIDs auto-resolved from characteristic_uuids.yaml ✅
    - Data types auto-resolved from GSS YAML files ✅ 
    - Field sizes auto-resolved from GSS YAML files ✅
    - Unit symbols auto-resolved via cross-file references ✅
    - Signed/unsigned detection from data type ✅
    - Byte order hints (little-endian by convention) ✅
    
    Manual implementation only required for:
    - Resolution factors (cannot be parsed from human text) ❌
    - Special value handling (0x8000 = "not known") ❌
    """

    _characteristic_name: str = "Temperature"

    def __post_init__(self):
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse temperature using enhanced YAML automation with minimal manual implementation."""
        # Enhanced YAML automation provides:
        field_size = self.get_enhanced_field_size()  # ✅ 2 (from GSS YAML)
        is_signed = self.is_signed_from_enhanced_yaml()  # ✅ True (from 'sint16')
        byte_order = self.get_byte_order_hint()  # ✅ "little" (by convention)
        
        if not field_size:
            # Fallback if enhanced YAML not available
            field_size = 2
            is_signed = True
            
        if len(data) < field_size:
            raise ValueError(f"Temperature data must be at least {field_size} bytes")

        # Parse using enhanced YAML metadata
        temp_raw = int.from_bytes(
            data[:field_size],
            byteorder=byte_order,
            signed=is_signed
        )
        
        # Special value handling (manual implementation required)
        if temp_raw == -32768:  # 0x8000 when interpreted as signed 16-bit
            raise ValueError("Temperature value is not known")
        
        # Resolution factor (manual implementation required - cannot automate from human text)
        resolution = self._get_resolution()
        return temp_raw * resolution

    def _get_resolution(self) -> float:
        """Manual implementation: Extract resolution from human text (cannot automate).
        
        Enhanced YAML provides resolution text but parsing "0.01 degrees Celsius" 
        from human language requires manual interpretation.
        """
        # Could attempt to parse from self.get_enhanced_resolution_text() but
        # human text parsing is error-prone, so manual implementation is safer
        return 0.01  # degrees Celsius

    @property  
    def unit(self) -> str:
        """Unit is automatically resolved via enhanced YAML cross-reference system."""
        # This will return "°C" automatically from:
        # GSS YAML: Base Unit: org.bluetooth.unit.thermodynamic_temperature.degree_celsius
        # → Cross-reference with units.yaml: "Celsius temperature (degree Celsius)" 
        # → Symbol extraction: "°C"
        return super().unit