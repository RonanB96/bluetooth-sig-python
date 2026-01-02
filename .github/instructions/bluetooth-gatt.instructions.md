---
applyTo: "src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py"
---

# Bluetooth GATT Layer Guidelines

## Architecture Boundaries (ABSOLUTE)

**Allowed module structure:**
```
src/bluetooth_sig/
├── gatt/              # ✅ Can import from: types, utils, registry
├── registry/          # ✅ Can import from: types, utils
├── types/             # ✅ Can import from: (nothing - pure types)
└── utils/             # ✅ Can import from: types
```

The translation layer must remain framework-agnostic to support multiple backends (bleak, simplepyble, etc.).

## UUID Hardcoding Policy (ABSOLUTE)

**NEVER hardcode UUID strings in implementation code.**

- ❌ **FORBIDDEN**: `if uuid == "2A19"` or `UUID("0000180f-0000-1000-8000-00805f9b34fb")`
- ✅ **REQUIRED**: Use registry resolution through the UUID registry system

UUIDs appear ONLY in:
1. YAML files in `bluetooth_sig/` submodule (source of truth)
2. Test fixtures (for validation)
3. Custom characteristic/service `_info` definitions (with justification)

**Example - CORRECT:**
```python
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.gatt.uuid_registry import uuid_registry

# Using enum and registry
char_info = uuid_registry.get_characteristic_info(CharacteristicName.BATTERY_LEVEL)

# Or for custom characteristics with _info
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

class MyCustomChar(BaseCharacteristic):
    _info = CharacteristicInfo(
        uuid=BluetoothUUID("XXXX"),
        name="My Custom Characteristic"
    )
```

## Registry & UUID Usage

**No hardcoded UUID string literals in logic modules:**
- Use registry resolution functions
- Supply `_service_name` / `_characteristic_name` ONLY for non-standard or provisional names
- Adding a new characteristic requires: registry entry, dataclass, tests validating name resolution, and parsing

**Registry resolution example:**
```python
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Resolve characteristic
char_info = uuid_registry.get_characteristic_info(CharacteristicName.BATTERY_LEVEL)
print(f"UUID: {char_info.uuid}")  # "2A19"
print(f"Name: {char_info.name}")  # "Battery Level"

# Resolve service
service_info = uuid_registry.get_service_info(ServiceName.BATTERY_SERVICE)
print(f"UUID: {service_info.uuid}")  # "180F"
```

## User-Facing API Consistency (CRITICAL)

**Custom and SIG characteristics/services MUST have identical usage patterns.**

- Users should NOT need to know whether a characteristic is SIG-defined or custom
- Both must support the same methods: `decode_value()`, `encode_value()`, property access
- Both must use the same initialization patterns
- The ONLY difference should be in registration (SIG auto-resolves, custom needs `_info`)
- API consistency is more important than internal implementation differences

**Example - CORRECT (identical usage):**
```python
from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# SIG characteristic - auto-resolves from registry
battery = BatteryLevelCharacteristic()
value = battery.decode_value(data)

# Custom characteristic - needs _info, but same usage pattern
class MyCustomChar(BaseCharacteristic):
    _info = CharacteristicInfo(uuid=BluetoothUUID("XXXX"), name="My Custom")

custom = MyCustomChar()
value = custom.decode_value(data)  # Same method!
```

## Characteristic Implementation Pattern

**Choose the appropriate pattern based on complexity:**

### Pattern 1: Simple Single-Value (Use Template)
```python
from __future__ import annotations
from .base import BaseCharacteristic
from .templates import Uint8Template

class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery Level characteristic (0x2A19).

    org.bluetooth.characteristic.battery_level

    Represents battery level as percentage (0-100).
    """

    # Template handles everything - no decode_value needed
    _template = Uint8Template()
```

