"""Termination Reason characteristic (0x2BC0)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class TerminationReason(IntEnum):
    """Call termination reason."""

    REMOTE_PARTY_ENDED = 0x00
    SERVER_ENDED = 0x01
    LINE_BUSY = 0x02
    NETWORK_CONGESTION = 0x03
    CLIENT_ENDED = 0x04
    NO_SERVICE = 0x05
    NO_ANSWER = 0x06
    UNSPECIFIED = 0x07


class TerminationReasonCharacteristic(BaseCharacteristic[TerminationReason]):
    """Termination Reason characteristic (0x2BC0).

    org.bluetooth.characteristic.termination_reason

    The reason for call termination.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(TerminationReason)
