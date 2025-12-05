"""Tests for Battery Level Status characteristic (0x2BED)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_level_status import (
    BatteryLevelStatus,
    BatteryLevelStatusCharacteristic,
    BatteryLevelStatusFlags,
)
from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types.battery import (
    BatteryChargeLevel,
    BatteryChargeState,
    BatteryChargingType,
    PowerConnectionState,
    ServiceRequiredState,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBatteryLevelStatusCharacteristic(CommonCharacteristicTests):
    """Test Battery Level Status characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Provide Battery Level Status characteristic for testing."""
        return BatteryLevelStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Level Status characteristic."""
        return "2BED"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery level status test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x07,  # flags: identifier present, battery level present, additional status present
                        0x01,
                        0x00,  # power state: battery present, others default
                        0x12,
                        0x34,  # identifier: 0x3412
                        0x64,  # battery level: 100
                        0x05,  # additional status: service required=1, battery fault=1
                    ]
                ),
                expected_value=BatteryLevelStatus(
                    flags=BatteryLevelStatusFlags(0x07),
                    battery_present=True,
                    wired_external_power_connected=PowerConnectionState.NO,
                    wireless_external_power_connected=PowerConnectionState.NO,
                    battery_charge_state=BatteryChargeState.UNKNOWN,
                    battery_charge_level=BatteryChargeLevel.UNKNOWN,
                    charging_type=BatteryChargingType.UNKNOWN,
                    charging_fault_battery=False,
                    charging_fault_external_power=False,
                    charging_fault_other=False,
                    identifier=0x3412,
                    battery_level=100,
                    service_required=ServiceRequiredState.TRUE,
                    battery_fault=True,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01, 0x00]),  # minimal: no optional fields, battery present
                expected_value=BatteryLevelStatus(
                    flags=BatteryLevelStatusFlags(0x00),
                    battery_present=True,
                    wired_external_power_connected=PowerConnectionState.NO,
                    wireless_external_power_connected=PowerConnectionState.NO,
                    battery_charge_state=BatteryChargeState.UNKNOWN,
                    battery_charge_level=BatteryChargeLevel.UNKNOWN,
                    charging_type=BatteryChargingType.UNKNOWN,
                    charging_fault_battery=False,
                    charging_fault_external_power=False,
                    charging_fault_other=False,
                    identifier=None,
                    battery_level=None,
                    service_required=None,  # Not present when additional status flag is 0
                    battery_fault=None,  # Not present when additional status flag is 0
                ),
                description="Minimal fields",
            ),
        ]

    # === Battery Level Status-Specific Tests ===

    def test_battery_level_status_minimal(self, characteristic: BaseCharacteristic) -> None:
        """Test minimal battery level status with only required fields."""
        data = bytearray(
            [
                0x00,  # no optional fields
                0x01,
                0x00,  # battery present
            ]
        )
        result = characteristic.decode_value(data)
        expected = BatteryLevelStatus(
            flags=BatteryLevelStatusFlags(0x00),
            battery_present=True,
            wired_external_power_connected=PowerConnectionState.NO,
            wireless_external_power_connected=PowerConnectionState.NO,
            battery_charge_state=BatteryChargeState.UNKNOWN,
            battery_charge_level=BatteryChargeLevel.UNKNOWN,
            charging_type=BatteryChargingType.UNKNOWN,
            charging_fault_battery=False,
            charging_fault_external_power=False,
            charging_fault_other=False,
            identifier=None,
            battery_level=None,
            service_required=None,
            battery_fault=None,
        )
        assert result == expected

    def test_battery_level_status_power_state_bits(self, characteristic: BaseCharacteristic) -> None:
        """Test power state bit field parsing."""
        # Construct power state with specific valid enum values
        # Power state is uint16: bits laid out as:
        # bit 0: battery_present (1)
        # bits 1-2: wired_external_power_connected (10 = 2 = UNKNOWN)
        # bits 3-4: wireless_external_power_connected (10 = 2 = UNKNOWN)
        # bits 5-6: battery_charge_state (00 = 0 = UNKNOWN)
        # bits 7-8: battery_charge_level (00 = 0 = UNKNOWN)
        # bits 9-11: charging_type (100 = 4 = FLOAT)
        # bit 12: charging_fault_battery (1)
        # bit 13: charging_fault_external_power (1)
        # bit 14: charging_fault_other (1)
        # bit 15: RFU (0)
        # Binary: 0111 1000 0001 0101 = 0x7815
        data = bytearray(
            [
                0x00,  # no optional fields
                0x15,  # Low byte of power state
                0x78,  # High byte of power state
            ]
        )
        result = characteristic.decode_value(data)
        assert result.battery_present is True
        assert result.wired_external_power_connected == PowerConnectionState.UNKNOWN
        assert result.wireless_external_power_connected == PowerConnectionState.UNKNOWN
        assert result.battery_charge_state == BatteryChargeState.UNKNOWN
        assert result.battery_charge_level == BatteryChargeLevel.UNKNOWN
        assert result.charging_type == BatteryChargingType.FLOAT
        assert result.charging_fault_battery is True
        assert result.charging_fault_external_power is True
        assert result.charging_fault_other is True

    def test_battery_level_status_encoding(self, characteristic: BatteryLevelStatusCharacteristic) -> None:
        """Test encoding BatteryLevelStatus to bytes."""
        flags = (
            BatteryLevelStatusFlags.IDENTIFIER_PRESENT
            | BatteryLevelStatusFlags.BATTERY_LEVEL_PRESENT
            | BatteryLevelStatusFlags.ADDITIONAL_STATUS_PRESENT
        )
        status = BatteryLevelStatus(
            flags=flags,
            battery_present=True,
            wired_external_power_connected=PowerConnectionState.YES,
            wireless_external_power_connected=PowerConnectionState.YES,
            battery_charge_state=BatteryChargeState.CHARGING,
            battery_charge_level=BatteryChargeLevel.CRITICALLY_LOW,
            charging_type=BatteryChargingType.CONSTANT_CURRENT,
            charging_fault_battery=True,
            charging_fault_external_power=False,
            charging_fault_other=True,
            identifier=0x1234,
            battery_level=50,
            service_required=ServiceRequiredState.TRUE,
            battery_fault=False,
        )
        encoded = characteristic.encode_value(status)
        expected = bytearray(
            [
                0x07,  # flags
                0xAB,
                0x53,  # power state: 0x53AB = 0101001110101011
                0x34,
                0x12,  # identifier little-endian
                0x32,  # battery level
                0x01,  # additional status: service_required=1 (bits 0-1), battery_fault=False
            ]
        )
        assert encoded == expected

    def test_battery_level_status_round_trip(self, characteristic: BatteryLevelStatusCharacteristic) -> None:
        """Test round-trip encoding/decoding preserves values."""
        original = BatteryLevelStatus(
            flags=BatteryLevelStatusFlags.IDENTIFIER_PRESENT | BatteryLevelStatusFlags.ADDITIONAL_STATUS_PRESENT,
            battery_present=False,
            wired_external_power_connected=PowerConnectionState.YES,
            wireless_external_power_connected=PowerConnectionState.YES,
            battery_charge_state=BatteryChargeState.DISCHARGING,
            battery_charge_level=BatteryChargeLevel.GOOD,
            charging_type=BatteryChargingType.FLOAT,
            charging_fault_battery=False,
            charging_fault_external_power=True,
            charging_fault_other=False,
            identifier=0xABCD,
            battery_level=None,
            service_required=ServiceRequiredState.FALSE,
            battery_fault=True,
        )
        encoded = characteristic.encode_value(original)
        decoded = characteristic.decode_value(encoded)
        assert decoded == original

    def test_insufficient_data_error(self, characteristic: BaseCharacteristic) -> None:
        """Test that insufficient data raises error."""
        with pytest.raises(InsufficientDataError):
            characteristic.decode_value(bytearray([0x00]))  # too short, missing power state

    def test_invalid_flags_optional_missing(self, characteristic: BaseCharacteristic) -> None:
        """Test that setting flags for optional fields but not providing data raises error."""
        # Flags say identifier present, but no identifier data
        data = bytearray(
            [
                0x01,  # identifier present
                0x00,
                0x00,  # power state
                # missing identifier
            ]
        )
        with pytest.raises(InsufficientDataError):
            characteristic.decode_value(data)

    def test_characteristic_metadata(self, characteristic: BatteryLevelStatusCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Battery Level Status"
        assert characteristic.unit == ""
        assert characteristic.uuid == "2BED"  # type: ignore[unreachable]
