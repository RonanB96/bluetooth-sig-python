---
applyTo: "**/tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Testing Requirements

## Characteristic Test Pattern

Inherit from `CommonCharacteristicTests` (in `tests/gatt/characteristics/test_characteristic_common.py`). It provides standard tests automatically — you only override three fixtures:

```python
class TestFooCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> FooCharacteristic:
        return FooCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AXX"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x42]), 66, "example value"),
        ]
```

For characteristics with dependencies, also override `dependency_test_data` returning `list[DependencyTestData]`.

## Coverage Policy

Every new function: success + 2 failure cases minimum.

## Required Edge Cases

- Empty: `bytearray([])`
- Boundaries: min, max, just outside
- Sentinels if applicable for the characteristic

## Commands

```bash
python -m pytest tests/ -v                                   # All
python -m pytest -k "battery" -v                             # Filter
python -m pytest --lf                                        # Last failed
python -m pytest tests/ --cov=bluetooth_sig --cov-fail-under=85
```

Tests must be deterministic.
