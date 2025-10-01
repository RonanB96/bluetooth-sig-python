"""UV Index characteristic implementation."""

from dataclasses import dataclass

from .templates import SimpleUint8Characteristic


@dataclass
class UVIndexCharacteristic(SimpleUint8Characteristic):
    """UV Index characteristic."""

    _characteristic_name: str = "UV Index"
    # YAML provides uint8 -> int, which is correct for UV Index values (0-11+ scale)
