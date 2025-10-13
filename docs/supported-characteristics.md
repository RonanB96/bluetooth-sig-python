# Supported Characteristics and Services

This page lists all GATT characteristics and services currently supported by the library.

!!! note "Auto-Generated"
    This page is automatically generated from the codebase. The list is updated when new characteristics or services are added.

## Characteristics

The library currently supports **74** GATT characteristics:


### Power & Battery

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **BatteryLevel** | `N/A` | Battery level characteristic. |
| **BatteryPowerState** | `N/A` | Battery Level Status characteristic (0x2BED). |
| **CyclingPowerControlPoint** | `N/A` | Cycling Power Control Point characteristic (0x2A66). |
| **CyclingPowerFeature** | `N/A` | Cycling Power Feature characteristic (0x2A65). |
| **CyclingPowerMeasurement** | `N/A` | Cycling Power Measurement characteristic (0x2A63). |
| **CyclingPowerVector** | `N/A` | Cycling Power Vector characteristic (0x2A64). |
| **SupportedPowerRange** | `N/A` | Supported Power Range characteristic. |
| **TxPowerLevel** | `N/A` | Tx Power Level characteristic. |

### Environmental Sensing

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **BarometricPressureTrend** | `N/A` | Barometric pressure trend characteristic. |
| **BloodPressureFeature** | `N/A` | Blood Pressure Feature characteristic (0x2A49). |
| **BloodPressureMeasurement** | `N/A` | Blood Pressure Measurement characteristic (0x2A35). |
| **CO2Concentration** | `N/A` | Carbon Dioxide concentration characteristic (0x2B8C). |
| **Humidity** | `N/A` | Humidity measurement characteristic. |
| **PM10Concentration** | `N/A` | PM10 particulate matter concentration characteristic (0x2BD7). |
| **PM1Concentration** | `N/A` | PM1 particulate matter concentration characteristic (0x2BD7). |
| **PM25Concentration** | `N/A` | PM2.5 particulate matter concentration characteristic (0x2BD6). |
| **Pressure** | `N/A` | Atmospheric pressure characteristic. |
| **Temperature** | `N/A` | Temperature measurement characteristic. |
| **TemperatureMeasurement** | `N/A` | Temperature Measurement characteristic (0x2A1C). |
| **UVIndex** | `N/A` | UV Index characteristic. |

### Health & Fitness

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **BodyCompositionFeature** | `N/A` | Body Composition Feature characteristic (0x2A9B). |
| **BodyCompositionMeasurement** | `N/A` | Body Composition Measurement characteristic (0x2A9C). |
| **GlucoseFeature** | `N/A` | Glucose Feature characteristic (0x2A51). |
| **GlucoseMeasurement** | `N/A` | Glucose Measurement characteristic (0x2A18). |
| **GlucoseMeasurementContext** | `N/A` | Glucose Measurement Context characteristic (0x2A34). |
| **HeartRateMeasurement** | `N/A` | Heart Rate Measurement characteristic (0x2A37). |
| **WeightMeasurement** | `N/A` | Weight Measurement characteristic (0x2A9D). |
| **WeightScaleFeature** | `N/A` | Weight Scale Feature characteristic (0x2A9E). |

### Sports & Activity

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **CSCMeasurement** | `N/A` | CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B). |
| **RSCMeasurement** | `N/A` | RSC (Running Speed and Cadence) Measurement characteristic (0x2A53). |

### Device Information

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **FirmwareRevisionString** | `N/A` | Firmware Revision String characteristic. |
| **HardwareRevisionString** | `N/A` | Hardware Revision String characteristic. |
| **ManufacturerNameString** | `N/A` | Manufacturer Name String characteristic. |
| **ModelNumberString** | `N/A` | Model Number String characteristic. |
| **SerialNumberString** | `N/A` | Serial Number String characteristic. |
| **SoftwareRevisionString** | `N/A` | Software Revision String characteristic. |

### Electrical

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **AverageCurrent** | `N/A` | Average Current characteristic. |
| **AverageVoltage** | `N/A` | Average Voltage characteristic. |
| **ElectricCurrent** | `N/A` | Electric Current characteristic. |
| **ElectricCurrentRange** | `N/A` | Electric Current Range characteristic. |
| **ElectricCurrentSpecification** | `N/A` | Electric Current Specification characteristic. |
| **ElectricCurrentStatistics** | `N/A` | Electric Current Statistics characteristic. |
| **HighVoltage** | `N/A` | High Voltage characteristic. |
| **Voltage** | `N/A` | Voltage characteristic. |
| **VoltageFrequency** | `N/A` | Voltage Frequency characteristic. |
| **VoltageSpecification** | `N/A` | Voltage Specification characteristic. |
| **VoltageStatistics** | `N/A` | Voltage Statistics characteristic. |

