"""Tests for HttpProxy Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.http_proxy import HttpProxyService

from .test_service_common import CommonServiceTests


class TestHttpProxyService(CommonServiceTests):
    """HttpProxy Service tests."""

    @pytest.fixture
    def service(self) -> HttpProxyService:
        """Provide the service instance."""
        return HttpProxyService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for HttpProxy."""
        return "1823"

    def test_characteristics_defined(self, service: HttpProxyService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6
