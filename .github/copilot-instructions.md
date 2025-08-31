# AI Coding Agent Instructions for BLE GATT Device

Reference these instructions as primary guidance while using search and bash commands to complement and verify the information provided here.

## Project Overview

BLE GATT Device is a **registry-driven BLE GATT framework** with real device integration and Home Assistant compatibility. This is a Python project with a four-layer architecture: UUID Registry → Base Classes → Implementations → Real Device Integration.

**Current State**: 2 services (Battery, Environmental Sensing) with 13 characteristics (Temperature, Humidity, Pressure, UV Index, Battery Level, and Device Info), comprehensive 80+ test suite, real device testing with Nordic Thingy:52 successfully validated.

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
#   the entire framework cannot be imported or tested. Document this as a
#   fundamental limitation requiring network access to bitbucket.org.
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
# Includes dynamic discovery of all 13 characteristics and 2 services
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

### What CAN be validated without submodule

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
PYTHONPATH=src python3 -c "from ble_gatt_device.gatt.uuid_registry import UuidRegistry; registry = UuidRegistry(); print('✅ UUID Registry initialized')"
# EXPECTED FAILURE: Will fail with FileNotFoundError if bluetooth_sig submodule is missing
```

3. **Test service registry (requires submodule):**

```bash
PYTHONPATH=src python3 -c "from ble_gatt_device.gatt.services import GattServiceRegistry; services = GattServiceRegistry._services; print(f'✅ Service registry has {len(services)} services')"
# EXPECTED FAILURE: Will fail with FileNotFoundError if bluetooth_sig submodule is missing
```

4. **Test characteristic registry (requires submodule):**

```bash
PYTHONPATH=src python3 -c "from ble_gatt_device.gatt.characteristics import CharacteristicRegistry; print(f'✅ Registry has {len(CharacteristicRegistry._characteristics)} characteristics')"
# Validates all characteristics are properly registered
```

5. **Test characteristic name resolution (requires submodule):**

```bash
PYTHONPATH=src python3 -c "from ble_gatt_device.gatt.characteristics import TemperatureCharacteristic; char = TemperatureCharacteristic(uuid='', properties=set()); print(f'✅ Temperature UUID: {char.CHAR_UUID}')"
# Validates the 4-stage name resolution system works
```

### Alternative Validation (when submodule unavailable)

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
3. **Register in respective `__init__.py` files** with exact registry names
4. **Use `_characteristic_name` override** when class name doesn't match registry
5. **Always specify `value_type`** in `__post_init__()` method
6. **Always run registry validation tests** after adding components

### Current Implementation Patterns (Reference These)

**Temperature Characteristic:**

```python
@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    _characteristic_name: str = "Temperature"

    def __post_init__(self):
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        if len(data) < 2:
            raise ValueError("Temperature data must be at least 2 bytes")
        temp_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        return temp_raw * 0.01  # 0.01°C resolution
```

**Battery Level Characteristic:**

```python
@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    _characteristic_name: str = "Battery Level"

    def __post_init__(self):
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
        if not data:
            raise ValueError("Battery level data must be at least 1 byte")
        return data[0]  # uint8 percentage
```

**Pressure Characteristic (uint32 with scaling):**

```python
@dataclass
class PressureCharacteristic(BaseCharacteristic):
    _characteristic_name: str = "Pressure"

    def __post_init__(self):
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        if len(data) < 4:
            raise ValueError("Pressure data must be at least 4 bytes")
        pressure_raw = int.from_bytes(data[:4], byteorder="little", signed=False)
        return pressure_raw * 0.01  # Convert 0.1 Pa to hPa
