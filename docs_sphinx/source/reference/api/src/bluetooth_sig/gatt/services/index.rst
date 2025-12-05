src.bluetooth_sig.gatt.services
===============================

.. py:module:: src.bluetooth_sig.gatt.services

.. autoapi-nested-parse::

   Registry of supported GATT services.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/gatt/services/alert_notification/index
   /reference/api/src/bluetooth_sig/gatt/services/automation_io/index
   /reference/api/src/bluetooth_sig/gatt/services/base/index
   /reference/api/src/bluetooth_sig/gatt/services/battery_service/index
   /reference/api/src/bluetooth_sig/gatt/services/blood_pressure/index
   /reference/api/src/bluetooth_sig/gatt/services/body_composition/index
   /reference/api/src/bluetooth_sig/gatt/services/bond_management/index
   /reference/api/src/bluetooth_sig/gatt/services/current_time_service/index
   /reference/api/src/bluetooth_sig/gatt/services/custom/index
   /reference/api/src/bluetooth_sig/gatt/services/cycling_power/index
   /reference/api/src/bluetooth_sig/gatt/services/cycling_speed_and_cadence/index
   /reference/api/src/bluetooth_sig/gatt/services/device_information/index
   /reference/api/src/bluetooth_sig/gatt/services/environmental_sensing/index
   /reference/api/src/bluetooth_sig/gatt/services/fitness_machine_service/index
   /reference/api/src/bluetooth_sig/gatt/services/generic_access/index
   /reference/api/src/bluetooth_sig/gatt/services/generic_attribute/index
   /reference/api/src/bluetooth_sig/gatt/services/glucose/index
   /reference/api/src/bluetooth_sig/gatt/services/health_thermometer/index
   /reference/api/src/bluetooth_sig/gatt/services/heart_rate/index
   /reference/api/src/bluetooth_sig/gatt/services/human_interface_device/index
   /reference/api/src/bluetooth_sig/gatt/services/immediate_alert/index
   /reference/api/src/bluetooth_sig/gatt/services/indoor_positioning_service/index
   /reference/api/src/bluetooth_sig/gatt/services/link_loss/index
   /reference/api/src/bluetooth_sig/gatt/services/location_and_navigation/index
   /reference/api/src/bluetooth_sig/gatt/services/next_dst_change/index
   /reference/api/src/bluetooth_sig/gatt/services/phone_alert_status/index
   /reference/api/src/bluetooth_sig/gatt/services/pulse_oximeter_service/index
   /reference/api/src/bluetooth_sig/gatt/services/reference_time_update/index
   /reference/api/src/bluetooth_sig/gatt/services/registry/index
   /reference/api/src/bluetooth_sig/gatt/services/running_speed_and_cadence/index
   /reference/api/src/bluetooth_sig/gatt/services/scan_parameters/index
   /reference/api/src/bluetooth_sig/gatt/services/tx_power/index
   /reference/api/src/bluetooth_sig/gatt/services/unknown/index
   /reference/api/src/bluetooth_sig/gatt/services/user_data/index
   /reference/api/src/bluetooth_sig/gatt/services/weight_scale/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.AlertNotificationService
   src.bluetooth_sig.gatt.services.AutomationIOService
   src.bluetooth_sig.gatt.services.CharacteristicStatus
   src.bluetooth_sig.gatt.services.ServiceCharacteristicInfo
   src.bluetooth_sig.gatt.services.ServiceCompletenessReport
   src.bluetooth_sig.gatt.services.ServiceHealthStatus
   src.bluetooth_sig.gatt.services.ServiceValidationResult
   src.bluetooth_sig.gatt.services.BatteryService
   src.bluetooth_sig.gatt.services.BloodPressureService
   src.bluetooth_sig.gatt.services.BodyCompositionService
   src.bluetooth_sig.gatt.services.BondManagementService
   src.bluetooth_sig.gatt.services.CurrentTimeService
   src.bluetooth_sig.gatt.services.CyclingPowerService
   src.bluetooth_sig.gatt.services.CyclingSpeedAndCadenceService
   src.bluetooth_sig.gatt.services.DeviceInformationService
   src.bluetooth_sig.gatt.services.EnvironmentalSensingService
   src.bluetooth_sig.gatt.services.GenericAccessService
   src.bluetooth_sig.gatt.services.GenericAttributeService
   src.bluetooth_sig.gatt.services.GlucoseService
   src.bluetooth_sig.gatt.services.HealthThermometerService
   src.bluetooth_sig.gatt.services.HeartRateService
   src.bluetooth_sig.gatt.services.ImmediateAlertService
   src.bluetooth_sig.gatt.services.LinkLossService
   src.bluetooth_sig.gatt.services.LocationAndNavigationService
   src.bluetooth_sig.gatt.services.NextDstChangeService
   src.bluetooth_sig.gatt.services.PhoneAlertStatusService
   src.bluetooth_sig.gatt.services.ReferenceTimeUpdateService
   src.bluetooth_sig.gatt.services.GattServiceRegistry
   src.bluetooth_sig.gatt.services.ServiceName
   src.bluetooth_sig.gatt.services.RunningSpeedAndCadenceService
   src.bluetooth_sig.gatt.services.ScanParametersService
   src.bluetooth_sig.gatt.services.TxPowerService
   src.bluetooth_sig.gatt.services.WeightScaleService


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.get_service_class_map


