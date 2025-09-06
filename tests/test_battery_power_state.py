"""Tests for Battery Power State characteristic implementation."""

import pytest

from bluetooth_sig.gatt.characteristics.battery_power_state import (
    BatteryPowerStateCharacteristic,
)


class TestBatteryPowerStateCharacteristic:
    """Test Battery Power State characteristic implementation."""

    def test_characteristic_name(self):
        """Test characteristic name resolution."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())
        assert char._characteristic_name == "Battery Level Status"
        assert (
            char.value_type == "string"
        )  # YAML has boolean[] which maps to string, but parse_value returns dict

    def test_parse_basic_battery_state(self):
        """Test parsing basic battery state with all flags."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery present, wired power, charging, good level
        # Binary: 11010110 = 0xD6
        # Bits 0-1: 10 (present)
        # Bit 2: 1 (wired power)
        # Bit 3: 0 (no wireless power)
        # Bits 4-5: 01 (charging)
        # Bits 6-7: 11 (good level)
        data = bytearray([0xD6])
        result = char.parse_value(data)

        assert result.raw_value == 0xD6
        assert result.battery_present == "present"
        assert result.wired_external_power_connected is True
        assert result.wireless_external_power_connected is False
        assert result.battery_charge_state == "charging"
        assert result.battery_charge_level == "good"
        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason is None

    def test_parse_battery_not_present(self):
        """Test parsing when battery is not present."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery not present, no external power, unknown states
        # Binary: 00000001 = 0x01
        # Bits 0-1: 01 (not present)
        # Other bits: 0 (unknown/false)
        data = bytearray([0x01])
        result = char.parse_value(data)

        assert result.raw_value == 0x01
        assert result.battery_present == "not_present"
        assert result.wired_external_power_connected is False
        assert result.wireless_external_power_connected is False
        assert result.battery_charge_state == "unknown"
        assert result.battery_charge_level == "unknown"
        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason is None

    def test_parse_wireless_power_discharging(self):
        """Test parsing with wireless power and discharging state."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery present, wireless power, discharging, low level
        # Binary: 10101010 = 0xAA
        # Bits 0-1: 10 (present)
        # Bit 2: 0 (no wired power)
        # Bit 3: 1 (wireless power)
        # Bits 4-5: 10 (discharging)
        # Bits 6-7: 10 (low level)
        data = bytearray([0xAA])
        result = char.parse_value(data)

        assert result.raw_value == 0xAA
        assert result.battery_present == "present"
        assert result.wired_external_power_connected is False
        assert result.wireless_external_power_connected is True
        assert result.battery_charge_state == "discharging"
        assert result.battery_charge_level == "low"
        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason is None

    def test_parse_critically_low_not_charging(self):
        """Test parsing critically low battery not charging."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery present, no external power, not charging, critically low
        # Binary: 01110010 = 0x72
        # Bits 0-1: 10 (present)
        # Bit 2: 0 (no wired power)
        # Bit 3: 0 (no wireless power)
        # Bits 4-5: 11 (not charging)
        # Bits 6-7: 01 (critically low)
        data = bytearray([0x72])
        result = char.parse_value(data)

        assert result.raw_value == 0x72
        assert result.battery_present == "present"
        assert result.wired_external_power_connected is False
        assert result.wireless_external_power_connected is False
        assert result.battery_charge_state == "not_charging"
        assert result.battery_charge_level == "critically_low"
        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason is None

    def test_parse_extended_format_with_charging_type(self):
        """Test parsing extended format with charging type information."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery present, wired power, charging, good level
        # Extended: constant current charging, no fault
        # First byte: 11010110 = 0xD6 (same as basic test)
        # Second byte: 00000001 = 0x01 (constant current, no fault)
        data = bytearray([0xD6, 0x01])
        result = char.parse_value(data)

        expected = {
            "raw_value": 0xD6,
            "battery_present": "present",
            "wired_external_power_connected": True,
            "wireless_external_power_connected": False,
            "battery_charge_state": "charging",
            "battery_charge_level": "good",
            "battery_charging_type": "constant_current",
            "charging_fault_reason": None,
        }
        assert result.raw_value == expected["raw_value"]
        assert result.battery_present == expected["battery_present"]
        assert (
            result.wired_external_power_connected
            == expected["wired_external_power_connected"]
        )
        assert (
            result.wireless_external_power_connected
            == expected["wireless_external_power_connected"]
        )
        assert result.battery_charge_state == expected["battery_charge_state"]
        assert result.battery_charge_level == expected["battery_charge_level"]
        assert result.battery_charging_type == expected["battery_charging_type"]
        assert result.charging_fault_reason == expected["charging_fault_reason"]

    def test_parse_extended_format_with_fault(self):
        """Test parsing extended format with charging fault."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test state: battery present, charging with fault
        # First byte: 0x82 = 10000010
        # Bits 0-1: 10 (present)
        # Bit 2: 0 (no wired power)
        # Bit 3: 0 (no wireless power)
        # Bits 4-5: 00 (unknown charge state)
        # Bits 6-7: 10 (low level)
        # Second byte: trickle charging with battery fault
        # Binary: 00001011 = 0x0B
        # Bits 0-2: 011 (trickle charging)
        # Bits 3-7: 00001 (battery fault)
        data = bytearray([0x82, 0x0B])
        result = char.parse_value(data)

        assert result.raw_value == 0x82
        assert result.battery_present == "present"
        assert result.wired_external_power_connected is False
        assert result.wireless_external_power_connected is False
        assert result.battery_charge_state == "unknown"
        assert result.battery_charge_level == "low"
        assert result.battery_charging_type == "trickle"
        assert result.charging_fault_reason == "battery_fault"

    def test_parse_extended_format_constant_voltage(self):
        """Test parsing with constant voltage charging type."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test constant voltage charging
        # Second byte: 00000010 = 0x02 (constant voltage, no fault)
        data = bytearray([0x82, 0x02])
        result = char.parse_value(data)

        assert result.battery_charging_type == "constant_voltage"
        assert result.charging_fault_reason is None

    def test_parse_full_flags_power_state_format(self):
        """Test parsing the full SIG Flags + 2-byte Power State format."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Device reported payload: 00 a3 00
        data = bytearray([0x00, 0xA3, 0x00])
        result = char.parse_value(data)

        assert result.raw_value == 0x00
        assert result.battery_present == "present"
        assert result.wired_external_power_connected is True
        assert result.wireless_external_power_connected is False
        assert result.battery_charge_state == "charging"
        assert result.battery_charge_level == "good"
        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason is None

    def test_flags_identifier_missing_raises(self):
        """If Flags indicate Identifier present but payload is too short, raise."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Flags=0x01 indicates Identifier present but no extra bytes follow
        data = bytearray([0x01, 0xA3, 0x00])
        with pytest.raises(ValueError, match="Identifier indicated by Flags"):
            char.parse_value(data)

    def test_parse_extended_format_external_power_fault(self):
        """Test parsing with external power fault."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test external power fault
        # Second byte: 00010000 = 0x10
        # Bits 0-2: 000 (unknown charging type)
        # Bits 3-7: 00010 (external power fault)
        data = bytearray([0x82, 0x10])
        result = char.parse_value(data)

        assert result.battery_charging_type == "unknown"
        assert result.charging_fault_reason == "external_power_fault"

    def test_parse_all_unknown_states(self):
        """Test parsing with all states unknown."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # All bits zero = all unknown states
        data = bytearray([0x00])
        result = char.parse_value(data)

        expected = {
            "raw_value": 0x00,
            "battery_present": "unknown",
            "wired_external_power_connected": False,
            "wireless_external_power_connected": False,
            "battery_charge_state": "unknown",
            "battery_charge_level": "unknown",
            "battery_charging_type": "unknown",
            "charging_fault_reason": None,
        }
        assert result.raw_value == expected["raw_value"]
        assert result.battery_present == expected["battery_present"]
        assert (
            result.wired_external_power_connected
            == expected["wired_external_power_connected"]
        )
        assert (
            result.wireless_external_power_connected
            == expected["wireless_external_power_connected"]
        )
        assert result.battery_charge_state == expected["battery_charge_state"]
        assert result.battery_charge_level == expected["battery_charge_level"]
        assert result.battery_charging_type == expected["battery_charging_type"]
        assert result.charging_fault_reason == expected["charging_fault_reason"]

    def test_parse_reserved_states(self):
        """Test parsing with reserved states."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test reserved battery present state
        # Binary: 00000011 = 0x03
        # Bits 0-1: 11 (reserved)
        data = bytearray([0x03])
        result = char.parse_value(data)

        assert result.battery_present == "reserved"

    def test_parse_invalid_data(self):
        """Test parsing with invalid data."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 1 byte"):
            char.parse_value(bytearray())

        # Test None data
        with pytest.raises(ValueError, match="must be at least 1 byte"):
            char.parse_value(bytearray([]))

    def test_unit_property(self):
        """Test unit property (should be empty for status characteristic)."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())
        assert char.unit == ""

    def test_characteristic_uuid_resolution(self):
        """Test characteristic UUID resolution."""
        char = BatteryPowerStateCharacteristic(uuid="2BED", properties={"read"})
        assert char.char_uuid == "2BED"

    def test_encode_value(self):
        """Test encoding BatteryPowerStateData back to bytes."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Create test data
        from bluetooth_sig.gatt.characteristics.battery_power_state import (
            BatteryPowerStateData,
        )

        test_data = BatteryPowerStateData(
            raw_value=0xD6,
            battery_present="present",
            wired_external_power_connected=True,
            wireless_external_power_connected=False,
            battery_charge_state="charging",
            battery_charge_level="good",
            battery_charging_type="unknown",
            charging_fault_reason=None,
        )

        # Encode the data
        encoded = char.encode_value(test_data)

        # Should produce the basic single-byte format
        # Battery present (10) + wired power (1<<2) + charging (01<<4) + good (11<<6)
        # = 0b11010110 = 0xD6
        assert len(encoded) == 1
        assert encoded[0] == 0xD6

    def test_round_trip_parse_encode(self):
        """Test that parsing and encoding preserve data for basic format."""
        char = BatteryPowerStateCharacteristic(uuid="", properties=set())

        # Test with basic single-byte format
        original_data = bytearray([0xD6])

        # Parse the data
        parsed = char.parse_value(original_data)

        # Encode it back
        encoded = char.encode_value(parsed)

        # Should match the original (for basic format)
        assert encoded == original_data
        assert char.name == "Battery Level Status"
