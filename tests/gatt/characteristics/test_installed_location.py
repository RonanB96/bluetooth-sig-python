from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.installed_location import (  # type: ignore[import-untyped]
    InstalledLocationCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

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
            CharacteristicTestData(bytearray([0x00]), 0, "unknown"),
            CharacteristicTestData(bytearray([0x05]), 5, "generic location 5"),
        ]

    def test_empty_payload_fails(self, characteristic: InstalledLocationCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_build_out_of_range_fails(self, characteristic: InstalledLocationCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(300)
