"""Test core BLEGATTDevice functionality using pytest framework."""

import pytest

from ble_gatt_device.core import BLEGATTDevice


class TestCoreFunctionality:
    """Test BLEGATTDevice core functionality."""

    def test_device_instantiation(self):
        """Test that BLEGATTDevice can be instantiated correctly."""
        test_address = "AA:BB:CC:DD:EE:FF"
        device = BLEGATTDevice(test_address)
        
        assert device.address == test_address, f"Expected address {test_address}, got {device.address}"
        assert hasattr(device, 'address'), "Device should have address attribute"

    def test_device_methods_exist(self):
        """Test that essential methods exist on BLEGATTDevice."""
        device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
        
        # Test that core methods exist
        assert hasattr(device, 'read_characteristics'), "Device should have read_characteristics method"
        assert hasattr(device, 'read_parsed_characteristics'), "Device should have read_parsed_characteristics method"
        assert hasattr(device, 'get_device_info'), "Device should have get_device_info method"
        
        # Test that methods are callable
        assert callable(device.read_characteristics), "read_characteristics should be callable"
        assert callable(device.read_parsed_characteristics), "read_parsed_characteristics should be callable"
        assert callable(device.get_device_info), "get_device_info should be callable"

    def test_device_address_validation(self):
        """Test device address validation and handling."""
        # Test valid MAC address formats
        valid_addresses = [
            "AA:BB:CC:DD:EE:FF",
            "00:11:22:33:44:55",
            "12:34:56:78:9A:BC",
        ]
        
        for address in valid_addresses:
            device = BLEGATTDevice(address)
            assert device.address == address, f"Address {address} should be preserved"

    def test_device_string_representation(self):
        """Test device string representation."""
        test_address = "AA:BB:CC:DD:EE:FF"
        device = BLEGATTDevice(test_address)
        
        # Test that device has a reasonable string representation
        device_str = str(device)
        assert test_address in device_str, f"Device string representation should contain address {test_address}"

    @pytest.mark.asyncio
    async def test_core_methods_are_async(self):
        """Test that core methods are properly async (even if they can't connect in test)."""
        device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
        
        # These methods should be async, even if they fail due to no real device
        # We're testing the method signatures and async nature, not actual BLE functionality
        
        import inspect
        
        assert inspect.iscoroutinefunction(device.read_characteristics), "read_characteristics should be async"
        assert inspect.iscoroutinefunction(device.read_parsed_characteristics), "read_parsed_characteristics should be async"
        
        # Note: We don't try to actually call these methods since that would require a real BLE device
        # This test validates the interface is correctly async

    def test_device_attributes_initialization(self):
        """Test that device initializes with expected attributes."""
        device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
        
        # Check that device has expected attributes
        assert hasattr(device, 'address'), "Device should have address attribute"
        
        # The device should be ready for use even without an active connection
        assert device.address is not None, "Device address should not be None"
        assert len(device.address) > 0, "Device address should not be empty"

    def test_multiple_device_instances(self):
        """Test that multiple device instances can be created independently."""
        address1 = "AA:BB:CC:DD:EE:FF"
        address2 = "11:22:33:44:55:66"
        
        device1 = BLEGATTDevice(address1)
        device2 = BLEGATTDevice(address2)
        
        assert device1.address == address1, "Device 1 should have correct address"
        assert device2.address == address2, "Device 2 should have correct address"
        assert device1 is not device2, "Device instances should be separate objects"
        assert device1.address != device2.address, "Device addresses should be different"

    def test_device_interface_completeness(self):
        """Test that device implements expected interface."""
        device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
        
        # Core interface methods
        required_methods = [
            'read_characteristics',
            'read_parsed_characteristics', 
            'get_device_info'
        ]
        
        for method_name in required_methods:
            assert hasattr(device, method_name), f"Device should have {method_name} method"
            method = getattr(device, method_name)
            assert callable(method), f"{method_name} should be callable"

    def test_device_ready_for_real_testing(self):
        """Test that device is properly structured for real device testing."""
        device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
        
        # Verify the device is ready for the real device testing workflow
        assert device.address == "AA:BB:CC:DD:EE:FF", "Device should store the provided address"
        
        # The device should have the expected interface for real BLE interaction
        # (even though we can't test actual BLE without hardware)
        assert hasattr(device, 'read_characteristics'), "Device needs read_characteristics for real testing"
        assert hasattr(device, 'read_parsed_characteristics'), "Device needs read_parsed_characteristics for real testing"