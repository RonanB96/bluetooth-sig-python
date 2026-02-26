"""Tests for automatic python_type resolution from generic parameters.

Verifies the H.1 auto-resolution mechanism:
  1. CodingTemplate.resolve_python_type() — introspects CodingTemplate[T_co]
  2. BaseCharacteristic._resolve_generic_python_type() — introspects BaseCharacteristic[T]
  3. Resolution chain: YAML → template → generic param → manual _python_type
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.templates import (
    EnumTemplate,
    ScaledUint16Template,
    Utf8StringTemplate,
)
from bluetooth_sig.gatt.characteristics.templates.base import CodingTemplate
from bluetooth_sig.gatt.characteristics.templates.numeric import Uint8Template
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ---------------------------------------------------------------------------
# Helpers — unique UUIDs for throwaway test classes
# ---------------------------------------------------------------------------
_UUID_COUNTER = 0xAA000000


def _next_uuid() -> BluetoothUUID:
    global _UUID_COUNTER  # noqa: PLW0603
    _UUID_COUNTER += 1
    return BluetoothUUID(f"{_UUID_COUNTER:08X}-0000-1000-8000-00805F9B34FB")


# ===================================================================
# Part 1: CodingTemplate.resolve_python_type()
# ===================================================================


class TestTemplateResolveType:
    """CodingTemplate.resolve_python_type() extracts T from CodingTemplate[T_co]."""

    def test_uint8_template_resolves_int(self) -> None:
        assert Uint8Template.resolve_python_type() is int

    def test_scaled_uint16_template_resolves_float(self) -> None:
        assert ScaledUint16Template.resolve_python_type() is float

    def test_utf8_string_template_resolves_str(self) -> None:
        assert Utf8StringTemplate.resolve_python_type() is str

    def test_enum_template_unbound_typevar_returns_none(self) -> None:
        """EnumTemplate[T] has an unbound TypeVar — should not resolve."""
        assert EnumTemplate.resolve_python_type() is None

    def test_base_coding_template_returns_none(self) -> None:
        """The abstract CodingTemplate itself has no concrete type arg."""
        assert CodingTemplate.resolve_python_type() is None

    def test_result_is_cached_per_class(self) -> None:
        """Calling twice should return the same cached result."""
        first = Uint8Template.resolve_python_type()
        second = Uint8Template.resolve_python_type()
        assert first is second is int


# ===================================================================
# Part 2: BaseCharacteristic._resolve_generic_python_type()
# ===================================================================


class _FloatChar(CustomBaseCharacteristic):
    """BaseCharacteristic[Any] (via Custom) then narrowed nowhere — should be None."""

    _info = CharacteristicInfo(uuid=_next_uuid(), name="FloatCustom")

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        return 0.0

    def _encode_value(self, data: float) -> bytearray:
        return bytearray()


class _ConcreteGenericChar(BaseCharacteristic[float]):
    """Directly parameterises BaseCharacteristic with float."""

    _characteristic_name = "Temperature"

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        return 0.0

    def _encode_value(self, data: float) -> bytearray:
        return bytearray()


class _AnyGenericChar(BaseCharacteristic[Any]):
    """BaseCharacteristic[Any] — should NOT resolve (Any is excluded)."""

    _characteristic_name = "Temperature"

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> Any:
        return None

    def _encode_value(self, data: Any) -> bytearray:
        return bytearray()


class TestGenericParamResolution:
    """BaseCharacteristic._resolve_generic_python_type() introspects BaseCharacteristic[T]."""

    def test_concrete_type_resolves(self) -> None:
        assert _ConcreteGenericChar._resolve_generic_python_type() is float

    def test_any_returns_none(self) -> None:
        assert _AnyGenericChar._resolve_generic_python_type() is None

    def test_custom_base_returns_none(self) -> None:
        """CustomBaseCharacteristic extends BaseCharacteristic[Any] — should not resolve."""
        assert CustomBaseCharacteristic._resolve_generic_python_type() is None

    def test_result_is_cached(self) -> None:
        first = _ConcreteGenericChar._resolve_generic_python_type()
        second = _ConcreteGenericChar._resolve_generic_python_type()
        assert first is second is float


# ===================================================================
# Part 3: End-to-end resolution chain
# ===================================================================


class _TemplateOnlyChar(CustomBaseCharacteristic):
    """Has a template (Uint8 → int) but no concrete generic param."""

    _info = CharacteristicInfo(uuid=_next_uuid(), name="TemplateOnly")
    _template = Uint8Template()

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        return 0

    def _encode_value(self, data: int) -> bytearray:
        return bytearray()


class _GenericBeatsTemplate(BaseCharacteristic[int]):
    """Generic param (int) should win over template (ScaledUint16 → float)."""

    _characteristic_name = "Battery Level"
    _template = ScaledUint16Template(scale_factor=0.01)  # type: ignore[assignment]

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        return 0

    def _encode_value(self, data: int) -> bytearray:
        return bytearray()


class _ManualOverrideChar(BaseCharacteristic[float]):
    """Manual _python_type (str) beats both generic (float) and template."""

    _characteristic_name = "Temperature"
    _python_type: type | str | None = str

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        return 0.0

    def _encode_value(self, data: float) -> bytearray:
        return bytearray()


class TestResolutionChain:
    """Full end-to-end resolution: YAML → template → generic → manual override."""

    def test_template_populates_python_type(self) -> None:
        """Template type flows into info.python_type when no generic param exists."""
        char = _TemplateOnlyChar()
        assert char.python_type is int

    def test_generic_param_overrides_template(self) -> None:
        """Generic param (int) overrides template (float) because it is more authoritative."""
        char = _GenericBeatsTemplate()
        assert char.python_type is int

    def test_manual_override_wins_over_all(self) -> None:
        """Explicit _python_type wins over both template and generic param."""
        char = _ManualOverrideChar()
        assert char.python_type is str


# ===================================================================
# Part 4: Spot-checks on real SIG characteristics
# ===================================================================


class TestRealCharacteristicResolution:
    """Verify representative SIG characteristics resolve python_type correctly."""

    def test_heart_rate_resolves_data_struct(self) -> None:
        from bluetooth_sig.gatt.characteristics.heart_rate_measurement import (
            HeartRateData,
            HeartRateMeasurementCharacteristic,
        )

        char = HeartRateMeasurementCharacteristic()
        assert char.python_type is HeartRateData

    def test_pushbutton_status_8_resolves_data_struct(self) -> None:
        from bluetooth_sig.gatt.characteristics.pushbutton_status_8 import (
            PushbuttonStatus8Characteristic,
            PushbuttonStatus8Data,
        )

        char = PushbuttonStatus8Characteristic()
        assert char.python_type is PushbuttonStatus8Data

    def test_fixed_string_8_resolves_str(self) -> None:
        from bluetooth_sig.gatt.characteristics.fixed_string_8 import (
            FixedString8Characteristic,
        )

        char = FixedString8Characteristic()
        assert char.python_type is str

    def test_temperature_resolves_float(self) -> None:
        from bluetooth_sig.gatt.characteristics.temperature import (
            TemperatureCharacteristic,
        )

        char = TemperatureCharacteristic()
        assert char.python_type is float

    def test_battery_level_resolves_int(self) -> None:
        from bluetooth_sig.gatt.characteristics.battery_level import (
            BatteryLevelCharacteristic,
        )

        char = BatteryLevelCharacteristic()
        # Generic param is int; template (PercentageTemplate) resolves float
        # but generic param wins.
        assert char.python_type is int
