# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-08-31

### Added

#### Enhanced Standards Library

- **Type-Safe API**: Dataclass-based returns for all parsing operations
- **Modern Python**: Python 3.9+ support with future annotations
- **Comprehensive Coverage**: Support for 70+ GATT characteristics
- **Quality Metrics**: Perfect pylint scores and extensive testing

#### Core API Improvements

- **BluetoothSIGTranslator**: Primary API for UUID resolution and data parsing
- **Rich Information Objects**: SIGInfo, CharacteristicInfo, ServiceInfo dataclasses
- **Standards Compliance**: Direct interpretation of official Bluetooth SIG specifications
- **Validation Framework**: Comprehensive testing against official standards

### Technical Details

- **Pure Standards Library**: Focus on Bluetooth SIG specification interpretation
- **Type Safety**: Complete type hints with modern union syntax (Class | None)
- **Code Quality**: Ruff-based toolchain providing 100x speed improvement over legacy tools
- **Python Compatibility**: Future annotations for 3.9+ compatibility

## [0.2.0] - Previous Release

### Added

- Initial registry-driven architecture
- Core standards interpretation functionality
- Basic UUID resolution and data parsing
- Testing framework with comprehensive validation
- Type-safe implementation with dataclass-based design

### Technical Foundation

- YAML-based UUID registry with Bluetooth SIG compliance
- Automatic name resolution with multiple format attempts
- Clean separation between standards interpretation and application logic
