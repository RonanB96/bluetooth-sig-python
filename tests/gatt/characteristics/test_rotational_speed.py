"""Tests for Rotational Speed characteristic (0x2C09)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.rotational_speed import RotationalSpeedCharacteristic
from bluetooth_sig.gatt.constants import SINT32_MAX
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRotationalSpeedCharacteristic(CommonCharacteristicTests):
    """Test Rotational Speed characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Rotational Speed characteristic for testing."""
        return RotationalSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Rotational Speed characteristic."""
        return "2C09"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid rotational speed test data covering various speeds and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="0 RPM (stopped)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]),
                expected_value=1000.0,
                description="1000 RPM (moderate speed)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x18, 0xFC, 0xFF, 0xFF]),
                expected_value=-1000.0,
                description="-1000 RPM (reverse rotation)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0xFF, 0xFF, 0x7F]), expected_value=2147483646.0, description="Maximum speed"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=1.0,
                description="1 RPM (precision test)",
            ),
        ]

    # === Rotational Speed-Specific Tests ===
    def test_rotational_speed_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test rotational speed precision and boundary values."""
        # Test zero speed
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result == 0.0

        # Test positive speed (1500 RPM)
        result = characteristic.parse_value(bytearray([0xDC, 0x05, 0x00, 0x00]))  # 1500 = 1500 RPM
        assert result is not None
        assert abs(result - 1500.0) < 0.001

        # Test negative speed (-500 RPM)
        result = characteristic.parse_value(bytearray([0x0C, 0xFE, 0xFF, 0xFF]))  # -500 = -500 RPM
        assert result is not None
        assert abs(result + 500.0) < 0.001

    def test_rotational_speed_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme rotational speed values within valid range."""
        # Test maximum positive value
        max_value = SINT32_MAX - 1
        max_data = bytearray(
            [max_value & 0xFF, (max_value >> 8) & 0xFF, (max_value >> 16) & 0xFF, (max_value >> 24) & 0xFF]
        )  # 2147483646 = 2147483646 RPM
        result = characteristic.parse_value(max_data)
        assert result is not None
        assert abs(result - 2147483646.0) < 0.001

        # Test near-minimum negative value (-2147483646 RPM, which is -2147483646)
        min_data = bytearray([0x02, 0x00, 0x00, 0x80])  # -2147483646 = -2147483646 RPM
        result = characteristic.parse_value(min_data)
        assert result is not None
        assert result is not None
        assert abs(result + 2147483646.0) < 0.001

        # Test "value is not known" special value
        unknown_data = bytearray([0xFF, 0xFF, 0xFF, 0x7F])  # 0x7FFFFFFF
        from bluetooth_sig.gatt.exceptions import SpecialValueDetectedError

        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(unknown_data)
        assert exc_info.value.special_value.meaning == "value is not known"

    def test_rotational_speed_encoding_accuracy(self, characteristic: RotationalSpeedCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common speeds
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert characteristic.build_value(1000.0) == bytearray([0xE8, 0x03, 0x00, 0x00])
        assert characteristic.build_value(-1000.0) == bytearray([0x18, 0xFC, 0xFF, 0xFF])

    def test_encode_value(self, characteristic: RotationalSpeedCharacteristic) -> None:
        """Test encoding rotational speed values."""
        # Test encoding positive speed
        encoded = characteristic.build_value(1500.0)
        assert encoded == bytearray([0xDC, 0x05, 0x00, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00])

        # Test encoding negative speed
        encoded = characteristic.build_value(-500.0)
        assert encoded == bytearray([0x0C, 0xFE, 0xFF, 0xFF])

    def test_characteristic_metadata(self, characteristic: RotationalSpeedCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Rotational Speed"
        assert characteristic.unit == "RPM"
        assert characteristic.uuid == "2C09"
