"""Bluetooth SIG GATT characteristic registry.
Provides type-safe, registry-driven lookup for all supported characteristics.
Now encapsulated in CharacteristicRegistry class for API clarity and extensibility.
"""

from __future__ import annotations

from enum import Enum

from .ammonia_concentration import AmmoniaConcentrationCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
from .base import BaseCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .battery_power_state import BatteryPowerStateCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic
from .device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    ManufacturerNameStringCharacteristic,
    ModelNumberStringCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)
from .dew_point import DewPointCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .generic_access import AppearanceCharacteristic, DeviceNameCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic
from .glucose_measurement import GlucoseMeasurementCharacteristic
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .heat_index import HeatIndexCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .humidity import HumidityCharacteristic
from .illuminance import IlluminanceCharacteristic
from .local_time_information import LocalTimeInformationCharacteristic
from .magnetic_declination import MagneticDeclinationCharacteristic
from .magnetic_flux_density_2d import MagneticFluxDensity2DCharacteristic
from .magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pollen_concentration import PollenConcentrationCharacteristic
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rainfall import RainfallCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .sound_pressure_level import SoundPressureLevelCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .time_zone import TimeZoneCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .uv_index import UVIndexCharacteristic
from .voc_concentration import VOCConcentrationCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .wind_chill import WindChillCharacteristic


class CharacteristicName(Enum):
    """Enumeration of all supported GATT characteristic names."""

    BATTERY_LEVEL = "Battery Level"
    BATTERY_LEVEL_STATUS = "Battery Level Status"
    TEMPERATURE = "Temperature"
    TEMPERATURE_MEASUREMENT = "Temperature Measurement"
    HUMIDITY = "Humidity"
    PRESSURE = "Pressure"
    UV_INDEX = "UV Index"
    ILLUMINANCE = "Illuminance"
    POWER_SPECIFICATION = "Power Specification"
    HEART_RATE_MEASUREMENT = "Heart Rate Measurement"
    BLOOD_PRESSURE_MEASUREMENT = "Blood Pressure Measurement"
    BLOOD_PRESSURE_FEATURE = "Blood Pressure Feature"
    CSC_MEASUREMENT = "CSC Measurement"
    RSC_MEASUREMENT = "RSC Measurement"
    CYCLING_POWER_MEASUREMENT = "Cycling Power Measurement"
    CYCLING_POWER_FEATURE = "Cycling Power Feature"
    CYCLING_POWER_VECTOR = "Cycling Power Vector"
    CYCLING_POWER_CONTROL_POINT = "Cycling Power Control Point"
    GLUCOSE_MEASUREMENT = "Glucose Measurement"
    GLUCOSE_MEASUREMENT_CONTEXT = "Glucose Measurement Context"
    GLUCOSE_FEATURE = "Glucose Feature"
    MANUFACTURER_NAME_STRING = "Manufacturer Name String"
    MODEL_NUMBER_STRING = "Model Number String"
    SERIAL_NUMBER_STRING = "Serial Number String"
    FIRMWARE_REVISION_STRING = "Firmware Revision String"
    HARDWARE_REVISION_STRING = "Hardware Revision String"
    SOFTWARE_REVISION_STRING = "Software Revision String"
    DEVICE_NAME = "Device Name"
    APPEARANCE = "Appearance"
    WEIGHT_MEASUREMENT = "Weight Measurement"
    WEIGHT_SCALE_FEATURE = "Weight Scale Feature"
    BODY_COMPOSITION_MEASUREMENT = "Body Composition Measurement"
    BODY_COMPOSITION_FEATURE = "Body Composition Feature"
    ELECTRIC_CURRENT = "Electric Current"
    VOLTAGE = "Voltage"
    AVERAGE_CURRENT = "Average Current"
    AVERAGE_VOLTAGE = "Average Voltage"
    ELECTRIC_CURRENT_RANGE = "Electric Current Range"
    ELECTRIC_CURRENT_SPECIFICATION = "Electric Current Specification"
    ELECTRIC_CURRENT_STATISTICS = "Electric Current Statistics"
    VOLTAGE_SPECIFICATION = "Voltage Specification"
    VOLTAGE_STATISTICS = "Voltage Statistics"
    HIGH_VOLTAGE = "High Voltage"
    VOLTAGE_FREQUENCY = "Voltage Frequency"
    SUPPORTED_POWER_RANGE = "Supported Power Range"
    TX_POWER_LEVEL = "Tx Power Level"
    DEW_POINT = "Dew Point"
    HEAT_INDEX = "Heat Index"
    WIND_CHILL = "Wind Chill"
    TRUE_WIND_SPEED = "True Wind Speed"
    TRUE_WIND_DIRECTION = "True Wind Direction"
    APPARENT_WIND_SPEED = "Apparent Wind Speed"
    APPARENT_WIND_DIRECTION = "Apparent Wind Direction"
    MAGNETIC_DECLINATION = "Magnetic Declination"
    MAGNETIC_FLUX_DENSITY_2D = "Magnetic Flux Density 2D"
    MAGNETIC_FLUX_DENSITY_3D = "Magnetic Flux Density 3D"
    ELEVATION = "Elevation"
    BAROMETRIC_PRESSURE_TREND = "Barometric Pressure Trend"
    TIME_ZONE = "Time Zone"
    LOCAL_TIME_INFORMATION = "Local Time Information"
    POLLEN_CONCENTRATION = "Pollen Concentration"
    RAINFALL = "Rainfall"
    CO2_CONCENTRATION = "CO2 Concentration"
    VOC_CONCENTRATION = "VOC Concentration"
    NON_METHANE_VOC_CONCENTRATION = "Non Methane VOC Concentration"
    AMMONIA_CONCENTRATION = "Ammonia Concentration"
    METHANE_CONCENTRATION = "Methane Concentration"
    NITROGEN_DIOXIDE_CONCENTRATION = "Nitrogen Dioxide Concentration"
    OZONE_CONCENTRATION = "Ozone Concentration"
    PM1_CONCENTRATION = "PM1 Concentration"
    PM25_CONCENTRATION = "PM25 Concentration"
    PM10_CONCENTRATION = "PM10 Concentration"
    SULFUR_DIOXIDE_CONCENTRATION = "Sulfur Dioxide Concentration"


