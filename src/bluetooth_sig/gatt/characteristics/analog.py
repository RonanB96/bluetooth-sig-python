"""Analog characteristic (0x2A58)."""

from __future__ import annotations

from ...types import CharacteristicInfo
from ...types.uuid import BluetoothUUID
from .base import BaseCharacteristic, ValidationConfig
from .templates import Uint16Template


class AnalogCharacteristic(BaseCharacteristic[int]):
    """Analog characteristic (0x2A58).

    org.bluetooth.characteristic.analog

    Represents one analog signal value as an unsigned 16-bit integer.
    """

    _template = Uint16Template()
    expected_length = 2

    def __init__(
        self,
        info: CharacteristicInfo | None = None,
        validation: ValidationConfig | None = None,
    ) -> None:
        """Initialize with hardcoded info since this UUID is absent from the YAML submodule.

        Args:
            info: Override characteristic information.
            validation: Validation constraints configuration.

        """
        if info is None:
            info = CharacteristicInfo(
                uuid=BluetoothUUID("2A58"),
                name="Analog",
                id="org.bluetooth.characteristic.analog",
                unit="",
                python_type=int,
            )
        super().__init__(info=info, validation=validation)
