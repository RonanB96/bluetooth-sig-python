"""Advertisement data builder for BLE peripheral encoding.

This module provides generic encoding functionality for BLE advertising data,
converting structured data into properly formatted AD structures that can be
broadcast by peripheral devices.

Reference: Bluetooth Core Specification Supplement, Part A (Advertising Data).
"""

from __future__ import annotations

import struct
from collections.abc import Sequence

import msgspec

from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.company import CompanyIdentifier, ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID

# Maximum data length for a single AD structure (255 - 1 for length byte - 1 for type byte)
AD_STRUCTURE_MAX_DATA_SIZE: int = 254


class ADStructure(msgspec.Struct, frozen=True, kw_only=True):
    """Single AD structure (Length-Type-Data format).

    Each AD structure consists of:
    - 1 byte: Length (length of type + data)
    - 1 byte: AD Type
    - N bytes: Data

    Attributes:
        ad_type: The AD type constant (e.g., ADType.FLAGS, ADType.COMPLETE_LOCAL_NAME).
        data: The raw data bytes for this AD structure.

    """

    ad_type: int
    data: bytes

    def to_bytes(self) -> bytes:
        """Encode to wire format (length-type-data).

        Returns:
            Encoded bytes ready for advertising payload.

        Raises:
            ValueError: If data exceeds maximum AD structure size (254 bytes).

        """
        if len(self.data) > AD_STRUCTURE_MAX_DATA_SIZE:
            raise ValueError(f"AD structure data too long: {len(self.data)} bytes, max {AD_STRUCTURE_MAX_DATA_SIZE}")
        length = len(self.data) + 1  # +1 for AD type byte
        return bytes([length, self.ad_type]) + self.data

    def __len__(self) -> int:
        """Total encoded length including length byte."""
        return 2 + len(self.data)


