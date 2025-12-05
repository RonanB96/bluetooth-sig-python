src.bluetooth_sig.types
=======================

.. py:module:: src.bluetooth_sig.types

.. autoapi-nested-parse::

   Data types for Bluetooth SIG standards.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/types/ad_types_constants/index
   /reference/api/src/bluetooth_sig/types/advertising/index
   /reference/api/src/bluetooth_sig/types/alert/index
   /reference/api/src/bluetooth_sig/types/appearance/index
   /reference/api/src/bluetooth_sig/types/base_types/index
   /reference/api/src/bluetooth_sig/types/battery/index
   /reference/api/src/bluetooth_sig/types/context/index
   /reference/api/src/bluetooth_sig/types/data_types/index
   /reference/api/src/bluetooth_sig/types/device_types/index
   /reference/api/src/bluetooth_sig/types/gatt_enums/index
   /reference/api/src/bluetooth_sig/types/gatt_services/index
   /reference/api/src/bluetooth_sig/types/io/index
   /reference/api/src/bluetooth_sig/types/location/index
   /reference/api/src/bluetooth_sig/types/protocols/index
   /reference/api/src/bluetooth_sig/types/registry/index
   /reference/api/src/bluetooth_sig/types/scan_interval_window/index
   /reference/api/src/bluetooth_sig/types/units/index
   /reference/api/src/bluetooth_sig/types/uuid/index


Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.types.ALERT_CATEGORY_DEFINED_MAX
   src.bluetooth_sig.types.ALERT_CATEGORY_RESERVED_MAX
   src.bluetooth_sig.types.ALERT_CATEGORY_RESERVED_MIN
   src.bluetooth_sig.types.ALERT_CATEGORY_SERVICE_SPECIFIC_MIN
   src.bluetooth_sig.types.ALERT_COMMAND_MAX
   src.bluetooth_sig.types.ALERT_TEXT_MAX_LENGTH
   src.bluetooth_sig.types.UNREAD_COUNT_MAX
   src.bluetooth_sig.types.UNREAD_COUNT_MORE_THAN_MAX


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.ADTypeInfo
   src.bluetooth_sig.types.AdvertisingData
   src.bluetooth_sig.types.AdvertisingDataStructures
   src.bluetooth_sig.types.BLEAdvertisingFlags
   src.bluetooth_sig.types.BLEAdvertisingPDU
   src.bluetooth_sig.types.BLEExtendedHeader
   src.bluetooth_sig.types.ConnectionData
   src.bluetooth_sig.types.CoreAdvertisingData
   src.bluetooth_sig.types.DeviceProperties
   src.bluetooth_sig.types.ExtendedAdvertisingData
   src.bluetooth_sig.types.ExtendedHeaderFlags
   src.bluetooth_sig.types.LocationAndSensingData
   src.bluetooth_sig.types.MeshAndBroadcastData
   src.bluetooth_sig.types.PDUHeaderFlags
   src.bluetooth_sig.types.PDULayout
   src.bluetooth_sig.types.PDUType
   src.bluetooth_sig.types.SecurityData
   src.bluetooth_sig.types.AlertCategoryBitMask
   src.bluetooth_sig.types.AlertCategoryID
   src.bluetooth_sig.types.AlertNotificationCommandID
   src.bluetooth_sig.types.AppearanceData
   src.bluetooth_sig.types.SIGInfo
   src.bluetooth_sig.types.BatteryChargeLevel
   src.bluetooth_sig.types.BatteryChargeState
   src.bluetooth_sig.types.BatteryChargingType
   src.bluetooth_sig.types.BatteryFaultReason
   src.bluetooth_sig.types.CharacteristicContext
   src.bluetooth_sig.types.DeviceInfo
   src.bluetooth_sig.types.CharacteristicInfo
   src.bluetooth_sig.types.DateData
   src.bluetooth_sig.types.ParseFieldError
   src.bluetooth_sig.types.ServiceInfo
   src.bluetooth_sig.types.ValidationResult
   src.bluetooth_sig.types.PositionStatus
   src.bluetooth_sig.types.CharacteristicDataProtocol
   src.bluetooth_sig.types.AppearanceInfo
   src.bluetooth_sig.types.ClassOfDeviceInfo
   src.bluetooth_sig.types.DescriptorData
   src.bluetooth_sig.types.DescriptorInfo
   src.bluetooth_sig.types.AngleUnit
   src.bluetooth_sig.types.ConcentrationUnit
   src.bluetooth_sig.types.ElectricalUnit
   src.bluetooth_sig.types.GlucoseConcentrationUnit
   src.bluetooth_sig.types.HeightUnit
   src.bluetooth_sig.types.LengthUnit
   src.bluetooth_sig.types.MeasurementSystem
   src.bluetooth_sig.types.PercentageUnit
   src.bluetooth_sig.types.PhysicalUnit
   src.bluetooth_sig.types.PressureUnit
   src.bluetooth_sig.types.SoundUnit
   src.bluetooth_sig.types.TemperatureUnit
   src.bluetooth_sig.types.WeightUnit


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.validate_category_id


Package Contents
----------------

.. py:class:: ADTypeInfo

   Bases: :py:obj:`msgspec.Struct`


   AD Type information from Bluetooth SIG assigned numbers.

   .. attribute:: value

      The AD type value (e.g., 0x01 for Flags)

   .. attribute:: name

      Human-readable name from the specification

   .. attribute:: reference

      Optional specification reference


   .. py:attribute:: value
      :type:  int


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: reference
      :type:  str


