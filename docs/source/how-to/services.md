# Working with GATT Services

GATT services group related characteristics and define which are required, optional, or conditional. The library provides service classes that mirror Bluetooth SIG service definitions, including validation, health checking, and compliance verification.

## When to Use Service Classes

- **Device identification** — Determine device capabilities from advertised services
- **Validation** — Check if a device has all required characteristics
- **Health monitoring** — Track service completeness over time
- **Compliance checking** — Verify Bluetooth SIG specification compliance
- **Characteristic grouping** — Understand which characteristics belong together

## Looking Up Service Information

### By UUID

When you discover a service UUID from a device, look up its metadata:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Short UUID (common format)
service_info = translator.get_service_info_by_uuid("180F")
print(f"Service: {service_info.name}")  # "Battery Service"

# Full 128-bit UUID also works
service_info = translator.get_service_info_by_uuid(
    "0000180F-0000-1000-8000-00805F9B34FB"
)
```

### By Enum Name

For compile-time safety, use the `ServiceName` enum:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import ServiceName

translator = BluetoothSIGTranslator()

service_info = translator.get_service_info_by_name(ServiceName.BATTERY)
print(f"UUID: {service_info.uuid}")
```

## Using Service Classes

Service classes define which characteristics belong to a service and their requirements:

```python
from bluetooth_sig.gatt.services import (
    BatteryService,
    HeartRateService,
)

# Get service UUID for filtering
battery_uuid = BatteryService.get_class_uuid()
print(f"Battery Service UUID: {battery_uuid}")

# Get service name without instantiation
name = HeartRateService.get_name()
print(f"Service name: {name}")
```

### Characteristic Requirements

Services define which characteristics are required, optional, or conditional:

```python
from bluetooth_sig.gatt.services import HeartRateService

# Required characteristics (must be present)
required = HeartRateService.get_required_characteristics()
for char_name, spec in required.items():
    print(f"Required: {char_name.value}")

# Optional characteristics (may be present)
optional = HeartRateService.get_optional_characteristics()
for char_name, spec in optional.items():
    print(f"Optional: {char_name.value}")

# All expected characteristics
expected = HeartRateService.get_expected_characteristics()
print(f"Total expected: {len(expected)}")

# Get UUIDs to filter for when connecting
service = HeartRateService()
required_uuids = service.get_required_characteristic_uuids()
print(f"Required UUIDs: {[str(u) for u in required_uuids]}")
```

## Service Validation

After discovering characteristics from a device, validate service completeness:

### Basic Validation

```python
from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ============================================
# SIMULATED DATA - Replace with actual BLE discovery
# ============================================
# Simulate discovered characteristics from a Heart Rate Service
# Keys are BluetoothUUIDs, values are CharacteristicInfo
discovered_characteristics = {
    BluetoothUUID("2A37"): CharacteristicInfo(
        uuid=BluetoothUUID("2A37"),
        name="Heart Rate Measurement",
    ),
    BluetoothUUID("2A38"): CharacteristicInfo(
        uuid=BluetoothUUID("2A38"),
        name="Body Sensor Location",
    ),
}

# Create service and populate with discovered characteristics
service = GattServiceRegistry.create_service(
    uuid="180D",
    characteristics=discovered_characteristics,  # From BLE library
)

if service:
    # Validate the service
    result = service.validate_service()

    print(
        f"Status: {result.status.value}"
    )  # complete, functional, partial, incomplete
    print(f"Is healthy: {result.is_healthy}")
    print(f"Has errors: {result.has_errors}")

    if result.missing_required:
        print("Missing required characteristics:")
        for char in result.missing_required:
            print(f"  - {char.name}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
```

### Health Status

Services report their health status:

| Status | Meaning |
| --- | --- |
| `COMPLETE` | All required and optional characteristics present |
| `FUNCTIONAL` | All required present, some optional missing |
| `PARTIAL` | Some required characteristics missing but usable |
| `INCOMPLETE` | Critical required characteristics missing |

```python
from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.gatt.services.base import ServiceHealthStatus
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ============================================
# SIMULATED DATA - Replace with actual BLE discovery
# ============================================
discovered_characteristics = {
    BluetoothUUID("2A37"): CharacteristicInfo(
        uuid=BluetoothUUID("2A37"),
        name="Heart Rate Measurement",
    ),
}

# Create and validate service
service = GattServiceRegistry.create_service(
    uuid="180D",
    characteristics=discovered_characteristics,
)

if service:
    result = service.validate_service()

    if result.status == ServiceHealthStatus.COMPLETE:
        print("Service is fully complete")
    elif result.status == ServiceHealthStatus.FUNCTIONAL:
        print("Service is functional but missing optional features")
    elif result.status == ServiceHealthStatus.PARTIAL:
        print("Service has reduced functionality")
    else:
        print("Service is not usable")
```

