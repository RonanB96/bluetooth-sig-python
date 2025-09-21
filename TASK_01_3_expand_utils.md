# Task 1.3: Expand Utils Classes

## Priority: Phase 1 (Foundation) - Can run in parallel with Task 1.2

## Parallelization: Can start after Task 1.1, parallel with Task 1.2

## Objective

Expand the existing utils classes with missing functionality discovered during characteristic analysis to support all conversion tasks.

## Files to Modify

- `src/bluetooth_sig/gatt/characteristics/utils.py`

## Implementation Details

### 1. Refactor DataParser Class with Simplified API

Replace multiple specific methods with simplified signed flag approach:

```python
@staticmethod
def parse_int8(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: str = "little") -> int:
    """Parse 8-bit integer with optional signed interpretation."""
    if len(data) < offset + 1:
        raise ValueError(f"Insufficient data for int8 at offset {offset}")
    value = data[offset]
    if signed and value >= 128:
        return value - 256
    return value

@staticmethod
def parse_int16(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: str = "little") -> int:
    """Parse 16-bit integer with configurable endianness and signed interpretation."""
    if len(data) < offset + 2:
        raise ValueError(f"Insufficient data for int16 at offset {offset}")
    return int.from_bytes(data[offset:offset+2], byteorder=endian, signed=signed)

@staticmethod
def parse_int32(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: str = "little") -> int:
    """Parse 32-bit integer with configurable endianness and signed interpretation."""
    if len(data) < offset + 4:
        raise ValueError(f"Insufficient data for int32 at offset {offset}")
    return int.from_bytes(data[offset:offset+4], byteorder=endian, signed=signed)

@staticmethod
def encode_int8(value: int, signed: bool = False, endian: str = "little") -> bytearray:
    """Encode 8-bit integer with signed/unsigned validation."""
    if signed:
        if not -128 <= value <= 127:
            raise ValueError(f"Value {value} out of sint8 range (-128 to 127)")
    else:
        if not 0 <= value <= 255:
            raise ValueError(f"Value {value} out of uint8 range (0-255)")
    return bytearray(value.to_bytes(1, byteorder=endian, signed=signed))

@staticmethod
def encode_int16(value: int, signed: bool = False, endian: str = "little") -> bytearray:
    """Encode 16-bit integer with configurable endianness and signed/unsigned validation."""
    if signed:
        if not -32768 <= value <= 32767:
            raise ValueError(f"Value {value} out of sint16 range (-32768 to 32767)")
    else:
        if not 0 <= value <= 65535:
            raise ValueError(f"Value {value} out of uint16 range (0-65535)")
    return bytearray(value.to_bytes(2, byteorder=endian, signed=signed))

@staticmethod
def encode_int32(value: int, signed: bool = False, endian: str = "little") -> bytearray:
    """Encode 32-bit integer with configurable endianness and signed/unsigned validation."""
    if signed:
        if not -2147483648 <= value <= 2147483647:
            raise ValueError(f"Value {value} out of sint32 range")
    else:
        if not 0 <= value <= 4294967295:
            raise ValueError(f"Value {value} out of uint32 range")
    return bytearray(value.to_bytes(4, byteorder=endian, signed=signed))

@staticmethod
def parse_variable_length(data: bytes | bytearray, min_length: int, max_length: int) -> bytes:
    """Parse variable length data with validation."""
    length = len(data)
    if length < min_length:
        raise ValueError(f"Data too short: {length} < {min_length}")
    if length > max_length:
        raise ValueError(f"Data too long: {length} > {max_length}")
    return bytes(data)
```

### 2. Expand IEEE11073Parser Class

Add complete IEEE 11073 format support:

```python
@staticmethod
def parse_sfloat(data: bytes | bytearray, offset: int = 0) -> float:
    """Parse IEEE 11073 16-bit SFLOAT."""
    if len(data) < offset + 2:
        raise ValueError(f"Insufficient data for SFLOAT at offset {offset}")

    raw_value = int.from_bytes(data[offset:offset+2], byteorder="little")

    # Handle special values
    if raw_value == 0x07FF:
        return float('nan')  # NaN
    elif raw_value == 0x0800:
        return float('inf')  # +INFINITY
    elif raw_value == 0x0801:
        return float('-inf') # -INFINITY
    elif raw_value == 0x0802:
        return None  # Not a Number (NRes)

    # Extract mantissa and exponent
    mantissa = raw_value & 0x0FFF
    if mantissa >= 0x0800:  # Negative mantissa
        mantissa = mantissa - 0x1000

    exponent = (raw_value >> 12) & 0x0F
    if exponent >= 0x08:  # Negative exponent
        exponent = exponent - 0x10

    return mantissa * (10 ** exponent)

@staticmethod
def encode_sfloat(value: float) -> bytearray:
    """Encode float to IEEE 11073 16-bit SFLOAT."""
    import math

    if math.isnan(value):
        return bytearray([0xFF, 0x07])  # NaN
    elif math.isinf(value):
        if value > 0:
            return bytearray([0x00, 0x08])  # +INFINITY
        else:
            return bytearray([0x01, 0x08])  # -INFINITY

    # Find best exponent and mantissa representation
    exponent = 0
    mantissa = value

    while abs(mantissa) >= 2048 and exponent < 7:
        mantissa /= 10
        exponent += 1

    while abs(mantissa) < 1 and mantissa != 0 and exponent > -8:
        mantissa *= 10
        exponent -= 1

    mantissa_int = int(round(mantissa))

    # Pack into 16-bit value
    if exponent < 0:
        exponent = exponent + 16
    if mantissa_int < 0:
        mantissa_int = mantissa_int + 4096

    raw_value = (exponent << 12) | (mantissa_int & 0x0FFF)
    return bytearray(raw_value.to_bytes(2, byteorder="little"))

@staticmethod
def parse_float32(data: bytes | bytearray, offset: int = 0) -> float:
    """Parse IEEE 11073 32-bit FLOAT."""
    if len(data) < offset + 4:
        raise ValueError(f"Insufficient data for FLOAT32 at offset {offset}")

    raw_value = int.from_bytes(data[offset:offset+4], byteorder="little")

    # Handle special values (similar to SFLOAT but 32-bit)
    if raw_value == 0x007FFFFF:
        return float('nan')
    elif raw_value == 0x00800000:
        return float('inf')
    elif raw_value == 0x00800001:
        return float('-inf')
    elif raw_value == 0x00800002:
        return None  # NRes

    # Extract mantissa (24-bit) and exponent (8-bit)
    mantissa = raw_value & 0x00FFFFFF
    if mantissa >= 0x00800000:  # Negative mantissa
        mantissa = mantissa - 0x01000000

    exponent = (raw_value >> 24) & 0xFF
    if exponent >= 0x80:  # Negative exponent
        exponent = exponent - 0x100

    return mantissa * (10 ** exponent)
```

