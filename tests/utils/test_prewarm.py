"""Tests for bluetooth_sig.utils.prewarm — prewarm_registries."""

from __future__ import annotations

from bluetooth_sig.gatt.uuid_registry import get_uuid_registry
from bluetooth_sig.utils.prewarm import prewarm_registries
from bluetooth_sig.utils.prewarm_catalog import get_prewarm_loaders


class TestPrewarmRegistries:
    """Tests for prewarm_registries()."""

    def test_prewarm_runs_without_error(self) -> None:
        """Calling prewarm_registries should not raise."""
        prewarm_registries()

    def test_prewarm_is_idempotent(self) -> None:
        """Calling prewarm_registries twice should not raise."""
        prewarm_registries()
        prewarm_registries()

    def test_registries_populated_after_prewarm(self) -> None:
        """After pre-warming, characteristic and service registries are populated."""
        from bluetooth_sig.gatt.characteristics.registry import (
            CharacteristicRegistry,
        )
        from bluetooth_sig.gatt.services.registry import GattServiceRegistry

        prewarm_registries()

        chars = CharacteristicRegistry.get_all_characteristics()
        assert len(chars) > 0

        services = GattServiceRegistry.get_all_services()
        assert len(services) > 0

    def test_prewarm_catalogue_contains_uuid_registry(self) -> None:
        """Prewarm catalogue must include UUID metadata hub warmup."""
        loader_names = {name for name, _ in get_prewarm_loaders()}
        assert "uuid_registry" in loader_names

    def test_prewarm_loads_uuid_registry(self) -> None:
        """Pre-warming must load UUID registry metadata."""
        prewarm_registries()
        info = get_uuid_registry().get_characteristic_info("2A19")
        assert info is not None
