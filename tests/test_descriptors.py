"""Tests for descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.descriptors import (
    CCCDDescriptor,
    CharacteristicAggregateFormatDescriptor,
    CharacteristicExtendedPropertiesDescriptor,
    CharacteristicPresentationFormatDescriptor,
    CharacteristicUserDescriptionDescriptor,
    CompleteBREDRTransportBlockDataDescriptor,
    DescriptorRegistry,
    EnvironmentalSensingConfigurationDescriptor,
    EnvironmentalSensingMeasurementDescriptor,
    EnvironmentalSensingTriggerSettingDescriptor,
    ExternalReportReferenceDescriptor,
    IMDTriggerSettingDescriptor,
    ManufacturerLimitsDescriptor,
    MeasurementDescriptionDescriptor,
    NumberOfDigitalsDescriptor,
    ObservationScheduleDescriptor,
    ProcessTolerancesDescriptor,
    ReportReferenceDescriptor,
    ServerCharacteristicConfigurationDescriptor,
    TimeTriggerSettingDescriptor,
    ValidRangeAndAccuracyDescriptor,
    ValidRangeDescriptor,
    ValueTriggerSettingDescriptor,
)
from bluetooth_sig.gatt.descriptors.cccd import CCCDData
from bluetooth_sig.gatt.descriptors.characteristic_aggregate_format import CharacteristicAggregateFormatData
from bluetooth_sig.gatt.descriptors.characteristic_extended_properties import CharacteristicExtendedPropertiesData
from bluetooth_sig.gatt.descriptors.characteristic_presentation_format import CharacteristicPresentationFormatData
from bluetooth_sig.gatt.descriptors.characteristic_user_description import CharacteristicUserDescriptionData
from bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data import CompleteBREDRTransportBlockDataData
from bluetooth_sig.gatt.descriptors.environmental_sensing_configuration import EnvironmentalSensingConfigurationData
from bluetooth_sig.gatt.descriptors.environmental_sensing_measurement import EnvironmentalSensingMeasurementData
from bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting import EnvironmentalSensingTriggerSettingData
from bluetooth_sig.gatt.descriptors.external_report_reference import ExternalReportReferenceData
from bluetooth_sig.gatt.descriptors.imd_trigger_setting import IMDTriggerSettingData
from bluetooth_sig.gatt.descriptors.manufacturer_limits import ManufacturerLimitsData
from bluetooth_sig.gatt.descriptors.measurement_description import MeasurementDescriptionData
from bluetooth_sig.gatt.descriptors.number_of_digitals import NumberOfDigitalsData
from bluetooth_sig.gatt.descriptors.observation_schedule import ObservationScheduleData
from bluetooth_sig.gatt.descriptors.process_tolerances import ProcessTolerancesData
from bluetooth_sig.gatt.descriptors.report_reference import ReportReferenceData
from bluetooth_sig.gatt.descriptors.server_characteristic_configuration import SCCDData
from bluetooth_sig.gatt.descriptors.time_trigger_setting import TimeTriggerSettingData
from bluetooth_sig.gatt.descriptors.valid_range import ValidRangeData
from bluetooth_sig.gatt.descriptors.valid_range_and_accuracy import ValidRangeAndAccuracyData
from bluetooth_sig.gatt.descriptors.value_trigger_setting import ValueTriggerSettingData
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class TestCCCDDescriptor:
    """Test CCCD descriptor functionality."""

    def test_parse_enable_notifications(self) -> None:
        """Test parsing CCCD value with notifications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x01\x00"  # Notifications enabled

        result = cccd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is True
        assert result.value.indications_enabled is False

    def test_parse_enable_indications(self) -> None:
        """Test parsing CCCD value with indications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x02\x00"  # Indications enabled

        result = cccd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is False
        assert result.value.indications_enabled is True

    def test_parse_enable_both(self) -> None:
        """Test parsing CCCD value with both notifications and indications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x03\x00"  # Both enabled

        result = cccd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is True
        assert result.value.indications_enabled is True

    def test_parse_disable_all(self) -> None:
        """Test parsing CCCD value with all disabled."""
        cccd = CCCDDescriptor()
        data = b"\x00\x00"  # All disabled

        result = cccd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is False
        assert result.value.indications_enabled is False

    def test_parse_invalid_length(self) -> None:
        """Test parsing CCCD value with invalid length."""
        cccd = CCCDDescriptor()
        data = b"\x01"  # Too short

        result = cccd.parse_value(data)
        assert not result.parse_success
        assert "CCCD data must be exactly 2 bytes" in result.error_message

    def test_create_enable_values(self) -> None:
        """Test creating CCCD enable values."""
        assert CCCDDescriptor.create_enable_notifications_value() == b"\x01\x00"
        assert CCCDDescriptor.create_enable_indications_value() == b"\x02\x00"
        assert CCCDDescriptor.create_enable_both_value() == b"\x03\x00"
        assert CCCDDescriptor.create_disable_value() == b"\x00\x00"

    def test_uuid_resolution(self) -> None:
        """Test that CCCD has correct UUID."""
        cccd = CCCDDescriptor()
        assert str(cccd.uuid) == "00002902-0000-1000-8000-00805F9B34FB"


