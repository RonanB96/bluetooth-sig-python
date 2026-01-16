---
applyTo: "**/tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Testing Requirements

## Policy (MANDATORY)

- Every new function/method needs tests
- Minimum: success case + 2 failure cases
- Run full test suite before completion: `python -m pytest tests/ -v`

## Required Test Cases

Each characteristic/service MUST include:
1. **Parsing success** - Canonical example from spec
2. **Length violation** - Too short, too long, empty
3. **Range violation** - Out of range or reserved value
4. **Registry resolution** - Name-to-UUID works
5. **Encoding roundtrip** - `build_value(parse_value(data)) == data`

## Edge Cases to Always Test

- Empty payload: `bytearray([])`
- Boundary values: min valid, max valid, just outside
- Special sentinels: 0xFF, 0xFFFF, 0x8000
- Variable length: if `allow_variable_length=True`

## Test Organisation

```
tests/
├── conftest.py           # Shared fixtures
├── gatt/
│   ├── test_battery_level.py
│   └── test_heart_rate.py
├── registry/
└── core/
```

## Fixtures

Use `conftest.py` for shared fixtures. Keep test data minimal and inline.

## Parametrised Tests

Use `@pytest.mark.parametrize` for multiple similar cases instead of separate test methods.

## Assertions

Be specific:
- ❌ `assert result`
- ✅ `assert result == 75`
- ✅ `assert isinstance(result, int)`

## Commands

```bash
python -m pytest tests/ -v              # All tests
python -m pytest tests/gatt/ -v         # Specific folder
python -m pytest -k "battery" -v        # Pattern match
python -m pytest --lf                   # Last failed only
pytest --cov=src/bluetooth_sig          # With coverage
```

## Determinism

All tests must be deterministic:
- No live device dependencies (mark and skip if needed)
- No network calls
- Mock external dependencies, not core logic

## Reference

See existing tests in `tests/gatt/` for patterns.
