# Workstream 1: God Class Decomposition Plan

**Goal**: Decompose 4 God classes using **composition + delegation**. Preserve all public APIs. No logic duplication. Single source of truth per concern.

**Execution order**: Step 3 → Step 1 → Step 4 → Step 2 (simplest first, most complex last).

---

## Step 1: Split `BluetoothSIGTranslator` (1,359 lines → ~682 line facade) — ✅ COMPLETE

The class is nearly stateless — only `_services: dict` is mutable. All other methods delegate to static registries. Pattern: **Composition + Delegation Facade** (like `requests.Session`).

### 1.1 New delegate modules under `src/bluetooth_sig/core/`

| New file | Class | Methods moved from translator.py | Mutable state |
|---|---|---|---|
| `core/query.py` | `CharacteristicQueryEngine` | `supports`, `get_value_type`, all 8 `get_*_info_*`, `get_characteristics_info_by_uuids`, `list_supported_*`, `get_service_characteristics`, `get_sig_info_by_name`, `get_sig_info_by_uuid` | None |
| `core/parser.py` | `CharacteristicParser` | `parse_characteristic` (+overloads), `parse_characteristics` (batch), 5 `_*` batch helpers | None |
| `core/encoder.py` | `CharacteristicEncoder` | `encode_characteristic` (+overloads), `create_value`, `validate_characteristic_data`, `_get_characteristic_value_type_class` | None |
| `core/registration.py` | `RegistrationManager` | `register_custom_characteristic_class`, `register_custom_service_class` | None (writes to registries) |
| `core/service_manager.py` | `ServiceManager` | `process_services`, `get_service_by_uuid`, `discovered_services`, `clear_services` | `_services: dict` — **only mutable state** |

### 1.2 Facade pattern

`BluetoothSIGTranslator.__init__` creates 5 delegate instances eagerly. Every public method becomes a one-line delegation with identical signature and `@overload` decorators. Async wrappers stay on facade. Singleton `__new__`/`get_instance()`/global `BluetoothSIG` stay.

### 1.3 Update `core/__init__.py`

Re-export delegate classes alongside `BluetoothSIGTranslator` and `AsyncParsingSession`.

---

## Step 2: Split `BaseCharacteristic` (1,761 lines → 1,258 lines) — ✅ COMPLETE

Keeps Template Method contract (`_decode_value`/`_encode_value`). Internal composition invisible to ~150 subclasses. Pattern: **Internal Composition with back-reference**.

### 2.1 New `pipeline/` package under `src/bluetooth_sig/gatt/characteristics/`

| New file | Class | Methods extracted | Status |
|---|---|---|---|
| `pipeline/__init__.py` | Re-exports | — | ✅ |
| `pipeline/parse_pipeline.py` | `ParsePipeline` | `parse_value` orchestration, `_perform_parse_validation`, `_extract_and_check_special_value`, `_decode_and_validate_value`, `_extract_raw_int`, `_check_special_value`, `_is_parse_trace_enabled` | ✅ |
| `pipeline/encode_pipeline.py` | `EncodePipeline` | `build_value` orchestration, `_pack_raw_int`, `encode_special`, `encode_special_by_meaning` | ✅ |
| `pipeline/validation.py` | `CharacteristicValidator` | `_validate_range` (3-level precedence), `_validate_type`, `_validate_length` | ✅ |

### 2.2 Additional extractions

| New file | Class | Methods extracted | Status |
|---|---|---|---|
| `role_classifier.py` | `classify_role()` function | `_classify_role`, `_spec_has_unit_fields` | ✅ |
| `descriptor_support.py` | `DescriptorSupport` | 11 descriptor methods | Deferred — low value, methods are 1-liner proxies |
| `special_values.py` | `SpecialValueHandler` | special value methods | Deferred — already uses SpecialValueResolver |

### 2.3 What stays on `BaseCharacteristic`

