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
from bluetooth_sig.stream import DependencyPairingBuffer


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