.. py:class:: AdvertisingData

   Bases: :py:obj:`msgspec.Struct`


   Complete BLE advertising data with device information and metadata.

   .. attribute:: raw_data

      Raw bytes from the advertising packet

   .. attribute:: ad_structures

      Parsed AD structures organized by category

   .. attribute:: extended

      Extended advertising data (BLE 5.0+)

   .. attribute:: rssi

      Received signal strength indicator in dBm


   .. py:attribute:: raw_data
      :type:  bytes


   .. py:attribute:: ad_structures
      :type:  AdvertisingDataStructures


   .. py:attribute:: extended
      :type:  ExtendedAdvertisingData


   .. py:attribute:: rssi
      :type:  int | None
      :value: None



   .. py:property:: is_extended_advertising
      :type: bool


      Check if this advertisement uses extended advertising.


   .. py:property:: total_payload_size
      :type: int


      Get total payload size including extended data.


.. py:class:: AdvertisingDataStructures

   Bases: :py:obj:`msgspec.Struct`


   Complete parsed advertising data structures organized by category.

   .. attribute:: core

      Core device identification and service information

   .. attribute:: properties

      Device capabilities and appearance

   .. attribute:: connection

      Connection and pairing related data

   .. attribute:: location

      Location and sensing data

   .. attribute:: mesh

      Mesh and broadcast audio data

   .. attribute:: security

      Security and encryption data


   .. py:attribute:: core
      :type:  CoreAdvertisingData


   .. py:attribute:: properties
      :type:  DeviceProperties


   .. py:attribute:: connection
      :type:  ConnectionData


   .. py:attribute:: location
      :type:  LocationAndSensingData


   .. py:attribute:: mesh
      :type:  MeshAndBroadcastData


   .. py:attribute:: security
      :type:  SecurityData


.. py:class:: BLEAdvertisingFlags

   Bases: :py:obj:`enum.IntFlag`


   BLE Advertising Flags (Core Spec Supplement, Part A, Section 1.3).

   These flags indicate the discoverable mode and capabilities of the advertising device.


   .. py:attribute:: LE_LIMITED_DISCOVERABLE_MODE
      :value: 1



   .. py:attribute:: LE_GENERAL_DISCOVERABLE_MODE
      :value: 2



   .. py:attribute:: BR_EDR_NOT_SUPPORTED
      :value: 4



   .. py:attribute:: SIMULTANEOUS_LE_BR_EDR_CONTROLLER
      :value: 8



   .. py:attribute:: SIMULTANEOUS_LE_BR_EDR_HOST
      :value: 16



   .. py:attribute:: RESERVED_BIT_5
      :value: 32



   .. py:attribute:: RESERVED_BIT_6
      :value: 64



   .. py:attribute:: RESERVED_BIT_7
      :value: 128



.. py:class:: BLEAdvertisingPDU

   Bases: :py:obj:`msgspec.Struct`


   BLE Advertising PDU structure.


   .. py:attribute:: pdu_type
      :type:  PDUType


   .. py:attribute:: tx_add
      :type:  bool


   .. py:attribute:: rx_add
      :type:  bool


   .. py:attribute:: length
      :type:  int


   .. py:attribute:: advertiser_address
      :type:  bytes
      :value: b''



   .. py:attribute:: target_address
      :type:  bytes
      :value: b''



   .. py:attribute:: payload
      :type:  bytes
      :value: b''



   .. py:attribute:: extended_header
      :type:  BLEExtendedHeader | None
      :value: None



   .. py:property:: is_extended_advertising
      :type: bool


      Check if this is an extended advertising PDU.


   .. py:property:: is_legacy_advertising
      :type: bool


      Check if this is a legacy advertising PDU.


   .. py:property:: pdu_name
      :type: str


      Get human-readable PDU type name.


.. py:class:: BLEExtendedHeader

   Bases: :py:obj:`msgspec.Struct`


   Extended Advertising Header fields (BLE 5.0+).


   .. py:attribute:: extended_header_length
      :type:  int
      :value: 0



   .. py:attribute:: adv_mode
      :type:  int
      :value: 0



   .. py:attribute:: extended_advertiser_address
      :type:  bytes
      :value: b''



   .. py:attribute:: extended_target_address
      :type:  bytes
      :value: b''



   .. py:attribute:: cte_info
      :type:  bytes
      :value: b''



   .. py:attribute:: advertising_data_info
      :type:  bytes
      :value: b''



   .. py:attribute:: auxiliary_pointer
      :type:  bytes
      :value: b''



   .. py:attribute:: sync_info
      :type:  bytes
      :value: b''



   .. py:attribute:: tx_power
      :type:  int | None
      :value: None



   .. py:attribute:: additional_controller_advertising_data
      :type:  bytes
      :value: b''



   .. py:property:: has_extended_advertiser_address
      :type: bool


      Check if extended advertiser address is present.


   .. py:property:: has_extended_target_address
      :type: bool


      Check if extended target address is present.


   .. py:property:: has_cte_info
      :type: bool


      Check if CTE info is present.


   .. py:property:: has_advertising_data_info
      :type: bool


      Check if advertising data info is present.


   .. py:property:: has_auxiliary_pointer
      :type: bool


      Check if auxiliary pointer is present.


   .. py:property:: has_sync_info
      :type: bool


      Check if sync info is present.


   .. py:property:: has_tx_power
      :type: bool


      Check if TX power is present.


   .. py:property:: has_additional_controller_data
      :type: bool


      Check if additional controller advertising data is present.


