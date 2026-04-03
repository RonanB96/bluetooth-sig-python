"""Tests for MeshProvisioning Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.mesh_provisioning import MeshProvisioningService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestMeshProvisioningService(CommonServiceTests):
    """MeshProvisioning Service tests."""

    @pytest.fixture
    def service(self) -> MeshProvisioningService:
        """Provide the service instance."""
        return MeshProvisioningService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MeshProvisioning."""
        return "1827"

    def test_characteristics_defined(self, service: MeshProvisioningService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2

    def test_required_characteristics(self, service: MeshProvisioningService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 2
        assert CharacteristicName.MESH_PROVISIONING_DATA_IN in required
        assert CharacteristicName.MESH_PROVISIONING_DATA_OUT in required
