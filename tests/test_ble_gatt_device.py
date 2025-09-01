"""Tests for BLE GATT device functionality."""

# pylint: disable=redefined-outer-name  # pytest fixtures


from unittest.mock import AsyncMock

import pytest

from ble_gatt_device.core import BLEGATTDevice


@pytest.fixture
def mock_device():
    """Create a mock BLE device with a mocked backend implementation."""
    device = BLEGATTDevice("00:11:22:33:44:55")
    device._impl = AsyncMock()
    return device


@pytest.mark.asyncio
async def test_connect_success(mock_device):
    """Test successful device connection."""
    mock_device._impl.connect.return_value = True
    result = await mock_device.connect()
    assert result is True
    mock_device._impl.connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_device_not_found(mock_device):
    """Test connection when device is not found (simulated by returning False)."""
    mock_device._impl.connect.return_value = False
    result = await mock_device.connect()
    assert result is False
    mock_device._impl.connect.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect(mock_device):
    """Test device disconnection."""
    await mock_device.disconnect()
    mock_device._impl.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_read_characteristics_success(mock_device):
    """Test successful characteristic reading."""
    mock_device._impl.read_characteristics.return_value = {
        "char1": b"foo",
        "char2": b"bar",
    }
    values = await mock_device.read_characteristics()
    assert isinstance(values, dict)
    assert "char1" in values and "char2" in values


@pytest.mark.asyncio
async def test_read_characteristics_not_connected(mock_device):
    """Test characteristic reading when device is not connected (simulated by returning empty dict)."""
    mock_device._impl.read_characteristics.return_value = {}
    values = await mock_device.read_characteristics()
    assert values == {}
