"""Tests for TDSControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.tds_control_point import (
    TDSControlPointCharacteristic,
    TDSControlPointData,
    TDSControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTDSControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> TDSControlPointCharacteristic:
        return TDSControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x05]),
                expected_value=TDSControlPointData(
                    op_code=TDSControlPointOpCode.ACTIVATE_TRANSPORT,
                    organization_id=5,
                    parameter=None,
                ),
                description="activate transport, org_id=5, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0xAB, 0xCD]),
                expected_value=TDSControlPointData(
                    op_code=TDSControlPointOpCode.ACTIVATE_TRANSPORT,
                    organization_id=2,
                    parameter=b"\xab\xcd",
                ),
                description="activate transport, org_id=2, with parameter",
            ),
        ]