.. py:class:: ConnectionData

   Bases: :py:obj:`msgspec.Struct`


   Connection and pairing related advertising data.

   .. attribute:: public_target_address

      List of public device addresses

   .. attribute:: random_target_address

      List of random device addresses

   .. attribute:: le_bluetooth_device_address

      LE Bluetooth device address

   .. attribute:: advertising_interval

      Advertising interval (0.625ms units)

   .. attribute:: advertising_interval_long

      Long advertising interval

   .. attribute:: slave_connection_interval_range

      Preferred connection interval range

   .. attribute:: simple_pairing_hash_c

      Simple Pairing Hash C (P-192)

   .. attribute:: simple_pairing_randomizer_r

      Simple Pairing Randomizer R (P-192)

   .. attribute:: secure_connections_confirmation

      Secure Connections Confirmation Value

   .. attribute:: secure_connections_random

      Secure Connections Random Value

   .. attribute:: security_manager_tk_value

      Security Manager TK Value

   .. attribute:: security_manager_out_of_band_flags

      SM Out of Band Flags


   .. py:attribute:: public_target_address
      :type:  list[str]


   .. py:attribute:: random_target_address
      :type:  list[str]


   .. py:attribute:: le_bluetooth_device_address
      :type:  str
      :value: ''



   .. py:attribute:: advertising_interval
      :type:  int | None
      :value: None



   .. py:attribute:: advertising_interval_long
      :type:  int | None
      :value: None



   .. py:attribute:: slave_connection_interval_range
      :type:  bytes
      :value: b''



   .. py:attribute:: simple_pairing_hash_c
      :type:  bytes
      :value: b''



   .. py:attribute:: simple_pairing_randomizer_r
      :type:  bytes
      :value: b''



   .. py:attribute:: secure_connections_confirmation
      :type:  bytes
      :value: b''



   .. py:attribute:: secure_connections_random
      :type:  bytes
      :value: b''



   .. py:attribute:: security_manager_tk_value
      :type:  bytes
      :value: b''



   .. py:attribute:: security_manager_out_of_band_flags
      :type:  bytes
      :value: b''



.. py:class:: CoreAdvertisingData

   Bases: :py:obj:`msgspec.Struct`


   Core advertising data - device identification and services.

   .. attribute:: manufacturer_data

      Manufacturer-specific data keyed by company ID

   .. attribute:: manufacturer_names

      Resolved company names keyed by company ID

   .. attribute:: service_uuids

      List of advertised service UUIDs

   .. attribute:: service_data

      Service-specific data keyed by service UUID

   .. attribute:: solicited_service_uuids

      List of service UUIDs the device is seeking

   .. attribute:: local_name

      Device's local name (complete or shortened)

   .. attribute:: uri

      Uniform Resource Identifier


   .. py:attribute:: manufacturer_data
      :type:  dict[int, bytes]


   .. py:attribute:: manufacturer_names
      :type:  dict[int, str]


   .. py:attribute:: service_uuids
      :type:  list[str]


   .. py:attribute:: service_data
      :type:  dict[str, bytes]


   .. py:attribute:: solicited_service_uuids
      :type:  list[str]


   .. py:attribute:: local_name
      :type:  str
      :value: ''



   .. py:attribute:: uri
      :type:  str
      :value: ''



.. py:class:: DeviceProperties

   Bases: :py:obj:`msgspec.Struct`


   Device capability and appearance properties.

   .. attribute:: flags

      BLE advertising flags (discoverable mode, capabilities)

   .. attribute:: appearance

      Device appearance category and subcategory

   .. attribute:: tx_power

      Transmission power level in dBm

   .. attribute:: le_role

      LE role (peripheral, central, etc.)

   .. attribute:: le_supported_features

      LE supported features bit field

   .. attribute:: class_of_device

      Classic Bluetooth Class of Device value

   .. attribute:: class_of_device_info

      Parsed Class of Device information


   .. py:attribute:: flags
      :type:  BLEAdvertisingFlags


   .. py:attribute:: appearance
      :type:  bluetooth_sig.types.appearance.AppearanceData | None
      :value: None



   .. py:attribute:: tx_power
      :type:  int
      :value: 0



   .. py:attribute:: le_role
      :type:  int | None
      :value: None



   .. py:attribute:: le_supported_features
      :type:  bytes
      :value: b''



   .. py:attribute:: class_of_device
      :type:  int | None
      :value: None



   .. py:attribute:: class_of_device_info
      :type:  bluetooth_sig.types.registry.class_of_device.ClassOfDeviceInfo | None
      :value: None



.. py:class:: ExtendedAdvertisingData

   Bases: :py:obj:`msgspec.Struct`


   Extended advertising data (BLE 5.0+).

   .. attribute:: extended_payload

      Extended advertising payload bytes

   .. attribute:: auxiliary_packets

      List of auxiliary advertising packets

   .. attribute:: periodic_advertising_data

      Periodic advertising data bytes

   .. attribute:: broadcast_code

      Broadcast audio code


   .. py:attribute:: extended_payload
      :type:  bytes
      :value: b''



   .. py:attribute:: auxiliary_packets
      :type:  list[BLEAdvertisingPDU]


   .. py:attribute:: periodic_advertising_data
      :type:  bytes
      :value: b''



   .. py:attribute:: broadcast_code
      :type:  bytes
      :value: b''