- `__init__`/`__post_init__` (composition wiring)
- Properties: `uuid`, `info`, `spec`, `name`, `description`, `display_name`, `unit`, `size`, `value_type_resolved`, `role`, `get_byte_order_hint`
- Abstract: `_decode_value`, `_encode_value` (Template Method hooks for subclasses)
- Thin delegation: `parse_value` → `ParsePipeline.run()`, `build_value` → `EncodePipeline.run()`, `encode_special*` → `EncodePipeline`
- Class-level UUID resolution (5 classmethods)
- Dependency resolution (5 methods)
- YAML metadata accessors (5 methods)
- Descriptor methods (kept in base, 1-liner proxies to descriptor_utils)
- Special value properties (kept in base, delegate to SpecialValueResolver)
- YAML metadata accessors (5 methods)
- Proxy methods for backward compat (delegate to composed objects)

---

## Step 3: Split `templates.py` (1,488 lines → package) — ✅ COMPLETE

No circular dependencies. Pure file reorganisation + re-export. Pattern: **Module → Package promotion**.

### 3.1 New `templates/` package

| New file | Classes | Approx lines |
|---|---|---|
| `templates/__init__.py` | Re-exports everything via explicit imports + `__all__` | ~60 |
| `templates/base.py` | `CodingTemplate[T_co]` (ABC), resolution constants | ~100 |
| `templates/data_structures.py` | `VectorData`, `Vector2DData`, `TimeData` | ~40 |
| `templates/numeric.py` | `Uint8Template`, `Sint8Template`, `Uint16Template`, `Sint16Template`, `Uint24Template`, `Uint32Template` | ~200 |
| `templates/scaled.py` | `ScaledTemplate` (abstract) + 8 `Scaled*Template` variants + `PercentageTemplate` | ~400 |
| `templates/domain.py` | `TemperatureTemplate`, `ConcentrationTemplate`, `PressureTemplate` | ~200 |
| `templates/ieee_float.py` | `IEEE11073FloatTemplate`, `Float32Template` | ~80 |
| `templates/string.py` | `Utf8StringTemplate`, `Utf16StringTemplate` | ~150 |
| `templates/complex.py` | `TimeDataTemplate`, `VectorTemplate`, `Vector2DTemplate` | ~200 |
| `templates/enum.py` | `EnumTemplate[T]` | ~240 |

### 3.2 Backward compat

Python resolves `from .templates import X` identically whether `templates` is a module or package — as long as `X` is in the package `__init__.py`. Zero characteristic files need changing.

---

## Step 4: Split `Device` (1,172 lines → ~818 lines) — ✅ COMPLETE

13/40 methods are pure delegation. Substantial logic in dependency resolution and characteristic I/O. Pattern: **Composition with explicit dependencies (no back-references)**.

### 4.1 New modules under `src/bluetooth_sig/device/`

| New file | Class | Methods extracted |
|---|---|---|
| `dependency_resolver.py` | `DependencyResolver` + `DependencyResolutionMode` enum | `_resolve_single_dependency`, `_ensure_dependencies_resolved` |
| `characteristic_io.py` | `CharacteristicIO` | `read` (+overloads), `write` (+overloads), `start_notify` (+overloads), `stop_notify`, `read_multiple`, `write_multiple`, `_resolve_characteristic_name` |

### 4.2 Device composes

```python
self._dep_resolver = DependencyResolver(connection_manager, translator, self.connected)
self._char_io = CharacteristicIO(connection_manager, translator, self.connected, self._dep_resolver)
```

Remaining on Device: delegation one-liners, discovery, advertising, properties, service queries.

---

## Verification (after each step)

1. `python -m pytest tests/ -v` — all existing tests pass
2. `./scripts/lint.sh --all` — zero errors
3. `./scripts/format.sh --check` — formatting valid
4. Backward compat imports still work

## Design Principles

| Principle | Application |
|---|---|
| **Single Responsibility** | Each delegate/composed class owns one concern |
| **DRY** | Each method exists in exactly one place; facade only delegates |
| **Composition over Inheritance** | Translator: 5 delegates. Base: internal composition. Templates: domain grouping |
| **Single Source of Truth** | Registry access per delegate. Validation in one validator. Pipeline in one orchestrator |
| **Open/Closed** | BaseCharacteristic open for extension (override hooks), closed for modification (pipeline internal) |
| **Dependency Inversion** | Delegates take abstractions (registries, protocols), not concretions |
| **Interface Segregation** | QueryEngine separate from Parser — consumers depend only on what they use |
