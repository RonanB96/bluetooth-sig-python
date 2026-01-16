# API Overview

This library provides a complete toolkit for Bluetooth Low Energy development:

- **Device abstraction** — High-level API combining characteristics, services, and connection management
- **Characteristic parsing** — Decode and encode GATT characteristic values
- **Service organisation** — Group characteristics into services
- **Advertising parsing** — Extract data from BLE advertising packets

---

## Quick Reference

Not a complete list, see individual guides for details.

| Feature                | API                                             | Returns           |
| ---------------------- | ----------------------------------------------- | ----------------- |
| **Device**             |                                                 |                   |
| Read characteristic    | `device.read(CharacteristicClass)`              | Typed value       |
| Discover services      | `device.discover_services()`                    | Service map       |
| Parse advertising      | `device.parse_raw_advertisement()`              | —                 |
| **Characteristics**    |                                                 |                   |
| Parse with type safety | `CharacteristicClass().parse_value()`           | Typed value       |
| Parse dynamically      | `translator.parse_characteristic()`             | `Any`             |
| **Services**           |                                                 |                   |
| Look up service info   | `translator.get_service_info_by_uuid()`         | `ServiceInfo`     |
| **Advertising**        |                                                 |                   |
| Parse advertising PDU  | `AdvertisingPDUParser.parse_advertising_data()` | `AdvertisingData` |

---

## Device Abstraction

The `Device` class provides a unified interface for interacting with BLE devices, combining characteristic parsing, service discovery, and connection management.

```python
# SKIP: Requires BLE connection manager
from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

device = Device(connection_manager, BluetoothSIGTranslator())
await device.connect()

# Read characteristics
battery = await device.read(BatteryLevelCharacteristic)

# Discover services
await device.discover_services()

# Parse advertising data
device.parse_raw_advertisement(raw_adv_bytes)
```

**Capabilities:**

- Characteristic reads (type-safe with classes, dynamic with UUIDs)
- Service discovery and caching
- Advertising data parsing
- Encryption requirements tracking
- Automatic dependency resolution

**Requires:** A connection manager implementing `ConnectionManagerProtocol`.

See [BLE Integration Guide](../how-to/ble-integration.md) for connection manager examples.

---

## Characteristic Parsing

Two approaches for parsing characteristics directly (without the Device abstraction).

### Characteristic Classes

Use when you know the characteristic type at development time:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)

battery_data = bytearray([85])  # 85% battery
hr_data_raw = bytearray([0x00, 72])  # Heart rate 72 bpm

battery = BatteryLevelCharacteristic()
level = battery.parse_value(battery_data)  # IDE infers: int

heart_rate = HeartRateMeasurementCharacteristic()
hr_data = heart_rate.parse_value(hr_data_raw)  # IDE infers: HeartRateData
print(f"BPM: {hr_data.heart_rate}")  # Full autocomplete
```

### Translator with UUIDs

Use when UUIDs are discovered at runtime:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# UUID discovered at runtime
raw_data = bytearray([75])  # Battery level 75%
value = translator.parse_characteristic("2A19", raw_data)  # Returns Any

info = translator.get_characteristic_info_by_uuid("2A19")
print(f"{info.name}: {value}")
```

See [Characteristics Guide](../how-to/characteristics.md) for more patterns.

---

## Service Organisation

GATT services group related characteristics together. Service classes define which characteristics belong to a service and their requirements (mandatory vs optional).

```python
from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)
from bluetooth_sig.gatt.services import HeartRateService

# Create service instance
service = HeartRateService()

# Get expected characteristics
print(f"Required: {[c.name for c in service.get_required_characteristics()]}")
print(f"Optional: {[c.name for c in service.get_optional_characteristics()]}")

# Validate discovered characteristics (from BLE service discovery)
hr_char = HeartRateMeasurementCharacteristic()
discovered_characteristics = {hr_char.uuid: hr_char.info}
service.process_characteristics(discovered_characteristics)
report = service.get_service_completeness_report()
print(f"Health: {report.health_status.value}")
print(f"Missing required: {[c.name for c in report.missing_required]}")
```

See [Services Guide](../how-to/services.md) for validation and health checking.

---

## Advertising Parsing

BLE devices broadcast advertising packets containing device information, service UUIDs, and manufacturer data. The `AdvertisingPDUParser` extracts structured data from raw advertising bytes.

### Parsing Advertising Data

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()

# Example advertising data (replace with bytes from your BLE library)
raw_bytes = bytearray([0x02, 0x01, 0x06])  # Flags: LE General Discoverable

# Parse raw advertising bytes
advertising_data = parser.parse_advertising_data(raw_bytes)

# Access parsed fields (when present)
if advertising_data.ad_structures.core.local_name:
    print(f"Device name: {advertising_data.ad_structures.core.local_name}")
if advertising_data.ad_structures.properties.tx_power is not None:
    print(
        f"TX Power: {advertising_data.ad_structures.properties.tx_power} dBm"
    )

# Service UUIDs advertised by the device
for uuid in advertising_data.ad_structures.core.service_uuids:
    print(f"Service: {uuid.short_form}")

# Manufacturer-specific data
for (
    company_id,
    data,
) in advertising_data.ad_structures.core.manufacturer_data.items():
    print(f"Company 0x{company_id:04X}: {data.hex()}")
```

### Interpreting Service Data

Combine advertising parsing with the translator to interpret service data:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.advertising import AdvertisingPDUParser

translator = BluetoothSIGTranslator()
parser = AdvertisingPDUParser()

# Example: Flags + Complete Local Name
raw_bytes = bytearray([0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74])
advertising_data = parser.parse_advertising_data(raw_bytes)

# Resolve service UUIDs to names
for uuid in advertising_data.ad_structures.core.service_uuids:
    service_info = translator.get_service_info_by_uuid(str(uuid))
    if service_info:
        print(f"{uuid.short_form}: {service_info.name}")
```

### Extended Advertising (BLE 5.0+)

The parser automatically detects and handles extended advertising PDUs:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()

# Example extended advertising data
extended_pdu_bytes = bytearray([0x02, 0x01, 0x06])
advertising_data = parser.parse_advertising_data(extended_pdu_bytes)

if advertising_data.extended:
    print("Extended advertising detected")
    if advertising_data.extended.extended_payload:
        print(
            f"Extended payload: {advertising_data.extended.extended_payload.hex()}"
        )
```

See [Advertising Parsing Guide](../how-to/advertising-parsing.md) for custom interpreters and filtering.
