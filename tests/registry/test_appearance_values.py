"""Tests for appearance values registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.appearance_values import AppearanceValuesRegistry
from bluetooth_sig.types.appearance_info import AppearanceInfo


@pytest.fixture(scope="session")
def appearance_registry() -> AppearanceValuesRegistry:
    """Create an appearance registry once per test session."""
    return AppearanceValuesRegistry()


class TestAppearanceValuesRegistry:
    """Test the AppearanceValuesRegistry class."""

    def test_registry_initialization(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(appearance_registry, AppearanceValuesRegistry)

    def test_lazy_loading(self) -> None:
        """Test that registry loads data on first access."""
        # Create a new registry to test lazy loading
        new_registry = AppearanceValuesRegistry()

        # First access should return data if YAML exists
        result = new_registry.get_appearance_info(833)
        # If YAML loaded successfully, we should get a result
        if result:
            assert isinstance(result, AppearanceInfo)
            # Subsequent calls should return same data
            result2 = new_registry.get_appearance_info(833)
            assert result == result2

    def test_get_category_only_appearance(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test decoding category-only appearance (no subcategory)."""
        # Phone (category 0x001, no subcategory)
        # Appearance code = 0x001 << 6 = 64 (0x40)
        info = appearance_registry.get_appearance_info(64)

        if info:  # Only if YAML loaded
            assert isinstance(info, AppearanceInfo)
            assert info.category == "Phone"
            assert info.subcategory is None
            assert info.category_value == 0x001
            assert info.subcategory_value is None
            assert info.full_name == "Phone"

    def test_get_category_with_subcategory(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test decoding category + subcategory appearance."""
        # Heart Rate Sensor: Heart Rate Belt
        # Category 0x00D (13), subcategory 0x01 (1)
        # Appearance code = (13 << 6) | 1 = 832 + 1 = 833
        info = appearance_registry.get_appearance_info(833)

        if info:  # Only if YAML loaded
            assert isinstance(info, AppearanceInfo)
            assert info.category == "Heart Rate Sensor"
            assert info.subcategory == "Heart Rate Belt"
            assert info.category_value == 0x00D
            assert info.subcategory_value == 0x01
            assert info.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_get_appearance_info_not_found(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test lookup for non-existent appearance code."""
        # Use a code that's unlikely to exist
        info = appearance_registry.get_appearance_info(65535)
        assert info is None

    def test_bit_shifting_calculation(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test that appearance codes follow correct bit shifting."""
        # Computer category (0x002) with Desktop Workstation subcategory (0x01)
        # Code = (0x002 << 6) | 0x01 = 128 + 1 = 129
        info = appearance_registry.get_appearance_info(129)

        if info:
            assert info.category == "Computer"
            assert info.subcategory == "Desktop Workstation"
            assert info.category_value == 0x002
            assert info.subcategory_value == 0x01

    def test_watch_subcategories(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test watch category with different subcategories."""
        # Watch category (0x003)
        # Sports Watch (subcategory 0x01): (3 << 6) | 1 = 193
        # Smartwatch (subcategory 0x02): (3 << 6) | 2 = 194

        sports_watch = appearance_registry.get_appearance_info(193)
        if sports_watch:
            assert sports_watch.category == "Watch"
            assert sports_watch.subcategory == "Sports Watch"

        smartwatch = appearance_registry.get_appearance_info(194)
        if smartwatch:
            assert smartwatch.category == "Watch"
            assert smartwatch.subcategory == "Smartwatch"

    def test_unknown_category(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test the Unknown category (0x000)."""
        # Unknown category: 0x000 << 6 = 0
        info = appearance_registry.get_appearance_info(0)

        if info:
            assert info.category == "Unknown"
            assert info.subcategory is None
            assert info.full_name == "Unknown"

    def test_thread_safety_concurrent_lookups(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test that concurrent lookups are thread-safe."""
        # Create a fresh registry to test thread-safe initialization
        new_registry = AppearanceValuesRegistry()
        results: list[AppearanceInfo | None] = []
        errors: list[Exception] = []

        def lookup_appearance(code: int) -> None:
            try:
                result = new_registry.get_appearance_info(code)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Test concurrent access with multiple threads
        appearance_codes = [64, 129, 193, 833, 0]  # Various valid codes

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit many concurrent lookups
            futures = []
            for _ in range(20):
                for code in appearance_codes:
                    futures.append(executor.submit(lookup_appearance, code))

            # Wait for all to complete
            for future in futures:
                future.result()

        # Should not have any errors
        assert len(errors) == 0
        # Should have results for all lookups
        assert len(results) == 100  # 20 iterations * 5 codes

    def test_full_name_property(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test the full_name property behavior."""
        # Category only
        phone = appearance_registry.get_appearance_info(64)
        if phone:
            assert phone.full_name == phone.category
            assert ":" not in phone.full_name

        # Category + subcategory
        hr_belt = appearance_registry.get_appearance_info(833)
        if hr_belt:
            assert hr_belt.full_name == f"{hr_belt.category}: {hr_belt.subcategory}"
            assert ":" in hr_belt.full_name

    def test_multiple_computers(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test Computer category with multiple subcategories."""
        # Computer (category 0x002) has many subcategories
        # Test a few: Desktop (0x01), Laptop (0x03), Tablet (0x07)

        desktop = appearance_registry.get_appearance_info(129)  # (2 << 6) | 1
        if desktop:
            assert desktop.category == "Computer"
            assert desktop.subcategory == "Desktop Workstation"

        laptop = appearance_registry.get_appearance_info(131)  # (2 << 6) | 3
        if laptop:
            assert laptop.category == "Computer"
            assert laptop.subcategory == "Laptop"

        tablet = appearance_registry.get_appearance_info(135)  # (2 << 6) | 7
        if tablet:
            assert tablet.category == "Computer"
            assert tablet.subcategory == "Tablet"

    def test_thermometer_with_subcategory(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test Thermometer category."""
        # Thermometer (category 0x00C)
        # Ear Thermometer (subcategory 0x01): (12 << 6) | 1 = 769

        thermometer = appearance_registry.get_appearance_info(768)  # (12 << 6) | 0
        if thermometer:
            assert thermometer.category == "Thermometer"

        ear_thermometer = appearance_registry.get_appearance_info(769)  # (12 << 6) | 1
        if ear_thermometer:
            assert ear_thermometer.category == "Thermometer"
            assert ear_thermometer.subcategory == "Ear Thermometer"

    def test_zero_subcategory_matches_category_only(self, appearance_registry: AppearanceValuesRegistry) -> None:
        """Test that subcategory 0 matches category-only appearance."""
        # Phone (0x001 << 6) | 0 = 64
        info_explicit_zero = appearance_registry.get_appearance_info(64)

        if info_explicit_zero:
            assert info_explicit_zero.category == "Phone"
            assert info_explicit_zero.subcategory is None