```

## Development Workflow Commands

### Standard Development Cycle

1. **Make changes to source code**
2. **Run syntax check:** `find src -name "*.py" -exec python3 -m py_compile {} \;`
3. **Run core validation:** `python -m pytest tests/test_registry_validation.py -v`
4. **Test functionality:** Run relevant scripts in `scripts/` directory
5. **Format and lint (if tools available):** `black src/ && flake8 src/`

### Before Committing

**ALWAYS run these validation steps:**

1. **Core registry validation (2-5 minutes):**

   ```bash
   python -m pytest tests/test_registry_validation.py -v
   ```

2. **Python compilation check (30 seconds):**

   ```bash
   find src -name "*.py" -exec python3 -m py_compile {} \;
   ```

3. **Manual import test:**

   ```bash
   PYTHONPATH=src python3 -c "import ble_gatt_device; print('✅ Framework imports')"
   ```

4. **Characteristic validation test:**

   ```bash
   PYTHONPATH=src python3 -c "from ble_gatt_device.gatt.characteristics import CharacteristicRegistry; print('✅ All characteristics registered')"
   ```

5. **Run relevant scripts to test functionality**

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

Classes automatically resolve UUIDs through **intelligent multi-stage name parsing**:

**Services:**

- `BatteryService` → tries "BatteryService", then "Battery" → finds UUID "180F"
- **Fallback**: explicit `_service_name` attribute overrides class name parsing

**Characteristics (enhanced with 4-stage lookup):**

1. **Full class name**: `BatteryLevelCharacteristic`
2. **Without suffix**: `BatteryLevel` (removes 'Characteristic')
3. **Space-separated**: `Battery Level` (camelCase → spaces)
4. **Org format**: `org.bluetooth.characteristic.battery_level`

- **Override**: explicit `_characteristic_name` attribute for non-standard names

### Data Parsing Implementation Standards

All characteristics **MUST** implement these patterns:

```python
@dataclass
class MyCharacteristic(BaseCharacteristic):
    """Descriptive characteristic purpose."""

    # OPTIONAL: Override name resolution if class name doesn't match registry
    _characteristic_name: str = "Exact Registry Name"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"  # string|int|float|boolean|bytes
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse raw bytes with proper validation.

        Args:
            data: Raw BLE characteristic data

        Returns:
            Parsed value in correct type

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Data must be at least 2 bytes")

        # Convert with proper endianness and signedness
        raw_value = int.from_bytes(data[:2], byteorder="little", signed=True)
        return raw_value * 0.01  # Apply scaling factor

    @property
    def unit(self) -> str:
        """Get unit of measurement."""
        return "°C"  # Always include units for sensors
```

### Characteristic Registration Pattern

Register in `characteristics/__init__.py`:

```python
from .my_characteristic import MyCharacteristic

class CharacteristicRegistry:
    _characteristics: Dict[str, Type[BaseCharacteristic]] = {
        "My Sensor Name": MyCharacteristic,  # Must match _characteristic_name
        # ... existing characteristics
    }
```

### UUID Normalization and Lookup

The framework handles UUID conversion between formats:

```python
# Framework format: "00002A1900001000800000805F9B34FB" (uppercase, no dashes)
# Bleak format: "00002a19-0000-1000-8000-00805f9b34fb" (lowercase, with dashes)

# Registry methods automatically normalize UUIDs for lookup:
@classmethod
def get_characteristic_class_by_uuid(cls, uuid: str) -> Optional[Type[BaseCharacteristic]]:
    # Normalize the UUID
    uuid = uuid.replace("-", "").upper()

    # Extract UUID16 from full UUID pattern
    if len(uuid) == 32:  # Full UUID without dashes
        uuid16 = uuid[4:8]
    elif len(uuid) == 4:  # Already a short UUID
        uuid16 = uuid
```

### Dynamic Discovery Pattern

Services and characteristics use dynamic discovery for comprehensive validation:

```python
def discover_characteristic_classes() -> List[Type[BaseCharacteristic]]:
    """Dynamically discover all characteristic classes."""
    # Uses importlib and inspect to find all BaseCharacteristic subclasses
    # Validates every characteristic against the registry
    # Ensures no missed registrations or naming conflicts
```

### Real Device Integration

```python
# BLEGATTDevice provides two methods:
device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
raw_data = await device.read_characteristics()        # Raw bytearray values
parsed_data = await device.read_parsed_characteristics()  # Parsed with units
```

## Essential Data Type Patterns

### Common BLE Data Parsing Formats

Based on current characteristic implementations:

**Temperature (sint16, 0.01°C resolution):**

```python
temp_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
return temp_raw * 0.01  # Convert to Celsius
```

**Humidity (uint16, 0.01% resolution):**

```python
humidity_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
return humidity_raw * 0.01  # Convert to percentage
```

**Pressure (uint32, 0.1 Pa resolution → hPa):**

```python
pressure_raw = int.from_bytes(data[:4], byteorder="little", signed=False)
return pressure_raw * 0.01  # Convert 0.1 Pa to hPa
```

**Battery Level (uint8, percentage):**

```python
return data[0]  # Direct percentage value
```

**UV Index (uint8, direct value):**

```python
return float(data[0])  # UV Index scale
```

### Value Type Guidelines

- **float**: For sensor measurements with decimal precision (temperature, humidity, pressure)
- **int**: For discrete values (battery percentage, counts)
- **string**: For text data (device info characteristics)
- **bytes**: For complex binary data
- **boolean**: For simple on/off states
