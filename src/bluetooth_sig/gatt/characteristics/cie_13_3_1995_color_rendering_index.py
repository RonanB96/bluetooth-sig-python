"""CIE 13.3-1995 Color Rendering Index characteristic (0x2AE7)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class CIE133ColorRenderingIndexCharacteristic(BaseCharacteristic[int]):
    """CIE 13.3-1995 Color Rendering Index characteristic (0x2AE7).

    org.bluetooth.characteristic.cie_13.3-1995_color_rendering_index

    Unitless color rendering index (CRI) value.
    M=1, d=0, b=0 — no scaling; plain signed 8-bit integer.
    Range: -128 to 100.
    A value of 127 represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 127).
    """

    _characteristic_name = "CIE 13.3-1995 Color Rendering Index"
    _template = Sint8Template()
