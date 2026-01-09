"""Tests for Linear Position characteristic (0x2C08)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.linear_position import LinearPositionCharacteristic
from bluetooth_sig.gatt.constants import SINT32_MAX
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLinearPositionCharacteristic(CommonCharacteristicTests):
    """Test Linear Position characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Linear Position characteristic for testing."""
        return LinearPositionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Linear Position characteristic."""
        return "2C08"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid linear position test data covering various positions and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="0 m (zero position)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x96, 0x98, 0x00]), expected_value=1.0, description="1.0 m (one meter)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x69, 0x67, 0xFF]),
                expected_value=-1.0,
                description="-1.0 m (negative position)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0xFF, 0xFF, 0x7F]),
                expected_value=214.7483646,
                description="Maximum position",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=1e-7,
                description="1e-7 m (precision test)",
            ),
        ]

    # === Linear Position-Specific Tests ===
    def test_linear_position_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test linear position precision and boundary values."""
        # Test zero position
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result == 0.0

        # Test positive position (0.5 m)
        result = characteristic.parse_value(bytearray([0x40, 0x4B, 0x4C, 0x00]))  # 5000000 = 0.5 m
        assert result is not None
        assert abs(result - 0.5) < 1e-7

        # Test negative position (-0.25 m)
        result = characteristic.parse_value(bytearray([0x60, 0xDA, 0xD9, 0xFF]))  # -2500000 = -0.25 m
        assert result is not None
        assert abs(result + 0.25) < 1e-7

    def test_linear_position_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme linear position values within valid range."""
        # Test maximum positive value
        max_value = SINT32_MAX - 1
        max_data = bytearray(
            [max_value & 0xFF, (max_value >> 8) & 0xFF, (max_value >> 16) & 0xFF, (max_value >> 24) & 0xFF]
        )  # 2147483646 = 214.7483646 m
        result = characteristic.parse_value(max_data)
        assert result is not None
        assert abs(result - 214.7483646) < 1e-7

        # Test near-minimum negative value (-214.7483646 m, which is -2147483646)
        min_data = bytearray([0x02, 0x00, 0x00, 0x80])  # -2147483646 = -214.7483646 m
        result = characteristic.parse_value(min_data)
        assert result is not None
        assert result is not None
        assert abs(result + 214.7483646) < 1e-7

        # Test "value is not known" special value
        unknown_data = bytearray([0xFF, 0xFF, 0xFF, 0x7F])  # 0x7FFFFFFF
        result = characteristic.parse_value(unknown_data)
        assert result is None

    def test_linear_position_encoding_accuracy(self, characteristic: LinearPositionCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common positions
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert characteristic.build_value(1.0) == bytearray([0x80, 0x96, 0x98, 0x00])
        assert characteristic.build_value(-1.0) == bytearray([0x80, 0x69, 0x67, 0xFF])

    def test_encode_value(self, characteristic: LinearPositionCharacteristic) -> None:
        """Test encoding linear position values."""
        # Test encoding positive position
        encoded = characteristic.build_value(0.5)
        assert encoded == bytearray([0x40, 0x4B, 0x4C, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00])

        # Test encoding negative position
        encoded = characteristic.build_value(-0.25)
        assert encoded == bytearray([0x60, 0xDA, 0xD9, 0xFF])

    def test_characteristic_metadata(self, characteristic: LinearPositionCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Linear Position"
        assert characteristic.unit == "m"
        assert characteristic.uuid == "2C08"
