"""Custom characteristic base class with auto-registration support."""

from __future__ import annotations

from typing import Any

from ...types import CharacteristicInfo
from .base import BaseCharacteristic


class CustomBaseCharacteristic(BaseCharacteristic):
    r"""Helper base class for custom characteristic implementations.

    This class provides a wrapper around physical BLE characteristics that are not
    defined in the Bluetooth SIG specification. It supports both manual info passing
    and automatic class-level _info binding via __init_subclass__.

    Auto-Registration:
        Custom characteristics automatically register themselves with the global
        BluetoothSIGTranslator singleton when first instantiated. No manual
        registration needed!

    Examples:
        >>> from bluetooth_sig.types.data_types import CharacteristicInfo
        >>> from bluetooth_sig.types.uuid import BluetoothUUID
        >>> class MyCharacteristic(CustomBaseCharacteristic):
        ...     _info = CharacteristicInfo(uuid=BluetoothUUID("AAAA"), name="My Char")
        >>> # Auto-registers with singleton on first instantiation
        >>> char = MyCharacteristic()  # Auto-registered!
        >>> # Now accessible via the global translator
        >>> from bluetooth_sig import BluetoothSIGTranslator
        >>> translator = BluetoothSIGTranslator.get_instance()
        >>> result = translator.parse_characteristic("AAAA", b"\x42")
    """

    _is_custom = True
    _is_base_class = True  # Exclude from registry validation tests
    _configured_info: CharacteristicInfo | None = None  # Stores class-level _info
    _allows_sig_override = False  # Default: no SIG override permission
    _registry_tracker: set[str] = set()  # Track registered UUIDs to avoid duplicates

    @classmethod
    def get_configured_info(cls) -> CharacteristicInfo | None:
        """Get the class-level configured CharacteristicInfo.

        Returns:
            CharacteristicInfo if configured, None otherwise

        """
        return cls._configured_info

    # pylint: disable=duplicate-code
    # NOTE: __init_subclass__ and __init__ patterns are intentionally similar to CustomBaseService.
    # This is by design - both custom characteristic and service classes need identical validation
    # and info management patterns. Consolidation not possible due to different base types and info types.
    def __init_subclass__(cls, allow_sig_override: bool = False, **kwargs: Any) -> None:  # noqa: ANN401  # Receives subclass kwargs
        """Automatically set up _info if provided as class attribute.

        Args:
            allow_sig_override: Set to True when intentionally overriding SIG UUIDs.
            **kwargs: Additional subclass keyword arguments passed by callers or
                metaclasses; these are accepted for compatibility and ignored
                unless explicitly handled.

        Raises:
            ValueError: If class uses SIG UUID without override permission.

        """
        super().__init_subclass__(**kwargs)

        # Store override permission for registry validation
        cls._allows_sig_override = allow_sig_override

        # If class has _info attribute, validate and store it
        if hasattr(cls, "_info"):
            info = getattr(cls, "_info", None)
            if info is not None:
                # Check for SIG UUID override (unless explicitly allowed)
                if not allow_sig_override and info.uuid.is_sig_characteristic():
                    raise ValueError(
                        f"{cls.__name__} uses SIG UUID {info.uuid} without override flag. "
                        "Use custom UUID or add allow_sig_override=True parameter."
                    )

                cls._configured_info = info

    def __init__(
        self,
        info: CharacteristicInfo | None = None,
        auto_register: bool = True,
    ) -> None:
        """Initialize a custom characteristic with automatic _info resolution and registration.

        Args:
            info: Optional override for class-configured _info
            auto_register: If True (default), automatically register with global translator singleton

        Raises:
            ValueError: If no valid info available from class or parameter

        Examples:
            >>> # Simple usage - auto-registers with global translator
            >>> char = MyCharacteristic()  # Auto-registered!
            >>> # Opt-out of auto-registration if needed
            >>> char = MyCharacteristic(auto_register=False)

        """
        # Use provided info, or fall back to class-configured _info
        final_info = info or self.__class__.get_configured_info()

        if not final_info:
            raise ValueError(f"{self.__class__.__name__} requires either 'info' parameter or '_info' class attribute")

        if not final_info.uuid or str(final_info.uuid) == "0000":
            raise ValueError("Valid UUID is required for custom characteristics")

        # Auto-register if requested and not already registered
        if auto_register:
            # TODO
            # NOTE: Import here to avoid circular import (translator imports characteristics)
            from ...core.translator import BluetoothSIGTranslator  # pylint: disable=import-outside-toplevel

            # Get the singleton translator instance
            translator = BluetoothSIGTranslator.get_instance()

            # Track registration to avoid duplicate registrations
            uuid_str = str(final_info.uuid)
            registry_key = f"{id(translator)}:{uuid_str}"

            if registry_key not in CustomBaseCharacteristic._registry_tracker:
                # Register this characteristic class with the translator
                # Use override=True to allow re-registration (idempotent behaviour)
                translator.register_custom_characteristic_class(
                    uuid_str,
                    self.__class__,
                    override=True,  # Allow override for idempotent registration
                )
                CustomBaseCharacteristic._registry_tracker.add(registry_key)

        # Call parent constructor with our info to maintain consistency
        super().__init__(info=final_info)

    def __post_init__(self) -> None:
        """Override BaseCharacteristic.__post_init__ to use custom info management.

        CustomBaseCharacteristic manages _info manually from provided or configured info,
        bypassing SIG resolution that would fail for custom characteristics.
        """
        # Use provided info if available (from manual override), otherwise use configured info
        if hasattr(self, "_provided_info") and self._provided_info:
            self._info = self._provided_info
        else:
            configured_info = self.__class__.get_configured_info()
            if configured_info:
                self._info = configured_info
            else:
                # This shouldn't happen if class setup is correct
                raise ValueError(f"CustomBaseCharacteristic {self.__class__.__name__} has no valid info source")
