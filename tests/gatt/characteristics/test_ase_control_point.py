"""Tests for ASEControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ase_control_point import (
    ASEControlPointCharacteristic,
    ASEControlPointData,
    ASEControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestASEControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ASEControlPointCharacteristic:
        return ASEControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02]),
                expected_value=ASEControlPointData(
                    op_code=ASEControlPointOpCode.CONFIG_CODEC,
                    number_of_ases=2,
                    parameter_data=b"",
                ),
                description="CONFIG_CODEC with 2 ASEs, no parameter data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x01, 0xAA, 0xBB]),
                expected_value=ASEControlPointData(
                    op_code=ASEControlPointOpCode.ENABLE,
                    number_of_ases=1,
                    parameter_data=b"\xaa\xbb",
                ),
                description="ENABLE with 1 ASE and parameter data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x01, 0x05]),
                expected_value=ASEControlPointData(
                    op_code=ASEControlPointOpCode.RELEASE,
                    number_of_ases=1,
                    parameter_data=b"\x05",
                ),
                description="RELEASE with 1 ASE and ASE_ID parameter",
            ),
        ]
