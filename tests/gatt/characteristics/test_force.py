"""Tests for Force characteristic (0x2C07)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.force import ForceCharacteristic
from bluetooth_sig.gatt.constants import SINT32_MAX
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestForceCharacteristic(CommonCharacteristicTests):
    """Test Force characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Force characteristic for testing."""
        return ForceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Force characteristic."""
        return "2C07"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid force test data covering various forces and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="0 N (no force)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]), expected_value=1.0, description="1 N (1 Newton)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x18, 0xFC, 0xFF, 0xFF]), expected_value=-1.0, description="-1 N (negative force)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0xFF, 0xFF, 0x7F]), expected_value=2147483.646, description="Maximum force"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=0.001,
                description="0.001 N (precision test)",
            ),
        ]

    # === Force-Specific Tests ===
    def test_force_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test force precision and boundary values."""
        # Test zero force
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result is not None
        assert result == 0.0

        # Test negative force (-1 N)
        result = characteristic.parse_value(bytearray([0x18, 0xFC, 0xFF, 0xFF]))  # -1000 = -1.00 N
        assert result is not None
        assert abs(result + 1.0) < 0.001

        # Test precision (1 N)
        result = characteristic.parse_value(bytearray([0xE8, 0x03, 0x00, 0x00]))  # 1000 = 1.00 N
        assert result is not None
        assert abs(result - 1.0) < 0.001

    def test_force_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme force values within valid range."""
        # Test maximum positive value
        max_value = SINT32_MAX - 1
        max_data = bytearray(
            [max_value & 0xFF, (max_value >> 8) & 0xFF, (max_value >> 16) & 0xFF, (max_value >> 24) & 0xFF]
        )  # 2147483646 = 2147483.646 N
        result = characteristic.parse_value(max_data)
        assert result is not None
        assert abs(result - 2147483.646) < 0.001

        # Test near-minimum negative value (-2147483.646 N, which is -2147483646)
        min_data = bytearray([0x02, 0x00, 0x00, 0x80])  # -2147483646 = -2147483.646 N
        result = characteristic.parse_value(min_data)
        assert result is not None
        assert abs(result + 2147483.646) < 0.001

        # Test "value is not known" special value
        unknown_data = bytearray([0xFF, 0xFF, 0xFF, 0x7F])  # 0x7FFFFFFF
        from bluetooth_sig.gatt.exceptions import SpecialValueDetectedError

        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(unknown_data)
        assert exc_info.value.special_value.meaning == "value is not known"

    def test_force_encoding_accuracy(self, characteristic: ForceCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common forces
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert characteristic.build_value(1.0) == bytearray([0xE8, 0x03, 0x00, 0x00])
        assert characteristic.build_value(-1.0) == bytearray([0x18, 0xFC, 0xFF, 0xFF])

        # Test exact length data
        data = bytearray([0xE8, 0x03, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result is not None
        assert abs(result - 1.0) < 0.001

    def test_encode_value(self, characteristic: ForceCharacteristic) -> None:
        """Test encoding force values."""
        # Test encoding positive force
        encoded = characteristic.build_value(1.0)
        assert encoded == bytearray([0xE8, 0x03, 0x00, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00])

        # Test encoding negative force
        encoded = characteristic.build_value(-1.0)
        assert encoded == bytearray([0x18, 0xFC, 0xFF, 0xFF])

    def test_characteristic_metadata(self, characteristic: ForceCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Force"
        assert characteristic.unit == "N"
        assert characteristic.uuid == "2C07"
