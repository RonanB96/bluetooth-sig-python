---
applyTo: "**/tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Testing Requirements

## Policy (MANDATORY)

Every new function needs: success + 2 failure cases minimum.

## Required Test Cases

1. Parsing success
2. Length violation (too short, empty)
3. Range violation
4. Registry resolution
5. Encoding roundtrip

## Edge Cases

- Empty: `bytearray([])`
- Boundaries: min, max, just outside
- Sentinels: 0xFF, 0xFFFF, 0x8000

## Commands

```bash
python -m pytest tests/ -v
python -m pytest -k "battery" -v
python -m pytest --lf
```

Tests must be deterministic. See `tests/gatt/` for patterns.
