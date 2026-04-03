"""Tests for MeshProxy Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.mesh_proxy import MeshProxyService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestMeshProxyService(CommonServiceTests):
    """MeshProxy Service tests."""

    @pytest.fixture
    def service(self) -> MeshProxyService:
        """Provide the service instance."""
        return MeshProxyService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MeshProxy."""
        return "1828"

    def test_characteristics_defined(self, service: MeshProxyService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2

    def test_required_characteristics(self, service: MeshProxyService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 2
        assert CharacteristicName.MESH_PROXY_DATA_IN in required
        assert CharacteristicName.MESH_PROXY_DATA_OUT in required
