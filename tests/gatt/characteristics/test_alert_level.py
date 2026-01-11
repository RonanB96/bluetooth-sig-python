"""Tests for Alert Level characteristic (0x2A06)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.alert_level import AlertLevel, AlertLevelCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAlertLevelCharacteristic(CommonCharacteristicTests):
    """Test suite for Alert Level characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds alert-specific edge cases and enum validation.
    """

    @pytest.fixture
    def characteristic(self) -> AlertLevelCharacteristic:
        """Return an Alert Level characteristic instance."""
        return AlertLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Alert Level characteristic."""
        return "2A06"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for all alert levels."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]), expected_value=AlertLevel.NO_ALERT, description="No Alert"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]), expected_value=AlertLevel.MILD_ALERT, description="Mild Alert"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]), expected_value=AlertLevel.HIGH_ALERT, description="High Alert"
            ),
        ]

    def test_alert_level_reserved_values_rejected(self, characteristic: AlertLevelCharacteristic) -> None:
        """Test that reserved values (0x03-0xFF) are rejected."""
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        # Test reserved value 0x03
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x03]))
        assert "reserved" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

        # Test higher reserved value 0xFF
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0xFF]))
        assert "reserved" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "alert_level",
        [AlertLevel.NO_ALERT, AlertLevel.MILD_ALERT, AlertLevel.HIGH_ALERT],
    )
    def test_alert_level_encoding_enum(self, characteristic: AlertLevelCharacteristic, alert_level: AlertLevel) -> None:
        """Test encoding alert levels from enum values."""
        encoded = characteristic.build_value(alert_level)
        assert len(encoded) == 1
        assert encoded[0] == alert_level.value

    @pytest.mark.parametrize(
        "alert_int",
        [0, 1, 2],
    )
    def test_alert_level_encoding_int(self, characteristic: AlertLevelCharacteristic, alert_int: int) -> None:
        """Test encoding alert levels from integer values."""
        encoded = characteristic.build_value(alert_int)
        assert len(encoded) == 1
        assert encoded[0] == alert_int

    def test_alert_level_roundtrip(self, characteristic: AlertLevelCharacteristic) -> None:
        """Test that encode/decode are inverse operations."""
        for level in [AlertLevel.NO_ALERT, AlertLevel.MILD_ALERT, AlertLevel.HIGH_ALERT]:
            encoded = characteristic.build_value(level)
            result = characteristic.parse_value(encoded)
            assert result == level

    def test_alert_level_enum_values(self) -> None:
        """Test AlertLevel enum has correct values per spec."""
        assert AlertLevel.NO_ALERT.value == 0x00
        assert AlertLevel.MILD_ALERT.value == 0x01
        assert AlertLevel.HIGH_ALERT.value == 0x02
