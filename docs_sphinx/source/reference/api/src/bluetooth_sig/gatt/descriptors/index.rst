src.bluetooth_sig.gatt.descriptors
==================================

.. py:module:: src.bluetooth_sig.gatt.descriptors

.. autoapi-nested-parse::

   GATT descriptors package.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/gatt/descriptors/base/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/cccd/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/characteristic_aggregate_format/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/characteristic_extended_properties/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/characteristic_presentation_format/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/characteristic_user_description/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/complete_br_edr_transport_block_data/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/environmental_sensing_configuration/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/environmental_sensing_measurement/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/environmental_sensing_trigger_setting/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/external_report_reference/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/imd_trigger_setting/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/manufacturer_limits/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/measurement_description/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/number_of_digitals/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/observation_schedule/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/process_tolerances/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/registry/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/report_reference/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/server_characteristic_configuration/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/time_trigger_setting/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/valid_range/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/valid_range_and_accuracy/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/value_trigger_setting/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.BaseDescriptor
   src.bluetooth_sig.gatt.descriptors.CCCDData
   src.bluetooth_sig.gatt.descriptors.CCCDDescriptor
   src.bluetooth_sig.gatt.descriptors.CharacteristicAggregateFormatData
   src.bluetooth_sig.gatt.descriptors.CharacteristicAggregateFormatDescriptor
   src.bluetooth_sig.gatt.descriptors.CharacteristicExtendedPropertiesData
   src.bluetooth_sig.gatt.descriptors.CharacteristicExtendedPropertiesDescriptor
   src.bluetooth_sig.gatt.descriptors.CharacteristicPresentationFormatData
   src.bluetooth_sig.gatt.descriptors.CharacteristicPresentationFormatDescriptor
   src.bluetooth_sig.gatt.descriptors.CharacteristicUserDescriptionData
   src.bluetooth_sig.gatt.descriptors.CharacteristicUserDescriptionDescriptor
   src.bluetooth_sig.gatt.descriptors.CompleteBREDRTransportBlockDataData
   src.bluetooth_sig.gatt.descriptors.CompleteBREDRTransportBlockDataDescriptor
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingConfigurationData
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingConfigurationDescriptor
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingMeasurementData
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingMeasurementDescriptor
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.EnvironmentalSensingTriggerSettingDescriptor
   src.bluetooth_sig.gatt.descriptors.ExternalReportReferenceData
   src.bluetooth_sig.gatt.descriptors.ExternalReportReferenceDescriptor
   src.bluetooth_sig.gatt.descriptors.IMDTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.IMDTriggerSettingDescriptor
   src.bluetooth_sig.gatt.descriptors.ManufacturerLimitsData
   src.bluetooth_sig.gatt.descriptors.ManufacturerLimitsDescriptor
   src.bluetooth_sig.gatt.descriptors.MeasurementDescriptionData
   src.bluetooth_sig.gatt.descriptors.MeasurementDescriptionDescriptor
   src.bluetooth_sig.gatt.descriptors.NumberOfDigitalsData
   src.bluetooth_sig.gatt.descriptors.NumberOfDigitalsDescriptor
   src.bluetooth_sig.gatt.descriptors.ObservationScheduleData
   src.bluetooth_sig.gatt.descriptors.ObservationScheduleDescriptor
   src.bluetooth_sig.gatt.descriptors.ProcessTolerancesData
   src.bluetooth_sig.gatt.descriptors.ProcessTolerancesDescriptor
   src.bluetooth_sig.gatt.descriptors.DescriptorRegistry
   src.bluetooth_sig.gatt.descriptors.ReportReferenceData
   src.bluetooth_sig.gatt.descriptors.ReportReferenceDescriptor
   src.bluetooth_sig.gatt.descriptors.SCCDData
   src.bluetooth_sig.gatt.descriptors.ServerCharacteristicConfigurationDescriptor
   src.bluetooth_sig.gatt.descriptors.TimeTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.TimeTriggerSettingDescriptor
   src.bluetooth_sig.gatt.descriptors.ValidRangeData
   src.bluetooth_sig.gatt.descriptors.ValidRangeDescriptor
   src.bluetooth_sig.gatt.descriptors.ValidRangeAndAccuracyData
   src.bluetooth_sig.gatt.descriptors.ValidRangeAndAccuracyDescriptor
   src.bluetooth_sig.gatt.descriptors.ValueTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.ValueTriggerSettingDescriptor