class TestValidRangeDescriptor:
    """Test Valid Range descriptor functionality."""

    def test_parse_valid_range(self) -> None:
        """Test parsing valid range descriptor."""
        valid_range = ValidRangeDescriptor()
        data = b"\x00\x00\xff\xff"  # Min: 0, Max: 65535

        result = valid_range.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ValidRangeData)
        assert result.value.min_value == 0
        assert result.value.max_value == 65535

    def test_parse_invalid_length(self) -> None:
        """Test parsing valid range with invalid length."""
        valid_range = ValidRangeDescriptor()
        data = b"\x00\x00"  # Too short

        result = valid_range.parse_value(data)
        assert not result.parse_success
        assert "Valid Range data expected 4 bytes, got 2" in result.error_message

    def test_validate_value_in_range(self) -> None:
        """Test validating a value within range."""
        valid_range = ValidRangeDescriptor()
        data = b"\x0a\x00\x64\x00"  # Min: 10, Max: 100

        result = valid_range.parse_value(data)
        assert result.parse_success

        # Test validation
        assert valid_range.is_value_in_range(data, 50) is True
        assert valid_range.is_value_in_range(data, 5) is False  # Below min
        assert valid_range.is_value_in_range(data, 150) is False  # Above max

    def test_uuid_resolution(self) -> None:
        """Test that Valid Range has correct UUID."""
        valid_range = ValidRangeDescriptor()
        assert str(valid_range.uuid) == "00002906-0000-1000-8000-00805F9B34FB"


