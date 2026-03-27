"""Tests for On-demand Ranging Data characteristic (0x2C16)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.on_demand_ranging_data import OnDemandRangingDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestOnDemandRangingDataCharacteristic(CommonCharacteristicTests):
    """Test suite for On-demand Ranging Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> OnDemandRangingDataCharacteristic:
        return OnDemandRangingDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C16"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFE]),
                expected_value=b"\xfe",
                description="Single byte on-demand ranging data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDE, 0xAD, 0xBE, 0xEF]),
                expected_value=b"\xde\xad\xbe\xef",
                description="Multi-byte on-demand ranging data",
            ),
        ]

    def test_roundtrip(self, characteristic: OnDemandRangingDataCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = b"\x11\x22\x33"
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
