# Bluetooth SIG Examples

This directory contains simplified, focused examples demonstrating the core functionality of the bluetooth_sig library.

## Core Examples

### basic_usage.py
Demonstrates basic read/write operations with the bluetooth_sig library.

```bash
python examples/basic_usage.py --address 12:34:56:78:9A:BC
```

### service_discovery.py
Shows the Device class API for service and characteristic discovery.

```bash
python examples/service_discovery.py --address 12:34:56:78:9A:BC
```

### notifications.py
Handles BLE notifications with characteristic parsing.

```bash
python examples/notifications.py --address 12:34:56:78:9A:BC --characteristic 2A19
```

### advertising_parsing.py
Parses BLE advertising data packets using the AdvertisingParser.

```bash
python examples/advertising_parsing.py --data "02010605FF4C001005011C7261F4"
```

### library_integration.py
Shows integration patterns for different BLE libraries and the Device class.

```bash
python examples/library_integration.py --address 12:34:56:78:9A:BC
python examples/library_integration.py --check-libraries
```

## Shared Utilities

### shared_utils.py
Contains common functions used across examples:
- Library availability checking
- Device creation helpers
- BLE connection utilities
- Parsing and display functions

## Running Examples

All examples require a BLE device address. You can discover devices using:

```bash
# Use any BLE scanning tool or check your system's Bluetooth settings
```

The examples will automatically use available BLE libraries (primarily Bleak) and handle library availability gracefully.
