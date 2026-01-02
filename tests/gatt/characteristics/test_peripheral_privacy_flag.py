"""Tests for Peripheral Privacy Flag characteristic (0x2A02)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PeripheralPrivacyFlagCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPeripheralPrivacyFlagCharacteristic(CommonCharacteristicTests):
    """Test suite for Peripheral Privacy Flag characteristic."""

    @pytest.fixture
    def characteristic(self) -> PeripheralPrivacyFlagCharacteristic:
        """Return a Peripheral Privacy Flag characteristic instance."""
        return PeripheralPrivacyFlagCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Peripheral Privacy Flag characteristic."""
        return "2A02"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for peripheral privacy flag."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=False, description="Privacy disabled"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=True, description="Privacy enabled"),
        ]

    def test_privacy_disabled(self) -> None:
        """Test privacy flag disabled."""
        char = PeripheralPrivacyFlagCharacteristic()
        result = char.decode_value(bytearray([0]))
        assert result is False

    def test_privacy_enabled(self) -> None:
        """Test privacy flag enabled."""
        char = PeripheralPrivacyFlagCharacteristic()
        result = char.decode_value(bytearray([1]))
        assert result is True

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = PeripheralPrivacyFlagCharacteristic()
        for value in [False, True]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value
