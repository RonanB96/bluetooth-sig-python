"""Tests for MeshProxySolicitation Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.mesh_proxy_solicitation import MeshProxySolicitationService

from .test_service_common import CommonServiceTests


class TestMeshProxySolicitationService(CommonServiceTests):
    """MeshProxySolicitation Service tests."""

    @pytest.fixture
    def service(self) -> MeshProxySolicitationService:
        """Provide the service instance."""
        return MeshProxySolicitationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MeshProxySolicitation."""
        return "1859"

    def test_characteristics_defined(self, service: MeshProxySolicitationService) -> None:
        """Test that this advertisement-only service has no characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 0