class TestDescriptorRegistry:
    """Test descriptor registry functionality."""

    def test_registry_registration(self) -> None:
        """Test descriptor registration and lookup."""
        # Test all known descriptors are registered
        test_cases = [
            ("2900", CharacteristicExtendedPropertiesDescriptor),
            ("2901", CharacteristicUserDescriptionDescriptor),
            ("2902", CCCDDescriptor),
            ("2903", ServerCharacteristicConfigurationDescriptor),
            ("2904", CharacteristicPresentationFormatDescriptor),
            ("2905", CharacteristicAggregateFormatDescriptor),
            ("2906", ValidRangeDescriptor),
            ("2907", ExternalReportReferenceDescriptor),
            ("2908", ReportReferenceDescriptor),
            ("2909", NumberOfDigitalsDescriptor),
            ("290A", ValueTriggerSettingDescriptor),
            ("290B", EnvironmentalSensingConfigurationDescriptor),
            ("290C", EnvironmentalSensingMeasurementDescriptor),
            ("290D", EnvironmentalSensingTriggerSettingDescriptor),
            ("290E", TimeTriggerSettingDescriptor),
            ("290F", CompleteBREDRTransportBlockDataDescriptor),
            ("2910", ObservationScheduleDescriptor),
            ("2911", ValidRangeAndAccuracyDescriptor),
            ("2912", MeasurementDescriptionDescriptor),
            ("2913", ManufacturerLimitsDescriptor),
            ("2914", ProcessTolerancesDescriptor),
            ("2915", IMDTriggerSettingDescriptor),
        ]

        for uuid_short, expected_class in test_cases:
            descriptor_class = DescriptorRegistry.get_descriptor_class(uuid_short)
            assert descriptor_class is not None, f"Descriptor {uuid_short} not registered"
            assert descriptor_class == expected_class, f"Wrong class for {uuid_short}"

    def test_create_descriptor(self) -> None:
        """Test descriptor creation from registry."""
        # Test creating various descriptors
        test_cases = [
            ("2900", CharacteristicExtendedPropertiesDescriptor),
            ("2901", CharacteristicUserDescriptionDescriptor),
            ("2902", CCCDDescriptor),
            ("2904", CharacteristicPresentationFormatDescriptor),
            ("2906", ValidRangeDescriptor),
            ("290B", EnvironmentalSensingConfigurationDescriptor),
            ("2910", ObservationScheduleDescriptor),
        ]

        for uuid_short, expected_class in test_cases:
            descriptor = DescriptorRegistry.create_descriptor(uuid_short)
            assert descriptor is not None, f"Failed to create descriptor {uuid_short}"
            assert isinstance(descriptor, expected_class), f"Wrong type for {uuid_short}"

    def test_create_unknown_descriptor(self) -> None:
        """Test creating unknown descriptor returns None."""
        unknown = DescriptorRegistry.create_descriptor("FFFF")
        assert unknown is None


class TestBaseDescriptor:
    """Test base descriptor functionality."""

    def test_uuid_resolution(self) -> None:
        """Test that descriptors resolve their UUID correctly."""
        cccd = CCCDDescriptor()
        assert cccd.uuid is not None
        assert "2902" in str(cccd.uuid)

    def test_info_property(self) -> None:
        """Test descriptor info property."""
        cccd = CCCDDescriptor()
        info = cccd.info
        assert info.name == "Client Characteristic Configuration"
        assert "2902" in str(info.uuid)


class TestDescriptorIntegration:
    """Test descriptor integration with characteristics."""

    def test_characteristic_descriptor_support(self) -> None:
        """Test that characteristics can have descriptors added."""

        # Create a mock characteristic that supports descriptors
        class MockCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789012"),
                name="Test Characteristic",
                unit="",
                value_type=ValueType.INT,
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return int.from_bytes(data, "little")

            def encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, "little"))

        char = MockCharacteristic()

        # Add a descriptor
        cccd = CCCDDescriptor()
        char.add_descriptor(cccd)

        # Check that descriptor was added
        retrieved = char.get_descriptor("2902")
        assert retrieved is cccd

        # Check descriptors collection
        descriptors = char.get_descriptors()
        assert "00002902-0000-1000-8000-00805F9B34FB" in descriptors
        assert descriptors["00002902-0000-1000-8000-00805F9B34FB"] is cccd

    def test_characteristic_notification_support(self) -> None:
        """Test characteristic notification support detection."""

        class MockCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789013"),
                name="Test Characteristic 2",
                unit="",
                value_type=ValueType.INT,
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return int.from_bytes(data, "little")

            def encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, "little"))

        char = MockCharacteristic()

        # Without CCCD
        assert not char.can_notify()
        assert char.get_cccd() is None

        # With CCCD
        cccd = CCCDDescriptor()
        char.add_descriptor(cccd)
        assert char.can_notify()
        assert char.get_cccd() is cccd


