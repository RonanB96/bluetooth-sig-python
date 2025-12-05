"""Tests for Next DST Change Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.next_dst_change import NextDstChangeService

from .test_service_common import CommonServiceTests


class TestNextDstChangeService(CommonServiceTests):
    """Test Next DST Change Service implementation."""

    @pytest.fixture
    def service(self) -> NextDstChangeService:
        """Provide the service instance."""
        return NextDstChangeService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Next DST Change Service."""
        return "1807"
