"""Tests for the constants module."""


from bluetooth_sig.gatt.constants import (
    ABSOLUTE_ZERO_CELSIUS,
    # Flag bit positions
    FLAG_BIT_0,
    FLAG_BIT_1,
    FLAG_BIT_7,
    # Heart Rate specific constants
    HR_FORMAT_UINT8,
    HR_FORMAT_UINT16,
    HR_SENSOR_CONTACT_SUPPORTED,
    HUMIDITY_RESOLUTION,
    # IEEE 11073 special values
    IEEE11073_NAN,
    IEEE11073_NEGATIVE_INFINITY,
    IEEE11073_NRES,
    IEEE11073_POSITIVE_INFINITY,
    # Validation ranges
    MAX_CONCENTRATION_PPM,
    MAX_POWER_WATTS,
    MAX_PRESSURE_PA,
    MAX_TEMPERATURE_CELSIUS,
    # Common measurement ranges
    PERCENTAGE_MAX,
    PRESSURE_RESOLUTION,
    RR_INTERVAL_RESOLUTION,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    SINT32_MAX,
    SINT32_MIN,
    # Common resolution values
    TEMPERATURE_RESOLUTION,
    # Data type maximum and minimum values
    UINT8_MAX,
    UINT16_MAX,
    UINT32_MAX,
    # Common unit strings
    UNIT_CELSIUS,
    UNIT_FAHRENHEIT,
    UNIT_HECTOPASCAL,
    UNIT_KELVIN,
    UNIT_PASCAL,
    UNIT_PERCENT,
    UNIT_PPM,
)


class TestConstants:
    """Test constant values are correct."""

    def test_uint_max_values(self):
        """Test unsigned integer maximum values."""
        assert UINT8_MAX == 255
        assert UINT16_MAX == 65535
        assert UINT32_MAX == 4294967295

    def test_sint_min_max_values(self):
        """Test signed integer min/max values."""
        assert SINT8_MIN == -128
        assert SINT8_MAX == 127
        assert SINT16_MIN == -32768
        assert SINT16_MAX == 32767
        assert SINT32_MIN == -2147483648
        assert SINT32_MAX == 2147483647

    def test_measurement_ranges(self):
        """Test measurement range constants."""
        assert PERCENTAGE_MAX == 100
        assert ABSOLUTE_ZERO_CELSIUS == -273.15

    def test_resolution_values(self):
        """Test resolution constants."""
        assert TEMPERATURE_RESOLUTION == 0.01
        assert PRESSURE_RESOLUTION == 0.1
        assert HUMIDITY_RESOLUTION == 0.01

    def test_ieee11073_special_values(self):
        """Test IEEE 11073 special values."""
        assert IEEE11073_NAN == 0x07FF
        assert IEEE11073_NRES == 0x0800
        assert IEEE11073_POSITIVE_INFINITY == 0x07FE
        assert IEEE11073_NEGATIVE_INFINITY == 0x0802

    def test_unit_strings(self):
        """Test unit string constants."""
        assert UNIT_CELSIUS == "°C"
        assert UNIT_FAHRENHEIT == "°F"
        assert UNIT_KELVIN == "K"
        assert UNIT_PERCENT == "%"
        assert UNIT_PPM == "ppm"
        assert UNIT_PASCAL == "Pa"
        assert UNIT_HECTOPASCAL == "hPa"

    def test_flag_bits(self):
        """Test flag bit constants."""
        assert FLAG_BIT_0 == 1
        assert FLAG_BIT_1 == 2
        assert FLAG_BIT_7 == 128

    def test_heart_rate_constants(self):
        """Test heart rate specific constants."""
        assert HR_FORMAT_UINT8 == 0
        assert HR_FORMAT_UINT16 == 1
        assert HR_SENSOR_CONTACT_SUPPORTED == 2
        assert RR_INTERVAL_RESOLUTION == 1 / 1024

    def test_validation_ranges(self):
        """Test validation range constants."""
        assert MAX_CONCENTRATION_PPM == 65535.0
        assert MAX_TEMPERATURE_CELSIUS == 1000.0
        assert MAX_PRESSURE_PA == 200000.0
        assert MAX_POWER_WATTS == 65535.0

    def test_constants_are_immutable_types(self):
        """Test that constants are immutable types."""
        # Check that constants are primitive types (int, float, str)
        assert isinstance(UINT8_MAX, int)
        assert isinstance(TEMPERATURE_RESOLUTION, float)
        assert isinstance(UNIT_CELSIUS, str)
        assert isinstance(ABSOLUTE_ZERO_CELSIUS, float)
