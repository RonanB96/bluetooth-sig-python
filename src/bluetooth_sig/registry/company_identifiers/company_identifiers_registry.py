"""Company Identifiers Registry for Bluetooth SIG manufacturer IDs."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseRegistry


class CompanyIdentifiersRegistry(BaseRegistry[str]):
    """Registry for Bluetooth SIG company identifiers with lazy loading.

    This registry resolves manufacturer company IDs to company names from
    the official Bluetooth SIG assigned numbers. Data is lazily loaded on
    first access for performance.

    Thread-safe: Multiple threads can safely access the registry concurrently.
    """

    def __init__(self) -> None:
        """Initialize the company identifiers registry."""
        super().__init__()
        self._companies: dict[int, str] = {}
        self._loaded = False
        self._lock = threading.RLock()

    def _load_company_identifiers(self, yaml_path: Path) -> None:
        """Load company identifiers from YAML file.

        Args:
            yaml_path: Path to the company_identifiers.yaml file
        """
        if not yaml_path.exists():
            return

        with yaml_path.open("r", encoding="utf-8") as file_handle:
            data = msgspec.yaml.decode(file_handle.read())

        if not isinstance(data, dict):
            return

        data_dict = cast(dict[str, Any], data)
        company_entries = data_dict.get("company_identifiers")
        if not isinstance(company_entries, list):
            return

        # Load all company identifiers into cache
        for entry in company_entries:
            if isinstance(entry, dict):
                company_id = entry.get("value")
                company_name = entry.get("name")
                if company_id is not None and company_name:
                    self._companies[company_id] = company_name

    def _ensure_loaded(self) -> None:
        """Lazy load: only parse YAML when first lookup happens.

        This method uses double-checked locking for thread safety and
        performance. The YAML file is only loaded once, on the first call
        to get_company_name().
        """
        if self._loaded:
            return

        with self._lock:
            if self._loaded:  # Double-check after acquiring lock
                return  # type: ignore[unreachable]  # Double-checked locking pattern

            # Find the bluetooth_sig submodule path
            base_path = self._find_company_identifiers_path()
            if not base_path:
                self._loaded = True
                return

            yaml_path = base_path / "company_identifiers.yaml"
            if not yaml_path.exists():
                self._loaded = True
                return

            # Load company identifiers from YAML
            self._load_company_identifiers(yaml_path)

            self._loaded = True

    def _find_company_identifiers_path(self) -> Path | None:
        """Find the Bluetooth SIG company_identifiers directory.

        Returns:
            Path to the company_identifiers directory, or None if not found
        """
        # Try development location first (git submodule)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        base_path = project_root / "bluetooth_sig" / "assigned_numbers" / "company_identifiers"

        if base_path.exists():
            return base_path

        # Try installed package location
        pkg_root = Path(__file__).parent.parent.parent
        base_path = pkg_root / "bluetooth_sig" / "assigned_numbers" / "company_identifiers"

        return base_path if base_path.exists() else None

    def get_company_name(self, company_id: int) -> str | None:
        """Get company name by ID (lazy loads on first call).

        Args:
            company_id: Manufacturer company identifier (e.g., 0x004C for Apple)

        Returns:
            Company name or None if not found

        Examples:
            >>> registry = CompanyIdentifiersRegistry()
            >>> registry.get_company_name(0x004C)
            'Apple, Inc.'
            >>> registry.get_company_name(0x0006)
            'Microsoft'
            >>> registry.get_company_name(0x00E0)
            'Google'
            >>> registry.get_company_name(0xFFFF)  # Unknown ID
            None
        """
        self._ensure_loaded()
        return self._companies.get(company_id)


# Singleton instance for global use
company_identifiers_registry = CompanyIdentifiersRegistry()
