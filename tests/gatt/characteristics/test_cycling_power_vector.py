"""Test cycling power vector characteristic parsing."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import CyclingPowerVectorCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


class TestCyclingPowerVectorCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Vector characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerVectorCharacteristic:
        """Provide Cycling Power Vector characteristic for testing."""
        return CyclingPowerVectorCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Vector characteristic."""
        return "2A64"

    @pytest.fixture
    def valid_test_data(self) -> bytearray:
        """Valid cycling power vector test data."""
        flags = 0x00  # No optional fields
        crank_revs = 1000
        crank_time = 1024  # 1 second
        force_magnitude = [100, 120, 110]  # Sample force data
        return bytearray(struct.pack("<BHHHHH", flags, crank_revs, crank_time, *force_magnitude))

    def test_cycling_power_vector_basic(self) -> None:
        """Test basic cycling power vector parsing."""
        char = CyclingPowerVectorCharacteristic()

        # Test minimum required data: Flags(1) + Crank Revs(2) + Crank Time(2) + First Angle(2)
        flags = 0x00  # No optional arrays
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 90  # 0.5 degrees (90 / 180)
        test_data = struct.pack("<BHHH", flags, crank_revs, crank_time, first_angle)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 0
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 0.5
        assert char.unit == "various"

    def test_cycling_power_vector_with_force_array(self) -> None:
        """Test cycling power vector with force magnitude array."""
        char = CyclingPowerVectorCharacteristic()

        # Test with force magnitude array
        flags = 0x01  # Force magnitudes present
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 180  # 1.0 degrees
        force1 = 100  # 100 N
        force2 = 150  # 150 N
        test_data = struct.pack("<BHHHhh", flags, crank_revs, crank_time, first_angle, force1, force2)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 1
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 1.0
        assert result.instantaneous_force_magnitude_array == (100.0, 150.0)

    def test_cycling_power_vector_with_torque_array(self) -> None:
        """Test cycling power vector with torque magnitude array."""
        char = CyclingPowerVectorCharacteristic()

        # Test with torque magnitude array
        flags = 0x02  # Torque magnitudes present
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 360  # 2.0 degrees
        torque1 = 160  # 5.0 Nm (160 / 32)
        torque2 = 192  # 6.0 Nm (192 / 32)
        test_data = struct.pack("<BHHHhh", flags, crank_revs, crank_time, first_angle, torque1, torque2)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 2
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 2.0
        assert result.instantaneous_torque_magnitude_array == (5.0, 6.0)

    def test_cycling_power_vector_invalid_data(self) -> None:
        """Test cycling power vector with invalid data."""
        char = CyclingPowerVectorCharacteristic()

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 7 bytes"):
            char.decode_value(bytearray([0x01, 0x02, 0x03]))

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 7 bytes"):
            char.decode_value(bytearray())
