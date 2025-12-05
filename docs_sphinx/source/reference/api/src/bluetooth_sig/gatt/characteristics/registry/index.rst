src.bluetooth_sig.gatt.characteristics.registry
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.registry

.. autoapi-nested-parse::

   Bluetooth SIG GATT characteristic registry.

   This module contains the characteristic registry implementation and
   class mappings. CharacteristicName enum is now centralized in
   types.gatt_enums to avoid circular imports.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName
   src.bluetooth_sig.gatt.characteristics.registry.CharacteristicRegistry


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.registry.get_characteristic_class_map


Module Contents
---------------

.. py:class:: CharacteristicName(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Enumeration of all supported GATT characteristic names.


   .. py:attribute:: BATTERY_LEVEL
      :value: 'Battery Level'



   .. py:attribute:: BATTERY_LEVEL_STATUS
      :value: 'Battery Level Status'



   .. py:attribute:: TEMPERATURE
      :value: 'Temperature'



   .. py:attribute:: TEMPERATURE_MEASUREMENT
      :value: 'Temperature Measurement'



   .. py:attribute:: HUMIDITY
      :value: 'Humidity'



   .. py:attribute:: PRESSURE
      :value: 'Pressure'



   .. py:attribute:: UV_INDEX
      :value: 'UV Index'



   .. py:attribute:: ILLUMINANCE
      :value: 'Illuminance'



   .. py:attribute:: POWER_SPECIFICATION
      :value: 'Power Specification'



   .. py:attribute:: HEART_RATE_MEASUREMENT
      :value: 'Heart Rate Measurement'



   .. py:attribute:: BLOOD_PRESSURE_MEASUREMENT
      :value: 'Blood Pressure Measurement'



   .. py:attribute:: INTERMEDIATE_CUFF_PRESSURE
      :value: 'Intermediate Cuff Pressure'



   .. py:attribute:: BLOOD_PRESSURE_FEATURE
      :value: 'Blood Pressure Feature'



   .. py:attribute:: CSC_MEASUREMENT
      :value: 'CSC Measurement'



   .. py:attribute:: CSC_FEATURE
      :value: 'CSC Feature'



   .. py:attribute:: RSC_MEASUREMENT
      :value: 'RSC Measurement'



   .. py:attribute:: RSC_FEATURE
      :value: 'RSC Feature'



   .. py:attribute:: CYCLING_POWER_MEASUREMENT
      :value: 'Cycling Power Measurement'



   .. py:attribute:: CYCLING_POWER_FEATURE
      :value: 'Cycling Power Feature'



   .. py:attribute:: CYCLING_POWER_VECTOR
      :value: 'Cycling Power Vector'



   .. py:attribute:: CYCLING_POWER_CONTROL_POINT
      :value: 'Cycling Power Control Point'



   .. py:attribute:: GLUCOSE_MEASUREMENT
      :value: 'Glucose Measurement'



   .. py:attribute:: GLUCOSE_MEASUREMENT_CONTEXT
      :value: 'Glucose Measurement Context'



   .. py:attribute:: GLUCOSE_FEATURE
      :value: 'Glucose Feature'



   .. py:attribute:: MANUFACTURER_NAME_STRING
      :value: 'Manufacturer Name String'



   .. py:attribute:: MODEL_NUMBER_STRING
      :value: 'Model Number String'



   .. py:attribute:: SERIAL_NUMBER_STRING
      :value: 'Serial Number String'



   .. py:attribute:: FIRMWARE_REVISION_STRING
      :value: 'Firmware Revision String'



   .. py:attribute:: HARDWARE_REVISION_STRING
      :value: 'Hardware Revision String'



   .. py:attribute:: SOFTWARE_REVISION_STRING
      :value: 'Software Revision String'



   .. py:attribute:: DEVICE_NAME
      :value: 'Device Name'



   .. py:attribute:: APPEARANCE
      :value: 'Appearance'



   .. py:attribute:: WEIGHT_MEASUREMENT
      :value: 'Weight Measurement'



   .. py:attribute:: WEIGHT_SCALE_FEATURE
      :value: 'Weight Scale Feature'



   .. py:attribute:: BODY_COMPOSITION_MEASUREMENT
      :value: 'Body Composition Measurement'



   .. py:attribute:: BODY_COMPOSITION_FEATURE
      :value: 'Body Composition Feature'



   .. py:attribute:: BODY_SENSOR_LOCATION
      :value: 'Body Sensor Location'



   .. py:attribute:: DEW_POINT
      :value: 'Dew Point'



   .. py:attribute:: HEAT_INDEX
      :value: 'Heat Index'



   .. py:attribute:: WIND_CHILL
      :value: 'Wind Chill'



   .. py:attribute:: TRUE_WIND_SPEED
      :value: 'True Wind Speed'



   .. py:attribute:: TRUE_WIND_DIRECTION
      :value: 'True Wind Direction'



   .. py:attribute:: APPARENT_WIND_SPEED
      :value: 'Apparent Wind Speed'



   .. py:attribute:: APPARENT_WIND_DIRECTION
      :value: 'Apparent Wind Direction'



   .. py:attribute:: MAGNETIC_DECLINATION
      :value: 'Magnetic Declination'



   .. py:attribute:: ELEVATION
      :value: 'Elevation'



   .. py:attribute:: MAGNETIC_FLUX_DENSITY_2D
      :value: 'Magnetic Flux Density - 2D'



   .. py:attribute:: MAGNETIC_FLUX_DENSITY_3D
      :value: 'Magnetic Flux Density - 3D'



   .. py:attribute:: BAROMETRIC_PRESSURE_TREND
      :value: 'Barometric Pressure Trend'



   .. py:attribute:: POLLEN_CONCENTRATION
      :value: 'Pollen Concentration'



   .. py:attribute:: RAINFALL
      :value: 'Rainfall'



   .. py:attribute:: TIME_ZONE
      :value: 'Time Zone'



   .. py:attribute:: LOCAL_TIME_INFORMATION
      :value: 'Local Time Information'



   .. py:attribute:: AMMONIA_CONCENTRATION
      :value: 'Ammonia Concentration'



   .. py:attribute:: CO2_CONCENTRATION
      :value: 'CO\\textsubscript{2} Concentration'



   .. py:attribute:: METHANE_CONCENTRATION
      :value: 'Methane Concentration'



   .. py:attribute:: NITROGEN_DIOXIDE_CONCENTRATION
      :value: 'Nitrogen Dioxide Concentration'



   .. py:attribute:: NON_METHANE_VOC_CONCENTRATION
      :value: 'Non-Methane Volatile Organic Compounds Concentration'



   .. py:attribute:: OZONE_CONCENTRATION
      :value: 'Ozone Concentration'



   .. py:attribute:: PM1_CONCENTRATION
      :value: 'Particulate Matter - PM1 Concentration'



   .. py:attribute:: PM10_CONCENTRATION
      :value: 'Particulate Matter - PM10 Concentration'



   .. py:attribute:: PM25_CONCENTRATION
      :value: 'Particulate Matter - PM2.5 Concentration'



   .. py:attribute:: SULFUR_DIOXIDE_CONCENTRATION
      :value: 'Sulfur Dioxide Concentration'



   .. py:attribute:: VOC_CONCENTRATION
      :value: 'VOC Concentration'



   .. py:attribute:: ELECTRIC_CURRENT
      :value: 'Electric Current'



   .. py:attribute:: ELECTRIC_CURRENT_RANGE
      :value: 'Electric Current Range'



   .. py:attribute:: ELECTRIC_CURRENT_SPECIFICATION
      :value: 'Electric Current Specification'



   .. py:attribute:: ELECTRIC_CURRENT_STATISTICS
      :value: 'Electric Current Statistics'



   .. py:attribute:: VOLTAGE
      :value: 'Voltage'



   .. py:attribute:: VOLTAGE_FREQUENCY
      :value: 'Voltage Frequency'



   .. py:attribute:: VOLTAGE_SPECIFICATION
      :value: 'Voltage Specification'



   .. py:attribute:: VOLTAGE_STATISTICS
      :value: 'Voltage Statistics'



   .. py:attribute:: HIGH_VOLTAGE
      :value: 'High Voltage'



   .. py:attribute:: AVERAGE_CURRENT
      :value: 'Average Current'



   .. py:attribute:: AVERAGE_VOLTAGE
      :value: 'Average Voltage'



   .. py:attribute:: SUPPORTED_POWER_RANGE
      :value: 'Supported Power Range'



   .. py:attribute:: NOISE
      :value: 'Noise'



   .. py:attribute:: PLX_CONTINUOUS_MEASUREMENT
      :value: 'PLX Continuous Measurement'



   .. py:attribute:: PLX_SPOT_CHECK_MEASUREMENT
      :value: 'PLX Spot-Check Measurement'



   .. py:attribute:: PLX_FEATURES
      :value: 'PLX Features'



   .. py:attribute:: LOCATION_AND_SPEED
      :value: 'Location and Speed'



   .. py:attribute:: NAVIGATION
      :value: 'Navigation'



   .. py:attribute:: POSITION_QUALITY
      :value: 'Position Quality'



   .. py:attribute:: LN_FEATURE
      :value: 'LN Feature'



   .. py:attribute:: LN_CONTROL_POINT
      :value: 'LN Control Point'



   .. py:attribute:: SERVICE_CHANGED
      :value: 'Service Changed'



   .. py:attribute:: ALERT_LEVEL
      :value: 'Alert Level'



   .. py:attribute:: ALERT_CATEGORY_ID_BIT_MASK
      :value: 'Alert Category ID Bit Mask'



   .. py:attribute:: ALERT_CATEGORY_ID
      :value: 'Alert Category ID'



   .. py:attribute:: ALERT_STATUS
      :value: 'Alert Status'



   .. py:attribute:: RINGER_SETTING
      :value: 'Ringer Setting'



   .. py:attribute:: RINGER_CONTROL_POINT
      :value: 'Ringer Control Point'



   .. py:attribute:: NEW_ALERT
      :value: 'New Alert'



   .. py:attribute:: SUPPORTED_NEW_ALERT_CATEGORY
      :value: 'Supported New Alert Category'



   .. py:attribute:: UNREAD_ALERT_STATUS
      :value: 'Unread Alert Status'



   .. py:attribute:: SUPPORTED_UNREAD_ALERT_CATEGORY
      :value: 'Supported Unread Alert Category'



   .. py:attribute:: ALERT_NOTIFICATION_CONTROL_POINT
      :value: 'Alert Notification Control Point'



   .. py:attribute:: CURRENT_TIME
      :value: 'Current Time'



   .. py:attribute:: REFERENCE_TIME_INFORMATION
      :value: 'Reference Time Information'



   .. py:attribute:: TIME_WITH_DST
      :value: 'Time with DST'



   .. py:attribute:: TIME_UPDATE_CONTROL_POINT
      :value: 'Time Update Control Point'



   .. py:attribute:: TIME_UPDATE_STATE
      :value: 'Time Update State'



   .. py:attribute:: TX_POWER_LEVEL
      :value: 'Tx Power Level'



   .. py:attribute:: SCAN_INTERVAL_WINDOW
      :value: 'Scan Interval Window'



   .. py:attribute:: BOND_MANAGEMENT_FEATURE
      :value: 'Bond Management Feature'



   .. py:attribute:: BOND_MANAGEMENT_CONTROL_POINT
      :value: 'Bond Management Control Point'



   .. py:attribute:: INDOOR_POSITIONING_CONFIGURATION
      :value: 'Indoor Positioning Configuration'



   .. py:attribute:: LATITUDE
      :value: 'Latitude'



   .. py:attribute:: LONGITUDE
      :value: 'Longitude'



   .. py:attribute:: FLOOR_NUMBER
      :value: 'Floor Number'



   .. py:attribute:: LOCATION_NAME
      :value: 'Location Name'



   .. py:attribute:: HID_INFORMATION
      :value: 'HID Information'



   .. py:attribute:: REPORT_MAP
      :value: 'Report Map'



   .. py:attribute:: HID_CONTROL_POINT
      :value: 'HID Control Point'



   .. py:attribute:: REPORT
      :value: 'Report'



   .. py:attribute:: PROTOCOL_MODE
      :value: 'Protocol Mode'



   .. py:attribute:: FITNESS_MACHINE_FEATURE
      :value: 'Fitness Machine Feature'



   .. py:attribute:: TREADMILL_DATA
      :value: 'Treadmill Data'



   .. py:attribute:: CROSS_TRAINER_DATA
      :value: 'Cross Trainer Data'



   .. py:attribute:: STEP_CLIMBER_DATA
      :value: 'Step Climber Data'



   .. py:attribute:: STAIR_CLIMBER_DATA
      :value: 'Stair Climber Data'



   .. py:attribute:: ROWER_DATA
      :value: 'Rower Data'



   .. py:attribute:: INDOOR_BIKE_DATA
      :value: 'Indoor Bike Data'



   .. py:attribute:: TRAINING_STATUS
      :value: 'Training Status'



   .. py:attribute:: SUPPORTED_SPEED_RANGE
      :value: 'Supported Speed Range'



   .. py:attribute:: SUPPORTED_INCLINATION_RANGE
      :value: 'Supported Inclination Range'



   .. py:attribute:: SUPPORTED_RESISTANCE_LEVEL_RANGE
      :value: 'Supported Resistance Level Range'



   .. py:attribute:: SUPPORTED_HEART_RATE_RANGE
      :value: 'Supported Heart Rate Range'



   .. py:attribute:: FITNESS_MACHINE_CONTROL_POINT
      :value: 'Fitness Machine Control Point'



   .. py:attribute:: FITNESS_MACHINE_STATUS
      :value: 'Fitness Machine Status'



   .. py:attribute:: ACTIVITY_GOAL
      :value: 'Activity Goal'



   .. py:attribute:: AEROBIC_HEART_RATE_LOWER_LIMIT
      :value: 'Aerobic Heart Rate Lower Limit'



   .. py:attribute:: AEROBIC_HEART_RATE_UPPER_LIMIT
      :value: 'Aerobic Heart Rate Upper Limit'



   .. py:attribute:: AEROBIC_THRESHOLD
      :value: 'Aerobic Threshold'



   .. py:attribute:: AGE
      :value: 'Age'



   .. py:attribute:: ANAEROBIC_HEART_RATE_LOWER_LIMIT
      :value: 'Anaerobic Heart Rate Lower Limit'



   .. py:attribute:: ANAEROBIC_HEART_RATE_UPPER_LIMIT
      :value: 'Anaerobic Heart Rate Upper Limit'



   .. py:attribute:: ANAEROBIC_THRESHOLD
      :value: 'Anaerobic Threshold'



   .. py:attribute:: CALORIC_INTAKE
      :value: 'Caloric Intake'



   .. py:attribute:: DATE_OF_BIRTH
      :value: 'Date of Birth'



   .. py:attribute:: DATE_OF_THRESHOLD_ASSESSMENT
      :value: 'Date of Threshold Assessment'



   .. py:attribute:: DEVICE_WEARING_POSITION
      :value: 'Device Wearing Position'



   .. py:attribute:: EMAIL_ADDRESS
      :value: 'Email Address'



   .. py:attribute:: FAT_BURN_HEART_RATE_LOWER_LIMIT
      :value: 'Fat Burn Heart Rate Lower Limit'



   .. py:attribute:: FAT_BURN_HEART_RATE_UPPER_LIMIT
      :value: 'Fat Burn Heart Rate Upper Limit'



   .. py:attribute:: FIRST_NAME
      :value: 'First Name'



   .. py:attribute:: FIVE_ZONE_HEART_RATE_LIMITS
      :value: 'Five Zone Heart Rate Limits'



   .. py:attribute:: FOUR_ZONE_HEART_RATE_LIMITS
      :value: 'Four Zone Heart Rate Limits'



   .. py:attribute:: GENDER
      :value: 'Gender'



   .. py:attribute:: HANDEDNESS
      :value: 'Handedness'



   .. py:attribute:: HEART_RATE_MAX
      :value: 'Heart Rate Max'



   .. py:attribute:: HEIGHT
      :value: 'Height'



   .. py:attribute:: HIGH_INTENSITY_EXERCISE_THRESHOLD
      :value: 'High Intensity Exercise Threshold'



   .. py:attribute:: HIGH_RESOLUTION_HEIGHT
      :value: 'High Resolution Height'



   .. py:attribute:: HIP_CIRCUMFERENCE
      :value: 'Hip Circumference'



   .. py:attribute:: LANGUAGE
      :value: 'Language'



   .. py:attribute:: LAST_NAME
      :value: 'Last Name'



   .. py:attribute:: MAXIMUM_RECOMMENDED_HEART_RATE
      :value: 'Maximum Recommended Heart Rate'



   .. py:attribute:: MIDDLE_NAME
      :value: 'Middle Name'



   .. py:attribute:: PREFERRED_UNITS
      :value: 'Preferred Units'



   .. py:attribute:: RESTING_HEART_RATE
      :value: 'Resting Heart Rate'



   .. py:attribute:: SEDENTARY_INTERVAL_NOTIFICATION
      :value: 'Sedentary Interval Notification'



   .. py:attribute:: SPORT_TYPE_FOR_AEROBIC_AND_ANAEROBIC_THRESHOLDS
      :value: 'Sport Type for Aerobic and Anaerobic Thresholds'



   .. py:attribute:: STRIDE_LENGTH
      :value: 'Stride Length'



   .. py:attribute:: THREE_ZONE_HEART_RATE_LIMITS
      :value: 'Three Zone Heart Rate Limits'



   .. py:attribute:: TWO_ZONE_HEART_RATE_LIMITS
      :value: 'Two Zone Heart Rate Limits'



   .. py:attribute:: VO2_MAX
      :value: 'VO2 Max'



   .. py:attribute:: WAIST_CIRCUMFERENCE
      :value: 'Waist Circumference'



   .. py:attribute:: WEIGHT
      :value: 'Weight'



   .. py:attribute:: ACS_CONTROL_POINT
      :value: 'ACS Control Point'



   .. py:attribute:: ACS_DATA_IN
      :value: 'ACS Data In'



   .. py:attribute:: ACS_DATA_OUT_INDICATE
      :value: 'ACS Data Out Indicate'



   .. py:attribute:: ACS_DATA_OUT_NOTIFY
      :value: 'ACS Data Out Notify'



   .. py:attribute:: ACS_STATUS
      :value: 'ACS Status'



   .. py:attribute:: AP_SYNC_KEY_MATERIAL
      :value: 'AP Sync Key Material'



   .. py:attribute:: ASE_CONTROL_POINT
      :value: 'ASE Control Point'



   .. py:attribute:: ACCELERATION
      :value: 'Acceleration'



   .. py:attribute:: ACCELERATION_3D
      :value: 'Acceleration 3D'



   .. py:attribute:: ACCELERATION_DETECTION_STATUS
      :value: 'Acceleration Detection Status'



   .. py:attribute:: ACTIVE_PRESET_INDEX
      :value: 'Active Preset Index'



   .. py:attribute:: ADVERTISING_CONSTANT_TONE_EXTENSION_INTERVAL
      :value: 'Advertising Constant Tone Extension Interval'



   .. py:attribute:: ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_LENGTH
      :value: 'Advertising Constant Tone Extension Minimum Length'



   .. py:attribute:: ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_TRANSMIT_COUNT
      :value: 'Advertising Constant Tone Extension Minimum Transmit Count'



   .. py:attribute:: ADVERTISING_CONSTANT_TONE_EXTENSION_PHY
      :value: 'Advertising Constant Tone Extension PHY'



   .. py:attribute:: ADVERTISING_CONSTANT_TONE_EXTENSION_TRANSMIT_DURATION
      :value: 'Advertising Constant Tone Extension Transmit Duration'



   .. py:attribute:: AGGREGATE
      :value: 'Aggregate'



   .. py:attribute:: ALTITUDE
      :value: 'Altitude'



   .. py:attribute:: APPARENT_ENERGY_32
      :value: 'Apparent Energy 32'



   .. py:attribute:: APPARENT_POWER
      :value: 'Apparent Power'



   .. py:attribute:: AUDIO_INPUT_CONTROL_POINT
      :value: 'Audio Input Control Point'



   .. py:attribute:: AUDIO_INPUT_DESCRIPTION
      :value: 'Audio Input Description'



   .. py:attribute:: AUDIO_INPUT_STATE
      :value: 'Audio Input State'



   .. py:attribute:: AUDIO_INPUT_STATUS
      :value: 'Audio Input Status'



   .. py:attribute:: AUDIO_INPUT_TYPE
      :value: 'Audio Input Type'



   .. py:attribute:: AUDIO_LOCATION
      :value: 'Audio Location'



   .. py:attribute:: AUDIO_OUTPUT_DESCRIPTION
      :value: 'Audio Output Description'



   .. py:attribute:: AVAILABLE_AUDIO_CONTEXTS
      :value: 'Available Audio Contexts'



   .. py:attribute:: BGR_FEATURES
      :value: 'BGR Features'



   .. py:attribute:: BGS_FEATURES
      :value: 'BGS Features'



   .. py:attribute:: BR_EDR_HANDOVER_DATA
      :value: 'BR-EDR Handover Data'



   .. py:attribute:: BSS_CONTROL_POINT
      :value: 'BSS Control Point'



   .. py:attribute:: BSS_RESPONSE
      :value: 'BSS Response'



   .. py:attribute:: BATTERY_CRITICAL_STATUS
      :value: 'Battery Critical Status'



   .. py:attribute:: BATTERY_ENERGY_STATUS
      :value: 'Battery Energy Status'



   .. py:attribute:: BATTERY_HEALTH_INFORMATION
      :value: 'Battery Health Information'



   .. py:attribute:: BATTERY_HEALTH_STATUS
      :value: 'Battery Health Status'



   .. py:attribute:: BATTERY_INFORMATION
      :value: 'Battery Information'



   .. py:attribute:: BATTERY_TIME_STATUS
      :value: 'Battery Time Status'



   .. py:attribute:: BEARER_LIST_CURRENT_CALLS
      :value: 'Bearer List Current Calls'



   .. py:attribute:: BEARER_PROVIDER_NAME
      :value: 'Bearer Provider Name'



   .. py:attribute:: BEARER_SIGNAL_STRENGTH
      :value: 'Bearer Signal Strength'



   .. py:attribute:: BEARER_SIGNAL_STRENGTH_REPORTING_INTERVAL
      :value: 'Bearer Signal Strength Reporting Interval'



   .. py:attribute:: BEARER_TECHNOLOGY
      :value: 'Bearer Technology'



   .. py:attribute:: BEARER_UCI
      :value: 'Bearer UCI'



   .. py:attribute:: BEARER_URI_SCHEMES_SUPPORTED_LIST
      :value: 'Bearer URI Schemes Supported List'



   .. py:attribute:: BLOOD_PRESSURE_RECORD
      :value: 'Blood Pressure Record'



   .. py:attribute:: BLUETOOTH_SIG_DATA
      :value: 'Bluetooth SIG Data'



   .. py:attribute:: BOOLEAN
      :value: 'Boolean'



   .. py:attribute:: BOOT_KEYBOARD_INPUT_REPORT
      :value: 'Boot Keyboard Input Report'



   .. py:attribute:: BOOT_KEYBOARD_OUTPUT_REPORT
      :value: 'Boot Keyboard Output Report'



   .. py:attribute:: BOOT_MOUSE_INPUT_REPORT
      :value: 'Boot Mouse Input Report'



   .. py:attribute:: BROADCAST_AUDIO_SCAN_CONTROL_POINT
      :value: 'Broadcast Audio Scan Control Point'



   .. py:attribute:: BROADCAST_RECEIVE_STATE
      :value: 'Broadcast Receive State'



   .. py:attribute:: CGM_FEATURE
      :value: 'CGM Feature'



   .. py:attribute:: CGM_MEASUREMENT
      :value: 'CGM Measurement'



   .. py:attribute:: CGM_SESSION_RUN_TIME
      :value: 'CGM Session Run Time'



   .. py:attribute:: CGM_SESSION_START_TIME
      :value: 'CGM Session Start Time'



   .. py:attribute:: CGM_SPECIFIC_OPS_CONTROL_POINT
      :value: 'CGM Specific Ops Control Point'



   .. py:attribute:: CGM_STATUS
      :value: 'CGM Status'



   .. py:attribute:: CIE_13_3_1995_COLOR_RENDERING_INDEX
      :value: 'CIE 13.3-1995 Color Rendering Index'



   .. py:attribute:: CALL_CONTROL_POINT
      :value: 'Call Control Point'



   .. py:attribute:: CALL_CONTROL_POINT_OPTIONAL_OPCODES
      :value: 'Call Control Point Optional Opcodes'



   .. py:attribute:: CALL_FRIENDLY_NAME
      :value: 'Call Friendly Name'



   .. py:attribute:: CALL_STATE
      :value: 'Call State'



   .. py:attribute:: CARBON_MONOXIDE_CONCENTRATION
      :value: 'Carbon Monoxide Concentration'



   .. py:attribute:: CARDIORESPIRATORY_ACTIVITY_INSTANTANEOUS_DATA
      :value: 'CardioRespiratory Activity Instantaneous Data'



   .. py:attribute:: CARDIORESPIRATORY_ACTIVITY_SUMMARY_DATA
      :value: 'CardioRespiratory Activity Summary Data'



   .. py:attribute:: CENTRAL_ADDRESS_RESOLUTION
      :value: 'Central Address Resolution'



   .. py:attribute:: CHROMATIC_DISTANCE_FROM_PLANCKIAN
      :value: 'Chromatic Distance from Planckian'



   .. py:attribute:: CHROMATICITY_COORDINATE
      :value: 'Chromaticity Coordinate'



   .. py:attribute:: CHROMATICITY_COORDINATES
      :value: 'Chromaticity Coordinates'



   .. py:attribute:: CHROMATICITY_TOLERANCE
      :value: 'Chromaticity Tolerance'



   .. py:attribute:: CHROMATICITY_IN_CCT_AND_DUV_VALUES
      :value: 'Chromaticity in CCT and Duv Values'



   .. py:attribute:: CLIENT_SUPPORTED_FEATURES
      :value: 'Client Supported Features'



   .. py:attribute:: COEFFICIENT
      :value: 'Coefficient'



   .. py:attribute:: CONSTANT_TONE_EXTENSION_ENABLE
      :value: 'Constant Tone Extension Enable'



   .. py:attribute:: CONTACT_STATUS_8
      :value: 'Contact Status 8'



   .. py:attribute:: CONTENT_CONTROL_ID
      :value: 'Content Control ID'



   .. py:attribute:: COORDINATED_SET_SIZE
      :value: 'Coordinated Set Size'



   .. py:attribute:: CORRELATED_COLOR_TEMPERATURE
      :value: 'Correlated Color Temperature'



   .. py:attribute:: COSINE_OF_THE_ANGLE
      :value: 'Cosine of the Angle'



   .. py:attribute:: COUNT_16
      :value: 'Count 16'



   .. py:attribute:: COUNT_24
      :value: 'Count 24'



   .. py:attribute:: COUNTRY_CODE
      :value: 'Country Code'



   .. py:attribute:: CURRENT_ELAPSED_TIME
      :value: 'Current Elapsed Time'



   .. py:attribute:: CURRENT_GROUP_OBJECT_ID
      :value: 'Current Group Object ID'



   .. py:attribute:: CURRENT_TRACK_OBJECT_ID
      :value: 'Current Track Object ID'



   .. py:attribute:: CURRENT_TRACK_SEGMENTS_OBJECT_ID
      :value: 'Current Track Segments Object ID'



   .. py:attribute:: DST_OFFSET
      :value: 'DST Offset'



   .. py:attribute:: DATABASE_CHANGE_INCREMENT
      :value: 'Database Change Increment'



   .. py:attribute:: DATABASE_HASH
      :value: 'Database Hash'



   .. py:attribute:: DATE_TIME
      :value: 'Date Time'



   .. py:attribute:: DATE_UTC
      :value: 'Date UTC'



   .. py:attribute:: DAY_DATE_TIME
      :value: 'Day Date Time'



   .. py:attribute:: DAY_OF_WEEK
      :value: 'Day of Week'



   .. py:attribute:: DESCRIPTOR_VALUE_CHANGED
      :value: 'Descriptor Value Changed'



   .. py:attribute:: DEVICE_TIME
      :value: 'Device Time'



   .. py:attribute:: DEVICE_TIME_CONTROL_POINT
      :value: 'Device Time Control Point'



   .. py:attribute:: DEVICE_TIME_FEATURE
      :value: 'Device Time Feature'



   .. py:attribute:: DEVICE_TIME_PARAMETERS
      :value: 'Device Time Parameters'



   .. py:attribute:: DOOR_WINDOW_STATUS
      :value: 'Door/Window Status'



   .. py:attribute:: ESL_ADDRESS
      :value: 'ESL Address'



   .. py:attribute:: ESL_CONTROL_POINT
      :value: 'ESL Control Point'



   .. py:attribute:: ESL_CURRENT_ABSOLUTE_TIME
      :value: 'ESL Current Absolute Time'



   .. py:attribute:: ESL_DISPLAY_INFORMATION
      :value: 'ESL Display Information'



   .. py:attribute:: ESL_IMAGE_INFORMATION
      :value: 'ESL Image Information'



   .. py:attribute:: ESL_LED_INFORMATION
      :value: 'ESL LED Information'



   .. py:attribute:: ESL_RESPONSE_KEY_MATERIAL
      :value: 'ESL Response Key Material'



   .. py:attribute:: ESL_SENSOR_INFORMATION
      :value: 'ESL Sensor Information'



   .. py:attribute:: EMERGENCY_ID
      :value: 'Emergency ID'



   .. py:attribute:: EMERGENCY_TEXT
      :value: 'Emergency Text'



   .. py:attribute:: ENCRYPTED_DATA_KEY_MATERIAL
      :value: 'Encrypted Data Key Material'



   .. py:attribute:: ENERGY
      :value: 'Energy'



   .. py:attribute:: ENERGY_32
      :value: 'Energy 32'



   .. py:attribute:: ENERGY_IN_A_PERIOD_OF_DAY
      :value: 'Energy in a Period of Day'



   .. py:attribute:: ENHANCED_BLOOD_PRESSURE_MEASUREMENT
      :value: 'Enhanced Blood Pressure Measurement'



   .. py:attribute:: ENHANCED_INTERMEDIATE_CUFF_PRESSURE
      :value: 'Enhanced Intermediate Cuff Pressure'



   .. py:attribute:: ESTIMATED_SERVICE_DATE
      :value: 'Estimated Service Date'



   .. py:attribute:: EVENT_STATISTICS
      :value: 'Event Statistics'



   .. py:attribute:: EXACT_TIME_256
      :value: 'Exact Time 256'



   .. py:attribute:: FIRST_USE_DATE
      :value: 'First Use Date'



   .. py:attribute:: FIXED_STRING_16
      :value: 'Fixed String 16'



   .. py:attribute:: FIXED_STRING_24
      :value: 'Fixed String 24'



   .. py:attribute:: FIXED_STRING_36
      :value: 'Fixed String 36'



   .. py:attribute:: FIXED_STRING_64
      :value: 'Fixed String 64'



   .. py:attribute:: FIXED_STRING_8
      :value: 'Fixed String 8'



   .. py:attribute:: FORCE
      :value: 'Force'



   .. py:attribute:: GHS_CONTROL_POINT
      :value: 'GHS Control Point'



   .. py:attribute:: GMAP_ROLE
      :value: 'GMAP Role'



   .. py:attribute:: GAIN_SETTINGS_ATTRIBUTE
      :value: 'Gain Settings Attribute'



   .. py:attribute:: GENERAL_ACTIVITY_INSTANTANEOUS_DATA
      :value: 'General Activity Instantaneous Data'



   .. py:attribute:: GENERAL_ACTIVITY_SUMMARY_DATA
      :value: 'General Activity Summary Data'



   .. py:attribute:: GENERIC_LEVEL
      :value: 'Generic Level'



   .. py:attribute:: GLOBAL_TRADE_ITEM_NUMBER
      :value: 'Global Trade Item Number'



   .. py:attribute:: GUST_FACTOR
      :value: 'Gust Factor'



   .. py:attribute:: HID_ISO_PROPERTIES
      :value: 'HID ISO Properties'



   .. py:attribute:: HTTP_CONTROL_POINT
      :value: 'HTTP Control Point'



   .. py:attribute:: HTTP_ENTITY_BODY
      :value: 'HTTP Entity Body'



   .. py:attribute:: HTTP_HEADERS
      :value: 'HTTP Headers'



   .. py:attribute:: HTTP_STATUS_CODE
      :value: 'HTTP Status Code'



   .. py:attribute:: HTTPS_SECURITY
      :value: 'HTTPS Security'



   .. py:attribute:: HEALTH_SENSOR_FEATURES
      :value: 'Health Sensor Features'



   .. py:attribute:: HEARING_AID_FEATURES
      :value: 'Hearing Aid Features'



   .. py:attribute:: HEARING_AID_PRESET_CONTROL_POINT
      :value: 'Hearing Aid Preset Control Point'



   .. py:attribute:: HEART_RATE_CONTROL_POINT
      :value: 'Heart Rate Control Point'



   .. py:attribute:: HIGH_TEMPERATURE
      :value: 'High Temperature'



   .. py:attribute:: HUMIDITY_8
      :value: 'Humidity 8'



   .. py:attribute:: IDD_ANNUNCIATION_STATUS
      :value: 'IDD Annunciation Status'



   .. py:attribute:: IDD_COMMAND_CONTROL_POINT
      :value: 'IDD Command Control Point'



   .. py:attribute:: IDD_COMMAND_DATA
      :value: 'IDD Command Data'



   .. py:attribute:: IDD_FEATURES
      :value: 'IDD Features'



   .. py:attribute:: IDD_HISTORY_DATA
      :value: 'IDD History Data'



   .. py:attribute:: IDD_RECORD_ACCESS_CONTROL_POINT
      :value: 'IDD Record Access Control Point'



   .. py:attribute:: IDD_STATUS
      :value: 'IDD Status'



   .. py:attribute:: IDD_STATUS_CHANGED
      :value: 'IDD Status Changed'



   .. py:attribute:: IDD_STATUS_READER_CONTROL_POINT
      :value: 'IDD Status Reader Control Point'



   .. py:attribute:: IEEE_11073_20601_REGULATORY_CERTIFICATION_DATA_LIST
      :value: 'IEEE 11073-20601 Regulatory Certification Data List'



   .. py:attribute:: IMD_CONTROL
      :value: 'IMD Control'



   .. py:attribute:: IMD_HISTORICAL_DATA
      :value: 'IMD Historical Data'



   .. py:attribute:: IMD_STATUS
      :value: 'IMD Status'



   .. py:attribute:: IMDS_DESCRIPTOR_VALUE_CHANGED
      :value: 'IMDS Descriptor Value Changed'



   .. py:attribute:: ILLUMINANCE_16
      :value: 'Illuminance 16'



   .. py:attribute:: INCOMING_CALL
      :value: 'Incoming Call'



   .. py:attribute:: INCOMING_CALL_TARGET_BEARER_URI
      :value: 'Incoming Call Target Bearer URI'



   .. py:attribute:: INTERMEDIATE_TEMPERATURE
      :value: 'Intermediate Temperature'



   .. py:attribute:: IRRADIANCE
      :value: 'Irradiance'



   .. py:attribute:: LE_GATT_SECURITY_LEVELS
      :value: 'LE GATT Security Levels'



   .. py:attribute:: LE_HID_OPERATION_MODE
      :value: 'LE HID Operation Mode'



   .. py:attribute:: LENGTH
      :value: 'Length'



   .. py:attribute:: LIFE_CYCLE_DATA
      :value: 'Life Cycle Data'



   .. py:attribute:: LIGHT_DISTRIBUTION
      :value: 'Light Distribution'



   .. py:attribute:: LIGHT_OUTPUT
      :value: 'Light Output'



   .. py:attribute:: LIGHT_SOURCE_TYPE
      :value: 'Light Source Type'



   .. py:attribute:: LINEAR_POSITION
      :value: 'Linear Position'



   .. py:attribute:: LIVE_HEALTH_OBSERVATIONS
      :value: 'Live Health Observations'



   .. py:attribute:: LOCAL_EAST_COORDINATE
      :value: 'Local East Coordinate'



   .. py:attribute:: LOCAL_NORTH_COORDINATE
      :value: 'Local North Coordinate'



   .. py:attribute:: LUMINOUS_EFFICACY
      :value: 'Luminous Efficacy'



   .. py:attribute:: LUMINOUS_ENERGY
      :value: 'Luminous Energy'



   .. py:attribute:: LUMINOUS_EXPOSURE
      :value: 'Luminous Exposure'



   .. py:attribute:: LUMINOUS_FLUX
      :value: 'Luminous Flux'



   .. py:attribute:: LUMINOUS_FLUX_RANGE
      :value: 'Luminous Flux Range'



   .. py:attribute:: LUMINOUS_INTENSITY
      :value: 'Luminous Intensity'



   .. py:attribute:: MASS_FLOW
      :value: 'Mass Flow'



   .. py:attribute:: MEASUREMENT_INTERVAL
      :value: 'Measurement Interval'



   .. py:attribute:: MEDIA_CONTROL_POINT
      :value: 'Media Control Point'



   .. py:attribute:: MEDIA_CONTROL_POINT_OPCODES_SUPPORTED
      :value: 'Media Control Point Opcodes Supported'



   .. py:attribute:: MEDIA_PLAYER_ICON_OBJECT_ID
      :value: 'Media Player Icon Object ID'



   .. py:attribute:: MEDIA_PLAYER_ICON_URL
      :value: 'Media Player Icon URL'



   .. py:attribute:: MEDIA_PLAYER_NAME
      :value: 'Media Player Name'



   .. py:attribute:: MEDIA_STATE
      :value: 'Media State'



   .. py:attribute:: MESH_PROVISIONING_DATA_IN
      :value: 'Mesh Provisioning Data In'



   .. py:attribute:: MESH_PROVISIONING_DATA_OUT
      :value: 'Mesh Provisioning Data Out'



   .. py:attribute:: MESH_PROXY_DATA_IN
      :value: 'Mesh Proxy Data In'



   .. py:attribute:: MESH_PROXY_DATA_OUT
      :value: 'Mesh Proxy Data Out'



   .. py:attribute:: MUTE
      :value: 'Mute'



   .. py:attribute:: NEXT_TRACK_OBJECT_ID
      :value: 'Next Track Object ID'



   .. py:attribute:: OTS_FEATURE
      :value: 'OTS Feature'



   .. py:attribute:: OBJECT_ACTION_CONTROL_POINT
      :value: 'Object Action Control Point'



   .. py:attribute:: OBJECT_CHANGED
      :value: 'Object Changed'



   .. py:attribute:: OBJECT_FIRST_CREATED
      :value: 'Object First-Created'



   .. py:attribute:: OBJECT_ID
      :value: 'Object ID'



   .. py:attribute:: OBJECT_LAST_MODIFIED
      :value: 'Object Last-Modified'



   .. py:attribute:: OBJECT_LIST_CONTROL_POINT
      :value: 'Object List Control Point'



   .. py:attribute:: OBJECT_LIST_FILTER
      :value: 'Object List Filter'



   .. py:attribute:: OBJECT_NAME
      :value: 'Object Name'



   .. py:attribute:: OBJECT_PROPERTIES
      :value: 'Object Properties'



   .. py:attribute:: OBJECT_SIZE
      :value: 'Object Size'



   .. py:attribute:: OBJECT_TYPE
      :value: 'Object Type'



   .. py:attribute:: OBSERVATION_SCHEDULE_CHANGED
      :value: 'Observation Schedule Changed'



   .. py:attribute:: ON_DEMAND_RANGING_DATA
      :value: 'On-demand Ranging Data'



   .. py:attribute:: PARENT_GROUP_OBJECT_ID
      :value: 'Parent Group Object ID'



   .. py:attribute:: PERCEIVED_LIGHTNESS
      :value: 'Perceived Lightness'



   .. py:attribute:: PERCENTAGE_8
      :value: 'Percentage 8'



   .. py:attribute:: PERCENTAGE_8_STEPS
      :value: 'Percentage 8 Steps'



   .. py:attribute:: PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS
      :value: 'Peripheral Preferred Connection Parameters'



   .. py:attribute:: PERIPHERAL_PRIVACY_FLAG
      :value: 'Peripheral Privacy Flag'



   .. py:attribute:: PHYSICAL_ACTIVITY_CURRENT_SESSION
      :value: 'Physical Activity Current Session'



   .. py:attribute:: PHYSICAL_ACTIVITY_MONITOR_CONTROL_POINT
      :value: 'Physical Activity Monitor Control Point'



   .. py:attribute:: PHYSICAL_ACTIVITY_MONITOR_FEATURES
      :value: 'Physical Activity Monitor Features'



   .. py:attribute:: PHYSICAL_ACTIVITY_SESSION_DESCRIPTOR
      :value: 'Physical Activity Session Descriptor'



   .. py:attribute:: PLAYBACK_SPEED
      :value: 'Playback Speed'



   .. py:attribute:: PLAYING_ORDER
      :value: 'Playing Order'



   .. py:attribute:: PLAYING_ORDERS_SUPPORTED
      :value: 'Playing Orders Supported'



   .. py:attribute:: PNP_ID
      :value: 'PnP ID'



   .. py:attribute:: POWER
      :value: 'Power'



   .. py:attribute:: PRECISE_ACCELERATION_3D
      :value: 'Precise Acceleration 3D'



   .. py:attribute:: PUSHBUTTON_STATUS_8
      :value: 'Pushbutton Status 8'



   .. py:attribute:: RAS_CONTROL_POINT
      :value: 'RAS Control Point'



   .. py:attribute:: RAS_FEATURES
      :value: 'RAS Features'



   .. py:attribute:: RC_FEATURE
      :value: 'RC Feature'



   .. py:attribute:: RC_SETTINGS
      :value: 'RC Settings'



   .. py:attribute:: RANGING_DATA_OVERWRITTEN
      :value: 'Ranging Data Overwritten'



   .. py:attribute:: RANGING_DATA_READY
      :value: 'Ranging Data Ready'



   .. py:attribute:: REAL_TIME_RANGING_DATA
      :value: 'Real-time Ranging Data'



   .. py:attribute:: RECONNECTION_ADDRESS
      :value: 'Reconnection Address'



   .. py:attribute:: RECONNECTION_CONFIGURATION_CONTROL_POINT
      :value: 'Reconnection Configuration Control Point'



   .. py:attribute:: RECORD_ACCESS_CONTROL_POINT
      :value: 'Record Access Control Point'



   .. py:attribute:: REGISTERED_USER
      :value: 'Registered User'



   .. py:attribute:: RELATIVE_RUNTIME_IN_A_CORRELATED_COLOR_TEMPERATURE_RANGE
      :value: 'Relative Runtime in a Correlated Color Temperature Range'



   .. py:attribute:: RELATIVE_RUNTIME_IN_A_CURRENT_RANGE
      :value: 'Relative Runtime in a Current Range'



   .. py:attribute:: RELATIVE_RUNTIME_IN_A_GENERIC_LEVEL_RANGE
      :value: 'Relative Runtime in a Generic Level Range'



   .. py:attribute:: RELATIVE_VALUE_IN_A_PERIOD_OF_DAY
      :value: 'Relative Value in a Period of Day'



   .. py:attribute:: RELATIVE_VALUE_IN_A_TEMPERATURE_RANGE
      :value: 'Relative Value in a Temperature Range'



   .. py:attribute:: RELATIVE_VALUE_IN_A_VOLTAGE_RANGE
      :value: 'Relative Value in a Voltage Range'



   .. py:attribute:: RELATIVE_VALUE_IN_AN_ILLUMINANCE_RANGE
      :value: 'Relative Value in an Illuminance Range'



   .. py:attribute:: RESOLVABLE_PRIVATE_ADDRESS_ONLY
      :value: 'Resolvable Private Address Only'



   .. py:attribute:: ROTATIONAL_SPEED
      :value: 'Rotational Speed'



   .. py:attribute:: SC_CONTROL_POINT
      :value: 'SC Control Point'



   .. py:attribute:: SCAN_REFRESH
      :value: 'Scan Refresh'



   .. py:attribute:: SEARCH_CONTROL_POINT
      :value: 'Search Control Point'



   .. py:attribute:: SEARCH_RESULTS_OBJECT_ID
      :value: 'Search Results Object ID'



   .. py:attribute:: SEEKING_SPEED
      :value: 'Seeking Speed'



   .. py:attribute:: SENSOR_LOCATION
      :value: 'Sensor Location'



   .. py:attribute:: SERVER_SUPPORTED_FEATURES
      :value: 'Server Supported Features'



   .. py:attribute:: SERVICE_CYCLE_DATA
      :value: 'Service Cycle Data'



   .. py:attribute:: SET_IDENTITY_RESOLVING_KEY
      :value: 'Set Identity Resolving Key'



   .. py:attribute:: SET_MEMBER_LOCK
      :value: 'Set Member Lock'



   .. py:attribute:: SET_MEMBER_RANK
      :value: 'Set Member Rank'



   .. py:attribute:: SINK_ASE
      :value: 'Sink ASE'



   .. py:attribute:: SINK_AUDIO_LOCATIONS
      :value: 'Sink Audio Locations'



   .. py:attribute:: SINK_PAC
      :value: 'Sink PAC'



   .. py:attribute:: SLEEP_ACTIVITY_INSTANTANEOUS_DATA
      :value: 'Sleep Activity Instantaneous Data'



   .. py:attribute:: SLEEP_ACTIVITY_SUMMARY_DATA
      :value: 'Sleep Activity Summary Data'



   .. py:attribute:: SOURCE_ASE
      :value: 'Source ASE'



   .. py:attribute:: SOURCE_AUDIO_LOCATIONS
      :value: 'Source Audio Locations'



   .. py:attribute:: SOURCE_PAC
      :value: 'Source PAC'



   .. py:attribute:: STATUS_FLAGS
      :value: 'Status Flags'



   .. py:attribute:: STEP_COUNTER_ACTIVITY_SUMMARY_DATA
      :value: 'Step Counter Activity Summary Data'



   .. py:attribute:: STORED_HEALTH_OBSERVATIONS
      :value: 'Stored Health Observations'



   .. py:attribute:: SULFUR_HEXAFLUORIDE_CONCENTRATION
      :value: 'Sulfur Hexafluoride Concentration'



   .. py:attribute:: SUPPORTED_AUDIO_CONTEXTS
      :value: 'Supported Audio Contexts'



   .. py:attribute:: SYSTEM_ID
      :value: 'System ID'



   .. py:attribute:: TDS_CONTROL_POINT
      :value: 'TDS Control Point'



   .. py:attribute:: TMAP_ROLE
      :value: 'TMAP Role'



   .. py:attribute:: TEMPERATURE_8
      :value: 'Temperature 8'



   .. py:attribute:: TEMPERATURE_8_STATISTICS
      :value: 'Temperature 8 Statistics'



   .. py:attribute:: TEMPERATURE_8_IN_A_PERIOD_OF_DAY
      :value: 'Temperature 8 in a Period of Day'



   .. py:attribute:: TEMPERATURE_RANGE
      :value: 'Temperature Range'



   .. py:attribute:: TEMPERATURE_STATISTICS
      :value: 'Temperature Statistics'



   .. py:attribute:: TEMPERATURE_TYPE
      :value: 'Temperature Type'



   .. py:attribute:: TERMINATION_REASON
      :value: 'Termination Reason'



   .. py:attribute:: TIME_ACCURACY
      :value: 'Time Accuracy'



   .. py:attribute:: TIME_CHANGE_LOG_DATA
      :value: 'Time Change Log Data'



   .. py:attribute:: TIME_DECIHOUR_8
      :value: 'Time Decihour 8'



   .. py:attribute:: TIME_EXPONENTIAL_8
      :value: 'Time Exponential 8'



   .. py:attribute:: TIME_HOUR_24
      :value: 'Time Hour 24'



   .. py:attribute:: TIME_MILLISECOND_24
      :value: 'Time Millisecond 24'



   .. py:attribute:: TIME_SECOND_16
      :value: 'Time Second 16'



   .. py:attribute:: TIME_SECOND_32
      :value: 'Time Second 32'



   .. py:attribute:: TIME_SECOND_8
      :value: 'Time Second 8'



   .. py:attribute:: TIME_SOURCE
      :value: 'Time Source'



   .. py:attribute:: TORQUE
      :value: 'Torque'



   .. py:attribute:: TRACK_CHANGED
      :value: 'Track Changed'



   .. py:attribute:: TRACK_DURATION
      :value: 'Track Duration'



   .. py:attribute:: TRACK_POSITION
      :value: 'Track Position'



   .. py:attribute:: TRACK_TITLE
      :value: 'Track Title'



   .. py:attribute:: UDI_FOR_MEDICAL_DEVICES
      :value: 'UDI for Medical Devices'



   .. py:attribute:: UGG_FEATURES
      :value: 'UGG Features'



   .. py:attribute:: UGT_FEATURES
      :value: 'UGT Features'



   .. py:attribute:: URI
      :value: 'URI'



   .. py:attribute:: UNCERTAINTY
      :value: 'Uncertainty'



   .. py:attribute:: USER_CONTROL_POINT
      :value: 'User Control Point'



   .. py:attribute:: USER_INDEX
      :value: 'User Index'



   .. py:attribute:: VOLUME_CONTROL_POINT
      :value: 'Volume Control Point'



   .. py:attribute:: VOLUME_FLAGS
      :value: 'Volume Flags'



   .. py:attribute:: VOLUME_FLOW
      :value: 'Volume Flow'



   .. py:attribute:: VOLUME_OFFSET_CONTROL_POINT
      :value: 'Volume Offset Control Point'



   .. py:attribute:: VOLUME_OFFSET_STATE
      :value: 'Volume Offset State'



   .. py:attribute:: VOLUME_STATE
      :value: 'Volume State'



   .. py:attribute:: WORK_CYCLE_DATA
      :value: 'Work Cycle Data'



.. py:function:: get_characteristic_class_map() -> dict[src.bluetooth_sig.types.gatt_enums.CharacteristicName, type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]]

   Get the current characteristic class map.

   Backward compatibility function that returns the current registry state.

   :returns: Dictionary mapping CharacteristicName enum to characteristic classes


