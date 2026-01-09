"""Tests for Unread Alert Status characteristic (0x2A45)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.unread_alert_status import (
    UnreadAlertStatusCharacteristic,
    UnreadAlertStatusData,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types import AlertCategoryID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUnreadAlertStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for Unread Alert Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> UnreadAlertStatusCharacteristic:
        """Return an Unread Alert Status characteristic instance."""
        return UnreadAlertStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A45"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x0A]),  # Email, 10 unread
                expected_value=UnreadAlertStatusData(category_id=AlertCategoryID.EMAIL, unread_count=10),
                description="10 unread emails",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x03]),  # Missed Call, 3 unread
                expected_value=UnreadAlertStatusData(category_id=AlertCategoryID.MISSED_CALL, unread_count=3),
                description="3 missed calls",
            ),
        ]

    def test_zero_unread(self, characteristic: UnreadAlertStatusCharacteristic) -> None:
        """Test with zero unread alerts."""
        data = bytearray([0x05, 0x00])  # SMS/MMS, 0 unread
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.category_id == AlertCategoryID.SMS_MMS
        assert result.unread_count == 0

    def test_max_unread_count(self, characteristic: UnreadAlertStatusCharacteristic) -> None:
        """Test with 255 (more than 254 unread)."""
        data = bytearray([0x04, 0xFF])  # Missed Call, 255 (>254)
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.category_id == AlertCategoryID.MISSED_CALL
        assert result.unread_count == 255

    def test_invalid_category_id(self, characteristic: UnreadAlertStatusCharacteristic) -> None:
        """Test that invalid category IDs are rejected."""
        data = bytearray([0x0A, 0x05])  # 10 is reserved
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data)
        assert "alertcategoryid" in str(exc_info.value).lower()

    def test_roundtrip(self, characteristic: UnreadAlertStatusCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = UnreadAlertStatusData(category_id=AlertCategoryID.VOICE_MAIL, unread_count=3)
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded is not None
        assert decoded.category_id == original.category_id
        assert decoded.unread_count == original.unread_count
