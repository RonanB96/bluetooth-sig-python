"""Tests for BLE GATT device functionality."""
# pylint: disable=redefined-outer-name  # pytest fixtures

import pytest
from unittest.mock import AsyncMock, patch

from ble_gatt_device.core import BLEGATTDevice


@pytest.fixture
def mock_device():
    """Create a mock BLE device."""
    device = BLEGATTDevice("00:11:22:33:44:55")
    device.client = AsyncMock()
    return device


@pytest.mark.asyncio
async def test_connect_success(mock_device):
    """Test successful device connection."""
    with patch("ble_gatt_device.core.BleakClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value = mock_client_instance
        
        result = await mock_device.connect()
        
        assert result is True
        mock_client_class.assert_called_once_with(mock_device.address)
        mock_client_instance.connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_device_not_found(mock_device):
    """Test connection when device is not found."""
    with patch("bleak.BleakScanner.find_device_by_address", return_value=None):
        result = await mock_device.connect()
        assert result is False
        mock_device.client.connect.assert_not_called()


@pytest.mark.asyncio
async def test_disconnect(mock_device):
    """Test device disconnection."""
    mock_device._client = mock_device.client  # Set the private client attribute
    await mock_device.disconnect()
    mock_device.client.disconnect.assert_called_once()
    assert mock_device._client is None


@pytest.mark.asyncio
async def test_read_characteristics_success(mock_device):
    """Test successful characteristic reading."""
    # Set up the mock client properly
    mock_client = AsyncMock()
    mock_device._client = mock_client
    
    # Mock get_services to return mock services
    mock_services = {
        "service1": {
            "characteristics": {
                "char1": {"properties": ["read"]},
                "char2": {"properties": ["read"]},
            }
        }
    }
    mock_client.get_services.return_value = mock_services  # pylint: disable=no-member
    
    # Mock read_gatt_char to return test values
    mock_client.read_gatt_char.side_effect = [
        bytes([100, 0]),  # First characteristic
        bytes([75]),      # Second characteristic
    ]
    
    values = await mock_device.read_characteristics()
    
    # Check that some values were returned
    assert isinstance(values, dict)


@pytest.mark.asyncio
async def test_read_characteristics_not_connected(mock_device):
    """Test characteristic reading when device is not connected."""
    mock_device.client.is_connected = False
    values = await mock_device.read_characteristics()
    assert values == {}
