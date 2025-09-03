# Usage

To use Bluetooth SIG Standards Library in a project:

```python
from bluetooth_sig.core import BluetoothSIGTranslator

# Create translator instance
translator = BluetoothSIGTranslator()

# Resolve UUIDs to get information
service_info = translator.resolve_uuid("180F")  # Battery Service
char_info = translator.resolve_uuid("2A19")    # Battery Level

print(f"Service: {service_info.name}")
print(f"Characteristic: {char_info.name}")
```

## Basic Example

```python
from bluetooth_sig.core import BluetoothSIGTranslator

def main():
    translator = BluetoothSIGTranslator()

    # UUID resolution
    uuid_info = translator.resolve_uuid("180F")
    print(f"UUID 180F: {uuid_info.name}")

    # Name resolution
    name_info = translator.resolve_name("Battery Level")
    print(f"Battery Level UUID: {name_info.uuid}")

    # Data parsing
    parsed = translator.parse_characteristic_data("2A19", bytearray([85]))
    print(f"Battery level: {parsed.value}%")

if __name__ == "__main__":
    main()
```
