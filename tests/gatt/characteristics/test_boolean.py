"""Tests for Boolean characteristic (0x2AE2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BooleanCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBooleanCharacteristic(CommonCharacteristicTests):
    """Test suite for Boolean characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds boolean-specific validation.
    """

    @pytest.fixture
    def characteristic(self) -> BooleanCharacteristic:
        """Return a Boolean characteristic instance."""
        return BooleanCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Boolean characteristic."""
        return "2AE2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for boolean."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=False, description="False (0)"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=True, description="True (1)"),
        ]

    def test_false_value(self) -> None:
        """Test decoding False value."""
        char = BooleanCharacteristic()
        result = char.decode_value(bytearray([0]))
        assert result is False
        assert isinstance(result, bool)

    def test_true_value(self) -> None:
        """Test decoding True value."""
        char = BooleanCharacteristic()
        result = char.decode_value(bytearray([1]))
        assert result is True
        assert isinstance(result, bool)

    def test_encode_false(self) -> None:
        """Test encoding False value."""
        char = BooleanCharacteristic()
        encoded = char.encode_value(False)
        assert encoded == bytearray([0])

    def test_encode_true(self) -> None:
        """Test encoding True value."""
        char = BooleanCharacteristic()
        encoded = char.encode_value(True)
        assert encoded == bytearray([1])

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = BooleanCharacteristic()
        for value in [False, True]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value
