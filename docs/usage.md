# Usage

To use BLE GATT Device in a project:

```python
import ble_gatt_device

# Create a BLE GATT device instance
device = ble_gatt_device.BLEGATTDevice("AA:BB:CC:DD:EE:FF")

# Connect and read characteristics
await device.connect()
characteristics = await device.read_parsed_characteristics()
print(characteristics)

await device.disconnect()
```

## Basic Example

```python
import asyncio
from ble_gatt_device import BLEGATTDevice

async def main():
    device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
    
    try:
        await device.connect()
        
        # Read raw characteristic data
        raw_data = await device.read_characteristics()
        
        # Read parsed characteristic data with units
        parsed_data = await device.read_parsed_characteristics()
        
        # Get device information
        device_info = await device.get_device_info()
        
        print("Raw data:", raw_data)
        print("Parsed data:", parsed_data)
        print("Device info:", device_info)
        
    finally:
        await device.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```
