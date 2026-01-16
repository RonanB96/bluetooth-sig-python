# Advertising Parsing

Parse BLE advertising packets to extract device information, service UUIDs, and manufacturer data before establishing a connection.

## When to Use Advertising Parsing

- **Device scanning** — Identify nearby BLE devices by name or services
- **Beacon detection** — Read iBeacon, Eddystone, or custom beacon data
- **Passive monitoring** — Collect broadcast data without connecting
- **Pre-connection filtering** — Check if a device supports required services

## Basic Usage

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()

# raw_bytes comes from your BLE library (bleak, simplepyble, etc.)
# Example: Flags (0x02, 0x01, 0x06) + Complete Local Name "Test"
raw_bytes = bytearray([0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74])
advertising_data = parser.parse_advertising_data(raw_bytes)

# Access parsed fields
if advertising_data.ad_structures.core.local_name:
    print(f"Device: {advertising_data.ad_structures.core.local_name}")
```

## Extracting Advertising Fields

The `AdvertisingData` object organises fields into logical groups. Here's how to extract common fields:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.advertising import AdvertisingPDUParser

translator = BluetoothSIGTranslator()
parser = AdvertisingPDUParser()

# Example: Flags + Local Name "Sensor" + Battery Service UUID (0x180F)
raw_bytes = bytearray(
    [
        0x02,
        0x01,
        0x06,  # Flags
        0x07,
        0x09,
        0x53,
        0x65,
        0x6E,
        0x73,
        0x6F,
        0x72,  # Complete Local Name "Sensor"
        0x03,
        0x03,
        0x0F,
        0x18,  # Complete List of 16-bit Service UUIDs: 0x180F
    ]
)
advertising_data = parser.parse_advertising_data(raw_bytes)

# Device name
name = advertising_data.ad_structures.core.local_name

# Service UUIDs - identify what the device supports
for uuid in advertising_data.ad_structures.core.service_uuids:
    service_info = translator.get_service_info_by_uuid(str(uuid))
    if service_info:
        print(f"{uuid.short_form}: {service_info.name}")

# Manufacturer data - vendor-specific payloads
for (
    company_id,
    data,
) in advertising_data.ad_structures.core.manufacturer_data.items():
    print(f"Company 0x{company_id:04X}: {data.hex()}")

# Service data - characteristic values broadcast without connection
for (
    service_uuid,
    data,
) in advertising_data.ad_structures.core.service_data.items():
    print(f"Service {service_uuid}: {data.hex()}")

# Signal strength
tx_power = advertising_data.ad_structures.properties.tx_power
rssi = advertising_data.rssi
```

**Available field groups:**

| Group      | Path                       | Contents                                                           |
| ---------- | -------------------------- | ------------------------------------------------------------------ |
| Core       | `ad_structures.core`       | `local_name`, `service_uuids`, `manufacturer_data`, `service_data` |
| Properties | `ad_structures.properties` | `tx_power`, `flags`, `appearance`                                  |
| Location   | `ad_structures.location`   | `indoor_positioning`, `transport_discovery_data`                   |
| Security   | `ad_structures.security`   | `encrypted_advertising_data`                                       |
| Mesh       | `ad_structures.mesh`       | `mesh_message`, `mesh_beacon`, `broadcast_name`                    |

## Extended Advertising (BLE 5.0+)

The parser automatically detects extended advertising PDUs (BLE 5.0+), which support larger payloads and additional metadata:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()

# Standard advertising data
raw_bytes = bytearray(
    [
        0x02,
        0x01,
        0x06,  # Flags
        0x05,
        0x09,
        0x54,
        0x65,
        0x73,
        0x74,  # Complete Local Name "Test"
    ]
)
advertising_data = parser.parse_advertising_data(raw_bytes)

# Check for extended advertising fields
if advertising_data.extended:
    print(f"PHY: {advertising_data.extended.primary_phy}")
    print(f"Data status: {advertising_data.extended.data_status}")
```

## Filtering Devices

### By Service UUID

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import ServiceName

translator = BluetoothSIGTranslator()
battery_uuid = translator.get_service_uuid_by_name(ServiceName.BATTERY)


def has_battery_service(advertising_data):
    return battery_uuid in advertising_data.ad_structures.core.service_uuids
```

### By Manufacturer

```python
APPLE_COMPANY_ID = 0x004C


def is_apple_device(advertising_data):
    return (
        APPLE_COMPANY_ID
        in advertising_data.ad_structures.core.manufacturer_data
    )
```

### By Name Pattern

```python
import re


def matches_name_pattern(advertising_data, pattern):
    name = advertising_data.ad_structures.core.local_name
    if name:
        return re.match(pattern, name) is not None
    return False


# Example: Create sample advertising data to test the filter
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()
# Advertising data with name "Sensor_42"
sample_bytes = bytearray(
    [
        0x02,
        0x01,
        0x06,
        0x0A,
        0x09,
        0x53,
        0x65,
        0x6E,
        0x73,
        0x6F,
        0x72,
        0x5F,
        0x34,
        0x32,
    ]
)
advertising_data = parser.parse_advertising_data(sample_bytes)

# Find devices starting with "Sensor_"
if matches_name_pattern(advertising_data, r"Sensor_\d+"):
    print("Found sensor device")
```

## Custom Advertising Interpreters

For vendor-specific advertising protocols (BTHome, Xiaomi, RuuviTag, etc.), create custom interpreters that convert raw advertising data into typed sensor readings.

### Architecture Overview

The library uses a two-layer architecture:

1. **PDU Parsing** (`AdvertisingPDUParser`) — Raw bytes → AD structures
2. **Data Interpretation** (`AdvertisingDataInterpreter`) — AD structures → typed results

Custom interpreters implement the second layer.

### Creating a Custom Interpreter

