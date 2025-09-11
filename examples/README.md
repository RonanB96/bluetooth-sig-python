# Bluetooth SIG Integration Examples

This directory contains comprehensive examples demonstrating how to use the `bluetooth_sig` library with different BLE connection libraries. The examples showcase the **framework-agnostic design** where bluetooth_sig provides pure SIG standards parsing while you choose your preferred BLE library for connections.

## 🎯 Key Concept: Framework-Agnostic Design

The `bluetooth_sig` library separates **connection management** from **data parsing**:

```python
# Step 1: Get raw data (using ANY BLE library)
raw_data = await your_ble_library.read_characteristic(device, uuid)

# Step 2: Parse with bluetooth_sig (connection-agnostic)
from bluetooth_sig import BluetoothSIGTranslator
translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(uuid, raw_data)

# Step 3: Use parsed result
print(f"Value: {result.value} {result.unit}")
```

This pattern works with **any BLE library** - you're not locked into a specific connection framework.

## 📁 Example Files

### 🔵 [`pure_sig_parsing.py`](pure_sig_parsing.py)
**Pure SIG parsing without any BLE connections**

Demonstrates the core functionality of bluetooth_sig for parsing characteristic data according to official SIG specifications. No BLE hardware required.

```bash
python pure_sig_parsing.py
```

**Features:**
- Parse test data using SIG standards
- UUID resolution and characteristic information lookup
- Batch parsing of multiple characteristics
- Framework integration patterns

**Use Cases:**
- Understanding the library functionality
- Testing without BLE hardware
- Data processing from any source (files, network, etc.)

### 📱 [`with_bleak.py`](with_bleak.py)
**Integration with Bleak BLE library**

Shows how to combine Bleak for BLE connections with bluetooth_sig for standards-compliant parsing.

```bash
# Scan for devices
python with_bleak.py --scan

# Connect and parse
python with_bleak.py --address 12:34:56:78:9A:BC
```

**Requirements:**
```bash
pip install bleak
```

**Features:**
- Device scanning with Bleak
- Characteristic reading and SIG parsing
- Notification handling patterns
- Error handling examples

### 🔄 [`with_bleak_retry.py`](with_bleak_retry.py)
**Integration with bleak-retry-connector (Recommended for Production)**

Demonstrates robust BLE connections with automatic retry logic combined with pure SIG parsing. This is the recommended pattern for production applications.

```bash
# Robust device reading
python with_bleak_retry.py --address 12:34:56:78:9A:BC

# Continuous monitoring with auto-reconnect
python with_bleak_retry.py --address 12:34:56:78:9A:BC --monitor --duration 300

# Notification monitoring
python with_bleak_retry.py --address 12:34:56:78:9A:BC --notifications
```

**Requirements:**
```bash
pip install bleak-retry-connector bleak
```

**Features:**
- Automatic connection retry logic
- Service caching for performance
- Continuous monitoring with reconnection
- Production-ready error recovery
- Notification handling with robust connections

### 🔧 [`with_simpleble.py`](with_simpleble.py)
**Integration with SimplePyBLE (Alternative BLE Library)**

Shows integration with SimplePyBLE as an alternative to Bleak, demonstrating the framework-agnostic design.

```bash
# Scan and connect
python with_simpleble.py --scan
python with_simpleble.py --address 12:34:56:78:9A:BC
```

**Requirements (Platform Dependent):**
```bash
# Cross-platform
pip install simplepyble
```

**Features:**
- Alternative BLE library integration
- Cross-platform sync BLE library usage
- Same SIG parsing as other examples
- Mock usage demonstration if library unavailable

### 📊 [`library_comparison.py`](library_comparison.py)
**Compare Multiple BLE Libraries with Identical SIG Parsing**

Demonstrates that the same bluetooth_sig parsing code works identically across different BLE libraries, proving the framework-agnostic design.

```bash
# Compare all available libraries
python library_comparison.py --address 12:34:56:78:9A:BC --compare-all

# Scan with comparison
python library_comparison.py --scan --compare-all
```

**Features:**
- Side-by-side library comparison
- Identical parsing results across libraries
- Performance comparison
- Migration guidance between libraries

### 🧪 [`testing_with_mocks.py`](testing_with_mocks.py)
**Unit Testing with Mock Data (No BLE Hardware Required)**

Essential for CI/CD pipelines and development environments without BLE hardware.