Package Contents
----------------

.. py:class:: BaseDescriptor

   Bases: :py:obj:`abc.ABC`


   Base class for all GATT descriptors.

   Automatically resolves UUID and name from Bluetooth SIG registry.
   Provides parsing capabilities for descriptor values.

   .. attribute:: _descriptor_name

      Optional explicit descriptor name for registry lookup.

   .. attribute:: _writable

      Whether this descriptor type supports write operations.
      Override to True in writable descriptor subclasses (CCCD, SCCD).

   .. note::

      Most descriptors are read-only per Bluetooth SIG specification.
      Some like CCCD (0x2902) and SCCD (0x2903) support writes.


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the descriptor UUID.


   .. py:property:: name
      :type: str


      Get the descriptor name.


   .. py:property:: info
      :type: src.bluetooth_sig.types.DescriptorInfo


      Get the descriptor information.


   .. py:method:: parse_value(data: bytes) -> src.bluetooth_sig.types.DescriptorData

      Parse raw descriptor data into structured format.

      :param data: Raw bytes from the descriptor read

      :returns: DescriptorData object with parsed value and metadata



   .. py:method:: is_writable() -> bool

      Check if descriptor type supports write operations.

      :returns: True if descriptor type supports writes, False otherwise.

      .. note::

         Only checks descriptor type, not runtime permissions or security.
         Example writable descriptors (CCCD, SCCD) override `_writable = True`.



.. py:class:: CCCDData

   Bases: :py:obj:`msgspec.Struct`


   CCCD (Client Characteristic Configuration Descriptor) data.


   .. py:attribute:: notifications_enabled
      :type:  bool


   .. py:attribute:: indications_enabled
      :type:  bool


.. py:class:: CCCDDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Client Characteristic Configuration Descriptor (0x2902).

   Controls notification and indication settings for a characteristic.
   Critical for enabling BLE notifications and indications.


   .. py:method:: create_enable_notifications_value() -> bytes
      :staticmethod:


      Create value to enable notifications.



   .. py:method:: create_enable_indications_value() -> bytes
      :staticmethod:


      Create value to enable indications.



   .. py:method:: create_enable_both_value() -> bytes
      :staticmethod:


      Create value to enable both notifications and indications.



   .. py:method:: create_disable_value() -> bytes
      :staticmethod:


      Create value to disable notifications/indications.



   .. py:method:: is_notifications_enabled(data: bytes) -> bool

      Check if notifications are enabled.



   .. py:method:: is_indications_enabled(data: bytes) -> bool

      Check if indications are enabled.



   .. py:method:: is_any_enabled(data: bytes) -> bool

      Check if either notifications or indications are enabled.



.. py:class:: CharacteristicAggregateFormatData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Aggregate Format descriptor data.


   .. py:attribute:: attribute_handles
      :type:  list[int]


.. py:class:: CharacteristicAggregateFormatDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Aggregate Format Descriptor (0x2905).

   Contains a list of attribute handles that collectively form an aggregate value.
   Used to group multiple characteristics into a single logical value.


   .. py:method:: get_attribute_handles(data: bytes) -> list[int]

      Get the list of attribute handles.



   .. py:method:: get_handle_count(data: bytes) -> int

      Get the number of attribute handles.



.. py:class:: CharacteristicExtendedPropertiesData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Extended Properties descriptor data.


   .. py:attribute:: reliable_write
      :type:  bool


   .. py:attribute:: writable_auxiliaries
      :type:  bool


.. py:class:: CharacteristicExtendedPropertiesDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Extended Properties Descriptor (0x2900).

   Defines extended properties for a characteristic using bit flags.
   Indicates support for reliable writes and writable auxiliaries.


   .. py:method:: supports_reliable_write(data: bytes) -> bool

      Check if reliable write is supported.



   .. py:method:: supports_writable_auxiliaries(data: bytes) -> bool

      Check if writable auxiliaries are supported.



.. py:class:: CharacteristicPresentationFormatData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Presentation Format descriptor data.


   .. py:attribute:: format
      :type:  int


   .. py:attribute:: exponent
      :type:  int


   .. py:attribute:: unit
      :type:  int


   .. py:attribute:: namespace
      :type:  int


   .. py:attribute:: description
      :type:  int


.. py:class:: CharacteristicPresentationFormatDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Presentation Format Descriptor (0x2904).

   Describes how characteristic values should be presented to users.
   Contains format, exponent, unit, namespace, and description information.


   .. py:method:: get_format_type(data: bytes) -> int

      Get the format type.



   .. py:method:: get_exponent(data: bytes) -> int

      Get the exponent for scaling.



   .. py:method:: get_unit(data: bytes) -> int

      Get the unit identifier.



   .. py:method:: get_namespace(data: bytes) -> int

      Get the namespace identifier.



   .. py:method:: get_description(data: bytes) -> int

      Get the description identifier.



.. py:class:: CharacteristicUserDescriptionData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic User Description descriptor data.


   .. py:attribute:: description
      :type:  str


.. py:class:: CharacteristicUserDescriptionDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic User Description Descriptor (0x2901).

   Contains a user-readable description of the characteristic.
   UTF-8 encoded string describing the characteristic's purpose.


   .. py:method:: get_description(data: bytes) -> str

      Get the user description string.



.. py:class:: CompleteBREDRTransportBlockDataData

   Bases: :py:obj:`msgspec.Struct`


   Complete BR-EDR Transport Block Data descriptor data.


   .. py:attribute:: transport_data
      :type:  bytes


.. py:class:: CompleteBREDRTransportBlockDataDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Complete BR-EDR Transport Block Data Descriptor (0x290F).

   Contains complete BR-EDR transport block data.
   Used for transporting large data blocks over BR-EDR.


   .. py:method:: get_transport_data(data: bytes) -> bytes

      Get the transport block data.



.. py:class:: EnvironmentalSensingConfigurationData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Configuration descriptor data.


   .. py:attribute:: trigger_logic_value
      :type:  bool


   .. py:attribute:: transmission_interval_present
      :type:  bool


   .. py:attribute:: measurement_period_present
      :type:  bool


   .. py:attribute:: update_interval_present
      :type:  bool


   .. py:attribute:: application_present
      :type:  bool


   .. py:attribute:: measurement_uncertainty_present
      :type:  bool


.. py:class:: EnvironmentalSensingConfigurationDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Configuration Descriptor (0x290B).

   Configures environmental sensing measurement parameters.
   Contains various configuration flags for sensor behaviour.


   .. py:method:: has_trigger_logic_value(data: bytes) -> bool

      Check if trigger logic value is present.



   .. py:method:: has_transmission_interval(data: bytes) -> bool

      Check if transmission interval is present.



   .. py:method:: has_measurement_period(data: bytes) -> bool

      Check if measurement period is present.



.. py:class:: EnvironmentalSensingMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Measurement descriptor data.


   .. py:attribute:: sampling_function
      :type:  int


   .. py:attribute:: measurement_period
      :type:  int


   .. py:attribute:: update_interval
      :type:  int


   .. py:attribute:: application
      :type:  int


   .. py:attribute:: measurement_uncertainty
      :type:  int


.. py:class:: EnvironmentalSensingMeasurementDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Measurement Descriptor (0x290C).

   Contains measurement parameters for environmental sensors.
   Includes sampling function, measurement period, and other parameters.


   .. py:method:: get_sampling_function(data: bytes) -> int

      Get the sampling function.



   .. py:method:: get_measurement_period(data: bytes) -> int

      Get the measurement period.



   .. py:method:: get_update_interval(data: bytes) -> int

      Get the update interval.



   .. py:method:: get_application(data: bytes) -> int

      Get the application identifier.



   .. py:method:: get_measurement_uncertainty(data: bytes) -> int

      Get the measurement uncertainty.



.. py:class:: EnvironmentalSensingTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Trigger Setting descriptor data.


   .. py:attribute:: condition
      :type:  int


   .. py:attribute:: operand
      :type:  int


.. py:class:: EnvironmentalSensingTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Trigger Setting Descriptor (0x290D).

   Defines trigger conditions for environmental sensing measurements.
   Contains condition and operand for triggering measurements.


   .. py:method:: get_condition(data: bytes) -> int

      Get the trigger condition.



   .. py:method:: get_operand(data: bytes) -> int

      Get the trigger operand.