## Completeness Reports

Get detailed reports about service state:

```python
from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ============================================
# SIMULATED DATA - Replace with actual BLE discovery
# ============================================
discovered_characteristics = {
    BluetoothUUID("2A37"): CharacteristicInfo(
        uuid=BluetoothUUID("2A37"),
        name="Heart Rate Measurement",
    ),
}

# Create service
service = GattServiceRegistry.create_service(
    uuid="180D",
    characteristics=discovered_characteristics,
)

if not service:
    raise RuntimeError("Service not found")

report = service.get_service_completeness_report()

print(f"Service: {report.service_name}")
print(f"UUID: {report.service_uuid}")
print(f"Health: {report.health_status.value}")
print(f"Healthy: {report.is_healthy}")
print()
print(f"Characteristics present: {report.characteristics_present}")
print(f"Characteristics expected: {report.characteristics_expected}")
print(f"Characteristics required: {report.characteristics_required}")

if report.missing_details:
    print("\nMissing characteristics:")
    for name, info in report.missing_details.items():
        req_str = "required" if info.is_required else "optional"
        print(f"  - {name} ({req_str})")
```

## Bluetooth SIG Compliance

Validate compliance with Bluetooth SIG specifications:

```python
from bluetooth_sig.gatt.services import HeartRateService

issues = HeartRateService.validate_bluetooth_sig_compliance()

if issues:
    print("Compliance issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Service definition is compliant")
```

## Service Registry

The `GattServiceRegistry` provides dynamic service lookup:

```python
from bluetooth_sig.gatt.services import GattServiceRegistry

registry = GattServiceRegistry.get_instance()

# Check if UUID is a known service
service_class = registry.get_service_class("180D")
if service_class:
    print(f"Found: {service_class.__name__}")  # HeartRateService

# Get by name
service_class_by_name = registry.get_service_class_by_name("Heart Rate")
if service_class_by_name:
    print(f"Found by name: {service_class_by_name.__name__}")

# List all supported services (showing first 5 for brevity)
for i, svc_class in enumerate(registry.get_all_services()):
    if i >= 5:
        print("...")
        break
    uuid = svc_class.get_class_uuid()
    print(f"{svc_class.__name__}: {uuid}")
```

## Registering Custom Services

For proprietary services not defined by the Bluetooth SIG:

```python
from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.types import ServiceInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class MyCustomService(BaseGattService):
    """Custom service for My Device."""

    _info = ServiceInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789ABC"),
        name="My Custom Service",
    )

    # Define expected characteristics
    service_characteristics = {
        # CharacteristicName.SOME_CHAR: True,  # Required
        # CharacteristicName.OTHER_CHAR: False,  # Optional
    }


# Register the custom service
GattServiceRegistry.register_service_class(
    uuid="12345678-1234-1234-1234-123456789ABC",
    service_cls=MyCustomService,
)

# Now discoverable via the registry
service_class = GattServiceRegistry.get_service_class(
    "12345678-1234-1234-1234-123456789ABC"
)
print(f"Found: {service_class.__name__}")  # MyCustomService
```

### Cleanup Custom Registrations

```python
from bluetooth_sig.gatt.services import GattServiceRegistry

# Remove specific registration (if it was registered)
GattServiceRegistry.unregister_service_class(
    "12345678-1234-1234-1234-123456789ABC"
)

# Clear all custom registrations (useful for testing)
GattServiceRegistry.clear_custom_registrations()
```

## Available Service Classes

The library includes implementations for common SIG-defined services:

| Service | Class | UUID |
| --- | --- | --- |
| Battery Service | `BatteryService` | 0x180F |
| Device Information | `DeviceInformationService` | 0x180A |
| Heart Rate | `HeartRateService` | 0x180D |
| Blood Pressure | `BloodPressureService` | 0x1810 |
| Health Thermometer | `HealthThermometerService` | 0x1809 |
| Glucose | `GlucoseService` | 0x1808 |
| Cycling Power | `CyclingPowerService` | 0x1818 |
| Running Speed and Cadence | `RunningSpeedAndCadenceService` | 0x1814 |
| Environmental Sensing | `EnvironmentalSensingService` | 0x181A |
| Generic Access | `GenericAccessService` | 0x1800 |
| Generic Attribute | `GenericAttributeService` | 0x1801 |

See the full list with `GattServiceRegistry.supported_service_names()`.

## See Also

- [API Overview](../explanation/api-overview.md#service-organisation) — Conceptual overview
- [Supported Characteristics](../reference/characteristics.md) — Complete characteristic list
- [BLE Integration](ble-integration.md) — Full integration patterns
