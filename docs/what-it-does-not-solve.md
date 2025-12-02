# What It Does NOT Solve

Understanding what this library **does not** do is just as important as understanding what it does. This helps set proper expectations and guides you to use the right tools for your needs.

## ❌ BLE Device Connection & Communication

### What This Library Does NOT Do (BLE Connection)

This library **does not** handle:

- Scanning for BLE devices
- Connecting to BLE devices
- Managing connection state
- Reading/writing characteristics over BLE
- Handling BLE callbacks and notifications
- Device pairing and bonding
- Connection parameters negotiation

### What You Should Use Instead

For BLE connectivity, use dedicated BLE libraries:

**Recommended BLE Libraries:**

- **[bleak](https://github.com/hbldh/bleak)** - Cross-platform async BLE library (Windows, macOS, Linux)
- **[bleak-retry-connector](https://github.com/Bluetooth-Devices/bleak-retry-connector)** - Robust connection handling with retry logic
- **[simplepyble](https://github.com/OpenBluetoothToolbox/SimpleBLE)** - Cross-platform sync BLE library
- **[PyBluez](https://github.com/pybluez/pybluez)** - Classic Bluetooth and BLE (Linux, Windows)

### How They Work Together

```python
# SKIP: Example requires BLE hardware access
from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# EXAMPLE UUIDs - From your BLE library
# ============================================
BATTERY_LEVEL_UUID = "2A19"  # UUID from device discovery
device_address = "AA:BB:CC:DD:EE:FF"  # Device MAC address

# bleak handles connection
async with BleakClient(device_address) as client:
    # bleak reads the raw data
    raw_data = await client.read_gatt_char(BATTERY_LEVEL_UUID)

    # bluetooth-sig interprets the data
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic(BATTERY_LEVEL_UUID, raw_data)
    print(f"Battery: {result.value}%")
```

**Separation of Concerns:**

- **BLE Library** → Device discovery, connection, I/O
- **bluetooth-sig** → Standards interpretation, data parsing

______________________________________________________________________

## ❌ Bluetooth Classic Support

### What This Library Does NOT Do (Bluetooth Classic)

This library **only** supports Bluetooth Low Energy (BLE) / GATT characteristics.

**Not Supported:**

- Bluetooth Classic (BR/EDR)
- RFCOMM profiles
- A2DP (audio streaming)
- HFP (hands-free profile)
- Other classic Bluetooth profiles

### Reason (Bluetooth Classic)

Bluetooth Classic and BLE are fundamentally different protocols with different standards. This library focuses exclusively on BLE/GATT standards as defined by Bluetooth SIG.

______________________________________________________________________

## ✅ Custom Characteristics ARE Supported

### What This Library DOES Support

While the library provides **70+ official Bluetooth SIG standard characteristics**, it also **fully supports adding custom characteristics**.

**You CAN:**

- ✅ Create vendor-specific characteristics
- ✅ Add custom protocols on top of BLE
- ✅ Implement proprietary data formats
- ✅ Extend with device manufacturer-specific characteristics

### How to Add Custom Characteristics

The library provides a clean API for extending with your own characteristics:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class MyCustomCharacteristic(CustomBaseCharacteristic):
    """Your custom characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("ABCD"),  # Your UUID
        name="My Custom Characteristic",
    )

    def decode_value(self, data: bytearray) -> int:
        """Your parsing logic."""
        return int(data[0])


# Auto-registers when first instantiated!
custom_char = MyCustomCharacteristic()

# Use it just like standard characteristics
# Option 1: Through the translator (recommended for most use cases)
result = translator.parse_characteristic("ABCD", bytearray([42]))
value = result.value

# Option 2: Direct method call on the characteristic instance
direct_value = custom_char.decode_value(bytearray([42]))
```

**See the [Adding New Characteristics Guide](guides/adding-characteristics.md) for complete examples.**

### What Is NOT Included Out-of-the-Box

The library includes 70+ official SIG characteristics, but doesn't include every possible vendor-specific characteristic. You need to implement those yourself using the extension API.

______________________________________________________________________

## ❌ Real-Time Streaming & High-Frequency Data

### What This Library Does NOT Do (Real-Time Streaming)

This library is optimized for **parsing individual characteristic reads**, not:

- High-frequency notification streams
- Real-time audio/video data
- Sub-millisecond latency requirements
- Buffer management for streaming data
- Data compression/decompression

### Use Cases Where This Matters

**Not Ideal For:**

- Audio streaming (use A2DP or dedicated audio libraries)
- High-frequency sensor data (>100 Hz)
- Video transmission
- Large file transfers

**Perfect For:**

- Periodic sensor readings (temperature, humidity, battery)
- On-demand characteristic reads
- Notification parsing (heart rate, step count)
- Device information queries

### Performance Characteristics

- **Typical parsing time:** \<1ms per characteristic
- **Memory footprint:** Minimal (no buffering)
- **Throughput:** Optimized for individual reads, not streaming

______________________________________________________________________

## ❌ Firmware or Embedded Device Implementation

### What This Library Does NOT Do (Firmware/Embedded)

This is a **client-side** library for applications that interact with BLE devices.

**Not Designed For:**

- Running on BLE peripheral devices
- Embedded systems (ESP32, Arduino, nRF52, etc.)
- Firmware implementation
- BLE server/peripheral role
- Resource-constrained environments

### Reason (Embedded/Firmware)

This library:

- Requires Python 3.9+ runtime
- Uses standard library features not available in embedded contexts
- Focuses on parsing from a client perspective
- Requires relatively more memory/CPU than embedded-optimized code

### Alternative for Embedded

For embedded/firmware development, use:

- Platform-specific BLE stacks (Nordic SDK, ESP-IDF, etc.)
- Embedded C/C++ BLE libraries
- Platform vendor SDKs

______________________________________________________________________

## ❌ Device Management & State Tracking

### What This Library Does NOT Do (Device Management)

**Not Included:**

- Device state management
- Connection history tracking
- Device pairing storage
- Credential management
- Device discovery caching
- Connection retry logic

### What You Should Use

These features are typically provided by:

1. **BLE libraries** (bleak-retry-connector provides retry logic)
1. **Your application** (track device state as needed)
1. **Platform services** (OS-level Bluetooth management)

```python
from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
BATTERY_LEVEL_UUID = "2A19"  # UUID from your BLE library
data1 = bytearray([85])  # First reading
data2 = bytearray([75])  # Second reading

# This library doesn't maintain device state
translator = BluetoothSIGTranslator()

# Each parse call is stateless
result1 = translator.parse_characteristic(BATTERY_LEVEL_UUID, data1)
result2 = translator.parse_characteristic(BATTERY_LEVEL_UUID, data2)
# No state maintained between calls
```

______________________________________________________________________

## ❌ GUI or User Interface

### What This Library Does NOT Do (GUI/Interface)

This is a **library**, not an application.

**Not Included:**

- Desktop applications
- Mobile apps
- Web interfaces
- Device management dashboards
- Configuration tools
- GUI widgets

### How to Build UIs

You can use this library as a foundation:

```python
# SKIP: Example requires Flask web framework and hardware access
# Example: Flask web app
from flask import Flask, jsonify

from bluetooth_sig import BluetoothSIGTranslator

app = Flask(__name__)
translator = BluetoothSIGTranslator()


@app.route("/parse/<uuid>")
def parse_data(uuid):
    # Your BLE read logic here
    raw_data = read_from_device(uuid)
    result = translator.parse_characteristic(uuid, raw_data)
    return jsonify({"value": result.value})
```

______________________________________________________________________

## ❌ Protocol Implementation

### What This Library Does NOT Do (Protocol Implementation)

**Not Provided:**

- BLE stack implementation
- GATT server implementation
- ATT protocol handling
- L2CAP implementation
- HCI interface
- Link layer implementation

### Scope

This library works at the **application layer**, interpreting data according to GATT profile specifications. Lower-level protocol details are handled by your BLE library and operating system.

______________________________________________________________________

## ❌ Hardware Abstraction

### What This Library Does NOT Do (Hardware Abstraction)

**No Hardware Dependencies:**

- Bluetooth adapter management
- Hardware initialization
- Driver installation
- Platform-specific configuration
- USB dongle management

### Reason (Hardware Abstraction)

Hardware abstraction is provided by:

1. **Operating system** Bluetooth stack
1. **BLE library** (bleak, simplepyble, etc.)
1. **Platform drivers**

This library remains hardware-agnostic by working with already-connected data.

______________________________________________________________________

## ❌ Testing Infrastructure for BLE Devices

### What This Library Does NOT Do (Testing Infrastructure)

**Not Included:**

- BLE device simulators
- Mock BLE peripherals
- Hardware test fixtures
- Automated device testing frameworks
- Compliance testing tools

### What You CAN Do

You can easily mock the parsing for testing:

```python
import pytest

from bluetooth_sig import BluetoothSIGTranslator


def test_battery_parsing():
    # ============================================
    # SIMULATED DATA - For testing without device
    # ============================================
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    mock_battery_data = bytearray([85])  # 85% battery

    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic(
        BATTERY_LEVEL_UUID, mock_battery_data
    )
    assert result.value == 85
```

______________________________________________________________________

## Clear Boundaries: What's In Scope vs Out of Scope

### ✅ In Scope (What We Do)

- Parse GATT characteristic data per Bluetooth SIG specs
- Resolve UUIDs to/from names
- Validate data format and ranges
- Provide type-safe data structures
- Support 70+ standard characteristics
- Framework-agnostic parsing

### ❌ Out of Scope (What We Don't Do)

- Device connection and communication
- BLE stack implementation
- Custom/proprietary protocols
- Real-time streaming
- Embedded/firmware implementation
- Device state management
- GUI/application layer
- Hardware abstraction

______________________________________________________________________

## Architecture Decision

This focused scope is **intentional design**:

### Benefits

1. **Simplicity** - One job, done well
1. **Flexibility** - Works with any BLE library
1. **Maintainability** - Focused on standards, not connections
1. **Testability** - Easy to test without hardware
1. **Portability** - Platform-agnostic

### Philosophy

> "Do one thing and do it well" - Unix Philosophy

By focusing exclusively on **standards interpretation**, this library remains:

- Simple to understand
- Easy to maintain
- Compatible with any BLE stack
- Testable without hardware

______________________________________________________________________

## Recommended Tool Stack

For a complete BLE solution:

```text
┌─────────────────────────────────────────────┐
│         Your Application                     │
│  (GUI, business logic, state management)    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       bluetooth-sig                          │
│  (Standards interpretation & data parsing)   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  BLE Connection Library (bleak, simplepyble) │
│  (Device discovery, connection, I/O)         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         OS Bluetooth Stack                   │
│  (Hardware access, protocol implementation) │
└─────────────────────────────────────────────┘
```

Each layer handles its specific responsibilities.

______________________________________________________________________

## Summary

**This library is:**

- A standards interpretation library
- For parsing GATT characteristics
- Framework-agnostic
- Focused on data translation

**This library is NOT:**

- A BLE connection manager
- A device management system
- An application framework
- A protocol implementation

## Next Steps

- [Why Use This Library](why-use.md) - Understand what problems we DO solve
- [What Problems It Solves](what-it-solves.md) - Detailed problem analysis
- [Quick Start](quickstart.md) - Get started with usage
- [BLE Integration Guide](guides/ble-integration.md) - Integrate with BLE libraries
