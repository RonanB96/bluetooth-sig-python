"""Tests for New Alert characteristic (0x2A46)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.new_alert import NewAlertCharacteristic, NewAlertData
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types import AlertCategoryID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNewAlertCharacteristic(CommonCharacteristicTests):
    """Test suite for New Alert characteristic."""

    @pytest.fixture
    def characteristic(self) -> NewAlertCharacteristic:
        """Return a New Alert characteristic instance."""
        return NewAlertCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A46"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x03]) + b"John",
                expected_value=NewAlertData(
                    category_id=AlertCategoryID.EMAIL, number_of_new_alert=3, text_string_information="John"
                ),
                description="3 new emails from John",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x02]) + b"Alice",
                expected_value=NewAlertData(
                    category_id=AlertCategoryID.CALL, number_of_new_alert=2, text_string_information="Alice"
                ),
                description="2 new calls from Alice",
            ),
        ]

    def test_new_alert_without_text(self, characteristic: NewAlertCharacteristic) -> None:
        """Test new alert with no text information."""
        data = bytearray([0x00, 0x01])  # Simple Alert, 1 new alert, no text
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.category_id == AlertCategoryID.SIMPLE_ALERT
        assert result.number_of_new_alert == 1
        assert result.text_string_information == ""

    def test_new_alert_with_max_text(self, characteristic: NewAlertCharacteristic) -> None:
        """Test new alert with maximum 18-character text."""
        text = "A" * 18
        data = bytearray([0x03, 0x02]) + text.encode("utf-8")  # Call, 2 alerts, 18 chars
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.category_id == AlertCategoryID.CALL
        assert result.number_of_new_alert == 2
        assert result.text_string_information == text

    def test_new_alert_text_too_long(self, characteristic: NewAlertCharacteristic) -> None:
        """Test that text longer than 18 characters is rejected."""
        text = "A" * 19
        data = bytearray([0x01, 0x01]) + text.encode("utf-8")
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data)
        assert "text string too long" in str(exc_info.value).lower()

    def test_invalid_category_id(self, characteristic: NewAlertCharacteristic) -> None:
        """Test that invalid category IDs are rejected."""
        data = bytearray([0x0A, 0x01])  # 10 is reserved
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data)
        assert "alertcategoryid" in str(exc_info.value).lower()

    def test_roundtrip(self, characteristic: NewAlertCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = NewAlertData(
            category_id=AlertCategoryID.SMS_MMS, number_of_new_alert=5, text_string_information="Alice"
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded is not None
        assert decoded.category_id == original.category_id
        assert decoded.number_of_new_alert == original.number_of_new_alert
        assert decoded.text_string_information == original.text_string_information
