"""Tests for Link Loss Service."""

import pytest

from bluetooth_sig.gatt.services.link_loss import LinkLossService

from .test_service_common import CommonServiceTests


class TestLinkLossService(CommonServiceTests):
    """Test Link Loss Service implementation."""

    @pytest.fixture
    def service(self) -> LinkLossService:
        """Provide the service instance."""
        return LinkLossService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Link Loss Service."""
        return "1803"
