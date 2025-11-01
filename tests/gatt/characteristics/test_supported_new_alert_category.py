"""Tests for Supported New Alert Category characteristic (0x2A47)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.supported_new_alert_category import SupportedNewAlertCategoryCharacteristic
from bluetooth_sig.types import AlertCategoryBitMask
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedNewAlertCategoryCharacteristic(CommonCharacteristicTests):
    """Test suite for Supported New Alert Category characteristic."""

    @pytest.fixture
    def characteristic(self) -> SupportedNewAlertCategoryCharacteristic:
        """Return a Supported New Alert Category characteristic instance."""
        return SupportedNewAlertCategoryCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A47"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data (Email + SMS + Call categories enabled)."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x2A, 0x00]),  # Bits 1, 3, 5 set (Email, Call, SMS)
                expected_value=AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.CALL | AlertCategoryBitMask.SMS_MMS,
                description="Email + Call + SMS categories",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="No categories enabled",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x03]),  # All 10 defined bits set
                expected_value=(
                    AlertCategoryBitMask.SIMPLE_ALERT
                    | AlertCategoryBitMask.EMAIL
                    | AlertCategoryBitMask.NEWS
                    | AlertCategoryBitMask.CALL
                    | AlertCategoryBitMask.MISSED_CALL
                    | AlertCategoryBitMask.SMS_MMS
                    | AlertCategoryBitMask.VOICE_MAIL
                    | AlertCategoryBitMask.SCHEDULE
                    | AlertCategoryBitMask.HIGH_PRIORITIZED_ALERT
                    | AlertCategoryBitMask.INSTANT_MESSAGE
                ),
                description="All categories enabled",
            ),
        ]

    def test_all_categories_enabled(self, characteristic: SupportedNewAlertCategoryCharacteristic) -> None:
        """Test with all defined categories enabled."""
        data = bytearray([0xFF, 0x03])  # All 10 defined bits set
        result = characteristic.decode_value(data)
        assert result & AlertCategoryBitMask.SIMPLE_ALERT
        assert result & AlertCategoryBitMask.EMAIL
        assert result & AlertCategoryBitMask.INSTANT_MESSAGE

    def test_no_categories_enabled(self, characteristic: SupportedNewAlertCategoryCharacteristic) -> None:
        """Test with no categories enabled."""
        data = bytearray([0x00, 0x00])
        result = characteristic.decode_value(data)
        assert result == 0

    def test_roundtrip(self, characteristic: SupportedNewAlertCategoryCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.HIGH_PRIORITIZED_ALERT
        encoded = characteristic.encode_value(original)
        decoded = characteristic.decode_value(encoded)
        assert decoded == original
