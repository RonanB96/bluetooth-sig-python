# AI Code Review Instructions for BLE GATT Device Framework

## Overview

This document provides comprehensive guidelines for AI agents reviewing pull requests in the BLE GATT Device Framework. This registry-driven BLE framework has specific architectural patterns, performance requirements, and testing standards that must be validated during code review.

## Critical Architecture Validation

### 1. Registry-Driven UUID Resolution

**✅ MUST CHECK:**
- **No hardcoded UUIDs**: All UUIDs must come from the registry system
- **Name-based resolution**: Classes should use intelligent name parsing (e.g., `BatteryService` → "Battery" → UUID "180F")
- **Fallback patterns**: Explicit `_service_name` or `_characteristic_name` should override class name parsing only when necessary

**❌ RED FLAGS:**
```python
# WRONG - hardcoded UUID
class MyService(BaseGattService):
    SERVICE_UUID = "180F"  # Should use registry lookup

# WRONG - bypassing registry
uuid = "00002A19-0000-1000-8000-00805F9B34FB"
```

**✅ CORRECT PATTERNS:**
```python
# Service with implicit name resolution
class BatteryService(BaseGattService):  # → "Battery" → "180F"
    pass

# Service with explicit name override
class GenericAccessService(BaseGattService):
    _service_name = "GAP"  # Override for non-standard names
```

### 2. Layer Separation Architecture

**CRITICAL RULE**: `GATT ← Translation ← Home Assistant` (never reverse)

**✅ VALIDATE:**
- GATT layer classes NEVER import Home Assistant modules
- Data parsing stays in GATT characteristics (`decode_value()` method)
- Home Assistant metadata (`device_class`, `state_class`) stays in GATT layer
- Clean separation between BLE communication and application logic

**❌ REJECT IF:**
```python
# WRONG - HA imports in GATT layer
from homeassistant.components.sensor import SensorEntity  # In GATT layer
```

### 3. Data Parsing Implementation

**✅ REQUIRED for all characteristics:**
```python
@dataclass
class MyCharacteristic(BaseCharacteristic):
    def encode_value(self, data: bytearray) -> float:
        """Convert raw bytes to meaningful value."""
        return struct.unpack("<f", data)[0]

    @property
    def unit(self) -> str:
        """Always include units for sensors."""
        return "°C"

    @property
    def device_class(self) -> str:
        """HA device class for sensors."""
        return "temperature"
```

## BLE Connection Requirements

### 1. Timeout Critical Pattern

**✅ MUST USE** optimized timeouts:
```python
# CORRECT - 10s timeout is critical for device compatibility
async with BleakClient(device, timeout=10.0) as client:
    # Connection logic
```

**❌ REJECT:**
```python
# WRONG - default timeout causes issues with many devices
async with BleakClient(device) as client:
    # May timeout on service discovery
```

### 2. UUID Transformation Handling

**✅ VALIDATE** proper UUID format handling:
- Framework UUIDs: `"00002A1900001000800000805F9B34FB"` (uppercase, no dashes)
- Bleak UUIDs: `"00002a19-0000-1000-8000-00805f9b34fb"` (lowercase, with dashes)
- Proper conversion between formats when interfacing with Bleak

### 3. Error Handling Patterns

**✅ REQUIRED** for BLE operations:
- Timeout handling with device-specific guidance
- Permission error detection and solutions
- Device busy/connection state management
- Graceful fallback for unsupported characteristics

## Testing Requirements

### 1. Registry Validation Tests

**✅ MANDATORY for new services/characteristics:**
- Test class name resolution works correctly
- Verify UUID registry lookup succeeds
- Validate fallback behavior with explicit names
- Test edge cases in name parsing

### 2. Real Device Testing Considerations

**✅ VALIDATE** test script compatibility:
- Scripts should work with `timeout=10.0` pattern
- Test both simulated and real device scenarios
- Validate parsing with actual BLE data formats
- Connection debugging capabilities

