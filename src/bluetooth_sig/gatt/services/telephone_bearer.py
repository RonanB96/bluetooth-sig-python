"""TelephoneBearer Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class TelephoneBearerService(BaseGattService):
    """Telephone Bearer Service implementation (0x184B).

    Provides telephony call control for a specific bearer including
    call state, signal strength, and call management.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BEARER_PROVIDER_NAME: True,
        CharacteristicName.BEARER_TECHNOLOGY: True,
        CharacteristicName.BEARER_UCI: False,
        CharacteristicName.BEARER_SIGNAL_STRENGTH: False,
        CharacteristicName.BEARER_SIGNAL_STRENGTH_REPORTING_INTERVAL: False,
        CharacteristicName.BEARER_URI_SCHEMES_SUPPORTED_LIST: False,
        CharacteristicName.BEARER_LIST_CURRENT_CALLS: False,
        CharacteristicName.CONTENT_CONTROL_ID: False,
        CharacteristicName.STATUS_FLAGS: False,
        CharacteristicName.CALL_CONTROL_POINT: False,
        CharacteristicName.CALL_CONTROL_POINT_OPTIONAL_OPCODES: False,
        CharacteristicName.CALL_STATE: False,
        CharacteristicName.CALL_FRIENDLY_NAME: False,
        CharacteristicName.INCOMING_CALL: False,
        CharacteristicName.INCOMING_CALL_TARGET_BEARER_URI: False,
        CharacteristicName.TERMINATION_REASON: False,
    }
