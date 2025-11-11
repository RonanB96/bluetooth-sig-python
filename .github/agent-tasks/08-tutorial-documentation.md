# Task 08: Tutorial Documentation

**Priority**: P1 (High Priority)
**Estimated Effort**: Medium (3-4 days)
**Dependencies**: Task 01 (Context Support) - ideally complete first
**Target Release**: v0.4.0

## Objective

Create step-by-step tutorial documentation to ease onboarding and demonstrate common use cases, making the library more accessible to new users.

## Background

Current documentation is excellent but assumes technical proficiency:
- Architecture docs are comprehensive but advanced
- Quick start is good but brief
- Missing hands-on tutorials for learning by doing
- No "first 15 minutes" experience guide

## Success Criteria

- [ ] "Your First BLE Parser" 15-minute tutorial
- [ ] "Multi-Sensor Dashboard" tutorial
- [ ] "Custom Characteristics Workshop" tutorial
- [ ] "Testing Without Hardware" guide
- [ ] Each tutorial tested and validated
- [ ] Tutorials linked from main docs

## Tutorial Structure

Each tutorial should include:
1. **Prerequisites** - What you need to know/have
2. **Learning Objectives** - What you'll learn
3. **Step-by-Step Instructions** - Clear, numbered steps
4. **Code Examples** - Complete, runnable code
5. **Expected Output** - What success looks like
6. **Troubleshooting** - Common issues and solutions
7. **Next Steps** - Where to go from here

## Tutorial 1: Your First BLE Parser (15 Minutes)

**File**: `docs/tutorials/first-parser.md` (new)

```markdown
# Tutorial: Your First BLE Parser

**Time**: 15 minutes
**Level**: Beginner
**Prerequisites**: Python 3.9+ installed

## What You'll Learn

- Install the bluetooth-sig library
- Parse your first characteristic
- Resolve UUIDs to human-readable names
- Handle parsing errors
- Work with different data types

## Step 1: Installation

```bash
pip install bluetooth-sig
```

Verify installation:

```python
python -c "import bluetooth_sig; print('✅ Ready!')"
```

## Step 2: Your First Parse

Create a file called `first_parse.py`:

```python
from bluetooth_sig import BluetoothSIGTranslator

# Create translator
translator = BluetoothSIGTranslator()

# Simulate raw BLE data (85% battery level)
battery_data = bytearray([85])

# Parse it!
result = translator.parse_characteristic("2A19", battery_data)

print(f"Battery: {result.value}%")
```

**Run it:**

```bash
python first_parse.py
```

**Expected output:**

```
Battery: 85%
```

🎉 **Congratulations!** You just parsed your first BLE characteristic!

## Step 3: Understanding UUIDs

Let's understand what `"2A19"` means:

```python
# Look up UUID information
info = translator.get_sig_info_by_uuid("2A19")

print(f"UUID: {info.uuid}")
print(f"Name: {info.name}")
print(f"Type: {info.value_type}")
```

**Output:**

```
UUID: 2A19
Name: Battery Level
Type: uint8
```

`2A19` is the Bluetooth SIG standard UUID for "Battery Level". The library knows about 70+ standard characteristics!

## Step 4: Parsing Different Data Types

Let's try temperature (16-bit signed integer with scaling):

```python
# Temperature: 24.04°C (stored as 2404 in 0.01°C units)
temp_data = bytearray([0x64, 0x09])  # Little-endian: 0x0964 = 2404

result = translator.parse_characteristic("2A6E", temp_data)

print(f"Temperature: {result.value}°C")
# Output: Temperature: 24.04°C
```

## Step 5: Handling Errors

What happens with invalid data?

```python
# Try to parse with wrong length
short_data = bytearray([0x64])  # Only 1 byte, need 2

result = translator.parse_characteristic("2A6E", short_data)

if not result.parse_success:
    print(f"❌ Error: {result.error_message}")
else:
    print(f"✅ Value: {result.value}")
```

**Output:**

```
❌ Error: Insufficient data: Temperature requires 2 bytes
```

The library validates data and gives clear error messages!

## Step 6: Parsing Multiple Characteristics

Real devices have multiple characteristics. Parse them together:

```python
# Simulate environmental sensor data
sensor_data = {
    "2A6E": bytearray([0x64, 0x09]),  # Temperature: 24.04°C
    "2A6F": bytearray([0x3A, 0x13]),  # Humidity: 49.42%
    "2A6D": bytearray([0xD0, 0x4C, 0x00, 0x00]),  # Pressure: 101.36 kPa
}

# Parse all at once
results = translator.parse_characteristics(sensor_data)

print("Environmental Sensor Readings:")
for uuid, result in results.items():
    if result.parse_success:
        print(f"  {result.name}: {result.value}")
```

**Output:**

```
Environmental Sensor Readings:
  Temperature: 24.04°C
  Humidity: 49.42%
  Pressure: 101.36 kPa
