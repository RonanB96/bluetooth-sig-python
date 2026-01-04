"""Tests for Peripheral Preferred Connection Parameters characteristic (0x2A04)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    ConnectionParametersData,
    PeripheralPreferredConnectionParametersCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPeripheralPreferredConnectionParametersCharacteristic(CommonCharacteristicTests):
    """Test suite for Peripheral Preferred Connection Parameters characteristic."""

    @pytest.fixture
    def characteristic(self) -> PeripheralPreferredConnectionParametersCharacteristic:
        """Return a Peripheral Preferred Connection Parameters characteristic instance."""
        return PeripheralPreferredConnectionParametersCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Peripheral Preferred Connection Parameters characteristic."""
        return "2A04"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for peripheral preferred connection parameters."""
        return [
            CharacteristicTestData(
                input_data=bytearray([6, 0, 6, 0, 0, 0, 100, 0]),
                expected_value=ConnectionParametersData(min_interval=7.5, max_interval=7.5, latency=0, timeout=1000),
                description="Fast connection (7.5ms)",
            ),
            CharacteristicTestData(
                input_data=bytearray([80, 0, 100, 0, 0, 0, 200, 1]),
                expected_value=ConnectionParametersData(
                    min_interval=100.0, max_interval=125.0, latency=0, timeout=4560
                ),
                description="Standard connection",
            ),
        ]

    def test_fast_connection_parameters(self) -> None:
        """Test fast connection parameters."""
        char = PeripheralPreferredConnectionParametersCharacteristic()
        result = char.parse_value(bytearray([6, 0, 6, 0, 0, 0, 100, 0]))
        assert result.min_interval == 7.5  # 6 * 1.25
        assert result.max_interval == 7.5  # 6 * 1.25
        assert result.latency == 0
        assert result.timeout == 1000  # 100 * 10

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = PeripheralPreferredConnectionParametersCharacteristic()
        original = ConnectionParametersData(min_interval=80, max_interval=100, latency=0, timeout=200)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
