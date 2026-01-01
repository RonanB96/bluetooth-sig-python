"""URI Schemes registry for Bluetooth SIG URI beacon parsing.

Used during advertising data parsing to decode Eddystone URI beacons
and other URI-based beacon formats.
"""

from __future__ import annotations

import logging

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.uri_schemes import UriSchemeInfo

logger = logging.getLogger(__name__)


class UriSchemesRegistry(BaseGenericRegistry[UriSchemeInfo]):
    """Registry for Bluetooth URI schemes with lazy loading.

    This registry loads URI scheme definitions from the official Bluetooth SIG
    assigned_numbers YAML file, enabling URI beacon decoding for Eddystone
    and similar beacon formats.

    The value field is used as a compact encoding for URI prefixes in
    advertising data, reducing packet size for common schemes like http://.

    Examples:
        >>> from bluetooth_sig.registry.core.uri_schemes import uri_schemes_registry
        >>> info = uri_schemes_registry.get_uri_scheme_info(0x16)
        >>> info.name
        'http:'
    """

    def __init__(self) -> None:
        """Initialize the URI schemes registry."""
        super().__init__()
        self._uri_schemes: dict[int, UriSchemeInfo] = {}
        self._uri_schemes_by_name: dict[str, UriSchemeInfo] = {}

    def _load(self) -> None:
        """Perform the actual loading of URI schemes data."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            logger.warning("Bluetooth SIG path not found. URI schemes registry will be empty.")
            self._loaded = True
            return

        yaml_path = base_path.parent / "core" / "uri_schemes.yaml"
        if not yaml_path.exists():
            logger.warning(
                "URI schemes YAML file not found at %s. Registry will be empty.",
                yaml_path,
            )
            self._loaded = True
            return

        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "uri_schemes" not in data:
                logger.warning("Invalid URI schemes YAML format. Registry will be empty.")
                self._loaded = True
                return

            for item in data["uri_schemes"]:
                value = item.get("value")
                name = item.get("name")

                if value is None or not name:
                    continue

                # Handle hex values in YAML (e.g., 0x16)
                if isinstance(value, str):
                    value = int(value, 16)

                uri_scheme_info = UriSchemeInfo(
                    value=value,
                    name=name,
                )

                self._uri_schemes[value] = uri_scheme_info
                self._uri_schemes_by_name[name.lower()] = uri_scheme_info

            logger.info("Loaded %d URI schemes from specification", len(self._uri_schemes))
        except (FileNotFoundError, OSError, msgspec.DecodeError, KeyError) as e:
            logger.warning(
                "Failed to load URI schemes from YAML: %s. Registry will be empty.",
                e,
            )

        self._loaded = True

    def get_uri_scheme_info(self, value: int) -> UriSchemeInfo | None:
        """Get URI scheme info by value (lazy loads on first call).

        Args:
            value: The URI scheme value (e.g., 0x16 for "http:")

        Returns:
            UriSchemeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._uri_schemes.get(value)

    def get_uri_scheme_by_name(self, name: str) -> UriSchemeInfo | None:
        """Get URI scheme info by name (lazy loads on first call).

        Args:
            name: URI scheme name (case-insensitive, e.g., "http:", "https:")

        Returns:
            UriSchemeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._uri_schemes_by_name.get(name.lower())

    def is_known_uri_scheme(self, value: int) -> bool:
        """Check if URI scheme is known (lazy loads on first call).

        Args:
            value: The URI scheme value to check

        Returns:
            True if the URI scheme is registered, False otherwise
        """
        self._ensure_loaded()
        with self._lock:
            return value in self._uri_schemes

    def get_all_uri_schemes(self) -> dict[int, UriSchemeInfo]:
        """Get all registered URI schemes (lazy loads on first call).

        Returns:
            Dictionary mapping URI scheme values to UriSchemeInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return self._uri_schemes.copy()

    def decode_uri_prefix(self, value: int) -> str:
        """Decode a URI scheme value to its string prefix.

        Convenience method for beacon parsing that returns the scheme
        string directly, or an empty string if unknown.

        Args:
            value: The URI scheme value from beacon data

        Returns:
            The URI scheme string (e.g., "http:"), or empty string if unknown
        """
        info = self.get_uri_scheme_info(value)
        return info.name if info else ""


# Global singleton instance
uri_schemes_registry = UriSchemesRegistry()