class AdvertisementBuilder(msgspec.Struct, frozen=True, kw_only=True):
    r"""Builder for constructing BLE advertising payloads.

    Provides a fluent interface for building advertising data with proper
    encoding according to Bluetooth Core Specification.

    The builder accumulates AD structures and can produce a final encoded
    payload suitable for use with BLE peripheral APIs.

    Example::
        >>> from bluetooth_sig.types.advertising.builder import AdvertisementBuilder
        >>> from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
        >>>
        >>> # Build advertising payload
        >>> builder = AdvertisementBuilder()
        >>> builder = builder.with_flags(
        ...     BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE | BLEAdvertisingFlags.BR_EDR_NOT_SUPPORTED
        ... )
        >>> builder = builder.with_complete_local_name("MySensor")
        >>> builder = builder.with_service_uuids(["180F", "181A"])
        >>> builder = builder.with_manufacturer_data(0x004C, b"\x02\x15...")
        >>>
        >>> payload = builder.build()

    Attributes:
        structures: List of AD structures accumulated so far.
        max_payload_size: Maximum payload size (31 for legacy, 254 for extended).

    """

    # Standard advertising payload limits
    LEGACY_MAX_SIZE: int = 31
    EXTENDED_MAX_SIZE: int = 254

    structures: list[ADStructure] = msgspec.field(default_factory=list)
    max_payload_size: int = LEGACY_MAX_SIZE

    def _add_structure(self, ad_type: int, data: bytes) -> AdvertisementBuilder:
        """Add an AD structure (returns new builder, immutable pattern)."""
        new_structure = ADStructure(ad_type=ad_type, data=data)
        return AdvertisementBuilder(
            structures=[*self.structures, new_structure],
            max_payload_size=self.max_payload_size,
        )

    def with_extended_advertising(self) -> AdvertisementBuilder:
        """Enable extended advertising mode (up to 254 bytes).

        Returns:
            New builder with extended payload size limit.

        """
        return AdvertisementBuilder(
            structures=list(self.structures),
            max_payload_size=self.EXTENDED_MAX_SIZE,
        )

    def with_flags(self, flags: BLEAdvertisingFlags | int) -> AdvertisementBuilder:
        """Add advertising flags.

        Args:
            flags: BLEAdvertisingFlags enum or raw int value.

        Returns:
            New builder with flags added.

        """
        flag_value = int(flags)
        return self._add_structure(ADType.FLAGS, bytes([flag_value]))

    def with_complete_local_name(self, name: str) -> AdvertisementBuilder:
        """Add complete local name.

        Args:
            name: Device name (UTF-8 encoded).

        Returns:
            New builder with name added.

        """
        return self._add_structure(
            ADType.COMPLETE_LOCAL_NAME,
            name.encode("utf-8"),
        )

    def with_shortened_local_name(self, name: str) -> AdvertisementBuilder:
        """Add shortened local name.

        Args:
            name: Shortened device name (UTF-8 encoded).

        Returns:
            New builder with shortened name added.

        """
        return self._add_structure(
            ADType.SHORTENED_LOCAL_NAME,
            name.encode("utf-8"),
        )

    def with_tx_power(self, power_dbm: int) -> AdvertisementBuilder:
        """Add TX power level.

        Args:
            power_dbm: Transmission power in dBm (-127 to +127).

        Returns:
            New builder with TX power added.

        """
        # TX power is signed int8
        data = struct.pack("b", power_dbm)
        return self._add_structure(ADType.TX_POWER_LEVEL, data)

    def with_service_uuids(
        self,
        uuids: Sequence[str | BluetoothUUID],
        *,
        complete: bool = True,
    ) -> AdvertisementBuilder:
        """Add service UUIDs to advertising data.

        Automatically selects the appropriate AD type based on UUID format:
        - 16-bit UUIDs (e.g., "180F") -> Compact 2-byte encoding
        - 128-bit UUIDs -> Full 16-byte encoding

        Args:
            uuids: Service UUIDs to advertise.
            complete: If True, use "Complete" list types; else "Incomplete".

        Returns:
            New builder with service UUIDs added (unchanged if uuids is empty).

        """
        if not uuids:
            # Return new instance to maintain immutable pattern
            return AdvertisementBuilder(
                structures=list(self.structures),
                max_payload_size=self.max_payload_size,
            )

        builder = self

        # Group by size for efficient encoding
        uuid_16bit: list[bytes] = []
        uuid_128bit: list[bytes] = []

        for uuid in uuids:
            bt_uuid = BluetoothUUID(str(uuid))
            full_form = bt_uuid.full_form

            # Check if this uses the SIG base UUID (can be encoded as 16-bit)
            if full_form.endswith(BluetoothUUID.SIG_BASE_SUFFIX) and full_form.startswith("0000"):
                # Use compact 16-bit encoding for SIG UUIDs
                short_hex = full_form[4:8]
                short_id = int(short_hex, 16)
                uuid_16bit.append(struct.pack("<H", short_id))
            else:
                # Custom 128-bit UUID
                uuid_128bit.append(bt_uuid.to_bytes())

        # Add 16-bit service UUIDs
        if uuid_16bit:
            ad_type = ADType.COMPLETE_16BIT_SERVICE_UUIDS if complete else ADType.INCOMPLETE_16BIT_SERVICE_UUIDS
            builder = builder._add_structure(ad_type, b"".join(uuid_16bit))

        # Add 128-bit service UUIDs
        if uuid_128bit:
            ad_type = ADType.COMPLETE_128BIT_SERVICE_UUIDS if complete else ADType.INCOMPLETE_128BIT_SERVICE_UUIDS
            builder = builder._add_structure(ad_type, b"".join(uuid_128bit))

        return builder

    def with_manufacturer_data(
        self,
        company_id: int | CompanyIdentifier,
        payload: bytes,
    ) -> AdvertisementBuilder:
        """Add manufacturer-specific data.

        Args:
            company_id: Bluetooth SIG company identifier (e.g., 0x004C for Apple).
            payload: Manufacturer-specific payload bytes.

        Returns:
            New builder with manufacturer data added.

        """
        cid = company_id.id if isinstance(company_id, CompanyIdentifier) else company_id

        # Company ID is little-endian uint16
        data = struct.pack("<H", cid) + payload
        return self._add_structure(ADType.MANUFACTURER_SPECIFIC_DATA, data)

    def with_manufacturer_data_struct(
        self,
        mfr_data: ManufacturerData,
    ) -> AdvertisementBuilder:
        """Add manufacturer-specific data from ManufacturerData struct.

        Args:
            mfr_data: ManufacturerData instance.

        Returns:
            New builder with manufacturer data added.

        """
        return self.with_manufacturer_data(mfr_data.company.id, mfr_data.payload)

    def with_service_data(
        self,
        service_uuid: str | BluetoothUUID,
        data: bytes,
    ) -> AdvertisementBuilder:
        """Add service data.

        Args:
            service_uuid: Service UUID.
            data: Service-specific data bytes.

        Returns:
            New builder with service data added.

        """
        bt_uuid = BluetoothUUID(str(service_uuid))
        full_form = bt_uuid.full_form

        # Check if this uses the SIG base UUID (can be encoded as 16-bit)
        if full_form.endswith(BluetoothUUID.SIG_BASE_SUFFIX) and full_form.startswith("0000"):
            # 16-bit service data
            short_hex = full_form[4:8]
            short_id = int(short_hex, 16)
            uuid_bytes = struct.pack("<H", short_id)
            return self._add_structure(ADType.SERVICE_DATA_16BIT, uuid_bytes + data)

        # 128-bit service data
        uuid_bytes = bt_uuid.to_bytes()
        return self._add_structure(ADType.SERVICE_DATA_128BIT, uuid_bytes + data)

    def with_appearance(self, appearance: int) -> AdvertisementBuilder:
        """Add device appearance.

        Args:
            appearance: 16-bit appearance value from Appearance registry.

        Returns:
            New builder with appearance added.

        """
        data = struct.pack("<H", appearance)
        return self._add_structure(ADType.APPEARANCE, data)

    def with_raw_structure(self, ad_type: int, data: bytes) -> AdvertisementBuilder:
        """Add a raw AD structure.

        Use this for AD types not covered by other methods.

        Args:
            ad_type: AD type constant.
            data: Raw data bytes.

        Returns:
            New builder with structure added.

        """
        return self._add_structure(ad_type, data)

    def current_size(self) -> int:
        """Get current encoded payload size.

        Returns:
            Total size in bytes of all AD structures.

        """
        return sum(len(s) for s in self.structures)

    def remaining_space(self) -> int:
        """Get remaining space in payload.

        Returns:
            Bytes remaining before max_payload_size.

        """
        return self.max_payload_size - self.current_size()

    def build(self) -> bytes:
        """Build the final advertising payload.

        Returns:
            Concatenated AD structures as bytes.

        Raises:
            ValueError: If payload exceeds max_payload_size.

        """
        payload = b"".join(s.to_bytes() for s in self.structures)

        if len(payload) > self.max_payload_size:
            raise ValueError(f"Advertising payload too large: {len(payload)} bytes, max {self.max_payload_size}")

        return payload


