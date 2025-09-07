# AI Coding Agent Instructions for Bluetooth SIG Standards Library

**bluetooth-sig-python** is a **pure Bluetooth SIG standards library** for parsing characteristic and service data according to official specifications. This is NOT a device integration library - it's a reference implementation for translating raw BLE data using SIG standards.

## 🚨 MANDATORY QUALITY REQUIREMENTS

**CRITICAL: Run these commands BEFORE every commit:**

```bash
./scripts/format.sh --fix         # Fix all formatting issues
./scripts/format.sh --check       # Verify formatting is correct
./scripts/lint.sh --all           # Run ALL linting (ruff + pylint 10.00/10)
python -m pytest tests/ -v        # Run ALL tests
```

**🛑 STOP: Do NOT create commits or PRs until ALL commands pass with ZERO issues.**
**🛑 STOP: Do NOT submit pull requests with failing CI checks.**
**🛑 STOP: Always run quality validation BEFORE pushing changes.**

**Individual debugging commands:**
```bash
./scripts/lint.sh --ruff          # Python style checking only
./scripts/lint.sh --pylint        # Python code analysis only
./scripts/format.sh --ruff        # Python code formatting only
```

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

### Core Validation Tests (NEVER skip these)
```bash
# Registry validation:
python -m pytest tests/test_registry_validation.py -v

# UUID registry functionality:
python -m pytest tests/test_uuid_registry.py -v

# Name resolution patterns:
python -m pytest tests/test_name_resolution.py -v
```

### Manual Framework Validation
```bash
# Test core import:
python -c "import bluetooth_sig; print('✅ Import successful')"

# Test registry loading:
python -c "from bluetooth_sig.gatt.uuid_registry import uuid_registry; print(f'✅ Registry loaded with {len(uuid_registry._characteristics)} characteristics')"

# Test characteristic creation:
python -c "from bluetooth_sig.gatt.characteristics import CharacteristicRegistry; char = CharacteristicRegistry.create_characteristic('2A19', set()); print(f'✅ Created: {char.__class__.__name__}')"
```

## Key Architecture Files

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
2. **Quality Standards**: Pylint 10.00/10, zero ruff violations
3. **Registry Validation**: All 128+ tests must pass
4. **Type Safety**: Use modern `Class | None` union syntax
5. **SIG Compliance**: Follow official Bluetooth specifications exactly
