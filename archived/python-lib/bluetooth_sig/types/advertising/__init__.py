"""BLE Advertising data types and parsing utilities.

This package contains types organised by category:
    - pdu: PDU-level structures (PDUType, BLEAdvertisingPDU, headers)
    - extended: Extended advertising fields (CTE, ADI, AuxPtr, SyncInfo)
    - flags: BLE advertising flags
    - features: LE supported features
    - ad_structures: Parsed AD structure categories
    - builder: Advertisement data encoding and building
    - result: Final composed advertising data types
    - indoor_positioning: Indoor Positioning AD type (0x25)
    - transport_discovery: Transport Discovery Data AD type (0x26)
    - channel_map_update: Channel Map Update Indication AD type (0x28)
    - three_d_information: 3D Information Data AD type (0x3D)
"""

from bluetooth_sig.types.advertising.ad_structures import (
    AdvertisingDataStructures,
    ConnectionIntervalRange,
    CoreAdvertisingData,
    DeviceProperties,
    DirectedAdvertisingData,
    ExtendedAdvertisingData,
    LocationAndSensingData,
    MeshAndBroadcastData,
    OOBSecurityData,
    SecurityData,
)
from bluetooth_sig.types.advertising.builder import (
    ADStructure,
    AdvertisementBuilder,
    encode_manufacturer_data,
    encode_service_uuids_16bit,
    encode_service_uuids_128bit,
)
from bluetooth_sig.types.advertising.channel_map_update import ChannelMapUpdateIndication
from bluetooth_sig.types.advertising.features import LEFeatures
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.advertising.indoor_positioning import (
    IndoorPositioningConfig,
    IndoorPositioningData,
)
from bluetooth_sig.types.advertising.pdu import BLEAdvertisingPDU
from bluetooth_sig.types.advertising.result import AdvertisementData, AdvertisingData
from bluetooth_sig.types.advertising.three_d_information import (
    ThreeDInformationData,
    ThreeDInformationFlags,
)
from bluetooth_sig.types.advertising.transport_discovery import (
    TDSFlags,
    TransportBlock,
    TransportDiscoveryData,
)

__all__ = [
    # ad_structures types
    "AdvertisingDataStructures",
    "ConnectionIntervalRange",
    "CoreAdvertisingData",
    "DeviceProperties",
    "DirectedAdvertisingData",
    "ExtendedAdvertisingData",
    "LocationAndSensingData",
    "MeshAndBroadcastData",
    "OOBSecurityData",
    "SecurityData",
    # builder types
    "ADStructure",
    "AdvertisementBuilder",
    "encode_manufacturer_data",
    "encode_service_uuids_16bit",
    "encode_service_uuids_128bit",
    # channel_map_update
    "ChannelMapUpdateIndication",
    # features
    "LEFeatures",
    # flags
    "BLEAdvertisingFlags",
    # indoor_positioning
    "IndoorPositioningConfig",
    "IndoorPositioningData",
    # pdu
    "BLEAdvertisingPDU",
    # result types
    "AdvertisementData",
    "AdvertisingData",
    # three_d_information
    "ThreeDInformationData",
    "ThreeDInformationFlags",
    # transport_discovery
    "TDSFlags",
    "TransportBlock",
    "TransportDiscoveryData",
]
