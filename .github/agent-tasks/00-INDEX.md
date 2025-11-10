# Agent Tasks Index

**Essential Reading:** 📖 [Bluetooth SIG to Library Mapping](../SIG-MAPPING.md) - Understand how this library directly maps to official Bluetooth SIG specifications.

This directory contains structured tasks for AI agents to systematically improve the Bluetooth SIG Standards Library.

## Quick Navigation

**New to this project?** Start here:
1. 📖 Read [Bluetooth SIG to Library Mapping](../SIG-MAPPING.md) to understand the architecture
2. 📋 Review [Task Matrix](README.md#task-matrix) to see all available work
3. 🎯 Pick a task based on your interest and skill level

## Task Organization

Tasks are organized by SIG specification mapping and priority. Each file contains:
- Clear objectives mapped to SIG components
- Success criteria
- Implementation guidance
- Testing requirements
- Related files and dependencies

## How This Library Maps to Bluetooth SIG

Our library provides a **direct, intuitive mapping** to the official Bluetooth SIG structure:

```
Bluetooth SIG Specifications → Library Components
├── Core Specification
│   ├── Appearance Values      → ⚠️ Task 05: appearance_registry
│   ├── AD Types              → ⚠️ Task 06: ad_types_registry
│   ├── Class of Device       → ⚠️ Task 07: cod_registry
│   └── Company Identifiers   → ⚠️ Task 04: company_registry
├── GATT Specification Supplement
│   ├── Characteristics       → ✅ 96 implemented (Task 17 for more)
│   └── Descriptors          → ✅ Complete
├── Assigned Numbers
│   ├── Service UUIDs        → ✅ service_uuids_registry
│   ├── Characteristic UUIDs → ✅ characteristic_uuids_registry
│   ├── Protocol IDs         → ⚠️ Task 08: protocol_registry
│   └── ...                  → ✅ 11 registries implemented
└── Profiles & Services
    └── Service Definitions  → ✅ 17 implemented (Tasks 16-17 for more)
```

**Legend:** ✅ Complete | ⚠️ Missing (High Priority)

## Priority Levels

- **P0**: Critical issues blocking release
- **P1**: High-priority improvements with significant impact
- **P2**: Medium-priority enhancements
- **P3**: Nice-to-have improvements

## Task Categories

### 1. Core Registries (SIG Mapping) - **CRITICAL PATH**
These complete the direct mapping to official Bluetooth SIG specifications:
- [04-company-identifiers-registry.md](04-company-identifiers-registry.md) - P1 ⚠️ Missing
- [05-appearance-values-registry.md](05-appearance-values-registry.md) - P1 ⚠️ Missing
- [06-ad-types-registry.md](06-ad-types-registry.md) - P1 ⚠️ Missing
- [07-class-of-device-registry.md](07-class-of-device-registry.md) - P2 ⚠️ Missing
- [08-protocol-identifiers-registry.md](08-protocol-identifiers-registry.md) - P2 ⚠️ Missing

### 2. Quality & Technical Debt
- [01-context-support-health-characteristics.md](01-context-support-health-characteristics.md) - P1 ✅ Complete
- [02-improve-test-coverage.md](02-improve-test-coverage.md) - P1 🔴 Not Started
- [03-performance-benchmarking.md](03-performance-benchmarking.md) - P1 🔴 Not Started

### 3. API Enhancement
- [11-async-api-variants.md](11-async-api-variants.md) - P1 ✅ Complete

### 4. Documentation
- [13-tutorial-documentation.md](13-tutorial-documentation.md) - P1 🔴 Not Started

### 5. Coverage Expansion (Future)
- Tasks 09-10, 12, 14-19 (see [README.md](README.md) for complete list)

## Workflow

1. **Select Task**: Choose a task file based on priority and dependencies
2. **Read Requirements**: Review objectives, success criteria, and constraints
3. **Implement**: Follow implementation guidance
4. **Test**: Run tests and validation steps
5. **Document**: Update relevant documentation
6. **Review**: Check success criteria before marking complete

## Dependencies Between Tasks

```
01 (Context Support) ← No dependencies
02 (Test Coverage) ← Should include 01
03 (Performance) ← No dependencies
04 (Property Testing) ← 02 (uses test infrastructure)
05 (Descriptors) ← No dependencies
06 (Async API) ← No dependencies
07 (Service Validation) ← 11 (needs more services)
08 (Tutorials) ← 01, 06 (use completed features)
09 (Cookbook) ← 08 (builds on tutorials)
10 (API Patterns) ← 06 (document async patterns)
11 (Services) ← No dependencies
12 (Characteristics) ← 11 (characteristics need services)
13 (CLI) ← 03, 06 (uses performance and async)
14 (Plugin) ← 11, 12 (plugin infrastructure)
```

## Recommended Execution Order (v0.4.0 Release)

### Phase 1: Core Improvements (Weeks 1-2)
1. Task 01: Context Support ✅ Complete
2. Task 02: Test Coverage 🔴 Not Started
3. Task 03: Performance Benchmarking 🔴 Not Started

### Phase 2: **Registry System (Weeks 3-4) - HIGH USER VALUE**
4. Task 04: Company Identifiers Registry ⚠️ **CRITICAL**
5. Task 05: Appearance Values Registry ⚠️ **CRITICAL**
6. Task 06: AD Types Registry ⚠️ **CRITICAL**

### Phase 3: API & Docs (Weeks 5-6)
7. Task 11: Async API ✅ Complete
8. Task 13: Tutorial Documentation 🔴 Not Started

### Phase 4: Polish (Weeks 7-8)
9. Task 07: Class of Device Registry ⚠️ Classic BT support
10. Task 08: Protocol Identifiers Registry ⚠️ Classic BT support
11. Tasks 09-10: Advanced testing & documentation

**Why Phase 2 is Critical:**
- Completes the direct SIG mapping
- Immediate user value (human-readable data)
- Users see "Apple, Inc." not `0x004C`
- Users see "Generic Watch" not `832`
- Spec-compliant advertising parsing

## Getting Started

For first-time contributors or agents:

1. **Understand the Architecture**: Read [Bluetooth SIG to Library Mapping](../SIG-MAPPING.md)
2. **See the Big Picture**: Review [Task Matrix](README.md#task-matrix)
3. **Start with Documentation**: Task 13 to understand the library
4. **Learn Testing Patterns**: Task 02 to familiarize with testing
5. **Implement Features**: Tasks 04-08 (registry system) provide high user value

## Design Principles

### 1. Direct SIG Mapping
Users should see the SIG spec and immediately know which library component to use:
- **SIG Spec**: "Appearance Values"
- **Library**: `appearance_registry.lookup()`

### 2. User Simplicity
Users shouldn't need to understand internal complexity:
```python
# BAD (current): Raw data
device.appearance = 832

# GOOD (after Task 05): Rich data
device.appearance_info.full_name  # → "Generic Watch"
device.appearance_info.category   # → "Watch"
```

### 3. Framework Agnostic
Works with ANY Bluetooth framework (bleak, simplepyble, pybluez, etc.)

### 4. Type Safe
Complete type hints on all public APIs, return dataclasses not primitives

### 5. Lazy Loading
Parse YAML only when needed for performance

## Notes for AI Agents

When working on tasks:

1. **Read [SIG-MAPPING.md](../SIG-MAPPING.md) first** to understand the architecture
2. **Follow existing patterns**: Study `service_uuids_registry` implementation for registries
3. **Return rich objects**: Never return primitives (int, str), always dataclasses
4. **Lazy load everything**: Use `_ensure_loaded()` with double-checked locking
5. **Type everything**: Complete type hints on all public APIs
6. **Test thoroughly**: Success + 2 failure modes minimum
7. **Run quality gates**: `./scripts/format.sh --check && ./scripts/lint.sh --all && python -m pytest tests/`
8. **Document your changes**: Reference task file in commits: `[Task-04] Add company identifiers registry`
9. **Alpha status**: Breaking changes allowed for best design - prioritize correctness over compatibility
10. **Consult official specs**: Always check Bluetooth SIG documentation before implementing

## Status Overview

| Category | Complete | Missing | Total | Priority |
|----------|----------|---------|-------|----------|
| **Core Registries** | 0/5 | 5 | 5 | ⚠️ **CRITICAL** |
| Assigned Numbers | 11/12 | 1 | 12 | ✅ Mostly complete |
| GATT Characteristics | 96/200+ | 100+ | 200+ | 🟡 Ongoing |
| GATT Services | 17/100+ | 80+ | 100+ | 🟡 Ongoing |

**Next Priority**: Complete Core Registries (Tasks 04-08) for direct SIG mapping and high user value.

## Completion Tracking

### ✅ Complete
- [x] Task 01: Context Support for Health Characteristics
- [x] Task 11: Async API Variants

### 🔴 High Priority (Critical Path)
- [ ] Task 04: Company Identifiers Registry ⚠️ **Direct SIG mapping**
- [ ] Task 05: Appearance Values Registry ⚠️ **Direct SIG mapping**
- [ ] Task 06: AD Types Registry ⚠️ **Direct SIG mapping**
- [ ] Task 02: Improve Test Coverage
- [ ] Task 03: Performance Benchmarking
- [ ] Task 13: Tutorial Documentation

### 🟡 Medium Priority
- [ ] Task 07: Class of Device Registry (Classic BT)
- [ ] Task 08: Protocol Identifiers Registry (Classic BT)

### 📝 Future Tasks (v1.0.0+)
- [ ] Tasks 09-10, 12, 14-19 (See [README.md](README.md) for full list)

## Version Planning

- **v0.4.0**: Tasks 01-10 (Core improvements)
- **v1.0.0**: Tasks 11-14 (Full expansion)
- **v2.0.0**: Plugin ecosystem, bindings
