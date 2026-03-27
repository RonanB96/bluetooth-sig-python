"""Tests for BearerSignalStrengthReportingIntervalCharacteristic (2BB8)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_signal_strength_reporting_interval import (
    BearerSignalStrengthReportingIntervalCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerSignalStrengthReportingInterval(CommonCharacteristicTests):
    """Test suite for BearerSignalStrengthReportingIntervalCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerSignalStrengthReportingIntervalCharacteristic:
        return BearerSignalStrengthReportingIntervalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Interval 0s"),
            CharacteristicTestData(bytearray([0x0A]), 10, "Interval 10s"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max interval"),
        ]

    def test_roundtrip(self, characteristic: BearerSignalStrengthReportingIntervalCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Interval 0s"),
            CharacteristicTestData(bytearray([0x0A]), 10, "Interval 10s"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max interval"),
        ]
