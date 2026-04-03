"""Tests for bluetooth_sig.utils.prewarm — prewarm_registries."""

from __future__ import annotations

from bluetooth_sig.utils.prewarm import prewarm_registries


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
