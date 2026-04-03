"""Tests for MeshProxyDataInCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.mesh_proxy_data_in import (
    MeshProxyDataInCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMeshProxyDataInCharacteristic(CommonCharacteristicTests):
    """Test Mesh Proxy Data In characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> MeshProxyDataInCharacteristic:
        return MeshProxyDataInCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ADD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=b"\x00",
                description="Single byte proxy PDU",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x10, 0x20, 0x30, 0x40]),
                expected_value=b"\x02\x10\x20\x30\x40",
                description="Multi-byte proxy PDU",
            ),
        ]
