"""Tests for MeshProvisioningDataOutCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.mesh_provisioning_data_out import (
    MeshProvisioningDataOutCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMeshProvisioningDataOutCharacteristic(CommonCharacteristicTests):
    """Test Mesh Provisioning Data Out characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> MeshProvisioningDataOutCharacteristic:
        return MeshProvisioningDataOutCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ADC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte provisioning PDU response",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0xAA, 0xBB, 0xCC]),
                expected_value=b"\x05\xaa\xbb\xcc",
                description="Multi-byte provisioning PDU response",
            ),
        ]
