from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementContextCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)
from bluetooth_sig.stream import BufferStats, DependencyPairingBuffer


def _glucose_measurement_bytes(seq: int) -> bytes:
    # Minimal payload resembling tests elsewhere: flags + seq + timestamp (7 bytes) + glucose (2 bytes)
    return bytes(
        [
            0x00,  # flags: no optional fields (unit default)
            seq & 0xFF,
            (seq >> 8) & 0xFF,  # sequence
            0xE8,
            0x07,
            0x03,
            0x0F,
            0x0E,
            0x1E,  # timestamp (2024-03-15 14:30)
            0x2D,  # seconds
            0x80,
            0x17,  # glucose SFLOAT 120.0 (as used in project tests)
        ]
    )


def _glucose_context_bytes(seq: int) -> bytes:
    # Minimal payload: flags + seq
    return bytes([0x00, seq & 0xFF, (seq >> 8) & 0xFF])


def test_glucose_pairing_out_of_order() -> None:
    translator = BluetoothSIGTranslator()

    gm_uuid = str(GlucoseMeasurementCharacteristic().uuid)
    gmc_uuid = str(GlucoseMeasurementContextCharacteristic().uuid)

    paired: list[dict[str, Any]] = []

    def group_key(uuid: str, parsed: Any) -> int:
        # For glucose measurement, extract sequence number from the parsed value
        return int(parsed.sequence_number)

    def on_pair(results: dict[str, Any]) -> None:
        paired.append(results)

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={gm_uuid, gmc_uuid},
        group_key=group_key,
        on_pair=on_pair,
    )

    # Out of order: context first, then measurement
    buf.ingest(gmc_uuid, _glucose_context_bytes(42))
    buf.ingest(gm_uuid, _glucose_measurement_bytes(42))

    assert len(paired) == 1
    results = paired[0]
    assert gm_uuid in results and gmc_uuid in results
    gm = results[gm_uuid]
    gmc = results[gmc_uuid]
    # Parsing succeeded (no exceptions raised), values are data objects directly
    assert gm is not None and gmc is not None
    assert gm.sequence_number == 42
    assert gmc.sequence_number == 42


def test_glucose_missing_counterpart_no_callback() -> None:
    translator = BluetoothSIGTranslator()
    gm_uuid = str(GlucoseMeasurementCharacteristic().uuid)
    gmc_uuid = str(GlucoseMeasurementContextCharacteristic().uuid)

    called = False

    def group_key(uuid: str, parsed: Any) -> int:
        # For glucose measurement, extract sequence number from the parsed value
        return int(parsed.sequence_number)

    def on_pair(_results: dict[str, Any]) -> None:
        nonlocal called
        called = True

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={gm_uuid, gmc_uuid},
        group_key=group_key,
        on_pair=on_pair,
    )

    # Only one side ingested
    buf.ingest(gm_uuid, _glucose_measurement_bytes(7))
    assert called is False


def test_glucose_mismatched_sequence_numbers_callback_validation() -> None:
    """Demonstrate that sequence_number validation is now caller's responsibility."""
    translator = BluetoothSIGTranslator()
    gm_uuid = str(GlucoseMeasurementCharacteristic().uuid)
    gmc_uuid = str(GlucoseMeasurementContextCharacteristic().uuid)

    def group_key(_uuid: str, _parsed: Any) -> str:
        # Force same group for both notifications regardless of seq to trigger batch
        return "force-same"

    def on_pair(results: dict[str, Any]) -> None:
        # User implements validation in callback
        gm = results[gm_uuid]
        gmc = results[gmc_uuid]
        if gm.sequence_number != gmc.sequence_number:
            raise ValueError(
                f"Glucose pairing validation failed: "
                f"measurement seq={gm.sequence_number}, "
                f"context seq={gmc.sequence_number}"
            )

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={gm_uuid, gmc_uuid},
        group_key=group_key,
        on_pair=on_pair,
    )

    buf.ingest(gm_uuid, _glucose_measurement_bytes(1))
    with pytest.raises(ValueError, match="Glucose pairing validation failed"):
        buf.ingest(gmc_uuid, _glucose_context_bytes(99))


