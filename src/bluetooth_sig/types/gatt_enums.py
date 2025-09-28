"""Core GATT enumerations for strong typing.

Defines enums for GATT properties, value types, characteristic names,
and other core BLE concepts to replace string usage with type-safe
alternatives.
"""

from __future__ import annotations

from enum import Enum


class GattProperty(Enum):
    """GATT characteristic properties defined by Bluetooth SIG."""

    BROADCAST = "broadcast"
    READ = "read"
    WRITE_WITHOUT_RESPONSE = "write-without-response"
    WRITE = "write"
    NOTIFY = "notify"
    INDICATE = "indicate"
    AUTHENTICATED_SIGNED_WRITES = "authenticated-signed-writes"
    EXTENDED_PROPERTIES = "extended-properties"
    RELIABLE_WRITE = "reliable-write"
    WRITABLE_AUXILIARIES = "writable-auxiliaries"


class ValueType(Enum):
    """Data types for characteristic values."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BYTES = "bytes"
    BOOL = "bool"
    DATETIME = "datetime"
    UUID = "uuid"


class DataType(Enum):
    """Bluetooth SIG data types from GATT specifications."""

    BOOLEAN = "boolean"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT24 = "uint24"
    UINT32 = "uint32"
    UINT64 = "uint64"
    SINT8 = "sint8"
    SINT16 = "sint16"
    SINT24 = "sint24"
    SINT32 = "sint32"
    SINT64 = "sint64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    UTF8S = "utf8s"
    STRUCT = "struct"
    MEDFLOAT16 = "medfloat16"
    MEDFLOAT32 = "medfloat32"


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
    # Environmental characteristics
    DEW_POINT = "Dew Point"
    HEAT_INDEX = "Heat Index"
    WIND_CHILL = "Wind Chill"
    TRUE_WIND_SPEED = "True Wind Speed"
    TRUE_WIND_DIRECTION = "True Wind Direction"
    APPARENT_WIND_SPEED = "Apparent Wind Speed"
    APPARENT_WIND_DIRECTION = "Apparent Wind Direction"
    MAGNETIC_DECLINATION = "Magnetic Declination"
    ELEVATION = "Elevation"
    MAGNETIC_FLUX_DENSITY_2D = "Magnetic Flux Density - 2D"
    MAGNETIC_FLUX_DENSITY_3D = "Magnetic Flux Density - 3D"
    BAROMETRIC_PRESSURE_TREND = "Barometric Pressure Trend"
    POLLEN_CONCENTRATION = "Pollen Concentration"
    RAINFALL = "Rainfall"
    TIME_ZONE = "Time Zone"
    LOCAL_TIME_INFORMATION = "Local Time Information"
    # Gas sensor characteristics
    AMMONIA_CONCENTRATION = "Ammonia Concentration"
    CO2_CONCENTRATION = "Carbon Dioxide Concentration"
    METHANE_CONCENTRATION = "Methane Concentration"
    NITROGEN_DIOXIDE_CONCENTRATION = "Nitrogen Dioxide Concentration"
    NON_METHANE_VOC_CONCENTRATION = "Non-Methane Volatile Organic Compounds Concentration"
    OZONE_CONCENTRATION = "Ozone Concentration"
    PM1_CONCENTRATION = "Particulate Matter - PM1 Concentration"
    PM10_CONCENTRATION = "Particulate Matter - PM10 Concentration"
    PM25_CONCENTRATION = "Particulate Matter - PM2.5 Concentration"
    SULFUR_DIOXIDE_CONCENTRATION = "Sulfur Dioxide Concentration"
    VOC_CONCENTRATION = "Volatile Organic Compounds Concentration"
    # Power characteristics
    ELECTRIC_CURRENT = "Electric Current"
    ELECTRIC_CURRENT_RANGE = "Electric Current Range"
    ELECTRIC_CURRENT_SPECIFICATION = "Electric Current Specification"
    ELECTRIC_CURRENT_STATISTICS = "Electric Current Statistics"
    VOLTAGE = "Voltage"
    VOLTAGE_FREQUENCY = "Voltage Frequency"
    VOLTAGE_SPECIFICATION = "Voltage Specification"
    VOLTAGE_STATISTICS = "Voltage Statistics"
    HIGH_VOLTAGE = "High Voltage"
    AVERAGE_CURRENT = "Average Current"
    AVERAGE_VOLTAGE = "Average Voltage"
    SUPPORTED_POWER_RANGE = "Supported Power Range"
    # Audio characteristics
    SOUND_PRESSURE_LEVEL = "Sound Pressure Level"
    # Pulse oximetry
    PULSE_OXIMETRY_CONTINUOUS_MEASUREMENT = "Pulse Oximetry Continuous Measurement"
    # Generic Access
    TX_POWER_LEVEL = "Tx Power Level"
