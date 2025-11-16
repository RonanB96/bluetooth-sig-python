<!-- Architecture overview page (canonical) - copied into a folder so
     relative links to diagrams/ and other docs resolve correctly when
     the page is served at /architecture/.
-->

# Architecture Overview

Understanding the architecture helps you make the most of the Bluetooth SIG Standards
Library.

## Design Philosophy

The library follows these core principles:

1. **Standards First** - Built directly from Bluetooth SIG specifications
1. **Separation of Concerns** - Parse data, don't manage connections
1. **Type Safety** - Strong typing throughout
1. **Framework Agnostic** - Works with any BLE library
1. **Zero Side Effects** - Pure functions for parsing

## High-Level Architecture

```text
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

## Package Structure

[![Package Dependencies](../diagrams/deps/bluetooth_sig.svg)](../diagrams/deps/bluetooth_sig.svg)

## Package Hierarchy

[![Package Hierarchy](../diagrams/svg/packages_bluetooth_sig.svg)](../diagrams/svg/packages_bluetooth_sig.svg)

## Class Hierarchy

[![Class Diagram](../diagrams/svg/classes_bluetooth_sig.svg)](../diagrams/svg/classes_bluetooth_sig.svg)

## Layer Breakdown

The library is organized into four main layers, each with a specific responsibility. This layered architecture ensures clean separation of concerns, making the codebase maintainable and extensible.

### 1. Core API Layer (`src/bluetooth_sig/core/translator.py`)

**Purpose**: High-level, user-facing API that provides the main entry points for parsing Bluetooth SIG data.

This layer acts as the primary interface for users of the library. It coordinates between the lower layers and provides a simple, consistent API for common operations like parsing characteristic data and resolving UUIDs to human-readable names.

**Key Class**: `BluetoothSIGTranslator` - see [Core API](../api/core.md)

**Responsibilities**:

- UUID ↔ Name resolution (converting between Bluetooth UUIDs and descriptive names)
- Characteristic data parsing (taking raw bytes and returning structured, typed data)
- Service information lookup (providing metadata about Bluetooth services)
- Type conversion and validation (ensuring data conforms to Bluetooth SIG specifications)

**Example Usage**:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", data)
```

### 2. GATT Layer (`src/bluetooth_sig/gatt/`)

**Purpose**: Implements the Bluetooth GATT (Generic Attribute Profile) specifications for parsing individual characteristics and services.

This layer contains the actual parsing logic for each Bluetooth SIG characteristic. Each characteristic has its own parser class that handles the specific encoding, validation, and data extraction rules defined in the official Bluetooth specifications.

**Structure**:

```text
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

All characteristic parsers inherit from a common base class that provides standard validation and error handling:

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

Each characteristic implementation provides:

- **Length validation** - Ensures the raw data has the correct number of bytes
- **Range validation** - Checks that parsed values are within specification limits
- **Type conversion** - Converts raw bytes to appropriate Python types (int, float, etc.)
- **Unit handling** - Applies correct scaling factors and units (%, °C, etc.)
- **Error handling** - Raises specific exceptions for different failure modes

### 3. Registry System (`src/bluetooth_sig/registry/`)

**Purpose**: Manages the mapping between Bluetooth UUIDs and their human-readable names, based on official Bluetooth SIG specifications.

The registry system loads and caches the official Bluetooth SIG UUID registry from YAML files. This allows the library to automatically identify characteristics and services without requiring users to memorize cryptic UUID strings.

**Structure**:

```text
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
from bluetooth_sig.gatt.uuid_registry import uuid_registry

# UUID to information
info = uuid_registry.get_characteristic_info("2A19")
# Returns: CharacteristicInfo(uuid="2A19", name="Battery Level")

# Handles both short and long UUID formats
info = uuid_registry.get_service_info("180F")
info = uuid_registry.get_service_info("0000180f-0000-1000-8000-00805f9b34fb")
```

### 4. Type System (`src/bluetooth_sig/types/`)

**Purpose**: Defines the data structures, enums, and type hints used throughout the library for type safety and consistency.

This layer provides strongly-typed representations of Bluetooth concepts, ensuring that data is validated at both runtime and compile-time (with mypy).

**Key Components**:

#### Enums

Type-safe enumerations for characteristic and service names:

```python
from bluetooth_sig.types.gatt_enums import (
     CharacteristicName,
     ServiceName,
)

# Strongly-typed enum values
CharacteristicName.BATTERY_LEVEL  # "Battery Level"
ServiceName.BATTERY               # "Battery"
```

#### Data Structures

Immutable msgspec structs for parsed characteristic data:

```python
import msgspec

class CharacteristicData(msgspec.Struct, kw_only=True):
    """Parse result container with back-reference to characteristic."""
    characteristic: BaseCharacteristic
    value: Any | None = None  # Parsed value (int, float, or complex struct)
    raw_data: bytes = b""
    parse_success: bool = False
    error_message: str = ""
```

For complex characteristics, the `value` field contains specialized structs:

```python
class HeartRateData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed heart rate measurement data."""
    heart_rate: int  # BPM
    sensor_contact: SensorContactState
    energy_expended: int | None = None  # kJ
    rr_intervals: tuple[float, ...] = ()  # R-R intervals in seconds
```

## Data Flow

### Parsing Flow

```text
1. Raw BLE Data
   ↓
2. BluetoothSIGTranslator.parse_characteristic()
   ↓
3. Registry lookup (UUID → Characteristic class)
   ↓
4. Characteristic.decode_value()
   ├─ Length validation
   ├─ Data extraction
   ├─ Range validation
   └─ Type conversion
   ↓
5. Typed Result (msgspec struct/primitive)
```

### Example Data Flow

```python
# Input: Raw bytes
raw_data = bytearray([0x64, 0x09])  # Temperature data

# Step 1: Call translator
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A6E", raw_data)

# Internal flow:
# 1. Registry resolves "2A6E" → TemperatureCharacteristic
# 2. TemperatureCharacteristic.decode_value(raw_data)
#    - Validates length (must be 2 bytes)
#    - Extracts int: 2404 (little-endian)
#    - Validates range
#    - Applies scaling: 2404 * 0.01 = 24.04°C
# 3. Returns CharacteristicData with value: 24.04

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
          return data[0]

class TemperatureCharacteristic(BaseCharacteristic):
     def decode_value(self, data: bytearray) -> float:
          # Temperature-specific parsing
          return int.from_bytes(data, byteorder='little') * 0.01
```

### 2. Registry Pattern

Central registry for UUID → implementation mapping:

```python
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry

char_class = CharacteristicRegistry.create_characteristic("2A19")
result = char_class.decode_value(data)
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
# SKIP: Example code with placeholder UUID - not executable
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
from bluetooth_sig.gatt.services.base import BaseGattService

class MyCustomService(BaseGattService):
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
from bluetooth_sig import BluetoothSIGTranslator

def test_battery_parsing():
     translator = BluetoothSIGTranslator()
     result = translator.parse_characteristic("2A19", bytearray([85]))
     assert result.value == 85
```

## Performance Considerations

### Optimizations

- **msgspec structs** - High-performance serialization/deserialization
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

- [API Reference](../api/core.md) - Detailed API documentation
- [Adding Characteristics](../guides/adding-characteristics.md) - Extend the library
- [Performance Guide](../guides/performance.md) - Optimization tips
- [Usage Guide](../usage.md) - Practical examples

