Plan: bluetooth-sig-python Library — Gap Analysis & Improvement Roadmap
TL;DR: The library has strong foundations (~200 characteristics, full PDU parser, Device abstraction, strict typing) but suffers from God classes, untracked GATT coverage gaps, empty registry stubs, stream/peripheral incompleteness, and misleading documentation. Python minimum bumps to >=3.10, removing TYPE_CHECKING workarounds. Architecture stays pure SIG — no vendor parsers or framework code in core. Work is structured as 5 independent parallel workstreams.

Workstream 1: Architecture — God Class Decomposition
The four largest files each exceed 1,100 lines with inline TODOs acknowledging the problem.

1.1 Split BluetoothSIGTranslator (1,359 lines at src/bluetooth_sig/core/translator.py)

Extract into 5 focused modules under src/bluetooth_sig/core/:

New Module	Methods to Extract	Approx Lines
query.py	get_value_type, supports, all 8 get_*_info_* methods, list_supported_*, get_service_characteristics	~400
parser.py	parse_characteristic, parse_characteristic_async, parse_characteristics, parse_characteristics_async, all private batch/dependency helpers	~450
encoder.py	encode_characteristic, encode_characteristic_async, create_value, validate_characteristic_data	~200
registration.py	register_custom_characteristic_class, register_custom_service_class	~120
service_manager.py	process_services, get_service_by_uuid, discovered_services, clear_services	~100
translator.py becomes a thin facade composing these via mixins or delegation. The BluetoothSIG global singleton interface stays intact.

1.2 Split Device (1,172 lines at src/bluetooth_sig/device/device.py)

Already partially decomposed (DeviceConnected, DeviceAdvertising). Extract remaining responsibility pockets:

Dependency resolution logic → src/bluetooth_sig/device/dependency_resolver.py
Connection lifecycle management → keep in connected.py
Device stays as composition root but slims to <400 lines
1.3 Split BaseCharacteristic (1,761 lines at src/bluetooth_sig/gatt/characteristics/base.py)

Extract the multi-stage parsing pipeline stages into separate modules:

src/bluetooth_sig/gatt/characteristics/pipeline/validation.py — length validation, range validation, type validation
src/bluetooth_sig/gatt/characteristics/pipeline/extraction.py — integer extraction, special value detection
src/bluetooth_sig/gatt/characteristics/pipeline/decoding.py — decode orchestration
base.py remains the ABC composing pipeline stages, targeting <600 lines
1.4 Split templates.py (1,488 lines at src/bluetooth_sig/gatt/characteristics/templates.py)

Group templates by domain:

templates/numeric.py — Uint8Template, Sint16Template, Uint16Template, PercentageTemplate
templates/temporal.py — DateTimeTemplate, ExactTime256Template, CurrentTimeTemplate
templates/enum.py — EnumTemplate
templates/base.py — CodingTemplate[T] base class + extractor/translator pipeline
templates/__init__.py — re-exports for backwards compat
Verification: All existing tests must pass after each split. Run python -m pytest tests/ -v and ./scripts/lint.sh --all after each module extraction. No public API changes — from bluetooth_sig.core.translator import BluetoothSIGTranslator must still work via re-exports.

Workstream 2: Code Quality & Python 3.10 Upgrade
2.1 Bump minimum Python to >=3.10

Update requires-python in pyproject.toml
Update classifiers, Ruff target-version, mypy python_version
Remove all 3 TYPE_CHECKING blocks: encryption.py:15, client.py:18, device_types.py:5 — move guarded imports to top-level
Update CI matrix in test-coverage.yml to test 3.10+3.12 (drop 3.9)
2.2 Reduce # type: ignore comments (20 currently)

Audit all 20 occurrences. For each, attempt to resolve with proper generics/overloads/protocols instead of suppression. Target: <=5 remaining, all with justification comments.

2.3 Eliminate silent pass in except blocks (12 occurrences)

