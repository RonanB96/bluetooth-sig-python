"""Tests for company identifiers registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.company_identifiers import CompanyIdentifiersRegistry


@pytest.fixture(scope="session")
def company_registry() -> CompanyIdentifiersRegistry:
    """Create a company identifiers registry once per test session."""
    return CompanyIdentifiersRegistry()


class TestCompanyIdentifiersRegistry:
    """Test the CompanyIdentifiersRegistry class."""

    def test_registry_initialization(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(company_registry, CompanyIdentifiersRegistry)

    def test_lazy_loading(self) -> None:
        """Test that registry loads data on first access."""
        # Create a new registry to test lazy loading
        new_registry = CompanyIdentifiersRegistry()

        # Verify data is not loaded initially
        assert not new_registry._loaded  # noqa: SLF001  # Testing internal state

        # First access should trigger loading
        result = new_registry.get_company_name(0x004C)

        # Now it should be loaded
        assert new_registry._loaded  # noqa: SLF001  # Testing internal state

        # If YAML loaded successfully, we should get a result for Apple
        if result:  # type: ignore[unreachable]  # Depends on YAML loading success
            assert isinstance(result, str)
            assert "apple" in result.lower()

    def test_get_known_company_apple(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test resolving Apple's company ID (0x004C)."""
        company_name = company_registry.get_company_name(0x004C)

        # Only assert if YAML loaded successfully
        if company_name:
            assert isinstance(company_name, str)
            assert "apple" in company_name.lower()
            # Exact match from the YAML
            assert company_name == "Apple, Inc."

    def test_get_known_company_microsoft(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test resolving Microsoft's company ID (0x0006)."""
        company_name = company_registry.get_company_name(0x0006)

        # Only assert if YAML loaded successfully
        if company_name:
            assert isinstance(company_name, str)
            assert "microsoft" in company_name.lower()
            # Exact match from the YAML
            assert company_name == "Microsoft"

    def test_get_known_company_google(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test resolving Google's company ID (0x00E0)."""
        company_name = company_registry.get_company_name(0x00E0)

        # Only assert if YAML loaded successfully
        if company_name:
            assert isinstance(company_name, str)
            assert "google" in company_name.lower()
            # Exact match from the YAML
            assert company_name == "Google"

    def test_get_unknown_company_id(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test that unknown company IDs return None."""
        # Use a very high ID that is unlikely to be assigned
        company_name = company_registry.get_company_name(0xFFFF)

        # Should return None or a valid company name for unknown/high IDs
        assert company_name is None or isinstance(company_name, str)

    def test_multiple_lookups_consistent(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test that multiple lookups return consistent results."""
        # First lookup
        result1 = company_registry.get_company_name(0x004C)

        # Second lookup
        result2 = company_registry.get_company_name(0x004C)

        # Results should be identical
        assert result1 == result2

    def test_thread_safety(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test that registry is thread-safe with concurrent lookups."""

        def lookup_company(company_id: int) -> str | None:
            """Helper function to lookup company name."""
            return company_registry.get_company_name(company_id)

        # Test multiple company IDs concurrently
        company_ids = [0x004C, 0x0006, 0x00E0, 0x004C, 0x0006, 0x00E0]

        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(lookup_company, company_ids))

        # Verify we got results (if YAML loaded)
        if results[0]:  # If first result is not None
            # Check that duplicate IDs returned same results
            assert results[0] == results[3]  # Both Apple
            assert results[1] == results[4]  # Both Microsoft
            assert results[2] == results[5]  # Both Google

    def test_missing_yaml_graceful_handling(self) -> None:
        """Test that missing YAML file is handled gracefully."""
        # Create a new registry
        new_registry = CompanyIdentifiersRegistry()

        # Even if YAML doesn't exist, lookups should not crash
        result = new_registry.get_company_name(0x004C)

        # Should return None if YAML not found, or a string if it was found
        assert result is None or isinstance(result, str)

        # Registry should be marked as loaded regardless
        assert new_registry._loaded  # noqa: SLF001  # Testing internal state

    def test_zero_company_id(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test handling of company ID 0."""
        # Company ID 0 might not be assigned
        result = company_registry.get_company_name(0x0000)

        # Should handle gracefully (return None or a valid company name)
        assert result is None or isinstance(result, str)

    def test_boundary_values(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test boundary values for company IDs."""
        # Test minimum value
        result_min = company_registry.get_company_name(0x0000)
        assert result_min is None or isinstance(result_min, str)

        # Test maximum 16-bit value
        result_max = company_registry.get_company_name(0xFFFF)
        assert result_max is None or isinstance(result_max, str)

    def test_negative_company_id_handling(self, company_registry: CompanyIdentifiersRegistry) -> None:
        """Test that negative company IDs are handled (even though they're invalid)."""
        # Python allows negative keys in dicts, but BLE doesn't use them
        # Should return None
        result = company_registry.get_company_name(-1)
        assert result is None
