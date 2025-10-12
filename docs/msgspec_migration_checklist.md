# msgspec Migration Checklist

This document tracks the migration of characteristic data models from Python dataclasses to msgspec.Struct for performance improvements.

**Target**: 2-4x faster struct creation, 2-4x faster equality comparisons, ~15% less memory usage

## Migration Status

### Phase 1: Foundation ✅ COMPLETE
- [x] Add msgspec dependency to pyproject.toml
- [x] Create performance benchmark (shows 2.7-3.6x speedup)
- [x] Migrate first characteristic (HeartRateData) as proof-of-concept
- [x] Verify all tests pass

### Phase 2: Simple Characteristics (1-3 fields)

- [ ] `ElectricCurrentRangeData` - 2 fields (min, max)
- [ ] `ElectricCurrentSpecificationData` - 3 fields (minimum, maximum, typical)
- [ ] `ElectricCurrentStatisticsData` - 3 fields (average, minimum, maximum)
- [ ] `VoltageSpecificationData` - 2 fields (minimum, maximum)
- [ ] `VoltageStatisticsData` - 2 fields (minimum, maximum)
- [ ] `SupportedPowerRangeData` - 2 fields (minimum, maximum)
- [ ] `PulseOximetryData` - 2 fields (spo2, pulse_rate)
- [ ] `TimezoneInfo` - 2 fields (description, offset_hours)
- [ ] `DSTOffsetInfo` - 2 fields (description, offset_hours)
- [ ] `VectorData` - 3 fields (x_axis, y_axis, z_axis)
- [ ] `Vector2DData` - 2 fields (x_axis, y_axis)

### Phase 3: Medium Characteristics (4-6 fields)

- [x] `HeartRateData` - 5 fields ✅ DONE
- [ ] `CSCMeasurementData` - 5 fields (flags, wheel_revolutions, wheel_event_time, crank_revolutions, crank_event_time)
- [ ] `RSCMeasurementData` - 4 fields (speed, cadence, stride_length, distance)
- [ ] `CrankRevolutionData` - 2 fields (crank_revolutions, last_crank_event_time)
- [ ] `LocalTimeInformationData` - 2 fields (timezone, dst_offset)
- [ ] `TemperatureMeasurementData` - 4 fields (temperature, unit, timestamp, type)
- [ ] `BloodPressureFeatureData` - 6 fields (features_bitmap, body_movement, cuff_fit, irregular_pulse, etc.)

### Phase 4: Complex Characteristics (7+ fields)

- [ ] `BatteryPowerStateData` - 8 fields
- [ ] `BatteryPowerState` - 7 fields
- [ ] `BloodPressureData` - 9 fields
- [ ] `BodyCompositionFeatureData` - 10+ fields
- [ ] `BodyCompositionMeasurementData` - 15+ fields
- [ ] `CyclingPowerControlPointData` - 8+ fields
- [ ] `CyclingPowerMeasurementData` - 12+ fields
- [ ] `CyclingPowerVectorData` - 8+ fields
- [ ] `GlucoseFeatureData` - 8+ fields
- [ ] `GlucoseMeasurementData` - 10+ fields
- [ ] `GlucoseMeasurementContextData` - 10+ fields

### Phase 5: Core Data Types

These are in `src/bluetooth_sig/types/data_types.py` and used across the library:

- [ ] `ParseFieldError` - frozen dataclass, 4 fields
- [ ] `SIGInfo` - 3 fields (base class)
- [ ] `CharacteristicInfo` - 6 fields (extends SIGInfo)
- [ ] `ServiceInfo` - 4 fields (extends SIGInfo)
- [ ] `CharacteristicData` - 8 fields (complex with properties)
- [ ] `ValidationResult` - 5 fields
- [ ] `CharacteristicRegistration` - 6 fields
- [ ] `ServiceRegistration` - 4 fields

### Phase 6: Context Types

These are in `src/bluetooth_sig/types/context.py`:

- [ ] `DeviceInfo` - 4 fields
- [ ] `CharacteristicContext` - 4 fields

### Phase 7: Service Base Types

These are in `src/bluetooth_sig/gatt/services/base.py`:

- [ ] Service-related dataclasses (if any)

## Migration Pattern

For each dataclass conversion:

1. **Import Change**:
   ```python
   # BEFORE
   from dataclasses import dataclass, field
   
   # AFTER
   import msgspec
   ```

2. **Class Definition**:
   ```python
   # BEFORE
   @dataclass
   class MyData:
       field1: int
       field2: list[str] = field(default_factory=list)
   
   # AFTER
   class MyData(msgspec.Struct, frozen=True, kw_only=True):
       field1: int
       field2: tuple[str, ...] = ()  # Use tuple for immutable default
   ```

3. **Keep `__post_init__`**: Validation logic works identically
4. **Update Lists to Tuples**: For frozen structs, use tuples for sequences
5. **Run Tests**: Ensure all tests pass after each conversion
6. **Run Linting**: Ensure code quality is maintained

## Testing Requirements

For each converted characteristic:

- [x] Existing tests must pass without modification
- [ ] Add immutability test (attempt to modify frozen field)
- [ ] Add equality test (compare two identical structs)
- [ ] Add keyword-only test (verify positional args rejected)
- [ ] Verify round-trip encode/decode still works

## Performance Validation

After completing migrations:

- [ ] Run comprehensive benchmark suite
- [ ] Validate 2-4x speedup in struct creation
- [ ] Validate 2-4x speedup in equality comparisons
- [ ] Document results in `benchmarks/RESULTS.md`

## Documentation Updates

- [ ] Update `docs/usage.md` with msgspec examples
- [ ] Update `docs/ARCHITECTURE.md` with msgspec rationale
- [ ] Ensure all public classes have complete docstrings
- [ ] Add inline comments for msgspec-specific patterns

## Non-Goals (Out of Scope)

- ❌ Do NOT change parsing logic in `decode_value()` methods
- ❌ Do NOT modify the `DataParser` utility class  
- ❌ Do NOT change public API method signatures
- ❌ Do NOT add web framework integrations
- ❌ Do NOT migrate service definitions (only characteristic data models)

## Success Criteria

- ✅ All dataclass models converted to msgspec.Struct
- ✅ All 914+ tests pass
- ✅ All linting passes (ruff, pylint, mypy)
- ✅ Measurable 2-4x performance improvement
- ✅ Test coverage ≥95% maintained
- ✅ No breaking changes to public API

---

**Last Updated**: 2025-10-12
**Current Phase**: Phase 2 (Simple Characteristics)
