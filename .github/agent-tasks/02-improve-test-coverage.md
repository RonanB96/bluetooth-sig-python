# Task 02: Improve Test Coverage

**Priority**: P1 (High Priority)
**Estimated Effort**: Medium (3-5 days)
**Dependencies**: None (but should include Task 01 when complete)
**Target Release**: v0.4.0

## Objective

Increase test coverage from 86% to >90% by addressing identified gaps, with focus on edge cases and error handling.

## Current State

**Overall Coverage**: 86% (2514 tests passing)

**Critical Gaps Identified**:
- `src/bluetooth_sig/utils/rssi_utils.py`: **15% coverage** ⚠️ Critical
- `src/bluetooth_sig/types/gatt_services.py`: 83% coverage
- `src/bluetooth_sig/types/uuid.py`: 80% coverage
- `src/bluetooth_sig/types/descriptor_types.py`: 90% coverage

## Success Criteria

- [ ] Overall coverage ≥90%
- [ ] `rssi_utils.py` coverage ≥80%
- [ ] `gatt_services.py` coverage ≥90%
- [ ] `uuid.py` coverage ≥90%
- [ ] All critical paths have error handling tests
- [ ] Edge cases covered for UUID parsing
- [ ] No test files with <80% coverage

## Implementation Plan

### Phase 1: RSSI Utilities (Critical - 15% → 80%)

**File**: `src/bluetooth_sig/utils/rssi_utils.py`

**Current Missing Tests**:
- RSSI distance calculation edge cases
- Signal strength classification
- Invalid RSSI values handling
- Mathematical edge cases (very weak signals, interference)

**Test Plan**:

```python
# tests/utils/test_rssi_utils.py (new or expand existing)

import pytest
from bluetooth_sig.utils.rssi_utils import (
    rssi_to_distance,
    classify_signal_strength,
    validate_rssi,
)

class TestRSSIToDistance:
    """Test RSSI to distance conversion."""

    def test_typical_rssi_values(self):
        """Test with typical RSSI values."""
        # Very close: -30 dBm
        assert rssi_to_distance(-30) < 1.0

        # Medium: -70 dBm
        distance = rssi_to_distance(-70)
        assert 5.0 < distance < 15.0

        # Far: -90 dBm
        assert rssi_to_distance(-90) > 20.0

    def test_edge_case_very_strong_signal(self):
        """Test with unrealistically strong signal."""
        # -10 dBm is very strong, almost touching
        distance = rssi_to_distance(-10)
        assert distance >= 0.0
        assert distance < 0.5

    def test_edge_case_very_weak_signal(self):
        """Test with very weak signal."""
        # -100 dBm is at the limit of detectability
        distance = rssi_to_distance(-100)
        assert distance > 50.0

    def test_invalid_positive_rssi(self):
        """Test that positive RSSI values are handled."""
        with pytest.raises(ValueError, match="RSSI cannot be positive"):
            rssi_to_distance(10)

    def test_invalid_zero_rssi(self):
        """Test zero RSSI."""
        with pytest.raises(ValueError, match="RSSI cannot be zero"):
            rssi_to_distance(0)

    def test_boundary_conditions(self):
        """Test mathematical boundary conditions."""
        # Test that formula doesn't produce NaN or infinity
        for rssi in range(-100, -10):
            distance = rssi_to_distance(rssi)
            assert not math.isnan(distance)
            assert not math.isinf(distance)
            assert distance > 0

class TestSignalStrengthClassification:
    """Test signal strength classification."""

    @pytest.mark.parametrize("rssi,expected", [
        (-30, "excellent"),
        (-50, "good"),
        (-70, "fair"),
        (-90, "poor"),
        (-100, "very_poor"),
    ])
    def test_classification(self, rssi, expected):
        """Test signal strength classification."""
        assert classify_signal_strength(rssi) == expected

    def test_classification_boundaries(self):
        """Test boundary values between classifications."""
        # Test around typical thresholds
        assert classify_signal_strength(-59) == "good"
        assert classify_signal_strength(-60) == "fair"

class TestValidateRSSI:
    """Test RSSI validation."""

    def test_valid_rssi_range(self):
        """Test valid RSSI values."""
        for rssi in range(-100, 0):
            assert validate_rssi(rssi) is True

    def test_invalid_positive(self):
        """Test that positive values are invalid."""
        assert validate_rssi(10) is False

    def test_invalid_too_weak(self):
        """Test values beyond detection limit."""
        assert validate_rssi(-120) is False

    def test_boundary_values(self):
        """Test boundary conditions."""
        assert validate_rssi(-100) is True   # Weakest valid
        assert validate_rssi(-1) is True     # Strongest valid
        assert validate_rssi(0) is False     # Invalid
        assert validate_rssi(-101) is False  # Too weak
```

