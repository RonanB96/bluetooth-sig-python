"""Custom service implementation for user-defined services."""

from __future__ import annotations

from ...types import ServiceInfo
from .base import BaseGattService


class CustomBaseGattService(BaseGattService):
    """Helper base class for custom service implementations.

    This class provides a wrapper around custom services that are not
    defined in the Bluetooth SIG specification.
    """

    _is_custom = True
    _is_base_class = True  # Exclude from registry validation tests
    _configured_info: ServiceInfo | None = None
    _allows_sig_override = False

    def __init_subclass__(cls, allow_sig_override: bool = False, **kwargs: object) -> None:
        """Set up _info if provided as class attribute.

        Args:
            allow_sig_override: Set to True when intentionally overriding SIG UUIDs
            **kwargs: Additional keyword arguments

        """
        super().__init_subclass__(**kwargs)
        cls._allows_sig_override = allow_sig_override

        info = cls._info
        if info is not None:
            if not allow_sig_override and info.uuid.is_sig_service():
                raise ValueError(f"{cls.__name__} uses SIG UUID {info.uuid} without override flag")
            cls._configured_info = info

    def __init__(self, info: ServiceInfo | None = None) -> None:
        """Initialize a custom service.

        Args:
            info: Optional override for class-configured _info

        """
        final_info = info or self.__class__._configured_info
        if not final_info:
            raise ValueError(f"{self.__class__.__name__} requires 'info' parameter or '_info' class attribute")
        if not final_info.uuid or str(final_info.uuid) == "0000":
            raise ValueError("Valid UUID is required for custom services")
        super().__init__(info=final_info)

    def __post_init__(self) -> None:
        """Initialize custom service info management."""
        if hasattr(self, "_provided_info") and self._provided_info:
            self._info = self._provided_info
        elif self.__class__._configured_info:  # pylint: disable=protected-access
            self._info = self.__class__._configured_info  # pylint: disable=protected-access
        else:
            raise ValueError(f"CustomBaseGattService {self.__class__.__name__} has no valid info source")
