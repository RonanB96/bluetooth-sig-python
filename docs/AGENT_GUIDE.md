
# AGENT GUIDE: Bluetooth SIG Standards Library

This guide is for both human contributors and AI agents working on the Bluetooth SIG standards translation library. It covers implementation patterns, templates, rationale, and agent-specific behaviour. Follow best practices for Python library documentation and PyPI standards.

---

## Agent Behaviour and Workflow

This section is for AI agents and automation:

- Always consult official documentation before coding or refactoring.
- Validate input, output, and error handling against SIG specs.
- Proactively check for duplication, unclear instructions, and broken references.
- Communicate in concise, technical, iterative updates (see memory file).
- If documentation is missing, escalate and flag for human review.
- Run format, lint, and tests before claiming any solution works.
- Never hardcode UUIDs; use registry-driven resolution.
- Raise clear, specific errors and add/maintain tests for all new features.

References for agents:

- See `.github/instructions/memory.instruction.md` for agent memory and preferences.
- See `.github/copilot-instructions.md` for agent checklist.
- [Bluetooth SIG assigned numbers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [Python documentation](https://docs.python.org/)

---

## Table of Contents (Human Coding Guide)

1. [Development Workflow](#development-workflow)
2. [Implementation Patterns](#implementation-patterns)
3. [Registry Registration](#registry-registration)
4. [Testing & Quality](#testing--quality)
5. [Common Data Parsing Standards](#common-data-parsing-standards)
6. [Critical Success Factors](#critical-success-factors)
7. [Framework-Agnostic Integration](#framework-agnostic-integration)
8. [Template System](#template-system)
9. [Validation Attributes](#validation-attributes)
10. [Error Handling](#error-handling)
11. [Import Organization](#import-organization)

---

---

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

---

---

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

---

---

## Registry Registration

Register in `characteristics/__init__.py`:

```python
from .temperature import TemperatureCharacteristic

class CharacteristicRegistry:
    _characteristics: dict[str, type[BaseCharacteristic]] = {
        "Temperature": TemperatureCharacteristic,  # Must match SIG name
        # ... existing characteristics
    }
```

---

---

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
```

---

---

## Common Data Parsing Standards

Based on SIG specifications:

- **Temperature**: sint16, 0.01°C resolution, little endian
- **Humidity**: uint16, 0.01% resolution, little endian
- **Pressure**: uint32, 0.1 Pa resolution → convert to hPa
- **Battery**: uint8, direct percentage value

---

---

## Critical Success Factors

1. **Submodule Dependency**: `bluetooth_sig/` must be initialized
2. **Quality Standards**: Run format --fix, --check, lint --all, pytest -v in sequence
3. **Registry Validation**: All tests must pass
4. **Type Safety**: Use modern `Class | None` union syntax
5. **SIG Compliance**: Follow official Bluetooth specifications exactly

---

---

## Framework-Agnostic Integration

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

**Supported BLE Libraries**: bleak-retry-connector, simplepyble, or any custom BLE implementation.

---

---

## Template System

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

---

---

## Validation Attributes

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

---

---

## Error Handling

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

---

---

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
