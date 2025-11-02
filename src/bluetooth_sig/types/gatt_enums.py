"""Core GATT enumerations for strong typing.

Defines enums for GATT properties, value types, characteristic names,
and other core BLE concepts to replace string usage with type-safe
alternatives.
"""

from __future__ import annotations

from enum import Enum, IntEnum


class DayOfWeek(IntEnum):
    """Day of week enumeration per ISO 8601.

    Used by Current Time Service and other time-related characteristics.
    Values follow ISO 8601 standard (Monday=1, Sunday=7, Unknown=0).
    """

    UNKNOWN = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class AdjustReason(IntEnum):
    """Time adjustment reason flags.

    Used by Current Time Service to indicate why time was adjusted.
    Can be combined as bitfield flags.
    """

    MANUAL_TIME_UPDATE = 1 << 0  # Bit 0
    EXTERNAL_REFERENCE_TIME_UPDATE = 1 << 1  # Bit 1
    CHANGE_OF_TIME_ZONE = 1 << 2  # Bit 2
    CHANGE_OF_DST = 1 << 3  # Bit 3


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
    # Encryption and authentication properties
    ENCRYPT_READ = "encrypt-read"
    ENCRYPT_WRITE = "encrypt-write"
    ENCRYPT_NOTIFY = "encrypt-notify"
    AUTH_READ = "auth-read"
    AUTH_WRITE = "auth-write"
    AUTH_NOTIFY = "auth-notify"


class ValueType(Enum):
    """Data types for characteristic values."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BYTES = "bytes"
    BOOL = "bool"
    DATETIME = "datetime"
    UUID = "uuid"
    DICT = "dict"
    VARIOUS = "various"
    UNKNOWN = "unknown"


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
    VARIOUS = "various"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, type_str: str | None) -> DataType:
        """Convert string representation to DataType enum.

        Args:
            type_str: String representation of data type (case-insensitive)

        Returns:
            Corresponding DataType enum, or DataType.UNKNOWN if not found
        """
        if not type_str:
            return cls.UNKNOWN

        # Handle common aliases
        type_str = type_str.lower()
        aliases = {
            "utf16s": cls.UTF8S,  # TODO utf16s maps to UTF8S for now
            "sfloat": cls.MEDFLOAT16,  # IEEE-11073 16-bit SFLOAT
            "float": cls.FLOAT32,  # IEEE-11073 32-bit FLOAT
            "variable": cls.STRUCT,  # variable maps to STRUCT
        }

        if type_str in aliases:
            return aliases[type_str]

        # Try direct match
        for member in cls:
            if member.value == type_str:
                return member

        return cls.UNKNOWN

    def to_value_type(self) -> ValueType:
        """Convert DataType to internal ValueType enum.

        Returns:
            Corresponding ValueType for this data type
        """
        mapping = {
            # Integer types
            self.SINT8: ValueType.INT,
            self.UINT8: ValueType.INT,
            self.SINT16: ValueType.INT,
            self.UINT16: ValueType.INT,
            self.UINT24: ValueType.INT,
            self.SINT32: ValueType.INT,
            self.UINT32: ValueType.INT,
            self.UINT64: ValueType.INT,
            self.SINT64: ValueType.INT,
            # Float types
            self.FLOAT32: ValueType.FLOAT,
            self.FLOAT64: ValueType.FLOAT,
            self.MEDFLOAT16: ValueType.FLOAT,
            self.MEDFLOAT32: ValueType.FLOAT,
            # String types
            self.UTF8S: ValueType.STRING,
            # Boolean type
            self.BOOLEAN: ValueType.BOOL,
            # Struct/opaque data
            self.STRUCT: ValueType.BYTES,
            # Meta types
            self.VARIOUS: ValueType.VARIOUS,
            self.UNKNOWN: ValueType.UNKNOWN,
        }
        return mapping.get(self, ValueType.UNKNOWN)

    def to_python_type(self) -> str:
        """Convert DataType to Python type string.

        Returns:
            Corresponding Python type string
        """
        mapping = {
            # Integer types
            self.UINT8: "int",
            self.UINT16: "int",
            self.UINT24: "int",
            self.UINT32: "int",
            self.UINT64: "int",
            self.SINT8: "int",
            self.SINT16: "int",
            self.SINT24: "int",
            self.SINT32: "int",
            self.SINT64: "int",
            # Float types
            self.FLOAT32: "float",
            self.FLOAT64: "float",
            self.MEDFLOAT16: "float",
            self.MEDFLOAT32: "float",
            # String types
            self.UTF8S: "string",
            # Boolean type
            self.BOOLEAN: "boolean",
            # Struct/opaque data
            self.STRUCT: "bytes",
            # Meta types
            self.VARIOUS: "various",
            self.UNKNOWN: "unknown",
        }
        return mapping.get(self, "bytes")


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
    INTERMEDIATE_CUFF_PRESSURE = "Intermediate Cuff Pressure"
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
    BODY_SENSOR_LOCATION = "Body Sensor Location"
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
    NOISE = "Noise"
    # Pulse oximetry
    PULSE_OXIMETRY_CONTINUOUS_MEASUREMENT = "Pulse Oximetry Continuous Measurement"
    PLX_FEATURES = "PLX Features"
    LOCATION_AND_SPEED = "Location and Speed"
    NAVIGATION = "Navigation"
    POSITION_QUALITY = "Position Quality"
    LN_FEATURE = "LN Feature"
    LN_CONTROL_POINT = "LN Control Point"
    SERVICE_CHANGED = "Service Changed"
    ALERT_STATUS = "Alert Status"
    RINGER_SETTING = "Ringer Setting"
    RINGER_CONTROL_POINT = "Ringer Control Point"
    # Alert Notification Service characteristics
    NEW_ALERT = "New Alert"
    SUPPORTED_NEW_ALERT_CATEGORY = "Supported New Alert Category"
    UNREAD_ALERT_STATUS = "Unread Alert Status"
    SUPPORTED_UNREAD_ALERT_CATEGORY = "Supported Unread Alert Category"
    ALERT_NOTIFICATION_CONTROL_POINT = "Alert Notification Control Point"


class ServiceName(Enum):
    """Enumeration of all supported GATT service names."""

    GENERIC_ACCESS = "Generic Access"
    GENERIC_ATTRIBUTE = "Generic Attribute"
    DEVICE_INFORMATION = "Device Information"
    BATTERY_SERVICE = "Battery Service"
    HEART_RATE = "Heart Rate"
    BLOOD_PRESSURE = "Blood Pressure"
    HEALTH_THERMOMETER = "Health Thermometer"
    GLUCOSE = "Glucose"
    CYCLING_SPEED_AND_CADENCE = "Cycling Speed and Cadence"
    CYCLING_POWER = "Cycling Power"
    RUNNING_SPEED_AND_CADENCE = "Running Speed and Cadence"
    AUTOMATION_IO = "Automation IO"
    ENVIRONMENTAL_SENSING = "Environmental Sensing"
    BODY_COMPOSITION = "Body Composition"
    WEIGHT_SCALE = "Weight Scale"
    LOCATION_AND_NAVIGATION = "Location and Navigation"
    PHONE_ALERT_STATUS = "Phone Alert Status"