CHARACTERISTIC_CLASS_MAP: dict[CharacteristicName, type[BaseCharacteristic]] = {
    CharacteristicName.BATTERY_LEVEL: BatteryLevelCharacteristic,
    CharacteristicName.BATTERY_LEVEL_STATUS: BatteryPowerStateCharacteristic,
    CharacteristicName.TEMPERATURE: TemperatureCharacteristic,
    CharacteristicName.TEMPERATURE_MEASUREMENT: TemperatureMeasurementCharacteristic,
    CharacteristicName.HUMIDITY: HumidityCharacteristic,
    CharacteristicName.PRESSURE: PressureCharacteristic,
    CharacteristicName.UV_INDEX: UVIndexCharacteristic,
    CharacteristicName.ILLUMINANCE: IlluminanceCharacteristic,
    CharacteristicName.POWER_SPECIFICATION: SoundPressureLevelCharacteristic,
    CharacteristicName.HEART_RATE_MEASUREMENT: HeartRateMeasurementCharacteristic,
    CharacteristicName.BLOOD_PRESSURE_MEASUREMENT: BloodPressureMeasurementCharacteristic,
    CharacteristicName.BLOOD_PRESSURE_FEATURE: BloodPressureFeatureCharacteristic,
    CharacteristicName.CSC_MEASUREMENT: CSCMeasurementCharacteristic,
    CharacteristicName.RSC_MEASUREMENT: RSCMeasurementCharacteristic,
    CharacteristicName.CYCLING_POWER_MEASUREMENT: CyclingPowerMeasurementCharacteristic,
    CharacteristicName.CYCLING_POWER_FEATURE: CyclingPowerFeatureCharacteristic,
    CharacteristicName.CYCLING_POWER_VECTOR: CyclingPowerVectorCharacteristic,
    CharacteristicName.CYCLING_POWER_CONTROL_POINT: CyclingPowerControlPointCharacteristic,
    CharacteristicName.GLUCOSE_MEASUREMENT: GlucoseMeasurementCharacteristic,
    CharacteristicName.GLUCOSE_MEASUREMENT_CONTEXT: GlucoseMeasurementContextCharacteristic,
    CharacteristicName.GLUCOSE_FEATURE: GlucoseFeatureCharacteristic,
    CharacteristicName.MANUFACTURER_NAME_STRING: ManufacturerNameStringCharacteristic,
    CharacteristicName.MODEL_NUMBER_STRING: ModelNumberStringCharacteristic,
    CharacteristicName.SERIAL_NUMBER_STRING: SerialNumberStringCharacteristic,
    CharacteristicName.FIRMWARE_REVISION_STRING: FirmwareRevisionStringCharacteristic,
    CharacteristicName.HARDWARE_REVISION_STRING: HardwareRevisionStringCharacteristic,
    CharacteristicName.SOFTWARE_REVISION_STRING: SoftwareRevisionStringCharacteristic,
    CharacteristicName.DEVICE_NAME: DeviceNameCharacteristic,
    CharacteristicName.APPEARANCE: AppearanceCharacteristic,
    CharacteristicName.WEIGHT_MEASUREMENT: WeightMeasurementCharacteristic,
    CharacteristicName.WEIGHT_SCALE_FEATURE: WeightScaleFeatureCharacteristic,
    CharacteristicName.BODY_COMPOSITION_MEASUREMENT: BodyCompositionMeasurementCharacteristic,
    CharacteristicName.BODY_COMPOSITION_FEATURE: BodyCompositionFeatureCharacteristic,
    CharacteristicName.ELECTRIC_CURRENT: ElectricCurrentCharacteristic,
    CharacteristicName.VOLTAGE: VoltageCharacteristic,
    CharacteristicName.AVERAGE_CURRENT: AverageCurrentCharacteristic,
    CharacteristicName.AVERAGE_VOLTAGE: AverageVoltageCharacteristic,
    CharacteristicName.ELECTRIC_CURRENT_RANGE: ElectricCurrentRangeCharacteristic,
    CharacteristicName.ELECTRIC_CURRENT_SPECIFICATION: ElectricCurrentSpecificationCharacteristic,
    CharacteristicName.ELECTRIC_CURRENT_STATISTICS: ElectricCurrentStatisticsCharacteristic,
    CharacteristicName.VOLTAGE_SPECIFICATION: VoltageSpecificationCharacteristic,
    CharacteristicName.VOLTAGE_STATISTICS: VoltageStatisticsCharacteristic,
    CharacteristicName.HIGH_VOLTAGE: HighVoltageCharacteristic,
    CharacteristicName.VOLTAGE_FREQUENCY: VoltageFrequencyCharacteristic,
    CharacteristicName.SUPPORTED_POWER_RANGE: SupportedPowerRangeCharacteristic,
    CharacteristicName.TX_POWER_LEVEL: TxPowerLevelCharacteristic,
    CharacteristicName.DEW_POINT: DewPointCharacteristic,
    CharacteristicName.HEAT_INDEX: HeatIndexCharacteristic,
    CharacteristicName.WIND_CHILL: WindChillCharacteristic,
    CharacteristicName.TRUE_WIND_SPEED: TrueWindSpeedCharacteristic,
    CharacteristicName.TRUE_WIND_DIRECTION: TrueWindDirectionCharacteristic,
    CharacteristicName.APPARENT_WIND_SPEED: ApparentWindSpeedCharacteristic,
    CharacteristicName.APPARENT_WIND_DIRECTION: ApparentWindDirectionCharacteristic,
    CharacteristicName.MAGNETIC_DECLINATION: MagneticDeclinationCharacteristic,
    CharacteristicName.MAGNETIC_FLUX_DENSITY_2D: MagneticFluxDensity2DCharacteristic,
    CharacteristicName.MAGNETIC_FLUX_DENSITY_3D: MagneticFluxDensity3DCharacteristic,
    CharacteristicName.ELEVATION: ElevationCharacteristic,
    CharacteristicName.BAROMETRIC_PRESSURE_TREND: BarometricPressureTrendCharacteristic,
    CharacteristicName.TIME_ZONE: TimeZoneCharacteristic,
    CharacteristicName.LOCAL_TIME_INFORMATION: LocalTimeInformationCharacteristic,
    CharacteristicName.POLLEN_CONCENTRATION: PollenConcentrationCharacteristic,
    CharacteristicName.RAINFALL: RainfallCharacteristic,
    CharacteristicName.CO2_CONCENTRATION: CO2ConcentrationCharacteristic,
    CharacteristicName.VOC_CONCENTRATION: VOCConcentrationCharacteristic,
    CharacteristicName.NON_METHANE_VOC_CONCENTRATION: NonMethaneVOCConcentrationCharacteristic,
    CharacteristicName.AMMONIA_CONCENTRATION: AmmoniaConcentrationCharacteristic,
    CharacteristicName.METHANE_CONCENTRATION: MethaneConcentrationCharacteristic,
    CharacteristicName.NITROGEN_DIOXIDE_CONCENTRATION: NitrogenDioxideConcentrationCharacteristic,
    CharacteristicName.OZONE_CONCENTRATION: OzoneConcentrationCharacteristic,
    CharacteristicName.PM1_CONCENTRATION: PM1ConcentrationCharacteristic,
    CharacteristicName.PM25_CONCENTRATION: PM25ConcentrationCharacteristic,
    CharacteristicName.PM10_CONCENTRATION: PM10ConcentrationCharacteristic,
    CharacteristicName.SULFUR_DIOXIDE_CONCENTRATION: SulfurDioxideConcentrationCharacteristic,
}