```bash
# Basic test suite
python testing_with_mocks.py

# Comprehensive testing
python testing_with_mocks.py --test-suite comprehensive

# Performance benchmarking
python testing_with_mocks.py --benchmark

# SIG compliance validation
python testing_with_mocks.py --compliance
```

**Features:**
- Complete test suite without hardware
- SIG specification compliance testing
- Performance benchmarking
- CI/CD integration examples
- Edge case and error condition testing

## 🚀 Enhanced Integration Examples

### 🔍 [`enhanced_service_explorer.py`](enhanced_service_explorer.py)
**Enhanced Service Explorer - SIG Library Integration Showcase**

Based on Bleak's `service_explorer.py` with comprehensive Bluetooth SIG library integration. Demonstrates the proper discovery pattern:

1. Use name-based lookups when you know what you want
2. Use UUID-based lookups only for exploring unknown services/characteristics
3. Parse all readable characteristics with SIG standards compliance

```bash
# Connect to device and explore with SIG parsing
python enhanced_service_explorer.py --address 12:34:56:78:9A:BC

# Scan for devices first
python enhanced_service_explorer.py --scan

# Run with mock data (no hardware required)
python enhanced_service_explorer.py --mock
```

**Features:**
- Demonstrates targeted vs discovery patterns
- Comprehensive SIG parsing during exploration
- Shows proper name vs UUID lookup usage
- Mock data support for testing without hardware

### 🔔 [`enhanced_notifications.py`](enhanced_notifications.py)
**Enhanced Notifications - SIG Library Integration with Notification Parsing**

Based on Bleak's `enable_notifications.py` with comprehensive Bluetooth SIG library integration for parsing notification data.

```bash
# Monitor all notifications with SIG parsing
python enhanced_notifications.py --address 12:34:56:78:9A:BC

# Monitor specific characteristic
python enhanced_notifications.py --address 12:34:56:78:9A:BC --characteristic "Heart Rate Measurement"

# Simulate notifications with mock data
python enhanced_notifications.py --mock --duration 10
```

**Features:**
- Automatic SIG parsing in notification callbacks
- Rich data extraction that manual parsing would miss
- Standards-compliant notification handling
- Real-time parsing with comprehensive error handling

### ⚖️ [`real_world_comparison.py`](real_world_comparison.py)
**Real-World Integration Comparison: Manual vs Bluetooth SIG Library**

Direct side-by-side comparison of manual BLE parsing versus using the Bluetooth SIG library, demonstrating code complexity differences, standards compliance gaps, and missing features in manual parsing.

```bash
# Compare with mock data (no hardware required)
python real_world_comparison.py --mock

# Performance benchmark
python real_world_comparison.py --benchmark

# Compare with real device
python real_world_comparison.py --address 12:34:56:78:9A:BC
```

**Features:**
- Side-by-side manual vs SIG library comparison
- Shows missing features in manual parsing
- Performance benchmarking
- Standards compliance analysis

### 📚 [`practical_integration_guide.py`](practical_integration_guide.py)
**Practical Integration Guide - Bluetooth SIG Library Best Practices**

Comprehensive guide demonstrating recommended patterns for integrating the Bluetooth SIG library with BLE connection libraries.

```bash
# Show all integration patterns
python practical_integration_guide.py --demo-patterns

# Demonstrate with mock device
python practical_integration_guide.py --mock-device

# Real device demonstration
python practical_integration_guide.py --address 12:34:56:78:9A:BC
```

**Features:**
- When to use name-based vs UUID-based lookups
- Proper service discovery workflows
- Production-ready error handling patterns
- Performance optimization techniques

## 🔗 BLE Library Compatibility

| Library | Platform | Async | Installation | Status |
|---------|----------|-------|--------------|--------|
| **bleak** | Cross-platform | ✅ | `pip install bleak` | ✅ Recommended |
| **bleak-retry-connector** | Cross-platform | ✅ | `pip install bleak-retry-connector` | 🏆 **Best for Production** |
| **simplepyble** | Cross-platform | ❌ | `pip install simplepyble` | ✅ Alternative |

## 🚀 Quick Start

1. **Choose your BLE library** based on your platform and requirements
2. **Install bluetooth_sig and your chosen BLE library**:
   ```bash
   pip install bluetooth-sig
   pip install bleak-retry-connector  # Recommended
   ```

### 📦 Installing All Example Dependencies

To install bluetooth_sig with all BLE libraries used in the examples:

