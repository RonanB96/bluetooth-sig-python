# Bluetooth SIG Examples

This directory contains clean, focused examples demonstrating the core functionality of the bluetooth_sig library with minimal overlap and organized utilities.

## Example BLE Libraries

### with_bleak_retry.py
Demonstrates robust BLE connections using Bleak with retry logic and SIG parsing.

```bash
python examples/with_bleak_retry.py --address 12:34:56:78:9A:BC
python examples/with_bleak_retry.py --scan
```

### with_simpleble.py
Shows integration with SimplePyBLE (cross-platform synchronous BLE library) and SIG parsing.

```bash
python examples/with_simpleble.py --address 12:34:56:78:9A:BC
python examples/with_simpleble.py --scan
```

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

### pure_sig_parsing.py
Shows pure SIG standards parsing without any BLE connection library dependencies.

```bash
python examples/pure_sig_parsing.py
```

## Utilities Package

The `utils/` subdirectory contains organized utility modules split by functionality:

- **`library_detection.py`** - BLE library availability checking
- **`device_scanning.py`** - Device discovery and scanning functions
- **`bleak_integration.py`** - Bleak-specific integration functions
- **`simpleble_integration.py`** - SimplePyBLE-specific integration functions
- **`data_parsing.py`** - Data parsing and display utilities
- **`mock_data.py`** - Mock data for testing without hardware
- **`demo_functions.py`** - Demo and comparison functions

### Using the Utils Package

```python
from utils import (
    show_library_availability,
    scan_with_bleak,
    parse_and_display_results,
    mock_ble_data,
)
```

## Deprecated Files

- **`shared_utils.py`** - Deprecated, use `utils/` package instead
- **`ble_utils.py.bak`** - Backup of original large utilities file

## Running Examples

All examples require a BLE device address. You can discover devices using:

```bash
# Using bleak-retry example
python examples/with_bleak_retry.py --scan

# Using SimplePyBLE example  
python examples/with_simpleble.py --scan
```

The examples will automatically use available BLE libraries and handle library availability gracefully.

## Design Philosophy

This examples directory follows these principles:

1. **Minimal Overlap** - Each example focuses on a specific use case
2. **Clean Separation** - Utilities are organized by functionality in the `utils/` package
3. **Library Agnostic** - Core SIG parsing works with any BLE library
4. **Production Ready** - Examples demonstrate robust patterns suitable for production use