uuid_registry.py L392, L420, L448 — add logger.debug() before pass to make failures visible
translator.py L553, L706 — same treatment
descriptors/registry.py L26 — log registration failures
Remaining: evaluate case-by-case; at minimum add debug logging
2.4 Tighten Any usage

Audit the heaviest Any usage files (translator.py, device.py, connected.py). Introduce TypeVar bounds or Protocol types where Any is used as a shortcut rather than a necessity. The dynamic dispatch in parse_characteristic(str, bytes) → Any is inherently untyped — that's fine — but internal helper returns should be tightened.

Verification: ./scripts/lint.sh --all and python -m pytest tests/ -v pass. mypy --strict remains clean.

Workstream 3: Completeness — Missing Features & Stubs

Gap analysis revealed that 2 original items were infeasible (3.6 auxiliary packets require radio
access; 3.3 SDP is irrelevant to BLE) and 1 was based on a false assumption about the YAML data
(3.2 profile YAMLs contain codec/param enums, not mandatory/optional service lists). The plan is
revised below. Implementation order follows priority (value ÷ risk).

3.1 Fix PeripheralDevice + Add Tests — ✅ DONE (commit 39a53b6)

peripheral_device.py was scaffolded but had a dead `translator` parameter — `SIGTranslatorProtocol`
is parse-only and encoding is already handled directly by `BaseCharacteristic.build_value()` on the
stored characteristic instances. The `_translator` field was never referenced.

Completed:
- Removed `translator` parameter from `PeripheralDevice.__init__`; updated docstrings
- Added `Any` import justification comment (heterogeneous characteristic dict)
- Wrote 29 tests in tests/device/test_peripheral_device.py across 8 test classes:
  - TestPeripheralDeviceInit (5 tests) — constructor, properties, empty state
  - TestAddCharacteristic (4 tests) — registration, auto-service creation, duplicate service
  - TestLifecycle (5 tests) — start flushes services, stop clears advertising, start-twice,
    stop-when-not-started, add-after-start raises RuntimeError
  - TestUpdateValue (5 tests) — encode + push, notify flag, unknown UUID KeyError
  - TestUpdateRaw (1 test) — raw bytes push
  - TestGetCurrentValue (3 tests) — initial value, latest value, unknown UUID KeyError
  - TestFluentConfiguration (7 tests) — method chaining for manufacturer data, tx power,
    connectable, discoverable
  - TestAddService (1 test) — pre-built ServiceDefinition
- All tests pass, lint clean

3.2 Profile Parameter Registries (Redesigned)

Original plan proposed a monolithic `Profile` struct with mandatory/optional services. The 44 YAML
files across 14 profile subdirectories actually contain 5 distinct structural patterns: simple
name/value lookups, permitted-characteristics lists, codec parameters, protocol parameters, and
LTV structures. No YAML contains profile-level service requirements.

Redesigned as per-category registries under registry/profiles/:

a) PermittedCharacteristicsRegistry — loads ESS, UDS, IMDS permitted_characteristics YAMLs.
   Query: get_permitted_characteristics("ess") → list of characteristic identifiers.
   Struct: PermittedCharacteristicEntry(service: str, characteristics: list[str]).
   Extends BaseGenericRegistry[PermittedCharacteristicEntry].

b) ProfileLookupRegistry — loads simple name/value files (A2DP codecs, TDS org IDs, ESL display
   types, HFP bearer technologies, AVRCP types, MAP chat states, etc.). Single registry keyed
   by YAML top-level key.
   Query: get_entries("audio_codec_id") → list[ProfileLookupEntry].
   Struct: ProfileLookupEntry(name: str, value: int, metadata: dict[str, str]).
   Extends BaseGenericRegistry[list[ProfileLookupEntry]].

