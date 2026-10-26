"""GenericTelephoneBearer Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class GenericTelephoneBearerService(BaseGattService):
    """Generic Telephone Bearer Service implementation (0x184C).

    A generic instance of the Telephone Bearer Service providing
    a standardised telephony interface.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BEARER_PROVIDER_NAME: True,
        CharacteristicName.BEARER_TECHNOLOGY: True,
        CharacteristicName.BEARER_UCI: True,
        CharacteristicName.BEARER_SIGNAL_STRENGTH: False,
        CharacteristicName.BEARER_SIGNAL_STRENGTH_REPORTING_INTERVAL: False,
        CharacteristicName.BEARER_URI_SCHEMES_SUPPORTED_LIST: True,
        CharacteristicName.BEARER_LIST_CURRENT_CALLS: True,
        CharacteristicName.CONTENT_CONTROL_ID: True,
        CharacteristicName.STATUS_FLAGS: True,
        CharacteristicName.CALL_CONTROL_POINT: True,
        CharacteristicName.CALL_STATE: True,
        CharacteristicName.CALL_FRIENDLY_NAME: False,
        CharacteristicName.INCOMING_CALL: True,
        CharacteristicName.INCOMING_CALL_TARGET_BEARER_URI: False,
        CharacteristicName.TERMINATION_REASON: True,
    }
