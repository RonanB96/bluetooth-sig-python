"""Bearer URI Schemes Supported List characteristic (0x2BB6)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class BearerURISchemesCharacteristic(BaseCharacteristic[str]):
    """Bearer URI Schemes Supported List characteristic (0x2BB6).

    org.bluetooth.characteristic.bearer_uri_schemes_supported_list

    Bearer URI Schemes Supported List characteristic.
    """

    _characteristic_name = "Bearer URI Schemes Supported List"
    _template = Utf8StringTemplate()
    min_length = 0
