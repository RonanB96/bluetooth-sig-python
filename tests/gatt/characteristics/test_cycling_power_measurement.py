"""Test cycling power measurement characteristic parsing."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import CyclingPowerMeasurementCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


class TestCyclingPowerMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Measurement characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerMeasurementCharacteristic:
        """Provide Cycling Power Measurement characteristic for testing."""
        return CyclingPowerMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Measurement characteristic."""
        return "2A63"

    @pytest.fixture
    def valid_test_data(self) -> bytearray:
        """Valid cycling power measurement test data."""
        flags = 0x0000  # No optional fields
        power = 250  # 250 watts
        return bytearray(struct.pack("<Hh", flags, power))

    def test_cycling_power_measurement_basic_parsing(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test basic cycling power measurement parsing."""
        # Test minimum required data: Flags(2) + Power(2)
        flags = 0x0000  # No optional fields
        power = 250  # 250 watts
        test_data = struct.pack("<Hh", flags, power)
        result = characteristic.decode_value(bytearray(test_data))

        assert result.flags == 0
        assert result.instantaneous_power == 250

    def test_cycling_power_measurement_with_pedal_balance(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test cycling power measurement with pedal power balance."""
        # Test with pedal power balance
        flags = 0x0001  # Pedal power balance present
        power = 300
        balance = 100  # 50% (100 * 0.5%)
        test_data = struct.pack("<HhB", flags, power, balance)
        result = characteristic.decode_value(bytearray(test_data))

        assert result.flags == 1
        assert result.instantaneous_power == 300
        assert result.pedal_power_balance == 50.0

    def test_cycling_power_measurement_with_wheel_data(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test cycling power measurement with wheel revolution data."""
        # Test with wheel revolution data
        flags = 0x0010  # Wheel revolution data present
        power = 320
        wheel_revs = 12345
        wheel_time = 2048  # 1 second in 1/2048 units
        test_data = struct.pack("<HhIH", flags, power, wheel_revs, wheel_time)
        result = characteristic.decode_value(bytearray(test_data))

        assert result.flags == 16
        assert result.instantaneous_power == 320
        assert result.cumulative_wheel_revolutions == 12345
        assert result.last_wheel_event_time == 1.0  # 2048 / 2048 = 1.0 second
