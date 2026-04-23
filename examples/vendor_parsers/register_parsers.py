"""Vendor/proprietary parser registration examples.

Demonstrates how to register custom parsers for non-SIG (proprietary) BLE
characteristic UUIDs using the bluetooth_sig runtime registration API.

Two real-world patterns are shown:

1. **Nordic LED Button Service (LBS)** — a well-known proprietary service from
   Nordic Semiconductor used in many nRF5 SDK examples.  Each characteristic
   carries a single byte: 0x00 = off/released, 0x01 = on/pressed.

2. **Govee-style thermometer** — a common 4-byte compound payload found in many
   low-cost Bluetooth thermometers and inspired by Govee device firmware.
   Layout: sint16 LE temperature (÷100 → °C), uint16 LE humidity (÷100 → %).

Running this script requires no BLE hardware; all payloads are simulated.

Usage::

    python -m examples.vendor_parsers.register_parsers
"""

from __future__ import annotations

import struct

import msgspec

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ---------------------------------------------------------------------------
# UUID constants — proprietary (non-SIG) identifiers
# ---------------------------------------------------------------------------

# Nordic Semiconductor LED Button Service characteristic UUIDs
# Source: nRF5 SDK / nRF Connect SDK ble_lbs example
NUS_LED_UUID = "00001525-1212-efde-1523-785feabcd123"
NUS_BUTTON_UUID = "00001524-1212-efde-1523-785feabcd123"

# Govee-style temperature + humidity UUID (vendor proprietary)
GOVEE_THERMO_UUID = "494e5445-4c4c-494e-5445-4c4c49000001"


# ---------------------------------------------------------------------------
# Nordic LED Button Service — LED state characteristic
# ---------------------------------------------------------------------------


class NordicLEDCharacteristic(CustomBaseCharacteristic):
    """Nordic LBS LED state: 1 byte, 0x00 = off, 0x01 = on."""

    expected_length: int = 1
    min_value: int = 0
    max_value: int = 1
    expected_type: type = int

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NUS_LED_UUID),
        name="Nordic LBS LED State",
        unit="",
        python_type=int,
    )

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> int:
        """Parse LED state byte (0 = off, 1 = on)."""
        return data[0]

    def _encode_value(self, data: int) -> bytearray:
        """Encode LED state to single byte."""
        return bytearray([data & 0x01])


# ---------------------------------------------------------------------------
# Nordic LED Button Service — button state characteristic
# ---------------------------------------------------------------------------


class NordicButtonCharacteristic(CustomBaseCharacteristic):
    """Nordic LBS button state: 1 byte, 0x00 = released, 0x01 = pressed."""

    expected_length: int = 1
    min_value: int = 0
    max_value: int = 1
    expected_type: type = int

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NUS_BUTTON_UUID),
        name="Nordic LBS Button State",
        unit="",
        python_type=int,
    )

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> int:
        """Parse button state byte (0 = released, 1 = pressed)."""
        return data[0]

    def _encode_value(self, data: int) -> bytearray:
        """Encode button state to single byte."""
        return bytearray([data & 0x01])


# ---------------------------------------------------------------------------
# Govee-style thermometer — compound temperature + humidity characteristic
# ---------------------------------------------------------------------------


class GoveeThermometerReading(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed Govee-style temperature and humidity reading.

    Attributes:
        temperature: Temperature in degrees Celsius (resolution 0.01 °C).
        humidity: Relative humidity in percent (resolution 0.01 %).
    """

    temperature: float
    humidity: float


class GoveeThermometerCharacteristic(CustomBaseCharacteristic):
    """Govee-style thermometer: 4-byte payload with temperature and humidity.

    Payload layout (little-endian):
        Bytes 0-1: sint16  temperature raw value (divide by 100 → °C)
        Bytes 2-3: uint16  humidity raw value   (divide by 100 → %)
    """

    expected_length: int = 4

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(GOVEE_THERMO_UUID),
        name="Govee Thermometer Reading",
        unit="°C / %",
        python_type=float,
    )

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> GoveeThermometerReading:
        """Parse 4-byte Govee thermometer payload."""
        temp_raw, hum_raw = struct.unpack_from("<hH", data, 0)
        return GoveeThermometerReading(
            temperature=round(temp_raw / 100.0, 2),
            humidity=round(hum_raw / 100.0, 2),
        )

    def _encode_value(self, data: GoveeThermometerReading) -> bytearray:
        """Encode temperature and humidity to 4-byte Govee payload."""
        temp_raw = round(data.temperature * 100)
        hum_raw = round(data.humidity * 100)
        return bytearray(struct.pack("<hH", temp_raw, hum_raw))


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------


def register_all(translator: BluetoothSIGTranslator | None = None) -> BluetoothSIGTranslator:
    """Register all vendor characteristic classes with a translator instance.

    Explicitly registers each vendor characteristic class so that the
    translator can dispatch by UUID.  Using ``override=True`` makes this
    call idempotent — safe to call multiple times (e.g. in tests).

    Args:
        translator: Existing translator to use, or None to use the singleton.

    Returns:
        The translator instance used for registration.
    """
    if translator is None:
        translator = BluetoothSIGTranslator.get_instance()

    registrations: list[tuple[str, type[CustomBaseCharacteristic]]] = [
        (NUS_LED_UUID, NordicLEDCharacteristic),
        (NUS_BUTTON_UUID, NordicButtonCharacteristic),
        (GOVEE_THERMO_UUID, GoveeThermometerCharacteristic),
    ]
    for uuid, cls in registrations:
        translator.register_custom_characteristic_class(uuid, cls, override=True)

    return translator


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run a short demo parsing simulated payloads with registered vendor parsers."""
    translator = register_all()

    print("=== Vendor Parser Demo ===\n")

    # --- Nordic LED ---
    led_on_payload = bytearray([0x01])
    led_result = translator.parse_characteristic(NUS_LED_UUID, led_on_payload)
    print(f"[Nordic LED] payload={led_on_payload.hex()!r}  →  LED state: {led_result} (1 = on)")

    led_off_payload = bytearray([0x00])
    led_result = translator.parse_characteristic(NUS_LED_UUID, led_off_payload)
    print(f"[Nordic LED] payload={led_off_payload.hex()!r}  →  LED state: {led_result} (0 = off)")

    # --- Nordic Button ---
    btn_pressed_payload = bytearray([0x01])
    btn_result = translator.parse_characteristic(NUS_BUTTON_UUID, btn_pressed_payload)
    print(f"[Nordic Button] payload={btn_pressed_payload.hex()!r}  →  Button: {btn_result} (1 = pressed)")

    # --- Govee thermometer: 22.50 °C, 65.10 % ---
    # temp_raw = 2250, hum_raw = 6510
    govee_payload = bytearray(struct.pack("<hH", 2250, 6510))
    govee_result = translator.parse_characteristic(GOVEE_THERMO_UUID, govee_payload)
    print(
        f"[Govee Thermo] payload={govee_payload.hex()!r}  →  "
        f"Temperature: {govee_result.temperature} °C, Humidity: {govee_result.humidity} %"
    )

    print("\nAll vendor parsers registered and working.")


if __name__ == "__main__":
    main()
