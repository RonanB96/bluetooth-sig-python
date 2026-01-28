"""Tests for advertising state classes."""

from __future__ import annotations

from bluetooth_sig.advertising.state import (
    DeviceAdvertisingState,
    EncryptionState,
    PacketState,
)


class TestEncryptionState:
    """Tests for EncryptionState struct."""

    def test_default_values(self) -> None:
        """Test default values are correct."""
        state = EncryptionState()
        assert state.bindkey is None
        assert state.bindkey_verified is False
        assert state.encryption_counter == 0
        assert state.decryption_failed is False

    def test_with_bindkey(self) -> None:
        """Test setting bindkey."""
        key = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")
        state = EncryptionState(bindkey=key)
        assert state.bindkey == key
        assert state.bindkey_verified is False

    def test_mutable(self) -> None:
        """Test state is mutable."""
        state = EncryptionState()
        state.bindkey_verified = True
        state.encryption_counter = 42
        assert state.bindkey_verified is True
        assert state.encryption_counter == 42


class TestPacketState:
    """Tests for PacketState struct."""

    def test_default_values(self) -> None:
        """Test default values are correct."""
        state = PacketState()
        assert state.packet_id is None
        assert state.last_seen_timestamp == 0.0
        assert state.last_service_data_hash is None

    def test_with_values(self) -> None:
        """Test setting values."""
        state = PacketState(
            packet_id=123,
            last_seen_timestamp=1234567890.5,
            last_service_data_hash=0xDEADBEEF,
        )
        assert state.packet_id == 123
        assert state.last_seen_timestamp == 1234567890.5
        assert state.last_service_data_hash == 0xDEADBEEF

    def test_mutable(self) -> None:
        """Test state is mutable."""
        state = PacketState()
        state.packet_id = 99
        assert state.packet_id == 99


class TestDeviceAdvertisingState:
    """Tests for DeviceAdvertisingState struct."""

    def test_default_values(self) -> None:
        """Test default values are correct."""
        state = DeviceAdvertisingState()
        assert state.address == ""
        assert isinstance(state.encryption, EncryptionState)
        assert isinstance(state.packets, PacketState)
        assert state.device_type is None
        assert state.protocol_version is None
        assert state.is_sleepy_device is False

    def test_with_address(self) -> None:
        """Test setting address."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        assert state.address == "AA:BB:CC:DD:EE:FF"

    def test_nested_state_access(self) -> None:
        """Test accessing nested encryption state."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        key = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")
        state.encryption.bindkey = key
        state.encryption.encryption_counter = 100
        assert state.encryption.bindkey == key
        assert state.encryption.encryption_counter == 100

    def test_device_type_and_protocol(self) -> None:
        """Test setting device type and protocol version."""
        state = DeviceAdvertisingState(
            device_type="BTHome sensor",
            protocol_version="v2",
        )
        assert state.device_type == "BTHome sensor"
        assert state.protocol_version == "v2"

    def test_sleepy_device_flag(self) -> None:
        """Test sleepy device flag."""
        state = DeviceAdvertisingState(is_sleepy_device=True)
        assert state.is_sleepy_device is True


class TestStateIntegration:
    """Integration tests for state management."""

    def test_full_state_lifecycle(self) -> None:
        """Test full state lifecycle: create, update, verify."""
        # Create initial state
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        # Simulate bindkey being set
        key = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")
        state.encryption.bindkey = key

        # Simulate first successful decryption
        state.encryption.bindkey_verified = True
        state.encryption.encryption_counter = 1
        state.packets.packet_id = 1
        state.packets.last_seen_timestamp = 1234567890.0
        state.device_type = "BTHome sensor"
        state.protocol_version = "v2"

        # Verify all state
        assert state.encryption.bindkey == key
        assert state.encryption.bindkey_verified is True
        assert state.encryption.encryption_counter == 1
        assert state.packets.packet_id == 1
        assert state.packets.last_seen_timestamp == 1234567890.0
        assert state.device_type == "BTHome sensor"
        assert state.protocol_version == "v2"

        # Simulate second advertisement
        state.encryption.encryption_counter = 2
        state.packets.packet_id = 2
        state.packets.last_seen_timestamp = 1234567891.0

        assert state.encryption.encryption_counter == 2
        assert state.packets.packet_id == 2