```

## Complete Example

Here's everything together:

```python
from bluetooth_sig import BluetoothSIGTranslator

def main():
    translator = BluetoothSIGTranslator()

    # Simulate sensor readings
    sensor_data = {
        "2A19": bytearray([85]),                    # Battery: 85%
        "2A6E": bytearray([0x64, 0x09]),            # Temp: 24.04°C
        "2A6F": bytearray([0x3A, 0x13]),            # Humidity: 49.42%
        "2A6D": bytearray([0xD0, 0x4C, 0x00, 0x00]),# Pressure
    }

    # Parse all
    results = translator.parse_characteristics(sensor_data)

    # Display results
    print("📊 Sensor Dashboard")
    print("=" * 40)

    for uuid, result in results.items():
        if result.parse_success:
            # Get unit if available
            unit = getattr(result.info, 'unit', '')
            print(f"{result.name:20} {result.value}{unit}")
        else:
            print(f"{uuid:20} Error: {result.error_message}")

if __name__ == "__main__":
    main()
```

## What You've Learned

✅ Install and import the library
✅ Parse individual characteristics
✅ Resolve UUIDs to names
✅ Handle different data types
✅ Validate and handle errors
✅ Parse multiple characteristics together

## Troubleshooting

### Import Error

```python
ModuleNotFoundError: No module named 'bluetooth_sig'
```

**Solution**: Install the library: `pip install bluetooth-sig`

### Type Hints Error

If you see type-related errors, ensure you're using Python 3.9+:

```bash
python --version  # Should be 3.9 or higher
```

### Data Format Issues

If parsing fails, check:
- Data length (use `len(data)` to verify)
- Byte order (most BLE data is little-endian)
- Valid value ranges

## Next Steps

**Continue learning:**
- [Multi-Sensor Dashboard Tutorial](multi-sensor-dashboard.md) - Build a complete application
- [Custom Characteristics](custom-characteristics.md) - Add your own parsers
- [BLE Integration Guide](../guides/ble-integration.md) - Connect to real devices

**Try it yourself:**
- Parse other characteristics from the [supported list](../supported-characteristics.md)
- Experiment with error cases
- Build a simple sensor logger

## Need Help?

- **Documentation**: [Full Docs](../index.md)
- **Examples**: [GitHub Examples](https://github.com/ronanb96/bluetooth-sig-python/tree/main/examples)
- **Issues**: [GitHub Issues](https://github.com/ronanb96/bluetooth-sig-python/issues)

---

**Completed in**: ~15 minutes ⏱️
**Next Tutorial**: [Multi-Sensor Dashboard →](multi-sensor-dashboard.md)
```

## Tutorial 2: Multi-Sensor Dashboard

**File**: `docs/tutorials/multi-sensor-dashboard.md` (new)

```markdown
# Tutorial: Building a Multi-Sensor Dashboard

**Time**: 30-45 minutes
**Level**: Intermediate
**Prerequisites**: Complete "Your First BLE Parser" tutorial

## What You'll Build

A real-time dashboard that:
- Reads from multiple BLE sensors
- Parses and displays data
- Updates continuously
- Handles connection issues gracefully

## Project Structure

```
sensor_dashboard/
├── main.py           # Dashboard application
├── device_reader.py  # BLE device reader
└── requirements.txt  # Dependencies
```

## Step 1: Setup

Create project directory and install dependencies:

```bash
mkdir sensor_dashboard
cd sensor_dashboard

# Create requirements.txt
cat > requirements.txt << EOF
bluetooth-sig>=0.3.0
bleak>=0.21.0
EOF

# Install
pip install -r requirements.txt
```

## Step 2: Device Reader Module

Create `device_reader.py`:

```python
"""BLE device reader module."""

import asyncio
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator


