src.bluetooth_sig.gatt.services.base
====================================

.. py:module:: src.bluetooth_sig.gatt.services.base

.. autoapi-nested-parse::

   Base class for GATT service implementations.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.base.GattCharacteristic
   src.bluetooth_sig.gatt.services.base.ServiceCharacteristicCollection
   src.bluetooth_sig.gatt.services.base.ServiceCharacteristics


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.base.BaseGattService
   src.bluetooth_sig.gatt.services.base.CharacteristicStatus
   src.bluetooth_sig.gatt.services.base.SIGServiceResolver
   src.bluetooth_sig.gatt.services.base.ServiceCharacteristicInfo
   src.bluetooth_sig.gatt.services.base.ServiceCompletenessReport
   src.bluetooth_sig.gatt.services.base.ServiceHealthStatus
   src.bluetooth_sig.gatt.services.base.ServiceValidationConfig
   src.bluetooth_sig.gatt.services.base.ServiceValidationResult


Module Contents
---------------

.. py:class:: BaseGattService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Base class for all GATT services.

   Automatically resolves UUID, name, and summary from Bluetooth SIG specifications.
   Follows the same pattern as BaseCharacteristic for consistency.

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:method:: get_characteristic(uuid: src.bluetooth_sig.types.uuid.BluetoothUUID) -> GattCharacteristic | None

      Get a characteristic by UUID.



   .. py:method:: get_characteristic_status(characteristic_name: src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName) -> ServiceCharacteristicInfo | None

      Get detailed status of a specific characteristic.

      :param characteristic_name: CharacteristicName enum

      :returns: CharacteristicInfo if characteristic is expected by this service, None otherwise



   .. py:method:: get_characteristics_schema() -> type | None
      :classmethod:


      Get the TypedDict schema for this service's characteristics.

      Override this method to provide strong typing for characteristics.
      If not implemented, falls back to get_expected_characteristics().

      :returns: TypedDict class defining the service's characteristics, or None



   .. py:method:: get_class_uuid() -> src.bluetooth_sig.types.uuid.BluetoothUUID
      :classmethod:


      Get the UUID for this service class without instantiation.

      :returns: BluetoothUUID for this service class

      :raises UUIDResolutionError: If UUID cannot be resolved



   .. py:method:: get_conditional_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get characteristics that are required only under certain conditions.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

      Override in subclasses to specify conditional characteristics.




   .. py:method:: get_expected_characteristic_uuids() -> set[src.bluetooth_sig.types.uuid.BluetoothUUID]

      Get the set of expected characteristic UUIDs for this service.



   .. py:method:: get_expected_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the expected characteristics for this service from the service_characteristics dict.

      Looks for a 'service_characteristics' class attribute containing a dictionary of
          CharacteristicName -> required flag, and automatically builds CharacteristicSpec objects.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_missing_characteristics() -> dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, ServiceCharacteristicInfo]

      Get detailed information about missing characteristics.

      :returns: Dict mapping characteristic name to ServiceCharacteristicInfo



   .. py:method:: get_name() -> str
      :classmethod:


      Get the service name for this class without creating an instance.

      :returns: The service name as registered in the UUID registry.



   .. py:method:: get_optional_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the optional characteristics for this service by name and class.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_required_characteristic_keys() -> set[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName]
      :classmethod:


      Get the set of required characteristic keys from the schema.

      Override this method when using strongly-typed characteristics.
      If not implemented, falls back to get_required_characteristics().keys().

      :returns: Set of required characteristic field names



   .. py:method:: get_required_characteristic_uuids() -> set[src.bluetooth_sig.types.uuid.BluetoothUUID]

      Get the set of required characteristic UUIDs for this service.



   .. py:method:: get_required_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the required characteristics for this service from the characteristics dict.

      Automatically filters the characteristics dictionary for required=True entries.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_service_completeness_report() -> ServiceCompletenessReport

      Get a comprehensive report about service completeness.

      :returns: ServiceCompletenessReport with detailed service status information



   .. py:method:: has_minimum_functionality() -> bool

      Check if service has minimum required functionality.

      :returns: True if service has all required characteristics and is usable



   .. py:method:: matches_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> bool
      :classmethod:


      Check if this service matches the given UUID.



   .. py:method:: process_characteristics(characteristics: src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData) -> None

      Process the characteristics for this service (default implementation).

      :param characteristics: Dict mapping UUID to characteristic info



   .. py:method:: validate_bluetooth_sig_compliance() -> list[str]
      :classmethod:


      Validate compliance with Bluetooth SIG service specification.

      :returns: List of compliance issues found

      Override in subclasses to provide service-specific validation.




   .. py:method:: validate_service(strict: bool = False) -> ServiceValidationResult

      Validate the completeness and health of this service.

      :param strict: If True, missing optional characteristics are treated as warnings

      :returns: ServiceValidationResult with detailed status information



   .. py:attribute:: characteristics
      :type:  dict[src.bluetooth_sig.types.uuid.BluetoothUUID, src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:property:: info
      :type: src.bluetooth_sig.types.ServiceInfo


      Return the resolved service information for this instance.

      The info property provides all metadata about the service, including UUID, name, and description.


   .. py:property:: name
      :type: str


      Get the service name from _info.


   .. py:property:: supported_characteristics
      :type: set[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


      Get the set of characteristic UUIDs supported by this service.


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the service UUID from _info.


.. py:class:: CharacteristicStatus(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Status of characteristics within a service.


   .. py:attribute:: INVALID
      :value: 'invalid'



   .. py:attribute:: MISSING
      :value: 'missing'



   .. py:attribute:: PRESENT
      :value: 'present'



.. py:class:: SIGServiceResolver

   Resolves SIG service information from registry.

   This class handles all SIG service resolution logic, separating
   concerns from the BaseGattService constructor. Uses shared utilities
   from the resolver module to avoid code duplication with characteristic resolution.


   .. py:method:: resolve_for_class(service_class: type[BaseGattService]) -> src.bluetooth_sig.types.ServiceInfo
      :staticmethod:


      Resolve ServiceInfo for a SIG service class.

      :param service_class: The service class to resolve info for

      :returns: ServiceInfo with resolved UUID, name, summary

      :raises UUIDResolutionError: If no UUID can be resolved for the class



   .. py:method:: resolve_from_registry(service_class: type[BaseGattService]) -> src.bluetooth_sig.types.ServiceInfo | None
      :staticmethod:


      Resolve service info from registry using shared search strategy.



.. py:class:: ServiceCharacteristicInfo

   Bases: :py:obj:`src.bluetooth_sig.types.CharacteristicInfo`


   Service-specific information about a characteristic with context about its presence.

   Provides status, requirement, and class context for a characteristic within a service.


   .. py:attribute:: char_class
      :type:  type[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic] | None
      :value: None



   .. py:attribute:: condition_description
      :type:  str
      :value: ''



   .. py:attribute:: is_conditional
      :type:  bool
      :value: False



   .. py:attribute:: is_required
      :type:  bool
      :value: False



   .. py:attribute:: status
      :type:  CharacteristicStatus


.. py:class:: ServiceCompletenessReport

   Bases: :py:obj:`msgspec.Struct`


   Comprehensive report about service completeness and health.


   .. py:attribute:: characteristics_expected
      :type:  int


   .. py:attribute:: characteristics_present
      :type:  int


   .. py:attribute:: characteristics_required
      :type:  int


   .. py:attribute:: errors
      :type:  list[str]


   .. py:attribute:: health_status
      :type:  ServiceHealthStatus


   .. py:attribute:: invalid_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: is_healthy
      :type:  bool


   .. py:attribute:: missing_details
      :type:  dict[str, ServiceCharacteristicInfo]


   .. py:attribute:: missing_optional
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: missing_required
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: present_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: service_name
      :type:  str


   .. py:attribute:: service_uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: warnings
      :type:  list[str]


.. py:class:: ServiceHealthStatus(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Health status of a GATT service.


   .. py:attribute:: COMPLETE
      :value: 'complete'



   .. py:attribute:: FUNCTIONAL
      :value: 'functional'



   .. py:attribute:: INCOMPLETE
      :value: 'incomplete'



   .. py:attribute:: PARTIAL
      :value: 'partial'



.. py:class:: ServiceValidationConfig

   Bases: :py:obj:`msgspec.Struct`


   Configuration for service validation constraints.

   Groups validation parameters into a single, optional configuration object
   to simplify BaseGattService constructor signatures.


   .. py:attribute:: require_all_optional
      :type:  bool
      :value: False



   .. py:attribute:: strict_validation
      :type:  bool
      :value: False



.. py:class:: ServiceValidationResult

   Bases: :py:obj:`msgspec.Struct`


   Result of service validation.


   .. py:attribute:: errors
      :type:  list[str]


   .. py:property:: has_errors
      :type: bool


      Check if service has any errors.


   .. py:attribute:: invalid_characteristics
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:property:: is_healthy
      :type: bool


      Check if service is in a healthy state.


   .. py:attribute:: missing_optional
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: missing_required
      :type:  list[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:attribute:: status
      :type:  ServiceHealthStatus


   .. py:attribute:: warnings
      :type:  list[str]


.. py:data:: GattCharacteristic

.. py:data:: ServiceCharacteristicCollection

.. py:data:: ServiceCharacteristics