.. py:class:: ExtendedHeaderFlags

   Bases: :py:obj:`enum.IntEnum`


   Extended advertising header field presence flags (BLE 5.0+).

   Each flag indicates whether a corresponding field is present
   in the extended advertising header.


   .. py:attribute:: ADV_ADDR
      :value: 1



   .. py:attribute:: TARGET_ADDR
      :value: 2



   .. py:attribute:: CTE_INFO
      :value: 4



   .. py:attribute:: ADV_DATA_INFO
      :value: 8



   .. py:attribute:: AUX_PTR
      :value: 16



   .. py:attribute:: SYNC_INFO
      :value: 32



   .. py:attribute:: TX_POWER
      :value: 64



   .. py:attribute:: ACAD
      :value: 128



.. py:class:: LocationAndSensingData

   Bases: :py:obj:`msgspec.Struct`


   Location, positioning, and sensing related data.

   .. attribute:: indoor_positioning

      Indoor positioning data

   .. attribute:: three_d_information

      3D information data

   .. attribute:: transport_discovery_data

      Transport Discovery Data

   .. attribute:: channel_map_update_indication

      Channel Map Update Indication


   .. py:attribute:: indoor_positioning
      :type:  bytes
      :value: b''



   .. py:attribute:: three_d_information
      :type:  bytes
      :value: b''



   .. py:attribute:: transport_discovery_data
      :type:  bytes
      :value: b''



   .. py:attribute:: channel_map_update_indication
      :type:  bytes
      :value: b''



.. py:class:: MeshAndBroadcastData

   Bases: :py:obj:`msgspec.Struct`


   Bluetooth Mesh and audio broadcast related data.

   .. attribute:: mesh_message

      Mesh Message

   .. attribute:: mesh_beacon

      Mesh Beacon

   .. attribute:: pb_adv

      Provisioning Bearer over advertising

   .. attribute:: broadcast_name

      Broadcast name

   .. attribute:: broadcast_code

      Broadcast Code for encrypted audio

   .. attribute:: biginfo

      BIG Info for Broadcast Isochronous Groups

   .. attribute:: periodic_advertising_response_timing

      Periodic Advertising Response Timing Info

   .. attribute:: electronic_shelf_label

      Electronic Shelf Label data


   .. py:attribute:: mesh_message
      :type:  bytes
      :value: b''



   .. py:attribute:: mesh_beacon
      :type:  bytes
      :value: b''



   .. py:attribute:: pb_adv
      :type:  bytes
      :value: b''



   .. py:attribute:: broadcast_name
      :type:  str
      :value: ''



   .. py:attribute:: broadcast_code
      :type:  bytes
      :value: b''



   .. py:attribute:: biginfo
      :type:  bytes
      :value: b''



   .. py:attribute:: periodic_advertising_response_timing
      :type:  bytes
      :value: b''



   .. py:attribute:: electronic_shelf_label
      :type:  bytes
      :value: b''



.. py:class:: PDUHeaderFlags

   Bases: :py:obj:`enum.IntFlag`


   BLE PDU header bit masks for parsing operations.

   These masks are pre-positioned to their correct bit locations,
   eliminating the need for shifts during extraction.


   .. py:attribute:: TYPE_MASK
      :value: 15



   .. py:attribute:: RFU_BIT_4
      :value: 16



   .. py:attribute:: RFU_BIT_5
      :value: 32



   .. py:attribute:: TX_ADD_MASK
      :value: 64



   .. py:attribute:: RX_ADD_MASK
      :value: 128



   .. py:method:: extract_bits(header: int, mask: int) -> int | bool
      :classmethod:


      Extract bits from header using the specified mask.

      Returns int for multi-bit masks, bool for single-bit masks.



   .. py:method:: extract_pdu_type(header: int) -> PDUType
      :classmethod:


      Extract PDU type from header byte and return as PDUType enum.



   .. py:method:: extract_tx_add(header: int) -> bool
      :classmethod:


      Extract TX address type from header.



   .. py:method:: extract_rx_add(header: int) -> bool
      :classmethod:


      Extract RX address type from header.



.. py:class:: PDULayout

   BLE PDU structure size and offset constants.

   Defines the sizes and offsets of fields within BLE PDU structures
   following Bluetooth Core Spec Vol 6, Part B.


   .. py:attribute:: BLE_ADDR
      :type:  int
      :value: 6



   .. py:attribute:: AUX_PTR
      :type:  int
      :value: 3



   .. py:attribute:: ADV_DATA_INFO
      :type:  int
      :value: 2



   .. py:attribute:: CTE_INFO
      :type:  int
      :value: 1



   .. py:attribute:: SYNC_INFO
      :type:  int
      :value: 18



   .. py:attribute:: TX_POWER
      :type:  int
      :value: 1



   .. py:attribute:: PDU_HEADER
      :type:  int
      :value: 2



   .. py:attribute:: MIN_EXTENDED_PDU
      :type:  int
      :value: 3



   .. py:attribute:: EXT_HEADER_LENGTH
      :type:  int
      :value: 1



   .. py:attribute:: EXTENDED_HEADER_START
      :type:  int
      :value: 3



   .. py:attribute:: ADV_MODE
      :type:  int
      :value: 1



   .. py:attribute:: ADV_ADDR_OFFSET
      :type:  int
      :value: 2



   .. py:attribute:: TARGET_ADDR_OFFSET
      :type:  int
      :value: 2



   .. py:attribute:: CTE_INFO_OFFSET
      :type:  int
      :value: 1



   .. py:attribute:: ADV_DATA_INFO_OFFSET
      :type:  int
      :value: 2



   .. py:attribute:: AUX_PTR_OFFSET
      :type:  int
      :value: 3



   .. py:attribute:: SYNC_INFO_OFFSET
      :type:  int
      :value: 18



   .. py:attribute:: TX_POWER_OFFSET
      :type:  int
      :value: 1



   .. py:attribute:: PDU_LENGTH_OFFSET
      :type:  int
      :value: 2



