"""Bluetooth SIG GATT characteristic registry.

This module contains the characteristic registry implementation and
class mappings. CharacteristicName enum is now centralized in
types.gatt_enums to avoid circular imports.
"""

from __future__ import annotations

import threading

from ...types.gatt_enums import CharacteristicName
from ...types.uuid import BluetoothUUID
from .base import BaseCharacteristic

# Export for other modules to import
__all__ = ["CharacteristicName", "CharacteristicRegistry"]

# Lazy initialization of the class mappings to avoid circular imports

# Lazy initialization of the class mappings to avoid circular imports
_characteristic_class_map: dict[CharacteristicName, type[BaseCharacteristic]] | None = None
_characteristic_class_map_str: dict[str, type[BaseCharacteristic]] | None = None


def _build_characteristic_class_map() -> dict[CharacteristicName, type[BaseCharacteristic]]:
    """Build the characteristic class mapping.

    This function is called lazily to avoid circular imports.
    """
    # pylint: disable=import-outside-toplevel,too-many-locals,too-many-statements
    from .ammonia_concentration import AmmoniaConcentrationCharacteristic
    from .apparent_wind_direction import ApparentWindDirectionCharacteristic
    from .apparent_wind_speed import ApparentWindSpeedCharacteristic
    from .average_current import AverageCurrentCharacteristic
    from .average_voltage import AverageVoltageCharacteristic
    from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
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
    from .electric_current_specification import (
        ElectricCurrentSpecificationCharacteristic,
    )
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
    from .nitrogen_dioxide_concentration import (
        NitrogenDioxideConcentrationCharacteristic,
    )
    from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
    from .ozone_concentration import OzoneConcentrationCharacteristic
    from .pm1_concentration import PM1ConcentrationCharacteristic
    from .pm10_concentration import PM10ConcentrationCharacteristic
    from .pm25_concentration import PM25ConcentrationCharacteristic
    from .pollen_concentration import PollenConcentrationCharacteristic
    from .pressure import PressureCharacteristic
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

    return {
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


def _get_characteristic_class_map() -> dict[CharacteristicName, type[BaseCharacteristic]]:
    """Get the characteristic class map, building it if necessary."""
    # pylint: disable=global-statement
    global _characteristic_class_map
    if _characteristic_class_map is None:
        _characteristic_class_map = _build_characteristic_class_map()
    return _characteristic_class_map


# Public API - enum-keyed map
CHARACTERISTIC_CLASS_MAP = _get_characteristic_class_map()


class CharacteristicRegistry:
    """Encapsulates all GATT characteristic registry operations."""

    _lock = threading.RLock()
    _custom_characteristic_classes: dict[BluetoothUUID, type[BaseCharacteristic]] = {}

    @classmethod
    def register_characteristic_class(
        cls, uuid: str | BluetoothUUID, char_cls: type[BaseCharacteristic], override: bool = False
    ) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID)
            char_cls: The characteristic class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If char_cls does not inherit from BaseCharacteristic
            ValueError: If UUID conflicts with existing registration and override=False
        """
        # Runtime safety check retained in case of dynamic caller misuse despite type hints.
        if not isinstance(char_cls, type) or not issubclass(char_cls, BaseCharacteristic):  # type: ignore[unreachable]
            raise TypeError(f"Class {char_cls!r} must inherit from BaseCharacteristic")

        # Always normalize UUID to BluetoothUUID
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid

        # Determine if this UUID is already represented by a SIG (built-in) characteristic
        def _find_sig_class_for_uuid(target: BluetoothUUID) -> type[BaseCharacteristic] | None:
            for candidate in _get_characteristic_class_map().values():
                try:
                    # Direct protected access acceptable within internal registry module.
                    resolved_uuid_obj = candidate._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
                    if resolved_uuid_obj and (
                        resolved_uuid_obj.normalized == target.normalized  # type: ignore[attr-defined]
                        or resolved_uuid_obj.short_form == target.short_form  # type: ignore[attr-defined]
                    ):
                        return candidate
                except Exception:  # pylint: disable=broad-exception-caught
                    continue
            return None

        sig_cls = _find_sig_class_for_uuid(bt_uuid)

        with cls._lock:
            # Prevent duplicate custom registration unless override explicitly requested
            if not override and bt_uuid in cls._custom_characteristic_classes:
                raise ValueError(f"UUID {bt_uuid} already registered. Use override=True to replace.")

            # If collides with a SIG characteristic, enforce explicit override + permission flag
            if sig_cls is not None:
                if not override:
                    raise ValueError(
                        f"UUID {bt_uuid} conflicts with existing SIG characteristic {sig_cls.__name__}. "
                        "Use override=True to replace."
                    )
                # Require an explicit opt‑in marker on the custom class
                try:
                    allows_override = bool(char_cls._allows_sig_override)  # type: ignore[attr-defined]
                except AttributeError:
                    allows_override = False
                if not allows_override:
                    raise ValueError(
                        "Override of SIG characteristic "
                        f"{sig_cls.__name__} requires _allows_sig_override=True on {char_cls.__name__}."
                    )

            cls._custom_characteristic_classes[bt_uuid] = char_cls

    @classmethod
    def unregister_characteristic_class(cls, uuid: str | BluetoothUUID) -> None:
        """Unregister a custom characteristic class.

        Args:
            uuid: The characteristic UUID to unregister (string or BluetoothUUID)
        """
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        with cls._lock:
            cls._custom_characteristic_classes.pop(bt_uuid, None)

    @staticmethod
    def get_characteristic_class(
        name: CharacteristicName,
    ) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given CharacteristicName enum.

        This API is enum-only. Callers must pass a `CharacteristicName`.
        """
        return _get_characteristic_class_map().get(name)

    @staticmethod
    # Enum-only registry: string-to-enum helpers removed to eliminate legacy usage.

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

    @classmethod
    def create_characteristic(
        cls,
        uuid: str | BluetoothUUID,
    ) -> BaseCharacteristic | None:
        """Create a characteristic instance from a UUID.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID).

        Returns:
            Characteristic instance if found, None otherwise.
        """
        # Handle UUID input
        if isinstance(uuid, BluetoothUUID):
            uuid_obj = uuid
        else:
            try:
                uuid_obj = BluetoothUUID(uuid)
            except ValueError:
                # Invalid UUID format, cannot create characteristic
                return None

        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_characteristic_classes.get(uuid_obj):
                return custom_cls()

        for _, char_cls in _get_characteristic_class_map().items():
            # Try to resolve UUID at class level first
            resolved_uuid = char_cls._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
            if resolved_uuid and (
                resolved_uuid.normalized == uuid_obj.normalized or resolved_uuid.short_form == uuid_obj.short_form
            ):
                return char_cls()
            # Fallback to instantiation if class-level resolution fails
            instance = char_cls()
            char_uuid_obj = instance.uuid
            if char_uuid_obj.normalized == uuid_obj.normalized or char_uuid_obj.short_form == uuid_obj.short_form:
                return instance
        return None

    @classmethod
    def get_characteristic_class_by_uuid(cls, uuid: str | BluetoothUUID) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given UUID.

        Args:
            uuid: The characteristic UUID (with or without dashes).

        Returns:
            The characteristic class if found, None otherwise.
        """
        # Always normalize UUID to BluetoothUUID
        try:
            bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        except ValueError:
            return None

        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_characteristic_classes.get(bt_uuid):
                return custom_cls

        for char_cls in _get_characteristic_class_map().values():
            # Try to resolve UUID at class level first
            resolved_uuid = char_cls._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
            if resolved_uuid and (
                resolved_uuid.normalized == bt_uuid.normalized or resolved_uuid.short_form == bt_uuid.short_form
            ):
                return char_cls
            # Fallback to instantiation if class-level resolution fails
            instance = char_cls()
            char_uuid_obj = instance.uuid
            if char_uuid_obj.normalized == bt_uuid.normalized or char_uuid_obj.short_form == bt_uuid.short_form:
                return char_cls
        return None

    @staticmethod
    def get_all_characteristics() -> dict[CharacteristicName, type[BaseCharacteristic]]:
        """Get all registered characteristic classes.

        Returns:
            Dictionary mapping characteristic names to classes
        """
        result: dict[CharacteristicName, type[BaseCharacteristic]] = {}
        for name, char_cls in _get_characteristic_class_map().items():
            result[name] = char_cls
        return result

    @classmethod
    def clear_custom_registrations(cls) -> None:
        """Clear all custom characteristic registrations (for testing)."""
        cls._custom_characteristic_classes.clear()
