"""Company identifier types for Bluetooth SIG manufacturer IDs.

Provides a unified type that encapsulates both the numeric company ID
and its resolved human-readable name from the Bluetooth SIG registry.
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.gatt.constants import SIZE_UINT16
from bluetooth_sig.registry.company_identifiers import company_identifiers_registry


class CompanyIdentifier(msgspec.Struct, kw_only=True, frozen=True):
    """Bluetooth SIG company identifier with resolved name.

    Encapsulates both the numeric company ID and its resolved name,
    providing a single source of truth for manufacturer identification
    in advertising data.

    Attributes:
        id: Numeric company identifier (16-bit unsigned integer).
        name: Resolved company name from Bluetooth SIG registry.
              Falls back to hex format if not found in registry.

    Example::
        # Direct construction
        apple = CompanyIdentifier(id=0x004C, name="Apple, Inc.")

        # Using factory method (recommended)
        apple = CompanyIdentifier.from_id(0x004C)
        assert apple.id == 0x004C
        assert apple.name == "Apple, Inc."

        # Unknown company ID
        unknown = CompanyIdentifier.from_id(0xFFFF)
        assert unknown.id == 0xFFFF
        assert unknown.name == "Unknown (0xFFFF)"

    """

    id: int
    name: str

    @classmethod
    def from_id(cls, company_id: int) -> CompanyIdentifier:
        """Create CompanyIdentifier from numeric ID with registry lookup.

        Args:
            company_id: Manufacturer company identifier (e.g., 0x004C for Apple).

        Returns:
            CompanyIdentifier with resolved name from registry.

        Example::
            >>> company = CompanyIdentifier.from_id(0x004C)
            >>> company.id
            76
            >>> company.name
            'Apple, Inc.'

        """
        name = company_identifiers_registry.get_company_name(company_id)
        if not name:
            name = f"Unknown (0x{company_id:04X})"
        return cls(id=company_id, name=name)

    def __str__(self) -> str:
        """String representation showing name and hex ID."""
        return f"{self.name} (0x{self.id:04X})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"CompanyIdentifier(id=0x{self.id:04X}, name={self.name!r})"


class ManufacturerData(msgspec.Struct, kw_only=True, frozen=True):
    r"""Manufacturer-specific advertising data.

    Attributes:
        company: Resolved company identifier with ID and name.
        payload: Raw manufacturer-specific data bytes.

    Example::
        # Parse from raw bytes
        mfr_data = ManufacturerData.from_bytes(b"\x4c\x00\x02\x15...")
        print(mfr_data.company.name)  # "Apple, Inc."
        print(mfr_data.payload.hex())  # "0215..."

    """

    company: CompanyIdentifier
    payload: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> ManufacturerData:
        """Parse manufacturer data from raw AD structure bytes.

        Args:
            data: Raw bytes with company ID (little-endian uint16) followed by payload.

        Returns:
            Parsed ManufacturerData with resolved company info.

        Raises:
            ValueError: If data is too short to contain company ID.

        """
        if len(data) < SIZE_UINT16:
            raise ValueError(f"Manufacturer data too short: {len(data)} bytes, need at least {SIZE_UINT16}")

        company_id = int.from_bytes(data[:2], byteorder="little", signed=False)
        payload = data[2:]
        company = CompanyIdentifier.from_id(company_id)

        return cls(company=company, payload=payload)

    @classmethod
    def from_id_and_payload(cls, company_id: int, payload: bytes) -> ManufacturerData:
        """Create manufacturer data from company ID and payload.

        Args:
            company_id: Numeric company identifier.
            payload: Raw manufacturer-specific data bytes.

        Returns:
            ManufacturerData with resolved company info.

        """
        company = CompanyIdentifier.from_id(company_id)
        return cls(company=company, payload=payload)

    def to_bytes(self) -> bytes:
        """Encode manufacturer data to wire format.

        Returns:
            Encoded bytes: company ID (little-endian uint16) + payload.

        """
        return self.company.id.to_bytes(SIZE_UINT16, byteorder="little") + self.payload
