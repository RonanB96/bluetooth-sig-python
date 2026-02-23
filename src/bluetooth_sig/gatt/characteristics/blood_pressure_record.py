"""Blood Pressure Record characteristic implementation.

Implements the Blood Pressure Record characteristic (0x2B36).  This is a
segmented record container that wraps another characteristic value identified
by a 16-bit UUID.

Structure (from GSS YAML):
    Segmentation Header (1 byte):
        Bit 0: First Segment
        Bit 1: Last Segment
        Bits 2-7: Rolling Segment Counter (0-63)
    Sequence Number (uint16)
    UUID (uint16) -- identifies the recorded characteristic
    Recorded Characteristic (variable) -- raw bytes of the inner characteristic
    E2E-CRC (uint16, optional) -- presence defined by service

References:
    Bluetooth SIG Blood Pressure Service 1.1
    org.bluetooth.characteristic.blood_pressure_record (GSS YAML)
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_SEGMENT_COUNTER_SHIFT = 2
_SEGMENT_COUNTER_MASK = 0x3F  # bits 2-7 = 6 bits


class BloodPressureRecordData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Blood Pressure Record characteristic.

    Attributes:
        first_segment: Whether this is the first segment of the record.
        last_segment: Whether this is the last segment of the record.
        segment_counter: Rolling segment counter (0-63).
        sequence_number: Sequence number identifying this record.
        uuid: 16-bit UUID of the recorded characteristic.
        recorded_data: Raw bytes of the recorded characteristic value.
        e2e_crc: End-to-end CRC value. None if absent.

    """

    first_segment: bool
    last_segment: bool
    segment_counter: int
    sequence_number: int
    uuid: BluetoothUUID
    recorded_data: bytes
    e2e_crc: int | None = None


class BloodPressureRecordCharacteristic(BaseCharacteristic[BloodPressureRecordData]):
    """Blood Pressure Record characteristic (0x2B36).

    A segmented record container that wraps another characteristic value.
    The inner characteristic is identified by the UUID field and its raw
    bytes are stored in ``recorded_data``.
    """

    expected_type = BloodPressureRecordData
    min_length: int = 5  # header(1) + sequence(2) + uuid(2)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BloodPressureRecordData:
        """Parse Blood Pressure Record from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BloodPressureRecordData with segmentation info and raw recorded data.

        """
        header = data[0]
        first_segment = bool(header & 0x01)
        last_segment = bool(header & 0x02)
        segment_counter = (header >> _SEGMENT_COUNTER_SHIFT) & _SEGMENT_COUNTER_MASK

        sequence_number = DataParser.parse_int16(data, 1, signed=False)
        uuid = BluetoothUUID(DataParser.parse_int16(data, 3, signed=False))
        offset = 5

        # Determine if E2E-CRC is present.
        # The recorded data occupies everything between offset and the end,
        # except for the optional 2-byte CRC at the very end.
        # We cannot deterministically know whether CRC is present without
        # service-level context, so we expose all remaining bytes as recorded
        # data.  When the caller knows CRC is enabled, they can split the
        # last 2 bytes themselves.
        recorded_data = bytes(data[offset:])

        return BloodPressureRecordData(
            first_segment=first_segment,
            last_segment=last_segment,
            segment_counter=segment_counter,
            sequence_number=sequence_number,
            uuid=uuid,
            recorded_data=recorded_data,
        )

    def _encode_value(self, data: BloodPressureRecordData) -> bytearray:
        """Encode BloodPressureRecordData back to BLE bytes.

        Args:
            data: BloodPressureRecordData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        header = 0
        if data.first_segment:
            header |= 0x01
        if data.last_segment:
            header |= 0x02
        header |= (data.segment_counter & _SEGMENT_COUNTER_MASK) << _SEGMENT_COUNTER_SHIFT

        result = bytearray([header])
        result.extend(DataParser.encode_int16(data.sequence_number, signed=False))
        result.extend(DataParser.encode_int16(int(data.uuid.short_form, 16), signed=False))
        result.extend(data.recorded_data)

        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))

        return result
