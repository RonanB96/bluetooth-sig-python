"""Test new sensor characteristics parsing and functionality."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import (
    BarometricPressureTrendCharacteristic,
    ElevationCharacteristic,
    LocalTimeInformationCharacteristic,
    MagneticDeclinationCharacteristic,
    MagneticFluxDensity2DCharacteristic,
    MagneticFluxDensity3DCharacteristic,
    PollenConcentrationCharacteristic,
    RainfallCharacteristic,
    TimeZoneCharacteristic,
)


class TestNavigationCharacteristics:
    """Test navigation and positioning characteristics."""

    def test_magnetic_declination_parsing(self):
        """Test Magnetic Declination characteristic parsing."""
        char = MagneticDeclinationCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A2C"

        # Test metadata
        assert char.unit == "°"
        assert char.value_type == "string"  # Changed from float - YAML overrides manual

        # Test normal parsing: 18000 (in 0.01 degrees) = 180.00 degrees
        test_data = bytearray([0x40, 0x46])  # 18000 in little endian uint16
        parsed = char.parse_value(test_data)
        assert parsed == 179.84

        # Test boundary values
        zero_data = bytearray([0x00, 0x00])  # 0 degrees
        assert char.parse_value(zero_data) == 0.0

        max_data = bytearray([0x9F, 0x8C])  # 35999 = 359.99 degrees
        assert char.parse_value(max_data) == 359.99

    def test_magnetic_declination_error_handling(self):
        """Test Magnetic Declination error handling."""
        char = MagneticDeclinationCharacteristic(uuid="", properties=set())

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 2 bytes"):
            char.parse_value(bytearray([0x12]))

    def test_elevation_parsing(self):
        """Test Elevation characteristic parsing."""
        char = ElevationCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A6C"

        # Test metadata
        assert char.unit == "length.meter"
        assert char.value_type == "string"  # Changed from float - YAML overrides manual

        # Test normal parsing: 50000 (in 0.01 meters) = 500.00 meters
        test_data = bytearray([0x50, 0xC3, 0x00])  # 50000 in 24-bit little endian
        parsed = char.parse_value(test_data)
        assert parsed == 500.0

        # Test negative elevation (below sea level)
        neg_data = bytearray([0xFF, 0xFF, 0xFF])  # -1 in 24-bit signed
        parsed_neg = char.parse_value(neg_data)
        assert parsed_neg == -0.01

    def test_elevation_error_handling(self):
        """Test Elevation error handling."""
        char = ElevationCharacteristic(uuid="", properties=set())

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 3 bytes"):
            char.parse_value(bytearray([0x12, 0x34]))

    def test_magnetic_flux_density_2d_parsing(self):
        """Test Magnetic Flux Density 2D characteristic parsing."""
        char = MagneticFluxDensity2DCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2AA0"

        # Test metadata
        assert char.unit == "tesla"
        assert char.value_type == "string"

        # Test normal parsing: X=1000, Y=-500 (in 10^-7 Tesla units)
        test_data = bytearray(struct.pack("<hh", 1000, -500))
        parsed = char.parse_value(test_data)

        assert abs(parsed["x_axis"] - 1e-4) < 1e-10  # 1000 * 10^-7 = 1e-4
        assert abs(parsed["y_axis"] - (-5e-5)) < 1e-10  # -500 * 10^-7 = -5e-5
        assert parsed["unit"] == "T"

    def test_magnetic_flux_density_3d_parsing(self):
        """Test Magnetic Flux Density 3D characteristic parsing."""
        char = MagneticFluxDensity3DCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2AA1"

        # Test metadata
        assert char.unit == "tesla"
        assert char.value_type == "string"

        # Test normal parsing: X=1000, Y=-500, Z=2000
        test_data = bytearray(struct.pack("<hhh", 1000, -500, 2000))
        parsed = char.parse_value(test_data)

        assert abs(parsed["x_axis"] - 1e-4) < 1e-10
        assert abs(parsed["y_axis"] - (-5e-5)) < 1e-10
        assert abs(parsed["z_axis"] - 2e-4) < 1e-10
        assert parsed["unit"] == "T"


class TestEnvironmentalCharacteristics:
    """Test environmental sensor characteristics."""

    def test_barometric_pressure_trend_parsing(self):
        """Test Barometric Pressure Trend characteristic parsing."""
        char = BarometricPressureTrendCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2AA3"

        # Test metadata
        assert char.unit == ""
        assert (
            char.value_type == "string"
        )  # Manual override: returns descriptive strings

        # Test known trend values
        test_cases = [
            (0, "Unknown"),
            (1, "Continuously falling"),
            (2, "Continuously rising"),
            (9, "Steady"),
        ]

        for value, expected in test_cases:
            test_data = bytearray([value])
            parsed = char.parse_value(test_data)
            assert parsed == expected

        # Test reserved value
        reserved_data = bytearray([255])
        parsed = char.parse_value(reserved_data)
        assert parsed == "Reserved (value: 255)"

    def test_pollen_concentration_parsing(self):
        """Test Pollen Concentration characteristic parsing."""
        char = PollenConcentrationCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A75"

        # Test metadata
        assert char.unit == "count/m³"
        assert char.value_type == "int"

        # Test normal parsing: 123456 count/m³
        test_data = bytearray([0x40, 0xE2, 0x01])  # 123456 in 24-bit little endian
        parsed = char.parse_value(test_data)
        assert parsed == 123456

    def test_rainfall_parsing(self):
        """Test Rainfall characteristic parsing."""
        char = RainfallCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A78"

        # Test metadata
        assert char.unit == "mm"
        assert char.value_type == "int"  # YAML provides uint16 -> int

        # Test normal parsing: 1250 mm rainfall
        test_data = bytearray([0xE2, 0x04])  # 1250 in little endian uint16
        parsed = char.parse_value(test_data)
        assert parsed == 1250.0


class TestTimeCharacteristics:
    """Test time-related characteristics."""

    def test_time_zone_parsing(self):
        """Test Time Zone characteristic parsing."""
        char = TimeZoneCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A0E"

        # Test metadata
        assert char.unit == ""
        assert (
            char.value_type == "string"
        )  # Manual override: returns descriptive strings

        # Test normal time zones
        test_cases = [
            (0, "UTC+00:00"),  # UTC
            (4, "UTC+01:00"),  # +1 hour (4 * 15 minutes)
            (-4, "UTC-01:00"),  # -1 hour
            (2, "UTC+00:30"),  # +30 minutes
            (32, "UTC+08:00"),  # +8 hours (Asia)
            (-20, "UTC-05:00"),  # -5 hours (US East)
        ]

        for offset, expected in test_cases:
            test_data = bytearray(struct.pack("b", offset))  # signed byte
            parsed = char.parse_value(test_data)
            assert parsed == expected

        # Test unknown value
        unknown_data = bytearray([0x80])  # -128
        parsed = char.parse_value(unknown_data)
        assert parsed == "Unknown"

    def test_local_time_information_parsing(self):
        """Test Local Time Information characteristic parsing."""
        char = LocalTimeInformationCharacteristic(uuid="", properties=set())

        # Test UUID resolution
        assert char.char_uuid == "2A0F"

        # Test metadata
        assert char.unit == ""
        assert char.value_type == "bytes"  # YAML provides struct -> bytes

        # Test normal parsing: UTC+2 with DST (+1 hour)
        test_data = bytearray([8, 4])  # timezone=+2h (8*15min), dst=+1h (value 4)
        parsed = char.parse_value(test_data)

        assert parsed.timezone.description == "UTC+02:00"
        assert parsed.timezone.offset_hours == 2.0
        assert parsed.dst_offset.description == "Daylight Time"
        assert parsed.dst_offset.offset_hours == 1.0
        assert parsed.total_offset_hours == 3.0

        # Test unknown values
        unknown_data = bytearray([0x80, 0xFF])  # unknown timezone and DST
        parsed_unknown = char.parse_value(unknown_data)
        assert parsed_unknown.timezone.description == "Unknown"
        assert parsed_unknown.dst_offset.description == "DST offset unknown"

    def test_local_time_information_encode_value(self):
        """Test encoding LocalTimeInformationData back to bytes."""
        char = LocalTimeInformationCharacteristic(uuid="", properties=set())
        
        from bluetooth_sig.gatt.characteristics.local_time_information import (
            LocalTimeInformationData, TimezoneInfo, DSTOffsetInfo
        )
        
        # Create test data for UTC+2 with DST
        test_data = LocalTimeInformationData(
            timezone=TimezoneInfo(
                description="UTC+02:00",
                offset_hours=2.0,
                raw_value=8,  # 8 * 15min = 120min = 2h
            ),
            dst_offset=DSTOffsetInfo(
                description="Daylight Time",
                offset_hours=1.0,
                raw_value=4,  # DST value 4 = +1h
            ),
            total_offset_hours=3.0,
        )
        
        # Encode the data
        encoded = char.encode_value(test_data)
        
        # Should produce the correct bytes
        assert len(encoded) == 2
        assert encoded == bytearray([8, 4])
        
    def test_local_time_information_round_trip(self):
        """Test that parsing and encoding preserve data."""
        char = LocalTimeInformationCharacteristic(uuid="", properties=set())
        
        # Test with UTC+2 and DST
        original_data = bytearray([8, 4])
        
        # Parse the data
        parsed = char.parse_value(original_data)
        
        # Encode it back
        encoded = char.encode_value(parsed)
        
        # Should match the original
        assert encoded == original_data