### Phase 2: UUID Utilities (80% → 90%)

**File**: `src/bluetooth_sig/types/uuid.py`

**Missing Coverage**:
- Edge cases in UUID normalization
- Invalid UUID format handling
- UUID comparison edge cases
- Short/long form conversion edge cases

**Test Plan**:

```python
# tests/types/test_uuid.py (expand existing)

class TestBluetoothUUID:
    """Test Bluetooth UUID class edge cases."""

    def test_invalid_uuid_formats(self):
        """Test various invalid UUID formats."""
        invalid_uuids = [
            "ZZZZ",              # Invalid hex
            "12345",             # Wrong length
            "1234-5678",         # Wrong format
            "",                  # Empty string
            "not-a-uuid",        # Invalid format
        ]

        for invalid in invalid_uuids:
            with pytest.raises(ValueError):
                BluetoothUUID(invalid)

    def test_uuid_normalization_edge_cases(self):
        """Test UUID normalization with edge cases."""
        # Mixed case
        uuid1 = BluetoothUUID("180f")
        uuid2 = BluetoothUUID("180F")
        assert str(uuid1) == str(uuid2)

        # With dashes in different positions
        uuid3 = BluetoothUUID("0000-180f-0000-1000-8000-00805f9b34fb")
        assert uuid3.short == "180F"

    def test_uuid_comparison_edge_cases(self):
        """Test UUID comparison with different formats."""
        short = BluetoothUUID("180F")
        long = BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb")

        assert short == long
        assert not (short != long)

    def test_uuid_hash_consistency(self):
        """Test that equal UUIDs have equal hashes."""
        uuid1 = BluetoothUUID("180F")
        uuid2 = BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb")

        assert hash(uuid1) == hash(uuid2)

        # Can be used in sets/dicts
        uuid_set = {uuid1, uuid2}
        assert len(uuid_set) == 1

    def test_custom_uuid_128bit(self):
        """Test custom 128-bit UUIDs."""
        custom = BluetoothUUID("12345678-1234-5678-1234-567812345678")
        assert custom.is_custom
        assert len(str(custom)) == 36

    def test_sig_base_uuid_detection(self):
        """Test SIG base UUID detection."""
        sig_uuid = BluetoothUUID("180F")
        custom_uuid = BluetoothUUID("12345678-1234-5678-1234-567812345678")

        assert not sig_uuid.is_custom
        assert custom_uuid.is_custom
```

### Phase 3: GATT Services (83% → 90%)

**File**: `src/bluetooth_sig/types/gatt_services.py`

**Missing Coverage**:
- Service validation edge cases
- Service comparison operations
- Error handling for malformed service data

**Test Plan**:

```python
# tests/types/test_gatt_services.py (expand existing)

class TestServiceInfo:
    """Test ServiceInfo edge cases."""

    def test_service_with_empty_characteristics(self):
        """Test service with no characteristics."""
        service = ServiceInfo(
            uuid=BluetoothUUID("180F"),
            name="Battery Service",
            characteristics=[]
        )
        assert len(service.characteristics) == 0

    def test_service_with_many_characteristics(self):
        """Test service with many characteristics."""
        chars = [
            CharacteristicInfo(
                uuid=BluetoothUUID(f"2A{i:02X}"),
                name=f"Char {i}",
                value_type=ValueType.UINT8,
                unit="",
                properties=[]
            )
            for i in range(100)
        ]

        service = ServiceInfo(
            uuid=BluetoothUUID("180F"),
            name="Test Service",
            characteristics=chars
        )

        assert len(service.characteristics) == 100

    def test_service_info_equality(self):
        """Test ServiceInfo equality comparison."""
        service1 = ServiceInfo(
            uuid=BluetoothUUID("180F"),
            name="Battery Service",
            characteristics=[]
        )
        service2 = ServiceInfo(
            uuid=BluetoothUUID("180F"),
            name="Battery Service",
            characteristics=[]
        )

        assert service1 == service2
```

