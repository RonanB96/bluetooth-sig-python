# Architecture Overview

Understanding the architecture helps you make the most of the Bluetooth SIG Standards Library.

## Design Philosophy

The library follows these core principles:

1. **Standards First** - Built directly from Bluetooth SIG specifications
2. **Separation of Concerns** - Parse data, don't manage connections
3. **Type Safety** - Strong typing throughout
4. **Framework Agnostic** - Works with any BLE library
5. **Zero Side Effects** - Pure functions for parsing

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Your Application                        │
│            (GUI, Business Logic, State)                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              bluetooth-sig Library                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Core API (BluetoothSIGTranslator)      │  │
│  │  • UUID Resolution    • Name Resolution           │  │
│  │  • Data Parsing       • Type Conversion           │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              GATT Layer                           │  │
│  │  • Characteristic Parsers (70+ implementations)   │  │
│  │  • Service Definitions                            │  │
│  │  • Validation Logic                               │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Registry System                         │  │
│  │  • UUID Registry (YAML-based)                     │  │
│  │  • Name Resolution                                │  │
│  │  • Official SIG Specifications                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│         BLE Connection Library (bleak, etc.)             │
│            (Your Choice - Not Part of Library)           │
└─────────────────────────────────────────────────────────┘
```

## Layer Breakdown

### 1. Core API Layer (`src/bluetooth_sig/core.py`)

**Purpose**: High-level, user-facing API

**Key Class**: `BluetoothSIGTranslator`

**Responsibilities**:
- UUID ↔ Name resolution
- Characteristic data parsing
- Service information lookup
- Type conversion and validation

**Example Usage**:
```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic_data("2A19", data)
```

### 2. GATT Layer (`src/bluetooth_sig/gatt/`)

**Purpose**: Bluetooth GATT specification implementation

**Structure**:
```
gatt/
├── characteristics/    # 70+ characteristic implementations
│   ├── base.py        # Base characteristic class
│   ├── battery_level.py
│   ├── temperature.py
│   ├── humidity.py
│   └── ...
├── services/          # Service definitions
│   ├── base.py
│   ├── battery_service.py
│   └── ...
└── exceptions.py      # GATT-specific exceptions
```

**Key Components**:

#### Base Characteristic
```python
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

class BatteryLevelCharacteristic(BaseCharacteristic):
    def decode_value(self, data: bytearray) -> int:
        # Standards-compliant parsing
        if len(data) != 1:
            raise InsufficientDataError("Battery Level requires 1 byte")
        value = int(data[0])
        if not 0 <= value <= 100:
            raise ValueRangeError("Battery must be 0-100%")
        return value
```

#### Characteristic Features
- **Length validation** - Ensures correct data size
- **Range validation** - Enforces spec limits
- **Type conversion** - Raw bytes → typed values
- **Unit handling** - Applies correct scaling
- **Error handling** - Clear, specific exceptions

### 3. Registry System (`src/bluetooth_sig/registry/`)

**Purpose**: UUID and name resolution based on official Bluetooth SIG registry

**Structure**:
```
registry/
├── yaml_cross_reference.py  # YAML registry loader
├── uuid_registry.py          # UUID resolution
└── name_resolver.py          # Name-based lookup
```

**Data Source**: 
- Official Bluetooth SIG YAML files (via git submodule)
- Located in `bluetooth_sig/assigned_numbers/uuids/`

**Capabilities**:
```python
# UUID to information
info = registry.get_characteristic_info("2A19")
# Returns: CharacteristicInfo(uuid="2A19", name="Battery Level")

# Name to UUID
uuid = registry.resolve_name("Battery Level")
# Returns: "2A19"

# Handles both short and long UUID formats
info = registry.get_service_info("180F")
info = registry.get_service_info("0000180f-0000-1000-8000-00805f9b34fb")
```

### 4. Type System (`src/bluetooth_sig/types/`)

**Purpose**: Type definitions, enums, and data structures

**Key Components**:

#### Enums
```python
from bluetooth_sig.types.gatt_enums import (
    CharacteristicName,
    ServiceName,
)

# Strongly-typed enum values
CharacteristicName.BATTERY_LEVEL  # "Battery Level"
ServiceName.BATTERY_SERVICE        # "Battery Service"
```

#### Data Structures
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class BatteryLevelData:
    value: int
    unit: str = "%"
```

## Data Flow

### Parsing Flow

```
1. Raw BLE Data
   ↓
2. BluetoothSIGTranslator.parse_characteristic_data()
   ↓
3. Registry lookup (UUID → Characteristic class)
   ↓
4. Characteristic.decode_value()
   ├─ Length validation
   ├─ Data extraction
   ├─ Range validation
   └─ Type conversion
   ↓
5. Typed Result (dataclass/primitive)
```

