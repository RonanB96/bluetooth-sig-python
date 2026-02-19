"""Tests for Indoor Positioning AD type decode (AD 0x25, CSS Part A §1.14).

Tests cover:
- WGS84 coordinate decoding (latitude, longitude)
- Local coordinate decoding (north, east)
- Optional fields: tx_power, floor_number, altitude, uncertainty
- Flag-driven field presence/absence
- Truncated and empty data handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types.advertising.indoor_positioning import (
    LOCATION_FLAGS_MASK,
    IndoorPositioningConfig,
    IndoorPositioningData,
)


@dataclass
class ADTypeTestData:
    """Test data for AD type decode — mirrors CharacteristicTestData."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


class TestIndoorPositioningDecode:
    """Tests for IndoorPositioningData.decode()."""

    @pytest.fixture
    def valid_test_data(self) -> list[ADTypeTestData]:
        """Standard decode scenarios covering major flag combinations."""
        return [
            ADTypeTestData(
                input_data=bytearray([0x00]),
                expected_value=IndoorPositioningData(
                    config=IndoorPositioningConfig(0),
                    is_local_coordinates=False,
                ),
                description="Config-only, no optional fields (WGS84 mode)",
            ),
            ADTypeTestData(
                input_data=bytearray(
                    [
                        0x06,  # LATITUDE_PRESENT | LONGITUDE_PRESENT
                        0x40,
                        0x42,
                        0x0F,
                        0x00,  # latitude  = 1_000_000 (little-endian)
                        0x80,
                        0x84,
                        0x1E,
                        0x00,  # longitude = 2_000_000
                        0xAA,  # uncertainty
                    ]
                ),
                expected_value=IndoorPositioningData(
                    config=IndoorPositioningConfig.LATITUDE_PRESENT | IndoorPositioningConfig.LONGITUDE_PRESENT,
                    is_local_coordinates=False,
                    latitude=1_000_000,
                    longitude=2_000_000,
                    uncertainty=0xAA,
                ),
                description="WGS84 lat+lon with uncertainty",
            ),
            ADTypeTestData(
                input_data=bytearray(
                    [
                        0x19,  # COORDINATE_SYSTEM_LOCAL | LOCAL_NORTH_PRESENT | LOCAL_EAST_PRESENT
                        0xE8,
                        0x03,  # local_north = 1000 (0.01 m units)
                        0xD0,
                        0x07,  # local_east  = 2000
                        0x55,  # uncertainty
                    ]
                ),
                expected_value=IndoorPositioningData(
                    config=(
                        IndoorPositioningConfig.COORDINATE_SYSTEM_LOCAL
                        | IndoorPositioningConfig.LOCAL_NORTH_PRESENT
                        | IndoorPositioningConfig.LOCAL_EAST_PRESENT
                    ),
                    is_local_coordinates=True,
                    local_north=1000,
                    local_east=2000,
                    uncertainty=0x55,
                ),
                description="Local coordinate system with north+east and uncertainty",
            ),
            ADTypeTestData(
                input_data=bytearray(
                    [
                        0xE6,  # LAT | LON | TX_POWER | FLOOR | ALTITUDE (WGS84)
                        0x60,
                        0x79,
                        0xFE,
                        0xFF,  # latitude  = -100_000 (signed)
                        0xC0,
                        0xF2,
                        0xFC,
                        0xFF,  # longitude = -200_000 (signed)
                        0xEC,  # tx_power  = -20 dBm (signed)
                        0x14,  # floor_number = 20 (offset -20 → floor 0)
                        0x10,
                        0x27,  # altitude = 10000 (0.01 m units)
                        0x42,  # uncertainty
                    ]
                ),
                expected_value=IndoorPositioningData(
                    config=IndoorPositioningConfig(0xE6),
                    is_local_coordinates=False,
                    latitude=-100_000,
                    longitude=-200_000,
                    tx_power=-20,
                    floor_number=20,
                    altitude=10000,
                    uncertainty=0x42,
                ),
                description="WGS84 with all optional fields and negative coordinates",
            ),
        ]

    def test_decode_valid_data(self, valid_test_data: list[ADTypeTestData]) -> None:
        """Decode each valid test case and verify all fields match."""
        for case in valid_test_data:
            result = IndoorPositioningData.decode(case.input_data)
            assert result == case.expected_value, f"Failed: {case.description}"

    def test_decode_wgs84_latitude_only(self) -> None:
        """Decode WGS84 payload with only latitude present (no longitude)."""
        data = bytearray(
            [
                0x02,  # LATITUDE_PRESENT only
                0x00,
                0xE1,
                0xF5,
                0x05,  # latitude = 100_000_000
                0x80,  # uncertainty
            ]
        )
        result = IndoorPositioningData.decode(data)

        assert result.is_local_coordinates is False
        assert result.latitude == 100_000_000
        assert result.longitude is None
        assert result.uncertainty == 0x80

    def test_decode_local_north_only(self) -> None:
        """Decode local coordinate payload with only north present."""
        data = bytearray(
            [
                0x09,  # COORDINATE_SYSTEM_LOCAL | LOCAL_NORTH_PRESENT
                0x01,
                0x00,  # local_north = 1
                0x00,  # uncertainty
            ]
        )
        result = IndoorPositioningData.decode(data)

        assert result.is_local_coordinates is True
        assert result.local_north == 1
        assert result.local_east is None
        assert result.uncertainty == 0x00

    def test_decode_tx_power_only(self) -> None:
        """Decode payload with only tx_power present — no location, no uncertainty."""
        data = bytearray([0x20, 0xF6])  # TX_POWER_PRESENT, tx_power = -10 dBm
        result = IndoorPositioningData.decode(data)

        assert result.tx_power == -10
        assert result.latitude is None
        assert result.uncertainty is None

    def test_decode_floor_number_only(self) -> None:
        """Decode payload with only floor_number present."""
        data = bytearray([0x40, 0xFF])  # FLOOR_NUMBER_PRESENT, floor = 255
        result = IndoorPositioningData.decode(data)

        assert result.floor_number == 255
        assert result.altitude is None

    def test_decode_altitude_only(self) -> None:
        """Decode payload with only altitude present."""
        data = bytearray([0x80, 0x00, 0x00])  # ALTITUDE_PRESENT, altitude = 0
        result = IndoorPositioningData.decode(data)

        assert result.altitude == 0

    def test_decode_uncertainty_absent_when_no_location_flags(self) -> None:
        """Uncertainty byte is skipped when no location-bearing flags are set.

        Even if extra bytes exist after the last field, uncertainty is only
        parsed when LOCATION_FLAGS_MASK bits are present.
        """
        # TX_POWER + FLOOR + ALTITUDE only — no lat/lon/north/east
        data = bytearray([0xE0, 0x05, 0x0A, 0x10, 0x27, 0xFF])
        result = IndoorPositioningData.decode(data)

        assert result.tx_power == 5
        assert result.floor_number == 10
        assert result.altitude == 10000
        assert result.uncertainty is None  # trailing 0xFF ignored

    def test_decode_uncertainty_absent_when_data_exhausted(self) -> None:
        """Uncertainty byte omitted when payload ends before it.

        Latitude present → uncertainty expected, but payload is exactly
        4 bytes for the coordinate with no trailing uncertainty byte.
        """
        data = bytearray(
            [
                0x02,  # LATITUDE_PRESENT
                0x40,
                0x42,
                0x0F,
                0x00,  # latitude = 1_000_000
            ]
        )
        result = IndoorPositioningData.decode(data)

        assert result.latitude == 1_000_000
        assert result.uncertainty is None


