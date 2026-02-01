"""Tests for Environmental Sensing descriptors functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import (
    EnvironmentalSensingConfigurationDescriptor,
    EnvironmentalSensingMeasurementDescriptor,
    EnvironmentalSensingTriggerSettingDescriptor,
)
from bluetooth_sig.gatt.descriptors.environmental_sensing_configuration import EnvironmentalSensingConfigurationData
from bluetooth_sig.gatt.descriptors.environmental_sensing_measurement import EnvironmentalSensingMeasurementData
from bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting import (
    EnvironmentalSensingTriggerSettingData,
)


class TestEnvironmentalSensingConfigurationDescriptor:
    """Test Environmental Sensing Configuration descriptor functionality."""

    def test_parse_es_configuration(self) -> None:
        """Test parsing environmental sensing configuration."""
        esc = EnvironmentalSensingConfigurationDescriptor()
        # Flags: 0x0007 (trigger logic, transmission interval, measurement period)
        data = b"\x07\x00"

        result = esc.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, EnvironmentalSensingConfigurationData)
        assert result.value.trigger_logic_value is True
        assert result.value.transmission_interval_present is True
        assert result.value.measurement_period_present is True
        assert result.value.update_interval_present is False

    def test_parse_invalid_length(self) -> None:
        """Test parsing ES configuration with invalid length."""
        esc = EnvironmentalSensingConfigurationDescriptor()
        data = b"\x07"  # Too short

        result = esc.parse_value(data)
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Environmental Sensing Configuration has correct UUID."""
        esc = EnvironmentalSensingConfigurationDescriptor()
        assert str(esc.uuid) == "0000290B-0000-1000-8000-00805F9B34FB"


class TestEnvironmentalSensingMeasurementDescriptor:
    """Test Environmental Sensing Measurement descriptor functionality."""

    def test_parse_es_measurement(self) -> None:
        """Test parsing environmental sensing measurement."""
        esm = EnvironmentalSensingMeasurementDescriptor()
        # 12 bytes structure: sampling_function (3 bytes), measurement_period (3 bytes),
        # update_interval (3 bytes), application (1 byte), measurement_uncertainty (2 bytes)
        data = b"\x01\x00\x00\x02\x00\x00\x03\x00\x00\x04\x05\x00"

        result = esm.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, EnvironmentalSensingMeasurementData)
        assert result.value.sampling_function == 0x000001
        assert result.value.measurement_period == 0x000002
        assert result.value.update_interval == 0x000003
        assert result.value.application == 0x04
        assert result.value.measurement_uncertainty == 0x0005

    def test_parse_invalid_length(self) -> None:
        """Test parsing ES measurement with invalid length."""
        esm = EnvironmentalSensingMeasurementDescriptor()
        data = b"\x07\x00"  # Too short (2 bytes instead of 12)

        result = esm.parse_value(data)
        assert result.parse_success is False
        assert "need 4 bytes, got 2" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Environmental Sensing Measurement has correct UUID."""
        esm = EnvironmentalSensingMeasurementDescriptor()
        assert str(esm.uuid) == "0000290C-0000-1000-8000-00805F9B34FB"


class TestEnvironmentalSensingTriggerSettingDescriptor:
    """Test Environmental Sensing Trigger Setting descriptor functionality."""

    def test_parse_es_trigger_setting(self) -> None:
        """Test parsing environmental sensing trigger setting."""
        ests = EnvironmentalSensingTriggerSettingDescriptor()
        # Condition: 0x01, Operand: 0x000A
        data = b"\x01\x0a\x00"

        result = ests.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, EnvironmentalSensingTriggerSettingData)
        assert result.value.condition == 0x01
        assert result.value.operand == 0x000A

    def test_parse_invalid_length(self) -> None:
        """Test parsing ES trigger setting with invalid length."""
        ests = EnvironmentalSensingTriggerSettingDescriptor()
        data = b"\x01\x00"  # Too short (2 bytes instead of 3)

        result = ests.parse_value(data)
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Environmental Sensing Trigger Setting has correct UUID."""
        ests = EnvironmentalSensingTriggerSettingDescriptor()
        assert str(ests.uuid) == "0000290D-0000-1000-8000-00805F9B34FB"
