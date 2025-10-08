"""Round trip tests for all GATT characteristics.

Ensures that encode(decode(data)) == data for all characteristics.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import (
    AmmoniaConcentrationCharacteristic,
    ApparentWindDirectionCharacteristic,
    ApparentWindSpeedCharacteristic,
    AppearanceCharacteristic,
    AverageCurrentCharacteristic,
    AverageVoltageCharacteristic,
    BarometricPressureTrendCharacteristic,
    BaseCharacteristic,
    BatteryLevelCharacteristic,
    BatteryPowerStateCharacteristic,
    BloodPressureFeatureCharacteristic,
    BloodPressureMeasurementCharacteristic,
    BodyCompositionFeatureCharacteristic,
    BodyCompositionMeasurementCharacteristic,
    CO2ConcentrationCharacteristic,
    CSCMeasurementCharacteristic,
    CyclingPowerControlPointCharacteristic,
    CyclingPowerFeatureCharacteristic,
    CyclingPowerMeasurementCharacteristic,
    CyclingPowerVectorCharacteristic,
    DeviceNameCharacteristic,
    DewPointCharacteristic,
    ElectricCurrentCharacteristic,
    ElectricCurrentRangeCharacteristic,
    ElectricCurrentSpecificationCharacteristic,
    ElectricCurrentStatisticsCharacteristic,
    ElevationCharacteristic,
    FirmwareRevisionStringCharacteristic,
    GlucoseFeatureCharacteristic,
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementContextCharacteristic,
    HardwareRevisionStringCharacteristic,
    HeartRateMeasurementCharacteristic,
    HeatIndexCharacteristic,
    HighVoltageCharacteristic,
    HumidityCharacteristic,
    IlluminanceCharacteristic,
    LocalTimeInformationCharacteristic,
    MagneticDeclinationCharacteristic,
    MagneticFluxDensity2DCharacteristic,
    MagneticFluxDensity3DCharacteristic,
    ManufacturerNameStringCharacteristic,
    MethaneConcentrationCharacteristic,
    ModelNumberStringCharacteristic,
    NitrogenDioxideConcentrationCharacteristic,
    NoiseCharacteristic,
    NonMethaneVOCConcentrationCharacteristic,
    OzoneConcentrationCharacteristic,
    PM1ConcentrationCharacteristic,
    PM10ConcentrationCharacteristic,
    PM25ConcentrationCharacteristic,
    PollenConcentrationCharacteristic,
    PressureCharacteristic,
    PulseOximetryMeasurementCharacteristic,
    RainfallCharacteristic,
    RSCMeasurementCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
    SulfurDioxideConcentrationCharacteristic,
    SupportedPowerRangeCharacteristic,
    TemperatureCharacteristic,
    TemperatureMeasurementCharacteristic,
    TimeZoneCharacteristic,
    TrueWindDirectionCharacteristic,
    TrueWindSpeedCharacteristic,
    TxPowerLevelCharacteristic,
    UVIndexCharacteristic,
    VOCConcentrationCharacteristic,
    VoltageCharacteristic,
    VoltageFrequencyCharacteristic,
    VoltageSpecificationCharacteristic,
    VoltageStatisticsCharacteristic,
    WeightMeasurementCharacteristic,
    WeightScaleFeatureCharacteristic,
    WindChillCharacteristic,
)

ROUND_TRIP_TEST_DATA = [
    (BatteryLevelCharacteristic, bytearray([75])),
    (BatteryPowerStateCharacteristic, bytearray([0x00])),
    (TemperatureCharacteristic, bytearray([0xC4, 0x09])),
    (HumidityCharacteristic, bytearray([0x3C, 0x00])),
    (PressureCharacteristic, bytearray([0x22, 0x8E, 0x8F, 0x00])),
    (UVIndexCharacteristic, bytearray([5])),
    (IlluminanceCharacteristic, bytearray([0xE8, 0x03, 0x00])),
    (HeartRateMeasurementCharacteristic, bytearray([0x00, 0x48])),
    (DeviceNameCharacteristic, bytearray(b"Hello")),
    (AppearanceCharacteristic, bytearray([0x00, 0x00])),
    (ManufacturerNameStringCharacteristic, bytearray(b"Test")),
    (ModelNumberStringCharacteristic, bytearray(b"Test")),
    (SerialNumberStringCharacteristic, bytearray(b"Test")),
    (HardwareRevisionStringCharacteristic, bytearray(b"Test")),
    (FirmwareRevisionStringCharacteristic, bytearray(b"Test")),
    (SoftwareRevisionStringCharacteristic, bytearray(b"Test")),
    (TxPowerLevelCharacteristic, bytearray([10])),
    (TimeZoneCharacteristic, bytearray([2])),
    (LocalTimeInformationCharacteristic, bytearray([0x00, 0x00])),
    (ElevationCharacteristic, bytearray([0x10, 0x27, 0x00])),
    (MagneticDeclinationCharacteristic, bytearray([0x40, 0x46])),
    (MagneticFluxDensity2DCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (
        MagneticFluxDensity3DCharacteristic,
        bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    ),
    (PollenConcentrationCharacteristic, bytearray([0x0A, 0x00, 0x00])),
    (RainfallCharacteristic, bytearray([0x00, 0x00])),
    (DewPointCharacteristic, bytearray([0xC4])),
    (HeatIndexCharacteristic, bytearray([0x19])),
    (WindChillCharacteristic, bytearray([0xC4])),
    (TrueWindSpeedCharacteristic, bytearray([0x64, 0x00])),
    (TrueWindDirectionCharacteristic, bytearray([0x00, 0x00])),
    (ApparentWindSpeedCharacteristic, bytearray([0x64, 0x00])),
    (ApparentWindDirectionCharacteristic, bytearray([0x00, 0x00])),
    (BarometricPressureTrendCharacteristic, bytearray([0x01])),
    (CO2ConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (VOCConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (NonMethaneVOCConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (AmmoniaConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (MethaneConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (NitrogenDioxideConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (OzoneConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (PM1ConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (PM25ConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (PM10ConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (SulfurDioxideConcentrationCharacteristic, bytearray([0xE8, 0x03])),
    (VoltageCharacteristic, bytearray([0x88, 0x13])),
    (ElectricCurrentCharacteristic, bytearray([0x88, 0x13])),
    (AverageVoltageCharacteristic, bytearray([0x88, 0x13])),
    (AverageCurrentCharacteristic, bytearray([0x88, 0x13])),
    (HighVoltageCharacteristic, bytearray([0x88, 0x13, 0x00])),
    (VoltageFrequencyCharacteristic, bytearray([0x88, 0x13])),
    (VoltageSpecificationCharacteristic, bytearray([0x88, 0x13, 0x88, 0x13])),
    (
        VoltageStatisticsCharacteristic,
        bytearray([0xE8, 0x03, 0xB8, 0x0B, 0xD0, 0x07]),
    ),
    (ElectricCurrentRangeCharacteristic, bytearray([0x88, 0x13, 0x88, 0x13])),
    (
        ElectricCurrentSpecificationCharacteristic,
        bytearray([0x88, 0x13, 0x88, 0x13]),
    ),
    (
        ElectricCurrentStatisticsCharacteristic,
        bytearray([0xE8, 0x03, 0xD0, 0x07, 0xDC, 0x05]),
    ),
    (
        SupportedPowerRangeCharacteristic,
        bytearray([0xE8, 0x03, 0xD0, 0x07]),
    ),
    (NoiseCharacteristic, bytearray([0x64])),
    (
        BloodPressureMeasurementCharacteristic,
        bytearray([0x00, 0xC8, 0x00, 0x00, 0x00, 0x00, 0x00]),
    ),
    (BloodPressureFeatureCharacteristic, bytearray([0x00, 0x00])),
    (CSCMeasurementCharacteristic, bytearray([0x00])),
    (RSCMeasurementCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (CyclingPowerMeasurementCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (CyclingPowerFeatureCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (
        CyclingPowerVectorCharacteristic,
        bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    ),
    (CyclingPowerControlPointCharacteristic, bytearray([0x01])),
    (
        GlucoseMeasurementCharacteristic,
        bytearray([0x00, 0x00, 0x00, 0xE2, 0x07, 0x0A, 0x11, 0x0F, 0x2A, 0x00, 0x00, 0x00]),
    ),
    (GlucoseMeasurementContextCharacteristic, bytearray([0x00, 0x00, 0x00])),
    (GlucoseFeatureCharacteristic, bytearray([0x00, 0x00])),
    (WeightMeasurementCharacteristic, bytearray([0x00, 0x00, 0x00])),
    (WeightScaleFeatureCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (
        BodyCompositionMeasurementCharacteristic,
        bytearray([0x1F, 0x00, 0x00, 0x00]),
    ),
    (BodyCompositionFeatureCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00])),
    (TemperatureMeasurementCharacteristic, bytearray([0x00, 0x90, 0xD0, 0x03, 0xFC])),
    (PulseOximetryMeasurementCharacteristic, bytearray([0x00, 0x00, 0x00, 0x00, 0x00])),
]


class TestRoundTrip:
    """Round trip tests for all characteristics."""

    def test_all_characteristics_are_tested(self):
        """Test that every characteristic class is included in
        ROUND_TRIP_TEST_DATA."""
        import bluetooth_sig.gatt.characteristics as char_module

        # Get all classes from the characteristics module that inherit from BaseCharacteristic
        all_characteristic_classes: set[Any] = set()
        for _name, obj in inspect.getmembers(char_module):
            if inspect.isclass(obj) and issubclass(obj, BaseCharacteristic) and obj is not BaseCharacteristic:
                all_characteristic_classes.add(obj)

        # Get all classes from ROUND_TRIP_TEST_DATA
        tested_classes: set[Any] = {char_class for char_class, _ in ROUND_TRIP_TEST_DATA}

        # Check that all characteristic classes are tested
        missing_classes = all_characteristic_classes - tested_classes
        extra_classes = tested_classes - all_characteristic_classes

        assert not missing_classes, f"Missing round trip tests for: {missing_classes}"
        assert not extra_classes, f"Extra classes in test data that don't exist: {extra_classes}"

    @pytest.mark.parametrize("char_class,test_data", ROUND_TRIP_TEST_DATA)
    def test_round_trip(self, char_class: type[BaseCharacteristic], test_data: bytearray):
        """Test that encoding and decoding preserve data."""
        char = char_class()  # SIG characteristics don't need UUID parameter
        parsed = char.decode_value(test_data)
        encoded = char.encode_value(parsed)
        assert encoded == test_data
