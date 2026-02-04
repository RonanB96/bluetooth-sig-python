"""BLE Advertising data types and parsing utilities.

This package contains types organized by category:
    - pdu: PDU-level structures (PDUType, BLEAdvertisingPDU, headers)
    - extended: Extended advertising fields (CTE, ADI, AuxPtr, SyncInfo)
    - flags: BLE advertising flags
    - features: LE supported features
    - ad_structures: Parsed AD structure categories
    - builder: Advertisement data encoding and building
    - result: Final composed advertising data types
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
from bluetooth_sig.types.advertising.features import LEFeatures
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.advertising.pdu import BLEAdvertisingPDU
from bluetooth_sig.types.advertising.result import AdvertisementData, AdvertisingData

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
    # features
    "LEFeatures",
    # flags
    "BLEAdvertisingFlags",
    # pdu
    "BLEAdvertisingPDU",
    # result types
    "AdvertisementData",
    "AdvertisingData",
]
