# AI Coding Agent Instructions for BLE GATT Device

## Project Architecture Overview

This is a **registry-driven BLE GATT framework** with four core layers:

1. **UUID Registry** (`src/ble_gatt_device/gatt/uuid_registry.py`) - Loads Bluetooth SIG official UUIDs from YAML files in `bluetooth_sig/` submodule
2. **Base Classes** (`src/ble_gatt_device/gatt/{services,characteristics}/base.py`) - Provide automatic UUID resolution via class name parsing
3. **Implementations** - Concrete services/characteristics that inherit from base classes
4. **Real Device Integration** (`src/ble_gatt_device/core.py`) - Bleak-based BLE connection and data parsing

### Critical Architecture Principle: Name-Based UUID Resolution

Classes automatically resolve UUIDs through **intelligent name parsing**:
- `BatteryService` → tries "BatteryService", then "Battery" → finds UUID "180F"
- `TemperatureCharacteristic` → tries "TemperatureCharacteristic", "Temperature" → finds UUID "2A6E"
- **Fallback**: explicit `_service_name` or `_characteristic_name` attributes override class name parsing

## Essential Development Workflows

### Real Device Testing (NEW)
```bash
# Scan for BLE devices
python scripts/test_real_device.py scan

# Test connection to specific device (use 10s timeout - critical!)
python scripts/test_real_device.py AA:BB:CC:DD:EE:FF

# Debug connection issues with detailed logging
python scripts/test_real_device_debug.py AA:BB:CC:DD:EE:FF

# Test different connection strategies
python scripts/test_connection_strategies.py AA:BB:CC:DD:EE:FF
```

### Running the Comprehensive Test Suite
```bash
# Core validation - 80+ tests that verify ALL services/characteristics
python -m pytest tests/test_registry_validation.py -v

# Quick discovery check
python tests/test_registry_validation.py

# Fallback behavior tests (name resolution edge cases)  
python -m pytest tests/test_registry_validation.py::TestNameResolutionFallback -v
```

### Data Parsing Testing
```bash
# Test framework parsing with simulated data
python scripts/test_parsing.py

# Test core BLEGATTDevice functionality
python scripts/test_core.py
```

## Project-Specific Patterns

### BLE Connection Critical Pattern
**NEVER use default timeouts** - many devices require specific timing:
```python
# ✅ Correct - use optimized timeout
async with BleakClient(device, timeout=10.0) as client:
    # Connection logic

# ❌ Wrong - default timeout causes issues
async with BleakClient(device) as client:
    # May timeout on service discovery
```

### UUID Transformation Pattern
Framework transforms UUIDs internally:
```python
# Raw Bleak UUID: "00002a19-0000-1000-8000-00805f9b34fb"
# Framework UUID: "00002A1900001000800000805F9B34FB"
# When reading data, map back to original format for Bleak calls
```

### Data Parsing Implementation
All characteristics must implement `parse_value()`:
```python
@dataclass
class MyCharacteristic(BaseCharacteristic):
    def parse_value(self, data: bytearray) -> float:
        # Convert raw bytes to meaningful value
        return struct.unpack("<f", data)[0]
    
    @property
    def unit(self) -> str:
        return "°C"  # Always include units for sensors
```

### Real Device Integration
```python
# BLEGATTDevice provides two methods:
device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
raw_data = await device.read_characteristics()        # Raw bytearray values
parsed_data = await device.read_parsed_characteristics()  # Parsed with units
```

## Critical Integration Points

### Connection Error Patterns
Common connection issues and solutions:
- **TimeoutError during service discovery**: Use `timeout=10.0` instead of longer timeouts
- **Device busy/connected**: Disconnect from phones/other apps first
- **Permission denied**: Run with `sudo` or add user to bluetooth group
- **Device not found**: Check if device is in advertising/pairing mode

### Bluetooth SIG Submodule
- **Location**: `bluetooth_sig/` (git submodule)
- **Update**: `git submodule update --remote` to get latest Bluetooth SIG assignments
- **Path resolution**: UuidRegistry tries both development (`bluetooth_sig/`) and installed package locations

### UUID Registry Integration
- **Never hardcode UUIDs** - always use the registry-based lookup
- **YAML source**: `bluetooth_sig/assigned_numbers/uuids/{service_uuids,characteristic_uuids}.yaml`
- **Lookup patterns**: `uuid_registry.get_service_info("Battery")` or `uuid_registry.get_characteristic_info("2A19")`

## Adding New Components

### Adding New Services
1. **Create service class** in `src/ble_gatt_device/gatt/services/new_service.py`:
```python
@dataclass
class MyNewService(BaseGattService):
    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        return {"Characteristic Name": CharacteristicClass}
```

2. **Register in** `src/ble_gatt_device/gatt/services/__init__.py`:
```python
_services: List[Type[BaseGattService]] = [
    MyNewService,  # Add here
    # ... existing services
]
```

### Adding New Characteristics
1. **Create characteristic** in `src/ble_gatt_device/gatt/characteristics/new_char.py`:
```python
@dataclass
class MyCharacteristic(BaseCharacteristic):
    def __post_init__(self):
        self.value_type = "float"  # string|int|float|boolean|bytes
        super().__post_init__()
    
    def parse_value(self, data: bytearray) -> float:
        return struct.unpack("<f", data)[0]
```

2. **Register in** `src/ble_gatt_device/gatt/characteristics/__init__.py`

## Debugging Real Device Issues

### Connection Debugging Workflow
1. **Verify device discovery**: `python scripts/test_real_device.py scan`
2. **Test basic connection**: `python scripts/test_connection_strategies.py <MAC>`
3. **Full diagnostic**: `python scripts/test_real_device_debug.py <MAC>`
4. **Check parsing**: `python scripts/test_parsing.py` (with simulated data)

### Common Device Types Tested
- **Nordic Thingy:52**: Environmental sensor with battery, temperature, humidity, pressure
- **Requires**: `timeout=10.0` for successful connection
- **Services**: Battery (180F), Environmental Sensing (181A), Device Information (180A)

## Architecture Validation
- **Run full test suite** after any changes - the 80+ tests catch integration issues
- **Test real device connections** after modifying core connection logic
- **Verify parsing** with both simulated and real device data
- **Check UUID transformations** when adding new characteristics

This framework prioritizes **real device compatibility** and **robust data parsing** alongside the registry-driven architecture. Connection timing and UUID handling are critical for successful BLE integration.
