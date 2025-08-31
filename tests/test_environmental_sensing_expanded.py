"""Tests for expanded Environmental Sensing Service characteristics."""

import pytest

from ble_gatt_device.gatt.characteristics.apparent_wind_direction import (
    ApparentWindDirectionCharacteristic,
)
from ble_gatt_device.gatt.characteristics.apparent_wind_speed import (
    ApparentWindSpeedCharacteristic,
)
from ble_gatt_device.gatt.characteristics.dew_point import DewPointCharacteristic
from ble_gatt_device.gatt.characteristics.heat_index import HeatIndexCharacteristic
from ble_gatt_device.gatt.characteristics.true_wind_direction import (
    TrueWindDirectionCharacteristic,
)
from ble_gatt_device.gatt.characteristics.true_wind_speed import (
    TrueWindSpeedCharacteristic,
)
from ble_gatt_device.gatt.characteristics.wind_chill import WindChillCharacteristic
from ble_gatt_device.gatt.services.environmental_sensing import (
    EnvironmentalSensingService,
)


class TestEnvironmentalSensingExpanded:
    """Test expanded environmental sensing characteristics."""

    def test_dew_point_parsing(self):
        """Test dew point characteristic parsing."""
        char = DewPointCharacteristic(uuid="", properties=set())

        # Test positive temperature
        data = bytearray([25])  # 25°C
        assert char.parse_value(data) == 25.0

        # Test negative temperature (sint8)
        data = bytearray([256 - 10])  # -10°C
        assert char.parse_value(data) == -10.0

        # Test extreme values
        data = bytearray([127])  # Max positive sint8
        assert char.parse_value(data) == 127.0

        data = bytearray([128])  # Max negative sint8 (-128)
        assert char.parse_value(data) == -128.0

    def test_heat_index_parsing(self):
        """Test heat index characteristic parsing."""
        char = HeatIndexCharacteristic(uuid="", properties=set())

        # Test normal temperature
        data = bytearray([35])  # 35°C
        assert char.parse_value(data) == 35.0

        # Test max uint8
        data = bytearray([255])  # 255°C
        assert char.parse_value(data) == 255.0

    def test_wind_chill_parsing(self):
        """Test wind chill characteristic parsing."""
        char = WindChillCharacteristic(uuid="", properties=set())

        # Test negative temperature
        data = bytearray([256 - 15])  # -15°C
        assert char.parse_value(data) == -15.0

        # Test positive temperature
        data = bytearray([5])  # 5°C
        assert char.parse_value(data) == 5.0

    def test_true_wind_speed_parsing(self):
        """Test true wind speed characteristic parsing."""
        char = TrueWindSpeedCharacteristic(uuid="", properties=set())

        # Test 10.50 m/s (1050 * 0.01)
        data = bytearray([0x1A, 0x04])  # 1050 in little endian
        assert char.parse_value(data) == 10.50

        # Test zero wind
        data = bytearray([0x00, 0x00])
        assert char.parse_value(data) == 0.0

    def test_true_wind_direction_parsing(self):
        """Test true wind direction characteristic parsing."""
        char = TrueWindDirectionCharacteristic(uuid="", properties=set())

        # Test 180.0° (18000 * 0.01)
        data = bytearray([0x50, 0x46])  # 18000 in little endian
        assert char.parse_value(data) == 180.0

        # Test 0° (north)
        data = bytearray([0x00, 0x00])
        assert char.parse_value(data) == 0.0

    def test_apparent_wind_characteristics(self):
        """Test apparent wind speed and direction characteristics."""
        speed_char = ApparentWindSpeedCharacteristic(uuid="", properties=set())
        direction_char = ApparentWindDirectionCharacteristic(uuid="", properties=set())

        # Test parsing similar to true wind
        speed_data = bytearray([0x64, 0x00])  # 100 * 0.01 = 1.0 m/s
        assert speed_char.parse_value(speed_data) == 1.0

        direction_data = bytearray([0x10, 0x27])  # 10000 * 0.01 = 100.0°
        assert direction_char.parse_value(direction_data) == 100.0

    def test_characteristic_properties(self):
        """Test characteristic metadata properties."""
        # Temperature-like characteristics
        dew_point = DewPointCharacteristic(uuid="", properties=set())
        assert dew_point.device_class == "temperature"
        assert dew_point.unit == "°C"
        assert dew_point.state_class == "measurement"

        # Wind speed characteristics
        wind_speed = TrueWindSpeedCharacteristic(uuid="", properties=set())
        assert wind_speed.device_class == "wind_speed"
        assert wind_speed.unit == "m/s"
        assert wind_speed.state_class == "measurement"

        # Wind direction characteristics
        wind_direction = TrueWindDirectionCharacteristic(uuid="", properties=set())
        assert wind_direction.device_class == "direction"
        assert wind_direction.unit == "°"
        assert wind_direction.state_class == "measurement"

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
            assert char.CHAR_UUID == expected_uuid

    def test_data_validation(self):
        """Test data validation for insufficient bytes."""
        # Single-byte characteristics
        dew_point = DewPointCharacteristic(uuid="", properties=set())
        with pytest.raises(ValueError, match="must be at least 1 byte"):
            dew_point.parse_value(bytearray([]))

        # Two-byte characteristics
        wind_speed = TrueWindSpeedCharacteristic(uuid="", properties=set())
        with pytest.raises(ValueError, match="must be at least 2 bytes"):
            wind_speed.parse_value(bytearray([0x50]))

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
            "Ammonia Concentration",
            "Methane Concentration",
            "Nitrogen Dioxide Concentration",
            "Ozone Concentration",
            "Particulate Matter - PM1 Concentration",
            "Particulate Matter - PM2.5 Concentration",
            "Particulate Matter - PM10 Concentration",
            "Sulfur Dioxide Concentration",
        ]

        # Verify we have all the expected characteristics
        # 3 original (Temperature, Humidity, Pressure) + 17 new ones = 20 total
        assert len(expected_chars) == len(new_characteristics) + 3

        for char_name in new_characteristics:
            assert char_name in expected_chars

        # Verify all are still optional
        required_chars = EnvironmentalSensingService.get_required_characteristics()
        assert len(required_chars) == 0  # All should remain optional