.. py:class:: PDUType

   Bases: :py:obj:`enum.IntEnum`


   BLE Advertising PDU Types (Core Spec Vol 6, Part B, Section 2.3).


   .. py:attribute:: ADV_IND
      :value: 0



   .. py:attribute:: ADV_DIRECT_IND
      :value: 1



   .. py:attribute:: ADV_NONCONN_IND
      :value: 2



   .. py:attribute:: SCAN_REQ
      :value: 3



   .. py:attribute:: SCAN_RSP
      :value: 4



   .. py:attribute:: CONNECT_IND
      :value: 5



   .. py:attribute:: ADV_SCAN_IND
      :value: 6



   .. py:attribute:: ADV_EXT_IND
      :value: 7



   .. py:attribute:: ADV_AUX_IND
      :value: 8



   .. py:property:: is_extended_advertising
      :type: bool


      Check if this is an extended advertising PDU.


   .. py:property:: is_legacy_advertising
      :type: bool


      Check if this is a legacy advertising PDU.


.. py:class:: SecurityData

   Bases: :py:obj:`msgspec.Struct`


   Security and encryption related advertising data.

   .. attribute:: encrypted_advertising_data

      Encrypted Advertising Data

   .. attribute:: resolvable_set_identifier

      Resolvable Set Identifier


   .. py:attribute:: encrypted_advertising_data
      :type:  bytes
      :value: b''



   .. py:attribute:: resolvable_set_identifier
      :type:  bytes
      :value: b''



.. py:data:: ALERT_CATEGORY_DEFINED_MAX
   :value: 9


.. py:data:: ALERT_CATEGORY_RESERVED_MAX
   :value: 250


.. py:data:: ALERT_CATEGORY_RESERVED_MIN
   :value: 10


.. py:data:: ALERT_CATEGORY_SERVICE_SPECIFIC_MIN
   :value: 251


.. py:data:: ALERT_COMMAND_MAX
   :value: 5


.. py:data:: ALERT_TEXT_MAX_LENGTH
   :value: 18


.. py:data:: UNREAD_COUNT_MAX
   :value: 254


.. py:data:: UNREAD_COUNT_MORE_THAN_MAX
   :value: 255


.. py:class:: AlertCategoryBitMask

   Bases: :py:obj:`enum.IntFlag`


   Alert category bit mask flags.

   Each bit represents support for a specific alert category.
   Bits 10-15 are reserved for future use.


   .. py:attribute:: SIMPLE_ALERT
      :value: 1



   .. py:attribute:: EMAIL
      :value: 2



   .. py:attribute:: NEWS
      :value: 4



   .. py:attribute:: CALL
      :value: 8



   .. py:attribute:: MISSED_CALL
      :value: 16



   .. py:attribute:: SMS_MMS
      :value: 32



   .. py:attribute:: VOICE_MAIL
      :value: 64



   .. py:attribute:: SCHEDULE
      :value: 128



   .. py:attribute:: HIGH_PRIORITIZED_ALERT
      :value: 256



   .. py:attribute:: INSTANT_MESSAGE
      :value: 512



.. py:class:: AlertCategoryID

   Bases: :py:obj:`enum.IntEnum`


   Alert category enumeration per Bluetooth SIG specification.

   Values 0-9 are defined, 10-250 reserved, 251-255 service-specific.


   .. py:attribute:: SIMPLE_ALERT
      :value: 0



   .. py:attribute:: EMAIL
      :value: 1



   .. py:attribute:: NEWS
      :value: 2



   .. py:attribute:: CALL
      :value: 3



   .. py:attribute:: MISSED_CALL
      :value: 4



   .. py:attribute:: SMS_MMS
      :value: 5



   .. py:attribute:: VOICE_MAIL
      :value: 6



   .. py:attribute:: SCHEDULE
      :value: 7



   .. py:attribute:: HIGH_PRIORITIZED_ALERT
      :value: 8



   .. py:attribute:: INSTANT_MESSAGE
      :value: 9



.. py:class:: AlertNotificationCommandID

   Bases: :py:obj:`enum.IntEnum`


   Alert Notification Control Point command enumeration.


   .. py:attribute:: ENABLE_NEW_ALERT
      :value: 0



   .. py:attribute:: ENABLE_UNREAD_STATUS
      :value: 1



   .. py:attribute:: DISABLE_NEW_ALERT
      :value: 2



   .. py:attribute:: DISABLE_UNREAD_STATUS
      :value: 3



   .. py:attribute:: NOTIFY_NEW_ALERT_IMMEDIATELY
      :value: 4



   .. py:attribute:: NOTIFY_UNREAD_STATUS_IMMEDIATELY
      :value: 5