### Phase 4: Descriptor Types (90% → 95%)

**File**: `src/bluetooth_sig/types/descriptor_types.py`

**Test Plan**:

```python
# tests/types/test_descriptor_types.py (expand)

class TestDescriptorData:
    """Test DescriptorData edge cases."""

    def test_descriptor_with_parse_failure(self):
        """Test descriptor parsing failure."""
        desc = DescriptorData(
            info=DescriptorInfo(
                uuid=BluetoothUUID("2901"),
                name="Characteristic User Description",
                description="",
                has_structured_data=True,
                data_format="utf8s"
            ),
            value=None,
            raw_data=bytearray([0xFF, 0xFF]),  # Invalid UTF-8
            parse_success=False,
            error_message="Invalid UTF-8 sequence"
        )

        assert not desc.parse_success
        assert desc.error_message is not None

    def test_descriptor_data_immutability(self):
        """Test that DescriptorData is frozen."""
        desc = DescriptorData(
            info=DescriptorInfo(uuid=BluetoothUUID("2901"), name="Test"),
            value="test",
            raw_data=bytearray([0x74, 0x65, 0x73, 0x74]),
            parse_success=True,
            error_message=None
        )

        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            desc.value = "modified"
```

### Phase 5: Error Path Coverage

Ensure all error paths have tests:

```python
# Add to relevant test files

class TestErrorPaths:
    """Test error handling paths."""

    def test_insufficient_data_errors(self):
        """Test all characteristics handle insufficient data."""
        # Test that every characteristic raises InsufficientDataError
        # when given too little data
        pass

    def test_value_range_errors(self):
        """Test all characteristics validate value ranges."""
        # Test characteristics with range constraints
        pass

    def test_invalid_format_errors(self):
        """Test characteristics handle malformed data."""
        # Test with intentionally corrupted data
        pass
```

## Files to Modify

### Create New Test Files
- `tests/utils/test_rssi_utils.py` (if doesn't exist, or expand)

### Expand Existing Test Files
- `tests/types/test_uuid.py`
- `tests/types/test_gatt_services.py`
- `tests/types/test_descriptor_types.py`
- `tests/gatt/characteristics/test_*.py` (add edge case tests)

### Coverage Configuration
- `.coveragerc` or `pyproject.toml` - Ensure coverage includes all modules

## Validation Steps

1. **Run coverage report**:
   ```bash
   python -m pytest tests/ --cov=src/bluetooth_sig --cov-report=html --cov-report=term
   ```

2. **Review HTML coverage report**:
   ```bash
   open htmlcov/index.html
   ```

3. **Check specific module coverage**:
   ```bash
   python -m pytest tests/utils/ --cov=src/bluetooth_sig/utils --cov-report=term-missing
   ```

4. **Verify quality gates**:
   ```bash
   ./scripts/format.sh --check
   ./scripts/lint.sh --all
   python -m pytest tests/ -v
   ```

## Acceptance Criteria

- [ ] Overall coverage ≥90%
- [ ] `rssi_utils.py` coverage ≥80%
- [ ] `gatt_services.py` coverage ≥90%
- [ ] `uuid.py` coverage ≥90%
- [ ] All error paths tested
- [ ] All edge cases have dedicated tests
- [ ] Coverage report generated in CI
- [ ] No regression in existing test passing rate

## Monitoring

Add coverage badge and tracking:

1. **Update CI workflow** to fail if coverage drops below 90%
2. **Add coverage badge** to README.md
3. **Track coverage trends** over time

## Notes for AI Agents

- Focus on quality over quantity - meaningful tests that catch real bugs
- Use parametrized tests for multiple similar test cases
- Follow existing test patterns in the repository
- Ensure tests are deterministic and don't rely on external state
- Use meaningful test names that describe what they're testing
- Add docstrings to test classes and methods
- Group related tests into classes
- Use fixtures for common setup code
- Mock external dependencies appropriately
- Test both success and failure paths
