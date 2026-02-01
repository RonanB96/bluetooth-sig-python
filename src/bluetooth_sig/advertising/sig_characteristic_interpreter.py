"""SIG characteristic interpreter for standard service data.

Built-in interpreter that uses CharacteristicRegistry to parse SIG-standard
service data from BLE advertisements. Automatically handles any UUID
registered in CharacteristicRegistry.

Based on Bluetooth SIG GATT Specification Supplement for characteristic
data formats.
"""

from __future__ import annotations

import logging
from typing import Any

import msgspec

from bluetooth_sig.advertising.base import (
    AdvertisingData,
    DataSource,
    InterpreterInfo,
    PayloadInterpreter,
)
from bluetooth_sig.advertising.exceptions import AdvertisingParseError
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class SIGCharacteristicData(msgspec.Struct, kw_only=True, frozen=True):
    """Parsed SIG characteristic data from service data advertisement.

    Attributes:
        uuid: The characteristic UUID that was parsed.
        characteristic_name: Human-readable characteristic name.
        parsed_value: The parsed characteristic value (type varies by characteristic).

    """

    uuid: BluetoothUUID
    characteristic_name: str
    # Any is justified: Runtime UUID dispatch means return type varies per characteristic
    parsed_value: Any


class SIGCharacteristicInterpreter(PayloadInterpreter[SIGCharacteristicData]):
    """Interprets service data using SIG characteristic definitions.

    Automatically handles any UUID registered in CharacteristicRegistry.
    No encryption support (SIG characteristics are not encrypted in service data).

    This interpreter checks service data UUIDs against the CharacteristicRegistry
    and parses the payload using the corresponding characteristic class.

    Example:
        from bluetooth_sig.advertising.base import AdvertisingData

        interpreter = SIGCharacteristicInterpreter("AA:BB:CC:DD:EE:FF")
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        # Create advertising data from BLE packet
        ad_data = AdvertisingData(
            service_data={BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"): bytes([75])},
            rssi=-60,
        )

        try:
            data = interpreter.interpret(ad_data, state)
            print(f"Parsed: {data.parsed_value}")
        except AdvertisingParseError as e:
            print(f"Parse failed: {e}")

    """

    _info = InterpreterInfo(
        name="SIG Characteristic",
        data_source=DataSource.SERVICE,
    )
    _is_base_class = False

    @classmethod
    def supports(cls, advertising_data: AdvertisingData) -> bool:
        """Check if any service data UUID matches a registered characteristic.

        Args:
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            True if at least one service data UUID has a registered characteristic.

        """
        for uuid in advertising_data.service_data:
            if CharacteristicRegistry.get_characteristic_class_by_uuid(uuid) is not None:
                return True
        return False

    def interpret(
        self,
        advertising_data: AdvertisingData,
        state: DeviceAdvertisingState,
    ) -> SIGCharacteristicData:
        """Interpret service data using SIG characteristic definitions.

        Finds the first service data UUID that matches a registered characteristic
        and parses the payload using that characteristic class.

        Args:
            advertising_data: Complete advertising data from BLE packet.
            state: Current device advertising state (unused, no encryption).

        Returns:
            SIGCharacteristicData with parsed characteristic value.

        Raises:
            AdvertisingParseError: If no matching characteristic or parsing fails.

        """
        del state  # Required by interface but not used in this implementation
        for uuid, payload in advertising_data.service_data.items():
            char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(uuid)
            if char_class is None:
                continue

            try:
                char_instance = char_class()
                parsed_value = char_instance.parse_value(payload)

                return SIGCharacteristicData(
                    uuid=uuid,
                    characteristic_name=char_class.__name__,
                    parsed_value=parsed_value,
                )
            except Exception as e:
                logger.warning(
                    "Failed to parse SIG characteristic %s: %s",
                    char_class.__name__,
                    e,
                )
                raise AdvertisingParseError(
                    message=f"Failed to parse {char_class.__name__}: {e}",
                    raw_data=payload,
                    interpreter_name=self._info.name,
                ) from e

        # No matching characteristic found
        raise AdvertisingParseError(
            message="No matching SIG characteristic found in service data",
            interpreter_name=self._info.name,
        )
