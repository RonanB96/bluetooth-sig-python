# Architectural Decision Records

This document explains key architectural decisions made in the bluetooth-sig-python library.

## ADR-001: Registry-Driven Resolution

**Context**: Need to support 70+ Bluetooth SIG characteristics without manual UUID mapping.

**Decision**: Automatic discovery via `pkgutil.walk_packages()` with enum-based registry.

**Rationale**:

- Adding a new characteristic requires zero boilerplate
- Compile-time safety through enum validation
- Registry stays synchronized with implementation automatically

**Consequences**:

- ✅ Zero maintenance overhead for UUID mappings
- ✅ Type-safe characteristic lookups
- ⚠️ First access incurs 10-50ms discovery cost (one-time)

**Alternatives Considered**:

- Manual UUID dictionary: High maintenance, error-prone
- Module-level registration: Requires explicit imports

## ADR-002: Double-Checked Locking for Lazy Initialization

**Context**: Registry initialization is expensive but must be thread-safe in concurrent applications.

**Decision**: Implement double-checked locking pattern with `threading.RLock`.

**Rationale**:

- Most accesses are reads after initialization
- Lock contention should only occur during first access
- RLock allows reentrant calls from same thread

**Consequences**:

- ✅ Lock-free reads after initialization (<0.1ms)
- ✅ Thread-safe lazy loading
- ⚠️ Slightly more complex initialization code

**Performance**:

- Cold (first access): 10-50ms (one-time cost)
- Warm (subsequent): <0.1ms (lock-free fast path)

## ADR-003: Template Composition Over Inheritance

**Context**: Many characteristics share identical parsing logic (uint16, float32, etc.).

**Decision**: Use composition with `_template` attribute instead of inheritance hierarchies.

**Rationale**:

- Avoids deep inheritance trees
- Templates are reusable and testable independently
- Clear separation: template handles encoding, characteristic handles validation

**Consequences**:

- ✅ Flat class hierarchy
- ✅ Reusable parsing strategies
- ✅ Easy to test templates independently
- ⚠️ Slight indirection in understanding data flow

**Example**:

```python
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.templates import ScaledSint16Template


class Temperature(BaseCharacteristic):
    _template = ScaledSint16Template(scale_factor=0.01)  # Composition
    expected_length = 2


# Little-endian: [low_byte, high_byte] = [0x00, 0x0A] = 0x0A00 = 2560
# 2560 * 0.01 = 25.6°C
temperature_data = bytearray([0x00, 0x0A])  # 2560 in little-endian
temp_char = Temperature()
result = temp_char.decode_value(temperature_data)
print(f"Temperature: {result}°C")  # Temperature: 25.6°C
```

## ADR-004: Declarative Validation

**Context**: Manual validation in every `decode_value()` method is verbose and inconsistent.

**Decision**: Use class-level validation attributes that `BaseCharacteristic` enforces.

**Rationale**:

- DRY principle: validation logic in one place
- Consistent error messages across all characteristics
- Self-documenting: attributes describe constraints clearly

**Consequences**:

- ✅ Reduced boilerplate in characteristic implementations
- ✅ Consistent validation behaviour
- ✅ Easy to understand constraints
- ⚠️ Less flexibility for complex conditional validation

**Validation Attributes**:

- `expected_length`: Enforce exact byte length
- `min_value` / `max_value`: Range validation
- `allowed_values`: Whitelist specific values

## ADR-005: Framework-Agnostic Design

**Context**: Users integrate with diverse BLE libraries (bleak, simplepyble, bluepy, etc.).

**Decision**: Never import BLE backend libraries in `src/bluetooth_sig/` code.

**Rationale**:

- Avoids coupling to specific BLE library versions
- Users choose their preferred connection manager
- Library focuses on standards interpretation only

**Consequences**:

- ✅ Works with any BLE library
- ✅ No dependency version conflicts
- ✅ Clear separation of concerns
- ⚠️ Users must handle connection management separately

**Boundary**:

```text
User's BLE Library → bytes → bluetooth-sig → structured data
```

## ADR-006: Bluetooth SIG Git Submodule

**Context**: Need authoritative Bluetooth SIG specification data.

**Decision**: Use official `bluetooth_sig/` repository as git submodule.

**Rationale**:

- Single source of truth for UUID definitions
- Automatic updates when Bluetooth SIG publishes changes
- No manual YAML maintenance

**Consequences**:

- ✅ Always synchronized with official specifications
- ✅ Zero maintenance for UUID registry
- ⚠️ Adds ~5MB to repository size

**Mitigation**: Clear documentation in README and setup guides.

## ADR-007: msgspec for Data Structures

**Context**: Need fast, type-safe data structures for parsed results.

**Decision**: Use `msgspec.Struct` for characteristic data classes.

**Rationale**:

- 5-10x faster than standard dataclasses
- Compact memory representation
- Built-in validation and type checking
- JSON serialization support

**Consequences**:

- ✅ Excellent performance
- ✅ Strong typing with runtime validation
- ✅ Easy JSON serialization for APIs
- ⚠️ Additional dependency

## ADR-008: Progressive API Levels

**Context**: Users have varying needs from simple parsing to advanced customization.

**Decision**: Provide four progressive API levels without breaking changes.

**Rationale**:

- Low barrier to entry (Level 1: direct characteristic usage)
- Advanced features available when needed
- Backward compatible across levels

**API Levels**:

1. Direct characteristic parsing
2. UUID-based parsing via translator
3. Metadata queries without parsing
4. Custom characteristic registration

**Consequences**:

- ✅ Easy for beginners
- ✅ Powerful for advanced users
- ✅ No breaking changes when advancing levels

## ADR-009: Lazy YAML Loading

**Context**: Loading all Bluetooth SIG YAML files at startup is slow.

**Decision**: Load YAML files on first access per registry type.

**Rationale**:

- Most applications only use subset of characteristics
- Startup time must be minimal
- Trade startup time for runtime overhead

**Consequences**:

- ✅ Fast application startup
- ✅ Load only what's needed
- ⚠️ First UUID lookup is slower (10-30ms)

**Optimization**: YAML loading is cached after first access.

## ADR-010: Singleton Pattern for Translators

**Context**: Multiple translator instances would cause unnecessary resource duplication.

**Decision**: Implement singleton pattern for `BluetoothSIGTranslator` and registries.

**Rationale**:

- Registry data should be shared across application
- Prevent memory waste from duplicate YAML loading
- Simplify API (no need to pass translator instances)

**Consequences**:

- ✅ Efficient resource usage
- ✅ Simple API (`get_instance()`)
- ✅ Consistent state across application
- ⚠️ Global state (acceptable for read-only registry data)

## Summary

These architectural decisions prioritize:

1. **Performance**: Lazy loading, caching, efficient data structures
2. **Maintainability**: Auto-discovery, declarative patterns, DRY
3. **Flexibility**: Framework-agnostic, progressive APIs
4. **Standards Compliance**: Official Bluetooth SIG data source

For implementation details, see [Internal Architecture](internals.md).
