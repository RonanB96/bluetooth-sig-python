src.bluetooth_sig.gatt.services.registry
========================================

.. py:module:: src.bluetooth_sig.gatt.services.registry

.. autoapi-nested-parse::

   Bluetooth SIG GATT service registry.

   This module contains the service registry implementation, including the
   ServiceName enum, service class mappings, and the GattServiceRegistry
   class. This was moved from __init__.py to follow Python best practices
   of keeping __init__.py files lightweight.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.registry.ServiceName
   src.bluetooth_sig.gatt.services.registry.GattServiceRegistry


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.registry.get_service_class_map


Module Contents
---------------

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