class TestCharacteristicUserDescriptionDescriptor:
    """Test Characteristic User Description descriptor functionality."""

    def test_parse_valid_description(self) -> None:
        """Test parsing valid UTF-8 description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"Hello World"

        result = desc.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == "Hello World"

    def test_parse_empty_description(self) -> None:
        """Test parsing empty description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b""

        result = desc.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == ""

    def test_parse_unicode_description(self) -> None:
        """Test parsing Unicode description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = "温度传感器".encode()

        result = desc.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == "温度传感器"

    def test_parse_invalid_utf8(self) -> None:
        """Test parsing invalid UTF-8 data."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"\xff\xfe\xfd"  # Invalid UTF-8

        result = desc.parse_value(data)
        assert not result.parse_success
        assert "Invalid UTF-8 data" in result.error_message

    def test_get_description_helper(self) -> None:
        """Test get_description helper method."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"Battery Level"

        assert desc.get_description(data) == "Battery Level"

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic User Description has correct UUID."""
        desc = CharacteristicUserDescriptionDescriptor()
        assert str(desc.uuid) == "00002901-0000-1000-8000-00805F9B34FB"


class TestCharacteristicExtendedPropertiesDescriptor:
    """Test Characteristic Extended Properties descriptor functionality."""

    def test_parse_extended_properties(self) -> None:
        """Test parsing extended properties flags."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x01\x00"  # Reliable Write enabled

        result = ext_props.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicExtendedPropertiesData)
        assert result.value.reliable_write is True
        assert result.value.writable_auxiliaries is False

    def test_parse_multiple_flags(self) -> None:
        """Test parsing multiple extended properties flags."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x03\x00"  # Reliable Write and Writable Auxiliaries enabled

        result = ext_props.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicExtendedPropertiesData)
        assert result.value.reliable_write is True
        assert result.value.writable_auxiliaries is True

    def test_parse_invalid_length(self) -> None:
        """Test parsing extended properties with invalid length."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x01"  # Too short

        result = ext_props.parse_value(data)
        assert not result.parse_success
        assert "Extended Properties data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Extended Properties has correct UUID."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        assert str(ext_props.uuid) == "00002900-0000-1000-8000-00805F9B34FB"


class TestServerCharacteristicConfigurationDescriptor:
    """Test Server Characteristic Configuration descriptor functionality."""

    def test_parse_sccd_value(self) -> None:
        """Test parsing SCCD value."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        data = b"\x01\x00"  # Broadcasts enabled

        result = sccd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, SCCDData)
        assert result.value.broadcasts_enabled is True

    def test_parse_invalid_length(self) -> None:
        """Test parsing SCCD with invalid length."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        data = b"\x01"  # Too short

        result = sccd.parse_value(data)
        assert not result.parse_success
        assert "SCCD data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that SCCD has correct UUID."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        assert str(sccd.uuid) == "00002903-0000-1000-8000-00805F9B34FB"


class TestCharacteristicPresentationFormatDescriptor:
    """Test Characteristic Presentation Format descriptor functionality."""

    def test_parse_presentation_format(self) -> None:
        """Test parsing presentation format data."""
        cpf = CharacteristicPresentationFormatDescriptor()
        # Format: UINT16 (0x06), Exponent: 0, Unit: Celsius (0x272F)
        # Namespace: Bluetooth SIG (0x01), Description: Temperature (0x0000)
        data = b"\x06\x00\x2f\x27\x01\x00\x00"

        result = cpf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicPresentationFormatData)
        assert result.value.format == 0x06  # UINT16
        assert result.value.exponent == 0
        assert result.value.unit == 0x272F  # Celsius
        assert result.value.namespace == 0x01  # Bluetooth SIG
        assert result.value.description == 0x0000

    def test_parse_invalid_length(self) -> None:
        """Test parsing presentation format with invalid length."""
        cpf = CharacteristicPresentationFormatDescriptor()
        data = b"\x06\x00\x2f\x27\x01\x00"  # Too short (6 bytes instead of 7)

        result = cpf.parse_value(data)
        assert not result.parse_success
        assert "Presentation Format data must be exactly 7 bytes" in result.error_message

    def test_helper_methods(self) -> None:
        """Test helper methods for accessing format components."""
        cpf = CharacteristicPresentationFormatDescriptor()
        data = b"\x06\x00\x2f\x27\x01\x00\x00"

        assert cpf.get_format_type(data) == 0x06
        assert cpf.get_exponent(data) == 0
        assert cpf.get_unit(data) == 0x272F
        assert cpf.get_namespace(data) == 0x01
        assert cpf.get_description(data) == 0x0000

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Presentation Format has correct UUID."""
        cpf = CharacteristicPresentationFormatDescriptor()
        assert str(cpf.uuid) == "00002904-0000-1000-8000-00805F9B34FB"