.. py:function:: validate_category_id(category_id_raw: int) -> AlertCategoryID

   Validate and convert raw category ID value.

   :param category_id_raw: Raw category ID value (0-255)

   :returns: AlertCategoryID enum value

   :raises ValueError: If category ID is in reserved range (10-250)


.. py:class:: AppearanceData

   Bases: :py:obj:`msgspec.Struct`


   Appearance characteristic data with human-readable info.

   .. attribute:: raw_value

      Raw 16-bit appearance code from BLE

   .. attribute:: info

      Optional decoded appearance information from registry


   .. py:attribute:: raw_value
      :type:  int


   .. py:attribute:: info
      :type:  bluetooth_sig.types.registry.appearance_info.AppearanceInfo | None
      :value: None



   .. py:method:: from_category(category: str, subcategory: str | None = None) -> AppearanceData
      :classmethod:


      Create AppearanceData from category and subcategory strings.

      This helper validates the strings and finds the correct raw_value by
      searching the registry. Useful when creating appearance data from
      user-provided human-readable names.

      :param category: Device category name (e.g., "Heart Rate Sensor")
      :param subcategory: Optional subcategory name (e.g., "Heart Rate Belt")

      :returns: AppearanceData with validated info and correct raw_value

      :raises ValueError: If category/subcategory combination is not found in registry

      .. admonition:: Example

         >>> data = AppearanceData.from_category("Heart Rate Sensor", "Heart Rate Belt")
         >>> data.raw_value
         833



   .. py:property:: category
      :type: str | None


      Get device category name.

      :returns: Category name or None if info not available


   .. py:property:: subcategory
      :type: str | None


      Get device subcategory name.

      :returns: Subcategory name or None if not available


   .. py:property:: full_name
      :type: str | None


      Get full human-readable name.

      :returns: Full device type name or None if info not available


.. py:class:: SIGInfo

   Bases: :py:obj:`msgspec.Struct`


   Base information about Bluetooth SIG characteristics or services.


   .. py:attribute:: uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: id
      :type:  str
      :value: ''



.. py:class:: BatteryChargeLevel

   Bases: :py:obj:`enum.IntEnum`


   Battery charge level enumeration.


   .. py:attribute:: UNKNOWN
      :value: 0



   .. py:attribute:: GOOD
      :value: 1



   .. py:attribute:: LOW
      :value: 2



   .. py:attribute:: CRITICALLY_LOW
      :value: 3



   .. py:method:: from_byte(byte_val: int) -> BatteryChargeLevel
      :classmethod:


      Create enum from byte value with fallback.



.. py:class:: BatteryChargeState

   Bases: :py:obj:`enum.IntEnum`


   Battery charge state enumeration.


   .. py:attribute:: UNKNOWN
      :value: 0



   .. py:attribute:: CHARGING
      :value: 1



   .. py:attribute:: DISCHARGING
      :value: 2



   .. py:attribute:: NOT_CHARGING
      :value: 3



   .. py:method:: from_byte(byte_val: int) -> BatteryChargeState
      :classmethod:


      Create enum from byte value with fallback.



.. py:class:: BatteryChargingType

   Bases: :py:obj:`enum.IntEnum`


   Battery charging type enumeration.


   .. py:attribute:: UNKNOWN
      :value: 0



   .. py:attribute:: CONSTANT_CURRENT
      :value: 1



   .. py:attribute:: CONSTANT_VOLTAGE
      :value: 2



   .. py:attribute:: TRICKLE
      :value: 3



   .. py:attribute:: FLOAT
      :value: 4



   .. py:method:: from_byte(byte_val: int) -> BatteryChargingType
      :classmethod:


      Create enum from byte value with fallback.



.. py:class:: BatteryFaultReason

   Bases: :py:obj:`enum.IntEnum`


   Battery fault reason enumeration.


   .. py:attribute:: BATTERY_FAULT
      :value: 0



   .. py:attribute:: EXTERNAL_POWER_FAULT
      :value: 1



   .. py:attribute:: OTHER_FAULT
      :value: 2



.. py:class:: CharacteristicContext

   Bases: :py:obj:`msgspec.Struct`


   Runtime context passed into parsers - INPUT only.

   This provides the parsing context (device info, other characteristics for
   dependencies, etc.) but does NOT contain output fields. Descriptors have
   their own separate parsing flow.

   .. attribute:: device_info

      Basic device metadata (address, name, manufacturer data).

   .. attribute:: advertisement

      Raw advertisement bytes if available.

   .. attribute:: other_characteristics

      Mapping from characteristic UUID string to
      previously-parsed characteristic result. Parsers may consult this
      mapping to implement multi-characteristic decoding.

   .. attribute:: descriptors

      Mapping from descriptor UUID string to parsed descriptor data.
      Provides access to characteristic descriptors during parsing.

   .. attribute:: raw_service

      Optional raw service-level payload when applicable.


   .. py:attribute:: device_info
      :type:  DeviceInfo | None
      :value: None



   .. py:attribute:: advertisement
      :type:  bytes
      :value: b''



   .. py:attribute:: other_characteristics
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.protocols.CharacteristicDataProtocol] | None
      :value: None



   .. py:attribute:: descriptors
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.registry.descriptor_types.DescriptorData] | None
      :value: None



   .. py:attribute:: raw_service
      :type:  bytes
      :value: b''



