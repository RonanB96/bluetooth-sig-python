"""Tests for MeshProxyDataOutCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.mesh_proxy_data_out import (
    MeshProxyDataOutCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMeshProxyDataOutCharacteristic(CommonCharacteristicTests):
    """Test Mesh Proxy Data Out characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> MeshProxyDataOutCharacteristic:
        return MeshProxyDataOutCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ADE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte proxy PDU response",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0xFF, 0x7E]),
                expected_value=b"\x00\xff\x7e",
                description="Multi-byte proxy PDU response",
            ),
        ]
