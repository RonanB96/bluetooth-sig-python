# AI Coding Agent Instructions for Bluetooth SIG Standards Library

## CRITICAL: Research and Documentation Requirements (RTFD!)

**BEFORE starting any work:**
1. **ALWAYS review relevant online documentation** for the specific technologies, libraries, frameworks, and APIs you are working with
2. **REFERENCE official documentation sources**:
   - **Bluetooth SIG specifications**: https://www.bluetooth.com/specifications/assigned-numbers/ for BLE characteristics and services
   - **Python documentation**: https://docs.python.org/ for language features, standard library, and best practices
   - **Library-specific docs**: Official documentation for any Python packages, dependencies, or frameworks being used
3. **VERIFY current standards and syntax** - specifications, APIs, and language features are updated regularly
4. **ONLY AFTER** reviewing official documentation, then reference these instructions and use search/bash commands for specific implementation details

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

**bluetooth-sig-python** is a **pure Bluetooth SIG standards library** for parsing characteristic and service data according to official specifications. This is NOT a device integration library - it's a reference implementation for translating raw BLE data using SIG standards.

## 🚨 MANDATORY QUALITY REQUIREMENTS

**CRITICAL: Run these commands in sequence BEFORE every commit:**

```bash
./scripts/format.sh --fix         # Fix all formatting issues
./scripts/format.sh --check       # Verify formatting is correct
./scripts/lint.sh --all           # Run ALL linting (ruff + pylint 10.00/10)
python -m pytest tests/ -v        # Run ALL tests
```

**For stubborn formatting issues, use unsafe fixes:**
```bash
./scripts/format.sh --fix-unsafe  # Fix including unsafe ruff fixes
```

**🛑 ALL commands must pass with ZERO issues before creating commits or PRs.**

## Project Architecture

### Core Purpose: Pure SIG Standards Translation

**CRITICAL**: This project requires the `bluetooth_sig/` submodule containing official Bluetooth SIG YAML files:
```bash
git submodule init && git submodule update
```

### Registry-Driven UUID Resolution (Core Innovation)

Classes automatically resolve UUIDs through **intelligent multi-stage name parsing**:

**Services** (tries multiple formats):
- `BatteryService` → "BatteryService", "Battery", "org.bluetooth.service.battery_service" → finds UUID "180F"
- Override with `_service_name` attribute when needed

**Characteristics** (4-stage lookup):
1. Full class name: `BatteryLevelCharacteristic`
2. Without suffix: `BatteryLevel` (removes 'Characteristic')
3. Space-separated: `Battery Level` (camelCase → spaces)
4. Org format: `org.bluetooth.characteristic.battery_level`
- Override with `_characteristic_name` attribute for non-standard names

### Type-Safe Modern API (Python 3.9+)

Uses `from __future__ import annotations` for modern union syntax:

```python
@dataclass
class ParsedData(CharacteristicInfo):
    """Rich parsing result with type safety."""
    value: Any | None = None           # Parsed value with proper type
    unit: str | None = None            # "%", "°C", "hPa", etc.
    raw_data: bytes | None = None      # Original raw bytes
    parse_success: bool = True         # Parse success indicator
    error_message: str | None = None   # Error details if failed
```

## Development Workflow

### Virtual Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac - Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Essential Commands
```bash
# Initialize Bluetooth SIG submodule (BLOCKING REQUIREMENT):
git submodule init && git submodule update

# Verify framework functionality:
python -c "import bluetooth_sig; print('✅ Framework ready')"

# Test registry loading:
python -m pytest tests/test_uuid_registry.py -v
```

## Implementation Patterns

### Standard Characteristic Pattern

ALL characteristics MUST follow this exact pattern:

```python
from __future__ import annotations
from dataclasses import dataclass
from .base import BaseCharacteristic

@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature measurement per SIG spec."""

    def __post_init__(self):
        self.value_type = "float"  # string|int|float|boolean|bytes
        super().__post_init__()

    def decode_value(self, data: bytearray) -> float:
        """Parse raw bytes with proper validation."""
        if len(data) < 2:
            raise ValueError("Temperature data must be at least 2 bytes")
        raw_value = int.from_bytes(data[:2], byteorder="little", signed=True)
        return raw_value * 0.01  # Apply SIG scaling factor

    @property
    def unit(self) -> str:
        return "°C"
```

