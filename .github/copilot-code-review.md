# AI Code Review Instructions (concise)

## Purpose
Short, actionable checklist for AI agents reviewing pull requests in this repository.

## Review Checklist

- [ ] **Architecture:** GATT layer must not import Home Assistant modules. Layer boundaries must be clear.
- [ ] **Registry:** No hardcoded UUIDs. All UUIDs must be resolved via the registry system or explicit name overrides.
- [ ] **Parsing:** All characteristics/services must validate input length, type, and value ranges per SIG spec.
- [ ] **Timeouts:** BLE connections must use explicit `timeout=10.0` for reliability.
- [ ] **Types:** All code must use complete type hints and dataclass-based design for characteristics/services.
- [ ] **Tests:** Registry resolution and parsing tests must be included for new/changed items.
- [ ] **Documentation:** All public APIs and methods must have clear docstrings and usage examples.
- [ ] **Performance:** BLE code must use efficient connection/discovery patterns and clean up resources.
- [ ] **Security:** No hardcoded secrets. All binary parsing must be safe and robust.

## Guidance
For full implementation patterns and rationale, see the project documentation and SIG specifications:
- [Bluetooth SIG assigned numbers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [Python documentation](https://docs.python.org/)
- See `docs/` for additional examples and rationale if available.
