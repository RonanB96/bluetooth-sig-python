"""Tests for device-related data types."""

from __future__ import annotations

from unittest.mock import Mock

from bluetooth_sig.types.device_types import DeviceEncryption, DeviceService


class TestDeviceService:
    """Test DeviceService dataclass."""

    def test_device_service_creation(self) -> None:
        """Test creation of DeviceService with mock service."""
        mock_service = Mock()
        mock_service.service_name = "Battery Service"
        mock_characteristic = Mock()

        device_service = DeviceService(service=mock_service, characteristics={"battery_level": mock_characteristic})

        assert device_service.service == mock_service
        assert device_service.characteristics == {"battery_level": mock_characteristic}

    def test_device_service_default_characteristics(self) -> None:
        """Test DeviceService with default empty characteristics."""
        mock_service = Mock()

        device_service = DeviceService(service=mock_service)

        assert device_service.service == mock_service
        assert device_service.characteristics == {}


class TestDeviceEncryption:
    """Test DeviceEncryption dataclass."""

    def test_device_encryption_creation_minimal(self) -> None:
        """Test creation of DeviceEncryption with minimal parameters."""
        encryption = DeviceEncryption()

        assert encryption.requires_authentication is False
        assert encryption.requires_encryption is False
        assert encryption.encryption_level == ""
        assert encryption.security_mode == 0
        assert encryption.key_size == 0

    def test_device_encryption_creation_full(self) -> None:
        """Test creation of DeviceEncryption with all parameters."""
        encryption = DeviceEncryption(
            requires_authentication=True,
            requires_encryption=True,
            encryption_level="AES-CCM",
            security_mode=1,
            key_size=128,
        )

        assert encryption.requires_authentication is True
        assert encryption.requires_encryption is True
        assert encryption.encryption_level == "AES-CCM"
        assert encryption.security_mode == 1
        assert encryption.key_size == 128

    def test_device_encryption_partial_config(self) -> None:
        """Test DeviceEncryption with partial configuration."""
        encryption = DeviceEncryption(requires_authentication=True, security_mode=2)

        assert encryption.requires_authentication is True
        assert encryption.requires_encryption is False  # default
        assert encryption.encryption_level == ""  # default
        assert encryption.security_mode == 2
        assert encryption.key_size == 0  # default
