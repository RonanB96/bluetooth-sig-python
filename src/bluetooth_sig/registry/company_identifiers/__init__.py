"""Company identifier registries from assigned_numbers/company_identifiers/.

This module contains the registry for manufacturer company IDs, allowing
resolution of Bluetooth SIG company identifiers to company names.
"""

from __future__ import annotations

from .company_identifiers_registry import (
    CompanyIdentifiersRegistry,
    get_company_identifiers_registry,
)

__all__ = [
    "CompanyIdentifiersRegistry",
    "get_company_identifiers_registry",
]
