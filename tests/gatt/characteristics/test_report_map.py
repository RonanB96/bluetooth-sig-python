"""Tests for ReportMapCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.report_map import ReportMapCharacteristic, ReportMapData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestReportMapCharacteristic(CommonCharacteristicTests):
    """Test suite for ReportMapCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> ReportMapCharacteristic:
        return ReportMapCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A4B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=ReportMapData(data=b"\x05"),
                description="single byte",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x01, 0x09, 0x06, 0xA1, 0x01]),
                expected_value=ReportMapData(data=b"\x05\x01\x09\x06\xa1\x01"),
                description="HID keyboard descriptor fragment",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=ReportMapData(data=b"\x00\x00\x00"),
                description="all zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAB]),
                expected_value=ReportMapData(data=b"\xab"),
                description="single 0xAB byte",
            ),
            CharacteristicTestData(
                input_data=bytearray(range(256)),
                expected_value=ReportMapData(data=bytes(range(256))),
                description="all 256 byte values",
            ),
        ]
