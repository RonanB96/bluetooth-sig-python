"""Tests for SIGCharacteristicInterpreter.

Tests cover:
- Parsing SIG characteristics from service data advertisements
- Error handling for parse failures
- supports() method for routing
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.base import AdvertisingData
from bluetooth_sig.advertising.exceptions import AdvertisingParseError
from bluetooth_sig.advertising.sig_characteristic_interpreter import (
    SIGCharacteristicData,
    SIGCharacteristicInterpreter,
)
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.types.uuid import BluetoothUUID


class TestSIGCharacteristicInterpreterSupports:
    """Tests for SIGCharacteristicInterpreter.supports() method."""

    def test_supports_registered_uuid(self) -> None:
        """Test supports() returns True for registered characteristic UUID."""
        # Battery Level (0x2A19) is a registered SIG characteristic
        battery_uuid = BluetoothUUID(0x2A19)
        ad_data = AdvertisingData(service_data={battery_uuid: bytes([75])})

        assert SIGCharacteristicInterpreter.supports(ad_data) is True

    def test_does_not_support_unknown_uuid(self) -> None:
        """Test supports() returns False for unknown UUID."""
        unknown_uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        ad_data = AdvertisingData(service_data={unknown_uuid: bytes([1, 2, 3])})

        assert SIGCharacteristicInterpreter.supports(ad_data) is False

    def test_does_not_support_empty_service_data(self) -> None:
        """Test supports() returns False for empty service data."""
        ad_data = AdvertisingData()

        assert SIGCharacteristicInterpreter.supports(ad_data) is False

    def test_supports_one_of_multiple_uuids(self) -> None:
        """Test supports() returns True if at least one UUID is registered."""
        battery_uuid = BluetoothUUID(0x2A19)
        unknown_uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        ad_data = AdvertisingData(
            service_data={
                unknown_uuid: bytes([1, 2, 3]),
                battery_uuid: bytes([75]),
            }
        )

        assert SIGCharacteristicInterpreter.supports(ad_data) is True


class TestSIGCharacteristicInterpreterInterpret:
    """Tests for SIGCharacteristicInterpreter.interpret() method."""

    @pytest.fixture
    def interpreter(self) -> SIGCharacteristicInterpreter:
        """Create interpreter instance."""
        return SIGCharacteristicInterpreter("AA:BB:CC:DD:EE:FF")

    @pytest.fixture
    def state(self) -> DeviceAdvertisingState:
        """Create device state."""
        return DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

    def test_interpret_battery_level_success(
        self, interpreter: SIGCharacteristicInterpreter, state: DeviceAdvertisingState
    ) -> None:
        """Test successful interpretation of Battery Level."""
        battery_uuid = BluetoothUUID(0x2A19)
        ad_data = AdvertisingData(service_data={battery_uuid: bytes([75])})

        result = interpreter.interpret(ad_data, state)

        assert isinstance(result, SIGCharacteristicData)
        assert result.uuid == battery_uuid
        assert result.parsed_value == 75
        assert "Battery" in result.characteristic_name

    def test_interpret_returns_first_matching_uuid(
        self, interpreter: SIGCharacteristicInterpreter, state: DeviceAdvertisingState
    ) -> None:
        """Test that interpret returns the first matching UUID."""
        # Two registered UUIDs - should return the first one it finds
        battery_uuid = BluetoothUUID(0x2A19)
        ad_data = AdvertisingData(
            service_data={
                battery_uuid: bytes([50]),
            }
        )

        result = interpreter.interpret(ad_data, state)

        # Should match battery level
        assert result.parsed_value == 50

    def test_interpret_raises_on_parse_error(
        self, interpreter: SIGCharacteristicInterpreter, state: DeviceAdvertisingState
    ) -> None:
        """Test that interpret raises AdvertisingParseError on parse failure."""
        battery_uuid = BluetoothUUID(0x2A19)
        # Empty bytes should fail parsing
        ad_data = AdvertisingData(service_data={battery_uuid: bytes([])})

        with pytest.raises(AdvertisingParseError):
            interpreter.interpret(ad_data, state)

    def test_interpret_raises_on_no_matching_uuid(
        self, interpreter: SIGCharacteristicInterpreter, state: DeviceAdvertisingState
    ) -> None:
        """Test that interpret raises AdvertisingParseError when no UUID matches."""
        unknown_uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        ad_data = AdvertisingData(service_data={unknown_uuid: bytes([1, 2, 3])})

        with pytest.raises(AdvertisingParseError) as exc_info:
            interpreter.interpret(ad_data, state)

        assert "No matching SIG characteristic" in str(exc_info.value)

    def test_interpret_raises_on_empty_service_data(
        self, interpreter: SIGCharacteristicInterpreter, state: DeviceAdvertisingState
    ) -> None:
        """Test that interpret raises AdvertisingParseError for empty service data."""
        ad_data = AdvertisingData()

        with pytest.raises(AdvertisingParseError):
            interpreter.interpret(ad_data, state)


class TestSIGCharacteristicInterpreterInfo:
    """Tests for SIGCharacteristicInterpreter metadata."""

    def test_interpreter_info(self) -> None:
        """Test interpreter info is set correctly."""
        interpreter = SIGCharacteristicInterpreter("AA:BB:CC:DD:EE:FF")

        assert interpreter.info.name == "SIG Characteristic"
        assert interpreter.info.company_id is None
        assert interpreter.info.service_uuid is None

    def test_mac_address(self) -> None:
        """Test MAC address is stored correctly."""
        interpreter = SIGCharacteristicInterpreter("AA:BB:CC:DD:EE:FF")

        assert interpreter.mac_address == "AA:BB:CC:DD:EE:FF"
