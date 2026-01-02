# Adding New Characteristics

Learn how to extend the library with custom or newly standardized characteristics.

## When to Add a Characteristic

You might need to add a characteristic when:

1. A new Bluetooth SIG standard characteristic is released
1. You're working with a vendor-specific characteristic
1. You need custom parsing for a specific use case

## Basic Structure

SIG characteristics extend :class:`~bluetooth_sig.gatt.characteristics.base.BaseCharacteristic` and are auto-discovered by UUID in the docstring:

```python
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.utils.data_parser import DataParser
from bluetooth_sig.gatt.context import CharacteristicContext


class MyCharacteristic(BaseCharacteristic):
    """My Characteristic (0x2AXX).

    org.bluetooth.characteristic.my_characteristic
    """

    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 100.0
    expected_type: type = float

    def decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None
    ) -> float:
        raw = DataParser.parse_int16(data, 0, signed=False)
        return raw * 0.01

    def encode_value(self, data: float) -> bytearray:
        return DataParser.encode_int16(int(data / 0.01), signed=False)
```

## Custom Characteristics

For vendor-specific characteristics, extend :class:`~bluetooth_sig.gatt.characteristics.custom.CustomBaseCharacteristic`:

```python
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.exceptions import (
    InsufficientDataError,
    ValueRangeError,
)
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class LightLevelCharacteristic(CustomBaseCharacteristic):
    """Light Level characteristic.

    Reports ambient light level as a percentage (0-100%).

    Format:
      - 1 byte: uint8
      - Range: 0-100
      - Unit: percentage
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("ABCD"),  # Your custom UUID
        name="Light Level",
        unit="%",
    )

    def decode_value(self, data: bytearray) -> int:
        """Decode light level.

        Args:
            data: Raw bytes (1 byte expected)

        Returns:
            Light level percentage (0-100)
        """
        # Validate length
        if len(data) != 1:
            raise InsufficientDataError(
                f"Light Level requires exactly 1 byte, got {len(data)}"
            )

        # Parse
        value = int(data[0])

        # Validate range
        if not 0 <= value <= 100:
            raise ValueRangeError(f"Light level must be 0-100%, got {value}%")

        return value
```

## Example: Complex Multi-Field Characteristic

For characteristics with multiple fields:

```python
from datetime import datetime

import msgspec


class SensorReading(msgspec.Struct, frozen=True, kw_only=True):
    """Multi-field sensor reading."""

    temperature: float
    humidity: float
    pressure: float
    timestamp: datetime
```

```python
class MultiSensorCharacteristic(CustomBaseCharacteristic):
    """Multi-sensor characteristic with multiple fields."""

    _info = CharacteristicInfo(uuid=BluetoothUUID("WXYZ"), name="Multi Sensor")

    def decode_value(self, data: bytearray) -> SensorReading:
        """Decode multi-field sensor data.

        Format:
          Bytes 0-1: Temperature (sint16, 0.01°C)
          Bytes 2-3: Humidity (uint16, 0.01%)
          Bytes 4-7: Pressure (uint32, 0.1 Pa)
          Bytes 8-15: Timestamp (64-bit Unix timestamp)
        """
        # Validate length
        if len(data) != 16:
            raise InsufficientDataError(
                f"Multi Sensor requires 16 bytes, got {len(data)}"
            )

        # Parse temperature
        temp_raw = int.from_bytes(data[0:2], byteorder="little", signed=True)
        temperature = temp_raw * 0.01

        # Parse humidity
        hum_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        humidity = hum_raw * 0.01

        # Parse pressure
        press_raw = int.from_bytes(data[4:8], byteorder="little", signed=False)
        pressure = press_raw * 0.1

        # SKIP: Incomplete class definition example
        # Parse timestamp
        ts_raw = int.from_bytes(data[8:16], byteorder="little", signed=False)
        timestamp = ts_raw  # Unix timestamp

        return SensorReading(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            timestamp=timestamp,
        )
```

## Testing Your Characteristic

Always add tests for your custom characteristic:

```python
import pytest

from bluetooth_sig.gatt.exceptions import (
    InsufficientDataError,
    ValueRangeError,
)


class TestLightLevelCharacteristic:
    """Test Light Level characteristic."""

    def test_valid_value(self):
        """Test valid light level."""
        char = LightLevelCharacteristic()
        result = char.decode_value(bytearray([50]))
        assert result == 50

    def test_boundary_values(self):
        """Test boundary values."""
        char = LightLevelCharacteristic()
        assert char.decode_value(bytearray([0])) == 0
        assert char.decode_value(bytearray([100])) == 100

    def test_insufficient_data(self):
        """Test error on insufficient data."""
        char = LightLevelCharacteristic()
        with pytest.raises(InsufficientDataError):
            char.decode_value(bytearray([]))

    def test_out_of_range(self):
        """Test error on out-of-range value."""
        char = LightLevelCharacteristic()
        with pytest.raises(ValueRangeError):
            char.decode_value(bytearray([101]))
```

## Contributing Back

If you've added a standard Bluetooth SIG characteristic,
consider contributing it back:

1. Ensure your implementation follows the official specification
1. Add comprehensive tests
1. Add proper docstrings
1. Open a pull request

See [Contributing Guide](contributing.md) for details.

## See Also

- [Architecture](../explanation/architecture/overview.md) - Understand the design
- [Testing Guide](testing.md) - Testing best practices
- [API Reference](../api/index.md) - GATT layer details
