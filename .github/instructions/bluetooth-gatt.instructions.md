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

**Example - WRONG:**
```python
# ❌ Hardcoded UUID string
if characteristic_uuid == "2A19":
    return parse_battery_level(data)

# ❌ Hardcoded full UUID
if str(uuid) == "0000180f-0000-1000-8000-00805f9b34fb":
    return BatteryService()
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

**Example - WRONG (different APIs):**
```python
# ❌ Don't make users use different patterns
sig_value = sig_char.decode(data)  # Different method name
custom_value = custom_char.parse_data(data)  # Different method name
```

## Characteristic Implementation Pattern

**ALL characteristics MUST follow this pattern:**
```python
from __future__ import annotations
from dataclasses import dataclass
from .base import BaseCharacteristic
from bluetooth_sig.gatt.exceptions import InsufficientDataError

@dataclass(frozen=True)
class BatteryLevelData:
    """Battery level characteristic data.

    Attributes:
        level: Battery level percentage (0-100)
        unit: Always '%'
    """
    level: int
    unit: str = "%"

class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery Level characteristic (0x2A19).

    Spec: Bluetooth SIG Assigned Numbers, Battery Level characteristic
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Decode battery level from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            Battery level percentage (0-100)

        Raises:
            InsufficientDataError: If data length is not exactly 1 byte
            ValueRangeError: If value is not in range 0-100
        """
        if len(data) != 1:
            raise InsufficientDataError(
                f"Battery Level requires exactly 1 byte, got {len(data)}"
            )

        value = int(data[0])
        if not 0 <= value <= 100:
            raise ValueRangeError(f"Battery level must be 0-100%, got {value}%")

        return value

    @property
    def unit(self) -> str:
        """Return the unit for this characteristic."""
        return "%"
```

## Parsing Standards

**Based on SIG specifications:**
- **Temperature**: sint16, 0.01°C resolution, little endian
- **Humidity**: uint16, 0.01% resolution, little endian
- **Pressure**: uint32, 0.1 Pa resolution → convert to hPa
- **Battery**: uint8, direct percentage value

**Validation sequence:**
1. Length validation FIRST (before any decoding)
2. Decode raw value
3. Check for special sentinels (0xFFFF, etc.)
4. Range validation
5. Apply scaling/conversion
6. Return typed result

**Example with sentinel handling:**
```python
def decode_value(self, data: bytearray) -> float | None:
    """Decode temperature with sentinel value handling."""
    # 1. Length validation
    if len(data) != 2:
        raise InsufficientDataError(f"Temperature requires 2 bytes, got {len(data)}")

    # 2. Decode raw value
    raw_value = int.from_bytes(data, byteorder="little", signed=True)

    # 3. Check sentinel
    if raw_value == -32768:  # 0x8000 = "Not available"
        return None

    # 4. Range validation
    if not -27315 <= raw_value <= 32767:  # -273.15°C to 327.67°C
        raise ValueRangeError(f"Temperature {raw_value * 0.01}°C out of valid range")

    # 5. Apply scaling
    return raw_value * 0.01  # °C
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

# ❌ WRONG - no timeout (could hang forever)
await client.read_gatt_char(uuid)
```

**Performance considerations:**
- Avoid redundant service discovery
- Cache structured discovery results where safe
- Release/close BLE resources deterministically (context managers or explicit close)

## Bit Field Parsing

**Use named bit field abstractions, not magic masks:**
```python
from dataclasses import dataclass

@dataclass
class TemperatureFlags:
    """Temperature measurement flags byte."""
    celsius: bool          # Bit 0: 0=Fahrenheit, 1=Celsius
    timestamp: bool        # Bit 1: Timestamp present
    temperature_type: bool # Bit 2: Temperature type present

    @classmethod
    def from_byte(cls, byte: int) -> TemperatureFlags:
        """Parse flags from byte."""
        return cls(
            celsius=bool(byte & 0x01),
            timestamp=bool(byte & 0x02),
            temperature_type=bool(byte & 0x04),
        )

# Usage in characteristic
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

## Error Handling

**GATT-specific exceptions:**
```python
from bluetooth_sig.gatt.exceptions import (
    BluetoothSIGError,        # Base exception
    InsufficientDataError,    # Data too short
    ValueRangeError,          # Value out of spec range
    UUIDResolutionError,      # UUID not found in registry
    TypeMismatchError,        # Wrong data type
)

# Usage
def decode_value(self, data: bytearray) -> int:
    """Decode with proper error handling."""
    if len(data) < 2:
        raise InsufficientDataError(
            f"{self._info.name} requires at least 2 bytes, got {len(data)}"
        )

    value = int.from_bytes(data[:2], "little")
    if value > 1000:
        raise ValueRangeError(
            f"{self._info.name} value {value} exceeds maximum 1000"
        )

    return value
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

    Raises:
        InsufficientDataError: If data is not exactly 2 bytes
        ValueRangeError: If temperature is outside valid range

    Examples:
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