```python
from typing import Any

import msgspec

from bluetooth_sig.advertising import (
    AdvertisingDataInterpreter,
    AdvertisingInterpreterInfo,
    DataSource,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class MySensorData(msgspec.Struct):
    """Typed result from my sensor protocol."""

    temperature: float
    humidity: float
    battery: int


class MySensorInterpreter(AdvertisingDataInterpreter[MySensorData]):
    """Interpreter for My Sensor advertising protocol."""

    _info = AdvertisingInterpreterInfo(
        company_id=0x1234,  # Your company ID
        name="My Sensor",
        data_source=DataSource.MANUFACTURER,
    )

    @classmethod
    def supports(
        cls,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
    ) -> bool:
        """Check if this interpreter handles the advertisement."""
        # Quick check based on company ID presence
        return 0x1234 in manufacturer_data

    def interpret(
        self,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
        rssi: int,
    ) -> MySensorData:
        """Parse manufacturer data into typed result."""
        data = manufacturer_data[0x1234]

        # Parse your protocol (example format)
        temperature = int.from_bytes(data[0:2], "little") / 100.0
        humidity = int.from_bytes(data[2:4], "little") / 100.0
        battery = data[4]

        return MySensorData(
            temperature=temperature,
            humidity=humidity,
            battery=battery,
        )
```

### Service-Based Interpreters

For protocols using service data instead of manufacturer data:

```python
import msgspec

from bluetooth_sig.advertising import (
    AdvertisingDataInterpreter,
    AdvertisingInterpreterInfo,
    DataSource,
)
from bluetooth_sig.types.uuid import BluetoothUUID

BTHOME_UUID = BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb")


class BTHomeData(msgspec.Struct):
    """Typed result from BTHome protocol."""

    temperature: float | None = None
    humidity: float | None = None
    battery: int | None = None


class BTHomeInterpreter(AdvertisingDataInterpreter[BTHomeData]):
    """Example BTHome-style interpreter."""

    _info = AdvertisingInterpreterInfo(
        service_uuid=BTHOME_UUID,
        name="BTHome",
        data_source=DataSource.SERVICE,
    )

    @classmethod
    def supports(
        cls,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
    ) -> bool:
        return BTHOME_UUID in service_data

    def interpret(
        self,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
        rssi: int,
    ) -> BTHomeData:
        data = service_data[BTHOME_UUID]
        # Parse BTHome format (simplified example)
        return BTHomeData(temperature=22.5, humidity=45.0, battery=85)
```

### Auto-Registration

Interpreters are automatically registered when defined (via `__init_subclass__`). The registry routes advertisements to the appropriate interpreter.

### Using the Registry

```python
from bluetooth_sig.advertising import (
    AdvertisingPDUParser,
    advertising_interpreter_registry,
)

parser = AdvertisingPDUParser()

# Example: Advertising data with manufacturer data (Company ID 0x1234)
# Payload: temp=100 (0x0064), humidity=50 (0x0032), battery=85 (0x55)
raw_bytes = bytearray(
    [
        0x02,
        0x01,
        0x06,  # Flags
        0x08,
        0xFF,
        0x34,
        0x12,
        0x64,
        0x00,
        0x32,
        0x00,
        0x55,  # Manufacturer data (5 bytes)
    ]
)
advertising_data = parser.parse_advertising_data(raw_bytes)

# Find interpreter for this advertisement
interpreter_class = advertising_interpreter_registry.find_interpreter_class(
    manufacturer_data=advertising_data.ad_structures.core.manufacturer_data,
    service_data=advertising_data.ad_structures.core.service_data,
    local_name=advertising_data.ad_structures.core.local_name,
)

if interpreter_class:
    # Create interpreter instance for this device
    interpreter = interpreter_class(mac_address="AA:BB:CC:DD:EE:FF")

    # Interpret the data
    result = interpreter.interpret(
        manufacturer_data=advertising_data.ad_structures.core.manufacturer_data,
        service_data=advertising_data.ad_structures.core.service_data,
        local_name=advertising_data.ad_structures.core.local_name,
        rssi=advertising_data.rssi or 0,
    )
    print(f"Interpreted: {result}")
```

### Encrypted Advertising

For protocols with encrypted payloads, pass a bindkey:

```python
# SKIP: Depends on MySensorInterpreter class defined in previous examples
interpreter = MySensorInterpreter(
    mac_address="AA:BB:CC:DD:EE:FF",
    bindkey=bytes.fromhex("0123456789ABCDEF0123456789ABCDEF"),
)

# Access bindkey in interpret() method
# self.bindkey contains the encryption key
```

### Stateful Interpreters

Interpreters maintain state across calls (useful for packet counters, replay protection):

```python
class StatefulInterpreter(AdvertisingDataInterpreter[MySensorData]):
    def interpret(self, manufacturer_data, service_data, local_name, rssi):
        # Access persistent state
        last_packet_id = self.state.get("last_packet_id", 0)

        # Parse current packet
        current_id = manufacturer_data[0x1234][0]

        if current_id <= last_packet_id:
            raise ValueError("Replay detected")

        # Update state
        self.state["last_packet_id"] = current_id

        # Continue parsing...
```

### Unregistering Interpreters

```python
# SKIP: Depends on MySensorInterpreter class defined in previous examples
from bluetooth_sig.advertising import advertising_interpreter_registry

# Remove a specific interpreter
advertising_interpreter_registry.unregister(MySensorInterpreter)
```

## See Also

- [API Overview](../explanation/api-overview.md#advertising-parsing) — Conceptual overview
- [Import Patterns](import-patterns.md) — Correct import statements
- [examples/advertising_parsing.py](https://github.com/RonanB96/bluetooth-sig-python/blob/main/examples/advertising_parsing.py) — Complete working example
