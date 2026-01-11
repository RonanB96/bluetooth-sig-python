"""Tests for Acceleration characteristic (0x2C06)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.acceleration import AccelerationCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.constants import SINT32_MAX
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAccelerationCharacteristic(CommonCharacteristicTests):
    """Test Acceleration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Acceleration characteristic for testing."""
        return AccelerationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Acceleration characteristic."""
        return "2C06"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid acceleration test data covering various accelerations and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="0 m/s² (no acceleration)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]),
                expected_value=1.0,
                description="1.0 m/s² (standard gravity)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x18, 0xFC, 0xFF, 0xFF]),
                expected_value=-1.0,
                description="-1.0 m/s² (negative acceleration)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0xFF, 0xFF, 0x7F]),
                expected_value=2147483.646,
                description="Maximum acceleration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=0.001,
                description="0.001 m/s² (precision test)",
            ),
        ]

    # === Acceleration-Specific Tests ===
    def test_acceleration_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test acceleration precision and boundary values."""
        # Test zero acceleration
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))

        assert result == 0.0

        # Test positive acceleration (9.81 m/s²)
        result = characteristic.parse_value(bytearray([0x52, 0x26, 0x00, 0x00]))  # 9810 = 9.81 m/s²

        assert result is not None
        assert abs(result - 9.81) < 0.001

        # Test negative acceleration (-5.0 m/s²)
        result = characteristic.parse_value(bytearray([0x78, 0xEC, 0xFF, 0xFF]))  # -5000 = -5.0 m/s²

        assert result is not None
        assert abs(result + 5.0) < 0.001

    def test_acceleration_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme acceleration values within valid range."""
        # Test maximum positive value
        max_value = SINT32_MAX - 1
        max_data = bytearray(
            [max_value & 0xFF, (max_value >> 8) & 0xFF, (max_value >> 16) & 0xFF, (max_value >> 24) & 0xFF]
        )  # 2147483646 = 2147483.646 m/s²
        result = characteristic.parse_value(max_data)

        assert result is not None
        assert abs(result - 2147483.646) < 0.001

        # Test near-minimum negative value (-2147483.646 m/s², which is -2147483646)
        min_data = bytearray([0x02, 0x00, 0x00, 0x80])  # -2147483646 = -2147483.646 m/s²
        result = characteristic.parse_value(min_data)

        assert result is not None
        assert abs(result + 2147483.646) < 0.001

        # Test "value is not known" special value
        unknown_data = bytearray([0xFF, 0xFF, 0xFF, 0x7F])  # 0x7FFFFFFF
        from bluetooth_sig.gatt.exceptions import SpecialValueDetected

        with pytest.raises(SpecialValueDetected) as exc_info:
            characteristic.parse_value(unknown_data)
        assert exc_info.value.special_value.meaning == "value is not known"

    def test_acceleration_encoding_accuracy(self, characteristic: AccelerationCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common accelerations
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert characteristic.build_value(1.0) == bytearray([0xE8, 0x03, 0x00, 0x00])
        assert characteristic.build_value(-1.0) == bytearray([0x18, 0xFC, 0xFF, 0xFF])

    def test_encode_value(self, characteristic: AccelerationCharacteristic) -> None:
        """Test encoding acceleration values."""
        # Test encoding positive acceleration
        encoded = characteristic.build_value(9.81)
        assert encoded == bytearray([0x52, 0x26, 0x00, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00])

        # Test encoding negative acceleration
        encoded = characteristic.build_value(-5.0)
        assert encoded == bytearray([0x78, 0xEC, 0xFF, 0xFF])

    def test_characteristic_metadata(self, characteristic: AccelerationCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Acceleration"
        assert characteristic.unit == "m/s²"
        assert characteristic.uuid == "2C06"
