# Testing Guide

## Running Tests

```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=src/bluetooth_sig --cov-report=term-missing
python -m pytest tests/ -k "battery" -v
```

## Writing Characteristic Tests

All characteristic tests inherit from `CommonCharacteristicTests` in
`tests/gatt/characteristics/test_characteristic_common.py`. The base class
automatically runs UUID verification, parse/decode consistency, length
validation, edge-case handling, and round-trip encode/decode against every
entry in `valid_test_data`.

### Required fixtures

| Fixture | What to return |
|---|---|
| `characteristic` | A fresh instance of the characteristic under test |
| `expected_uuid` | The short UUID string, e.g. `"2A19"` |
| `valid_test_data` | A `list[CharacteristicTestData]` covering every meaningful input variant |

```python
import pytest

from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBatteryLevelCharacteristic(CommonCharacteristicTests):

    @pytest.fixture
    def characteristic(self) -> BatteryLevelCharacteristic:
        return BatteryLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A19"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0]), 0, "empty battery"),
            CharacteristicTestData(bytearray([75]), 75, "75% battery"),
            CharacteristicTestData(bytearray([100]), 100, "full battery"),
        ]
```

### What the base class tests automatically

Every `valid_test_data` entry is exercised by:

- `test_characteristic_uuid_matches_expected`
- `test_parse_valid_data_succeeds` and `test_decode_valid_data_returns_expected_value`
- `test_round_trip` — `parse_value → build_value` must reproduce the original bytes
- `test_empty_data_handling`, `test_undersized_data_handling`, `test_oversized_data_validation`
- `test_length_validation_behaviour`, `test_range_validation_behaviour`
- `test_parse_decode_consistency`, `test_decode_exception_handling`
- `test_uuid_resolution_behaviour`
- Dependency coverage enforcement (see below)

### When to add explicit test methods

Only add a method when it tests something `valid_test_data` cannot express:

- **Structural byte assertions** — checking a specific offset or flag bit in the encoded output.
- **Error conditions** — inputs that must raise an exception.
- **Dependency scenarios** — use the `dependency_test_data` fixture (see below).

**Do not** add separate encode or round-trip methods — those are covered automatically.

### Dependencies

If the characteristic declares `required_dependencies` or `optional_dependencies`,
the base class enforces a `dependency_test_data` fixture. See
`test_characteristic_common.py` for the `DependencyTestData` structure and
`tests/gatt/characteristics/test_characteristic_dependencies.py` for examples.

## Test Structure

```text
tests/
├── conftest.py
├── gatt/
│   └── characteristics/
│       ├── test_characteristic_common.py   ← base class and shared helpers
│       ├── test_characteristic_dependencies.py
│       └── test_<characteristic_name>.py   ← one file per characteristic
├── advertising/
├── core/
├── registry/
├── integration/
└── ...
```

## Continuous Integration

```yaml
- name: Run tests
  run: pytest tests/ --cov=src/bluetooth_sig --cov-report=xml
```

See `.github/workflows/` for the full CI configuration.

## Next Steps

- [Contributing Guide](contributing.md)
- [API Reference](../api/index.md)

