"""Tests for TimeExponential8 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeExponential8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeExponential8Characteristic(CommonCharacteristicTests):
    """Test suite for TimeExponential8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeExponential8Characteristic:
        """Provide TimeExponential8 characteristic."""
        return TimeExponential8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeExponential8."""
        return "2B13"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeExponential8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([64]),
                expected_value=datetime.timedelta(seconds=1),
                description="1.1^(64-64) = 1.0 second",
            ),
            CharacteristicTestData(
                input_data=bytearray([74]),
                expected_value=datetime.timedelta(seconds=1.1**10),
                description="1.1^(74-64) = 1.1^10 seconds",
            ),
        ]
