"""Tests for advertising exceptions."""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.exceptions import (
    AdvertisingError,
    AdvertisingParseError,
    DecryptionFailedError,
    DuplicatePacketError,
    EncryptionRequiredError,
    ReplayDetectedError,
    UnsupportedVersionError,
)


class TestAdvertisingError:
    """Tests for AdvertisingError base exception."""

    def test_is_exception(self) -> None:
        """Test AdvertisingError is an Exception."""
        error = AdvertisingError("Test error")
        assert isinstance(error, Exception)

    def test_message(self) -> None:
        """Test error message."""
        error = AdvertisingError("Custom message")
        assert str(error) == "Custom message"


class TestAdvertisingParseError:
    """Tests for AdvertisingParseError."""

    def test_basic_message(self) -> None:
        """Test basic error message."""
        error = AdvertisingParseError(message="Parse failed")
        assert "Parse failed" in str(error)

    def test_with_interpreter_name(self) -> None:
        """Test error with interpreter name."""
        error = AdvertisingParseError(
            message="Invalid data",
            interpreter_name="BTHome",
        )
        assert "[BTHome]" in str(error)
        assert "Invalid data" in str(error)

    def test_with_raw_data(self) -> None:
        """Test error with raw data."""
        error = AdvertisingParseError(
            message="Parse failed",
            raw_data=b"\x01\x02\x03",
        )
        assert "010203" in str(error)

    def test_with_field(self) -> None:
        """Test error with field name."""
        error = AdvertisingParseError(
            message="Invalid value",
            field="temperature",
        )
        assert "temperature" in str(error)

    def test_truncates_long_data(self) -> None:
        """Test that long raw data is truncated."""
        long_data = bytes(range(64))
        error = AdvertisingParseError(
            message="Parse failed",
            raw_data=long_data,
        )
        # Should be truncated with "..."
        assert "..." in str(error)


class TestEncryptionRequiredError:
    """Tests for EncryptionRequiredError."""

    def test_message(self) -> None:
        """Test error message includes MAC address."""
        error = EncryptionRequiredError(mac_address="AA:BB:CC:DD:EE:FF")
        assert "AA:BB:CC:DD:EE:FF" in str(error)
        assert "Encryption required" in str(error)

    def test_mac_address_attribute(self) -> None:
        """Test mac_address attribute."""
        error = EncryptionRequiredError(mac_address="AA:BB:CC:DD:EE:FF")
        assert error.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_is_parse_error(self) -> None:
        """Test is subclass of AdvertisingParseError."""
        error = EncryptionRequiredError(mac_address="AA:BB:CC:DD:EE:FF")
        assert isinstance(error, AdvertisingParseError)


class TestDecryptionFailedError:
    """Tests for DecryptionFailedError."""

    def test_message(self) -> None:
        """Test error message includes reason."""
        error = DecryptionFailedError(
            mac_address="AA:BB:CC:DD:EE:FF",
            reason="wrong bindkey",
        )
        assert "AA:BB:CC:DD:EE:FF" in str(error)
        assert "wrong bindkey" in str(error)

    def test_default_reason(self) -> None:
        """Test default reason message."""
        error = DecryptionFailedError(mac_address="AA:BB:CC:DD:EE:FF")
        assert "decryption failed" in str(error)

    def test_attributes(self) -> None:
        """Test attributes are set correctly."""
        error = DecryptionFailedError(
            mac_address="AA:BB:CC:DD:EE:FF",
            reason="corrupt data",
            raw_data=b"\x01\x02",
        )
        assert error.mac_address == "AA:BB:CC:DD:EE:FF"
        assert error.reason == "corrupt data"


