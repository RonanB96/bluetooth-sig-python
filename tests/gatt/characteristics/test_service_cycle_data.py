"""Tests for Service Cycle Data characteristic (0x2C11)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.service_cycle_data import ServiceCycleDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestServiceCycleDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Service Cycle Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> ServiceCycleDataCharacteristic:
        return ServiceCycleDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C11"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x42]),
                expected_value=b"\x42",
                description="Single byte service cycle record",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x20, 0x30]),
                expected_value=b"\x10\x20\x30",
                description="Multi-byte service cycle record",
            ),
        ]

    def test_roundtrip(self, characteristic: ServiceCycleDataCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = b"\xab\xcd\xef"
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
