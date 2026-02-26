"""Tests for Battery Time Status characteristic (0x2BEF)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_time_status import (
    BatteryTimeStatus,
    BatteryTimeStatusCharacteristic,
    BatteryTimeStatusFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestBatteryTimeStatusCharacteristic(CommonCharacteristicTests):
    """Test Battery Time Status characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Battery Time Status characteristic for testing."""
        return BatteryTimeStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Time Status characteristic."""
        return "2BEE"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery time status test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,  # flags: both optional fields present
                        0x3C,
                        0x00,
                        0x00,  # time_until_discharged: 60 minutes
                        0x1E,
                        0x00,
                        0x00,  # time_until_discharged_on_standby: 30 minutes
                        0x5A,
                        0x00,
                        0x00,  # time_until_recharged: 90 minutes
                    ]
                ),
                expected_value=BatteryTimeStatus(
                    flags=BatteryTimeStatusFlags(0x03),
                    time_until_discharged=60,
                    time_until_discharged_on_standby=30,
                    time_until_recharged=90,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0x78,
                        0x00,
                        0x00,  # time_until_discharged: 120 minutes
                    ]
                ),
                expected_value=BatteryTimeStatus(
                    flags=BatteryTimeStatusFlags(0x00),
                    time_until_discharged=120,
                ),
                description="Mandatory field only",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0xFF,
                        0xFF,
                        0xFF,  # time_until_discharged: Unknown sentinel
                    ]
                ),
                expected_value=BatteryTimeStatus(
                    flags=BatteryTimeStatusFlags(0x00),
                    time_until_discharged=None,
                ),
                description="Unknown sentinel for mandatory field",
            ),
        ]

    def test_sentinel_unknown_returns_none(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that 0xFFFFFF sentinel decodes to None."""
        data = bytearray(
            [
                0x03,  # both optional fields present
                0xFF,
                0xFF,
                0xFF,  # discharged: Unknown
                0xFF,
                0xFF,
                0xFF,  # on standby: Unknown
                0xFF,
                0xFF,
                0xFF,  # recharged: Unknown
            ]
        )
        result = characteristic.parse_value(data)
        assert result.time_until_discharged is None
        assert result.time_until_discharged_on_standby is None
        assert result.time_until_recharged is None

    def test_large_time_value(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify large time values (just under sentinel) decode correctly."""
        # 0xFFFFFD = 16777213 minutes
        data = bytearray(
            [
                0x00,  # flags: mandatory only
                0xFD,
                0xFF,
                0xFF,  # time_until_discharged: 16777213 minutes
            ]
        )
        result = characteristic.parse_value(data)
        assert result.time_until_discharged == 0xFFFFFD

    def test_standby_only(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify only standby optional field present."""
        data = bytearray(
            [
                0x01,  # flags: bit 0 = standby present
                0x0A,
                0x00,
                0x00,  # discharged: 10 minutes
                0x14,
                0x00,
                0x00,  # on standby: 20 minutes
            ]
        )
        result = characteristic.parse_value(data)
        assert result.time_until_discharged == 10
        assert result.time_until_discharged_on_standby == 20
        assert result.time_until_recharged is None

    def test_recharged_only(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify only recharged optional field present."""
        data = bytearray(
            [
                0x02,  # flags: bit 1 = recharged present
                0x05,
                0x00,
                0x00,  # discharged: 5 minutes
                0x2D,
                0x00,
                0x00,  # recharged: 45 minutes
            ]
        )
        result = characteristic.parse_value(data)
        assert result.time_until_discharged == 5
        assert result.time_until_discharged_on_standby is None
        assert result.time_until_recharged == 45

    def test_roundtrip_all_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with all fields."""
        original = BatteryTimeStatus(
            flags=BatteryTimeStatusFlags(0x03),
            time_until_discharged=120,
            time_until_discharged_on_standby=480,
            time_until_recharged=60,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_roundtrip_unknown_sentinel(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with None (unknown sentinel)."""
        original = BatteryTimeStatus(
            flags=BatteryTimeStatusFlags(0x00),
            time_until_discharged=None,
        )
        encoded = characteristic.build_value(original)
        # Unknown sentinel should produce 0xFF 0xFF 0xFF
        assert encoded[1:4] == bytearray([0xFF, 0xFF, 0xFF])
        decoded = characteristic.parse_value(encoded)
        assert decoded.time_until_discharged is None

    def test_zero_time(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify zero minutes value is valid."""
        data = bytearray(
            [
                0x00,
                0x00,
                0x00,
                0x00,  # discharged: 0 minutes
            ]
        )
        result = characteristic.parse_value(data)
        assert result.time_until_discharged == 0

    def test_too_short_data(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that data shorter than min_length raises error."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x01, 0x02]))
