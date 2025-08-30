# BLE GATT Device Integration

A Home Assistant integration for reading standard GATT services from BLE devices.

## Development Status

This project is currently in development phase, focusing on:

1. Initial Phase:
   - Connecting to hardcoded BLE device MAC addresses
   - Reading standard GATT services (Environmental Sensing, Battery)
   - Basic disconnect handling

2. Future Phase:
   - Device discovery via BLE advertisements
   - Dynamic entity creation based on available services
   - Custom service UUID support

## Development Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
```

2. Install development dependencies:
```bash
pip install -e ".[test]"
```

3. Run tests:
```bash
pytest
```

## Supported GATT Services

- Environmental Sensing Service (0x181A)
  - Temperature
  - Humidity
  - Pressure
- Battery Service (0x180F)
  - Battery Level
