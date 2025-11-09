"""Company identifier registries from assigned_numbers/company_identifiers/.

This module contains the registry for manufacturer company IDs, allowing
resolution of Bluetooth SIG company identifiers to company names.
"""

from bluetooth_sig.registry.company_identifiers.company_identifiers_registry import (
    CompanyIdentifiersRegistry,
    company_identifiers_registry,
)

__all__ = [
    "CompanyIdentifiersRegistry",
    "company_identifiers_registry",
]