class SensorDevice:
    """Represents a BLE sensor device."""

    def __init__(self, address: str, name: str = "Unknown"):
        self.address = address
        self.name = name
        self.translator = BluetoothSIGTranslator()
        self.client = None

    async def connect(self):
        """Connect to device."""
        print(f"Connecting to {self.name} ({self.address})...")
        self.client = BleakClient(self.address)
        await self.client.connect()
        print(f"✓ Connected to {self.name}")

    async def disconnect(self):
        """Disconnect from device."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print(f"✓ Disconnected from {self.name}")

    async def read_characteristic(self, uuid: str):
        """Read and parse a characteristic."""
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Not connected")

        # Read raw data
        raw_data = await self.client.read_gatt_char(uuid)

        # Parse with bluetooth-sig
        result = self.translator.parse_characteristic(uuid, raw_data)

        return result

    async def read_all_sensors(self):
        """Read all available sensors."""
        # Common sensor UUIDs
        sensor_uuids = {
            "Battery Level": "2A19",
            "Temperature": "2A6E",
            "Humidity": "2A6F",
            "Pressure": "2A6D",
        }

        readings = {}

        for name, uuid in sensor_uuids.items():
            try:
                result = await self.read_characteristic(uuid)
                if result.parse_success:
                    readings[name] = {
                        "value": result.value,
                        "unit": getattr(result.info, 'unit', ''),
                    }
            except Exception as e:
                # Characteristic might not be available
                continue

        return readings
```

[Continue with more steps...]
```

## Tutorial 3: Custom Characteristics Workshop

**File**: `docs/tutorials/custom-characteristics.md` (new)

[Full content similar to tutorial 1 & 2...]

## Tutorial 4: Testing Without Hardware

**File**: `docs/tutorials/testing-without-hardware.md` (new)

```markdown
# Tutorial: Testing Without Hardware

**Time**: 20 minutes
**Level**: Beginner/Intermediate
**Prerequisites**: Basic Python knowledge

## Why This Matters

You can develop and test BLE applications **without physical devices**:
- Faster development iteration
- No hardware required
- Automated testing
- Predictable, reproducible tests

## Approach 1: Mock Data

Simply create bytearray data matching the spec:

```python
import pytest
from bluetooth_sig import BluetoothSIGTranslator

def test_temperature_sensor():
    """Test temperature parsing without hardware."""
    translator = BluetoothSIGTranslator()

    # Mock temperature data: 24.04°C
    mock_data = bytearray([0x64, 0x09])

    result = translator.parse_characteristic("2A6E", mock_data)

    assert result.parse_success
    assert abs(result.value - 24.04) < 0.01
```

## Approach 2: Test Fixtures

Create reusable mock data:

```python
# conftest.py
import pytest

@pytest.fixture
def battery_data():
    """Mock battery level data."""
    return {
        "full": bytearray([100]),
        "half": bytearray([50]),
        "low": bytearray([15]),
        "empty": bytearray([0]),
    }

# test_battery.py
def test_battery_levels(battery_data):
    """Test various battery levels."""
    translator = BluetoothSIGTranslator()

    for level, data in battery_data.items():
        result = translator.parse_characteristic("2A19", data)
        assert result.parse_success
```

[Continue...]
```

## Implementation Plan

### Week 1: Core Tutorials
1. Write "Your First BLE Parser" tutorial
2. Write "Multi-Sensor Dashboard" tutorial
3. Test tutorials with fresh eyes (or have someone else test)

### Week 2: Advanced Tutorials
4. Write "Custom Characteristics Workshop"
5. Write "Testing Without Hardware"
6. Create supporting code examples

### Week 3: Integration & Polish
7. Link tutorials from main docs
8. Add tutorial navigation
9. Create "Tutorials" landing page
10. Review and edit for clarity

## Files to Create

### New Directories
- `docs/tutorials/` - Tutorial content directory

### New Files
- `docs/tutorials/index.md` - Tutorials landing page
- `docs/tutorials/first-parser.md` - Tutorial 1
- `docs/tutorials/multi-sensor-dashboard.md` - Tutorial 2
- `docs/tutorials/custom-characteristics.md` - Tutorial 3
- `docs/tutorials/testing-without-hardware.md` - Tutorial 4

### Update Files
- `docs/index.md` - Add tutorials section
- `mkdocs.yml` - Add tutorials to navigation
- `README.md` - Link to tutorials

## Validation Steps

1. **Test each tutorial**:
   - Follow every step exactly as written
   - Verify all code examples work
   - Check expected outputs match actual

2. **Fresh perspective test**:
   - Have someone unfamiliar with the library try tutorials
   - Note where they get stuck
   - Improve unclear sections

3. **Build docs and review**:
   ```bash
   mkdocs serve
   open http://localhost:8000/tutorials/
   ```

4. **Check code quality**:
   ```bash
   python -m black docs/tutorials/*.py
   python -m flake8 docs/tutorials/*.py
   ```

## Acceptance Criteria

- [ ] All 4 tutorials written and tested
- [ ] Each tutorial takes stated time to complete
- [ ] All code examples are complete and runnable
- [ ] Tutorials linked from main documentation
- [ ] Navigation between tutorials works
- [ ] Screenshots/diagrams where helpful (optional)
- [ ] Troubleshooting sections complete

## Style Guidelines

### Writing Style
- Use clear, simple language
- Write in second person ("you will...")
- Use active voice
- Break into small, manageable steps
- Include success confirmations ("✅ Done!")

### Code Examples
- Keep examples short and focused
- Include complete, runnable code
- Add comments explaining non-obvious parts
- Show expected output
- Handle errors gracefully

### Formatting
- Use numbered steps for sequences
- Use bullet points for lists
- Use code blocks with syntax highlighting
- Use admonitions (notes, warnings) sparingly
- Include emoji for visual interest (✅ ❌ 🎉 ⚠️)

## Notes for AI Agents

- Write for complete beginners unless stated otherwise
- Test every command and code example
- Use realistic but simple examples
- Don't assume prior BLE knowledge
- Link to relevant documentation sections
- Keep tutorials focused - don't try to cover everything
- Update tutorials when library changes
- Consider adding video walkthroughs in future
