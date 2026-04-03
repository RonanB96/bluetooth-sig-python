"""Tests for BroadcastReceiveStateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.broadcast_receive_state import (
    BIGEncryption,
    BroadcastReceiveStateCharacteristic,
    BroadcastReceiveStateData,
    PASyncState,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBroadcastReceiveStateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BroadcastReceiveStateCharacteristic:
        return BroadcastReceiveStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # source_id=1, addr_type=0, addr=AA:BB:CC:DD:EE:FF, adv_sid=5,
                # broadcast_id=0x010203 (LE: 03 02 01), pa_sync=SYNCHRONIZED, big_enc=NOT_ENCRYPTED
                input_data=bytearray(
                    [
                        0x01,  # source_id
                        0x00,  # source_address_type (public)
                        0xAA,
                        0xBB,
                        0xCC,
                        0xDD,
                        0xEE,
                        0xFF,  # source_address
                        0x05,  # source_adv_sid
                        0x03,
                        0x02,
                        0x01,  # broadcast_id (uint24 LE = 0x010203)
                        0x02,  # pa_sync_state = SYNCHRONIZED
                        0x00,  # big_encryption = NOT_ENCRYPTED
                    ]
                ),
                expected_value=BroadcastReceiveStateData(
                    source_id=1,
                    source_address_type=0,
                    source_address=b"\xaa\xbb\xcc\xdd\xee\xff",
                    source_adv_sid=5,
                    broadcast_id=0x010203,
                    pa_sync_state=PASyncState.SYNCHRONIZED,
                    big_encryption=BIGEncryption.NOT_ENCRYPTED,
                    additional_data=b"",
                ),
                description="Synchronized source, not encrypted, no additional data",
            ),
            CharacteristicTestData(
                # source_id=0, addr_type=1, addr=all zeros, adv_sid=0,
                # broadcast_id=0, pa_sync=NOT_SYNCHRONIZED, big_enc=BROADCAST_CODE_REQUIRED,
                # additional_data=0xDE 0xAD
                input_data=bytearray(
                    [
                        0x00,  # source_id
                        0x01,  # source_address_type (random)
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # source_address
                        0x00,  # source_adv_sid
                        0x00,
                        0x00,
                        0x00,  # broadcast_id = 0
                        0x00,  # pa_sync_state = NOT_SYNCHRONIZED
                        0x01,  # big_encryption = BROADCAST_CODE_REQUIRED
                        0xDE,
                        0xAD,  # additional_data
                    ]
                ),
                expected_value=BroadcastReceiveStateData(
                    source_id=0,
                    source_address_type=1,
                    source_address=b"\x00\x00\x00\x00\x00\x00",
                    source_adv_sid=0,
                    broadcast_id=0,
                    pa_sync_state=PASyncState.NOT_SYNCHRONIZED,
                    big_encryption=BIGEncryption.BROADCAST_CODE_REQUIRED,
                    additional_data=b"\xde\xad",
                ),
                description="Not synchronized, broadcast code required, with additional data",
            ),
        ]
