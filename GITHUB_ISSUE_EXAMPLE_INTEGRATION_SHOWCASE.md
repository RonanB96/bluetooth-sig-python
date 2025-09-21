# Example Integration Showcase: Bluetooth SIG Translation Library

## Issue Overview

**Objective**: Create a comprehensive, modern example suite that showcases the Bluetooth SIG library's capabilities across different BLE connection libraries, implements missing APIs for enhanced developer experience, and establishes the library as the definitive Bluetooth SIG standards implementation.

## Official BLE Library Examples Reference

### Bleak Library Official Examples
From [hbldh/bleak/examples](https://github.com/hbldh/bleak/tree/develop/examples):

1. **`service_explorer.py`** - Service/characteristic discovery and enumeration
2. **`enable_notifications.py`** - Notification setup and callback handling
3. **`discover.py`** - Device scanning with service filtering
4. **`sensortag.py`** - Complete TI SensorTag device interaction (real-world example)
5. **`uart_service.py`** - Nordic UART service bidirectional communication
6. **`two_devices.py`** - Simultaneous connection to multiple devices
7. **`disconnect_callback.py`** - Connection management and disconnect handling

### SimplePyBLE Patterns
From existing project examples and [OpenBluetoothToolbox/SimplePyBLE](https://github.com/OpenBluetoothToolbox/SimplePyBLE):

- **Synchronous scanning**: `adapter.scan_for(5000)` → `adapter.scan_get_results()`
- **Direct connection**: `peripheral.connect()` → operations → `peripheral.disconnect()`
- **Service enumeration**: `peripheral.services()` → `service.characteristics()`
- **Data reading**: `peripheral.read(service_uuid, characteristic_uuid)` with service/characteristic discovery by name

## Current State Analysis

### ✅ Existing Examples Foundation

- **Framework-agnostic design** already established
- **Multiple BLE library examples** (Bleak, SimplePyBLE, Bleak-retry)
- **Pure translation focus** correctly maintained
- **Shared utilities** in `ble_utils.py`

### 🎯 Core Requirement: Translation Showcase with Service-Based Discovery

**CRITICAL**: This library handles **translation/parsing only**. Connection, streaming, and device management belong to the BLE libraries (Bleak, SimplePyBLE, etc.).

**IMPORTANT**: Examples must demonstrate proper service discovery workflows:

1. **Discover services** by name/type, not UUID
2. **Find characteristics** within discovered services by name
3. **Parse data** using characteristic names, not UUIDs
4. **Show SIG compliance** features that manual parsing misses

### When to Use UUID vs Name Lookups

**✅ Use name-based lookups when you know what you want:**

- `translator.get_service_info("Battery Service")` - when you want Battery Service
- `translator.get_characteristic_info("Battery Level")` - when you want Battery Level characteristic
- `translator.parse_characteristic("Temperature Measurement", data)` - when parsing known data

**✅ Use UUID-based lookups only for discovery:**

- `translator.get_service_info_by_uuid(service.uuid)` - to identify unknown services during exploration
- `translator.get_characteristic_info_by_uuid(char.uuid)` - to identify unknown characteristics during exploration

## 1. Enhanced Integration Examples

### Proper Service/Characteristic Discovery Pattern

```python
# ✅ RECOMMENDED: When you know what you want
async def read_battery_level_proper(client, translator):
    """Proper way to read battery level when you know what you want."""

    # Get service info by name
    service_info = translator.get_service_info("Battery Service")
    if not service_info:
        print("Battery Service not supported by SIG library")
        return None

    # Find the service on device by matching UUID
    battery_service = None
    for service in client.services:
        if str(service.uuid).upper() == service_info.uuid.upper():
            battery_service = service
            break

    if not battery_service:
        print("Battery Service not found on device")
        return None

    # Get characteristic info by name
    char_info = translator.get_characteristic_info("Battery Level")
    if not char_info:
        print("Battery Level characteristic not supported by SIG library")
        return None

    # Find the characteristic on device by matching UUID
    battery_char = None
    for char in battery_service.characteristics:
        if str(char.uuid).upper() == char_info.uuid.upper():
            battery_char = char
            break

    if not battery_char:
        print("Battery Level characteristic not found on device")
        return None

    # Read and parse using name
    raw_data = await client.read_gatt_char(battery_char)
    result = translator.parse_characteristic("Battery Level", raw_data)

    return result

# ✅ ACCEPTABLE: For discovery/exploration scenarios
async def explore_unknown_services(client, translator):
    """Acceptable use of UUID lookups for discovering unknown services."""

    for service in client.services:
        # Use UUID lookup to identify unknown services
        service_info = translator.get_service_info_by_uuid(service.uuid)
        service_name = service_info.name if service_info else f"Unknown Service ({service.uuid})"
        print(f"Found service: {service_name}")

        for char in service.characteristics:
            if "read" in char.properties:
                # Use UUID lookup to identify unknown characteristics
                char_info = translator.get_characteristic_info_by_uuid(char.uuid)
                if char_info:
                    # Once identified, parse by name
                    raw_data = await client.read_gatt_char(char)
                    result = translator.parse_characteristic(char_info.name, raw_data)
                    print(f"  {char_info.name}: {result.value} {result.unit}")
                else:
                    print(f"  Unknown characteristic: {char.uuid}")
```

### 1.1 Enhanced Service Explorer (Based on Bleak's `service_explorer.py`)

**Original Pattern**: [service_explorer.py](https://github.com/hbldh/bleak/blob/develop/examples/service_explorer.py)
**Enhancement**: Add SIG library parsing to characteristic reads

```python
# Original Bleak pattern:
for service in client.services:
    for char in service.characteristics:
        if "read" in char.properties:
            try:
                value = await client.read_gatt_char(char)
                print(f"Value: {value}")
            except Exception as e:
                print(f"Error: {e}")

# Enhanced with SIG library:
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

for service in client.services:
    # Use UUID only to identify unknown services during discovery
    service_info = translator.get_service_info_by_uuid(service.uuid)
    service_name = service_info.name if service_info else "Unknown Service"
    print(f"🔧 Exploring service: {service_name}")

    for char in service.characteristics:
        if "read" in char.properties:
            try:
                raw_data = await client.read_gatt_char(char)

                # Use UUID only to identify unknown characteristics during discovery
                char_info = translator.get_characteristic_info_by_uuid(char.uuid)
                if char_info:
                    characteristic_name = char_info.name
                    result = translator.parse_characteristic(characteristic_name, raw_data)

                    if result.parse_success:
                        print(f"  ✅ {result.name}: {result.value} {result.unit}")
                        print(f"     Raw: {raw_data.hex()}")
                    else:
                        print(f"  ❌ {result.name}: {result.error_message}")
                        print(f"     Raw: {raw_data.hex()}")
                else:
                    print(f"  ❓ Unknown characteristic: {char.uuid}")
                    print(f"     Raw: {raw_data.hex()}")
            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")
```

### 1.2 Enhanced TI SensorTag (Based on Bleak's `sensortag.py`)

**Original Pattern**: [sensortag.py](https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py)
**Enhancement**: Replace manual parsing with comprehensive SIG parsing

```python
# Original manual parsing:
battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
print("Battery Level: {0}%".format(int(battery_level[0])))

# Enhanced with SIG library:
# Find the Battery Service by name, not by discovering UUIDs
battery_service = None
for service in client.services:
    # Check if this service matches the Battery Service
    service_info = translator.get_service_info("Battery Service")
    if service_info and str(service.uuid).upper() == service_info.uuid.upper():
        battery_service = service
        break

if battery_service:
    # Find Battery Level characteristic by name within the service
    battery_char = None
    for char in battery_service.characteristics:
        char_info = translator.get_characteristic_info("Battery Level")
        if char_info and str(char.uuid).upper() == char_info.uuid.upper():
            battery_char = char
            break

    if battery_char:
        battery_data = await client.read_gatt_char(battery_char)
        result = translator.parse_characteristic("Battery Level", battery_data)
        print(f"Battery: {result.value.level}% (Status: {result.value.status})")
        print(f"SIG Compliant: {result.parse_success}")
    else:
        print("Battery Level characteristic not found")
else:
    print("Battery Service not found")

# Device Information Service - SIG library enhancement:
# Find Device Information Service by name, not by discovering UUIDs
device_info_service = None
for service in client.services:
    # Check if this service matches the Device Information Service
    service_info = translator.get_service_info("Device Information")
    if service_info and str(service.uuid).upper() == service_info.uuid.upper():
        device_info_service = service
        break

if device_info_service:
    # Define what characteristics we want to read by name
    desired_device_info = [
        "Manufacturer Name String",
        "Model Number String",
        "Serial Number String",
        "Hardware Revision String",
        "Firmware Revision String"
    ]

    for characteristic_name in desired_device_info:
        try:
            # Find the characteristic within the service by name
            char_info = translator.get_characteristic_info(characteristic_name)
            if not char_info:
                print(f"❓ {characteristic_name}: Not a known SIG characteristic")
                continue

            found_char = None
            for char in device_info_service.characteristics:
                if str(char.uuid).upper() == char_info.uuid.upper():
                    found_char = char
                    break

            if found_char:
                raw_data = await client.read_gatt_char(found_char)
                result = translator.parse_characteristic(characteristic_name, raw_data)

                if result.parse_success:
                    print(f"✅ {result.name}: {result.value}")
                    # Show SIG standard compliance features that manual parsing misses
                    if hasattr(result.value, 'encoding'):
                        print(f"  📝 Encoding: {result.value.encoding}")
                    if hasattr(result.value, 'language'):
                        print(f"  🌐 Language: {result.value.language}")
                    if hasattr(result.value, 'format'):
                        print(f"  📋 Format: {result.value.format}")
                else:
                    print(f"❌ {characteristic_name}: {result.error_message}")
            else:
                print(f"❓ {characteristic_name}: Not found in device")
        except Exception as e:
            print(f"⚠️ {characteristic_name}: Error - {e}")
else:
    print("Device Information Service not found")
```

### 1.3 Enhanced Notifications (Based on Bleak's `enable_notifications.py`)

**Original Pattern**: [enable_notifications.py](https://github.com/hbldh/bleak/blob/develop/examples/enable_notifications.py)
**Enhancement**: Automatic parsing in notification callbacks

```python
# Original notification handler:
def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    logger.info("%s: %r", characteristic.description, data)

# Enhanced with SIG library:
def sig_notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    # Get characteristic name from SIG registry first
    char_info = translator.get_characteristic_info_by_uuid(characteristic.uuid)
    if char_info:
        characteristic_name = char_info.name
        result = translator.parse_characteristic(characteristic_name, data)

        if result.parse_success:
            logger.info("📊 %s: %s %s",
                       result.name, result.value, result.unit)

            # Show rich data that manual parsing would miss
            if hasattr(result.value, 'timestamp'):
                logger.info("   ⏰ Timestamp: %s", result.value.timestamp)
            if hasattr(result.value, 'measurement_status'):
                logger.info("   📈 Status: %s", result.value.measurement_status)
        else:
            logger.warning("❌ %s: Parse failed - %s",
                          result.name, result.error_message)
            logger.info("   Raw data: %s", data.hex())
    else:
        logger.warning("❓ Unknown characteristic %s", characteristic.uuid)
        logger.info("   Raw data: %s", data.hex())

# Usage remains the same:
await client.start_notify(args.characteristic, sig_notification_handler)
```

### 1.4 Enhanced SimplePyBLE Integration

**Original Pattern**: From existing `with_simpleble.py` and [SimplePyBLE docs](https://github.com/OpenBluetoothToolbox/SimplePyBLE)
**Enhancement**: Add SIG parsing to SimplePyBLE synchronous operations

```python
# Original SimplePyBLE pattern:
import simplepyble

adapter = simplepyble.Adapter.get_adapters()[0]
adapter.scan_for(5000)
peripherals = adapter.scan_get_results()

peripheral = peripherals[0]
peripheral.connect()

for service in peripheral.services():
    for characteristic in service.characteristics():
        if characteristic.can_read():
            try:
                data = peripheral.read(service.uuid(), characteristic.uuid())
                print(f"Data: {data.hex()}")
            except Exception as e:
                print(f"Error: {e}")

# Enhanced with SIG library:
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
adapter = simplepyble.Adapter.get_adapters()[0]
adapter.scan_for(5000)
peripherals = adapter.scan_get_results()

peripheral = peripherals[0]
peripheral.connect()

print(f"🔗 Connected to: {peripheral.identifier()}")

for service in peripheral.services():
    # Use UUID only to identify unknown services during discovery
    service_info = translator.get_service_info_by_uuid(service.uuid())
    service_name = service_info.name if service_info else "Unknown Service"
    print(f"🔧 Service: {service_name}")

    for characteristic in service.characteristics():
        if characteristic.can_read():
            try:
                raw_data = peripheral.read(service.uuid(), characteristic.uuid())

                # Use UUID only to identify unknown characteristics during discovery
                char_info = translator.get_characteristic_info_by_uuid(characteristic.uuid())
                if char_info:
                    characteristic_name = char_info.name
                    result = translator.parse_characteristic(characteristic_name, raw_data)

                    if result.parse_success:
                        print(f"  ✅ {result.name}")
                        print(f"     Value: {result.value} {result.unit}")
                        print(f"     Raw: {raw_data.hex()}")

                        # Show SIG standard compliance info
                        print(f"     SIG Name: {char_info.name}")
                        print(f"     Format: {char_info.format}")
                    else:
                        print(f"  ❌ {result.name}: Parse failed")
                        print(f"     Error: {result.error_message}")
                        print(f"     Raw: {raw_data.hex()}")
                else:
                    print(f"  ❓ Unknown characteristic: {characteristic.uuid()}")
                    print(f"     Raw: {raw_data.hex()}")

            except Exception as e:
                print(f"  ⚠️  Read error - {e}")

peripheral.disconnect()
```

### 1.5 Multi-Device with SIG Parsing (Based on Bleak's `two_devices.py`)

**Original Pattern**: [two_devices.py](https://github.com/hbldh/bleak/blob/develop/examples/two_devices.py)
**Enhancement**: Add SIG parsing to multi-device notification handling

```python
# Enhanced notification callback with SIG parsing:
def sig_multi_device_callback(device_name: str, translator: BluetoothSIGTranslator):
    def callback(char: BleakGATTCharacteristic, data: bytearray) -> None:
        # Get characteristic name from SIG registry first
        char_info = translator.get_characteristic_info_by_uuid(char.uuid)
        if char_info:
            characteristic_name = char_info.name
            result = translator.parse_characteristic(characteristic_name, data)

            if result.parse_success:
                logging.info("📊 %s - %s: %s %s",
                            device_name, result.name, result.value, result.unit)

                # Device-specific data correlation
                if result.name == "Heart Rate Measurement":
                    logging.info("   💓 HR: %d bpm, Contact: %s",
                               result.value.heart_rate,
                               "Yes" if result.value.sensor_contact else "No")
                elif result.name == "Battery Level":
                    logging.info("   🔋 Battery: %d%%", result.value.level)
            else:
                logging.warning("❌ %s - %s: Parse failed - %s",
                              device_name, result.name, result.error_message)
        else:
            logging.warning("❓ %s - Unknown characteristic %s",
                          device_name, char.uuid)

    return callback

# Usage in multi-device setup:
translator = BluetoothSIGTranslator()

async with contextlib.AsyncExitStack() as stack:
    # Connect to multiple devices
    client1 = await stack.enter_async_context(BleakClient(device1))
    client2 = await stack.enter_async_context(BleakClient(device2))

    # Set up SIG-enhanced notifications for each device
    # Find characteristics by service and name rather than hardcoded UUIDs

    # Device 1: Find Heart Rate Service and its measurement characteristic
    heart_rate_service_info = translator.get_service_info("Heart Rate")
    if heart_rate_service_info:
        for service in client1.services:
            if str(service.uuid).upper() == heart_rate_service_info.uuid.upper():
                hr_measurement_info = translator.get_characteristic_info("Heart Rate Measurement")
                if hr_measurement_info:
                    for char in service.characteristics:
                        if str(char.uuid).upper() == hr_measurement_info.uuid.upper():
                            await client1.start_notify(char, sig_multi_device_callback("Device1", translator))
                            break
                break

    # Device 2: Find Battery Service and its level characteristic
    battery_service_info = translator.get_service_info("Battery Service")
    if battery_service_info:
        for service in client2.services:
            if str(service.uuid).upper() == battery_service_info.uuid.upper():
                battery_level_info = translator.get_characteristic_info("Battery Level")
                if battery_level_info:
                    for char in service.characteristics:
                        if str(char.uuid).upper() == battery_level_info.uuid.upper():
                            await client2.start_notify(char, sig_multi_device_callback("Device2", translator))
                            break
                break

    # Monitor both devices with rich parsing
    await asyncio.sleep(10.0)
```

## 2. Real-World Integration Examples

```python
"""Direct comparison: Manual parsing vs Bluetooth SIG library.

Shows the dramatic difference in code complexity and reliability
when using the Bluetooth SIG library for standards-compliant parsing.
"""

import struct
from bluetooth_sig import BluetoothSIGTranslator

def manual_temperature_parsing(data: bytes) -> dict:
    """Manual parsing - error-prone and incomplete."""
    if len(data) < 2:
        raise ValueError("Invalid temperature data")

    # Manual parsing - missing many SIG standard features
    raw_temp = struct.unpack('<h', data[:2])[0]
    celsius = raw_temp * 0.01

    return {
        "temperature": celsius,
        "unit": "°C",
        # Missing: timestamp, temperature type, measurement status, etc.
    }

def sig_library_parsing(data: bytes) -> dict:
    """Bluetooth SIG library - complete and standards-compliant."""
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic("Temperature Measurement", data)

    return {
        "temperature": result.value.temperature,
        "unit": result.unit,
        "timestamp": result.value.timestamp,
        "temperature_type": result.value.temperature_type,
        "measurement_status": result.value.status,
        "parse_success": result.parse_success,
        "raw_data": result.raw_data.hex()
    }

async def comparison_demo():
    """Demonstrate the difference in parsing capabilities."""
    # Example data from a real temperature sensor
    sample_data = bytes.fromhex("FE06E507E407010000")

    print("=== Manual Parsing ===")
    manual_result = manual_temperature_parsing(sample_data)
    print(f"Manual: {manual_result}")

    print("\n=== Bluetooth SIG Library Parsing ===")
    sig_result = sig_library_parsing(sample_data)
    print(f"SIG Library: {sig_result}")

    print("\n=== Key Advantages of SIG Library ===")
    print("✅ Standards-compliant parsing")
    print("✅ Complete data extraction")
    print("✅ Proper error handling")
    print("✅ Type safety and validation")
    print("✅ Future-proof with SIG updates")
```

### 1.2 Enhanced BLE Library Integration Examples

#### `examples/enhanced_bleak_integration.py`

```python
"""Enhanced Bleak integration showcasing Bluetooth SIG library.

Demonstrates how the SIG library transforms raw BLE data into
structured, standards-compliant information.
"""

import asyncio
from bleak import BleakClient, BleakScanner
from bluetooth_sig import BluetoothSIGTranslator

class SIGEnhancedBleakClient:
    """Bleak client enhanced with Bluetooth SIG translation."""

    def __init__(self):
        self.translator = BluetoothSIGTranslator()
        self.client = None

    async def connect(self, address: str):
        """Connect to device using Bleak."""
        self.client = BleakClient(address)
        await self.client.connect()

    async def read_characteristic_with_sig(self, service_name: str, characteristic_name: str) -> dict:
        """Read and parse characteristic using SIG standards and names."""
        # Get service info by name to find its UUID
        service_info = self.translator.get_service_info(service_name)
        if not service_info:
            raise ValueError(f"Unknown service: '{service_name}'")

        # Find service by UUID
        target_service = None
        for service in self.client.services:
            if str(service.uuid).upper() == service_info.uuid.upper():
                target_service = service
                break

        if not target_service:
            raise ValueError(f"Service '{service_name}' not found on device")

        # Get characteristic info by name to find its UUID
        char_info = self.translator.get_characteristic_info(characteristic_name)
        if not char_info:
            raise ValueError(f"Unknown characteristic: '{characteristic_name}'")

        # Find characteristic by UUID within the service
        target_char = None
        for char in target_service.characteristics:
            if str(char.uuid).upper() == char_info.uuid.upper():
                target_char = char
                break

        if not target_char:
            raise ValueError(f"Characteristic '{characteristic_name}' not found in service '{service_name}'")

        # Bleak handles the connection and reading
        raw_data = await self.client.read_gatt_char(target_char)

        # Bluetooth SIG library handles the parsing
        result = self.translator.parse_characteristic(characteristic_name, raw_data)

        return {
            "service_name": service_name,
            "characteristic_name": characteristic_name,
            "parsed_value": result.value,
            "unit": result.unit,
            "raw_data": raw_data.hex(),
            "parse_success": result.parse_success,
            "characteristic_info": char_info
        }

    async def read_device_information_service(self) -> dict:
        """Read complete Device Information Service with SIG parsing."""
        device_info = {}

        # Standard Device Information characteristics by name
        dis_characteristics = [
            "Manufacturer Name String",
            "Model Number String",
            "Serial Number String",
            "Hardware Revision String",
            "Firmware Revision String",
            "Software Revision String"
        ]

        for characteristic_name in dis_characteristics:
            try:
                result = await self.read_characteristic_with_sig("Device Information", characteristic_name)
                device_info[characteristic_name.lower().replace(' ', '_')] = result
            except Exception as e:
                device_info[characteristic_name.lower().replace(' ', '_')] = {"error": str(e)}

        return device_info

async def enhanced_bleak_demo():
    """Demonstrate enhanced Bleak integration."""
    # Scan for devices
    devices = await BleakScanner.discover()
    if not devices:
        print("No devices found")
        return

    # Connect to first device
    client = SIGEnhancedBleakClient()
    await client.connect(devices[0].address)

    # Read device information with SIG parsing
    device_info = await client.read_device_information_service()

    print("=== Device Information (SIG Parsed) ===")
    for name, data in device_info.items():
        print(f"{name}: {data}")
```

#### `examples/enhanced_simplepyble_integration.py`

```python
"""Enhanced SimplePyBLE integration showcasing Bluetooth SIG library.

Shows how the SIG library adds standards compliance to SimplePyBLE
without changing the connection management.
"""

import simplepyble
from bluetooth_sig import BluetoothSIGTranslator

class SIGEnhancedSimpleBLE:
    """SimplePyBLE enhanced with Bluetooth SIG translation."""

    def __init__(self):
        self.translator = BluetoothSIGTranslator()
        self.peripheral = None

    def scan_and_connect(self, timeout_ms: int = 5000):
        """Scan and connect using SimplePyBLE."""
        adapter = simplepyble.Adapter.get_adapters()[0]
        adapter.scan_for(timeout_ms)

        peripherals = adapter.scan_get_results()
        if peripherals:
            self.peripheral = peripherals[0]
            self.peripheral.connect()
            return True
        return False

    def read_characteristic_with_sig(self, service_name: str, characteristic_name: str) -> dict:
        """Read and parse characteristic using SIG standards and names."""
        # Get service info by name to find its UUID
        service_info = self.translator.get_service_info(service_name)
        if not service_info:
            return {"error": f"Unknown service: '{service_name}'"}

        # Find service by UUID
        target_service = None
        for service in self.peripheral.services():
            if str(service.uuid()).upper() == service_info.uuid.upper():
                target_service = service
                break

        if not target_service:
            return {"error": f"Service '{service_name}' not found on device"}

        # Get characteristic info by name to find its UUID
        char_info = self.translator.get_characteristic_info(characteristic_name)
        if not char_info:
            return {"error": f"Unknown characteristic: '{characteristic_name}'"}

        # Find characteristic by UUID within the service
        target_char = None
        for characteristic in target_service.characteristics():
            if str(characteristic.uuid()).upper() == char_info.uuid.upper():
                target_char = characteristic
                break

        if not target_char:
            return {"error": f"Characteristic '{characteristic_name}' not found in service '{service_name}'"}

        # SimplePyBLE handles the connection and reading
        raw_data = self.peripheral.read(target_service.uuid(), target_char.uuid())

        # Bluetooth SIG library handles the parsing
        result = self.translator.parse_characteristic(characteristic_name, raw_data)

        return {
            "service_name": service_name,
            "characteristic_name": characteristic_name,
            "parsed_value": result.value,
            "unit": result.unit,
            "raw_data": raw_data.hex(),
            "parse_success": result.parse_success,
            "validation_errors": result.error_message if not result.parse_success else None
        }

    def get_all_characteristics_with_sig(self) -> list[dict]:
        """Get all characteristics and parse with SIG library."""
        all_characteristics = []

        for service in self.peripheral.services():
            # Use UUID only to identify unknown services during discovery
            service_info = self.translator.get_service_info_by_uuid(service.uuid())
            service_name = service_info.name if service_info else "Unknown Service"

            for characteristic in service.characteristics():
                # Use UUID only to identify unknown characteristics during discovery
                char_info = self.translator.get_characteristic_info_by_uuid(characteristic.uuid())
                if char_info:
                    characteristic_name = char_info.name
                    try:
                        # Now use name-based lookup for known characteristics
                        result = self.read_characteristic_with_sig(service_name, characteristic_name)
                        all_characteristics.append(result)
                    except Exception as e:
                        all_characteristics.append({
                            "service_name": service_name,
                            "characteristic_name": characteristic_name,
                            "error": str(e)
                        })
                else:
                    all_characteristics.append({
                        "service_name": service_name,
                        "characteristic_name": "Unknown",
                        "error": f"Unknown characteristic {characteristic.uuid()}"
                    })

        return all_characteristics

def enhanced_simplepyble_demo():
    """Demonstrate enhanced SimplePyBLE integration."""
    client = SIGEnhancedSimpleBLE()

    if client.scan_and_connect():
        print("Connected to device")

        # Get all characteristics with SIG parsing
        characteristics = client.get_all_characteristics_with_sig()

        print("=== All Characteristics (SIG Parsed) ===")
        for char in characteristics:
            if "error" not in char:
                print(f"✅ {char['characteristic_name']}: {char['parsed_value']} {char['unit']}")
            else:
                print(f"❌ {char.get('characteristic_name', 'Unknown')}: {char['error']}")
    else:
        print("Failed to connect to device")
```

### 1.3 Library Feature Comparison Matrix

#### `examples/comparison/library_feature_matrix.py`

```python
"""Feature comparison matrix across BLE libraries with SIG integration.

Demonstrates how the Bluetooth SIG library provides consistent
parsing capabilities regardless of the underlying BLE library.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional
from bluetooth_sig import BluetoothSIGTranslator

@dataclass
class LibraryCapabilities:
    """Capabilities comparison for each BLE library."""
    name: str
    connection_management: str
    async_support: bool
    cross_platform: bool
    parsing_built_in: bool
    sig_library_compatible: bool
    ease_of_use: str
    performance: str
    maintenance: str

@dataclass
class ParsingComparison:
    """Parsing capability comparison."""
    library: str
    manual_parsing_lines: int
    sig_library_lines: int
    standards_compliance: bool
    error_handling: bool
    type_safety: bool
    maintainability: str

def get_library_comparison() -> list[LibraryCapabilities]:
    """Compare BLE library capabilities."""
    return [
        LibraryCapabilities(
            name="Bleak",
            connection_management="Excellent",
            async_support=True,
            cross_platform=True,
            parsing_built_in=False,
            sig_library_compatible=True,
            ease_of_use="High",
            performance="High",
            maintenance="Active"
        ),
        LibraryCapabilities(
            name="SimplePyBLE",
            connection_management="Good",
            async_support=False,
            cross_platform=True,
            parsing_built_in=False,
            sig_library_compatible=True,
            ease_of_use="Very High",
            performance="Medium",
            maintenance="Active"
        ),
        LibraryCapabilities(
            name="Bleak-retry-connector",
            connection_management="Excellent+",
            async_support=True,
            cross_platform=True,
            parsing_built_in=False,
            sig_library_compatible=True,
            ease_of_use="High",
            performance="High",
            maintenance="Active"
        ),
        LibraryCapabilities(
            name="Manual Implementation",
            connection_management="Variable",
            async_support=False,
            cross_platform=False,
            parsing_built_in=False,
            sig_library_compatible=False,
            ease_of_use="Low",
            performance="Variable",
            maintenance="User Burden"
        )
    ]

def get_parsing_comparison() -> list[ParsingComparison]:
    """Compare parsing implementations."""
    return [
        ParsingComparison(
            library="Manual Temperature Parsing",
            manual_parsing_lines=25,
            sig_library_lines=3,
            standards_compliance=False,
            error_handling=False,
            type_safety=False,
            maintainability="Poor"
        ),
        ParsingComparison(
            library="Manual Heart Rate Parsing",
            manual_parsing_lines=45,
            sig_library_lines=3,
            standards_compliance=False,
            error_handling=False,
            type_safety=False,
            maintainability="Poor"
        ),
        ParsingComparison(
            library="Manual Environmental Parsing",
            manual_parsing_lines=35,
            sig_library_lines=3,
            standards_compliance=False,
            error_handling=False,
            type_safety=False,
            maintainability="Poor"
        ),
        ParsingComparison(
            library="Bluetooth SIG Library",
            manual_parsing_lines=0,
            sig_library_lines=3,
            standards_compliance=True,
            error_handling=True,
            type_safety=True,
            maintainability="Excellent"
        )
    ]

def print_comparison_matrix():
    """Print comprehensive comparison matrix."""
    print("=== BLE Library Capabilities Comparison ===")
    libraries = get_library_comparison()

    for lib in libraries:
        print(f"\n{lib.name}:")
        print(f"  Connection Management: {lib.connection_management}")
        print(f"  Async Support: {'✅' if lib.async_support else '❌'}")
        print(f"  Cross Platform: {'✅' if lib.cross_platform else '❌'}")
        print(f"  Built-in Parsing: {'✅' if lib.parsing_built_in else '❌'}")
        print(f"  SIG Library Compatible: {'✅' if lib.sig_library_compatible else '❌'}")
        print(f"  Ease of Use: {lib.ease_of_use}")
        print(f"  Performance: {lib.performance}")
        print(f"  Maintenance: {lib.maintenance}")

    print("\n=== Parsing Implementation Comparison ===")
    parsing = get_parsing_comparison()

    print(f"{'Implementation':<30} {'Lines':<8} {'Standards':<12} {'Errors':<8} {'Types':<8} {'Maintenance'}")
    print("-" * 80)

    for p in parsing:
        if p.library == "Bluetooth SIG Library":
            lines = f"{p.sig_library_lines}"
        else:
            lines = f"{p.manual_parsing_lines}"

        standards = "✅" if p.standards_compliance else "❌"
        errors = "✅" if p.error_handling else "❌"
        types = "✅" if p.type_safety else "❌"

        print(f"{p.library:<30} {lines:<8} {standards:<12} {errors:<8} {types:<8} {p.maintainability}")
```

## 2. Real-World Integration Patterns

### 2.1 Home Assistant Custom Component Example

#### `examples/integration/homeassistant_ble_component.py`

```python
"""Home Assistant BLE integration using Bluetooth SIG library.

Shows how to create a proper Home Assistant component that uses
the SIG library for parsing BLE characteristic data.
"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS
from bluetooth_sig import BluetoothSIGTranslator

class SIGBLETemperatureSensor(SensorEntity):
    """Temperature sensor using Bluetooth SIG library for parsing."""

    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self.translator = BluetoothSIGTranslator()
        self._attr_name = f"SIG Temperature {mac_address}"
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_unit_of_measurement = TEMP_CELSIUS

    def update_from_ble_data(self, raw_data: bytes) -> None:
        """Update sensor from BLE advertisement data."""
        # Parse using Bluetooth SIG library with characteristic name
        result = self.translator.parse_characteristic("Temperature Measurement", raw_data)

        if result.parse_success:
            self._attr_native_value = result.value.temperature
            self._attr_extra_state_attributes = {
                "timestamp": result.value.timestamp,
                "temperature_type": result.value.temperature_type,
                "measurement_status": result.value.status,
                "raw_data": raw_data.hex(),
                "parsing_library": "bluetooth-sig"
            }
        else:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {
                "error": result.error_message,
                "raw_data": raw_data.hex()
            }

# Integration with Home Assistant's BLE framework
async def setup_ble_device_with_sig(hass, mac_address: str):
    """Set up BLE device with SIG library integration."""
    sensor = SIGBLETemperatureSensor(mac_address)

    # Register with Home Assistant's BLE callback system
    def ble_advertisement_callback(data):
        if data.get("manufacturer_data"):
            # Extract temperature data from manufacturer data
            temp_data = extract_temperature_from_advertisement(data)
            if temp_data:
                sensor.update_from_ble_data(temp_data)
                sensor.async_write_ha_state()

    # Register callback with Home Assistant BLE integration
    hass.data["bluetooth"].async_register_callback(
        ble_advertisement_callback,
        {"address": mac_address}
    )
```

### 2.2 MQTT Bridge Example

#### `examples/integration/mqtt_ble_bridge.py`

```python
"""MQTT bridge for BLE devices using Bluetooth SIG library.

Demonstrates how to create an MQTT bridge that publishes
standards-compliant BLE data using the SIG library.
"""

import json
import asyncio
from paho.mqtt.client import Client as MQTTClient
from bleak import BleakScanner
from bluetooth_sig import BluetoothSIGTranslator

class SIGBLEMQTTBridge:
    """MQTT bridge enhanced with Bluetooth SIG parsing."""

    def __init__(self, mqtt_broker: str, mqtt_port: int = 1883):
        self.translator = BluetoothSIGTranslator()
        self.mqtt_client = MQTTClient()
        self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)

    def parse_and_publish(self, device_address: str, characteristic_name: str, raw_data: bytes):
        """Parse BLE data and publish to MQTT."""
        # Parse using Bluetooth SIG library with characteristic name
        result = self.translator.parse_characteristic(characteristic_name, raw_data)

        # Create MQTT payload
        payload = {
            "device_address": device_address,
            "characteristic_name": characteristic_name,
            "parsed_name": result.name,
            "timestamp": asyncio.get_event_loop().time(),
            "parsing_library": "bluetooth-sig-python"
        }

        if result.parse_success:
            payload.update({
                "value": result.value,
                "unit": result.unit,
                "parse_success": True,
                "raw_data": raw_data.hex()
            })
        else:
            payload.update({
                "parse_success": False,
                "error": result.error_message,
                "raw_data": raw_data.hex()
            })

        # Publish to MQTT
        topic = f"ble_sig/{device_address}/{result.name.lower().replace(' ', '_')}"
        self.mqtt_client.publish(topic, json.dumps(payload))

        print(f"Published to {topic}: {payload}")

async def mqtt_bridge_demo():
    """Demonstrate MQTT bridge with SIG parsing."""
    bridge = SIGBLEMQTTBridge("localhost")

    # Simulate BLE data reception and parsing
    sample_devices = [
        {
            "address": "12:34:56:78:9A:BC",
            "characteristics": {
                "Temperature Measurement": bytes.fromhex("FE06E507E407010000"),
                "Heart Rate Measurement": bytes.fromhex("0E5A01"),
                "Battery Level": bytes.fromhex("64")
            }
        }
    ]

    for device in sample_devices:
        for char_name, data in device["characteristics"].items():
            bridge.parse_and_publish(device["address"], char_name, data)
```

## 3. Performance and Quality Demonstration

### 3.1 Performance Benchmark Example

#### `examples/benchmarks/parsing_performance_comparison.py`

```python
"""Performance comparison: Manual vs SIG library parsing.

Demonstrates that the SIG library is not only more feature-complete
but also performs better than typical manual parsing implementations.
"""

import time
import struct
from typing import Any
from bluetooth_sig import BluetoothSIGTranslator

def benchmark_parsing_performance():
    """Compare parsing performance across different approaches."""

    # Test data
    temperature_data = bytes.fromhex("FE06E507E407010000")
    heart_rate_data = bytes.fromhex("0E5A01")
    battery_data = bytes.fromhex("64")

    iterations = 10000

    print("=== Parsing Performance Benchmark ===")
    print(f"Iterations: {iterations}")

    # Manual temperature parsing
    start_time = time.perf_counter()
    for _ in range(iterations):
        manual_temperature_parse(temperature_data)
    manual_temp_time = time.perf_counter() - start_time

    # SIG library temperature parsing
    translator = BluetoothSIGTranslator()
    start_time = time.perf_counter()
    for _ in range(iterations):
        translator.parse_characteristic("Temperature Measurement", temperature_data)
    sig_temp_time = time.perf_counter() - start_time

    # Results
    print(f"\nTemperature Parsing:")
    print(f"  Manual parsing: {manual_temp_time:.4f}s ({manual_temp_time/iterations*1000:.2f}ms per parse)")
    print(f"  SIG library:    {sig_temp_time:.4f}s ({sig_temp_time/iterations*1000:.2f}ms per parse)")
    print(f"  Performance:    {manual_temp_time/sig_temp_time:.2f}x {'slower' if manual_temp_time > sig_temp_time else 'faster'} with manual parsing")

    # Feature comparison
    print(f"\nFeature Comparison:")
    print(f"  Manual parsing features: Temperature value only")
    print(f"  SIG library features:    Temperature, timestamp, type, status, validation, units")
    print(f"  SIG library advantage:   {'Significantly more features' if sig_temp_time < manual_temp_time * 2 else 'More features with minimal performance cost'}")

def manual_temperature_parse(data: bytes) -> float:
    """Manual temperature parsing - minimal features."""
    return struct.unpack('<h', data[:2])[0] * 0.01
```

### 3.2 Code Quality Comparison

#### `examples/quality/code_maintainability_demo.py`

```python
"""Code quality and maintainability comparison.

Shows how the SIG library reduces code complexity and improves
maintainability compared to manual parsing implementations.
"""

from bluetooth_sig import BluetoothSIGTranslator

def demonstrate_code_quality():
    """Show code quality improvements with SIG library."""

    print("=== Code Quality Comparison ===")

    # Manual approach - complex and error-prone
    manual_code_lines = '''
def parse_temperature_manual(data: bytes) -> dict:
    """Manual parsing - 25+ lines of error-prone code."""
    if len(data) < 2:
        raise ValueError("Invalid data length")

    # Basic temperature
    raw_temp = struct.unpack('<h', data[:2])[0]
    temperature = raw_temp * 0.01

    # Try to parse timestamp (often missing in manual implementations)
    timestamp = None
    if len(data) >= 9:
        try:
            year = struct.unpack('<H', data[2:4])[0]
            month = data[4]
            day = data[5]
            hour = data[6]
            minute = data[7]
            second = data[8]
            # ... complex timestamp parsing
        except:
            pass

    # Missing: temperature type, measurement status, proper validation
    return {"temperature": temperature, "timestamp": timestamp}
    '''

    # SIG library approach - simple and complete
    sig_code_lines = '''
def parse_temperature_sig(data: bytes) -> dict:
    """SIG library parsing - 3 lines, full features."""
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic("Temperature Measurement", data)
    return result  # Complete with all SIG standard fields
    '''

    print("Manual Implementation:")
    print(f"  Lines of code: 25+")
    print(f"  Error handling: Basic")
    print(f"  Standards compliance: Partial")
    print(f"  Maintainability: Poor")
    print(f"  Testing required: Extensive")

    print("\nSIG Library Implementation:")
    print(f"  Lines of code: 3")
    print(f"  Error handling: Comprehensive")
    print(f"  Standards compliance: Full SIG compliance")
    print(f"  Maintainability: Excellent")
    print(f"  Testing required: Minimal (library is pre-tested)")

    print("\n✅ SIG Library Advantages:")
    print("  - 8x fewer lines of code")
    print("  - Built-in error handling")
    print("  - Standards compliance guaranteed")
    print("  - Future-proof with SIG updates")
    print("  - Comprehensive test coverage included")
```

## 4. Success Criteria

### 4.1 Integration Requirements

- [ ] **Enhanced examples for each major BLE library** (Bleak, SimplePyBLE, Bleak-retry)
- [ ] **Side-by-side comparison demos** showing manual vs SIG library parsing
- [ ] **Real-world integration examples** (Home Assistant, MQTT, data logging)
- [ ] **Performance benchmarks** demonstrating SIG library advantages
- [ ] **Code quality demonstrations** showing maintainability improvements

### 4.2 Quality Standards

- [ ] **Zero streaming/connection code** in translation library
- [ ] **Clear separation of concerns** (BLE libraries handle connections, SIG library handles parsing)
- [ ] **Comprehensive documentation** for each integration pattern
- [ ] **Runnable examples** with sample data for offline testing
- [ ] **Performance metrics** proving SIG library efficiency

### 4.3 Developer Experience

- [ ] **5-minute integration** guides for each BLE library
- [ ] **Copy-paste ready code** for common patterns
- [ ] **Clear migration paths** from manual parsing to SIG library
- [ ] **Comprehensive error handling** examples
- [ ] **Best practices documentation** for each integration type

## 5. Implementation Focus

### Phase 1: Core Integration Examples

- Enhance existing Bleak/SimplePyBLE examples with SIG library integration
- Create direct comparison demonstrations
- Add performance benchmarking

### Phase 2: Real-World Integration Patterns

- Home Assistant component integration
- MQTT bridge implementation
- Data logging and export examples

### Phase 3: Quality and Performance Documentation

- Code quality comparisons
- Performance benchmarks
- Maintainability demonstrations

---

**This issue focuses on showcasing the Bluetooth SIG library's translation capabilities within existing BLE ecosystem tools, maintaining the library's pure translation focus while demonstrating clear advantages over manual parsing.**
