"""Typed containers for staging raw BLE I/O into the translator.

These structs model common outputs from BLE connection managers (e.g., Bleak,
SimpleBLE) and provide a convenient way to feed raw bytes into the
`BluetoothSIGTranslator` batch parser, including descriptor bytes when
available.
"""

from __future__ import annotations

import msgspec

from .uuid import BluetoothUUID


class RawCharacteristicRead(msgspec.Struct, kw_only=True):
    """Container for a single characteristic read.

    This type is convenient for users to stage raw values coming from their BLE
    connection manager (e.g. Bleak, SimpleBLE) before handing them to the
    translator. It models the common shape produced by those libraries:

    - `uuid`: characteristic UUID (short or full form)
    - `raw_data`: bytes value as returned by `read_gatt_char`/notification
    - `descriptors`: optional mapping of descriptor UUID -> raw bytes (if read)
    - `properties`: optional list of characteristic properties (e.g. "read",
      "notify"). These are currently informational for the parser.
    """

    uuid: BluetoothUUID | str
    raw_data: bytes
    descriptors: dict[str, bytes] = msgspec.field(default_factory=dict)
    properties: list[str] = msgspec.field(default_factory=list)


class RawCharacteristicBatch(msgspec.Struct, kw_only=True):
    """A batch of raw characteristic reads to be parsed together.

    Use this when you have multiple related characteristics (e.g., Glucose
    Measurement + Glucose Measurement Context). The translator can parse them in
    dependency-aware order.
    """

    items: list[RawCharacteristicRead]


def to_parse_inputs(
    batch: RawCharacteristicBatch,
) -> tuple[dict[str, bytes], dict[str, dict[str, bytes]]]:
    """Convert a :class:`RawCharacteristicBatch` to translator inputs.

    Returns a tuple of `(char_data, descriptor_data)` suitable for
    `BluetoothSIGTranslator.parse_characteristics(char_data, descriptor_data=...)`.

    - `char_data` is a mapping of UUID -> raw bytes
    - `descriptor_data` is a nested mapping of char UUID -> (descriptor UUID -> raw bytes)
    """
    char_data: dict[str, bytes] = {}
    descriptor_data: dict[str, dict[str, bytes]] = {}

    for item in batch.items:
        uuid_str = str(item.uuid)
        char_data[uuid_str] = item.raw_data
        if item.descriptors:
            descriptor_data[uuid_str] = dict(item.descriptors)

    return char_data, descriptor_data
