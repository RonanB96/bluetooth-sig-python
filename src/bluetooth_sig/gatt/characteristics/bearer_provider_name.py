"""Bearer Provider Name characteristic (0x2BB3)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class BearerProviderNameCharacteristic(BaseCharacteristic[str]):
    """Bearer Provider Name characteristic (0x2BB3).

    org.bluetooth.characteristic.bearer_provider_name

    Bearer Provider Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
