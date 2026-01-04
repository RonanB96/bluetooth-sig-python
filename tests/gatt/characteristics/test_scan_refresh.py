"""Tests for Scan Refresh characteristic (0x2A31)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ScanRefreshCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestScanRefreshCharacteristic(CommonCharacteristicTests):
    """Test suite for Scan Refresh characteristic."""

    @pytest.fixture
    def characteristic(self) -> ScanRefreshCharacteristic:
        """Return a Scan Refresh characteristic instance."""
        return ScanRefreshCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Scan Refresh characteristic."""
        return "2A31"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for scan refresh."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Refresh not required"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Server requires refresh"),
        ]

    def test_no_refresh_required(self) -> None:
        """Test no refresh required."""
        char = ScanRefreshCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0

    def test_refresh_required(self) -> None:
        """Test server requires refresh."""
        char = ScanRefreshCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == 1

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = ScanRefreshCharacteristic()
        for value in [0, 1]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
