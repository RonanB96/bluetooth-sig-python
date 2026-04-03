"""Digital characteristic (0x2A56)."""

from __future__ import annotations

from enum import IntEnum

from ...types import CharacteristicInfo
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class DigitalSignalState(IntEnum):
    """2-bit digital signal state enumeration (Automation IO Service v1.0).

    Per AIO spec §3.1, each digital signal is encoded as a 2-bit value:
      0b00: Inactive state (logical low / contact open)
      0b01: Active state (logical high / contact closed)
      0b10: Tri-state (if supported; ignored on write)
      0b11: Unknown (server cannot report; writes with this value are ignored by server)
    """

    INACTIVE = 0b00
    ACTIVE = 0b01
    TRISTATE = 0b10
    UNKNOWN = 0b11


class DigitalCharacteristic(BaseCharacteristic[tuple[DigitalSignalState, ...]]):
    """Digital characteristic (0x2A56).

    org.bluetooth.characteristic.digital

    Automation IO Service (AIOS) v1.0 §3.1: Array of n 2-bit digital signal values
    in little-endian bit order within packed octets.

    Format:
      - Length: ceil(n/4) octets, where n = number of digital signals
      - Each 2-bit field encodes one signal state (see DigitalSignalState enum)
      - Bit order within each octet: LSB first (little-endian)
        Byte bits [1:0] = Signal 0, bits [3:2] = Signal 1, bits [5:4] = Signal 2, bits [7:6] = Signal 3

    Specification:
      - Source: Bluetooth SIG Automation IO Service v1.0 (AIOS_v1.0)
      - Mandatory descriptor: Number of Digitals (0x2908) - specifies number of valid 2-bit fields
      - Optional descriptors: Value Trigger Setting, Time Trigger Setting
    """

    # Help the registry resolver find this characteristic by name
    _characteristic_name = "Digital"

    min_length = 0
    allow_variable_length = True
    # TODO Remove once uuid is added to yaml files
    _info = CharacteristicInfo(
        uuid=BluetoothUUID(0x2A56),
        name="Digital",
        id="org.bluetooth.characteristic.digital",
        unit="",
    )

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> tuple[DigitalSignalState, ...]:
        """Decode packed 2-bit digital signal states from little-endian bytes.

        Args:
            data: Raw bytes containing packed 2-bit signal values.
            ctx: Optional context (unused for Digital).
            validate: Whether to validate (currently unused; all 2-bit values are valid).

        Returns:
            Tuple of DigitalSignalState enums, one per 2-bit field.
            Example: bytearray([0x05]) decodes to (ACTIVE, ACTIVE, INACTIVE, INACTIVE)
                     because 0x05 = 0b0000_0101
                     - bits [1:0] = 0b01 = ACTIVE
                     - bits [3:2] = 0b01 = ACTIVE
                     - bits [5:4] = 0b00 = INACTIVE
                     - bits [7:6] = 0b00 = INACTIVE
        """
        signals: list[DigitalSignalState] = []

        for byte in data:
            # Extract four 2-bit values from each byte (little-endian bit order)
            for shift in range(0, 8, 2):
                value = (byte >> shift) & 0x03
                signals.append(DigitalSignalState(value))

        return tuple(signals)

    def _encode_value(self, data: tuple[DigitalSignalState, ...]) -> bytearray:
        """Encode digital signal states as packed little-endian 2-bit values.

        Args:
            data: Tuple of DigitalSignalState values to encode.

        Returns:
            Bytearray with packed 2-bit values (4 signals per byte).
            Example: (ACTIVE, ACTIVE, INACTIVE, INACTIVE) encodes to bytearray([0x05])
        """
        result = bytearray()

        # Pack 4 signals per byte
        for i in range(0, len(data), 4):
            byte = 0

            for j in range(4):
                if i + j < len(data):
                    signal_value = int(data[i + j])
                    byte |= (signal_value & 0x03) << (j * 2)

            result.append(byte)

        return result