.. py:class:: CharacteristicRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.CharacteristicName`\ , :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`\ ]


   Encapsulates all GATT characteristic registry operations.


   .. py:method:: register_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, char_cls: type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic], override: bool = False) -> None
      :classmethod:


      Register a custom characteristic class at runtime.

      Backward compatibility wrapper for register_class().



   .. py:method:: unregister_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom characteristic class.

      Backward compatibility wrapper for unregister_class().



   .. py:method:: get_characteristic_class(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given CharacteristicName enum.

      Backward compatibility wrapper for get_class_by_enum().



   .. py:method:: get_characteristic_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given UUID.

      Backward compatibility wrapper for get_class_by_uuid().



   .. py:method:: create_characteristic(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic | None
      :classmethod:


      Create a characteristic instance from a UUID.

      :param uuid: The characteristic UUID (string, BluetoothUUID, or int)

      :returns: Characteristic instance if found, None if UUID not registered

      :raises ValueError: If uuid format is invalid



   .. py:method:: list_all_characteristic_names() -> list[str]
      :staticmethod:


      List all supported characteristic names as strings.



   .. py:method:: list_all_characteristic_enums() -> list[src.bluetooth_sig.types.gatt_enums.CharacteristicName]
      :staticmethod:


      List all supported characteristic names as enum values.



   .. py:method:: get_all_characteristics() -> dict[src.bluetooth_sig.types.gatt_enums.CharacteristicName, type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]]
      :classmethod:


      Get all registered characteristic classes.



   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom characteristic registrations (for testing).



   .. py:method:: clear_cache() -> None
      :classmethod:


      Clear the characteristic class map cache (for testing).