### Pattern 2: Structured Multi-Field (Manual Decode)
```python
from __future__ import annotations
from enum import IntFlag
import msgspec
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

class HeartRateFlags(IntFlag):
    """Heart rate measurement flags."""
    HEART_RATE_VALUE_FORMAT_UINT16 = 0x01
    SENSOR_CONTACT_DETECTED = 0x02
    SENSOR_CONTACT_SUPPORTED = 0x04
    ENERGY_EXPENDED_PRESENT = 0x08
    RR_INTERVAL_PRESENT = 0x10

class HeartRateData(msgspec.Struct, frozen=True, kw_only=True):
    """Heart rate measurement data.

    Attributes:
        heart_rate: Heart rate in BPM
        energy_expended: Optional energy in kJ
        rr_intervals: RR intervals in seconds
    """
    heart_rate: int
    energy_expended: int | None = None
    rr_intervals: tuple[float, ...] = ()

class HeartRateMeasurementCharacteristic(BaseCharacteristic):
    """Heart Rate Measurement characteristic (0x2A37).

    org.bluetooth.characteristic.heart_rate_measurement
    """

    _manual_value_type = "HeartRateData"  # Override for structured types

    min_length = 2  # BaseCharacteristic validates
    allow_variable_length = True

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> HeartRateData:
        """Parse heart rate measurement.

        Args:
            data: Raw bytes (length already validated by BaseCharacteristic)
            ctx: Optional context

        Returns:
            HeartRateData with parsed fields
        """
        # Parse flags using IntFlag enum
        flags = HeartRateFlags(data[0])
        offset = 1

        # Parse based on flags - use named enum members
        if flags & HeartRateFlags.HEART_RATE_VALUE_FORMAT_UINT16:
            heart_rate = DataParser.parse_int16(data, offset, signed=False)
            offset += 2
        else:
            heart_rate = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        # Optional fields based on flags...
        return HeartRateData(heart_rate=heart_rate)
```

### Pattern 3: Enum/Bitfield (Use EnumTemplate or IntFlag)
```python
from __future__ import annotations
from enum import IntFlag
from .base import BaseCharacteristic
from .templates import EnumTemplate

class AlertLevel(IntFlag):
    """Alert level enumeration."""
    NO_ALERT = 0x00
    MILD_ALERT = 0x01
    HIGH_ALERT = 0x02

class AlertLevelCharacteristic(BaseCharacteristic):
    """Alert Level characteristic (0x2A06).

    org.bluetooth.characteristic.alert_level
    """

    _template = EnumTemplate.uint8(AlertLevel)
```

## Parsing Standards

**Based on SIG specifications:**
- **Temperature**: sint16, 0.01°C resolution, little endian
- **Humidity**: uint16, 0.01% resolution, little endian
- **Pressure**: uint32, 0.1 Pa resolution → convert to hPa
- **Battery**: uint8, direct percentage value

**Framework Responsibilities (BaseCharacteristic handles these - DO NOT duplicate in decode_value):**
1. **Length validation**: Via `min_length`, `max_length`, `allow_variable_length` attributes
2. **Special/sentinel values**: Via `special_values` dictionary on BaseCharacteristic
3. **Range validation**: Via validators in characteristic definition

**Characteristic decode_value() should ONLY:**
1. Parse raw bytes into structured data using templates or DataParser
2. Apply scaling/conversions per spec
3. Return typed result

**Example - CORRECT (using template):**
```python
from .templates import ScaledSint16Template

class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature characteristic (0x2A6E).

    org.bluetooth.characteristic.temperature
    """

    # Framework handles validation via attributes
    min_length = 2
    max_length = 2
    allow_variable_length = False

    # Use template for parsing - no manual validation needed
    _template = ScaledSint16Template.from_letter_method(M=1, d=-2, b=0)  # 0.01 scaling
```

**Example - CORRECT (manual decode with DataParser):**
```python
from __future__ import annotations
import msgspec
from ..context import CharacteristicContext
from .utils import DataParser

class MyCharacteristicData(msgspec.Struct, frozen=True, kw_only=True):
    """Multi-field characteristic data.

    Attributes:
        field1: First field description
        field2: Second field description
    """
    field1: int
    field2: int

def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> MyCharacteristicData:
    """Decode structured multi-field characteristic."""
    # BaseCharacteristic already validated length - just parse
    return MyCharacteristicData(
        field1=DataParser.parse_int16(data, 0, signed=False),
        field2=DataParser.parse_int8(data, 2, signed=True),
    )
```

## Service Implementation Pattern