.. py:class:: DeviceInfo

   Bases: :py:obj:`msgspec.Struct`


   Basic device metadata available to parsers.


   .. py:attribute:: address
      :type:  str
      :value: ''



   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: manufacturer_data
      :type:  dict[int, bytes]


   .. py:attribute:: service_uuids
      :type:  list[str]


.. py:class:: CharacteristicInfo

   Bases: :py:obj:`src.bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth characteristic from SIG/YAML specifications.

   This contains only static metadata resolved from YAML or SIG specs.
   Runtime properties (read/write/notify capabilities) are stored separately
   on the BaseCharacteristic instance as they're discovered from the actual device.


   .. py:attribute:: value_type
      :type:  src.bluetooth_sig.types.gatt_enums.ValueType


   .. py:attribute:: unit
      :type:  str
      :value: ''



.. py:class:: DateData

   Bases: :py:obj:`msgspec.Struct`


   Shared data type for date values with year, month, and day fields.


   .. py:attribute:: year
      :type:  int


   .. py:attribute:: month
      :type:  int


   .. py:attribute:: day
      :type:  int


.. py:class:: ParseFieldError

   Bases: :py:obj:`msgspec.Struct`


   Represents a field-level parsing error with diagnostic information.

   This provides structured error information similar to Pydantic's validation
   errors, making it easier to debug which specific field failed and why.

   .. attribute:: field

      Name of the field that failed (e.g., "temperature", "flags")

   .. attribute:: reason

      Human-readable description of why parsing failed

   .. attribute:: offset

      Optional byte offset where the field starts in raw data

   .. attribute:: raw_slice

      Optional raw bytes that were being parsed when error occurred


   .. py:attribute:: field
      :type:  str


   .. py:attribute:: reason
      :type:  str


   .. py:attribute:: offset
      :type:  int | None
      :value: None



   .. py:attribute:: raw_slice
      :type:  bytes | None
      :value: None



.. py:class:: ServiceInfo

   Bases: :py:obj:`src.bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth service.


   .. py:attribute:: characteristics
      :type:  list[CharacteristicInfo]


.. py:class:: ValidationResult

   Bases: :py:obj:`msgspec.Struct`


   Result of characteristic data validation.

   Provides diagnostic information about whether characteristic data
   matches the expected format per Bluetooth SIG specifications.

   This is a lightweight validation result, NOT SIG registry metadata.
   For characteristic metadata (uuid, name, description), query the
   characteristic's info directly.

   .. attribute:: is_valid

      Whether the data format is valid per SIG specs

   .. attribute:: actual_length

      Number of bytes in the data

   .. attribute:: expected_length

      Expected bytes for fixed-length characteristics, None for variable

   .. attribute:: error_message

      Description of validation failure, empty string if valid


   .. py:attribute:: is_valid
      :type:  bool


   .. py:attribute:: actual_length
      :type:  int


   .. py:attribute:: expected_length
      :type:  int | None
      :value: None



   .. py:attribute:: error_message
      :type:  str
      :value: ''



.. py:class:: PositionStatus

   Bases: :py:obj:`enum.IntEnum`


   Position status enumeration.

   Used by Navigation and Position Quality characteristics to indicate
   the status/quality of position data.

   Per Bluetooth SIG Location and Navigation Service specification.


   .. py:attribute:: NO_POSITION
      :value: 0



   .. py:attribute:: POSITION_OK
      :value: 1



   .. py:attribute:: ESTIMATED_POSITION
      :value: 2



   .. py:attribute:: LAST_KNOWN_POSITION
      :value: 3



.. py:class:: CharacteristicDataProtocol

   Bases: :py:obj:`Protocol`


   Minimal protocol describing the attributes used by parsers.

   This avoids importing the full `CharacteristicData` type here and
   gives callers a useful static type for `other_characteristics`.

   Now includes field-level error reporting and parse trace capabilities
   for improved diagnostics.


   .. py:attribute:: value
      :type:  Any


   .. py:attribute:: raw_data
      :type:  bytes


   .. py:attribute:: parse_success
      :type:  bool


   .. py:property:: properties
      :type: list[src.bluetooth_sig.types.gatt_enums.GattProperty]


      BLE GATT properties.


   .. py:property:: name
      :type: str


      Characteristic name.


   .. py:attribute:: field_errors
      :type:  list[Any]


   .. py:attribute:: parse_trace
      :type:  list[str]


.. py:class:: AppearanceInfo

   Bases: :py:obj:`msgspec.Struct`


   Decoded appearance information from registry.

   The 16-bit appearance value encodes device type information:
   - Bits 15-6 (10 bits): Category value (0-1023)
   - Bits 5-0 (6 bits): Subcategory value (0-63)
   - Full code = (category << 6) | subcategory

   .. attribute:: category

      Human-readable device category name (e.g., "Heart Rate Sensor")

   .. attribute:: category_value

      Category value (upper 10 bits of appearance code)

   .. attribute:: subcategory

      Optional subcategory information (e.g., "Heart Rate Belt")


   .. py:attribute:: category
      :type:  str


   .. py:attribute:: category_value
      :type:  int


   .. py:attribute:: subcategory
      :type:  AppearanceSubcategoryInfo | None
      :value: None



   .. py:property:: full_name
      :type: str


      Get full appearance name.

      :returns: Full name with category and optional subcategory
                (e.g., "Heart Rate Sensor: Heart Rate Belt" or "Phone")


