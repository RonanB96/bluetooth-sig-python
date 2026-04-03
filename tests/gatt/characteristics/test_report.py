"""Tests for ReportCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.report import ReportCharacteristic, ReportData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestReportCharacteristic(CommonCharacteristicTests):
    """Test suite for ReportCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> ReportCharacteristic:
        return ReportCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A4D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=ReportData(data=b"\x01"),
                description="single byte",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDE, 0xAD, 0xBE, 0xEF]),
                expected_value=ReportData(data=b"\xde\xad\xbe\xef"),
                description="multi-byte payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03]),
                expected_value=ReportData(data=b"\x01\x02\x03"),
                description="three-byte payload",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xaa\xbb\xcc\xdd\xee"),
                expected_value=ReportData(data=b"\xaa\xbb\xcc\xdd\xee"),
                description="five-byte payload",
            ),
        ]
