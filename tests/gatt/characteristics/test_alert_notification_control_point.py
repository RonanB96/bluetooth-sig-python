"""Tests for Alert Notification Control Point characteristic (0x2A44)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.alert_notification_control_point import (
    AlertNotificationControlPointCharacteristic,
    AlertNotificationControlPointData,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types import AlertCategoryID, AlertNotificationCommandID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAlertNotificationControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Alert Notification Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> AlertNotificationControlPointCharacteristic:
        """Return an Alert Notification Control Point characteristic instance."""
        return AlertNotificationControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID."""
        return "2A44"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data (Enable new email alerts)."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]),  # Enable New Alert, Email category
                expected_value=AlertNotificationControlPointData(
                    command_id=AlertNotificationCommandID.ENABLE_NEW_ALERT, category_id=AlertCategoryID.EMAIL
                ),
                description="Enable new email alerts",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x03]),  # Notify New Alert Immediately, Call category
                expected_value=AlertNotificationControlPointData(
                    command_id=AlertNotificationCommandID.NOTIFY_NEW_ALERT_IMMEDIATELY, category_id=AlertCategoryID.CALL
                ),
                description="Notify new call alerts immediately",
            ),
        ]

    @pytest.mark.parametrize(
        "command_id,expected_enum",
        [
            (0, AlertNotificationCommandID.ENABLE_NEW_ALERT),
            (1, AlertNotificationCommandID.ENABLE_UNREAD_STATUS),
            (2, AlertNotificationCommandID.DISABLE_NEW_ALERT),
            (3, AlertNotificationCommandID.DISABLE_UNREAD_STATUS),
            (4, AlertNotificationCommandID.NOTIFY_NEW_ALERT_IMMEDIATELY),
            (5, AlertNotificationCommandID.NOTIFY_UNREAD_STATUS_IMMEDIATELY),
        ],
    )
    def test_all_command_ids(
        self,
        characteristic: AlertNotificationControlPointCharacteristic,
        command_id: int,
        expected_enum: AlertNotificationCommandID,
    ) -> None:
        """Test all valid command IDs."""
        data = bytearray([command_id, 0x00])
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.command_id == expected_enum

    def test_invalid_command_id(self, characteristic: AlertNotificationControlPointCharacteristic) -> None:
        """Test that invalid command IDs are rejected."""
        data = bytearray([0x06, 0x00])  # 6 is reserved
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data)
        assert "6 is not a valid AlertNotificationCommandID" in str(exc_info.value)

    def test_invalid_category_id(self, characteristic: AlertNotificationControlPointCharacteristic) -> None:
        """Test that invalid category IDs are rejected."""
        data = bytearray([0x00, 0x0A])  # 10 is reserved
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data)
        assert "10 is not a valid AlertCategoryID" in str(exc_info.value)

    def test_notify_immediately_command(self, characteristic: AlertNotificationControlPointCharacteristic) -> None:
        """Test notify immediately command."""
        data = bytearray([0x04, 0x03])  # Notify New Alert Immediately, Call category
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.command_id == AlertNotificationCommandID.NOTIFY_NEW_ALERT_IMMEDIATELY
        assert result.category_id == AlertCategoryID.CALL

    def test_roundtrip(self, characteristic: AlertNotificationControlPointCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = AlertNotificationControlPointData(
            command_id=AlertNotificationCommandID.DISABLE_UNREAD_STATUS, category_id=AlertCategoryID.SMS_MMS
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded is not None
        assert decoded.command_id == original.command_id
        assert decoded.category_id == original.category_id