class TestCharacteristicAggregateFormatDescriptor:
    """Test Characteristic Aggregate Format descriptor functionality."""

    def test_parse_aggregate_format(self) -> None:
        """Test parsing aggregate format data."""
        caf = CharacteristicAggregateFormatDescriptor()
        # Two handles: 0x0001, 0x0002
        data = b"\x01\x00\x02\x00"

        result = caf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicAggregateFormatData)
        assert result.value.attribute_handles == [0x0001, 0x0002]

    def test_parse_single_handle(self) -> None:
        """Test parsing aggregate format with single handle."""
        caf = CharacteristicAggregateFormatDescriptor()
        data = b"\x01\x00"

        result = caf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicAggregateFormatData)
        assert result.value.attribute_handles == [0x0001]

    def test_parse_invalid_length(self) -> None:
        """Test parsing aggregate format with invalid length."""
        caf = CharacteristicAggregateFormatDescriptor()
        data = b"\x01"  # Odd length (should be even)

        result = caf.parse_value(data)
        assert not result.parse_success
        assert "must have even length" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Aggregate Format has correct UUID."""
        caf = CharacteristicAggregateFormatDescriptor()
        assert str(caf.uuid) == "00002905-0000-1000-8000-00805F9B34FB"


class TestExternalReportReferenceDescriptor:
    """Test External Report Reference descriptor functionality."""

    def test_parse_external_report_reference(self) -> None:
        """Test parsing external report reference."""
        err = ExternalReportReferenceDescriptor()
        data = b"\x01\x00"  # Report ID 1

        result = err.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ExternalReportReferenceData)
        assert result.value.external_report_id == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing external report reference with invalid length."""
        err = ExternalReportReferenceDescriptor()
        data = b"\x01\x00\x02"  # Too long

        result = err.parse_value(data)
        assert not result.parse_success
        assert "External Report Reference data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that External Report Reference has correct UUID."""
        err = ExternalReportReferenceDescriptor()
        assert str(err.uuid) == "00002907-0000-1000-8000-00805F9B34FB"


class TestReportReferenceDescriptor:
    """Test Report Reference descriptor functionality."""

    def test_parse_report_reference(self) -> None:
        """Test parsing report reference."""
        rr = ReportReferenceDescriptor()
        data = b"\x01\x00"  # Report ID 1

        result = rr.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ReportReferenceData)
        assert result.value.report_id == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing report reference with invalid length."""
        rr = ReportReferenceDescriptor()
        data = b"\x01"  # Too short

        result = rr.parse_value(data)
        assert not result.parse_success
        assert "Report Reference data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Report Reference has correct UUID."""
        rr = ReportReferenceDescriptor()
        assert str(rr.uuid) == "00002908-0000-1000-8000-00805F9B34FB"


