# AI Coding Agent Instructions for BLE GATT Device

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

BLE GATT Device is a **registry-driven BLE GATT framework** with real device integration and Home Assistant compatibility. This is a Python project with a four-layer architecture: UUID Registry → Base Classes → Implementations → Real Device Integration.

**CRITICAL**: This project requires specific network access for Bluetooth SIG data and PyPI packages. Some commands may fail due to network limitations - document failures and provide alternatives.

## Essential Development Setup

### Prerequisites and Bootstrap
- Python 3.9+ (tested with 3.9, 3.10, 3.11, 3.12)
- Git with submodule support
- Network access to PyPI and Bitbucket (for Bluetooth SIG data)

**CRITICAL DEPENDENCY**: This project REQUIRES the bluetooth_sig submodule to function. Without it, the entire framework fails to import.

### Core Setup Commands - VALIDATE EACH STEP
1. **Clone and enter repository:**
```bash
git clone https://github.com/RonanB96/ble_gatt_device.git
cd ble_gatt_device
```

2. **Initialize Bluetooth SIG submodule (BLOCKING REQUIREMENT):**
```bash
git submodule init
git submodule update
# TIMEOUT WARNING: May take 5+ minutes. NEVER CANCEL.
# BLOCKING ISSUE: If this fails with "Could not resolve host: bitbucket.org"
# the entire framework cannot be imported or tested. Document this as a 
# fundamental limitation requiring network access to bitbucket.org.
```

3. **Verify submodule initialization (CRITICAL VALIDATION):**
```bash
ls -la bluetooth_sig/assigned_numbers/uuids/
# Should show service_uuids.yaml and characteristic_uuids.yaml
# If these files are missing, ALL subsequent commands will fail
```

4. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# Windows: .venv\Scripts\activate
```

5. **Install dependencies (NETWORK INTENSIVE - 5+ minutes):**
```bash
# NEVER CANCEL: Installation takes 3-10 minutes depending on network
pip install --timeout 600 -e ".[dev]"
# KNOWN ISSUE: May fail with network timeouts or PyPI connectivity issues
# If this fails, try: pip install --timeout 600 bleak pyyaml pytest pytest-asyncio
```

## Core Validation and Testing

### Essential Test Commands - MEASURE AND VALIDATE
**NEVER CANCEL these commands - they validate the entire framework:**

1. **Basic Python compilation check (30 seconds):**
```bash
find src -name "*.py" -exec python3 -m py_compile {} \;
# Should complete silently with no errors
```

2. **Core framework validation (80+ tests, 2-5 minutes):**
```bash
# NEVER CANCEL: Takes 2-5 minutes, timeout at 10+ minutes
python -m pytest tests/test_registry_validation.py -v
# This validates ALL services and characteristics against the registry
# REQUIRES: bluetooth_sig submodule and pytest installation
```

3. **Quick discovery validation (30 seconds):**
```bash
PYTHONPATH=src python tests/test_registry_validation.py
# Direct execution for quick validation without pytest
# REQUIRES: bluetooth_sig submodule to be initialized
```

4. **UUID registry validation (1 minute):**
```bash
python -m pytest tests/test_uuid_registry.py -v
# REQUIRES: bluetooth_sig submodule and pytest installation
# Will fail if bluetooth_sig submodule failed to initialize
```

### Development Script Validation
**CRITICAL: ALL scripts require bluetooth_sig submodule to be initialized**

1. **YAML loading test (requires submodule, 30 seconds):**
```bash
PYTHONPATH=src python scripts/test_yaml_loading.py
# BLOCKING FAILURE: Will fail with FileNotFoundError if bluetooth_sig submodule is missing
```

2. **Core parsing test (requires submodule, 1 minute):**
```bash
PYTHONPATH=src python scripts/test_parsing.py
# BLOCKING FAILURE: Cannot import framework without submodule
```

3. **Real device scanning (requires Bluetooth permissions and submodule):**
```bash
PYTHONPATH=src python scripts/test_real_device.py scan
# BLOCKING FAILURE: Cannot import framework without submodule
# Also may require 'sudo' or Bluetooth permissions
```

**If submodule initialization failed**: Document that ALL framework functionality is unavailable until network access to bitbucket.org is restored.

### What CAN be validated without submodule:
1. **Python syntax checking:**
```bash
find src -name "*.py" -exec python3 -m py_compile {} \;
# This works - validates Python syntax without imports
```

2. **Project structure examination:**
```bash
find src -name "*.py" | head -20
# Shows source code organization
```

## Linting and Code Quality

### Available Linting Commands
**ONLY use these if the tools are installed:**

1. **Flake8 validation (2 minutes):**
```bash
flake8 src/ tests/
# May not be available if dev dependencies failed to install
```

2. **Black formatting check:**
```bash
black --check src/ tests/
# May not be available if dev dependencies failed to install
```

3. **Pylint analysis (3-5 minutes):**
```bash
# NEVER CANCEL: Pylint can take 3-5 minutes on this codebase
pylint src/ble_gatt_device
```

## Manual Validation Scenarios

### Core Framework Validation
**CRITICAL: All framework validation requires bluetooth_sig submodule**

1. **Test module imports (requires submodule):**
```bash
PYTHONPATH=src python3 -c "import ble_gatt_device; print('✅ Module imports successfully')"
# BLOCKING FAILURE: Will fail with FileNotFoundError if submodule missing
```

2. **Test UUID registry functionality (requires submodule):**
```bash
PYTHONPATH=src python3 -c "
from ble_gatt_device.gatt.uuid_registry import UuidRegistry
registry = UuidRegistry()
print('✅ UUID Registry initialized')
"
# EXPECTED FAILURE: Will fail with FileNotFoundError if bluetooth_sig submodule is missing
```

3. **Test service discovery (requires submodule):**
```bash
PYTHONPATH=src python3 -c "
from ble_gatt_device.gatt.services import discover_service_classes
services = discover_service_classes()
print(f'✅ Discovered {len(services)} service classes')
"
# EXPECTED FAILURE: Will fail with FileNotFoundError if bluetooth_sig submodule is missing
```

### Alternative Validation (when submodule unavailable):
1. **Python syntax validation:**
```bash
find src -name "*.py" -exec python3 -m py_compile {} \;
echo "✅ All Python files compile successfully"
```

2. **Source code examination:**
```bash
ls -la src/ble_gatt_device/gatt/
echo "✅ Source structure verified"
```

### Real Device Integration Testing
**For Bluetooth-enabled environments only:**

1. **Device scanning:**
```bash
# Requires Bluetooth permissions, may need sudo
PYTHONPATH=src python scripts/test_real_device.py scan
```

2. **Connection strategy testing:**
```bash
# Replace MAC_ADDRESS with actual device
PYTHONPATH=src python scripts/test_connection_strategies.py AA:BB:CC:DD:EE:FF
```

## Troubleshooting Known Issues

### Network and Dependency Issues
1. **PyPI timeout failures:**
   - Use `pip install --timeout 600` for longer timeout
   - Try installing individual packages: `pip install bleak pyyaml pytest`
   - Document if installation fails due to network limitations

2. **Bluetooth SIG submodule failure (CRITICAL):**
   - Expected if bitbucket.org is unreachable
   - **IMPACT**: Entire framework cannot import without submodule
   - **Workaround**: None - must document this as a blocking issue
   - **Check status**: `git submodule status` should show initialized submodule

3. **Permission denied for Bluetooth:**
   - Run with `sudo` for Bluetooth access
   - Or add user to bluetooth group: `sudo usermod -a -G bluetooth $USER`

### Test Failures
1. **FileNotFoundError during import:**
   - **Root cause**: Missing bluetooth_sig submodule
   - **Solution**: Ensure `git submodule init && git submodule update` succeeds
   - **If network blocked**: Document as known limitation

2. **Registry validation failures:**
   - Usually indicates missing bluetooth_sig submodule
   - Check submodule status: `git submodule status`

3. **Import errors:**
   - Ensure `PYTHONPATH=src` for script execution
   - Check virtual environment activation
   - Verify submodule is initialized

## Architecture-Specific Patterns

### Critical BLE Connection Pattern
**ALWAYS use timeout=10.0 for BLE connections:**
```python
# ✅ Correct
async with BleakClient(device, timeout=10.0) as client:
    # Connection logic

