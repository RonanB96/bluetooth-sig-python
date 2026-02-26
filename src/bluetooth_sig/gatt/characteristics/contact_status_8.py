"""Contact Status 8 characteristic (0x2C10)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class ContactStatus(IntFlag):
    """Individual contact status flags for Contact Status 8.

    Each flag represents one contact input:
    0 = no contact, 1 = contact detected.
    """

    CONTACT_0 = 0x01
    CONTACT_1 = 0x02
    CONTACT_2 = 0x04
    CONTACT_3 = 0x08
    CONTACT_4 = 0x10
    CONTACT_5 = 0x20
    CONTACT_6 = 0x40
    CONTACT_7 = 0x80


class ContactStatus8Characteristic(BaseCharacteristic[ContactStatus]):
    """Contact Status 8 characteristic (0x2C10).

    org.bluetooth.characteristic.contact_status_8

    Eight independent contact status bits packed in a single byte.
    Each bit represents one contact: 0 = no contact, 1 = contact detected.
    """

    _template = FlagTemplate.uint8(ContactStatus)
