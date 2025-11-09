"""Pytest configuration for benchmarks."""

from __future__ import annotations

import pytest

from bluetooth_sig import BluetoothSIGTranslator


@pytest.fixture
def translator():
    """Provide a BluetoothSIGTranslator instance for benchmarks."""
    return BluetoothSIGTranslator()


@pytest.fixture
def battery_level_data():
    """Valid battery level characteristic data."""
    return bytearray([85])  # 85%


@pytest.fixture
def temperature_data():
    """Valid temperature characteristic data."""
    return bytearray([0x64, 0x09])  # 24.36°C


@pytest.fixture
def humidity_data():
    """Valid humidity characteristic data."""
    return bytearray([0x3A, 0x13])  # 49.46%


@pytest.fixture
def heart_rate_data():
    """Valid heart rate measurement data."""
    return bytearray([0x16, 0x3C, 0x00, 0x40, 0x00])


@pytest.fixture
def batch_characteristics_small():
    """Small batch of characteristic data for benchmarking."""
    return {
        "2A19": bytearray([85]),         # Battery Level
        "2A6E": bytearray([0x64, 0x09]), # Temperature
        "2A6F": bytearray([0x3A, 0x13]), # Humidity
    }


@pytest.fixture
def batch_characteristics_medium():
    """Medium batch of characteristic data for benchmarking."""
    return {
        "2A19": bytearray([85]),         # Battery Level
        "2A6E": bytearray([0x64, 0x09]), # Temperature
        "2A6F": bytearray([0x3A, 0x13]), # Humidity
        "2A1C": bytearray([0x64, 0x09]), # Temperature Measurement
        "2A1E": bytearray([0x00]),        # Intermediate Temperature
        "2A21": bytearray([0x3A, 0x13]), # Measurement Interval
        "2A23": bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]), # System ID
        "2A25": bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]), # Serial Number String
        "2A27": bytearray([0x01, 0x02, 0x03, 0x04]), # Hardware Revision
        "2A28": bytearray([0x01, 0x02, 0x03, 0x04]), # Software Revision
    }
