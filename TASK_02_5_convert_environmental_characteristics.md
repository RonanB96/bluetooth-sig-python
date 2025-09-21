# Task 2.5: Convert Environmental Characteristics

## Priority: Phase 2 - After Phase 1 complete

## Parallelization: Can run in parallel with other 2.x tasks

## Objective

Standardize environmental sensor characteristics using appropriate template classes and eliminate duplicate parsing logic.

## Files to Convert

1. `src/bluetooth_sig/gatt/characteristics/temperature.py`
2. `src/bluetooth_sig/gatt/characteristics/humidity.py`
3. `src/bluetooth_sig/gatt/characteristics/pressure.py`
4. `src/bluetooth_sig/gatt/characteristics/elevation.py`
5. `src/bluetooth_sig/gatt/characteristics/wind_chill.py`
6. `src/bluetooth_sig/gatt/characteristics/heat_index.py`
7. `src/bluetooth_sig/gatt/characteristics/apparent_wind_direction.py`
8. `src/bluetooth_sig/gatt/characteristics/apparent_wind_speed.py`
9. `src/bluetooth_sig/gatt/characteristics/true_wind_direction.py`
10. `src/bluetooth_sig/gatt/characteristics/true_wind_speed.py`
11. `src/bluetooth_sig/gatt/characteristics/magnetic_declination.py`
12. `src/bluetooth_sig/gatt/characteristics/magnetic_flux_density_2d.py`
13. `src/bluetooth_sig/gatt/characteristics/magnetic_flux_density_3d.py`
14. `src/bluetooth_sig/gatt/characteristics/high_voltage.py`
15. `src/bluetooth_sig/gatt/characteristics/tx_power_level.py`

## Template Mapping Strategy

### TemperatureCharacteristic Template (5 files)
Use for temperature-related measurements:
- `temperature.py` → TemperatureCharacteristic
- `wind_chill.py` → TemperatureCharacteristic
- `heat_index.py` → TemperatureCharacteristic

### SimpleUint16Characteristic Template (7 files)
Use for basic 16-bit measurements:
- `humidity.py` → SimpleUint16Characteristic + custom resolution
- `elevation.py` → SimpleUint16Characteristic + custom resolution
- `apparent_wind_direction.py` → SimpleUint16Characteristic + custom resolution
- `true_wind_direction.py` → SimpleUint16Characteristic + custom resolution
- `apparent_wind_speed.py` → SimpleUint16Characteristic + custom resolution
- `true_wind_speed.py` → SimpleUint16Characteristic + custom resolution
- `magnetic_declination.py` → SimpleUint16Characteristic + custom resolution

### Custom Template Inheritance (3 files)
For complex measurements requiring custom templates:
- `pressure.py` → Custom pressure template (uint32)
- `magnetic_flux_density_2d.py` → Custom vector template
- `magnetic_flux_density_3d.py` → Custom vector template
- `high_voltage.py` → SimpleUint16Characteristic + custom resolution
- `tx_power_level.py` → Custom signed power template

## Specific Conversions

### temperature.py

```python
from __future__ import annotations
from .templates import TemperatureCharacteristic

class TemperatureCharacteristic(TemperatureCharacteristic):
    """Environmental temperature measurement per SIG spec."""
    # All functionality inherited from template
    pass
```

### humidity.py

```python
from __future__ import annotations
from .templates import SimpleUint16Characteristic

class HumidityCharacteristic(SimpleUint16Characteristic):
    """Humidity measurement per SIG spec."""

    def decode_value(self, data: bytearray) -> float:
        """Parse humidity with 0.01% resolution."""
        raw_value = super().decode_value(data)
        return raw_value * 0.01

    def encode_value(self, value: float) -> bytearray:
        """Encode humidity to bytes."""
        raw_value = int(value / 0.01)
        return super().encode_value(raw_value)

    @property
    def unit(self) -> str:
        return "%"
```

### pressure.py

```python
from __future__ import annotations
from .base import BaseCharacteristic
from .utils import DataParser

class PressureCharacteristic(BaseCharacteristic):
    """Pressure measurement per SIG spec."""

    expected_length = 4
    min_value = 0.0
    max_value = 429496729.5  # Max uint32 * 0.1
    expected_type = float

    def decode_value(self, data: bytearray) -> float:
        """Parse pressure in Pa, convert to hPa."""
        raw_value = DataParser.parse_int32(data, 0, signed=False)
        pressure_pa = raw_value * 0.1
        return pressure_pa / 100.0  # Convert Pa to hPa

    def encode_value(self, value: float) -> bytearray:
        """Encode pressure to bytes."""
        pressure_pa = value * 100.0  # Convert hPa to Pa
        raw_value = int(pressure_pa / 0.1)
        return DataParser.encode_int32(raw_value, signed=False)

    @property
    def unit(self) -> str:
        return "hPa"
```