def test_generic_reuse_with_synthetic_key() -> None:
    translator = BluetoothSIGTranslator()
    temp_uuid = str(TemperatureCharacteristic().uuid)
    humid_uuid = str(HumidityCharacteristic().uuid)

    # Simple fixed grouping key for a made-up data stream (e.g., one device/topic)
    def group_key(_uuid: str, _parsed: Any) -> str:
        return "room-1"

    captured: list[dict[str, Any]] = []

    def on_pair(results: dict[str, Any]) -> None:
        captured.append(results)

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={temp_uuid, humid_uuid},
        group_key=group_key,
        on_pair=on_pair,
    )

    # Minimal bytes as used in examples (10°C and 50% RH)
    temp_bytes = bytes([0x0A, 0x00])
    humid_bytes = bytes([0x32, 0x00])

    # Out of order
    buf.ingest(humid_uuid, humid_bytes)
    buf.ingest(temp_uuid, temp_bytes)

    assert len(captured) == 1
    results = captured[0]
    assert temp_uuid in results and humid_uuid in results
    # Values are parsed successfully (no exceptions raised during parsing)
    assert isinstance(results[temp_uuid], (int, float))
    assert isinstance(results[humid_uuid], (int, float))


def test_blood_pressure_pairing_multiple_sessions() -> None:
    """Blood Pressure pairing groups interleaved notifications from multiple measurement sessions.

    During a BP measurement, intermediate cuff pressures arrive repeatedly
    as the cuff inflates, then the final measurement arrives. If multiple sessions
    overlap or you have multiple devices, you need to pair notifications by timestamp.
    Without the buffer, you'd have to manually track which ICP belongs to which final measurement.
    """
    from datetime import datetime

    from bluetooth_sig.gatt.characteristics import BloodPressureMeasurementCharacteristic
    from bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure import IntermediateCuffPressureCharacteristic

    translator = BluetoothSIGTranslator()
    bpm_uuid = str(BloodPressureMeasurementCharacteristic().uuid)
    icp_uuid = str(IntermediateCuffPressureCharacteristic().uuid)

    sessions: list[dict[str, Any]] = []

    def group_key(_uuid: str, parsed: Any) -> datetime:
        # Group by timestamp - notifications with same timestamp are from same session
        ts = parsed.optional_fields.timestamp
        if ts is not None:
            assert isinstance(ts, datetime)
            return ts
        raise ValueError("Test requires timestamp for grouping")

    def on_pair(results: dict[str, Any]) -> None:
        sessions.append(results)

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={bpm_uuid, icp_uuid},
        group_key=group_key,
        on_pair=on_pair,
    )

    # Simulate TWO interleaved measurement sessions arriving out of order
    # Session 1: 10:00 timestamp
    # Session 2: 10:05 timestamp

    # ICP from session 1 (arrives first during inflation)
    icp1_bytes = bytes(
        [0x02, 80, 128, 0xFF, 0x07, 0xFF, 0x07, 0xE8, 0x07, 0x0B, 0x04, 0x0A, 0x00, 0x00]
    )  # flags=0x02 (timestamp, mmHg), pressure=80, timestamp=2024-11-04 10:00:00

    # Final BP from session 2 (arrives while session 1 still inflating!)
    bpm2_bytes = bytes(
        [0x02, 130, 128, 85, 128, 105, 128, 0xE8, 0x07, 0x0B, 0x04, 0x0A, 0x05, 0x00]
    )  # flags=0x02, 130/85/105, timestamp=2024-11-04 10:05:00

    # ICP from session 2 (arrived earlier during its inflation)
    icp2_bytes = bytes(
        [0x02, 90, 128, 0xFF, 0x07, 0xFF, 0x07, 0xE8, 0x07, 0x0B, 0x04, 0x0A, 0x05, 0x00]
    )  # pressure=90, timestamp=2024-11-04 10:05:00

    # Final BP from session 1 (arrives last)
    bpm1_bytes = bytes(
        [0x02, 120, 128, 80, 128, 100, 128, 0xE8, 0x07, 0x0B, 0x04, 0x0A, 0x00, 0x00]
    )  # 120/80/100, timestamp=2024-11-04 10:00:00

    # Notifications arrive completely interleaved - pairing buffer sorts it out
    buf.ingest(icp_uuid, icp1_bytes)  # Session 1 ICP (10:00) - buffered, waiting for BPM
    assert len(sessions) == 0  # No complete pairs yet

    buf.ingest(bpm_uuid, bpm2_bytes)  # Session 2 BPM (10:05) - buffered, waiting for ICP
    assert len(sessions) == 0  # Still no complete pairs

    buf.ingest(icp_uuid, icp2_bytes)  # Session 2 ICP (10:05) - triggers session 2 callback
    assert len(sessions) == 1  # Session 2 now complete

    buf.ingest(bpm_uuid, bpm1_bytes)  # Session 1 BPM (10:00) - triggers session 1 callback
    assert len(sessions) == 2  # Both sessions complete

    # Session 2 completed first (10:05 timestamp)
    session2 = sessions[0]
    assert session2[bpm_uuid].systolic == 130.0
    assert session2[bpm_uuid].optional_fields.timestamp.hour == 10
    assert session2[bpm_uuid].optional_fields.timestamp.minute == 5
    assert session2[icp_uuid].current_cuff_pressure == 90.0
    assert session2[icp_uuid].optional_fields.timestamp.hour == 10
    assert session2[icp_uuid].optional_fields.timestamp.minute == 5

    # Session 1 completed second (10:00 timestamp)
    session1 = sessions[1]
    assert session1[bpm_uuid].systolic == 120.0
    assert session1[bpm_uuid].optional_fields.timestamp.hour == 10
    assert session1[bpm_uuid].optional_fields.timestamp.minute == 0
    assert session1[icp_uuid].current_cuff_pressure == 80.0
    assert session1[icp_uuid].optional_fields.timestamp.hour == 10
    assert session1[icp_uuid].optional_fields.timestamp.minute == 0


