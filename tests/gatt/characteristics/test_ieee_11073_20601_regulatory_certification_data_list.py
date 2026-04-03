"""Tests for IEEE 11073-20601 Regulatory Certification Data List."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ieee_11073_20601_regulatory_certification_data_list import (
    IEEE11073RegulatoryData,
    IEEE1107320601RegulatoryCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIEEE1107320601RegulatoryCharacteristic(CommonCharacteristicTests):
    """Test suite for IEEE1107320601RegulatoryCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IEEE1107320601RegulatoryCharacteristic:
        return IEEE1107320601RegulatoryCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A2A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x42"),
                expected_value=IEEE11073RegulatoryData(certification_data=b"\x42"),
                description="single byte",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x01\x02\x03\x04\x05\x06\x07\x08"),
                expected_value=IEEE11073RegulatoryData(certification_data=b"\x01\x02\x03\x04\x05\x06\x07\x08"),
                description="multi-byte certification data",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x00\xff\x00\xff\x00"),
                expected_value=IEEE11073RegulatoryData(certification_data=b"\x00\xff\x00\xff\x00"),
                description="embedded nulls preserved",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xde\xad\xbe\xef\xca\xfe\xba\xbe"),
                expected_value=IEEE11073RegulatoryData(certification_data=b"\xde\xad\xbe\xef\xca\xfe\xba\xbe"),
                description="arbitrary byte pattern",
            ),
            CharacteristicTestData(
                input_data=bytearray(range(256)),
                expected_value=IEEE11073RegulatoryData(certification_data=bytes(range(256))),
                description="all 256 byte values",
            ),
        ]
