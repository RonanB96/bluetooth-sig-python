"""Tests for bluetooth_sig.utils.values — to_primitive and is_struct_value."""

from __future__ import annotations

import enum
from datetime import datetime, timedelta

import msgspec
import pytest

from bluetooth_sig.utils.values import is_struct_value, to_primitive

# ── Test fixtures ────────────────────────────────────────────────────────────


class _Colour(enum.Enum):
    RED = 1
    GREEN = 2


class _Sensor(enum.IntEnum):
    TEMPERATURE = 0
    HUMIDITY = 1


class _Flags(enum.IntFlag):
    READ = 1
    WRITE = 2
    NOTIFY = 4


class _SampleStruct(msgspec.Struct):
    name: str
    value: int


class _ObjectWithName:
    """Non-enum object that happens to have a .name attribute."""

    name: str = "should_not_match"


# ── is_struct_value ──────────────────────────────────────────────────────────


class TestIsStructValue:
    """Tests for is_struct_value()."""

    def test_returns_true_for_struct(self) -> None:
        assert is_struct_value(_SampleStruct(name="x", value=1)) is True

    def test_returns_false_for_dict(self) -> None:
        assert is_struct_value({"name": "x", "value": 1}) is False

    def test_returns_false_for_none(self) -> None:
        assert is_struct_value(None) is False

    def test_returns_false_for_primitive(self) -> None:
        assert is_struct_value(42) is False
        assert is_struct_value("hello") is False

    def test_returns_false_for_dataclass_like(self) -> None:
        assert is_struct_value(_ObjectWithName()) is False


# ── to_primitive ─────────────────────────────────────────────────────────────


class TestToPrimitive:
    """Tests for to_primitive()."""

    # ── bool (must come before int) ──────────────────────────────────────

    def test_bool_true(self) -> None:
        assert to_primitive(True) is True

    def test_bool_false(self) -> None:
        assert to_primitive(False) is False

    # ── IntFlag → int ────────────────────────────────────────────────────

    def test_intflag_single(self) -> None:
        result = to_primitive(_Flags.READ)
        assert result == 1
        assert isinstance(result, int)

    def test_intflag_combined(self) -> None:
        result = to_primitive(_Flags.READ | _Flags.WRITE)
        assert result == 3
        assert isinstance(result, int)

    # ── Enum / IntEnum → name string ─────────────────────────────────────

    def test_enum_returns_name(self) -> None:
        assert to_primitive(_Colour.RED) == "RED"

    def test_intenum_returns_name(self) -> None:
        assert to_primitive(_Sensor.HUMIDITY) == "HUMIDITY"

    # ── plain int ────────────────────────────────────────────────────────

    def test_plain_int(self) -> None:
        result = to_primitive(42)
        assert result == 42
        assert type(result) is int

    def test_int_subclass_unwrapped(self) -> None:
        """An int-subclass that is NOT an enum should still return plain int."""

        class _CustomInt(int):
            pass

        result = to_primitive(_CustomInt(7))
        assert result == 7
        assert type(result) is int

    # ── float ────────────────────────────────────────────────────────────

    def test_float(self) -> None:
        assert to_primitive(3.14) == pytest.approx(3.14)

    # ── str passthrough ──────────────────────────────────────────────────

    def test_str(self) -> None:
        assert to_primitive("hello") == "hello"

    def test_empty_str(self) -> None:
        assert to_primitive("") == ""

    # ── fallback to str() ────────────────────────────────────────────────

    def test_datetime_falls_through(self) -> None:
        dt = datetime(2026, 1, 1, 12, 0, 0)
        assert to_primitive(dt) == str(dt)

    def test_timedelta_falls_through(self) -> None:
        td = timedelta(seconds=90)
        assert to_primitive(td) == str(td)

    def test_struct_falls_through(self) -> None:
        s = _SampleStruct(name="x", value=1)
        assert to_primitive(s) == str(s)

    # ── regression: object with .name must NOT be treated as enum ────────

    def test_object_with_name_attr_not_treated_as_enum(self) -> None:
        """Ensure non-enum objects with a .name attribute fall through to str()."""
        obj = _ObjectWithName()
        result = to_primitive(obj)
        assert result == str(obj)
        assert result != "should_not_match"
