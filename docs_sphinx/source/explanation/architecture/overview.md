# Architecture Documentation

This section contains architecture documentation for contributors and maintainers.

## Documentation Structure

```mermaid
graph TB
    A[Architecture Overview<br/>You are here] --> B[Design Decisions]
    A --> C[Deep Dive Guides]

    B --> B1[decisions.md<br/>Why we made key choices]

    C --> C1[internals.md<br/>Internal implementation details]
    C --> C2[registry-system.md<br/>UUID registry deep dive]

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
```

## Core Architecture Principles

### Framework-Agnostic Design

- Zero dependencies on BLE backends (bleak, simplepyble, etc.)
- Accepts `bytes`, returns typed Python objects
- You manage connections, we handle parsing

### Standards-Driven Parsing

- All logic follows official Bluetooth SIG specifications
- YAML data loaded from `bluetooth_sig/` git submodule
- Automatic compliance with specification updates

### Type Safety

- Complete type hints on all public APIs
- Dataclasses for structured data (no raw `dict`/`tuple`)
- Validation during parsing, not at usage time

### Lazy Loading with Thread Safety

- Registry data loads on first access
- Double-checked locking for concurrent safety
- Minimal startup overhead

## Key Patterns

| Pattern | Purpose | Location |
|---------|---------|----------|
| **Registry Pattern** | Dynamic discovery of characteristics | [internals.md](internals.md) |
| **Singleton Pattern** | Single translator/registry instances | [internals.md](internals.md) |
| **Template Method** | Abstract parsing contracts | [internals.md](internals.md) |
| **Lazy Initialization** | On-demand data loading | [registry-system.md](registry-system.md) |

## System Layers

```mermaid
graph TB
    subgraph API["Public API"]
        T[BluetoothSIGTranslator<br/>Single entry point]
    end

    subgraph Char["Characteristic Parsing"]
        B[BaseCharacteristic<br/>Abstract base]
        S[70+ SIG Characteristics]
        C[Custom Characteristics]
    end

    subgraph Reg["Registry System"]
        CR[CharacteristicRegistry]
        UR[UuidRegistry]
    end

    subgraph Data["Data Source"]
        Y[Bluetooth SIG YAML Files]
    end

    T --> B
    T --> CR
    CR --> S
    CR --> C
    S --> B
    C --> B
    B --> UR
    UR --> Y

    style API fill:#e3f2fd
    style Char fill:#fff3e0
    style Reg fill:#f3e5f5
    style Data fill:#e8f5e9
```

## Documentation Map

### For Understanding Design

- **[Design Decisions](decisions.md)** - Architectural Decision Records explaining why key choices were made

### For Implementation Details

- **[Internal Architecture](internals.md)** - Detailed implementation of core systems
- **[Registry System](registry-system.md)** - Deep dive into UUID registry and YAML loading

### For Contributing

- **[Adding Characteristics](../../how-to/adding-characteristics.md)** - Step-by-step guide for new characteristics
- **[Contributing Guide](../../how-to/contributing.md)** - Development setup and workflows

### For Performance

- **[Performance Guide](../../how-to/performance-tuning.md)** - Optimization techniques
- **[Benchmarks](../../reference/benchmarks.md)** - Live benchmark results

## Visual Diagrams

### Package Dependencies

[![Package Dependencies](../../diagrams/deps/bluetooth_sig.svg)](../../diagrams/deps/bluetooth_sig.svg)

### Package Hierarchy

[![Package Hierarchy](../../diagrams/svg/packages_bluetooth_sig.svg)](../../diagrams/svg/packages_bluetooth_sig.svg)

### Class Hierarchy

[![Class Diagram](../../diagrams/svg/classes_bluetooth_sig.svg)](../../diagrams/svg/classes_bluetooth_sig.svg)
