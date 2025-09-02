# Script Consolidation Migration Guide

This document provides migration guidance for users of the consolidated BLE debugging scripts.

## Removed Scripts and Migration

### `test_connection_strategies.py` → `ble_debug.py connect`

**Old usage:**
```bash
python scripts/test_connection_strategies.py AA:BB:CC:DD:EE:FF
```

**New usage:**
```bash
python scripts/ble_debug.py connect AA:BB:CC:DD:EE:FF
```

**What changed:**
- Same connection testing strategies
- Better error analysis and troubleshooting
- More structured output with step-by-step feedback

### `test_real_device_debug.py` → `ble_debug.py discover` and `ble_debug.py test`

**Old usage:**
```bash
python scripts/test_real_device_debug.py AA:BB:CC:DD:EE:FF
python scripts/test_real_device_debug.py scan
```

**New usage:**
```bash
# For full discovery (equivalent to old script)
python scripts/ble_debug.py discover AA:BB:CC:DD:EE:FF

# For comprehensive testing
python scripts/ble_debug.py test AA:BB:CC:DD:EE:FF

# For scanning
python scripts/ble_debug.py scan
```

**What changed:**
- More modular approach with specific commands
- Enhanced error analysis
- Preserved all 5-step debugging functionality
- Added comprehensive test suite option

## New Consolidated Script: `ble_debug.py`

The new `ble_debug.py` script provides all functionality from the removed scripts plus additional features:

### Available Commands

```bash
# Scan for devices
python scripts/ble_debug.py scan [--timeout 30] [--details]

# Test connection strategies
python scripts/ble_debug.py connect AA:BB:CC:DD:EE:FF

# Full service/characteristic discovery
python scripts/ble_debug.py discover AA:BB:CC:DD:EE:FF

# Read all readable characteristics
python scripts/ble_debug.py read AA:BB:CC:DD:EE:FF

# Monitor device (future enhancement)
python scripts/ble_debug.py monitor AA:BB:CC:DD:EE:FF [--duration 60]

# Comprehensive test suite
python scripts/ble_debug.py test AA:BB:CC:DD:EE:FF
```

### Enhanced Features

1. **Better CLI**: Structured subcommands with help text
2. **Error Analysis**: Comprehensive troubleshooting guidance
3. **Framework Integration**: Works with or without GATT framework
4. **Modular Testing**: Choose specific functionality needed
5. **Consistent Output**: Structured, easy-to-read results

## Main Real Device Script: `test_real_device.py`

The main real device testing script has been improved but maintains backward compatibility:

**Enhanced features:**
- Improved scanning with timeout support
- References to advanced debugging options
- Consistent path configuration

**Usage remains the same:**
```bash
python scripts/test_real_device.py AA:BB:CC:DD:EE:FF
python scripts/test_real_device.py scan [timeout]
python scripts/test_real_device.py analyze
```

## Quick Reference

| Old Script | New Command | Purpose |
|------------|-------------|---------|
| `test_connection_strategies.py ADDR` | `ble_debug.py connect ADDR` | Test connection strategies |
| `test_real_device_debug.py ADDR` | `ble_debug.py discover ADDR` | Full device discovery |
| `test_real_device_debug.py scan` | `ble_debug.py scan` | Scan for devices |
| N/A | `ble_debug.py read ADDR` | Read characteristics only |
| N/A | `ble_debug.py test ADDR` | Comprehensive test suite |

## Help and Documentation

Get help for any command:
```bash
python scripts/ble_debug.py --help
python scripts/ble_debug.py scan --help
python scripts/ble_debug.py connect --help
# etc.
```

All functionality from the removed scripts has been preserved and enhanced in the new consolidated script.