.. py:class:: ExternalReportReferenceData

   Bases: :py:obj:`msgspec.Struct`


   External Report Reference descriptor data.


   .. py:attribute:: external_report_id
      :type:  int


.. py:class:: ExternalReportReferenceDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   External Report Reference Descriptor (0x2907).

   References an external report by ID.
   Used in HID (Human Interface Device) profiles.


   .. py:method:: get_external_report_id(data: bytes) -> int

      Get the external report ID.



.. py:class:: IMDTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   IMD Trigger Setting descriptor data.


   .. py:attribute:: trigger_setting
      :type:  int


.. py:class:: IMDTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   IMD Trigger Setting Descriptor (0x2915).

   Defines trigger settings for Impedance Measurement Devices (IMD).
   Contains trigger configuration for IMD measurements.


   .. py:method:: get_trigger_setting(data: bytes) -> int

      Get the IMD trigger setting.



.. py:class:: ManufacturerLimitsData

   Bases: :py:obj:`msgspec.Struct`


   Manufacturer Limits descriptor data.


   .. py:attribute:: min_limit
      :type:  int | float


   .. py:attribute:: max_limit
      :type:  int | float


.. py:class:: ManufacturerLimitsDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Manufacturer Limits Descriptor (0x2913).

   Defines manufacturer-specified limits for characteristic values.
   Contains minimum and maximum limits set by the manufacturer.


   .. py:method:: get_min_limit(data: bytes) -> int | float

      Get the minimum manufacturer limit.



   .. py:method:: get_max_limit(data: bytes) -> int | float

      Get the maximum manufacturer limit.



   .. py:method:: is_value_within_limits(data: bytes, value: int | float) -> bool

      Check if a value is within manufacturer limits.



.. py:class:: MeasurementDescriptionData

   Bases: :py:obj:`msgspec.Struct`


   Measurement Description descriptor data.


   .. py:attribute:: description
      :type:  str


.. py:class:: MeasurementDescriptionDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Measurement Description Descriptor (0x2912).

   Contains a human-readable description of the measurement.
   UTF-8 encoded string describing what the measurement represents.


   .. py:method:: get_description(data: bytes) -> str

      Get the measurement description string.



.. py:class:: NumberOfDigitalsData

   Bases: :py:obj:`msgspec.Struct`


   Number of Digitals descriptor data.


   .. py:attribute:: number_of_digitals
      :type:  int


.. py:class:: NumberOfDigitalsDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Number of Digitals Descriptor (0x2909).

   Specifies the number of digital states supported by a characteristic.
   Used in sensor applications.


   .. py:method:: get_number_of_digitals(data: bytes) -> int

      Get the number of digitals.



.. py:class:: ObservationScheduleData

   Bases: :py:obj:`msgspec.Struct`


   Observation Schedule descriptor data.


   .. py:attribute:: schedule
      :type:  bytes


.. py:class:: ObservationScheduleDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Observation Schedule Descriptor (0x2910).

   Defines the observation schedule for sensor measurements.
   Format varies depending on the sensor type and requirements.


   .. py:method:: get_schedule_data(data: bytes) -> bytes

      Get the raw schedule data.



.. py:class:: ProcessTolerancesData

   Bases: :py:obj:`msgspec.Struct`


   Process Tolerances descriptor data.


   .. py:attribute:: tolerance_min
      :type:  int | float


   .. py:attribute:: tolerance_max
      :type:  int | float


.. py:class:: ProcessTolerancesDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Process Tolerances Descriptor (0x2914).

   Defines process tolerances for characteristic values.
   Contains minimum and maximum tolerance values.


   .. py:method:: get_tolerance_min(data: bytes) -> int | float

      Get the minimum process tolerance.



   .. py:method:: get_tolerance_max(data: bytes) -> int | float

      Get the maximum process tolerance.



