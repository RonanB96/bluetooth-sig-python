# Limitations

What this library does **not** do.

## ❌ Bluetooth Classic (BR/EDR)

**Not supported:**

- RFCOMM, A2DP, HFP, and other Classic Bluetooth profiles
- SDP service discovery
- L2CAP for Classic connections

This library focuses exclusively on BLE GATT.

______________________________________________________________________

## ❌ BLE Stack Implementation

**Not provided:**

- ATT protocol handling
- L2CAP implementation
- HCI interface
- Link layer implementation
- GATT server/peripheral role

The library works at the application layer. Lower-level protocols are handled by your BLE backend (bleak, simplepyble, etc.) and OS.

______________________________________________________________________

## ❌ Hardware Abstraction

**Not included:**

- Bluetooth adapter management
- Driver installation
- Platform-specific configuration
- USB dongle management

Hardware abstraction is provided by the OS Bluetooth stack and your chosen BLE library.

______________________________________________________________________

## ❌ Real-Time Streaming

**Not optimized for:**

- High-frequency data (>100 Hz)
- Sub-millisecond latency requirements
- Audio/video streaming
- Large file transfers

**Best suited for:** Periodic sensor reads, notifications, device queries (<1ms parse time).

______________________________________________________________________

## ❌ Embedded/Firmware

**Not designed for:**

- BLE peripheral devices
- Embedded systems (ESP32, Arduino, nRF52)
- Resource-constrained environments
- Server/peripheral role

Requires Python 3.9+ runtime with standard library.

______________________________________________________________________

## ❌ Persistent Storage

**Not included:**

- Connection history
- Credential storage
- Pairing database
- Cross-session state

Platform-level pairing is handled by the OS. Application-level persistence is your responsibility.

______________________________________________________________________

## ❌ GUI/Application Framework

This is a library, not an application. No desktop apps, mobile apps, web interfaces, or dashboards are provided.

______________________________________________________________________

## ❌ BLE Device Simulators

**Not included:**

- Mock BLE peripherals
- Hardware test fixtures
- Compliance testing tools

For testing, mock at the data level—the translator accepts raw bytes without hardware.

______________________________________________________________________

## ❌ Connection Manager Implementations

The library provides `ConnectionManagerProtocol` (abstract base class) but **not** production-ready adapters. Example adapters in `examples/connection_managers/` demonstrate the pattern for bleak, simplepyble, and bluepy—adapt these for your needs.

______________________________________________________________________

## Summary

| Category | Status |
|----------|--------|
| BLE GATT parsing | ✅ Supported |
| Device abstraction | ✅ Supported (requires adapter) |
| Bluetooth Classic | ❌ Not supported |
| BLE stack/protocols | ❌ Not implemented |
| Hardware abstraction | ❌ Not included |
| Real-time streaming | ❌ Not optimized |
| Embedded devices | ❌ Not supported |
| Persistent storage | ❌ Not included |
| GUI framework | ❌ Not included |

## See Also

- [Why Use This Library](why-use.md) - What problems we solve
- [BLE Integration Guide](../how-to/ble-integration.md) - Using the Device class with adapters
