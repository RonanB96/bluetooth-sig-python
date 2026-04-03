"""Tests for AP Sync Key Material characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ap_sync_key_material import (
    APSyncKeyMaterialCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAPSyncKeyMaterialCharacteristic(CommonCharacteristicTests):
    """Test suite for AP Sync Key Material characteristic."""

    @pytest.fixture
    def characteristic(self) -> APSyncKeyMaterialCharacteristic:
        return APSyncKeyMaterialCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x00" * 16),
                expected_value=b"\x00" * 16,
                description="All zeros key material",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf0"),
                expected_value=(b"\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf0"),
                description="Descending byte key material",
            ),
        ]