Package Contents
----------------

.. py:class:: AlertNotificationService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Alert Notification Service implementation.

   Exposes alert information from a device to a peer device.

   Contains characteristics related to alert notifications:
   - Supported New Alert Category - Required
   - New Alert - Optional
   - Supported Unread Alert Category - Required
   - Unread Alert Status - Optional
   - Alert Notification Control Point - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: AutomationIOService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Automation IO Service implementation.

   Contains characteristics related to electrical power monitoring and automation:
   - Electric Current - Optional
   - Voltage - Optional
   - Average Current - Optional
   - Average Voltage - Optional
   - Electric Current Range - Optional
   - Electric Current Specification - Optional
   - Electric Current Statistics - Optional
   - Voltage Specification - Optional
   - Voltage Statistics - Optional
   - High Voltage - Optional
   - Voltage Frequency - Optional
   - Supported Power Range - Optional
   - Tx Power Level - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: CharacteristicStatus(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Status of characteristics within a service.


   .. py:attribute:: PRESENT
      :value: 'present'



   .. py:attribute:: MISSING
      :value: 'missing'



   .. py:attribute:: INVALID
      :value: 'invalid'



.. py:class:: ServiceCharacteristicInfo

   Bases: :py:obj:`src.bluetooth_sig.types.CharacteristicInfo`


   Service-specific information about a characteristic with context about its presence.

   Provides status, requirement, and class context for a characteristic within a service.


   .. py:attribute:: status
      :type:  CharacteristicStatus


   .. py:attribute:: is_required
      :type:  bool
      :value: False



   .. py:attribute:: is_conditional
      :type:  bool
      :value: False



   .. py:attribute:: condition_description
      :type:  str
      :value: ''



   .. py:attribute:: char_class
      :type:  type[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic] | None
      :value: None



.. py:class:: ServiceCompletenessReport

   Bases: :py:obj:`msgspec.Struct`


   Comprehensive report about service completeness and health.


   .. py:attribute:: service_name
      :type:  str


   .. py:attribute:: service_uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: health_status
      :type:  ServiceHealthStatus


   .. py:attribute:: is_healthy
      :type:  bool


   .. py:attribute:: characteristics_present
      :type:  int


   .. py:attribute:: characteristics_expected
      :type:  int


   .. py:attribute:: characteristics_required
      :type:  int


   .. py:attribute:: present_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: missing_required
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: missing_optional
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: invalid_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: warnings
      :type:  list[str]


   .. py:attribute:: errors
      :type:  list[str]


   .. py:attribute:: missing_details
      :type:  dict[str, ServiceCharacteristicInfo]


.. py:class:: ServiceHealthStatus(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Health status of a GATT service.


   .. py:attribute:: COMPLETE
      :value: 'complete'



   .. py:attribute:: FUNCTIONAL
      :value: 'functional'



   .. py:attribute:: PARTIAL
      :value: 'partial'



   .. py:attribute:: INCOMPLETE
      :value: 'incomplete'



.. py:class:: ServiceValidationResult

   Bases: :py:obj:`msgspec.Struct`


   Result of service validation.


   .. py:attribute:: status
      :type:  ServiceHealthStatus


   .. py:attribute:: missing_required
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: missing_optional
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: invalid_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: warnings
      :type:  list[str]


   .. py:attribute:: errors
      :type:  list[str]


   .. py:property:: is_healthy
      :type: bool


      Check if service is in a healthy state.


   .. py:property:: has_errors
      :type: bool


      Check if service has any errors.


.. py:class:: BatteryService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Battery Service implementation.

   Contains characteristics related to battery information:
   - Battery Level - Required
   - Battery Level Status - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: BloodPressureService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Blood Pressure Service implementation.

   Contains characteristics related to blood pressure measurement:
   - Blood Pressure Measurement - Required
   - Intermediate Cuff Pressure - Optional
   - Blood Pressure Feature - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: BodyCompositionService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Body Composition Service implementation (0x181B).

   Used for smart scale devices that measure body composition metrics
   including body fat percentage, muscle mass, bone mass, and water
   percentage. Contains Body Composition Measurement and Body
   Composition Feature characteristics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: BondManagementService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Bond Management Service implementation.

   Contains characteristics for managing Bluetooth bonds:
   - Bond Management Feature - Required
   - Bond Management Control Point - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: CurrentTimeService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Current Time Service implementation.

   Exposes the current date and time with additional information.

   Contains characteristics related to time:
   - Current Time - Required
   - Local Time Information - Optional
   - Reference Time Information - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: CyclingPowerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Cycling Power Service implementation (0x1818).

   Used for cycling power meters that measure power output in watts.
   Supports instantaneous power, force/torque vectors, and control
   functions.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: CyclingSpeedAndCadenceService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Cycling Speed and Cadence Service implementation (0x1816).

   Used for cycling sensors that measure wheel and crank revolutions.
   Contains the CSC Measurement characteristic for cycling metrics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: DeviceInformationService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Device Information Service implementation.

   Contains characteristics that expose device information:
   - Manufacturer Name String - Required
   - Model Number String - Optional
   - Serial Number String - Optional
   - Hardware Revision String - Optional
   - Firmware Revision String - Optional
   - Software Revision String - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: EnvironmentalSensingService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Environmental Sensing Service implementation (0x181A).

   Used for environmental monitoring devices including weather stations,
   air quality sensors, and comprehensive environmental monitoring systems.
   Supports a wide range of environmental measurements including:
   - Traditional weather measurements (temperature, humidity, pressure)
   - Air quality metrics (gas concentrations, particulate matter)
   - Advanced environmental conditions (wind, elevation, trends)

   Contains comprehensive characteristics for environmental sensing including:
   - Temperature - Optional
   - Humidity - Optional
   - Pressure - Optional
   - Dew Point - Optional
   - Heat Index - Optional
   - Wind Chill - Optional
   - True Wind Speed - Optional
   - True Wind Direction - Optional
   - Apparent Wind Speed - Optional
   - Apparent Wind Direction - Optional
   - CO2 Concentration - Optional
   - VOC Concentration - Optional
   - Non-Methane VOC Concentration - Optional
   - Ammonia Concentration - Optional
   - Methane Concentration - Optional
   - Nitrogen Dioxide Concentration - Optional
   - Ozone Concentration - Optional
   - PM1 Concentration - Optional
   - PM2.5 Concentration - Optional
   - PM10 Concentration - Optional
   - Sulfur Dioxide Concentration - Optional
   - Elevation - Optional
   - Barometric Pressure Trend - Optional
   - Pollen Concentration - Optional
   - Rainfall - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: GenericAccessService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic Access Service implementation.

   Contains characteristics that expose basic device access information:
   - Device Name - Required
   - Appearance - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: GenericAttributeService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic Attribute Service implementation.

   The GATT Service contains information about the GATT database and is
   primarily used for service discovery and attribute access.

   This service typically contains:
   - Service Changed characteristic (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: GlucoseService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Glucose Service implementation (0x1808).

   Used for glucose monitoring devices including continuous glucose
   monitors (CGMs) and traditional glucose meters. Provides
   comprehensive glucose measurement data with context and device
   capabilities.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: HealthThermometerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Health Thermometer Service implementation (0x1809).

   Used for medical temperature measurement devices. Contains the
   Temperature Measurement characteristic for medical-grade temperature
   readings.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: HeartRateService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Heart Rate Service implementation (0x180D).

   Used for heart rate monitoring devices. Contains the Heart Rate
   Measurement characteristic for heart rate data with optional RR-
   intervals and energy expenditure.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: ImmediateAlertService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Immediate Alert Service implementation.

   Exposes a control point to allow a peer device to cause the device to
   immediately alert.

   Contains characteristics related to immediate alerts:
   - Alert Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: LinkLossService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Link Loss Service implementation.

   Defines behaviour when a link is lost between two devices.

   Contains characteristics related to link loss alerts:
   - Alert Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: LocationAndNavigationService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Location and Navigation Service implementation.

   Contains characteristics related to location and navigation data:
   - LN Feature - Required
   - Location and Speed - Optional
   - Navigation - Optional
   - Position Quality - Optional
   - LN Control Point - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: NextDstChangeService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Next DST Change Service implementation.

   Exposes the date and time of the next Daylight Saving Time change.

   Contains characteristics related to DST changes:
   - Time with DST - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: PhoneAlertStatusService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Phone Alert Status Service implementation.

   Contains characteristics related to phone alert status:
   - Alert Status - Required
   - Ringer Setting - Required
   - Ringer Control Point - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: ReferenceTimeUpdateService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Reference Time Update Service implementation.

   Allows clients to request time updates from reference time sources.

   Contains characteristics related to time updates:
   - Time Update Control Point - Required
   - Time Update State - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: GattServiceRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.ServiceName`\ , :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`\ ]


   Registry for all supported GATT services.


   .. py:method:: register_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, service_cls: type[src.bluetooth_sig.gatt.services.base.BaseGattService], override: bool = False) -> None
      :classmethod:


      Register a custom service class at runtime.

      :param uuid: The service UUID
      :param service_cls: The service class to register
      :param override: Whether to override existing registrations

      :raises TypeError: If service_cls does not inherit from BaseGattService
      :raises ValueError: If UUID conflicts with existing registration and override=False



   .. py:method:: unregister_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom service class.

      :param uuid: The service UUID to unregister



   .. py:method:: get_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID.

      :param uuid: The service UUID

      :returns: Service class if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_service_class_by_name(name: str | src.bluetooth_sig.types.gatt_enums.ServiceName) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given name or enum.



   .. py:method:: get_service_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID (alias for get_service_class).



   .. py:method:: create_service(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, characteristics: src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData) -> src.bluetooth_sig.gatt.services.base.BaseGattService | None
      :classmethod:


      Create a service instance for the given UUID and characteristics.

      :param uuid: Service UUID
      :param characteristics: Dict mapping characteristic UUIDs to CharacteristicInfo

      :returns: Service instance if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_all_services() -> list[type[src.bluetooth_sig.gatt.services.base.BaseGattService]]
      :classmethod:


      Get all registered service classes.

      :returns: List of all registered service classes



   .. py:method:: supported_services() -> list[str]
      :classmethod:


      Get a list of supported service UUIDs.



   .. py:method:: supported_service_names() -> list[str]
      :classmethod:


      Get a list of supported service names.



   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom service registrations (for testing).



.. py:class:: ServiceName(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Enumeration of all supported GATT service names.


   .. py:attribute:: GAP
      :value: 'GAP'



   .. py:attribute:: GATT
      :value: 'GATT'



   .. py:attribute:: IMMEDIATE_ALERT
      :value: 'Immediate Alert'



   .. py:attribute:: LINK_LOSS
      :value: 'Link Loss'



   .. py:attribute:: TX_POWER
      :value: 'Tx Power'



   .. py:attribute:: NEXT_DST_CHANGE
      :value: 'Next DST Change'



   .. py:attribute:: DEVICE_INFORMATION
      :value: 'Device Information'



   .. py:attribute:: BATTERY
      :value: 'Battery'



   .. py:attribute:: HEART_RATE
      :value: 'Heart Rate'



   .. py:attribute:: BLOOD_PRESSURE
      :value: 'Blood Pressure'



   .. py:attribute:: HEALTH_THERMOMETER
      :value: 'Health Thermometer'



   .. py:attribute:: GLUCOSE
      :value: 'Glucose'



   .. py:attribute:: CYCLING_SPEED_AND_CADENCE
      :value: 'Cycling Speed and Cadence'



   .. py:attribute:: CYCLING_POWER
      :value: 'Cycling Power'



   .. py:attribute:: RUNNING_SPEED_AND_CADENCE
      :value: 'Running Speed and Cadence'



   .. py:attribute:: AUTOMATION_IO
      :value: 'Automation IO'



   .. py:attribute:: ENVIRONMENTAL_SENSING
      :value: 'Environmental Sensing'



   .. py:attribute:: ALERT_NOTIFICATION
      :value: 'Alert Notification'



   .. py:attribute:: BODY_COMPOSITION
      :value: 'Body Composition'



   .. py:attribute:: USER_DATA
      :value: 'User Data'



   .. py:attribute:: WEIGHT_SCALE
      :value: 'Weight Scale'



   .. py:attribute:: LOCATION_AND_NAVIGATION
      :value: 'Location and Navigation'



   .. py:attribute:: PHONE_ALERT_STATUS
      :value: 'Phone Alert Status'



   .. py:attribute:: REFERENCE_TIME_UPDATE
      :value: 'Reference Time Update'



   .. py:attribute:: CURRENT_TIME
      :value: 'Current Time'



   .. py:attribute:: SCAN_PARAMETERS
      :value: 'Scan Parameters'



   .. py:attribute:: BOND_MANAGEMENT
      :value: 'Bond Management'



   .. py:attribute:: INDOOR_POSITIONING
      :value: 'Indoor Positioning'



   .. py:attribute:: HUMAN_INTERFACE_DEVICE
      :value: 'Human Interface Device'



   .. py:attribute:: PULSE_OXIMETER
      :value: 'Pulse Oximeter'



   .. py:attribute:: FITNESS_MACHINE
      :value: 'Fitness Machine'



.. py:function:: get_service_class_map() -> dict[src.bluetooth_sig.types.gatt_enums.ServiceName, type[src.bluetooth_sig.gatt.services.base.BaseGattService]]

   Get the current service class map.

   :returns: Dictionary mapping ServiceName enum to service classes


.. py:class:: RunningSpeedAndCadenceService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Running Speed and Cadence Service implementation (0x1814).

   Used for running sensors that measure speed, cadence, stride length,
   and distance. Contains the RSC Measurement characteristic for
   running metrics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: ScanParametersService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Scan Parameters service implementation.

   Contains characteristics that control BLE scanning parameters:
   - Scan Interval Window - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: TxPowerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Tx Power Service implementation.

   Exposes the current transmit power level of a device.

   Contains characteristics related to transmit power:
   - Tx Power Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


.. py:class:: WeightScaleService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Weight Scale Service implementation (0x181D).

   Used for smart scale devices that measure weight and related body
   metrics. Contains Weight Measurement and Weight Scale Feature
   characteristics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


