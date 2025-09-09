"""Tests for expanded Environmental Sensing Service characteristics."""

import pytest

from bluetooth_sig.gatt.characteristics.apparent_wind_direction import (
    ApparentWindDirectionCharacteristic,
)
from bluetooth_sig.gatt.characteristics.apparent_wind_speed import (
    ApparentWindSpeedCharacteristic,
)
from bluetooth_sig.gatt.characteristics.dew_point import DewPointCharacteristic
from bluetooth_sig.gatt.characteristics.heat_index import HeatIndexCharacteristic
from bluetooth_sig.gatt.characteristics.true_wind_direction import (
    TrueWindDirectionCharacteristic,
)
from bluetooth_sig.gatt.characteristics.true_wind_speed import (
    TrueWindSpeedCharacteristic,
)
from bluetooth_sig.gatt.characteristics.wind_chill import WindChillCharacteristic
from bluetooth_sig.gatt.services.environmental_sensing import (
    EnvironmentalSensingService,
)


class TestEnvironmentalSensingExpanded:
    """Test expanded environmental sensing characteristics."""

    def test_dew_point_parsing(self):
        """Test dew point characteristic parsing."""
        char = DewPointCharacteristic(uuid="", properties=set())

        # Test positive temperature
        data = bytearray([25])  # 25°C
        assert char.decode_value(data) == 25.0

        # Test negative temperature (sint8)
        data = bytearray([256 - 10])  # -10°C
        assert char.decode_value(data) == -10.0

        # Test extreme values
        data = bytearray([127])  # Max positive sint8
        assert char.decode_value(data) == 127.0

        data = bytearray([128])  # Max negative sint8 (-128)
        assert char.decode_value(data) == -128.0

    def test_heat_index_parsing(self):
        """Test heat index characteristic parsing."""
        char = HeatIndexCharacteristic(uuid="", properties=set())

        # Test normal temperature
        data = bytearray([35])  # 35°C
        assert char.decode_value(data) == 35.0

        # Test max uint8
        data = bytearray([255])  # 255°C
        assert char.decode_value(data) == 255.0

    def test_wind_chill_parsing(self):
        """Test wind chill characteristic parsing."""
        char = WindChillCharacteristic(uuid="", properties=set())

        # Test negative temperature
        data = bytearray([256 - 15])  # -15°C
        assert char.decode_value(data) == -15.0

        # Test positive temperature
        data = bytearray([5])  # 5°C
        assert char.decode_value(data) == 5.0

    def test_true_wind_speed_parsing(self):
        """Test true wind speed characteristic parsing."""
        char = TrueWindSpeedCharacteristic(uuid="", properties=set())

        # Test 10.50 m/s (1050 * 0.01)
        data = bytearray([0x1A, 0x04])  # 1050 in little endian
        assert char.decode_value(data) == 10.50

        # Test zero wind
        data = bytearray([0x00, 0x00])
        assert char.decode_value(data) == 0.0

    def test_true_wind_direction_parsing(self):
        """Test true wind direction characteristic parsing."""
        char = TrueWindDirectionCharacteristic(uuid="", properties=set())

        # Test 180.0° (18000 * 0.01)
        data = bytearray([0x50, 0x46])  # 18000 in little endian
        assert char.decode_value(data) == 180.0

        # Test 0° (north)
        data = bytearray([0x00, 0x00])
        assert char.decode_value(data) == 0.0

    def test_apparent_wind_characteristics(self):
        """Test apparent wind speed and direction characteristics."""
        speed_char = ApparentWindSpeedCharacteristic(uuid="", properties=set())
        direction_char = ApparentWindDirectionCharacteristic(uuid="", properties=set())

        # Test parsing similar to true wind
        speed_data = bytearray([0x64, 0x00])  # 100 * 0.01 = 1.0 m/s
        assert speed_char.decode_value(speed_data) == 1.0

        direction_data = bytearray([0x10, 0x27])  # 10000 * 0.01 = 100.0°
        assert direction_char.decode_value(direction_data) == 100.0

    def test_characteristic_properties(self):
        """Test characteristic metadata properties."""
        # Temperature-like characteristics
        dew_point = DewPointCharacteristic(uuid="", properties=set())
        assert dew_point.unit == "°C"

        # Wind speed characteristics - now using YAML units
        wind_speed = TrueWindSpeedCharacteristic(uuid="", properties=set())
        assert wind_speed.unit == "m/s"

        # Wind direction characteristics - still using YAML units
        wind_direction = TrueWindDirectionCharacteristic(uuid="", properties=set())
        assert wind_direction.unit == "°"

    def test_characteristic_uuid_resolution(self):
        """Test that characteristics resolve to correct UUIDs."""
        characteristics = [
            (DewPointCharacteristic, "2A7B"),
            (HeatIndexCharacteristic, "2A7A"),
            (WindChillCharacteristic, "2A79"),
            (TrueWindSpeedCharacteristic, "2A70"),
            (TrueWindDirectionCharacteristic, "2A71"),
            (ApparentWindSpeedCharacteristic, "2A72"),
            (ApparentWindDirectionCharacteristic, "2A73"),
        ]

        for char_class, expected_uuid in characteristics:
            char = char_class(uuid="", properties=set())
            assert char.char_uuid == expected_uuid

    def test_data_validation(self):
        """Test data validation for insufficient bytes."""
        # Single-byte characteristics
        dew_point = DewPointCharacteristic(uuid="", properties=set())
        with pytest.raises(ValueError, match="Insufficient data for int8"):
            dew_point.decode_value(bytearray([]))

        # Two-byte characteristics
        wind_speed = TrueWindSpeedCharacteristic(uuid="", properties=set())
        with pytest.raises(ValueError, match="Insufficient data for int16"):
            wind_speed.decode_value(bytearray([0x50]))

    def test_environmental_sensing_service_expansion(self):
        """Test that Environmental Sensing Service includes all new characteristics."""
        expected_chars = EnvironmentalSensingService.get_expected_characteristics()

        # Check all new characteristics are present
        new_characteristics = [
            # Environmental wind characteristics
            "Dew Point",
            "Heat Index",
            "Wind Chill",
            "True Wind Speed",
            "True Wind Direction",
            "Apparent Wind Speed",
            "Apparent Wind Direction",
            # Gas sensor characteristics for air quality monitoring
            "CO\\textsubscript{2} Concentration",
            "VOC Concentration",
            "Non-Methane Volatile Organic Compounds Concentration",
            "Ammonia Concentration",
            "Methane Concentration",
            "Nitrogen Dioxide Concentration",
            "Ozone Concentration",
            "Particulate Matter - PM1 Concentration",
            "Particulate Matter - PM2.5 Concentration",
            "Particulate Matter - PM10 Concentration",
            "Sulfur Dioxide Concentration",
            # Additional environmental characteristics
            "Elevation",
            "Barometric Pressure Trend",
            "Pollen Concentration",
            "Rainfall",
        ]

        # Verify we have all the expected characteristics
        # 3 original (Temperature, Humidity, Pressure) + 22 new ones = 25 total
        assert len(expected_chars) == len(new_characteristics) + 3

        for char_name in new_characteristics:
            assert char_name in expected_chars

        # Verify all are still optional
        required_chars = EnvironmentalSensingService.get_required_characteristics()
        assert len(required_chars) == 0  # All should remain optional