### Example Data Flow

```python
# Input: Raw bytes
raw_data = bytearray([0x64, 0x09])  # Temperature data

# Step 1: Call translator
translator = BluetoothSIGTranslator()
result = translator.parse_characteristic_data("2A6E", raw_data)

# Internal flow:
# 1. Registry resolves "2A6E" → TemperatureCharacteristic
# 2. TemperatureCharacteristic.decode_value(raw_data)
#    - Validates length (must be 2 bytes)
#    - Extracts int: 2404 (little-endian)
#    - Validates range
#    - Applies scaling: 2404 * 0.01 = 24.04°C
# 3. Returns typed float: 24.04

# Output: Parsed value
print(result.value)  # 24.04
```

## Key Design Patterns

### 1. Strategy Pattern

Each characteristic is a strategy for parsing specific data:

```python
class BaseCharacteristic:
    def decode_value(self, data: bytearray) -> Any:
        raise NotImplementedError

class BatteryLevelCharacteristic(BaseCharacteristic):
    def decode_value(self, data: bytearray) -> int:
        # Battery-specific parsing

class TemperatureCharacteristic(BaseCharacteristic):
    def decode_value(self, data: bytearray) -> float:
        # Temperature-specific parsing
```

### 2. Registry Pattern

Central registry for UUID → implementation mapping:

```python
registry = UUIDRegistry()
char_class = registry.get_characteristic_class("2A19")
parser = char_class()
result = parser.decode_value(data)
```

### 3. Validation Pattern

Multi-layer validation:

```python
def decode_value(self, data: bytearray) -> int:
    # Layer 1: Structure validation
    if len(data) != 1:
        raise InsufficientDataError(...)
    
    # Layer 2: Data extraction
    value = int(data[0])
    
    # Layer 3: Domain validation
    if not 0 <= value <= 100:
        raise ValueRangeError(...)
    
    return value
```

## Extension Points

### Adding Custom Characteristics

```python
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

class MyCustomCharacteristic(BaseCharacteristic):
    _info = CharacteristicInfo(
        uuid=BluetoothUUID("XXXX"),
        name="My Custom Characteristic"
    )
    
    def decode_value(self, data: bytearray) -> int:
        # Your parsing logic
        return int(data[0])
```

### Custom Services

```python
from bluetooth_sig.gatt.services.base import BaseService

class MyCustomService(BaseService):
    def __init__(self):
        super().__init__()
        self.my_char = MyCustomCharacteristic()
    
    @property
    def characteristics(self) -> dict:
        return {"my_char": self.my_char}
```

## Testing Architecture

### Unit Tests
- Individual characteristic parsing
- Registry resolution
- Validation logic

### Integration Tests
- Full parsing flow
- Multiple characteristics
- Error handling

### Example
```python
def test_battery_parsing():
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic_data("2A19", bytearray([85]))
    assert result.value == 85
```

## Performance Considerations

### Optimizations
- **Registry caching** - UUID lookups cached after first resolution
- **Minimal allocations** - Direct parsing without intermediate objects
- **Type hints** - Enable JIT optimization
- **Lazy loading** - Characteristics loaded on-demand

### Benchmarks
- UUID resolution: ~10 μs
- Simple characteristic parse: ~50 μs
- Complex characteristic parse: ~200 μs

## Architectural Benefits

### 1. Maintainability
- Clear separation of concerns
- Each characteristic is independent
- Easy to add new characteristics

### 2. Testability
- Pure functions (no side effects)
- Easy to mock
- No hardware required for testing

### 3. Flexibility
- Framework agnostic
- Platform independent
- Extensible design

### 4. Type Safety
- Full type hints
- Runtime validation
- Compile-time checking (mypy)

## Comparison with Alternatives

| Aspect | This Library | Bleak | PyBluez | DIY |
|--------|-------------|-------|---------|-----|
| **Focus** | Standards parsing | Connection | Connection | Whatever you build |
| **UUID Registry** | ✅ Official | ❌ Manual | ❌ Manual | ❌ Manual |
| **Type Safety** | ✅ Full | ⚠️ Partial | ❌ None | ⚠️ Depends |
| **BLE Connection** | ❌ Not included | ✅ Full | ✅ Full | ⚠️ Depends |
| **Validation** | ✅ Automatic | ❌ Manual | ❌ Manual | ⚠️ Depends |

## Next Steps

- [API Reference](api/core.md) - Detailed API documentation
- [Adding Characteristics](guides/adding-characteristics.md) - Extend the library
- [Performance Guide](guides/performance.md) - Optimization tips
- [Usage Guide](usage.md) - Practical examples