### Registry Registration Pattern

Register in `characteristics/__init__.py`:
```python
from .temperature import TemperatureCharacteristic

class CharacteristicRegistry:
    _characteristics: dict[str, type[BaseCharacteristic]] = {
        "Temperature": TemperatureCharacteristic,  # Must match SIG name
        # ... existing characteristics
    }
```

## Testing & Quality

### Core Validation (Run these commands in sequence)
```bash
./scripts/format.sh --fix         # Fix formatting
./scripts/format.sh --check       # Verify formatting
./scripts/lint.sh --all           # Full linting
python -m pytest tests/ -v        # All tests
```

**For stubborn issues:**
```bash
./scripts/format.sh --fix-unsafe  # Use ruff unsafe fixes if needed
```## Key Architecture Files

**Core API**: `src/bluetooth_sig/core.py` - BluetoothSIGTranslator with dataclass returns
**UUID Registry**: `src/bluetooth_sig/gatt/uuid_registry.py` - Multi-stage name resolution
**Characteristic Base**: `src/bluetooth_sig/gatt/characteristics/base.py` - Standard patterns
**Registry Tests**: `tests/test_registry_validation.py` - Comprehensive validation
**SIG Data**: `bluetooth_sig/assigned_numbers/uuids/*.yaml` - Official specifications

## Common Data Parsing Standards

Based on SIG specifications:
- **Temperature**: sint16, 0.01°C resolution, little endian
- **Humidity**: uint16, 0.01% resolution, little endian
- **Pressure**: uint32, 0.1 Pa resolution → convert to hPa
- **Battery**: uint8, direct percentage value

## Critical Success Factors

1. **Submodule Dependency**: `bluetooth_sig/` must be initialized
2. **Quality Standards**: Run format --fix, --check, lint --all, pytest -v in sequence
3. **Registry Validation**: All tests must pass
4. **Type Safety**: Use modern `Class | None` union syntax
5. **SIG Compliance**: Follow official Bluetooth specifications exactly

## Framework-Agnostic Integration Pattern

**CRITICAL**: This library works with ANY BLE connection library. The integration pattern is:

```python
# Step 1: Get raw data (using ANY BLE library)
raw_data = await your_ble_library.read_characteristic(device, uuid)

# Step 2: Parse with bluetooth_sig (connection-agnostic)
from bluetooth_sig import BluetoothSIGTranslator
translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(uuid, raw_data)

# Step 3: Use parsed result
print(f"Value: {result.value} {result.unit}")
```

**Supported BLE Libraries**: bleak, bleak-retry-connector, simplepyble, or any custom BLE implementation.

## Template System for Common Patterns

Use templates in `characteristics/templates.py` for common characteristic types:

```python
# For simple uint8 characteristics (battery level, etc.)
@dataclass
class SimpleUint8Characteristic(BaseCharacteristic):
    expected_length: int = 1
    min_value: int = 0
    max_value: int = 255
    expected_type: type = int
```

## Validation Attributes Pattern

Use declarative validation in characteristic classes:

```python
@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level with validation constraints."""

    # Declarative validation (automatically enforced)
    expected_length: int = 1
    min_value: int = 0
    max_value: int = 100
    expected_type: type = int

    def decode_value(self, data: bytearray) -> int:
        return data[0]  # Validation happens automatically
```

## Error Handling Patterns

**Use specific ValueError messages** that reference the characteristic:

```python
def decode_value(self, data: bytearray) -> float:
    if len(data) < 2:
        raise ValueError("Temperature data must be at least 2 bytes")
    # ... parsing logic
```

**Handle SIG special values** appropriately:
- `0x07FF`: Positive infinity
- `0x0800`: Negative infinity
- `0x07FE`: NaN (Not a Number)

## Import Organization

**Always follow this import order:**
1. `from __future__ import annotations` (first line after docstring)
2. Standard library imports
3. Third-party imports
4. Local imports (relative imports)

**Example:**
```python
"""Module docstring."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic
from .utils import IEEE11073Parser
```
