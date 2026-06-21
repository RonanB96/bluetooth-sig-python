"""Tests for PEP 562 lazy characteristic exports."""

from __future__ import annotations

import pytest

import bluetooth_sig.gatt.characteristics as characteristics_pkg
from bluetooth_sig.gatt.characteristics._export_map import LAZY_EXPORT_MAP
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.registry_utils import ModuleDiscovery


class TestLazyCharacteristicExports:
    """Lazy export map and __getattr__ behavior."""

    def test_export_map_includes_battery_level(self) -> None:
        """Generated map must include common characteristics."""
        assert "BatteryLevelCharacteristic" in LAZY_EXPORT_MAP

    def test_lazy_getattr_resolves_class(self) -> None:
        """__getattr__ should resolve a characteristic class on demand."""
        cls = characteristics_pkg.BatteryLevelCharacteristic
        assert cls is BatteryLevelCharacteristic

    def test_lazy_getattr_caches_on_package(self) -> None:
        """Second access should use cached package attribute."""
        _ = characteristics_pkg.CO2ConcentrationCharacteristic
        from bluetooth_sig.gatt import characteristics

        assert "CO2ConcentrationCharacteristic" in characteristics.__dict__

    def test_unknown_export_raises_attribute_error(self) -> None:
        """Unknown names must raise AttributeError."""
        missing_name = "NotARealCharacteristicName"
        with pytest.raises(AttributeError, match=missing_name):
            getattr(characteristics_pkg, missing_name)

    def test_dir_includes_lazy_exports(self) -> None:
        """dir(package) should list lazy export names."""
        names = dir(characteristics_pkg)
        assert "BatteryLevelCharacteristic" in names
        assert "BaseCharacteristic" in names

    def test_eager_base_characteristic(self) -> None:
        """BaseCharacteristic remains eagerly available."""
        assert characteristics_pkg.BaseCharacteristic is BaseCharacteristic

    def test_export_map_matches_discovery(self) -> None:
        """Generated lazy export map must stay in sync with package modules."""
        discovered = ModuleDiscovery.build_lazy_export_map(
            "bluetooth_sig.gatt.characteristics",
            CharacteristicRegistry._MODULE_EXCLUSIONS,
            BaseCharacteristic,
        )
        assert discovered == LAZY_EXPORT_MAP
