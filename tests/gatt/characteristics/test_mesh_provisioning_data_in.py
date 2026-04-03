"""Tests for MeshProvisioningDataInCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.mesh_provisioning_data_in import (
    MeshProvisioningDataInCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMeshProvisioningDataInCharacteristic(CommonCharacteristicTests):
    """Test Mesh Provisioning Data In characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> MeshProvisioningDataInCharacteristic:
        return MeshProvisioningDataInCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ADB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte provisioning PDU",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x01, 0x00, 0x01, 0x00, 0x00]),
                expected_value=b"\x03\x01\x00\x01\x00\x00",
                description="Multi-byte provisioning PDU",
            ),
        ]
