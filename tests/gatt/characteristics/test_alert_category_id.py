"""Tests for Alert Category ID characteristic (0x2A43)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.alert_category_id import AlertCategoryIdCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types import AlertCategoryID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAlertCategoryIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Alert Category ID characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds alert category-specific edge cases and enum validation.
    """

    @pytest.fixture
    def characteristic(self) -> AlertCategoryIdCharacteristic:
        """Return an Alert Category ID characteristic instance."""
        return AlertCategoryIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Alert Category ID characteristic."""
        return "2A43"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for all alert categories."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]), expected_value=AlertCategoryID.SIMPLE_ALERT, description="Simple Alert"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]), expected_value=AlertCategoryID.EMAIL, description="Email"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]), expected_value=AlertCategoryID.NEWS, description="News"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]), expected_value=AlertCategoryID.CALL, description="Call"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]), expected_value=AlertCategoryID.MISSED_CALL, description="Missed Call"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]), expected_value=AlertCategoryID.SMS_MMS, description="SMS/MMS"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06]), expected_value=AlertCategoryID.VOICE_MAIL, description="Voice Mail"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07]), expected_value=AlertCategoryID.SCHEDULE, description="Schedule"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08]),
                expected_value=AlertCategoryID.HIGH_PRIORITIZED_ALERT,
                description="High Priority",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x09]), expected_value=AlertCategoryID.INSTANT_MESSAGE, description="Instant Msg"
            ),
        ]

    def test_alert_category_id_reserved_values_rejected(self, characteristic: AlertCategoryIdCharacteristic) -> None:
        """Test that reserved values (0x0A-0xFA) are rejected."""
        # Test reserved value 0x0A
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x0A]))
        assert "reserved" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

        # Test higher reserved value 0xFA
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0xFA]))
        assert "reserved" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_alert_category_id_service_specific_values_accepted(
        self, characteristic: AlertCategoryIdCharacteristic
    ) -> None:
        """Test that service-specific values (0xFB-0xFF) are accepted."""
        # Test service-specific value 0xFB
        result = characteristic.parse_value(bytearray([0xFB]))

        assert result == AlertCategoryID.SIMPLE_ALERT  # Should map to SIMPLE_ALERT

        # Test service-specific value 0xFF
        result = characteristic.parse_value(bytearray([0xFF]))

        assert result == AlertCategoryID.SIMPLE_ALERT  # Should map to SIMPLE_ALERT

    @pytest.mark.parametrize("enum_value", list(AlertCategoryID))
    def test_alert_category_id_encoding_enum(
        self, characteristic: AlertCategoryIdCharacteristic, enum_value: AlertCategoryID
    ) -> None:
        """Test encoding AlertCategoryID enum values."""
        encoded = characteristic.build_value(enum_value)
        assert isinstance(encoded, bytearray)
        assert len(encoded) == 1
        assert encoded[0] == enum_value.value

    @pytest.mark.parametrize("int_value", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    def test_alert_category_id_encoding_int(
        self, characteristic: AlertCategoryIdCharacteristic, int_value: int
    ) -> None:
        """Test encoding integer values."""
        encoded = characteristic.build_value(int_value)
        assert isinstance(encoded, bytearray)
        assert len(encoded) == 1
        assert encoded[0] == int_value

    def test_alert_category_id_roundtrip(self, characteristic: AlertCategoryIdCharacteristic) -> None:
        """Test round-trip encoding/decoding."""
        for category in AlertCategoryID:
            encoded = characteristic.build_value(category)
            decoded = characteristic.parse_value(encoded)
            assert decoded == category

    def test_alert_category_id_enum_values(self, characteristic: AlertCategoryIdCharacteristic) -> None:
        """Test that all enum values are properly handled."""
        for category in AlertCategoryID:
            encoded = characteristic.build_value(category)
            decoded = characteristic.parse_value(encoded)
            assert decoded == category
            assert isinstance(decoded, AlertCategoryID)