.. py:class:: ClassOfDeviceInfo

   Bases: :py:obj:`msgspec.Struct`


   Decoded Class of Device information.

   Represents the decoded classification information from a 24-bit CoD field,
   including major/minor device classes and service classes.

   .. attribute:: major_class

      Major device class name (e.g., "Computer", "Phone")

   .. attribute:: minor_class

      Minor device class name (e.g., "Laptop", "Smartphone"), or None

   .. attribute:: service_classes

      List of service class names (e.g., ["Networking", "Audio"])

   .. attribute:: raw_value

      Original 24-bit CoD value


   .. py:attribute:: major_class
      :type:  list[MajorDeviceClassInfo] | None


   .. py:attribute:: minor_class
      :type:  list[MinorDeviceClassInfo] | None


   .. py:attribute:: service_classes
      :type:  list[str]


   .. py:attribute:: raw_value
      :type:  int


   .. py:property:: full_description
      :type: str


      Get full device description combining major, minor, and services.

      :returns: Laptop (Networking, Audio)"
      :rtype: Human-readable description like "Computer

      .. admonition:: Examples

         >>> info = ClassOfDeviceInfo(
         ...     major_class=[MajorDeviceClassInfo(value=1, name="Computer")],
         ...     minor_class=[MinorDeviceClassInfo(value=3, name="Laptop", major_class=1)],
         ...     service_classes=["Networking"],
         ...     raw_value=0x02010C,
         ... )
         >>> info.full_description
         'Computer: Laptop (Networking)'


.. py:class:: DescriptorData

   Bases: :py:obj:`msgspec.Struct`


   Parsed descriptor data with validation results.


   .. py:attribute:: info
      :type:  DescriptorInfo


   .. py:attribute:: value
      :type:  Any | None
      :value: None



   .. py:attribute:: raw_data
      :type:  bytes
      :value: b''



   .. py:attribute:: parse_success
      :type:  bool
      :value: False



   .. py:attribute:: error_message
      :type:  str
      :value: ''



   .. py:property:: name
      :type: str


      Get the descriptor name from info.


   .. py:property:: uuid
      :type: bluetooth_sig.types.uuid.BluetoothUUID


      Get the descriptor UUID from info.


.. py:class:: DescriptorInfo

   Bases: :py:obj:`bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth descriptor.


   .. py:attribute:: has_structured_data
      :type:  bool
      :value: False



   .. py:attribute:: data_format
      :type:  str
      :value: ''



.. py:class:: AngleUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for angle measurements.


   .. py:attribute:: DEGREES
      :value: '°'



.. py:class:: ConcentrationUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for concentration measurements.


   .. py:attribute:: MICROGRAMS_PER_CUBIC_METER
      :value: 'µg/m³'



   .. py:attribute:: PARTS_PER_MILLION
      :value: 'ppm'



   .. py:attribute:: PARTS_PER_BILLION
      :value: 'ppb'



   .. py:attribute:: KILOGRAMS_PER_CUBIC_METER
      :value: 'kg/m³'



   .. py:attribute:: GRAINS_PER_CUBIC_METER
      :value: 'grains/m³'



.. py:class:: ElectricalUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for electrical measurements.


   .. py:attribute:: VOLTS
      :value: 'V'



   .. py:attribute:: AMPS
      :value: 'A'



   .. py:attribute:: HERTZ
      :value: 'Hz'



   .. py:attribute:: DBM
      :value: 'dBm'



.. py:class:: GlucoseConcentrationUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for glucose concentration measurements.


   .. py:attribute:: MG_DL
      :value: 'mg/dL'



   .. py:attribute:: MMOL_L
      :value: 'mmol/L'



.. py:class:: HeightUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for height measurements.


   .. py:attribute:: METERS
      :value: 'meters'



   .. py:attribute:: INCHES
      :value: 'inches'



.. py:class:: LengthUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for length measurements.


   .. py:attribute:: MILLIMETERS
      :value: 'mm'



   .. py:attribute:: METERS
      :value: 'm'



   .. py:attribute:: INCHES
      :value: "'"



.. py:class:: MeasurementSystem(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Measurement system for body composition and weight data.


   .. py:attribute:: METRIC
      :value: 'metric'



   .. py:attribute:: IMPERIAL
      :value: 'imperial'



.. py:class:: PercentageUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for percentage measurements.


   .. py:attribute:: PERCENT
      :value: '%'



.. py:class:: PhysicalUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for physical measurements.


   .. py:attribute:: TESLA
      :value: 'T'



.. py:class:: PressureUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for pressure measurements.


   .. py:attribute:: KPA
      :value: 'kPa'



   .. py:attribute:: MMHG
      :value: 'mmHg'



.. py:class:: SoundUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for sound measurements.


   .. py:attribute:: DECIBELS_SPL
      :value: 'dB SPL'



.. py:class:: TemperatureUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for temperature measurements.


   .. py:attribute:: CELSIUS
      :value: '°C'



   .. py:attribute:: FAHRENHEIT
      :value: '°F'



.. py:class:: WeightUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for weight/mass measurements.


   .. py:attribute:: KG
      :value: 'kg'



   .. py:attribute:: LB
      :value: 'lb'



