"""Tests for BroadcastAudioScanControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.broadcast_audio_scan_control_point import (
    BroadcastAudioScanControlPointCharacteristic,
    BroadcastAudioScanControlPointData,
    BroadcastAudioScanControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBroadcastAudioScanControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BroadcastAudioScanControlPointCharacteristic:
        return BroadcastAudioScanControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=BroadcastAudioScanControlPointData(
                    op_code=BroadcastAudioScanControlPointOpCode.REMOTE_SCAN_STOPPED,
                    parameter_data=b"",
                ),
                description="Remote scan stopped, no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BroadcastAudioScanControlPointData(
                    op_code=BroadcastAudioScanControlPointOpCode.REMOTE_SCAN_STARTED,
                    parameter_data=b"",
                ),
                description="Remote scan started, no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0xAA, 0xBB, 0xCC]),
                expected_value=BroadcastAudioScanControlPointData(
                    op_code=BroadcastAudioScanControlPointOpCode.ADD_SOURCE,
                    parameter_data=b"\xaa\xbb\xcc",
                ),
                description="Add source with parameter data",
            ),
        ]