class TestNumberOfDigitalsDescriptor:
    """Test Number of Digitals descriptor functionality."""

    def test_parse_number_of_digitals(self) -> None:
        """Test parsing number of digitals."""
        nod = NumberOfDigitalsDescriptor()
        data = b"\x02"  # 2 digitals (1 byte)

        result = nod.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, NumberOfDigitalsData)
        assert result.value.number_of_digitals == 0x02

    def test_parse_invalid_length(self) -> None:
        """Test parsing number of digitals with invalid length."""
        nod = NumberOfDigitalsDescriptor()
        data = b"\x02\x00"  # Too long (2 bytes instead of 1)

        result = nod.parse_value(data)
        assert not result.parse_success
        assert "Number of Digitals data must be exactly 1 byte" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Number of Digitals has correct UUID."""
        nod = NumberOfDigitalsDescriptor()
        assert str(nod.uuid) == "00002909-0000-1000-8000-00805F9B34FB"


class TestValueTriggerSettingDescriptor:
    """Test Value Trigger Setting descriptor functionality."""

    def test_parse_value_trigger_setting(self) -> None:
        """Test parsing value trigger setting."""
        vts = ValueTriggerSettingDescriptor()
        # Condition: 0x01 (less than), Value: 0x0A
        data = b"\x01\x0a"

        result = vts.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ValueTriggerSettingData)
        assert result.value.condition == 0x01
        assert result.value.value == 0x0A

    def test_parse_invalid_length(self) -> None:
        """Test parsing value trigger setting with invalid length."""
        vts = ValueTriggerSettingDescriptor()
        data = b"\x01"  # Too short (1 byte, need at least 2)

        result = vts.parse_value(data)
        assert not result.parse_success
        assert "Value Trigger Setting data must be at least 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Value Trigger Setting has correct UUID."""
        vts = ValueTriggerSettingDescriptor()
        assert str(vts.uuid) == "0000290A-0000-1000-8000-00805F9B34FB"


class TestEnvironmentalSensingConfigurationDescriptor:
    """Test Environmental Sensing Configuration descriptor functionality."""

    def test_parse_es_configuration(self) -> None:
        """Test parsing environmental sensing configuration."""
        esc = EnvironmentalSensingConfigurationDescriptor()
        # Flags: 0x0007 (trigger logic, transmission interval, measurement period)
        data = b"\x07\x00"

        result = esc.parse_value(data)
        assert result.parse_success
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
        assert not result.parse_success
        assert "Environmental Sensing Configuration data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Environmental Sensing Configuration has correct UUID."""
        esc = EnvironmentalSensingConfigurationDescriptor()
        assert str(esc.uuid) == "0000290B-0000-1000-8000-00805F9B34FB"


class TestEnvironmentalSensingMeasurementDescriptor:
    """Test Environmental Sensing Measurement descriptor functionality."""

    def test_parse_es_measurement(self) -> None:
        """Test parsing environmental sensing measurement."""
        esm = EnvironmentalSensingMeasurementDescriptor()
        # 12 bytes: sampling_function (3), measurement_period (3), update_interval (3),
        # application (1), measurement_uncertainty (2)
        data = b"\x01\x00\x00\x02\x00\x00\x03\x00\x00\x04\x05\x00"

        result = esm.parse_value(data)
        assert result.parse_success
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
        assert not result.parse_success
        assert "Environmental Sensing Measurement data must be exactly 12 bytes" in result.error_message

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
        assert result.parse_success
        assert isinstance(result.value, EnvironmentalSensingTriggerSettingData)
        assert result.value.condition == 0x01
        assert result.value.operand == 0x000A

    def test_parse_invalid_length(self) -> None:
        """Test parsing ES trigger setting with invalid length."""
        ests = EnvironmentalSensingTriggerSettingDescriptor()
        data = b"\x01\x00"  # Too short (2 bytes instead of 3)

        result = ests.parse_value(data)
        assert not result.parse_success
        assert "Environmental Sensing Trigger Setting data must be exactly 3 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Environmental Sensing Trigger Setting has correct UUID."""
        ests = EnvironmentalSensingTriggerSettingDescriptor()
        assert str(ests.uuid) == "0000290D-0000-1000-8000-00805F9B34FB"


