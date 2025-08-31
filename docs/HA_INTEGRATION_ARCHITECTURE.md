# Home Assistant Integration Architecture

This document describes the proper separation of concerns between the BLE GATT framework and Home Assistant integration.

## Architecture Overview

The framework follows a strict three-layer architecture:

```
Home Assistant Integration Layer
            ↓ (calls)
    Translation Layer  
            ↓ (calls)
       GATT Layer
```

**IMPORTANT**: Dependencies flow in one direction only: HA → Translation → GATT (never reverse)

## Layer Responsibilities

### 1. GATT Layer (`src/ble_gatt_device/gatt/`)

**Purpose**: Pure Bluetooth functionality with metadata properties for translation layer

**Contains**:
- Bluetooth SIG UUID resolution
- Raw BLE data parsing according to specifications
- Characteristic and service implementations
- Metadata properties for HA integration (`device_class`, `state_class`, `unit`)

**Must NOT contain**:
- Any `homeassistant` imports
- HA entity creation logic
- HA-specific configuration
- Direct HA API calls

### 2. Translation Layer (`src/ble_gatt_device/gatt/ha_translation.py`)

**Purpose**: Convert GATT data to Home Assistant-compatible format

### 3. Home Assistant Integration Layer (Future/External)

**Purpose**: Create actual HA entities and handle HA-specific logic

## Validation Rules

The framework includes tests to validate architectural boundaries and ensure clean separation of concerns.

## Benefits of This Architecture

1. **Clean Separation**: Each layer has a single responsibility
2. **Testability**: Each layer can be tested independently
3. **Reusability**: GATT layer can work without HA
4. **Maintainability**: Changes in one layer don't affect others
5. **Extensibility**: Easy to add new characteristics or HA features