---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt,**/setup.py"
---

# Python Implementation Guidelines

## CRITICAL MUST READ - Prohibited Practices

- Hardcoded UUIDs (use registry resolution)
- Conditional imports for core logic
- Use of TYPE_CHECKING
- Non top-level or lazy imports
- rexporting outside of the module where defined
- Untyped public function signatures
- Using hasattr or getattr when direct attribute access is possible
- Silent exception pass / bare `except:`
- Returning unstructured `dict` / `tuple` when a msgspec.Struct fits
- Magic numbers without an inline named constant or spec citation
- Parsing without pre-validating length

## Type Safety (ABSOLUTE REQUIREMENT)

**Every function MUST have complete, explicit type hints.**

- ❌ **FORBIDDEN**: `def parse(data)` or `def get_value(self)`
- ✅ **REQUIRED**: `def parse(data: bytes) -> BatteryLevelData` and `def get_value(self) -> int | None`
- Return types are MANDATORY - no implicit returns
- Use modern union syntax: `Type | None` not `Optional[Type]`. Use `from __future__ import annotations` for forward refs.
- Use msgspec.Struct for structured data - NEVER return raw `dict` or `tuple`
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

**Use msgspect.struct for structured data:**
- Mutable only if justified with inline comment
- Use `int`, `float`, `Decimal`, `Enum`, or purpose-specific structs
- NO raw `dict` or `tuple` returns from public functions
- Optional fields: `Type | None` not `Optional[Type]`
- Include docstrings with physical units where applicable

**Example:**
```python
from msgspec import Struct

class TemperatureData(Struct):
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

## Docstrings & in-code documentation

Docstrings are the authoritative in-code documentation for this project. Because every public Python symbol in this repository must be fully typed and documented, docstrings should focus on semantics, units, expected ranges, sentinel values and error modes rather than repeating type annotations.

- PEP 257 basics: always use triple double quotes ("""), start with a one-line imperative summary (<=80 chars preferred) followed by a blank line and an extended description when needed.
- Preferred style: Google style for all public API docstrings (Args, Returns, Raises, Examples). NumPy style may be used only for highly numerical modules after explicit justification.
- Content expectations for public APIs:
  - Summary: what the function/class does (imperative sentence).
  - Parameters: describe semantics, units, valid ranges, special sentinel values (do not duplicate type information that already appears in the function signature).
  - Returns/Yields: describe the returned value(s), units, rounding/resolution, and sentinel mapping (e.g., 0xFFFF → None).
  - Raises: list the exceptions that will be raised and the conditions that cause them.
  - Examples: provide short, copy/paste runnable examples in doctest format where practical; include assertions or expected output so readers can self-verify.
  - Attributes (for msgspec.Struct): include an Attributes section with physical units and any invariants or constraints.

- Semantics vs. types: because this project mandates PEP 484 type hints for all public functions and methods, docstrings SHOULD NOT repeat the type annotations except when doing so improves readability (for example when documenting returned structured msgspec.Struct or complex union types). If a type is repeated in a docstring, it MUST match the source annotation exactly.

 - Tooling and enforcement:
    - Use `pydocstyle` for enforcing docstring presence and high-level conventions (PEP 257) during CI and local checks. Configure `pydocstyle` rules in `pyproject.toml` or `setup.cfg` as project policy evolves.
    - Make Google style the canonical style. When rendering documentation with sphinx, configure the handler to parse Google-style docstrings so generated API docs are consistent. If using Sphinx, enable `sphinx.ext.napoleon` and set:

        ```py
        napoleon_google_docstring = True
        napoleon_numpy_docstring = False
        ```

    - Include doctest examples as part of the test suite where reasonable (pytest's `--doctest-glob` or `--doctest-modules`) so examples stay correct.

Example (Google style):

```python
def decode_battery_level(data: bytearray) -> int:
    """Decode the Battery Level characteristic.

    The battery level is encoded in the first byte and ranges from 0 to 100
    representing percent charge. A value of ``0xFF`` indicates "unknown" and
    should be handled by callers or converted to ``None`` by a higher-level
    adapter where appropriate.

    Args:
        data: Raw bytes containing the battery level; the first byte holds
            the battery percentage.

    Returns:
        int: Battery percentage (0-100).

    Raises:
        InsufficientDataError: If ``data`` is shorter than 1 byte.

    Examples:
        >>> decode_battery_level(bytearray([100]))
        100
    """
    if len(data) < 1:
        raise InsufficientDataError("Battery Level characteristic requires 1 byte")
    return int(data[0])
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
    # NOTE: Duplicates AdvertisingPDUParser for backwards compatibility.
    # TODO: Refactor to delegate to AdvertisingPDUParser instead.
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
from datetime import datetime
from typing import Any

# Third-party (if any)
import pyyaml

# Local application
from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types import CharacteristicContext
from .base import BaseCharacteristic
```

## Quality Gates

**Before claiming completion:**
```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```
