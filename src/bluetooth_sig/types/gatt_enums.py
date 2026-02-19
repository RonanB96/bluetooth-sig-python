"""Core GATT enumerations for strong typing.

Defines enums for GATT properties, value types, characteristic names,
and other core BLE concepts to replace string usage with type-safe
alternatives.
"""

from __future__ import annotations

import logging
from enum import Enum, IntEnum, IntFlag

logger = logging.getLogger(__name__)


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


class AdjustReason(IntFlag):
    """Time adjustment reason flags.

    Used by Current Time Service to indicate why time was adjusted.
    Can be combined as bitfield flags.
    """

    MANUAL_TIME_UPDATE = 1 << 0  # Bit 0
    EXTERNAL_REFERENCE_TIME_UPDATE = 1 << 1  # Bit 1
    CHANGE_OF_TIME_ZONE = 1 << 2  # Bit 2
    CHANGE_OF_DST = 1 << 3  # Bit 3
    # Bits 4-7: Reserved for future use

    @classmethod
    def from_raw(cls, value: int) -> AdjustReason:
        """Create AdjustReason from raw byte value, masking reserved bits."""
        if value & 0xF0:
            logger.warning("AdjustReason: Reserved bits set in raw value %d, masking to valid bits only", value)
        # Only bits 0-3 are defined, mask out bits 4-7 for forward compatibility
        masked_value = value & 0x0F
        return cls(masked_value)


class GattProperty(IntFlag):
    """GATT characteristic properties defined by Bluetooth SIG.

    Uses IntFlag for bitwise operations when combining properties.
    Bit values match the Bluetooth Core Specification.
    """

    BROADCAST = 0x0001
    READ = 0x0002
    WRITE_WITHOUT_RESPONSE = 0x0004
    WRITE = 0x0008
    NOTIFY = 0x0010
    INDICATE = 0x0020
    AUTHENTICATED_SIGNED_WRITES = 0x0040
    EXTENDED_PROPERTIES = 0x0080
    RELIABLE_WRITE = 0x0100
    WRITABLE_AUXILIARIES = 0x0200
    # Encryption and authentication properties (extended)
    ENCRYPT_READ = 0x0400
    ENCRYPT_WRITE = 0x0800
    ENCRYPT_NOTIFY = 0x1000
    AUTH_READ = 0x2000
    AUTH_WRITE = 0x4000
    AUTH_NOTIFY = 0x8000