### Other

| Characteristic | UUID | Description |
|----------------|------|-------------|
| **AmmoniaConcentration** | `N/A` | Ammonia concentration measurement characteristic (0x2BCF). |
| **ApparentWindDirection** | `N/A` | Apparent Wind Direction measurement characteristic. |
| **ApparentWindSpeed** | `N/A` | Apparent Wind Speed measurement characteristic. |
| **Appearance** | `N/A` | Appearance characteristic. |
| **DeviceName** | `N/A` | Device Name characteristic. |
| **DewPoint** | `N/A` | Dew Point measurement characteristic. |
| **Elevation** | `N/A` | Elevation characteristic. |
| **HeatIndex** | `N/A` | Heat Index measurement characteristic. |
| **Illuminance** | `N/A` | Illuminance characteristic (0x2AFB). |
| **LocalTimeInformation** | `N/A` | Local time information characteristic. |
| **MagneticDeclination** | `N/A` | Magnetic declination characteristic. |
| **MagneticFluxDensity2D** | `N/A` | Magnetic flux density 2D characteristic. |
| **MagneticFluxDensity3D** | `N/A` | Magnetic flux density 3D characteristic. |
| **MethaneConcentration** | `N/A` | Methane concentration measurement characteristic (0x2BD1). |
| **NitrogenDioxideConcentration** | `N/A` | Nitrogen dioxide concentration measurement characteristic (0x2BD2). |
| **Noise** | `N/A` | Noise characteristic (0x2BE4) - Sound pressure level measurement. |
| **NonMethaneVOCConcentration** | `N/A` | Non-Methane Volatile Organic Compounds concentration characteristic |
| **OzoneConcentration** | `N/A` | Ozone concentration measurement characteristic (0x2BD4). |
| **PollenConcentration** | `N/A` | Pollen concentration measurement characteristic (0x2A75). |
| **PulseOximetryMeasurement** | `N/A` | PLX Continuous Measurement characteristic (0x2A5F). |
| **Rainfall** | `N/A` | Rainfall characteristic. |
| **SulfurDioxideConcentration** | `N/A` | Sulfur dioxide concentration measurement characteristic (0x2BD3). |
| **TimeZone** | `N/A` | Time zone characteristic. |
| **TrueWindDirection** | `N/A` | True Wind Direction measurement characteristic. |
| **TrueWindSpeed** | `N/A` | True Wind Speed measurement characteristic. |
| **VOCConcentration** | `N/A` | Volatile Organic Compounds concentration characteristic (0x2BE7). |
| **WindChill** | `N/A` | Wind Chill measurement characteristic. |

## Services

The library currently supports **14** GATT services:

| Service | Description |
|---------|-------------|
| **AutomationIO** | Automation IO Service implementation. |
| **Battery** | Battery Service implementation. |
| **BodyComposition** | Body Composition Service implementation (0x181B). |
| **CyclingPower** | Cycling Power Service implementation (0x1818). |
| **CyclingSpeedAndCadence** | Cycling Speed and Cadence Service implementation (0x1816). |
| **DeviceInformation** | Device Information Service implementation. |
| **EnvironmentalSensing** | Environmental Sensing Service implementation (0x181A). |
| **GenericAccess** | Generic Access Service implementation. |
| **GenericAttribute** | Generic Attribute Service implementation. |
| **Glucose** | Glucose Service implementation (0x1808). |
| **HealthThermometer** | Health Thermometer Service implementation (0x1809). |
| **HeartRate** | Heart Rate Service implementation (0x180D). |
| **RunningSpeedAndCadence** | Running Speed and Cadence Service implementation (0x1814). |
| **WeightScale** | Weight Scale Service implementation (0x181D). |


## Adding Support for New Characteristics

To add support for a new characteristic:

1. See the [Adding New Characteristics](guides/adding-characteristics.md) guide
2. Follow the existing patterns in `src/bluetooth_sig/gatt/characteristics/`
3. Add tests for your new characteristic
4. Submit a pull request

## Official Bluetooth SIG Registry

This library is based on the official [Bluetooth SIG Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/) registry. The UUID registry is loaded from YAML files in the `bluetooth_sig` submodule.
