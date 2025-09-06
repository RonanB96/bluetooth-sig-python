# Dataclass Conversion Guide

This guide documents the patterns established for converting characteristic `parse_value()` methods from returning `dict[str, Any]` to returning typed dataclasses, and adding `encode_value()` methods for write support.

## Established Patterns

### 1. Complex State Data Pattern
**Example**: `BatteryPowerStateCharacteristic`

**Use for**: Characteristics with multiple data formats, conditional parsing, complex state logic.

```python
@dataclass
class BatteryPowerStateData:
    """Parsed data from Battery Power State characteristic."""
    raw_value: int
    battery_present: str
    wired_external_power_connected: bool
    # ... other fields
    charging_fault_reason: str | list[str] | None = None

def parse_value(self, data: bytearray) -> BatteryPowerStateData:
    # Complex parsing logic with multiple formats
    # ...
    return BatteryPowerStateData(...)

def encode_value(self, data: BatteryPowerStateData) -> bytearray:
    # Encode to simplest format (e.g., basic single-byte)
    # ...
    return bytearray([encoded_byte])
```

### 2. Feature Bitmap Pattern
**Example**: `GlucoseFeatureCharacteristic`, `BodyCompositionFeatureCharacteristic`

**Use for**: Characteristics that represent device capabilities via bitmaps.

```python
@dataclass
class FeatureData:
    """Parsed data from Feature characteristic."""
    features_bitmap: int
    feature_1_supported: bool
    feature_2_supported: bool
    # ... all feature flags
    enabled_features: list[str]  # Human-readable list
    feature_count: int

def parse_value(self, data: bytearray) -> FeatureData:
    bitmap = struct.unpack("<H", data[:2])[0]  # or "<L" for 32-bit
    
    # Parse individual flags
    feature_1 = bool(bitmap & 0x01)
    feature_2 = bool(bitmap & 0x02)
    # ...
    
    # Generate human-readable list
    enabled = []
    if feature_1:
        enabled.append("Feature 1 Name")
    # ...
    
    return FeatureData(
        features_bitmap=bitmap,
        feature_1_supported=feature_1,
        # ...
        enabled_features=enabled,
        feature_count=len(enabled),
    )

def encode_value(self, data: FeatureData) -> bytearray:
    # Reconstruct bitmap from individual flags
    bitmap = 0
    if data.feature_1_supported:
        bitmap |= 0x01
    # ...
    return bytearray(struct.pack("<H", bitmap))
```

### 3. Nested Structured Data Pattern
**Example**: `LocalTimeInformationCharacteristic`

**Use for**: Characteristics with complex nested data structures.

```python
@dataclass
class SubDataType:
    """Sub-component of the main data."""
    field1: str
    field2: int | None
    raw_value: int

@dataclass
class MainData:
    """Main parsed data structure."""
    sub_data1: SubDataType
    sub_data2: SubDataType
    computed_field: float | None = None

def parse_value(self, data: bytearray) -> MainData:
    # Parse components
    sub1 = SubDataType(...)
    sub2 = SubDataType(...)
    
    # Compute derived fields
    computed = sub1.field2 + sub2.field2 if both_available else None
    
    return MainData(
        sub_data1=sub1,
        sub_data2=sub2,
        computed_field=computed,
    )

def encode_value(self, data: MainData) -> bytearray:
    # Use raw values for perfect round-trip
    return bytearray([
        data.sub_data1.raw_value,
        data.sub_data2.raw_value,
    ])
```

## Implementation Checklist

For each characteristic conversion:

### 1. Create Dataclass
- [ ] Add `from __future__ import annotations` import
- [ ] Create dataclass with proper type hints
- [ ] Use `| None` union syntax (not `Optional`)
- [ ] Include `raw_value` fields for encoding when needed
- [ ] Add computed/derived fields as needed

### 2. Update parse_value()
- [ ] Change return type from `dict[str, Any]` to dataclass
- [ ] Replace dict construction with dataclass instantiation
- [ ] Preserve all existing parsing logic

### 3. Add encode_value()
- [ ] Create method that takes dataclass instance
- [ ] Return `bytearray` with encoded data
- [ ] Focus on basic/common format for simplicity
- [ ] Use raw values when available for round-trip compatibility

### 4. Update Tests
- [ ] Change dict access (`result["field"]`) to attribute access (`result.field`)
- [ ] Update assertions to use dataclass attributes
- [ ] Add round-trip test: `parse → encode → parse`
- [ ] Add direct encoding test with known data

### 5. Verify Integration
- [ ] Test framework integration with `BluetoothSIGTranslator`
- [ ] Confirm `ParsedData.value` contains dataclass instance
- [ ] Ensure all existing tests still pass

## Framework Compatibility

The dataclass instances are automatically wrapped in the existing `ParsedData` framework structure:

```python
result = translator.parse_characteristic('UUID', raw_bytes)
# result is ParsedData
# result.value is YourDataclass instance
# result.parse_success indicates success
# result.error_message contains any errors
```

## Remaining Characteristics to Convert

1. `blood_pressure_measurement.py` - Measurement data pattern
2. `body_composition_measurement.py` - Measurement data pattern  
3. `csc_measurement.py` - Measurement data pattern
4. `cycling_power_control_point.py` - Control point pattern
5. `cycling_power_measurement.py` - Measurement data pattern
6. `cycling_power_vector.py` - Measurement data pattern
7. `glucose_measurement.py` - Measurement data pattern
8. `glucose_measurement_context.py` - Measurement data pattern
9. `heart_rate_measurement.py` - Measurement data pattern
10. `magnetic_flux_density_2d.py` - Simple measurement pattern
11. `magnetic_flux_density_3d.py` - Simple measurement pattern
12. `pulse_oximetry_measurement.py` - Measurement data pattern
13. `rsc_measurement.py` - Measurement data pattern
14. `temperature_measurement.py` - Measurement data pattern
15. `weight_measurement.py` - Measurement data pattern
16. `weight_scale_feature.py` - Feature bitmap pattern

## Testing Strategy

1. **Unit Tests**: Update each characteristic's tests
2. **Round-trip Tests**: Ensure `parse → encode → parse` works
3. **Framework Tests**: Verify `BluetoothSIGTranslator` integration
4. **Registry Tests**: Ensure no regressions in validation

## Next Steps

1. Choose simpler characteristics first (magnetic_flux_density_*, weight_scale_feature)
2. Use established patterns as templates
3. Focus on one characteristic at a time
4. Run tests frequently to catch issues early
5. Consider measurement data patterns for complex characteristics