c) ServiceDiscoveryAttributeRegistry — loads the 26 attribute_ids/*.yaml files plus
   protocol_parameters.yaml and attribute_id_offsets_for_strings.yaml.
   Query: get_attribute_ids("universal_attributes") → list[AttributeIdEntry].
   Struct: AttributeIdEntry(name: str, value: int).

d) Defer generic_audio/ LTV structures — polymorphic nested schemas need a dedicated LTV codec
   framework. Mark as follow-up.

New files:
- src/bluetooth_sig/types/registry/profile_types.py (msgspec.Struct types)
- src/bluetooth_sig/registry/profiles/permitted_characteristics.py
- src/bluetooth_sig/registry/profiles/profile_lookup.py
- src/bluetooth_sig/registry/service_discovery/attribute_ids.py
- Tests for each registry

3.3 — REMOVED (SDP irrelevant to BLE)

SDP is classic Bluetooth (BR/EDR). This library is BLE-focused. The service_class.yaml UUIDs are
already accessible via the existing ServiceClassesRegistry. The attribute_ids/*.yaml loading is
rolled into 3.2c above. No standalone ServiceDiscoveryRegistry needed.

3.4 GATT Coverage Gap Tracking

Existing static analysis tests check consistency (implementation → enum → YAML) but not coverage
(YAML → implementation). This adds the reverse direction.

New file: tests/static_analysis/test_yaml_implementation_coverage.py
- Load all UUIDs from characteristic_uuids.yaml (~481 entries)
- Compare against CharacteristicRegistry.get_instance()._get_sig_classes_map() keys
- Same for services (service_uuids.yaml vs GattServiceRegistry)
- Same for descriptors (descriptors.yaml vs DescriptorRegistry)
- Output as pytest warnings, not failures — the test reports coverage % without failing CI
- Print summary to stdout for CI visibility

Verification: python -m pytest tests/static_analysis/test_yaml_implementation_coverage.py -v runs
and produces coverage report without failing.

3.5 Advertising Location Struct Parsing — ✅ DONE (commit 31bf76a)

The PDU parser stored Indoor Positioning, Transport Discovery Data, 3D Information, and Channel
Map Update Indication as raw bytes. All 4 are now parsed into typed structs.

Completed (one file per type, not monolithic location.py as originally planned):
- src/bluetooth_sig/types/advertising/indoor_positioning.py
  IndoorPositioningConfig(IntFlag) + IndoorPositioningData(msgspec.Struct)
  Flag-driven WGS84/local coords, DataParser for all fields, optional uncertainty guard
- src/bluetooth_sig/types/advertising/transport_discovery.py
  TDSFlags(IntFlag) + TransportBlock + TransportDiscoveryData
  Multi-block iteration, role/state/incomplete as properties on TransportBlock
- src/bluetooth_sig/types/advertising/three_d_information.py
  ThreeDInformationFlags(IntFlag) + ThreeDInformationData
  Boolean properties for flag accessors (single source of truth — no duplicate fields)
- src/bluetooth_sig/types/advertising/channel_map_update.py
  ChannelMapUpdateIndication with is_channel_used(channel) method, named constants
- ad_structures.py LocationAndSensingData fields changed from bytes to typed | None
- pdu_parser.py _handle_location_ad_types calls .decode() instead of raw assignment
- __init__.py exports updated for all new types
- 58 tests across 4 test files (tests/advertising/test_{indoor_positioning,transport_discovery,
  three_d_information,channel_map_update}.py) covering decode, errors, properties, constants
- Patterns followed: IntFlag for all flags, DataParser for all parsing (auto InsufficientDataError),
  msgspec.Struct frozen=True kw_only=True, one file per type
- All 5523 tests pass, lint clean

3.6 — REMOVED (Auxiliary packet parsing is physically impossible)

The _parse_auxiliary_packets stub is correct. The AuxiliaryPointer is a radio scheduling
instruction (channel, offset, PHY), not data. Resolving auxiliary chains requires real-time radio
access — impossible in a pure parser. If a PDU stream correlator is ever needed, it belongs in the
stream module, matching AuxiliaryPointer fields across separately captured PDUs.

3.7 Stream Module: TTL Eviction + Stats

TTL eviction prevents memory leaks in long-running processes (e.g. Home Assistant running for
months). A device that sends a glucose measurement but never the context leaves an incomplete
group in _buffer forever. The async variant is deferred — the sync callback pattern works well
with async callers already.

Changes to DependencyPairingBuffer:
- Add max_age_seconds: float | None = None parameter to __init__
- Store _group_timestamps: dict[Hashable, float] for first-seen time per group
- In ingest(), call _evict_stale() before processing (removes groups older than max_age_seconds)
- Add stats() → BufferStats(pending: int, completed: int, evicted: int) dataclass
- Track _completed_count and _evicted_count as instance counters

Tests in tests/stream/test_pairing.py (extend existing file):
- TTL eviction: ingest partial group, advance time past TTL, verify stale group evicted
- Stats: verify counters after completions and evictions
- No-TTL default: existing tests pass unchanged

Verification: python -m pytest tests/stream/ -v passes. No breaking changes.

Implementation Priority:

| # | Item | Effort | Value | Risk | Status |
|---|------|--------|-------|------|--------|
| 1 | 3.1 Fix PeripheralDevice + tests | Low | Medium | Low | ✅ DONE |
| 2 | 3.5 Location AD struct parsing | Medium | High | Low | ✅ DONE |
| 3 | 3.7 Stream TTL + stats | Low | Medium | Low | Not started |
| 4 | 3.4 GATT coverage gap tracking | Low | Medium | None | Not started |
| 5 | 3.2 Profile parameter registries | Medium | Medium | Medium | Not started |

Verification: Each feature has its own test file with success + failure cases. All quality gates pass.

Workstream 4: Testing & Quality Infrastructure
4.1 Add property-based testing with Hypothesis

Add hypothesis to [project.optional-dependencies.test] in pyproject.toml
Target: parsing round-trip invariant — for every characteristic that supports parse_value + build_value, parse(build(x)) == x
Start with numeric templates (Uint8Template, Sint16Template, PercentageTemplate) — generate random valid ranges
Add fuzz tests for PDU parser: random bytes should never crash (return error, not exception)
4.2 Raise coverage threshold

Current: 70% in test-coverage.yml
Target: 85%
Identify uncovered paths using pytest --cov-report=html and write targeted tests
4.3 Enable benchmarks in CI

Add a separate CI job in test-coverage.yml that runs pytest tests/benchmarks/ --benchmark-only
Store benchmark results as CI artefacts
Add regression detection: fail if any benchmark regresses >20% from baseline
Use scripts/update_benchmark_history.py to track trends
4.4 Add integration test for round-trip encoding

New test: tests/integration/test_round_trip.py

For every characteristic that implements both parse_value and build_value, verify parse(build(x)) == x
Systematic coverage, not just spot-checks
Verification: python -m pytest tests/ -v --cov --cov-fail-under=85 passes. Benchmark job runs in CI.

Workstream 5: Documentation & Examples
5.1 Fix misleading README code samples

The README.md "Translator API (Device Scanning)" section shows result.info.name and result.value — but parse_characteristic returns the parsed value directly, not a wrapper object. Fix the code sample to match actual API.

5.2 Document undocumented features in README

Add sections for:

Stream module (DependencyPairingBuffer)
PeripheralManagerProtocol (and PeripheralDevice once built)
EAD encryption/decryption support
Async session API (AsyncParsingSession)
5.3 Generate static CHANGELOG.md

git-cliff is configured but no CHANGELOG file exists. Add a just changelog command and generate CHANGELOG.md from git history. Add to CI release workflow.

5.4 Clean up examples

Remove stubs in with_bleak_retry.py (robust_service_discovery and notification_monitoring that print "not yet implemented")
Either implement or remove incomplete examples
Remove emoji from output strings (keep professional)
5.5 Update copilot instructions

Remove TYPE_CHECKING prohibition (it was already violated in 3 places; with Python >=3.10, the need disappears anyway)
Update Python version references
Add the new module boundaries from Workstream 1 to architecture docs
Verification: pytest tests/docs/test_docs_code_blocks.py passes (validates code samples in docs). Link checking on all markdown files.