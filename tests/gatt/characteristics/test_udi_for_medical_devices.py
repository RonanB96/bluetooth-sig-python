"""Tests for UDIForMedicalDevicesCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.udi_for_medical_devices import (
    UDIFlags,
    UDIForMedicalDevicesCharacteristic,
    UDIForMedicalDevicesData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestUDIForMedicalDevicesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> UDIForMedicalDevicesCharacteristic:
        return UDIForMedicalDevicesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]) + bytearray(b"ABC\x00"),
                expected_value=UDIForMedicalDevicesData(
                    flags=UDIFlags.UDI_LABEL_PRESENT,
                    udi_label="ABC",
                ),
                description="label only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0F])
                + bytearray(b"LBL\x00")
                + bytearray(b"DI\x00")
                + bytearray(b"ISS\x00")
                + bytearray(b"AUTH\x00"),
                expected_value=UDIForMedicalDevicesData(
                    flags=UDIFlags.UDI_LABEL_PRESENT
                    | UDIFlags.UDI_DEVICE_IDENTIFIER_PRESENT
                    | UDIFlags.UDI_ISSUER_PRESENT
                    | UDIFlags.UDI_AUTHORITY_PRESENT,
                    udi_label="LBL",
                    device_identifier="DI",
                    udi_issuer="ISS",
                    udi_authority="AUTH",
                ),
                description="all fields present",
            ),
        ]