CHARACTERISTIC_CLASS_MAP_STR: dict[str, type[BaseCharacteristic]] = {
    e.value: c for e, c in CHARACTERISTIC_CLASS_MAP.items()
}


class CharacteristicRegistry:
    """Encapsulates all GATT characteristic registry operations."""

    @staticmethod
    def get_characteristic_class(
        name: str | CharacteristicName,
    ) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given name or enum.

        Args:
            name: The characteristic name or enum

        Returns:
            The characteristic class if found, None otherwise.
        """
        if isinstance(name, CharacteristicName):
            return CHARACTERISTIC_CLASS_MAP.get(name)
        return CHARACTERISTIC_CLASS_MAP_STR.get(name)

    @staticmethod
    def list_all_characteristic_names() -> list[str]:
        """List all supported characteristic names as strings.

        Returns:
            List of all characteristic names.
        """
        return [e.value for e in CharacteristicName]

    @staticmethod
    def list_all_characteristic_enums() -> list[CharacteristicName]:
        """List all supported characteristic names as enum values.

        Returns:
            List of all characteristic enum values.
        """
        return list(CharacteristicName)

    @staticmethod
    def create_characteristic(
        uuid_or_name: str | CharacteristicName, properties: set[str] | None = None
    ) -> BaseCharacteristic | None:
        """Create a characteristic instance from a UUID or enum name.

        For type safety and better IDE support, prefer using CharacteristicName enums
        over raw UUID strings. Example:
            # Preferred (type-safe):
            temp_char = CharacteristicRegistry.create_characteristic(
                CharacteristicName.TEMPERATURE
            )

            # Also supported (but less type-safe):
            temp_char = CharacteristicRegistry.create_characteristic("2A6E")

        Args:
            uuid_or_name: The characteristic UUID (string) or CharacteristicName enum.
            properties: Optional set of characteristic properties.

        Returns:
            Characteristic instance if found, None otherwise.
        """
        # Handle enum input by looking up the class directly
        if isinstance(uuid_or_name, CharacteristicName):
            char_cls = CHARACTERISTIC_CLASS_MAP.get(uuid_or_name)
            if char_cls:
                try:
                    return char_cls(uuid="", properties=properties or set())
                except (ValueError, TypeError, AttributeError):
                    return None
            return None

        # Handle string UUID input (existing logic)
        norm_uuid = uuid_or_name.replace("-", "").upper()
        short_uuid = norm_uuid[4:8] if len(norm_uuid) == 32 else norm_uuid
        for _, char_cls in CHARACTERISTIC_CLASS_MAP.items():
            try:
                instance = char_cls(uuid=norm_uuid, properties=properties or set())
                char_uuid_norm = instance.char_uuid.replace("-", "").upper()
                char_uuid_short = (
                    char_uuid_norm[4:8] if len(char_uuid_norm) == 32 else char_uuid_norm
                )
                if char_uuid_norm == norm_uuid or char_uuid_short == short_uuid:
                    return instance
            except (ValueError, TypeError, AttributeError):
                continue
        return None

    @staticmethod
    def create_characteristic_by_name(
        name: CharacteristicName, properties: set[str] | None = None
    ) -> BaseCharacteristic | None:
        """Create a characteristic instance by enum name (type-safe).

        This is the preferred method for creating characteristics as it provides
        full type safety and IDE autocompletion. Example:

            temp_char = CharacteristicRegistry.create_characteristic_by_name(
                CharacteristicName.TEMPERATURE
            )

            battery_char = CharacteristicRegistry.create_characteristic_by_name(
                CharacteristicName.BATTERY_LEVEL,
                properties={"read", "notify"}
            )

        Args:
            name: The CharacteristicName enum value.
            properties: Optional set of characteristic properties.

        Returns:
            Characteristic instance if the enum is valid, None otherwise.
        """
        char_cls = CHARACTERISTIC_CLASS_MAP.get(name)
        if char_cls:
            try:
                return char_cls(uuid="", properties=properties or set())
            except (ValueError, TypeError, AttributeError):
                return None
        return None

    @staticmethod
    def get_characteristic_class_by_uuid(uuid: str) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given UUID.

        Args:
            uuid: The characteristic UUID (with or without dashes).

        Returns:
            The characteristic class if found, None otherwise.
        """
        norm_uuid = uuid.replace("-", "").upper()
        for char_cls in CHARACTERISTIC_CLASS_MAP.values():
            try:
                instance = char_cls(uuid=norm_uuid, properties=set())
                if instance.char_uuid.replace("-", "").upper() == norm_uuid:
                    return char_cls
            except (ValueError, TypeError, AttributeError):
                continue
        return None

    @staticmethod
    def get_all_characteristics() -> dict[str, type[BaseCharacteristic]]:
        """Get all supported characteristics as a dictionary.

        Returns:
            Dictionary mapping characteristic names to their classes.
        """
        return {e.value: c for e, c in CHARACTERISTIC_CLASS_MAP.items()}