# ❌ Wrong - causes timeouts
async with BleakClient(device) as client:
    # May fail on service discovery
```

### Adding New Components
1. **Services:** Add to `src/ble_gatt_device/gatt/services/`
2. **Characteristics:** Add to `src/ble_gatt_device/gatt/characteristics/`
3. **Register in respective `__init__.py` files**
4. **Always run registry validation tests after adding components**

## Development Workflow Commands

### Standard Development Cycle
1. **Make changes to source code**
2. **Run syntax check:** `find src -name "*.py" -exec python3 -m py_compile {} \;`
3. **Run core validation:** `python -m pytest tests/test_registry_validation.py -v`
4. **Test functionality:** Run relevant scripts in `scripts/` directory
5. **Format and lint (if tools available):** `black src/ && flake8 src/`

### Before Committing
**ALWAYS run these validation steps:**
1. Core registry validation (2-5 minutes)
2. Python compilation check (30 seconds)
3. Manual import test
4. Run any related scripts to test functionality

## Timeout Guidelines and Expectations

- **pip install:** 5-10 minutes, timeout at 15+ minutes
- **pytest registry validation:** 2-5 minutes, timeout at 10+ minutes
- **Submodule update:** 3-5 minutes, timeout at 10+ minutes
- **pylint analysis:** 3-5 minutes, timeout at 10+ minutes
- **Script execution:** 30 seconds - 2 minutes, timeout at 5+ minutes

**NEVER CANCEL** operations that are within expected time ranges. This framework has extensive validation that takes time to complete.

## Common File Locations

- **Main source:** `src/ble_gatt_device/`
- **Tests:** `tests/` (especially `test_registry_validation.py`)
- **Development scripts:** `scripts/`
- **Configuration:** `pyproject.toml`, `.flake8`
- **Bluetooth data:** `bluetooth_sig/` (submodule, may be empty)

## Additional Architecture Details

### Registry-Driven UUID Resolution
Classes automatically resolve UUIDs through **intelligent name parsing**:
- `BatteryService` → tries "BatteryService", then "Battery" → finds UUID "180F"
- `TemperatureCharacteristic` → tries "TemperatureCharacteristic", "Temperature" → finds UUID "2A6E"
- **Fallback**: explicit `_service_name` or `_characteristic_name` attributes override class name parsing

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
