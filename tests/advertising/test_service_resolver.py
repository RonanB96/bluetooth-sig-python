"""Tests for AdvertisingServiceResolver."""

from __future__ import annotations

from bluetooth_sig.advertising.service_resolver import (
    AdvertisingServiceResolver,
    ResolvedService,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class TestResolvedService:
    """Tests for ResolvedService class."""

    def test_with_known_service(self) -> None:
        """Test ResolvedService with a known service class."""
        from bluetooth_sig.gatt.services.battery_service import BatteryService

        uuid = BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb")
        resolved = ResolvedService(
            uuid=uuid,
            service_class=BatteryService,
            name="BatteryService",
            is_sig_defined=True,
        )

        assert resolved.uuid == uuid
        assert resolved.service_class is BatteryService
        assert resolved.name == "BatteryService"
        assert resolved.is_sig_defined is True

    def test_with_unknown_service(self) -> None:
        """Test ResolvedService with an unknown service."""
        uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        resolved = ResolvedService(
            uuid=uuid,
            service_class=None,
            name="Unknown Service",
            is_sig_defined=False,
        )

        assert resolved.uuid == uuid
        assert resolved.service_class is None
        assert resolved.name == "Unknown Service"
        assert resolved.is_sig_defined is False

    def test_repr(self) -> None:
        """Test string representation."""
        uuid = BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb")
        resolved = ResolvedService(
            uuid=uuid,
            service_class=None,
            name="Test",
            is_sig_defined=False,
        )

        repr_str = repr(resolved)
        assert "ResolvedService" in repr_str
        assert "uuid=" in repr_str
        assert "name='Test'" in repr_str


class TestAdvertisingServiceResolver:
    """Tests for AdvertisingServiceResolver."""

    def test_resolve_known_service(self) -> None:
        """Test resolving a known SIG service UUID."""
        resolver = AdvertisingServiceResolver()

        # Battery Service UUID
        uuid = BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb")
        resolved = resolver.resolve(uuid)

        assert resolved.uuid == uuid
        assert resolved.service_class is not None
        assert resolved.is_sig_defined is True

    def test_resolve_unknown_service(self) -> None:
        """Test resolving an unknown UUID."""
        resolver = AdvertisingServiceResolver()

        # Custom/unknown UUID
        uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        resolved = resolver.resolve(uuid)

        assert resolved.uuid == uuid
        assert resolved.service_class is None
        assert resolved.is_sig_defined is False
        assert "Unknown" in resolved.name

    def test_resolve_string_uuid(self) -> None:
        """Test resolving with string UUID."""
        resolver = AdvertisingServiceResolver()

        # Pass string instead of BluetoothUUID
        resolved = resolver.resolve("0000180f-0000-1000-8000-00805f9b34fb")

        assert resolved.service_class is not None

    def test_resolve_all(self) -> None:
        """Test resolving multiple UUIDs."""
        resolver = AdvertisingServiceResolver()

        uuids = [
            BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"),  # Battery Service
            BluetoothUUID("12345678-1234-1234-1234-123456789abc"),  # Unknown
        ]

        results = resolver.resolve_all(uuids)

        assert len(results) == 2
        assert results[0].service_class is not None  # Battery known
        assert results[1].service_class is None  # Custom unknown

    def test_resolve_all_string_uuids(self) -> None:
        """Test resolving multiple string UUIDs."""
        resolver = AdvertisingServiceResolver()

        uuids = [
            "0000180f-0000-1000-8000-00805f9b34fb",
            "12345678-1234-1234-1234-123456789abc",
        ]

        results = resolver.resolve_all(uuids)
        assert len(results) == 2

    def test_get_known_services(self) -> None:
        """Test filtering to only known services."""
        resolver = AdvertisingServiceResolver()

        uuids = [
            BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"),  # Battery - known
            BluetoothUUID("12345678-1234-1234-1234-123456789abc"),  # Unknown
        ]

        known = resolver.get_known_services(uuids)

        assert len(known) == 1
        assert known[0].service_class is not None

    def test_get_sig_services(self) -> None:
        """Test filtering to only SIG-defined services."""
        resolver = AdvertisingServiceResolver()

        uuids = [
            BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"),  # Battery - SIG
            BluetoothUUID("12345678-1234-1234-1234-123456789abc"),  # Custom
        ]

        sig_services = resolver.get_sig_services(uuids)

        # Should only include SIG-defined services
        assert all(s.is_sig_defined for s in sig_services)

    def test_empty_list(self) -> None:
        """Test resolving empty list."""
        resolver = AdvertisingServiceResolver()

        results = resolver.resolve_all([])
        assert results == []

        known = resolver.get_known_services([])
        assert known == []

        sig = resolver.get_sig_services([])
        assert sig == []