class TestUnsupportedVersionError:
    """Tests for UnsupportedVersionError."""

    def test_message_with_supported_versions(self) -> None:
        """Test error message with supported versions."""
        error = UnsupportedVersionError(
            version="v3",
            supported_versions=["v1", "v2"],
        )
        assert "v3" in str(error)
        assert "v1, v2" in str(error)

    def test_message_without_supported_versions(self) -> None:
        """Test error message without supported versions."""
        error = UnsupportedVersionError(version=5)
        assert "5" in str(error)
        assert "unknown" in str(error)

    def test_attributes(self) -> None:
        """Test attributes are set correctly."""
        error = UnsupportedVersionError(version="v3", supported_versions=["v1", "v2"])
        assert error.version == "v3"
        assert error.supported_versions == ["v1", "v2"]


class TestReplayDetectedError:
    """Tests for ReplayDetectedError."""

    def test_message(self) -> None:
        """Test error message includes counters."""
        error = ReplayDetectedError(
            mac_address="AA:BB:CC:DD:EE:FF",
            received_counter=100,
            expected_counter=200,
        )
        assert "AA:BB:CC:DD:EE:FF" in str(error)
        assert "100" in str(error)
        assert "200" in str(error)

    def test_attributes(self) -> None:
        """Test attributes are set correctly."""
        error = ReplayDetectedError(
            mac_address="AA:BB:CC:DD:EE:FF",
            received_counter=100,
            expected_counter=200,
        )
        assert error.mac_address == "AA:BB:CC:DD:EE:FF"
        assert error.received_counter == 100
        assert error.expected_counter == 200

    def test_is_advertising_error(self) -> None:
        """Test is subclass of AdvertisingError but not AdvertisingParseError."""
        error = ReplayDetectedError(
            mac_address="AA:BB:CC:DD:EE:FF",
            received_counter=100,
            expected_counter=200,
        )
        assert isinstance(error, AdvertisingError)
        assert not isinstance(error, AdvertisingParseError)


class TestDuplicatePacketError:
    """Tests for DuplicatePacketError."""

    def test_message(self) -> None:
        """Test error message includes packet ID."""
        error = DuplicatePacketError(
            mac_address="AA:BB:CC:DD:EE:FF",
            packet_id=42,
        )
        assert "AA:BB:CC:DD:EE:FF" in str(error)
        assert "42" in str(error)

    def test_attributes(self) -> None:
        """Test attributes are set correctly."""
        error = DuplicatePacketError(
            mac_address="AA:BB:CC:DD:EE:FF",
            packet_id=42,
        )
        assert error.mac_address == "AA:BB:CC:DD:EE:FF"
        assert error.packet_id == 42

    def test_is_advertising_error(self) -> None:
        """Test is subclass of AdvertisingError but not AdvertisingParseError."""
        error = DuplicatePacketError(
            mac_address="AA:BB:CC:DD:EE:FF",
            packet_id=42,
        )
        assert isinstance(error, AdvertisingError)
        assert not isinstance(error, AdvertisingParseError)


class TestExceptionCatching:
    """Tests for exception catching patterns."""

    def test_catch_all_advertising_errors(self) -> None:
        """Test catching all advertising errors with base class."""
        errors = [
            AdvertisingParseError(message="parse"),
            EncryptionRequiredError(mac_address="AA:BB:CC:DD:EE:FF"),
            DecryptionFailedError(mac_address="AA:BB:CC:DD:EE:FF"),
            ReplayDetectedError(mac_address="AA:BB:CC:DD:EE:FF", received_counter=1, expected_counter=2),
            DuplicatePacketError(mac_address="AA:BB:CC:DD:EE:FF", packet_id=1),
        ]

        for error in errors:
            with pytest.raises(AdvertisingError):
                raise error

    def test_catch_parse_errors(self) -> None:
        """Test catching parse errors specifically."""
        parse_errors = [
            AdvertisingParseError(message="parse"),
            EncryptionRequiredError(mac_address="AA:BB:CC:DD:EE:FF"),
            DecryptionFailedError(mac_address="AA:BB:CC:DD:EE:FF"),
            UnsupportedVersionError(version="v3"),
        ]

        for error in parse_errors:
            with pytest.raises(AdvertisingParseError):
                raise error