class TestTimeTriggerSettingDescriptor:
    """Test Time Trigger Setting descriptor functionality."""

    def test_parse_time_trigger_setting(self) -> None:
        """Test parsing time trigger setting."""
        tts = TimeTriggerSettingDescriptor()
        # Value: 0x00000A00 (2560 seconds)
        data = b"\x00\x0a\x00"

        result = tts.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, TimeTriggerSettingData)
        assert result.value.time_interval == 0x000A00

    def test_parse_invalid_length(self) -> None:
        """Test parsing time trigger setting with invalid length."""
        tts = TimeTriggerSettingDescriptor()
        data = b"\x00\x0a\x00\x00"  # Too long (4 bytes instead of 3)

        result = tts.parse_value(data)
        assert not result.parse_success
        assert "Time Trigger Setting data must be exactly 3 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Time Trigger Setting has correct UUID."""
        tts = TimeTriggerSettingDescriptor()
        assert str(tts.uuid) == "0000290E-0000-1000-8000-00805F9B34FB"


class TestCompleteBREDRTransportBlockDataDescriptor:
    """Test Complete BR-EDR Transport Block Data descriptor functionality."""

    def test_parse_complete_br_edr_transport_block_data(self) -> None:
        """Test parsing complete BR-EDR transport block data."""
        cbtbd = CompleteBREDRTransportBlockDataDescriptor()
        # Simple test data - actual format is complex
        data = b"\x01\x02\x03\x04"

        result = cbtbd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CompleteBREDRTransportBlockDataData)
        # Note: This descriptor has a complex format, so we're just testing basic parsing

    def test_uuid_resolution(self) -> None:
        """Test that Complete BR-EDR Transport Block Data has correct UUID."""
        cbtbd = CompleteBREDRTransportBlockDataDescriptor()
        assert str(cbtbd.uuid) == "0000290F-0000-1000-8000-00805F9B34FB"


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


class TestValidRangeAndAccuracyDescriptor:
    """Test Valid Range and Accuracy descriptor functionality."""

    def test_parse_valid_range_and_accuracy(self) -> None:
        """Test parsing valid range and accuracy."""
        vra = ValidRangeAndAccuracyDescriptor()
        # Min: 0x0000, Max: 0xFFFF, Accuracy: 0x0001
        data = b"\x00\x00\xff\xff\x01\x00"

        result = vra.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ValidRangeAndAccuracyData)
        assert result.value.min_value == 0x0000
        assert result.value.max_value == 0xFFFF
        assert result.value.accuracy == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing valid range and accuracy with invalid length."""
        vra = ValidRangeAndAccuracyDescriptor()
        data = b"\x00\x00\xff\xff"  # Too short

        result = vra.parse_value(data)
        assert not result.parse_success
        assert "Valid Range and Accuracy data expected 6 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Valid Range and Accuracy has correct UUID."""
        vra = ValidRangeAndAccuracyDescriptor()
        assert str(vra.uuid) == "00002911-0000-1000-8000-00805F9B34FB"