__all__ = [
    # Core types
    "BaseCharacteristic",
    "CharacteristicName",
    "CharacteristicRegistry",
    # Characteristic classes
    "AmmoniaConcentrationCharacteristic",
    "ApparentWindDirectionCharacteristic",
    "ApparentWindSpeedCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    "BatteryLevelCharacteristic",
    "BatteryPowerStateCharacteristic",
    "BloodPressureFeatureCharacteristic",
    "BloodPressureMeasurementCharacteristic",
    "BodyCompositionFeatureCharacteristic",
    "BodyCompositionMeasurementCharacteristic",
    "CO2ConcentrationCharacteristic",
    "CSCMeasurementCharacteristic",
    "CyclingPowerControlPointCharacteristic",
    "CyclingPowerFeatureCharacteristic",
    "CyclingPowerMeasurementCharacteristic",
    "CyclingPowerVectorCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "ModelNumberStringCharacteristic",
    "SerialNumberStringCharacteristic",
    "SoftwareRevisionStringCharacteristic",
    "DewPointCharacteristic",
    "ElectricCurrentCharacteristic",
    "ElectricCurrentRangeCharacteristic",
    "ElectricCurrentSpecificationCharacteristic",
    "ElectricCurrentStatisticsCharacteristic",
    "ElevationCharacteristic",
    "AppearanceCharacteristic",
    "DeviceNameCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "HeartRateMeasurementCharacteristic",
    "HeatIndexCharacteristic",
    "HighVoltageCharacteristic",
    "HumidityCharacteristic",
    "IlluminanceCharacteristic",
    "LocalTimeInformationCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "MethaneConcentrationCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "OzoneConcentrationCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PollenConcentrationCharacteristic",
    "PressureCharacteristic",
    "PulseOximetryMeasurementCharacteristic",
    "RainfallCharacteristic",
    "RSCMeasurementCharacteristic",
    "SoundPressureLevelCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "TemperatureCharacteristic",
    "TemperatureMeasurementCharacteristic",
    "TimeZoneCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TxPowerLevelCharacteristic",
    "UVIndexCharacteristic",
    "VOCConcentrationCharacteristic",
    "VoltageCharacteristic",
    "VoltageFrequencyCharacteristic",
    "VoltageSpecificationCharacteristic",
    "VoltageStatisticsCharacteristic",
    "WeightMeasurementCharacteristic",
    "WeightScaleFeatureCharacteristic",
    "WindChillCharacteristic",
    # Registry mappings
    "CHARACTERISTIC_CLASS_MAP",
    "CHARACTERISTIC_CLASS_MAP_STR",
]
