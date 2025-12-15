"""Tests for Observation Schedule descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ObservationScheduleDescriptor
from bluetooth_sig.gatt.descriptors.observation_schedule import ObservationScheduleData


class TestObservationScheduleDescriptor:
    """Test Observation Schedule descriptor functionality."""

    def test_parse_observation_schedule(self) -> None:
        """Test parsing observation schedule."""
        os_desc = ObservationScheduleDescriptor()
        # Flags: 0x01 (periodic observation)
        data = b"\x01\x00"

        result = os_desc.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ObservationScheduleData)
        assert result.value.schedule == b"\x01\x00"

    def test_uuid_resolution(self) -> None:
        """Test that Observation Schedule has correct UUID."""
        os_desc = ObservationScheduleDescriptor()
        assert str(os_desc.uuid) == "00002910-0000-1000-8000-00805F9B34FB"