**Services should aggregate characteristics:**
```python
from bluetooth_sig.gatt.services.base import BaseService
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

class BatteryService(BaseService):
    """Battery Service (0x180F).

    Spec: Bluetooth SIG Assigned Numbers, Battery Service
    """

    def __init__(self):
        super().__init__()
        self.battery_level = BatteryLevelCharacteristic()

    @property
    def characteristics(self) -> dict[str, BaseCharacteristic]:
        """Return all characteristics in this service."""
        return {
            "battery_level": self.battery_level,
        }
```

## Timeouts & Performance

**All BLE connection routines MUST specify timeout:**
```python
# ✅ CORRECT - explicit timeout
await client.read_gatt_char(uuid, timeout=10.0)

**Only raise exceptions for:**
- Parse errors specific to your characteristic's structure
- Invalid flag combinations
- Malformed multi-field data

**Example - CORRECT:**
```python
from __future__ import annotations
from enum import IntFlag
import msgspec

class MyCharacteristicFlags(IntFlag):
    """Characteristic flags."""
    FIELD_PRESENT = 0x01
    EXTENDED_FORMAT = 0x02

class MyCharacteristicData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic data.

    Attributes:
        field: Field description
    """
    field: int

def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> MyCharacteristicData:
    """Parse complex characteristic."""
    # Length already validated by BaseCharacteristic

    flags = MyCharacteristicFlags(data[0])
    offset = 1

    # Raise only for structural/logical errors
    if flags & MyCharacteristicFlags.FIELD_PRESENT and len(data) < offset + 2:
        raise ValueError(f"FIELD_PRESENT flag set but insufficient data")

    # Parse and return - no length checks needed
    return MyCharacteristicData(field=DataParser.parse_int16(data, offset, signed=False))
```

# Usage in characteristic
```python
def decode_value(self, data: bytearray) -> TemperatureMeasurement:
    """Decode temperature measurement."""
    flags = TemperatureFlags.from_byte(data[0])

    offset = 1
    temp_value = int.from_bytes(data[offset:offset+4], "little", signed=True)
    offset += 4

    if flags.timestamp:
        # Parse timestamp...
        offset += 7

    # etc.
```


## Documentation Requirements

**Public APIs need complete docstrings:**
```python
def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
    """Decode temperature characteristic.

    Decodes a 16-bit signed integer representing temperature in 0.01°C
    increments per Bluetooth SIG Temperature Type specification.

    Args:
        data: Raw bytes from BLE characteristic (exactly 2 bytes, little-endian)
        ctx: Optional context for parsing (device info, flags, etc.)

    Returns:
        Temperature in degrees Celsius

   **Is it in Bluetooth SIG assigned numbers?** → Use registry resolution (no `_info` needed)
2. **Is it vendor-specific?** → Create custom with `_info`
3. **Can I use a template?** → Check templates.py for Uint8/16/32, Scaled, Enum, Float, String, etc.
4. **Does similar characteristic exist?** → Inherit and extend
5. **What validation attributes do I need?** → Set `min_length`, `max_length`, `allow_variable_length`
6. **Are there special values?** → Use `special_values` attribute, don't check in decode_value
7. **What's the spec say?** → Check official Bluetooth SIG documentation

**Implementation Checklist:**
- [ ] Choose appropriate pattern (template vs manual decode)
- [ ] Set validation attributes (min_length, max_length, allow_variable_length)
- [ ] Configure special_values if needed (don't check manually)
- [ ] Use DataParser or templates for parsing (no manual length checks)
- [ ] Return typed data (int, float, msgspec.Struct, IntFlag, etc.)
- [ ] Write tests with valid and invalid data
        >>> char = TemperatureCharacteristic()
        >>> char.decode_value(bytearray([0x00, 0x10]))  # 4096 * 0.01 = 40.96°C
        40.96

    Spec Reference:
        Bluetooth SIG Assigned Numbers, Temperature Type characteristic (0x2A1D)
    """
    ...
```

## Before Implementing New Characteristic

Ask yourself:
1. Is it in Bluetooth SIG assigned numbers? → Use registry resolution
2. Is it vendor-specific? → Create custom with `_info`
3. Does similar characteristic exist? → Inherit and extend
4. What are the edge cases? → Empty, too short, too long, sentinel values
5. What's the spec say? → Check official Bluetooth SIG documentation
