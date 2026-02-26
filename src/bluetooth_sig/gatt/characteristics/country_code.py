"""Country Code characteristic (0x2C13)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class CountryCodeCharacteristic(BaseCharacteristic[int]):
    """Country Code characteristic (0x2C13).

    org.bluetooth.characteristic.country_code

    ISO 3166-1 numeric country code.
    """

    _template = Uint16Template()
