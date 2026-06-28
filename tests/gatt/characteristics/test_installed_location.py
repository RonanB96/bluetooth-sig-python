from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.installed_location import (  # type: ignore[import-untyped]
    InstalledLocationCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestInstalledLocationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> InstalledLocationCharacteristic:
        return InstalledLocationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C34"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Kitchen"), "Kitchen", "configured location"),
            CharacteristicTestData(bytearray(), "", "not configured"),
        ]

    def test_invalid_utf8_fails(self, characteristic: InstalledLocationCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xFF]))
