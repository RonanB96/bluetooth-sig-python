"""IEEE floating-point templates for medical and standard float formats.

Covers IEEE11073FloatTemplate (SFLOAT 16-bit) and Float32Template (IEEE-754 32-bit).
"""

from __future__ import annotations

from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError
from ..utils import DataParser
from ..utils.extractors import (
    FLOAT32,
    UINT16,
    RawExtractor,
)
from ..utils.translators import (
    SFLOAT,
    SfloatTranslator,
)
from .base import CodingTemplate


class IEEE11073FloatTemplate(CodingTemplate[float]):
    """Template for IEEE 11073 SFLOAT format (16-bit medical device float)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def extractor(self) -> RawExtractor:
        """Get uint16 extractor for raw bits."""
        return UINT16

    @property
    def translator(self) -> SfloatTranslator:
        """Get SFLOAT translator."""
        return SFLOAT

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse IEEE 11073 SFLOAT format."""
        if validate and len(data) < offset + 2:
            raise InsufficientDataError("IEEE11073 SFLOAT", data[offset:], 2)
        raw = self.extractor.extract(data, offset)
        return self.translator.translate(raw)

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode value to IEEE 11073 SFLOAT format."""
        raw = self.translator.untranslate(value)
        return self.extractor.pack(raw)


class Float32Template(CodingTemplate[float]):
    """Template for IEEE-754 32-bit float parsing."""

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def extractor(self) -> RawExtractor:
        """Get float32 extractor."""
        return FLOAT32

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse IEEE-754 32-bit float."""
        if validate and len(data) < offset + 4:
            raise InsufficientDataError("float32", data[offset:], 4)
        return DataParser.parse_float32(data, offset)

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode float32 value to bytes."""
        return DataParser.encode_float32(float(value))