class TestIndoorPositioningErrors:
    """Error-path tests for IndoorPositioningData.decode()."""

    def test_decode_empty_data_raises(self) -> None:
        """Empty bytearray raises InsufficientDataError — no config byte."""
        with pytest.raises(InsufficientDataError):
            IndoorPositioningData.decode(bytearray())

    def test_decode_truncated_latitude_raises(self) -> None:
        """Config says latitude present but only 2 of 4 bytes available."""
        data = bytearray([0x02, 0x01, 0x02])  # LATITUDE_PRESENT + 2 bytes
        with pytest.raises(InsufficientDataError):
            IndoorPositioningData.decode(data)

    def test_decode_truncated_longitude_raises(self) -> None:
        """Longitude flag set but no bytes follow latitude."""
        data = bytearray(
            [
                0x06,  # LAT + LON present
                0x40,
                0x42,
                0x0F,
                0x00,  # latitude OK
                0x01,  # only 1 byte for longitude (need 4)
            ]
        )
        with pytest.raises(InsufficientDataError):
            IndoorPositioningData.decode(data)

    def test_decode_truncated_local_north_raises(self) -> None:
        """Local north flag set but only 1 byte available (need 2)."""
        data = bytearray([0x09, 0xFF])  # LOCAL + NORTH_PRESENT + 1 byte
        with pytest.raises(InsufficientDataError):
            IndoorPositioningData.decode(data)

    def test_decode_truncated_altitude_raises(self) -> None:
        """Altitude flag set but only 1 byte available (need 2)."""
        data = bytearray([0x80, 0x01])  # ALTITUDE_PRESENT + 1 byte
        with pytest.raises(InsufficientDataError):
            IndoorPositioningData.decode(data)


class TestIndoorPositioningConfig:
    """Tests for the IndoorPositioningConfig IntFlag."""

    def test_config_round_trip(self) -> None:
        """IntFlag value round-trips through int conversion."""
        flags = (
            IndoorPositioningConfig.LATITUDE_PRESENT
            | IndoorPositioningConfig.TX_POWER_PRESENT
            | IndoorPositioningConfig.ALTITUDE_PRESENT
        )
        assert IndoorPositioningConfig(int(flags)) == flags

    def test_location_flags_mask_covers_all_coordinate_bits(self) -> None:
        """LOCATION_FLAGS_MASK includes all four coordinate-bearing flags."""
        assert LOCATION_FLAGS_MASK & IndoorPositioningConfig.LATITUDE_PRESENT
        assert LOCATION_FLAGS_MASK & IndoorPositioningConfig.LONGITUDE_PRESENT
        assert LOCATION_FLAGS_MASK & IndoorPositioningConfig.LOCAL_NORTH_PRESENT
        assert LOCATION_FLAGS_MASK & IndoorPositioningConfig.LOCAL_EAST_PRESENT
        # Non-coordinate flags must not be in the mask
        assert not (LOCATION_FLAGS_MASK & IndoorPositioningConfig.TX_POWER_PRESENT)
        assert not (LOCATION_FLAGS_MASK & IndoorPositioningConfig.FLOOR_NUMBER_PRESENT)
        assert not (LOCATION_FLAGS_MASK & IndoorPositioningConfig.ALTITUDE_PRESENT)

    def test_coordinate_system_local_is_bit_zero(self) -> None:
        """COORDINATE_SYSTEM_LOCAL is bit 0 per CSS Part A §1.14."""
        assert IndoorPositioningConfig.COORDINATE_SYSTEM_LOCAL == 0x01
