"""Lifecycle tests for UuidRegistry lazy loading semantics."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.uuid_registry import UuidRegistry


class TestUuidRegistryLifecycle:
    """Validate lazy loading, single-load behaviour, and sticky failures."""

    def test_constructor_does_not_load_yaml(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Constructing registry must not trigger YAML loading."""
        calls = 0

        def _fake_load(self: UuidRegistry) -> None:
            nonlocal calls
            calls += 1

        monkeypatch.setattr(UuidRegistry, "_load_uuids", _fake_load)

        registry = UuidRegistry()

        assert calls == 0
        assert registry._loaded is False  # pylint: disable=protected-access

    def test_first_lookup_loads_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """First lookup should load once, subsequent lookups should not reload."""
        calls = 0

        def _fake_load(self: UuidRegistry) -> None:
            nonlocal calls
            calls += 1

        monkeypatch.setattr(UuidRegistry, "_load_uuids", _fake_load)
        registry = UuidRegistry()

        assert registry.get_service_info("2A19") is None
        assert registry.get_service_info("2A19") is None

        assert calls == 1
        assert registry._loaded is True  # pylint: disable=protected-access

    def test_failed_load_is_sticky(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A failed load should be surfaced deterministically and not retried implicitly."""
        calls = 0

        def _failing_load(self: UuidRegistry) -> None:
            nonlocal calls
            calls += 1
            raise FileNotFoundError("simulated missing YAML")

        monkeypatch.setattr(UuidRegistry, "_load_uuids", _failing_load)
        registry = UuidRegistry()

        with pytest.raises(RuntimeError, match="failed to load SIG data"):
            registry.get_characteristic_info("2A19")

        with pytest.raises(RuntimeError, match="failed to load SIG data"):
            registry.get_characteristic_info("2A19")

        assert calls == 1
