"""Tests for Supported Unread Alert Category characteristic (0x2A48)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.supported_unread_alert_category import (
    SupportedUnreadAlertCategoryCharacteristic,
)
from bluetooth_sig.types import AlertCategoryBitMask
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedUnreadAlertCategoryCharacteristic(CommonCharacteristicTests):
    """Test suite for Supported Unread Alert Category characteristic."""

    @pytest.fixture
    def characteristic(self) -> SupportedUnreadAlertCategoryCharacteristic:
        """Return a Supported Unread Alert Category characteristic instance."""
        return SupportedUnreadAlertCategoryCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A48"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00]),  # Bit 1 set (Email)
                expected_value=AlertCategoryBitMask.EMAIL,
                description="Email category only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00]),  # Bits 1, 3 set (Email, Call)
                expected_value=AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.CALL,
                description="Email + Call categories",
            ),
        ]

    def test_single_category(self, characteristic: SupportedUnreadAlertCategoryCharacteristic) -> None:
        """Test with single category enabled."""
        data = bytearray([0x01, 0x00])  # Bit 0 set (Simple Alert)
        result = characteristic.parse_value(data)
        assert result is not None
        assert result == AlertCategoryBitMask.SIMPLE_ALERT

    def test_all_categories(self, characteristic: SupportedUnreadAlertCategoryCharacteristic) -> None:
        """Test with all categories enabled."""
        data = bytearray([0xFF, 0x03])
        result = characteristic.parse_value(data)
        assert result is not None
        assert result & AlertCategoryBitMask.NEWS
        assert result & AlertCategoryBitMask.SCHEDULE

    def test_single_byte_data(self, characteristic: SupportedUnreadAlertCategoryCharacteristic) -> None:
        """Test decoding 1-byte data (only lower 8 category bits)."""
        data = bytearray([0x02])  # Bit 1 (Email)
        result = characteristic.parse_value(data)
        assert result is not None
        assert result == AlertCategoryBitMask.EMAIL

    def test_single_byte_multiple_categories(self, characteristic: SupportedUnreadAlertCategoryCharacteristic) -> None:
        """Test 1-byte data with multiple categories."""
        data = bytearray([0xC1])  # Bits 0, 6, 7 (Simple Alert, Voice Mail, Schedule)
        result = characteristic.parse_value(data)
        assert result is not None
        expected = AlertCategoryBitMask.SIMPLE_ALERT | AlertCategoryBitMask.VOICE_MAIL | AlertCategoryBitMask.SCHEDULE
        assert result == expected
