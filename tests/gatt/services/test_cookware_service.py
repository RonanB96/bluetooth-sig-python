"""Tests for Cookware Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services import GattServiceRegistry
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
        assert set(service.get_expected_characteristics()) == {
            CharacteristicName.COOKWARE_DESCRIPTION,
            CharacteristicName.COOKWARE_SENSOR_DATA,
            CharacteristicName.RECIPE_PARAMETERS,
            CharacteristicName.RECIPE_CONTROL,
            CharacteristicName.COOKING_STEP_STATUS,
            CharacteristicName.COOKING_ZONE_CAPABILITIES,
            CharacteristicName.COOKING_ZONE_DESIRED_COOKING_CONDITIONS,
            CharacteristicName.COOKING_ZONE_ACTUAL_COOKING_CONDITIONS,
            CharacteristicName.COOKWARE_SENSOR_AGGREGATE,
        }

    def test_required_characteristics_match_spec(self, service: CookwareService) -> None:
        assert set(service.get_required_characteristics()) == {
            CharacteristicName.COOKWARE_DESCRIPTION,
            CharacteristicName.COOKWARE_SENSOR_DATA,
        }

    def test_service_registration(self) -> None:
        assert GattServiceRegistry.get_service_class("185D") == CookwareService
