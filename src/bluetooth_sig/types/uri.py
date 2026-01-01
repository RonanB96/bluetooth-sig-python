"""URI data types for Bluetooth advertising."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.core.uri_schemes import uri_schemes_registry
from bluetooth_sig.types.registry.uri_schemes import UriSchemeInfo


class URIData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed URI from Bluetooth advertising data.

    The Bluetooth SIG URI AD type (0x24) uses a compressed format where
    the first byte is a scheme code from the URI Schemes registry, followed
    by the remainder of the URI encoded as UTF-8.

    For example:
        - 0x16 = "http:" prefix
        - 0x17 = "https:" prefix

    Attributes:
        scheme_code: Raw scheme code from first byte (0 if plain URI)
        scheme_info: Resolved scheme information from registry
        full_uri: Complete decoded URI with scheme prefix
        raw_data: Original raw bytes from advertising data
    """

    scheme_code: int
    """Raw URI scheme code from the first byte of encoded data."""

    scheme_info: UriSchemeInfo | None = None
    """Resolved scheme info from UriSchemesRegistry, or None if unknown."""

    full_uri: str = ""
    """Complete URI with resolved scheme prefix."""

    raw_data: bytes = b""
    """Original raw advertising data bytes."""

    @property
    def scheme_name(self) -> str:
        """Get the URI scheme name (e.g., 'http:', 'https:').

        Returns:
            Scheme name from registry, or empty string if unknown.
        """
        return self.scheme_info.name if self.scheme_info else ""

    @property
    def is_known_scheme(self) -> bool:
        """Check if the URI scheme is a known Bluetooth SIG registered scheme.

        Returns:
            True if scheme_code resolved to a known scheme.
        """
        return self.scheme_info is not None

    @classmethod
    def from_raw_data(cls, data: bytes) -> URIData:
        r"""Parse URI advertising data using Bluetooth SIG encoding.

        The first byte is a URI scheme code from the registry. The remaining
        bytes are the URI suffix encoded as UTF-8.

        Args:
            data: Raw bytes from URI AD type (ADType 0x24)

        Returns:
            URIData with decoded URI and scheme information

        Example:
            >>> # 0x17 = "https:", followed by "//example.com"
            >>> uri_data = URIData.from_raw_data(b"\x17//example.com")
            >>> uri_data.full_uri
            'https://example.com'
            >>> uri_data.scheme_name
            'https:'
        """
        if not data:
            return cls(scheme_code=0, raw_data=data)

        scheme_code = data[0]
        scheme_info = uri_schemes_registry.get_uri_scheme_info(scheme_code)

        # Decode the URI suffix (remaining bytes after scheme code)
        try:
            uri_suffix = data[1:].decode("utf-8") if len(data) > 1 else ""
        except UnicodeDecodeError:
            # Fall back to hex representation if not valid UTF-8
            uri_suffix = data[1:].hex() if len(data) > 1 else ""

        # Build full URI by combining scheme prefix with suffix
        scheme_prefix = scheme_info.name if scheme_info else ""
        full_uri = f"{scheme_prefix}{uri_suffix}"

        return cls(
            scheme_code=scheme_code,
            scheme_info=scheme_info,
            full_uri=full_uri,
            raw_data=data,
        )

    @classmethod
    def from_plain_uri(cls, uri: str) -> URIData:
        """Create URIData from a plain URI string (no scheme encoding).

        Use this for URIs that aren't using Bluetooth SIG compressed encoding.

        Args:
            uri: Plain URI string

        Returns:
            URIData with the URI stored directly
        """
        return cls(
            scheme_code=0,
            full_uri=uri,
            raw_data=uri.encode("utf-8"),
        )