# ---------------------------------------------------------------------------
# TTL eviction tests
# ---------------------------------------------------------------------------


def _make_ttl_buffer(
    *,
    max_age_seconds: float,
    clock: Any,
    paired: list[dict[str, Any]],
) -> tuple[DependencyPairingBuffer, str, str]:
    """Create a temperature+humidity buffer with injectable clock for TTL tests."""
    translator = BluetoothSIGTranslator()
    temp_uuid = str(TemperatureCharacteristic().uuid)
    humid_uuid = str(HumidityCharacteristic().uuid)

    buf = DependencyPairingBuffer(
        translator=translator,
        required_uuids={temp_uuid, humid_uuid},
        group_key=lambda _uuid, _parsed: "room-1",
        on_pair=paired.append,
        max_age_seconds=max_age_seconds,
        clock=clock,
    )
    return buf, temp_uuid, humid_uuid


class TestTTLEviction:
    """TTL-based eviction of stale incomplete groups."""

    def test_stale_group_evicted_before_completion(self) -> None:
        """A group that exceeds max_age_seconds is evicted on next ingest."""
        current_time = 0.0

        def clock() -> float:
            return current_time

        paired: list[dict[str, Any]] = []
        buf, temp_uuid, _humid_uuid = _make_ttl_buffer(
            max_age_seconds=10.0,
            clock=clock,
            paired=paired,
        )

        # Ingest first half at t=0
        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
        assert buf.stats().pending == 1

        # Advance past TTL
        current_time = 11.0

        # Ingest something — eviction runs first, removing the stale group
        buf.ingest(temp_uuid, bytes([0x14, 0x00]))
        assert buf.stats().pending == 1  # new group, old one evicted
        assert buf.stats().evicted == 1
        assert len(paired) == 0  # never completed

    def test_fresh_group_not_evicted(self) -> None:
        """Groups within max_age_seconds are preserved."""
        current_time = 0.0

        def clock() -> float:
            return current_time

        paired: list[dict[str, Any]] = []
        buf, temp_uuid, humid_uuid = _make_ttl_buffer(
            max_age_seconds=10.0,
            clock=clock,
            paired=paired,
        )

        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))

        # Advance but stay within TTL
        current_time = 5.0
        buf.ingest(humid_uuid, bytes([0x32, 0x00]))

        assert len(paired) == 1
        assert buf.stats().evicted == 0
        assert buf.stats().completed == 1

    def test_multiple_groups_selective_eviction(self) -> None:
        """Only groups exceeding TTL are evicted; fresh groups remain."""
        current_time = 0.0

        def clock() -> float:
            return current_time

        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        paired: list[dict[str, Any]] = []

        # Mutable group ID — set before each ingest to control grouping
        current_group: list[str] = ["A"]

        def group_key(_uuid: str, _parsed: Any) -> str:
            return current_group[0]

        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=group_key,
            on_pair=paired.append,
            max_age_seconds=10.0,
            clock=clock,
        )

        # Group A at t=0
        current_group[0] = "A"
        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
        assert buf.stats().pending == 1

        # Group B at t=8
        current_time = 8.0
        current_group[0] = "B"
        buf.ingest(temp_uuid, bytes([0x14, 0x00]))
        assert buf.stats().pending == 2

        # Advance to t=11 — group A is stale (age=11), group B is fresh (age=3)
        # Complete group B with humidity
        current_time = 11.0
        current_group[0] = "B"
        buf.ingest(humid_uuid, bytes([0x32, 0x00]))

        assert buf.stats().evicted == 1  # group A evicted
        assert buf.stats().completed == 1  # group B completed
        assert buf.stats().pending == 0

    def test_exact_boundary_evicted(self) -> None:
        """A group at exactly max_age_seconds is evicted (<=, not <)."""
        current_time = 0.0

        def clock() -> float:
            return current_time

        paired: list[dict[str, Any]] = []
        buf, temp_uuid, _humid_uuid = _make_ttl_buffer(
            max_age_seconds=10.0,
            clock=clock,
            paired=paired,
        )

        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))

        # Advance to exactly TTL boundary
        current_time = 10.0
        buf.ingest(temp_uuid, bytes([0x14, 0x00]))

        assert buf.stats().evicted == 1