```bash
# Install with all example dependencies (recommended for trying all examples)
pip install bluetooth-sig[examples]

# Or install individually based on your needs:
pip install bluetooth-sig bleak                    # Basic async BLE
pip install bluetooth-sig bleak-retry-connector    # Production-ready with retry logic  
pip install bluetooth-sig simplepyble              # Cross-platform sync alternative
```

**Note:** The `[examples]` installation includes the main supported BLE libraries for cross-platform development.
3. **Start with an example** that matches your chosen library
4. **Adapt the pattern** to your specific use case

## 🎓 Integration Patterns

### Pattern 1: Pure SIG Translation (Core)
```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(uuid, raw_data)
```

### Pattern 2: With Connection Library
```python
# Connection: Your choice of BLE library
raw_data = await ble_library.read_characteristic(uuid)

# Parsing: Always bluetooth_sig
result = translator.parse_characteristic(uuid, raw_data)
```

### Pattern 3: Robust Production Usage
```python
from bleak_retry_connector import establish_connection
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

async with establish_connection(BleakClient, address) as client:
    raw_data = await client.read_gatt_char(uuid)
    result = translator.parse_characteristic(uuid, raw_data)
```

### Pattern 4: Testing Without Hardware
```python
# Mock or file data
test_data = bytes([0x64])  # 100% battery level

# Same parsing code
result = translator.parse_characteristic("2A19", test_data)
assert result.value == 100
```

## 🏗️ Architecture Benefits

### ✅ Framework Agnostic
- **Not locked into any BLE library** - choose based on your needs
- **Easy migration** between BLE libraries without changing parsing logic
- **Works with existing codebases** using any BLE implementation

### ✅ Separation of Concerns
- **Connection management**: Handled by your chosen BLE library
- **Standards parsing**: Handled by bluetooth_sig
- **Clean interfaces** between connection and parsing logic

### ✅ Testing & CI/CD Ready
- **Test without hardware** using mock data
- **Deterministic results** for regression testing
- **Fast CI/CD pipelines** without BLE dependencies

### ✅ Standards Compliant
- **Official SIG specifications** for all parsing logic
- **Consistent behavior** across all BLE libraries
- **Type-safe results** with comprehensive validation

## 📝 Development Workflow

1. **Develop and test** using `testing_with_mocks.py` (no hardware needed)
2. **Choose BLE library** based on your platform and requirements
3. **Integrate** using the appropriate example as a template
4. **Deploy** with confidence knowing parsing is standards-compliant

## 🎯 Production Recommendations

- **Use `bleak-retry-connector`** for robust production applications
- **Implement proper error handling** as shown in the examples
- **Test with mock data** in your CI/CD pipeline
- **Monitor connection health** and implement reconnection logic
- **Cache service discoveries** when possible for performance

## 🔧 Common Use Cases

### IoT Sensor Reading
```python
# Read environmental sensors
sensor_data = {}
for uuid in ["2A6E", "2A6F", "2A6D"]:  # Temperature, Humidity, Pressure
    raw_data = await client.read_gatt_char(uuid)
    result = translator.parse_characteristic(uuid, raw_data)
    sensor_data[result.name] = result.value
```

### Device Information Discovery
```python
# Read device information
device_info = {}
for uuid in ["2A29", "2A24", "2A25"]:  # Manufacturer, Model, Serial
    raw_data = await client.read_gatt_char(uuid)
    result = translator.parse_characteristic(uuid, raw_data)
    device_info[result.name] = result.value
```

### Health Monitoring
```python
# Monitor health characteristics
def handle_heart_rate(sender, data):
    result = translator.parse_characteristic("2A37", data)
    print(f"Heart Rate: {result.value['heart_rate']} BPM")

await client.start_notify("2A37", handle_heart_rate)
```

## 🚨 Important Notes

- **No BLE hardware required** for most examples - they include mock data demonstrations
- **Platform compatibility** varies by BLE library - check requirements
- **bluetooth_sig works identically** regardless of your BLE library choice
- **Connection management complexity** varies by library - choose based on your needs

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [Architecture Overview](../docs/Bluetooth_sig_python_arch.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Bluetooth SIG Specifications](https://www.bluetooth.com/specifications/assigned-numbers/)

---

**💡 Remember**: The power of bluetooth_sig is that it provides pure SIG standards parsing that works with ANY BLE library. You're free to choose the best connection library for your needs while maintaining standards-compliant data interpretation.