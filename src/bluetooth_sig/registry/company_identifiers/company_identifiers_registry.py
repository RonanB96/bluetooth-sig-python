"""Company Identifiers Registry for Bluetooth SIG manufacturer IDs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path


class CompanyIdentifierInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG company identifier."""

    id: int
    name: str


class CompanyIdentifiersRegistry(BaseGenericRegistry[CompanyIdentifierInfo]):
    """Registry for Bluetooth SIG company identifiers with lazy loading.

    This registry resolves manufacturer company IDs to company names from
    the official Bluetooth SIG assigned numbers. Data is lazily loaded on
    first access for performance.

    Thread-safe: Multiple threads can safely access the registry concurrently.
    """

    def __init__(self) -> None:
        """Initialize the company identifiers registry."""
        super().__init__()
        self._companies: dict[int, CompanyIdentifierInfo] = {}

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

        data_dict = cast("dict[str, Any]", data)
        company_entries = data_dict.get("company_identifiers")
        if not isinstance(company_entries, list):
            return

        # Load all company identifiers into cache
        for entry in company_entries:
            if isinstance(entry, dict):
                company_id = entry.get("value")
                company_name = entry.get("name")
                if company_id is not None and company_name:
                    self._companies[company_id] = CompanyIdentifierInfo(id=company_id, name=company_name)

    def _load(self) -> None:
        """Perform the actual loading of company identifiers data."""
        # Use find_bluetooth_sig_path and navigate to company_identifiers
        uuids_path = find_bluetooth_sig_path()
        if not uuids_path:
            self._loaded = True
            return

        # Navigate from uuids/ to company_identifiers/
        base_path = uuids_path.parent / "company_identifiers"
        if not base_path.exists():
            self._loaded = True
            return

        yaml_path = base_path / "company_identifiers.yaml"
        if not yaml_path.exists():
            self._loaded = True
            return

        # Load company identifiers from YAML
        self._load_company_identifiers(yaml_path)
        self._loaded = True

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
        with self._lock:
            info = self._companies.get(company_id)
            return info.name if info else None


# Singleton instance for global use
company_identifiers_registry = CompanyIdentifiersRegistry()
