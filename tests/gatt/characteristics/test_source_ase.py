"""Tests for Source ASE characteristic (0x2BC5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.source_ase import (
    SourceASECharacteristic,
    SourceASEData,
    SourceASEState,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSourceASECharacteristic(CommonCharacteristicTests):
    """Test suite for Source ASE characteristic."""

    @pytest.fixture
    def characteristic(self) -> SourceASECharacteristic:
        return SourceASECharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00]),
                expected_value=SourceASEData(
                    ase_id=2,
                    ase_state=SourceASEState.IDLE,
                    additional_data=b"",
                ),
                description="ASE ID 2, Idle state, no additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x03, 0xCC, 0xDD, 0xEE]),
                expected_value=SourceASEData(
                    ase_id=4,
                    ase_state=SourceASEState.ENABLING,
                    additional_data=b"\xcc\xdd\xee",
                ),
                description="ASE ID 4, Enabling state, with additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x05]),
                expected_value=SourceASEData(
                    ase_id=1,
                    ase_state=SourceASEState.DISABLING,
                    additional_data=b"",
                ),
                description="ASE ID 1, Disabling state",
            ),
        ]
