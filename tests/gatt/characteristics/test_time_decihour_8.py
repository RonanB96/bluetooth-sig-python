"""Tests for TimeDecihour8 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeDecihour8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeDecihour8Characteristic(CommonCharacteristicTests):
    """Test suite for TimeDecihour8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeDecihour8Characteristic:
        """Provide TimeDecihour8 characteristic."""
        return TimeDecihour8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeDecihour8."""
        return "2B12"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeDecihour8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([10]),
                expected_value=datetime.timedelta(seconds=3600),
                description="10 decihours = 1 hour",
            ),
            CharacteristicTestData(
                input_data=bytearray([1]),
                expected_value=datetime.timedelta(seconds=360),
                description="1 decihour = 6 min",
            ),
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=datetime.timedelta(seconds=36000),
                description="100 decihours = 10 hours",
            ),
        ]
