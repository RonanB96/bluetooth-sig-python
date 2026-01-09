"""Tests for Alert Category ID Bit Mask characteristic (0x2A42)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.alert_category_id_bit_mask import AlertCategoryIdBitMaskCharacteristic
from bluetooth_sig.types import AlertCategoryBitMask
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAlertCategoryIdBitMaskCharacteristic(CommonCharacteristicTests):
    """Test suite for Alert Category ID Bit Mask characteristic."""

    @pytest.fixture
    def characteristic(self) -> AlertCategoryIdBitMaskCharacteristic:
        """Return an Alert Category ID Bit Mask characteristic instance."""
        return AlertCategoryIdBitMaskCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A42"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for various bit mask combinations."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x2A, 0x00]),  # Bits 1, 3, 5 set (Email, Call, SMS)
                expected_value=AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.CALL | AlertCategoryBitMask.SMS_MMS,
                description="Email + Call + SMS categories",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=AlertCategoryBitMask(0),
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
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),  # Only Simple Alert
                expected_value=AlertCategoryBitMask.SIMPLE_ALERT,
                description="Simple Alert only",
            ),
        ]

    def test_all_categories_enabled(self, characteristic: AlertCategoryIdBitMaskCharacteristic) -> None:
        """Test that all categories can be enabled."""
        all_categories = (
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
        )

        encoded = characteristic.build_value(all_categories)
        assert isinstance(encoded, bytearray)
        assert len(encoded) == 2
        assert encoded[0] == 0xFF  # Lower byte
        assert encoded[1] == 0x03  # Upper byte (bits 8-9 set)

        decoded = characteristic.parse_value(encoded)
        assert decoded == all_categories

    def test_no_categories_enabled(self, characteristic: AlertCategoryIdBitMaskCharacteristic) -> None:
        """Test that no categories enabled works."""
        no_categories = AlertCategoryBitMask(0)

        encoded = characteristic.build_value(no_categories)
        assert isinstance(encoded, bytearray)
        assert len(encoded) == 2
        assert encoded[0] == 0x00
        assert encoded[1] == 0x00

        decoded = characteristic.parse_value(encoded)
        assert decoded == no_categories

    def test_single_category(self, characteristic: AlertCategoryIdBitMaskCharacteristic) -> None:
        """Test enabling a single category."""
        single_category = AlertCategoryBitMask.SIMPLE_ALERT

        encoded = characteristic.build_value(single_category)
        assert isinstance(encoded, bytearray)
        assert len(encoded) == 2
        assert encoded[0] == 0x01  # Bit 0 set
        assert encoded[1] == 0x00

        decoded = characteristic.parse_value(encoded)
        assert decoded == single_category

    def test_roundtrip(self, characteristic: AlertCategoryIdBitMaskCharacteristic) -> None:
        """Test round-trip encoding/decoding for various combinations."""
        test_masks = [
            AlertCategoryBitMask.SIMPLE_ALERT,
            AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.CALL,
            AlertCategoryBitMask.SIMPLE_ALERT | AlertCategoryBitMask.EMAIL | AlertCategoryBitMask.NEWS,
            AlertCategoryBitMask(0xFFFF),  # All bits set (including reserved)
        ]

        for mask in test_masks:
            encoded = characteristic.build_value(mask)
            decoded = characteristic.parse_value(encoded)
            assert decoded == mask