class ValueType(Enum):
    """Data types for characteristic values."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BYTES = "bytes"
    BITFIELD = "bitfield"
    BOOL = "bool"
    DATETIME = "datetime"
    UUID = "uuid"
    DICT = "dict"
    VARIOUS = "various"
    UNKNOWN = "unknown"


class CharacteristicRole(Enum):
    """Inferred purpose of a GATT characteristic.

    Derived algorithmically from SIG spec metadata (name patterns,
    value_type, unit presence, field structure).  No per-characteristic
    maintenance is required — the classification is computed at
    instantiation time from data already parsed from the SIG YAML specs.

    Members:
        MEASUREMENT — carries numeric or structured sensor data with
                      physical units (temperature, heart rate, SpO₂, …).
        STATUS      — reports a device state or enum value
                      (training status, alert status, …).
        FEATURE     — describes device capabilities as a bitfield
                      (blood pressure feature, cycling power feature, …).
        CONTROL     — write-only control point used to command the device
                      (heart rate control point, fitness machine CP, …).
        INFO        — static metadata string
                      (device name, firmware revision, serial number, …).
        UNKNOWN     — cannot be classified from spec metadata alone;
                      consumers should apply their own heuristic.
    """

    MEASUREMENT = "measurement"
    STATUS = "status"
    FEATURE = "feature"
    CONTROL = "control"
    INFO = "info"
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
    UTF16S = "utf16s"
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
            "utf16s": cls.UTF16S,  # UTF-16 string support
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
            self.SINT24: ValueType.INT,
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
            self.UTF16S: ValueType.STRING,
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
            self.UTF16S: "string",
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
    CSC_FEATURE = "CSC Feature"
    RSC_MEASUREMENT = "RSC Measurement"
    RSC_FEATURE = "RSC Feature"
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
    CO2_CONCENTRATION = r"CO\textsubscript{2} Concentration"
    METHANE_CONCENTRATION = "Methane Concentration"
    NITROGEN_DIOXIDE_CONCENTRATION = "Nitrogen Dioxide Concentration"
    NON_METHANE_VOC_CONCENTRATION = "Non-Methane Volatile Organic Compounds Concentration"
    OZONE_CONCENTRATION = "Ozone Concentration"
    PM1_CONCENTRATION = "Particulate Matter - PM1 Concentration"
    PM10_CONCENTRATION = "Particulate Matter - PM10 Concentration"
    PM25_CONCENTRATION = "Particulate Matter - PM2.5 Concentration"
    SULFUR_DIOXIDE_CONCENTRATION = "Sulfur Dioxide Concentration"
    VOC_CONCENTRATION = "VOC Concentration"
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
    PLX_CONTINUOUS_MEASUREMENT = "PLX Continuous Measurement"
    PLX_SPOT_CHECK_MEASUREMENT = "PLX Spot-Check Measurement"
    PLX_FEATURES = "PLX Features"
    LOCATION_AND_SPEED = "Location and Speed"
    NAVIGATION = "Navigation"
    POSITION_QUALITY = "Position Quality"
    LN_FEATURE = "LN Feature"
    LN_CONTROL_POINT = "LN Control Point"
    SERVICE_CHANGED = "Service Changed"
    ALERT_LEVEL = "Alert Level"
    ALERT_CATEGORY_ID_BIT_MASK = "Alert Category ID Bit Mask"
    ALERT_CATEGORY_ID = "Alert Category ID"
    ALERT_STATUS = "Alert Status"
    RINGER_SETTING = "Ringer Setting"
    RINGER_CONTROL_POINT = "Ringer Control Point"
    # Alert Notification Service characteristics
    NEW_ALERT = "New Alert"
    SUPPORTED_NEW_ALERT_CATEGORY = "Supported New Alert Category"
    UNREAD_ALERT_STATUS = "Unread Alert Status"
    SUPPORTED_UNREAD_ALERT_CATEGORY = "Supported Unread Alert Category"
    ALERT_NOTIFICATION_CONTROL_POINT = "Alert Notification Control Point"
    # Time characteristics
    CURRENT_TIME = "Current Time"
    REFERENCE_TIME_INFORMATION = "Reference Time Information"
    TIME_WITH_DST = "Time with DST"
    TIME_UPDATE_CONTROL_POINT = "Time Update Control Point"
    TIME_UPDATE_STATE = "Time Update State"
    # Power level
    TX_POWER_LEVEL = "Tx Power Level"
    SCAN_INTERVAL_WINDOW = "Scan Interval Window"
    BOND_MANAGEMENT_FEATURE = "Bond Management Feature"
    BOND_MANAGEMENT_CONTROL_POINT = "Bond Management Control Point"
    # Indoor positioning characteristics
    INDOOR_POSITIONING_CONFIGURATION = "Indoor Positioning Configuration"
    LATITUDE = "Latitude"
    LONGITUDE = "Longitude"
    FLOOR_NUMBER = "Floor Number"
    LOCATION_NAME = "Location Name"
    HID_INFORMATION = "HID Information"
    REPORT_MAP = "Report Map"
    HID_CONTROL_POINT = "HID Control Point"
    REPORT = "Report"
    PROTOCOL_MODE = "Protocol Mode"
    FITNESS_MACHINE_FEATURE = "Fitness Machine Feature"
    TREADMILL_DATA = "Treadmill Data"
    CROSS_TRAINER_DATA = "Cross Trainer Data"
    STEP_CLIMBER_DATA = "Step Climber Data"
    STAIR_CLIMBER_DATA = "Stair Climber Data"
    ROWER_DATA = "Rower Data"
    INDOOR_BIKE_DATA = "Indoor Bike Data"
    TRAINING_STATUS = "Training Status"
    SUPPORTED_SPEED_RANGE = "Supported Speed Range"
    SUPPORTED_INCLINATION_RANGE = "Supported Inclination Range"
    SUPPORTED_RESISTANCE_LEVEL_RANGE = "Supported Resistance Level Range"
    SUPPORTED_HEART_RATE_RANGE = "Supported Heart Rate Range"
    FITNESS_MACHINE_CONTROL_POINT = "Fitness Machine Control Point"
    FITNESS_MACHINE_STATUS = "Fitness Machine Status"
    # User Data Service characteristics
    ACTIVITY_GOAL = "Activity Goal"
    AEROBIC_HEART_RATE_LOWER_LIMIT = "Aerobic Heart Rate Lower Limit"
    AEROBIC_HEART_RATE_UPPER_LIMIT = "Aerobic Heart Rate Upper Limit"
    AEROBIC_THRESHOLD = "Aerobic Threshold"
    AGE = "Age"
    ANAEROBIC_HEART_RATE_LOWER_LIMIT = "Anaerobic Heart Rate Lower Limit"
    ANAEROBIC_HEART_RATE_UPPER_LIMIT = "Anaerobic Heart Rate Upper Limit"
    ANAEROBIC_THRESHOLD = "Anaerobic Threshold"
    CALORIC_INTAKE = "Caloric Intake"
    DATE_OF_BIRTH = "Date of Birth"
    DATE_OF_THRESHOLD_ASSESSMENT = "Date of Threshold Assessment"
    DEVICE_WEARING_POSITION = "Device Wearing Position"
    EMAIL_ADDRESS = "Email Address"
    FAT_BURN_HEART_RATE_LOWER_LIMIT = "Fat Burn Heart Rate Lower Limit"
    FAT_BURN_HEART_RATE_UPPER_LIMIT = "Fat Burn Heart Rate Upper Limit"
    FIRST_NAME = "First Name"
    FIVE_ZONE_HEART_RATE_LIMITS = "Five Zone Heart Rate Limits"
    FOUR_ZONE_HEART_RATE_LIMITS = "Four Zone Heart Rate Limits"
    GENDER = "Gender"
    HANDEDNESS = "Handedness"
    HEART_RATE_MAX = "Heart Rate Max"
    HEIGHT = "Height"
    HIGH_INTENSITY_EXERCISE_THRESHOLD = "High Intensity Exercise Threshold"
    HIGH_RESOLUTION_HEIGHT = "High Resolution Height"
    HIP_CIRCUMFERENCE = "Hip Circumference"
    LANGUAGE = "Language"
    LAST_NAME = "Last Name"
    MAXIMUM_RECOMMENDED_HEART_RATE = "Maximum Recommended Heart Rate"
    MIDDLE_NAME = "Middle Name"
    PREFERRED_UNITS = "Preferred Units"
    RESTING_HEART_RATE = "Resting Heart Rate"
    SEDENTARY_INTERVAL_NOTIFICATION = "Sedentary Interval Notification"
    SPORT_TYPE_FOR_AEROBIC_AND_ANAEROBIC_THRESHOLDS = "Sport Type for Aerobic and Anaerobic Thresholds"
    STRIDE_LENGTH = "Stride Length"
    THREE_ZONE_HEART_RATE_LIMITS = "Three Zone Heart Rate Limits"
    TWO_ZONE_HEART_RATE_LIMITS = "Two Zone Heart Rate Limits"
    VO2_MAX = "VO2 Max"
    WAIST_CIRCUMFERENCE = "Waist Circumference"
    WEIGHT = "Weight"

    # Not implemented characteristics - listed for completeness
    ACS_CONTROL_POINT = "ACS Control Point"
    ACS_DATA_IN = "ACS Data In"
    ACS_DATA_OUT_INDICATE = "ACS Data Out Indicate"
    ACS_DATA_OUT_NOTIFY = "ACS Data Out Notify"
    ACS_STATUS = "ACS Status"
    AP_SYNC_KEY_MATERIAL = "AP Sync Key Material"
    ASE_CONTROL_POINT = "ASE Control Point"
    ACCELERATION = "Acceleration"
    ACCELERATION_3D = "Acceleration 3D"
    ACCELERATION_DETECTION_STATUS = "Acceleration Detection Status"
    ACTIVE_PRESET_INDEX = "Active Preset Index"
    ADVERTISING_CONSTANT_TONE_EXTENSION_INTERVAL = "Advertising Constant Tone Extension Interval"
    ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_LENGTH = "Advertising Constant Tone Extension Minimum Length"
    ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_TRANSMIT_COUNT = (
        "Advertising Constant Tone Extension Minimum Transmit Count"
    )
    ADVERTISING_CONSTANT_TONE_EXTENSION_PHY = "Advertising Constant Tone Extension PHY"
    ADVERTISING_CONSTANT_TONE_EXTENSION_TRANSMIT_DURATION = "Advertising Constant Tone Extension Transmit Duration"
    AGGREGATE = "Aggregate"
    ALTITUDE = "Altitude"
    APPARENT_ENERGY_32 = "Apparent Energy 32"
    APPARENT_POWER = "Apparent Power"
    AUDIO_INPUT_CONTROL_POINT = "Audio Input Control Point"
    AUDIO_INPUT_DESCRIPTION = "Audio Input Description"
    AUDIO_INPUT_STATE = "Audio Input State"
    AUDIO_INPUT_STATUS = "Audio Input Status"
    AUDIO_INPUT_TYPE = "Audio Input Type"
    AUDIO_LOCATION = "Audio Location"
    AUDIO_OUTPUT_DESCRIPTION = "Audio Output Description"
    AVAILABLE_AUDIO_CONTEXTS = "Available Audio Contexts"
    BGR_FEATURES = "BGR Features"
    BGS_FEATURES = "BGS Features"
    BR_EDR_HANDOVER_DATA = "BR-EDR Handover Data"
    BSS_CONTROL_POINT = "BSS Control Point"
    BSS_RESPONSE = "BSS Response"
    BATTERY_CRITICAL_STATUS = "Battery Critical Status"
    BATTERY_ENERGY_STATUS = "Battery Energy Status"
    BATTERY_HEALTH_INFORMATION = "Battery Health Information"
    BATTERY_HEALTH_STATUS = "Battery Health Status"
    BATTERY_INFORMATION = "Battery Information"
    BATTERY_TIME_STATUS = "Battery Time Status"
    BEARER_LIST_CURRENT_CALLS = "Bearer List Current Calls"
    BEARER_PROVIDER_NAME = "Bearer Provider Name"
    BEARER_SIGNAL_STRENGTH = "Bearer Signal Strength"
    BEARER_SIGNAL_STRENGTH_REPORTING_INTERVAL = "Bearer Signal Strength Reporting Interval"
    BEARER_TECHNOLOGY = "Bearer Technology"
    BEARER_UCI = "Bearer UCI"
    BEARER_URI_SCHEMES_SUPPORTED_LIST = "Bearer URI Schemes Supported List"
    BLOOD_PRESSURE_RECORD = "Blood Pressure Record"
    BLUETOOTH_SIG_DATA = "Bluetooth SIG Data"
    BOOLEAN = "Boolean"
    BOOT_KEYBOARD_INPUT_REPORT = "Boot Keyboard Input Report"
    BOOT_KEYBOARD_OUTPUT_REPORT = "Boot Keyboard Output Report"
    BOOT_MOUSE_INPUT_REPORT = "Boot Mouse Input Report"
    BROADCAST_AUDIO_SCAN_CONTROL_POINT = "Broadcast Audio Scan Control Point"
    BROADCAST_RECEIVE_STATE = "Broadcast Receive State"
    CGM_FEATURE = "CGM Feature"
    CGM_MEASUREMENT = "CGM Measurement"
    CGM_SESSION_RUN_TIME = "CGM Session Run Time"
    CGM_SESSION_START_TIME = "CGM Session Start Time"
    CGM_SPECIFIC_OPS_CONTROL_POINT = "CGM Specific Ops Control Point"
    CGM_STATUS = "CGM Status"
    CIE_13_3_1995_COLOR_RENDERING_INDEX = "CIE 13.3-1995 Color Rendering Index"
    CALL_CONTROL_POINT = "Call Control Point"
    CALL_CONTROL_POINT_OPTIONAL_OPCODES = "Call Control Point Optional Opcodes"
    CALL_FRIENDLY_NAME = "Call Friendly Name"
    CALL_STATE = "Call State"
    CARBON_MONOXIDE_CONCENTRATION = "Carbon Monoxide Concentration"
    CARDIORESPIRATORY_ACTIVITY_INSTANTANEOUS_DATA = "CardioRespiratory Activity Instantaneous Data"
    CARDIORESPIRATORY_ACTIVITY_SUMMARY_DATA = "CardioRespiratory Activity Summary Data"
    CENTRAL_ADDRESS_RESOLUTION = "Central Address Resolution"
    CHROMATIC_DISTANCE_FROM_PLANCKIAN = "Chromatic Distance from Planckian"
    CHROMATICITY_COORDINATE = "Chromaticity Coordinate"
    CHROMATICITY_COORDINATES = "Chromaticity Coordinates"
    CHROMATICITY_TOLERANCE = "Chromaticity Tolerance"
    CHROMATICITY_IN_CCT_AND_DUV_VALUES = "Chromaticity in CCT and Duv Values"
    CLIENT_SUPPORTED_FEATURES = "Client Supported Features"
    COEFFICIENT = "Coefficient"
    CONSTANT_TONE_EXTENSION_ENABLE = "Constant Tone Extension Enable"
    CONTACT_STATUS_8 = "Contact Status 8"
    CONTENT_CONTROL_ID = "Content Control ID"
    COORDINATED_SET_SIZE = "Coordinated Set Size"
    CORRELATED_COLOR_TEMPERATURE = "Correlated Color Temperature"
    COSINE_OF_THE_ANGLE = "Cosine of the Angle"
    COUNT_16 = "Count 16"
    COUNT_24 = "Count 24"
    COUNTRY_CODE = "Country Code"
    CURRENT_ELAPSED_TIME = "Current Elapsed Time"
    CURRENT_GROUP_OBJECT_ID = "Current Group Object ID"
    CURRENT_TRACK_OBJECT_ID = "Current Track Object ID"
    CURRENT_TRACK_SEGMENTS_OBJECT_ID = "Current Track Segments Object ID"
    DST_OFFSET = "DST Offset"
    DATABASE_CHANGE_INCREMENT = "Database Change Increment"
    DATABASE_HASH = "Database Hash"
    DATE_TIME = "Date Time"
    DATE_UTC = "Date UTC"
    DAY_DATE_TIME = "Day Date Time"
    DAY_OF_WEEK = "Day of Week"
    DESCRIPTOR_VALUE_CHANGED = "Descriptor Value Changed"
    DEVICE_TIME = "Device Time"
    DEVICE_TIME_CONTROL_POINT = "Device Time Control Point"
    DEVICE_TIME_FEATURE = "Device Time Feature"
    DEVICE_TIME_PARAMETERS = "Device Time Parameters"
    DOOR_WINDOW_STATUS = "Door/Window Status"
    ESL_ADDRESS = "ESL Address"
    ESL_CONTROL_POINT = "ESL Control Point"
    ESL_CURRENT_ABSOLUTE_TIME = "ESL Current Absolute Time"
    ESL_DISPLAY_INFORMATION = "ESL Display Information"
    ESL_IMAGE_INFORMATION = "ESL Image Information"
    ESL_LED_INFORMATION = "ESL LED Information"
    ESL_RESPONSE_KEY_MATERIAL = "ESL Response Key Material"
    ESL_SENSOR_INFORMATION = "ESL Sensor Information"
    EMERGENCY_ID = "Emergency ID"
    EMERGENCY_TEXT = "Emergency Text"
    ENCRYPTED_DATA_KEY_MATERIAL = "Encrypted Data Key Material"
    ENERGY = "Energy"
    ENERGY_32 = "Energy 32"
    ENERGY_IN_A_PERIOD_OF_DAY = "Energy in a Period of Day"
    ENHANCED_BLOOD_PRESSURE_MEASUREMENT = "Enhanced Blood Pressure Measurement"
    ENHANCED_INTERMEDIATE_CUFF_PRESSURE = "Enhanced Intermediate Cuff Pressure"
    ESTIMATED_SERVICE_DATE = "Estimated Service Date"
    EVENT_STATISTICS = "Event Statistics"
    EXACT_TIME_256 = "Exact Time 256"
    FIRST_USE_DATE = "First Use Date"
    FIXED_STRING_16 = "Fixed String 16"
    FIXED_STRING_24 = "Fixed String 24"
    FIXED_STRING_36 = "Fixed String 36"
    FIXED_STRING_64 = "Fixed String 64"
    FIXED_STRING_8 = "Fixed String 8"
    FORCE = "Force"
    GHS_CONTROL_POINT = "GHS Control Point"
    GMAP_ROLE = "GMAP Role"
    GAIN_SETTINGS_ATTRIBUTE = "Gain Settings Attribute"
    GENERAL_ACTIVITY_INSTANTANEOUS_DATA = "General Activity Instantaneous Data"
    GENERAL_ACTIVITY_SUMMARY_DATA = "General Activity Summary Data"
    GENERIC_LEVEL = "Generic Level"
    GLOBAL_TRADE_ITEM_NUMBER = "Global Trade Item Number"
    GUST_FACTOR = "Gust Factor"
    HID_ISO_PROPERTIES = "HID ISO Properties"
    HTTP_CONTROL_POINT = "HTTP Control Point"
    HTTP_ENTITY_BODY = "HTTP Entity Body"
    HTTP_HEADERS = "HTTP Headers"
    HTTP_STATUS_CODE = "HTTP Status Code"
    HTTPS_SECURITY = "HTTPS Security"
    HEALTH_SENSOR_FEATURES = "Health Sensor Features"
    HEARING_AID_FEATURES = "Hearing Aid Features"
    HEARING_AID_PRESET_CONTROL_POINT = "Hearing Aid Preset Control Point"
    HEART_RATE_CONTROL_POINT = "Heart Rate Control Point"
    HIGH_TEMPERATURE = "High Temperature"
    HUMIDITY_8 = "Humidity 8"
    IDD_ANNUNCIATION_STATUS = "IDD Annunciation Status"
    IDD_COMMAND_CONTROL_POINT = "IDD Command Control Point"
    IDD_COMMAND_DATA = "IDD Command Data"
    IDD_FEATURES = "IDD Features"
    IDD_HISTORY_DATA = "IDD History Data"
    IDD_RECORD_ACCESS_CONTROL_POINT = "IDD Record Access Control Point"
    IDD_STATUS = "IDD Status"
    IDD_STATUS_CHANGED = "IDD Status Changed"
    IDD_STATUS_READER_CONTROL_POINT = "IDD Status Reader Control Point"
    IEEE_11073_20601_REGULATORY_CERTIFICATION_DATA_LIST = "IEEE 11073-20601 Regulatory Certification Data List"
    IMD_CONTROL = "IMD Control"
    IMD_HISTORICAL_DATA = "IMD Historical Data"
    IMD_STATUS = "IMD Status"
    IMDS_DESCRIPTOR_VALUE_CHANGED = "IMDS Descriptor Value Changed"
    ILLUMINANCE_16 = "Illuminance 16"
    INCOMING_CALL = "Incoming Call"
    INCOMING_CALL_TARGET_BEARER_URI = "Incoming Call Target Bearer URI"
    INTERMEDIATE_TEMPERATURE = "Intermediate Temperature"
    IRRADIANCE = "Irradiance"
    LE_GATT_SECURITY_LEVELS = "LE GATT Security Levels"
    LE_HID_OPERATION_MODE = "LE HID Operation Mode"
    LENGTH = "Length"
    LIFE_CYCLE_DATA = "Life Cycle Data"
    LIGHT_DISTRIBUTION = "Light Distribution"
    LIGHT_OUTPUT = "Light Output"
    LIGHT_SOURCE_TYPE = "Light Source Type"
    LINEAR_POSITION = "Linear Position"
    LIVE_HEALTH_OBSERVATIONS = "Live Health Observations"
    LOCAL_EAST_COORDINATE = "Local East Coordinate"
    LOCAL_NORTH_COORDINATE = "Local North Coordinate"
    LUMINOUS_EFFICACY = "Luminous Efficacy"
    LUMINOUS_ENERGY = "Luminous Energy"
    LUMINOUS_EXPOSURE = "Luminous Exposure"
    LUMINOUS_FLUX = "Luminous Flux"
    LUMINOUS_FLUX_RANGE = "Luminous Flux Range"
    LUMINOUS_INTENSITY = "Luminous Intensity"
    MASS_FLOW = "Mass Flow"
    MEASUREMENT_INTERVAL = "Measurement Interval"
    MEDIA_CONTROL_POINT = "Media Control Point"
    MEDIA_CONTROL_POINT_OPCODES_SUPPORTED = "Media Control Point Opcodes Supported"
    MEDIA_PLAYER_ICON_OBJECT_ID = "Media Player Icon Object ID"
    MEDIA_PLAYER_ICON_URL = "Media Player Icon URL"
    MEDIA_PLAYER_NAME = "Media Player Name"
    MEDIA_STATE = "Media State"
    MESH_PROVISIONING_DATA_IN = "Mesh Provisioning Data In"
    MESH_PROVISIONING_DATA_OUT = "Mesh Provisioning Data Out"
    MESH_PROXY_DATA_IN = "Mesh Proxy Data In"
    MESH_PROXY_DATA_OUT = "Mesh Proxy Data Out"
    MUTE = "Mute"
    NEXT_TRACK_OBJECT_ID = "Next Track Object ID"
    OTS_FEATURE = "OTS Feature"
    OBJECT_ACTION_CONTROL_POINT = "Object Action Control Point"
    OBJECT_CHANGED = "Object Changed"
    OBJECT_FIRST_CREATED = "Object First-Created"
    OBJECT_ID = "Object ID"
    OBJECT_LAST_MODIFIED = "Object Last-Modified"
    OBJECT_LIST_CONTROL_POINT = "Object List Control Point"
    OBJECT_LIST_FILTER = "Object List Filter"
    OBJECT_NAME = "Object Name"
    OBJECT_PROPERTIES = "Object Properties"
    OBJECT_SIZE = "Object Size"
    OBJECT_TYPE = "Object Type"
    OBSERVATION_SCHEDULE_CHANGED = "Observation Schedule Changed"
    ON_DEMAND_RANGING_DATA = "On-demand Ranging Data"
    PARENT_GROUP_OBJECT_ID = "Parent Group Object ID"
    PERCEIVED_LIGHTNESS = "Perceived Lightness"
    PERCENTAGE_8 = "Percentage 8"
    PERCENTAGE_8_STEPS = "Percentage 8 Steps"
    PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS = "Peripheral Preferred Connection Parameters"
    PERIPHERAL_PRIVACY_FLAG = "Peripheral Privacy Flag"
    PHYSICAL_ACTIVITY_CURRENT_SESSION = "Physical Activity Current Session"
    PHYSICAL_ACTIVITY_MONITOR_CONTROL_POINT = "Physical Activity Monitor Control Point"
    PHYSICAL_ACTIVITY_MONITOR_FEATURES = "Physical Activity Monitor Features"
    PHYSICAL_ACTIVITY_SESSION_DESCRIPTOR = "Physical Activity Session Descriptor"
    PLAYBACK_SPEED = "Playback Speed"
    PLAYING_ORDER = "Playing Order"
    PLAYING_ORDERS_SUPPORTED = "Playing Orders Supported"
    PNP_ID = "PnP ID"
    POWER = "Power"
    PRECISE_ACCELERATION_3D = "Precise Acceleration 3D"
    PUSHBUTTON_STATUS_8 = "Pushbutton Status 8"
    RAS_CONTROL_POINT = "RAS Control Point"
    RAS_FEATURES = "RAS Features"
    RC_FEATURE = "RC Feature"
    RC_SETTINGS = "RC Settings"
    RANGING_DATA_OVERWRITTEN = "Ranging Data Overwritten"
    RANGING_DATA_READY = "Ranging Data Ready"
    REAL_TIME_RANGING_DATA = "Real-time Ranging Data"
    RECONNECTION_ADDRESS = "Reconnection Address"
    RECONNECTION_CONFIGURATION_CONTROL_POINT = "Reconnection Configuration Control Point"
    RECORD_ACCESS_CONTROL_POINT = "Record Access Control Point"
    REGISTERED_USER = "Registered User"
    RELATIVE_RUNTIME_IN_A_CORRELATED_COLOR_TEMPERATURE_RANGE = (
        "Relative Runtime in a Correlated Color Temperature Range"
    )
    RELATIVE_RUNTIME_IN_A_CURRENT_RANGE = "Relative Runtime in a Current Range"
    RELATIVE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE = "Relative Runtime in a Generic Level Range"
    RELATIVE_VALUE_IN_A_PERIOD_OF_DAY = "Relative Value in a Period of Day"
    RELATIVE_VALUE_IN_A_TEMPERATURE_RANGE = "Relative Value in a Temperature Range"
    RELATIVE_VALUE_IN_A_VOLTAGE_RANGE = "Relative Value in a Voltage Range"
    RELATIVE_VALUE_IN_AN_ILLUMINANCE_RANGE = "Relative Value in an Illuminance Range"
    RESOLVABLE_PRIVATE_ADDRESS_ONLY = "Resolvable Private Address Only"
    ROTATIONAL_SPEED = "Rotational Speed"
    SC_CONTROL_POINT = "SC Control Point"
    SCAN_REFRESH = "Scan Refresh"
    SEARCH_CONTROL_POINT = "Search Control Point"
    SEARCH_RESULTS_OBJECT_ID = "Search Results Object ID"
    SEEKING_SPEED = "Seeking Speed"
    SENSOR_LOCATION = "Sensor Location"
    SERVER_SUPPORTED_FEATURES = "Server Supported Features"
    SERVICE_CYCLE_DATA = "Service Cycle Data"
    SET_IDENTITY_RESOLVING_KEY = "Set Identity Resolving Key"
    SET_MEMBER_LOCK = "Set Member Lock"
    SET_MEMBER_RANK = "Set Member Rank"
    SINK_ASE = "Sink ASE"
    SINK_AUDIO_LOCATIONS = "Sink Audio Locations"
    SINK_PAC = "Sink PAC"
    SLEEP_ACTIVITY_INSTANTANEOUS_DATA = "Sleep Activity Instantaneous Data"
    SLEEP_ACTIVITY_SUMMARY_DATA = "Sleep Activity Summary Data"
    SOURCE_ASE = "Source ASE"
    SOURCE_AUDIO_LOCATIONS = "Source Audio Locations"
    SOURCE_PAC = "Source PAC"
    STATUS_FLAGS = "Status Flags"
    STEP_COUNTER_ACTIVITY_SUMMARY_DATA = "Step Counter Activity Summary Data"
    STORED_HEALTH_OBSERVATIONS = "Stored Health Observations"
    SULFUR_HEXAFLUORIDE_CONCENTRATION = "Sulfur Hexafluoride Concentration"
    SUPPORTED_AUDIO_CONTEXTS = "Supported Audio Contexts"
    SYSTEM_ID = "System ID"
    TDS_CONTROL_POINT = "TDS Control Point"
    TMAP_ROLE = "TMAP Role"
    TEMPERATURE_8 = "Temperature 8"
    TEMPERATURE_8_STATISTICS = "Temperature 8 Statistics"
    TEMPERATURE_8_IN_A_PERIOD_OF_DAY = "Temperature 8 in a Period of Day"
    TEMPERATURE_RANGE = "Temperature Range"
    TEMPERATURE_STATISTICS = "Temperature Statistics"
    TEMPERATURE_TYPE = "Temperature Type"
    TERMINATION_REASON = "Termination Reason"
    TIME_ACCURACY = "Time Accuracy"
    TIME_CHANGE_LOG_DATA = "Time Change Log Data"
    TIME_DECIHOUR_8 = "Time Decihour 8"
    TIME_EXPONENTIAL_8 = "Time Exponential 8"
    TIME_HOUR_24 = "Time Hour 24"
    TIME_MILLISECOND_24 = "Time Millisecond 24"
    TIME_SECOND_16 = "Time Second 16"
    TIME_SECOND_32 = "Time Second 32"
    TIME_SECOND_8 = "Time Second 8"
    TIME_SOURCE = "Time Source"
    TORQUE = "Torque"
    TRACK_CHANGED = "Track Changed"
    TRACK_DURATION = "Track Duration"
    TRACK_POSITION = "Track Position"
    TRACK_TITLE = "Track Title"
    UDI_FOR_MEDICAL_DEVICES = "UDI for Medical Devices"
    UGG_FEATURES = "UGG Features"
    UGT_FEATURES = "UGT Features"
    URI = "URI"
    UNCERTAINTY = "Uncertainty"
    USER_CONTROL_POINT = "User Control Point"
    USER_INDEX = "User Index"
    VOLUME_CONTROL_POINT = "Volume Control Point"
    VOLUME_FLAGS = "Volume Flags"
    VOLUME_FLOW = "Volume Flow"
    VOLUME_OFFSET_CONTROL_POINT = "Volume Offset Control Point"
    VOLUME_OFFSET_STATE = "Volume Offset State"
    VOLUME_STATE = "Volume State"
    WORK_CYCLE_DATA = "Work Cycle Data"


class ServiceName(Enum):
    """Enumeration of all supported GATT service names."""

    GAP = "GAP"
    GATT = "GATT"
    IMMEDIATE_ALERT = "Immediate Alert"
    LINK_LOSS = "Link Loss"
    TX_POWER = "Tx Power"
    NEXT_DST_CHANGE = "Next DST Change"
    DEVICE_INFORMATION = "Device Information"
    BATTERY = "Battery"
    HEART_RATE = "Heart Rate"
    BLOOD_PRESSURE = "Blood Pressure"
    HEALTH_THERMOMETER = "Health Thermometer"
    GLUCOSE = "Glucose"
    CYCLING_SPEED_AND_CADENCE = "Cycling Speed and Cadence"
    CYCLING_POWER = "Cycling Power"
    RUNNING_SPEED_AND_CADENCE = "Running Speed and Cadence"
    AUTOMATION_IO = "Automation IO"
    ENVIRONMENTAL_SENSING = "Environmental Sensing"
    ALERT_NOTIFICATION = "Alert Notification"
    BODY_COMPOSITION = "Body Composition"
    USER_DATA = "User Data"
    WEIGHT_SCALE = "Weight Scale"
    LOCATION_AND_NAVIGATION = "Location and Navigation"
    PHONE_ALERT_STATUS = "Phone Alert Status"
    REFERENCE_TIME_UPDATE = "Reference Time Update"
    CURRENT_TIME = "Current Time"
    SCAN_PARAMETERS = "Scan Parameters"
    BOND_MANAGEMENT = "Bond Management"
    INDOOR_POSITIONING = "Indoor Positioning"
    HUMAN_INTERFACE_DEVICE = "Human Interface Device"
    PULSE_OXIMETER = "Pulse Oximeter"
    FITNESS_MACHINE = "Fitness Machine"