.. py:class:: DescriptorRegistry

   Registry for descriptor classes.


   .. py:method:: register(descriptor_class: type[src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor]) -> None
      :classmethod:


      Register a descriptor class.



   .. py:method:: get_descriptor_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor] | None
      :classmethod:


      Get descriptor class for UUID.

      :param uuid: The descriptor UUID

      :returns: Descriptor class if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: create_descriptor(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor | None
      :classmethod:


      Create descriptor instance for UUID.

      :param uuid: The descriptor UUID

      :returns: Descriptor instance if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: list_registered_descriptors() -> list[str]
      :classmethod:


      List all registered descriptor UUIDs.



.. py:class:: ReportReferenceData

   Bases: :py:obj:`msgspec.Struct`


   Report Reference descriptor data.


   .. py:attribute:: report_id
      :type:  int


   .. py:attribute:: report_type
      :type:  int


.. py:class:: ReportReferenceDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Report Reference Descriptor (0x2908).

   Contains report ID and report type information.
   Used in HID (Human Interface Device) profiles.


   .. py:method:: get_report_id(data: bytes) -> int

      Get the report ID.



   .. py:method:: get_report_type(data: bytes) -> int

      Get the report type.



   .. py:method:: is_input_report(data: bytes) -> bool

      Check if this is an input report.



   .. py:method:: is_output_report(data: bytes) -> bool

      Check if this is an output report.



   .. py:method:: is_feature_report(data: bytes) -> bool

      Check if this is a feature report.



.. py:class:: SCCDData

   Bases: :py:obj:`msgspec.Struct`


   SCCD (Server Characteristic Configuration Descriptor) data.


   .. py:attribute:: broadcasts_enabled
      :type:  bool


.. py:class:: ServerCharacteristicConfigurationDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Server Characteristic Configuration Descriptor (0x2903).

   Controls server-side configuration for a characteristic.
   Currently only supports broadcast enable/disable.


   .. py:method:: create_enable_broadcasts_value() -> bytes
      :staticmethod:


      Create value to enable broadcasts.



   .. py:method:: create_disable_broadcasts_value() -> bytes
      :staticmethod:


      Create value to disable broadcasts.



   .. py:method:: is_broadcasts_enabled(data: bytes) -> bool

      Check if broadcasts are enabled.



.. py:class:: TimeTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Time Trigger Setting descriptor data.


   .. py:attribute:: time_interval
      :type:  int


.. py:class:: TimeTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Time Trigger Setting Descriptor (0x290E).

   Defines time-based trigger settings for measurements.
   Contains time interval in seconds for periodic triggering.


   .. py:method:: get_time_interval(data: bytes) -> int

      Get the time interval in seconds.



.. py:class:: ValidRangeData

   Bases: :py:obj:`msgspec.Struct`


   Valid Range descriptor data.


   .. py:attribute:: min_value
      :type:  int | float


   .. py:attribute:: max_value
      :type:  int | float


.. py:class:: ValidRangeDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`, :py:obj:`src.bluetooth_sig.gatt.descriptors.base.RangeDescriptorMixin`


   Valid Range Descriptor (0x2906).

   Defines the valid range for characteristic values.
   Contains minimum and maximum values for validation.


.. py:class:: ValidRangeAndAccuracyData

   Bases: :py:obj:`msgspec.Struct`


   Valid Range and Accuracy descriptor data.


   .. py:attribute:: min_value
      :type:  int | float


   .. py:attribute:: max_value
      :type:  int | float


   .. py:attribute:: accuracy
      :type:  int | float


.. py:class:: ValidRangeAndAccuracyDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`, :py:obj:`src.bluetooth_sig.gatt.descriptors.base.RangeDescriptorMixin`


   Valid Range and Accuracy Descriptor (0x2911).

   Defines the valid range and accuracy for characteristic values.
   Contains minimum value, maximum value, and accuracy information.


   .. py:method:: get_accuracy(data: bytes) -> int | float

      Get the accuracy value.

      :param data: Raw descriptor data

      :returns: Accuracy value for the characteristic



.. py:class:: ValueTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Value Trigger Setting descriptor data.


   .. py:attribute:: condition
      :type:  int


   .. py:attribute:: value
      :type:  int


.. py:class:: ValueTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Value Trigger Setting Descriptor (0x290A).

   Defines trigger conditions for value-based notifications.
   Contains condition and reference value for triggering.


   .. py:method:: get_condition(data: bytes) -> int

      Get the trigger condition.



   .. py:method:: get_trigger_value(data: bytes) -> int

      Get the trigger reference value.



   .. py:method:: is_condition_equal_to(data: bytes) -> bool

      Check if condition is 'equal to'.



   .. py:method:: is_condition_greater_than(data: bytes) -> bool

      Check if condition is 'greater than'.



