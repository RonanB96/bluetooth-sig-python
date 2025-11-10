"""Pytest configuration helpers.

Ensure repository root and `src/` are on `sys.path` so tests can import
local packages without per-test sys.path hacks.
"""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
# Export ROOT_DIR for tests that need to construct paths relative to project root
ROOT_DIR = ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Skip all tests marked 'benchmark' unless -m benchmark is passed
    if not config.getoption("-m"):
        skip_benchmark = pytest.mark.skip(reason="Skipped by default. Use -m benchmark to run benchmarks.")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_benchmark)


@pytest.fixture(scope="session", autouse=True)
def clear_module_level_registrations() -> None:
    """Clear custom registrations that happened during module import/collection.

    This runs ONCE at the START of the test session, AFTER pytest has collected
    all tests (which imports all test modules). Module-level custom characteristic
    definitions (like SimpleTemperatureSensor, CustomCharacteristicImpl, etc.)
    register themselves when their modules are imported.

    This fixture cleans up those registrations before ANY test runs.
    """
    from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
    from bluetooth_sig.gatt.services.registry import GattServiceRegistry
    from bluetooth_sig.gatt.uuid_registry import uuid_registry

    # Clear all custom registrations that happened during module imports
    CharacteristicRegistry.clear_custom_registrations()
    GattServiceRegistry.clear_custom_registrations()
    uuid_registry.clear_custom_registrations()


@pytest.fixture(autouse=True)
def reset_registries() -> Generator[None, None, None]:
    """Reset characteristic and service registries before and after EVERY test.

    This fixture runs automatically for every test (autouse=True) to ensure
    complete test isolation. It cleans up:
    1. Custom characteristics/services registered at module level
    2. SIG characteristic/service overrides from previous tests

    The fixture runs:
    - BEFORE each test: clears any pollution from module-level registrations
    - AFTER each test: cleans up any registrations made during the test

    This is required because pytest imports all test modules during collection,
    which triggers module-level class registrations BEFORE any test runs.
    Without autouse, these registrations persist and pollute tests that expect
    clean SIG registries.

    NOTE: We intentionally do NOT clear the SIG characteristic/service caches
    (_CharacteristicMapBuilder and _ServiceClassMapBuilder caches) because:
    1. Clearing caches forces expensive re-discovery of all SIG classes
    2. SIG characteristics are immutable - no need to rediscover them
    3. Custom registrations are handled separately via clear_custom_registrations()
    """
    from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
    from bluetooth_sig.gatt.services.registry import GattServiceRegistry
    from bluetooth_sig.gatt.uuid_registry import uuid_registry

    # Clear custom registrations BEFORE test
    CharacteristicRegistry.clear_custom_registrations()
    GattServiceRegistry.clear_custom_registrations()
    uuid_registry.clear_custom_registrations()

    yield

    # Clear custom registrations AFTER test
    CharacteristicRegistry.clear_custom_registrations()
    GattServiceRegistry.clear_custom_registrations()
    uuid_registry.clear_custom_registrations()
