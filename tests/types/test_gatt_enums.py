"""Tests for GATT enums and WIRE_TYPE_MAP functionality."""

from __future__ import annotations

from bluetooth_sig.types.gatt_enums import WIRE_TYPE_MAP


class TestWireTypeMap:
    """Test the WIRE_TYPE_MAP lookup table."""

    def test_utf16s_maps_to_str(self) -> None:
        """Test that utf16s maps to str."""
        assert WIRE_TYPE_MAP["utf16s"] is str

    def test_utf8s_maps_to_str(self) -> None:
        """Test that utf8s maps to str."""
        assert WIRE_TYPE_MAP["utf8s"] is str

    def test_integer_types(self) -> None:
        """Test that unsigned and signed integer wire types map to int."""
        for key in ("uint8", "uint16", "uint24", "uint32", "uint64", "sint8", "sint16", "sint24", "sint32", "sint64"):
            assert WIRE_TYPE_MAP[key] is int, f"{key} should map to int"

    def test_float_types(self) -> None:
        """Test that float wire types map to float."""
        for key in ("float32", "float64", "medfloat16", "medfloat32", "sfloat", "float"):
            assert WIRE_TYPE_MAP[key] is float, f"{key} should map to float"

    def test_boolean_type(self) -> None:
        """Test that boolean maps to bool."""
        assert WIRE_TYPE_MAP["boolean"] is bool

    def test_unknown_type_returns_none(self) -> None:
        """Test that unknown wire type strings return None via .get()."""
        assert WIRE_TYPE_MAP.get("unknown_type") is None
        assert WIRE_TYPE_MAP.get("") is None
        assert WIRE_TYPE_MAP.get("struct") is None

    def test_all_values_are_types(self) -> None:
        """Test that every value in the map is a Python type."""
        for key, val in WIRE_TYPE_MAP.items():
            assert isinstance(val, type), f"WIRE_TYPE_MAP[{key!r}] = {val!r} is not a type"
