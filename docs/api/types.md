# Types & Enums API Reference

Type definitions and enumerations used throughout the library.

## Enumerations

### CharacteristicName

Enumeration of standard characteristic names.

```python
from bluetooth_sig.types.gatt_enums import CharacteristicName

CharacteristicName.BATTERY_LEVEL  # "Battery Level"
CharacteristicName.TEMPERATURE    # "Temperature"
CharacteristicName.HUMIDITY       # "Humidity"
```

### ServiceName

Enumeration of standard service names.

```python
from bluetooth_sig.types.gatt_enums import ServiceName

ServiceName.BATTERY_SERVICE           # "Battery Service"
ServiceName.ENVIRONMENTAL_SENSING     # "Environmental Sensing"
ServiceName.DEVICE_INFORMATION        # "Device Information"
```

## Data Types

### UUIDInfo

Information about a UUID.

```python
from bluetooth_sig.types import UUIDInfo

info = UUIDInfo(
    uuid="2A19",
    name="Battery Level",
    type="characteristic"
)
```

### CharacteristicInfo

Extended information for characteristics.

```python
from bluetooth_sig.types import CharacteristicInfo

info = CharacteristicInfo(
    uuid="2A19",
    name="Battery Level"
)
```

## See Also

- [Core API](core.md) - Using these types
- [GATT API](gatt.md) - Characteristic implementations