class TestBufferStats:
    """BufferStats tracking across operations."""

    def test_initial_stats_all_zero(self) -> None:
        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=lambda _u, _p: "g",
            on_pair=lambda _r: None,
        )

        s = buf.stats()
        assert s == BufferStats(pending=0, completed=0, evicted=0)

    def test_pending_increments_on_partial(self) -> None:
        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=lambda _u, _p: "g",
            on_pair=lambda _r: None,
        )

        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
        assert buf.stats().pending == 1
        assert buf.stats().completed == 0

    def test_completed_increments_on_pair(self) -> None:
        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        paired: list[dict[str, Any]] = []
        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=lambda _u, _p: "g",
            on_pair=paired.append,
        )

        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
        buf.ingest(humid_uuid, bytes([0x32, 0x00]))

        s = buf.stats()
        assert s.pending == 0
        assert s.completed == 1
        assert s.evicted == 0

    def test_stats_accumulate_over_multiple_pairs(self) -> None:
        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=lambda _u, _p: "g",
            on_pair=lambda _r: None,
        )

        for _ in range(3):
            buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
            buf.ingest(humid_uuid, bytes([0x32, 0x00]))

        assert buf.stats().completed == 3
        assert buf.stats().pending == 0

    def test_stats_frozen_struct(self) -> None:
        """BufferStats is immutable (frozen msgspec.Struct)."""
        s = BufferStats(pending=1, completed=2, evicted=3)
        with pytest.raises(AttributeError):
            s.pending = 99  # type: ignore[misc]

    def test_no_ttl_means_no_eviction(self) -> None:
        """Default (no max_age_seconds) never evicts."""
        translator = BluetoothSIGTranslator()
        temp_uuid = str(TemperatureCharacteristic().uuid)
        humid_uuid = str(HumidityCharacteristic().uuid)

        buf = DependencyPairingBuffer(
            translator=translator,
            required_uuids={temp_uuid, humid_uuid},
            group_key=lambda _u, _p: "g",
            on_pair=lambda _r: None,
        )

        # Ingest partial and never complete
        buf.ingest(temp_uuid, bytes([0x0A, 0x00]))
        buf.ingest(temp_uuid, bytes([0x14, 0x00]))
        buf.ingest(temp_uuid, bytes([0x1E, 0x00]))

        assert buf.stats().pending == 1
        assert buf.stats().evicted == 0
