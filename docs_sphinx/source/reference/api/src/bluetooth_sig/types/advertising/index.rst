src.bluetooth_sig.types.advertising
===================================

.. py:module:: src.bluetooth_sig.types.advertising

.. autoapi-nested-parse::

   BLE Advertising data types and parsing utilities.

   Organization:
       1. Core PDU Types and Enums - Low-level PDU structure definitions
       2. Advertising Data Type Registry - AD Type metadata
       3. Advertising Flags - Device discovery and capabilities flags
       4. PDU and Header Structures - Structured PDU representations
       5. Parsed Advertising Data - High-level parsed advertisement content



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.advertising.PDUType
   src.bluetooth_sig.types.advertising.PDUHeaderFlags
   src.bluetooth_sig.types.advertising.PDULayout
   src.bluetooth_sig.types.advertising.ExtendedHeaderFlags
   src.bluetooth_sig.types.advertising.ADTypeInfo
   src.bluetooth_sig.types.advertising.BLEAdvertisingFlags
   src.bluetooth_sig.types.advertising.BLEExtendedHeader
   src.bluetooth_sig.types.advertising.BLEAdvertisingPDU
   src.bluetooth_sig.types.advertising.CoreAdvertisingData
   src.bluetooth_sig.types.advertising.DeviceProperties
   src.bluetooth_sig.types.advertising.ConnectionData
   src.bluetooth_sig.types.advertising.LocationAndSensingData
   src.bluetooth_sig.types.advertising.MeshAndBroadcastData
   src.bluetooth_sig.types.advertising.SecurityData
   src.bluetooth_sig.types.advertising.ExtendedAdvertisingData
   src.bluetooth_sig.types.advertising.AdvertisingDataStructures
   src.bluetooth_sig.types.advertising.AdvertisingData


Module Contents
---------------

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


