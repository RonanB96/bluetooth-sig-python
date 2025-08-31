# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-08-31

### Added

#### New Services (4 new services)
- **Health Thermometer Service (0x1809)**: Medical-grade temperature monitoring
- **Heart Rate Service (0x180D)**: Fitness and health heart rate monitoring  
- **Running Speed and Cadence Service (0x1814)**: Running fitness metrics
- **Cycling Speed and Cadence Service (0x1816)**: Cycling fitness metrics

#### New Characteristics (7 new characteristics)
- **Health Monitoring Characteristics**:
  - Heart Rate Measurement (0x2A37): Complex heart rate data with RR intervals
  - Blood Pressure Measurement (0x2A35): Systolic/diastolic pressure readings
  - Pulse Oximetry Measurement (PLX Continuous Measurement): SpO2 and pulse rate
  - Temperature Measurement (0x2A1C): IEEE-11073 medical temperature format
- **Environmental Characteristics**:
  - Illuminance (0x2A77): Light level measurements in lux
  - Sound Pressure Level (Power Specification): Audio environment monitoring
- **Fitness Characteristics**:
  - CSC Measurement (0x2A5B): Cycling speed and cadence data
  - RSC Measurement (0x2A53): Running speed and cadence data

#### Architecture Enhancements
- **Home Assistant Integration Layer**: Complete 3-layer architecture (GATT → Translation → HA)
- **IEEE-11073 Parsing Utilities**: Support for medical device data formats
- **Enhanced Error Handling**: Improved validation and error reporting
- **Translation Layer**: Clean separation between GATT and Home Assistant concerns

#### Testing & Quality
- **Comprehensive Test Suite**: Expanded test coverage with dynamic discovery
- **Architectural Validation**: Tests to enforce clean layer separation
- **Real Device Simulation**: Enhanced testing with mock device data
- **Code Quality**: Maintained Pylint 10.00/10 score

### Changed
- **Registry Coverage**: Expanded from 13 to 20+ characteristics
- **Service Count**: Expanded from 4 to 8 implemented services
- **Test Framework**: Enhanced validation with architectural compliance checks
- **Documentation**: Comprehensive updates reflecting current capabilities

### Technical Details
- **Total Services**: 8 (Battery, Device Info, Environmental Sensing, Generic Access, Health Thermometer, Heart Rate, RSC, CSC)
- **Total Characteristics**: 20+ fully implemented with Home Assistant metadata
- **Architecture**: Registry-driven with automatic UUID resolution and class name parsing
- **Dependencies**: Maintained compatibility with Python 3.11+ and current Bleak versions

## [0.2.0] - Previous Release

### Added
- Initial registry-driven architecture
- Real device integration with Nordic Thingy:52
- Core services: Battery, Device Information, Environmental Sensing, Generic Access
- Basic characteristics: Temperature, Humidity, Pressure, UV Index, Battery Level, Device Info
- Testing framework with 80+ tests
- Bleak-based BLE connection with 10-second timeout optimization

### Technical Foundation
- YAML-based UUID registry with Bluetooth SIG compliance
- Automatic name resolution with multiple format attempts
- Type-safe implementation with dataclass-based design
- Clean separation between Bluetooth and application layers

---

## Release Notes

### v0.3.0 Key Highlights

This release represents a significant expansion of the BLE GATT Device Framework, focusing on health monitoring, fitness tracking, and environmental sensing capabilities. The framework now supports comprehensive health metrics including heart rate, blood pressure, and pulse oximetry, making it suitable for medical and fitness applications.

#### Health & Fitness Focus
The addition of Health Thermometer, Heart Rate, RSC, and CSC services provides a complete foundation for health and fitness device integration. These services follow medical device standards (IEEE-11073) and include complex data parsing for multi-field measurements.

#### Architectural Maturity
The introduction of the Home Assistant integration layer demonstrates the framework's evolution toward production-ready architecture. The clean separation between GATT operations and application-specific concerns enables maintainable, testable code.

#### Expanded Environmental Sensing
New environmental characteristics (Illuminance, Sound Pressure Level) complement the existing temperature, humidity, pressure, and UV index sensors, providing comprehensive environmental monitoring capabilities.

### Migration Guide

No breaking changes in this release. All v0.2.0 code remains compatible. New services and characteristics are additive and follow the same patterns established in v0.2.0.

### Future Roadmap

- Additional health services (Weight Scale, Glucose)
- Enhanced Home Assistant entity auto-discovery
- Real-time data streaming optimizations
- Extended environmental sensor support