def encode_manufacturer_data(company_id: int, payload: bytes) -> bytes:
    """Encode manufacturer-specific data to bytes.

    Args:
        company_id: Bluetooth SIG company identifier.
        payload: Manufacturer-specific payload.

    Returns:
        Encoded bytes (company ID little-endian + payload).

    """
    return struct.pack("<H", company_id) + payload


def encode_service_uuids_16bit(uuids: Sequence[str | BluetoothUUID]) -> bytes:
    """Encode 16-bit service UUIDs.

    Args:
        uuids: Service UUIDs (must be SIG UUIDs using base UUID).

    Returns:
        Concatenated little-endian 16-bit UUIDs.

    Raises:
        ValueError: If any UUID cannot be encoded as 16-bit.

    """
    result = bytearray()
    for uuid in uuids:
        bt_uuid = BluetoothUUID(str(uuid))
        full_form = bt_uuid.full_form

        # Check if this uses the SIG base UUID
        if not (full_form.endswith(BluetoothUUID.SIG_BASE_SUFFIX) and full_form.startswith("0000")):
            raise ValueError(f"UUID {uuid} cannot be encoded as 16-bit SIG UUID")

        short_hex = full_form[4:8]
        short_id = int(short_hex, 16)
        result.extend(struct.pack("<H", short_id))
    return bytes(result)


def encode_service_uuids_128bit(uuids: Sequence[str | BluetoothUUID]) -> bytes:
    """Encode 128-bit service UUIDs.

    Args:
        uuids: Service UUIDs.

    Returns:
        Concatenated 128-bit UUID bytes.

    """
    result = bytearray()
    for uuid in uuids:
        bt_uuid = BluetoothUUID(str(uuid))
        result.extend(bt_uuid.to_bytes())
    return bytes(result)


__all__ = [
    "ADStructure",
    "AdvertisementBuilder",
    "encode_manufacturer_data",
    "encode_service_uuids_16bit",
    "encode_service_uuids_128bit",
]
