"""Tests for Email Address characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import EmailAddressCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEmailAddressCharacteristic(CommonCharacteristicTests):
    """Test suite for Email Address characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds email address-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> EmailAddressCharacteristic:
        """Return an Email Address characteristic instance."""
        return EmailAddressCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Email Address characteristic."""
        return "2A87"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for email address."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"user@example.com"), expected_value="user@example.com", description="Simple email"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"test.email@domain.org"),
                expected_value="test.email@domain.org",
                description="Email with subdomain",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"name+tag@gmail.com"),
                expected_value="name+tag@gmail.com",
                description="Email with plus addressing",
            ),
        ]

    # === Email Address-Specific Tests ===

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "test.email@domain.org",
            "name+tag@gmail.com",
            "user_name@company.co.uk",
        ],
    )
    def test_email_values(self, characteristic: EmailAddressCharacteristic, email: str) -> None:
        """Test email address with various valid values."""
        data = bytearray(email.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == email

    def test_email_empty(self, characteristic: EmailAddressCharacteristic) -> None:
        """Test empty email address."""
        result = characteristic.decode_value(bytearray())
        assert result == ""

    def test_email_unicode(self, characteristic: EmailAddressCharacteristic) -> None:
        """Test email address with unicode characters."""
        email = "tëst@example.com"
        data = bytearray(email.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == email
