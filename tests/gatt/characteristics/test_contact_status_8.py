"""Tests for ContactStatus8 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ContactStatus8Characteristic
from bluetooth_sig.gatt.characteristics.contact_status_8 import ContactStatus
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestContactStatus8Characteristic(CommonCharacteristicTests):
    """Test suite for ContactStatus8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> ContactStatus8Characteristic:
        """Provide ContactStatus8 characteristic."""
        return ContactStatus8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ContactStatus8."""
        return "2C22"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for ContactStatus8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=ContactStatus(0),
                description="no contacts",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=ContactStatus.CONTACT_0 | ContactStatus.CONTACT_1,
                description="contacts 0+1",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=ContactStatus.CONTACT_0
                | ContactStatus.CONTACT_1
                | ContactStatus.CONTACT_2
                | ContactStatus.CONTACT_3
                | ContactStatus.CONTACT_4
                | ContactStatus.CONTACT_5
                | ContactStatus.CONTACT_6
                | ContactStatus.CONTACT_7,
                description="all contacts",
            ),
        ]