### 3. Architecture Separation Tests

**✅ ENSURE** tests validate:
- No circular imports between layers
- GATT classes don't depend on HA components
- Registry-driven resolution works end-to-end
- Data parsing produces correct types and units

## Code Quality Standards

### 1. Type Safety

**✅ REQUIRED:**
- Complete type hints throughout
- Dataclass-based design for characteristics/services
- Proper generic types for collections
- Type-safe UUID registry lookups

### 2. Documentation Standards

**✅ VALIDATE:**
- Clear docstrings for all public methods
- Architecture principle explanations
- BLE-specific timing and compatibility notes
- Real device testing examples

### 3. Naming Conventions

**✅ CONSISTENT patterns:**
- Service classes: `{Name}Service` (e.g., `BatteryService`)
- Characteristic classes: `{Name}Characteristic` (e.g., `TemperatureCharacteristic`)
- Registry methods: `get_service_info()`, `get_characteristic_info()`

## Performance & Security

### 1. Connection Performance

**✅ VALIDATE:**
- Proper timeout usage (`timeout=10.0`)
- Efficient service discovery patterns
- Minimal connection overhead
- Graceful handling of slow devices

### 2. Security Considerations

**✅ CHECK:**
- No secrets or credentials in code
- Proper input validation for BLE data
- Safe parsing of binary data (buffer overflows)
- Error messages don't leak sensitive info

### 3. Resource Management

**✅ ENSURE:**
- Proper async context manager usage
- BLE client cleanup in error cases
- Memory efficient data parsing
- No resource leaks in long-running operations

## Common Issues to Flag

### 1. Architecture Violations

- **Layer boundary violations**: HA imports in GATT layer
- **Registry bypassing**: Hardcoded UUIDs instead of registry lookup
- **Circular dependencies**: Services depending on characteristics incorrectly

### 2. BLE Integration Problems

- **Default timeouts**: Missing explicit `timeout=10.0`
- **UUID format mismatches**: Wrong format for Bleak vs framework
- **Connection state issues**: Not handling device busy/connected states

### 3. Testing Gaps

- **Missing registry tests**: New services/characteristics without validation
- **No real device consideration**: Scripts that won't work with actual hardware
- **Incomplete parsing tests**: Missing edge cases for data conversion

## Review Checklist

For each PR, verify:

- [ ] **Architecture**: Maintains clean layer separation
- [ ] **Registry**: Uses UUID registry system consistently
- [ ] **Timeouts**: BLE connections use `timeout=10.0`
- [ ] **Parsing**: All characteristics implement `encode_value()`
- [ ] **Types**: Complete type hints and dataclass usage
- [ ] **Tests**: Registry validation and parsing tests included
- [ ] **Documentation**: Clear docstrings and examples
- [ ] **Performance**: Efficient BLE patterns and resource cleanup
- [ ] **Security**: No hardcoded secrets, safe data parsing

## Framework-Specific Patterns

### UUID Registry Integration
```python
# Pattern for looking up UUIDs
info = uuid_registry.get_service_info("Battery")
if info:
    uuid = info.uuid
    name = info.name
```

### Service Registration
```python
# Pattern for registering new services
_services: List[Type[BaseGattService]] = [
    NewService,  # Add new services here
    # ... existing services
]
```

### Characteristic Implementation
```python
# Complete characteristic pattern
@dataclass
class NewCharacteristic(BaseCharacteristic):
    def __post_init__(self):
        self.value_type = "float"  # string|int|float|boolean|bytes
        super().__post_init__()

    def encode_value(self, data: bytearray) -> float:
        return struct.unpack("<f", data)[0]

    @property
    def unit(self) -> str:
        return "°C"

    @property
    def device_class(self) -> str:
        return "temperature"
```

This framework prioritizes **real device compatibility**, **architectural integrity**, and **robust data parsing**. Code reviews should ensure all changes maintain these critical qualities while following the established patterns and performance requirements.