### wind_speed characteristics (apparent_wind_speed.py, true_wind_speed.py)

```python
from __future__ import annotations
from .templates import SimpleUint16Characteristic

class ApparentWindSpeedCharacteristic(SimpleUint16Characteristic):
    """Apparent wind speed measurement per SIG spec."""

    def decode_value(self, data: bytearray) -> float:
        """Parse wind speed with 0.01 m/s resolution."""
        raw_value = super().decode_value(data)
        return raw_value * 0.01

    def encode_value(self, value: float) -> bytearray:
        """Encode wind speed to bytes."""
        raw_value = int(value / 0.01)
        return super().encode_value(raw_value)

    @property
    def unit(self) -> str:
        return "m/s"
```

### wind_direction characteristics (apparent_wind_direction.py, true_wind_direction.py)

```python
from __future__ import annotations
from .templates import SimpleUint16Characteristic

class ApparentWindDirectionCharacteristic(SimpleUint16Characteristic):
    """Apparent wind direction measurement per SIG spec."""

    max_value = 359  # 0-359 degrees

    def decode_value(self, data: bytearray) -> float:
        """Parse wind direction with 0.01 degree resolution."""
        raw_value = super().decode_value(data)
        return raw_value * 0.01

    def encode_value(self, value: float) -> bytearray:
        """Encode wind direction to bytes."""
        raw_value = int(value / 0.01)
        return super().encode_value(raw_value)

    @property
    def unit(self) -> str:
        return "°"
```

### magnetic_flux_density_2d.py

```python
from __future__ import annotations
from .base import BaseCharacteristic
from .utils import DataParser

class MagneticFluxDensity2DCharacteristic(BaseCharacteristic):
    """2D magnetic flux density measurement per SIG spec."""

    expected_length = 4  # 2x uint16
    expected_type = dict

    def decode_value(self, data: bytearray) -> dict:
        """Parse X and Y magnetic flux density."""
        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)

        # Convert to Tesla with resolution
        x_tesla = x_raw * 1e-7  # 0.1 μT resolution
        y_tesla = y_raw * 1e-7

        return {
            "x": x_tesla,
            "y": y_tesla
        }

    def encode_value(self, value: dict) -> bytearray:
        """Encode 2D magnetic flux density to bytes."""
        x_raw = int(value["x"] / 1e-7)
        y_raw = int(value["y"] / 1e-7)

        result = bytearray()
        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))
        return result

    @property
    def unit(self) -> str:
        return "T"
```

### tx_power_level.py

```python
from __future__ import annotations
from .base import BaseCharacteristic
from .utils import DataParser

class TxPowerLevelCharacteristic(BaseCharacteristic):
    """TX power level measurement per SIG spec."""

    expected_length = 1
    min_value = -127
    max_value = 127
    expected_type = int

    def decode_value(self, data: bytearray) -> int:
        """Parse TX power level in dBm."""
        return DataParser.parse_int8(data, 0, signed=True)

    def encode_value(self, value: int) -> bytearray:
        """Encode TX power level to bytes."""
        return DataParser.encode_int8(value, signed=True)

    @property
    def unit(self) -> str:
        return "dBm"
```

## Conversion Process

### Step 1: Analyze Current Implementation
For each file:
- Identify data format (uint8/16/32, sint16, etc.)
- Determine resolution and units
- Check for validation patterns
- Map to appropriate template

### Step 2: Choose Template Strategy
- Simple values → use appropriate template
- Complex values → inherit from BaseCharacteristic
- Temperature-like → use TemperatureCharacteristic
- Percentage-like → use specific resolution

### Step 3: Implement Conversion
- Update imports
- Change inheritance
- Add resolution/unit properties
- Remove manual parsing/validation
- Test functionality

## Success Criteria

- All environmental characteristics use appropriate templates or standardized patterns
- No manual parsing remains (int.from_bytes, struct.unpack)
- Consistent resolution and unit handling
- All validation handled by base classes
- File sizes reduced significantly
- All tests continue to pass

## Dependencies

- **REQUIRES**: Task 1.2 (Templates) must complete first
- **PARALLEL**: Can run with other 2.x tasks
- **ENABLES**: Phase 3 quality assurance

## Testing

```bash
# Test environmental characteristics
python -c "
from src.bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic
from src.bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
temp = TemperatureCharacteristic()
humid = HumidityCharacteristic()
print('✅ Environmental characteristics working')
"

# Test parsing
python -m pytest tests/ -k "temperature or humidity or pressure" -v
```

## Expected Code Reduction

- Remove 300+ lines of duplicate parsing code
- Eliminate 60+ manual validation checks
- Standardize resolution handling across all environmental sensors
- Reduce average file size by 60-70%
