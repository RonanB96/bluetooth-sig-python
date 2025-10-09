---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt,**/setup.py"
---

# Python Implementation Guidelines

## Type Safety (ABSOLUTE REQUIREMENT)

**Every public function MUST have complete, explicit type hints.**

- ❌ **FORBIDDEN**: `def parse(data)` or `def get_value(self)`
- ✅ **REQUIRED**: `def parse(data: bytes) -> BatteryLevelData` and `def get_value(self) -> int | None`
- Return types are MANDATORY - no implicit returns
- Use modern union syntax: `Type | None` not `Optional[Type]`
- Use dataclasses for structured data - NEVER return raw `dict` or `tuple`
- `Any` type requires inline justification comment explaining why typing is impossible
- No gradual typing - all parameters and returns must be typed from the start

**Example - CORRECT:**
```python
def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
    """Decode temperature characteristic.

    Args:
        data: Raw bytes from BLE characteristic
        ctx: Optional context for parsing (device info, flags, etc.)

    Returns:
        Decoded temperature value in °C
    """
    if len(data) < 2:
        raise InsufficientDataError("Temperature data must be at least 2 bytes")
    raw_value = int.from_bytes(data[:2], byteorder="little", signed=True)
    return raw_value * 0.01
```

**Example - WRONG:**
```python
def decode_value(self, data, ctx=None):  # ❌ No types!
    """Decode temperature characteristic."""
    ...
```

## Data Modeling Standards

**Use dataclasses for structured data:**
- `@dataclass(slots=True, frozen=True)` where immutability fits
- Mutable only if justified with inline comment
- Use `int`, `float`, `Decimal`, `Enum`, or purpose-specific dataclasses
- NO raw `dict` or `tuple` returns from public functions
- Optional fields: `Type | None` not `Optional[Type]`
- Include docstrings with physical units where applicable

**Example:**
```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class TemperatureData:
    """Temperature measurement from BLE characteristic.

    Attributes:
        value: Temperature in °C (resolution: 0.01°C)
        unit: Always "°C" for this characteristic
        timestamp: Optional measurement timestamp
    """
    value: float
    unit: str = "°C"
    timestamp: datetime | None = None
```

## Code Duplication Policy

**NEVER disable duplicate-code warnings for entire files.**

- ❌ **FORBIDDEN**: Adding `# pylint: disable=duplicate-code` at module level (top of file)
- ✅ **REQUIRED**: Add disable comments ONLY at the specific function/method/block where duplication exists
- ✅ **REQUIRED**: Every disable comment MUST include:
  1. **NOTE**: Clear explanation of WHY the duplication exists
  2. **Justification**: Why consolidation is not practical/possible
  3. **TODO**: Future refactoring action item (if applicable)

**Example - CORRECT:**
```python
def _parse_legacy_advertising(self, raw_data: bytes) -> None:
    # pylint: disable=duplicate-code
    # NOTE: Duplicates AdvertisingParser for backwards compatibility.
    # TODO: Refactor to delegate to AdvertisingParser instead.
    # Duplication exists because Device has legacy inline parsing.
    ...actual duplicated code...
```

## Error Handling

**Raise precise custom exceptions:**
- Never swallow exceptions silently
- Rewrap with context if necessary
- Reference characteristic name and offending condition
- Bounds/length checks precede buffer slicing
- Reject malformed binary inputs early and clearly

**Example:**
```python
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError

def decode_value(self, data: bytearray) -> int:
    """Decode battery level (0-100%)."""
    if len(data) < 1:
        raise InsufficientDataError(
            "Battery Level characteristic requires exactly 1 byte, "
            f"got {len(data)} bytes"
        )

    value = int(data[0])
    if not 0 <= value <= 100:
        raise ValueRangeError(
            f"Battery level must be 0-100%, got {value}%"
        )

    return value
```

## Parsing & Validation Rules

For each characteristic:
- Validate payload length exactly (or declared variable length constraints) before decoding
- Enforce numeric domain (min/max) per spec
- Handle special sentinel values (e.g., 0xFFFF meaning "unknown") mapping to `None`
- Multi-field bit parsing must use named bit field abstractions; avoid manual magic masks inline
- Endianness explicit (`little` vs `big`) - never rely on default assumptions

**Example:**
```python
def decode_value(self, data: bytearray) -> float | None:
    """Decode humidity with special value handling."""
    if len(data) != 2:
        raise InsufficientDataError(f"Humidity requires 2 bytes, got {len(data)}")

    raw_value = int.from_bytes(data, byteorder="little", signed=False)

    # Handle special sentinel value
    if raw_value == 0xFFFF:
        return None  # "Unknown" or "Not available"

    # Normal range: 0-10000 (0.00% to 100.00%)
    if raw_value > 10000:
        raise ValueRangeError(f"Humidity value {raw_value} exceeds maximum 10000")

    return raw_value * 0.01  # Convert to percentage
```

## Import Organization

**Standard order:**
```python
"""Module docstring."""

from __future__ import annotations  # Always first for postponed annotations

# Standard library
import struct
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Third-party (if any)
import pyyaml

# Local application
from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types import CharacteristicContext
from .base import BaseCharacteristic
```

## Prohibited Practices

- Hardcoded UUIDs (use registry resolution)
- Conditional imports for core logic
- Untyped public function signatures
- Silent exception pass / bare `except:`
- Returning unstructured `dict` / `tuple` when a dataclass fits
- Magic numbers without an inline named constant or spec citation
- Parsing without pre-validating length

## Quality Gates

**Before claiming completion:**
```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```
