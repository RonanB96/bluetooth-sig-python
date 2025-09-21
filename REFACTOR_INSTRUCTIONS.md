# AI Agent Instructions: Refactor Device Class and Examples

## Overview

This document provides step-by-step instructions for an AI agent to refactor the Bluetooth SIG library's device class and example scripts. The goal is to improve code organization, reduce duplication, and enhance maintainability.

## Phase 1: Extract Advertising Logic from Devi## Implementation Order

1. ✅ Create MD instructions file
2. ✅ Extract `AdvertisingParser` class
3. ✅ Update `Device` class to use `AdvertisingParser`
4. ✅ Analyze missing features compared to standard BLE libraries
5. ✅ Implement missing features (service discovery, batch operations, connection state tracking)
6. ⏳ Simplify example scripts
7. ⏳ Update examples for new architecture
8. ⏳ Update tests
9. ⏳ Validate functionality## Current State Analysis

The `Device` class in `/src/bluetooth_sig/device/device.py` contains extensive advertising data parsing logic that should be extracted into a separate class. This includes:

- `parse_advertiser_data()` method
- `_is_extended_advertising_pdu()` method
- `_parse_extended_advertising()` method
- `_parse_legacy_advertising()` method
- `_parse_extended_pdu()` method
- `_parse_extended_header()` method
- `_parse_auxiliary_packets()` method
- `_parse_ad_structures()` method

### Step 1.1: Create AdvertisingParser Class

Create a new file `/src/bluetooth_sig/device/advertising_parser.py` with the following structure:

```python
from __future__ import annotations

from typing import Any

from ..types import (
    BLEAdvertisementTypes,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    DeviceAdvertiserData,
    ParsedADStructures,
    PDUConstants,
    PDUFlags,
    PDUType,
)


class AdvertisingParser:
    """Parser for BLE advertising data packets.

    Handles both legacy and extended advertising PDU formats,
    extracting device information, manufacturer data, and service UUIDs.
    """

    def parse_advertising_data(self, raw_data: bytes) -> DeviceAdvertiserData:
        """Parse raw advertising data and return structured information.

        Args:
            raw_data: Raw bytes from BLE advertising packet

        Returns:
            DeviceAdvertiserData with parsed information
        """
        # Implementation moved from Device.parse_advertiser_data()
        pass

    # All private methods from Device class related to advertising parsing
    # should be moved here with appropriate access modifiers
```

### Step 1.2: Move Advertising Methods

Move all advertising-related methods from `Device` class to `AdvertisingParser`:

1. `parse_advertiser_data()` → `parse_advertising_data()`
2. `_is_extended_advertising_pdu()` → `_is_extended_pdu()`
3. `_parse_extended_advertising()` → `_parse_extended_pdu()`
4. `_parse_legacy_advertising()` → `_parse_legacy_pdu()`
5. `_parse_extended_pdu()` → `_parse_extended_pdu_header()`
6. `_parse_extended_header()` → `_parse_extended_header()`
7. `_parse_auxiliary_packets()` → `_parse_auxiliary_packets()`
8. `_parse_ad_structures()` → `_parse_ad_structures()`

### Step 1.3: Update Device Class

Modify the `Device` class to use the new `AdvertisingParser`:

```python
class Device:
    def __init__(self, address: str, translator: SIGTranslatorProtocol) -> None:
        # ... existing code ...
        self.advertising_parser = AdvertisingParser()

    def parse_advertiser_data(self, raw_data: bytes) -> None:
        """Parse raw advertising data and update device information."""
        parsed_data = self.advertising_parser.parse_advertising_data(raw_data)
        self.advertiser_data = parsed_data

        # Update device name if not set
        if parsed_data.local_name and not self.name:
            self.name = parsed_data.local_name
```

### Step 1.4: Update Imports

Update all files that import from `device.py` to also import `AdvertisingParser` if needed.

## Phase 2: Compare with Standard BLE Libraries

### Analysis Requirements

Compare the current `Device` class with standard BLE connection libraries to determine if it contains everything needed to abstract reading and writing to characteristics.

### Standard BLE Library Patterns

Common BLE libraries provide:

- Connection management (connect/disconnect)
- Service discovery
- Characteristic read/write operations
- Notification subscriptions
- Advertising data parsing

### Current Device Class Capabilities

The `Device` class currently provides:

- ✅ Connection management via `ConnectionManagerProtocol`
- ✅ Characteristic read/write via `read()`/`write()` methods
- ✅ Notification handling via `start_notify()`/`stop_notify()`
- ✅ Service management via `add_service()`
- ✅ Advertising data parsing (to be extracted)
- ✅ Characteristic data access via `get_characteristic_data()`

### Missing Features Analysis

After analysis, the following features were identified as missing for complete BLE abstraction:

1. **Service Discovery**: No methods to discover services from the connection manager
2. **Batch Operations**: No methods for reading/writing multiple characteristics at once
3. **Connection State Tracking**: Limited connection state visibility
4. **Enhanced Service Queries**: Better methods for querying services and characteristics

But remember this lib is not a connection manager, it just uses one and provides a wrapper for a common interface.

### Implementation Plan

Based on the analysis, the following features have been implemented:

```python
class Device:
    async def discover_services(self) -> dict[str, Any]:
        """Discover all services and characteristics from the device."""
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached")

        services = await self.connection_manager.get_services()
        # Parse and store services
        return services

    async def read_multiple(self, char_names: list[str | CharacteristicName]) -> dict[str, Any | None]:
        """Read multiple characteristics in batch."""

    async def write_multiple(self, data_map: dict[str | CharacteristicName, bytes]) -> dict[str, bool]:
        """Write to multiple characteristics in batch."""

    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected."""

    def get_service_by_uuid(self, service_uuid: str) -> DeviceService | None:
        """Get a service by its UUID."""

    def list_characteristics(self, service_uuid: str | None = None) -> dict[str, list[str]]:
        """List all characteristics, optionally filtered by service."""
```## Phase 3: Reduce Example Scripts

### Current Issues

The example scripts have significant overlap and contain excessive "marketing" style printouts that don't add value:

1. **Overlapping Code**: `ble_utils.py` contains shared utilities, but individual examples still duplicate logic
2. **Marketing Printouts**: Excessive emojis, ASCII art, and promotional text
3. **Redundant Examples**: Multiple examples doing similar things with different libraries

### Step 3.1: Consolidate Shared Utilities

Create a more focused `examples/shared_utils.py` that contains only essential utilities:

```python
# examples/shared_utils.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device

def setup_library_check() -> dict[str, bool]:
    """Check which BLE libraries are available."""
    libraries = {}

    try:
        import bleak
        libraries['bleak'] = True
    except ImportError:
        libraries['bleak'] = False

    # ... other library checks

    return libraries

def create_device(address: str) -> Device:
    """Create a configured Device instance."""
    translator = BluetoothSIGTranslator()
    return Device(address, translator)
```

### Step 3.2: Simplify Example Structure

Reduce examples to focus on core functionality:

1. **Remove Marketing Content**: Strip out excessive emojis, ASCII art, and promotional text
2. **Focus on Code**: Keep only essential comments and documentation
3. **Consolidate Examples**: Merge similar examples, keep only one per major pattern

### Step 3.3: Create Core Examples

Keep these essential examples:

1. **`basic_usage.py`**: Simple read/write operations
2. **`service_discovery.py`**: Service and characteristic discovery
3. **`notifications.py`**: Notification handling
4. **`advertising_parsing.py`**: Advertising data parsing
5. **`library_integration.py`**: Integration patterns for different BLE libraries

### Step 3.4: Update Example Documentation

Update `examples/README.md` to reflect the simplified structure:

```markdown
# Bluetooth SIG Examples

## Core Examples

### basic_usage.py
Demonstrates basic read/write operations with the Device class.

### service_discovery.py
Shows how to discover services and characteristics.

### notifications.py
Handles BLE notifications and callbacks.

### advertising_parsing.py
Parses BLE advertising data packets.

### library_integration.py
Shows integration patterns for different BLE libraries.

## Running Examples

```bash
```

## Running Examples

```bash
# Basic usage
python examples/basic_usage.py --address 12:34:56:78:9A:BC

# Service discovery
python examples/service_discovery.py --address 12:34:56:78:9A:BC
```
```
```

## Phase 4: Update Examples for New Architecture

### Step 4.1: Update Imports

Update all examples to use the new `AdvertisingParser` and simplified `Device` class:

```python
# Before
from bluetooth_sig.device import Device

# After
from bluetooth_sig.device import Device, AdvertisingParser
```

### Step 4.2: Simplify Connection Management

Use the improved connection management features:

```python
# Before: Manual connection management
device = Device(address, translator)
device.attach_connection_manager(connection_manager)
await device.connect()

# After: Simplified with context manager support
async with device.connect() as connected_device:
    # Use device
    pass
```

### Step 4.3: Update Advertising Examples

Update advertising examples to use the new `AdvertisingParser`:

```python
# Before: Device handles advertising
device.parse_advertiser_data(raw_data)

# After: Direct parser usage
parser = AdvertisingParser()
advertising_data = parser.parse_advertising_data(raw_data)
```

### Step 4.4: Remove Redundant Code

Remove duplicate utility functions and consolidate common patterns.

## Phase 5: Testing and Validation

### Step 5.1: Update Tests

Update existing tests to work with the new architecture:

1. Update device tests to use new `AdvertisingParser`
2. Update example tests to use simplified examples
3. Add tests for new features

### Step 5.2: Validate Functionality

Ensure all functionality still works:

1. Advertising data parsing
2. Device connection management
3. Characteristic read/write operations
4. Notification handling
5. Service discovery

### Step 5.3: Performance Testing

Verify that the refactoring doesn't impact performance:

1. Advertising parsing speed
2. Connection establishment time
3. Characteristic operation latency

## Implementation Order

1. ✅ Create MD instructions file (this file)
2. ⏳ Extract `AdvertisingParser` class
3. ⏳ Update `Device` class to use `AdvertisingParser`
4. ⏳ Analyze missing features compared to standard BLE libraries
5. ⏳ Implement any missing features
6. ⏳ Simplify example scripts
7. ⏳ Update examples for new architecture
8. ⏳ Update tests
9. ⏳ Validate functionality

## Success Criteria

- ✅ Advertising logic successfully extracted from `Device` class
- ✅ `Device` class provides complete abstraction for BLE operations
- ✅ Example scripts are simplified and focused
- ✅ All tests pass
- ✅ Performance is maintained or improved
- ✅ - ✅ Code is more maintainable and follows single responsibility principle
