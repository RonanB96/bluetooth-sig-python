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
from bluetooth_sig.gatt.constants import SINT8_MAX, SINT8_MIN, UINT8_MAX
from bluetooth_sig.gatt.exceptions import InsufficientDataError
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
        data = bytearray([SINT8_MAX])  # Max positive sint8
        assert char.decode_value(data) == SINT8_MAX

        data = bytearray([SINT8_MIN])  # Max negative sint8 (SINT8_MIN)
        assert char.decode_value(data) == SINT8_MIN

    def test_heat_index_parsing(self):
        """Test heat index characteristic parsing."""
        char = HeatIndexCharacteristic(uuid="", properties=set())

        # Test normal temperature
        data = bytearray([35])  # 35°C
        assert char.decode_value(data) == 35.0

        # Test max uint8
        data = bytearray([UINT8_MAX])  # UINT8_MAX°C
        assert char.decode_value(data) == UINT8_MAX

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
        with pytest.raises(InsufficientDataError):
            dew_point.decode_value(bytearray([]))

        # Two-byte characteristics
        wind_speed = TrueWindSpeedCharacteristic(uuid="", properties=set())
        with pytest.raises(InsufficientDataError):
            wind_speed.decode_value(bytearray([0x50]))

    def test_environmental_sensing_service_expansion(self):
        """Test that Environmental Sensing Service includes all new characteristics."""
        from bluetooth_sig.types.gatt_enums import CharacteristicName

        expected_chars = EnvironmentalSensingService.get_expected_characteristics()

        # Check all new characteristics are present
        new_characteristics = [
            # Environmental wind characteristics
            CharacteristicName.DEW_POINT,
            CharacteristicName.HEAT_INDEX,
            CharacteristicName.WIND_CHILL,
            CharacteristicName.TRUE_WIND_SPEED,
            CharacteristicName.TRUE_WIND_DIRECTION,
            CharacteristicName.APPARENT_WIND_SPEED,
            CharacteristicName.APPARENT_WIND_DIRECTION,
            # Gas sensor characteristics for air quality monitoring
            CharacteristicName.CO2_CONCENTRATION,
            CharacteristicName.VOC_CONCENTRATION,
            CharacteristicName.NON_METHANE_VOC_CONCENTRATION,
            CharacteristicName.AMMONIA_CONCENTRATION,
            CharacteristicName.METHANE_CONCENTRATION,
            CharacteristicName.NITROGEN_DIOXIDE_CONCENTRATION,
            CharacteristicName.OZONE_CONCENTRATION,
            CharacteristicName.PM1_CONCENTRATION,
            CharacteristicName.PM25_CONCENTRATION,
            CharacteristicName.PM10_CONCENTRATION,
            CharacteristicName.SULFUR_DIOXIDE_CONCENTRATION,
            # Additional environmental characteristics
            CharacteristicName.ELEVATION,
            CharacteristicName.BAROMETRIC_PRESSURE_TREND,
            CharacteristicName.POLLEN_CONCENTRATION,
            CharacteristicName.RAINFALL,
        ]

        # Verify we have all the expected characteristics
        # 3 original (Temperature, Humidity, Pressure) + 22 new ones = 25 total
        assert len(expected_chars) == len(new_characteristics) + 3

        for char_enum in new_characteristics:
            assert char_enum in expected_chars

        # Verify all are still optional
        required_chars = EnvironmentalSensingService.get_required_characteristics()
        assert len(required_chars) == 0  # All should remain optional