### 3. Expand DataValidator Class

Add common validation patterns found in characteristics:

```python
@staticmethod
def validate_concentration_range(value: float, max_ppm: float = 65535.0) -> None:
    """Validate concentration value is in acceptable range."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"Concentration must be numeric, got {type(value)}")
    if value < 0:
        raise ValueError(f"Concentration cannot be negative: {value}")
    if value > max_ppm:
        raise ValueError(f"Concentration {value} exceeds maximum {max_ppm} ppm")

@staticmethod
def validate_temperature_range(value: float, min_celsius: float = -273.15, max_celsius: float = 1000.0) -> None:
    """Validate temperature is in physically reasonable range."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"Temperature must be numeric, got {type(value)}")
    if value < min_celsius:
        raise ValueError(f"Temperature {value}°C below absolute zero")
    if value > max_celsius:
        raise ValueError(f"Temperature {value}°C exceeds maximum {max_celsius}°C")

@staticmethod
def validate_percentage(value: int | float, allow_over_100: bool = False) -> None:
    """Validate percentage value (0-100% or 0-200% for some characteristics)."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"Percentage must be numeric, got {type(value)}")
    if value < 0:
        raise ValueError(f"Percentage cannot be negative: {value}")
    max_value = 200 if allow_over_100 else 100
    if value > max_value:
        raise ValueError(f"Percentage {value}% exceeds maximum {max_value}%")

@staticmethod
def validate_power_range(value: int | float, max_watts: float = 65535.0) -> None:
    """Validate power measurement range."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"Power must be numeric, got {type(value)}")
    if value < 0:
        raise ValueError(f"Power cannot be negative: {value}")
    if value > max_watts:
        raise ValueError(f"Power {value}W exceeds maximum {max_watts}W")
```

### 4. Expand DebugUtils Class

Add formatting utilities found in characteristics:

```python
@staticmethod
def format_measurement_value(value: Any, unit: str | None = None, precision: int = 2) -> str:
    """Format measurement value with unit for display."""
    if value is None:
        return "N/A"

    if isinstance(value, float):
        formatted = f"{value:.{precision}f}"
    else:
        formatted = str(value)

    if unit:
        return f"{formatted} {unit}"
    return formatted

@staticmethod
def format_hex_data(data: bytes | bytearray, separator: str = " ") -> str:
    """Format binary data as hex string."""
    return separator.join(f"{byte:02X}" for byte in data)

@staticmethod
def format_binary_flags(value: int, bit_names: list[str]) -> str:
    """Format integer as binary flags with names."""
    flags = []
    for i, name in enumerate(bit_names):
        if value & (1 << i):
            flags.append(name)
    return ", ".join(flags) if flags else "None"

@staticmethod
def validate_struct_format(data: bytes | bytearray, format_string: str) -> None:
    """Validate data length matches struct format requirements."""
    import struct
    expected_size = struct.calcsize(format_string)
    actual_size = len(data)
    if actual_size != expected_size:
        raise ValueError(f"Data size {actual_size} doesn't match format '{format_string}' size {expected_size}")
```

## Success Criteria

- All new utility methods properly documented
- Methods include comprehensive error handling
- Encoding methods validate input ranges
- IEEE 11073 parser handles all special values correctly
- All utilities have consistent error message formats
- Utilities integrate seamlessly with existing code

## Dependencies

- **REQUIRES**: Task 1.1 (BaseCharacteristic) for integration
- **PARALLEL**: Can run with Task 1.2 (Templates)
- **ENABLES**: All characteristic conversion tasks

## Testing

```bash
# Test new utility methods with different endianness
python -c "from src.bluetooth_sig.gatt.characteristics.utils import DataParser; print(DataParser.parse_int16(b'\\x00\\x80', 0, signed=True))"

# Test big-endian parsing
python -c "from src.bluetooth_sig.gatt.characteristics.utils import DataParser; print(DataParser.parse_int16(b'\\x80\\x00', 0, signed=True, endian='big'))"

# Test IEEE 11073 parsing
python -c "from src.bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser; print(IEEE11073Parser.parse_sfloat(b'\\xFF\\x07', 0))"

# Run specific utils tests
python -m pytest tests/ -k "utils" -v
```