class TestMeasurementDescriptionDescriptor:
    """Test Measurement Description descriptor functionality."""

    def test_parse_measurement_description(self) -> None:
        """Test parsing measurement description."""
        md = MeasurementDescriptionDescriptor()
        # Description: "Temperature"
        data = b"Temperature"

        result = md.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, MeasurementDescriptionData)
        assert result.value.description == "Temperature"

    def test_parse_invalid_utf8(self) -> None:
        """Test parsing measurement description with invalid UTF-8."""
        md = MeasurementDescriptionDescriptor()
        data = b"\xff\xfe\xfd"  # Invalid UTF-8

        result = md.parse_value(data)
        assert not result.parse_success
        assert "Invalid UTF-8 data" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Measurement Description has correct UUID."""
        md = MeasurementDescriptionDescriptor()
        assert str(md.uuid) == "00002912-0000-1000-8000-00805F9B34FB"


class TestManufacturerLimitsDescriptor:
    """Test Manufacturer Limits descriptor functionality."""

    def test_parse_manufacturer_limits(self) -> None:
        """Test parsing manufacturer limits."""
        ml = ManufacturerLimitsDescriptor()
        # Lower limit: 0x0000, Upper limit: 0xFFFF
        data = b"\x00\x00\xff\xff"

        result = ml.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ManufacturerLimitsData)
        assert result.value.min_limit == 0x0000
        assert result.value.max_limit == 0xFFFF

    def test_parse_invalid_length(self) -> None:
        """Test parsing manufacturer limits with invalid length."""
        ml = ManufacturerLimitsDescriptor()
        data = b"\x00\x00"  # Too short

        result = ml.parse_value(data)
        assert not result.parse_success
        assert "Manufacturer Limits data expected 4 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Manufacturer Limits has correct UUID."""
        ml = ManufacturerLimitsDescriptor()
        assert str(ml.uuid) == "00002913-0000-1000-8000-00805F9B34FB"


class TestProcessTolerancesDescriptor:
    """Test Process Tolerances descriptor functionality."""

    def test_parse_process_tolerances(self) -> None:
        """Test parsing process tolerances."""
        pt = ProcessTolerancesDescriptor()
        # Tolerance: 0x00000001
        data = b"\x01\x00\x00\x00"

        result = pt.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ProcessTolerancesData)
        assert result.value.tolerance_min == 0x0001
        assert result.value.tolerance_max == 0x0000

    def test_parse_invalid_length(self) -> None:
        """Test parsing process tolerances with invalid length."""
        pt = ProcessTolerancesDescriptor()
        data = b"\x01\x00\x00"  # Too short

        result = pt.parse_value(data)
        assert not result.parse_success
        assert "Process Tolerances data expected 4 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Process Tolerances has correct UUID."""
        pt = ProcessTolerancesDescriptor()
        assert str(pt.uuid) == "00002914-0000-1000-8000-00805F9B34FB"


class TestIMDTriggerSettingDescriptor:
    """Test IMD Trigger Setting descriptor functionality."""

    def test_parse_imd_trigger_setting(self) -> None:
        """Test parsing IMD trigger setting."""
        imd = IMDTriggerSettingDescriptor()
        # Trigger setting: 0x0001
        data = b"\x01\x00"

        result = imd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, IMDTriggerSettingData)
        assert result.value.trigger_setting == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing IMD trigger setting with invalid length."""
        imd = IMDTriggerSettingDescriptor()
        data = b"\x01\x00\x00"  # Too long (3 bytes instead of 2)

        result = imd.parse_value(data)
        assert not result.parse_success
        assert "IMD Trigger Setting data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that IMD Trigger Setting has correct UUID."""
        imd = IMDTriggerSettingDescriptor()
        assert str(imd.uuid) == "00002915-0000-1000-8000-00805F9B34FB"


class TestDescriptorWritability:
    """Test descriptor writability checks."""

    def test_cccd_is_writable(self) -> None:
        """CCCD should be marked as writable."""
        cccd = CCCDDescriptor()
        assert cccd.is_writable() is True

    def test_sccd_is_writable(self) -> None:
        """SCCD should be marked as writable."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        assert sccd.is_writable() is True

    def test_user_description_not_writable(self) -> None:
        """User Description should be non-writable (conservative approach)."""
        user_desc = CharacteristicUserDescriptionDescriptor()
        assert user_desc.is_writable() is False

    def test_read_only_descriptors_not_writable(self) -> None:
        """Read-only descriptors should be marked as non-writable."""
        valid_range = ValidRangeDescriptor()
        assert valid_range.is_writable() is False

        presentation_format = CharacteristicPresentationFormatDescriptor()
        assert presentation_format.is_writable() is False

        extended_props = CharacteristicExtendedPropertiesDescriptor()
        assert extended_props.is_writable() is False
