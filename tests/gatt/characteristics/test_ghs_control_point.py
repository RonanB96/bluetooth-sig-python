"""Tests for GHS Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ghs_control_point import (
    GHSControlPointCharacteristic,
    GHSControlPointData,
    GHSControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGHSControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for GHS Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> GHSControlPointCharacteristic:
        return GHSControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=GHSControlPointData(
                    opcode=GHSControlPointOpCode.START_SEND_LIVE_OBSERVATIONS,
                ),
                description="Start sending live observations",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x01, 0x02]),
                expected_value=GHSControlPointData(
                    opcode=GHSControlPointOpCode.RESPONSE_CODE,
                    parameter=b"\x01\x02",
                ),
                description="Response code with parameters",
            ),
        ]
