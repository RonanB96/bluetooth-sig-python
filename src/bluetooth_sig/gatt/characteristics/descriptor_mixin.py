"""Descriptor support mixin for GATT characteristics.

Provides all descriptor-related methods (add, get, CCCD, context lookups)
as a mixin that :class:`BaseCharacteristic` inherits from.
"""

from __future__ import annotations

from ...types.registry.descriptor_types import DescriptorData
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..descriptor_utils import enhance_error_message_with_descriptors as _enhance_error_message
from ..descriptor_utils import get_descriptor_from_context as _get_descriptor
from ..descriptor_utils import get_presentation_format_from_context as _get_presentation_format
from ..descriptor_utils import get_user_description_from_context as _get_user_description
from ..descriptor_utils import get_valid_range_from_context as _get_valid_range
from ..descriptor_utils import validate_value_against_descriptor_range as _validate_value_range
from ..descriptors import BaseDescriptor
from ..descriptors.cccd import CCCDDescriptor
from ..descriptors.characteristic_presentation_format import CharacteristicPresentationFormatData


class DescriptorMixin:
    """Mixin providing descriptor management and context lookup helpers.

    Expects the consuming class to initialise ``_descriptors`` as an empty
    ``dict[str, BaseDescriptor]`` in ``__init__``.
    """

    _descriptors: dict[str, BaseDescriptor]

    # ------------------------------------------------------------------
    # Instance descriptor management
    # ------------------------------------------------------------------

    def add_descriptor(self, descriptor: BaseDescriptor) -> None:
        """Add a descriptor to this characteristic.

        Args:
            descriptor: The descriptor instance to add.
        """
        self._descriptors[str(descriptor.uuid)] = descriptor

    def get_descriptor(self, uuid: str | BluetoothUUID) -> BaseDescriptor | None:
        """Get a descriptor by UUID.

        Args:
            uuid: Descriptor UUID (string or BluetoothUUID).

        Returns:
            Descriptor instance if found, ``None`` otherwise.
        """
        if isinstance(uuid, str):
            try:
                uuid_obj = BluetoothUUID(uuid)
            except ValueError:
                return None
        else:
            uuid_obj = uuid

        return self._descriptors.get(uuid_obj.dashed_form)

    def get_descriptors(self) -> dict[str, BaseDescriptor]:
        """Get all descriptors for this characteristic.

        Returns:
            Dict mapping descriptor UUID strings to descriptor instances.
        """
        return self._descriptors.copy()

    def get_cccd(self) -> BaseDescriptor | None:
        """Get the Client Characteristic Configuration Descriptor (CCCD).

        Returns:
            CCCD descriptor instance if present, ``None`` otherwise.
        """
        return self.get_descriptor(CCCDDescriptor().uuid)

    def can_notify(self) -> bool:
        """Check if this characteristic supports notifications.

        Returns:
            ``True`` if the characteristic has a CCCD descriptor.
        """
        return self.get_cccd() is not None

    # ------------------------------------------------------------------
    # Context-based descriptor lookups
    # ------------------------------------------------------------------

    def get_descriptor_from_context(
        self, ctx: CharacteristicContext | None, descriptor_class: type[BaseDescriptor]
    ) -> DescriptorData | None:
        """Get a descriptor of the specified type from the context.

        Args:
            ctx: Characteristic context containing descriptors.
            descriptor_class: The descriptor class to look for.

        Returns:
            DescriptorData if found, ``None`` otherwise.
        """
        return _get_descriptor(ctx, descriptor_class)

    def get_valid_range_from_context(
        self,
        ctx: CharacteristicContext | None = None,
    ) -> tuple[int | float, int | float] | None:
        """Get valid range from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors.

        Returns:
            Tuple of (min, max) values if Valid Range descriptor present, ``None`` otherwise.
        """
        return _get_valid_range(ctx)

    def get_presentation_format_from_context(
        self,
        ctx: CharacteristicContext | None = None,
    ) -> CharacteristicPresentationFormatData | None:
        """Get presentation format from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors.

        Returns:
            CharacteristicPresentationFormatData if present, ``None`` otherwise.
        """
        return _get_presentation_format(ctx)

    def get_user_description_from_context(self, ctx: CharacteristicContext | None = None) -> str | None:
        """Get user description from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors.

        Returns:
            User description string if present, ``None`` otherwise.
        """
        return _get_user_description(ctx)

    def validate_value_against_descriptor_range(self, value: float, ctx: CharacteristicContext | None = None) -> bool:
        """Validate a value against descriptor-defined valid range.

        Args:
            value: Value to validate.
            ctx: Characteristic context containing descriptors.

        Returns:
            ``True`` if value is within valid range or no range defined.
        """
        return _validate_value_range(value, ctx)

    def enhance_error_message_with_descriptors(
        self,
        base_message: str,
        ctx: CharacteristicContext | None = None,
    ) -> str:
        """Enhance error message with descriptor information for better debugging.

        Args:
            base_message: Original error message.
            ctx: Characteristic context containing descriptors.

        Returns:
            Enhanced error message with descriptor context.
        """
        return _enhance_error_message(base_message, ctx)
