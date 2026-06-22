"""Tests for Cookware Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.cookware import CookwareService  # type: ignore[import-untyped]
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestCookwareService(CommonServiceTests):
    @pytest.fixture
    def service(self) -> CookwareService:
        return CookwareService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "185D"

    def test_expected_characteristics_count(self, service: CookwareService) -> None:
        assert len(service.get_expected_characteristics()) == 9

    def test_required_characteristics_match_spec(self, service: CookwareService) -> None:
        required = service.get_required_characteristics()
        assert CharacteristicName.COOKWARE_DESCRIPTION in required
        assert CharacteristicName.COOKWARE_SENSOR_DATA in required
        assert CharacteristicName.RECIPE_CONTROL not in required
