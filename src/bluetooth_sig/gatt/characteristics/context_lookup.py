"""Context lookup mixin for GATT characteristics.

Provides methods to retrieve dependency and sibling characteristics from
a :class:`CharacteristicContext`, extracted from :mod:`.base` to keep it
focused on core parsing/encoding.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from ...types import CharacteristicInfo
from ...types.gatt_enums import CharacteristicName
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..uuid_registry import uuid_registry


class ContextLookupMixin:
    """Mixin providing context-based characteristic lookup helpers.

    These methods allow a characteristic to resolve its dependencies and
    siblings from a shared :class:`CharacteristicContext` at parse/encode
    time.
    """

    @staticmethod
    @lru_cache(maxsize=32)
    def _get_characteristic_uuid_by_name(
        characteristic_name: CharacteristicName | str,
    ) -> BluetoothUUID | None:
        """Get characteristic UUID by name using cached registry lookup."""
        name_str = (
            characteristic_name.value if isinstance(characteristic_name, CharacteristicName) else characteristic_name
        )
        char_info = uuid_registry.get_characteristic_info(name_str)
        return char_info.uuid if char_info else None

    def get_context_characteristic(
        self,
        ctx: CharacteristicContext | None,
        characteristic_name: CharacteristicName | str | type,
    ) -> Any:  # noqa: ANN401  # Type determined by characteristic_name at runtime
        """Find a characteristic in a context by name or class.

        Note:
            Returns ``Any`` because the characteristic type is determined at
            runtime by *characteristic_name*.  For type-safe access, use direct
            characteristic class instantiation instead of this lookup method.

        Args:
            ctx: Context containing other characteristics.
            characteristic_name: Enum, string name, or characteristic class.

        Returns:
            Parsed characteristic value if found, ``None`` otherwise.

        """
        if not ctx or not ctx.other_characteristics:
            return None

        if isinstance(characteristic_name, type):
            configured_info: CharacteristicInfo | None = getattr(characteristic_name, "_configured_info", None)
            if configured_info is not None:
                char_uuid = configured_info.uuid
            else:
                class_name: str = characteristic_name.__name__
                name_without_suffix: str = class_name.replace("Characteristic", "")
                sig_name: str = re.sub(r"(?<!^)(?=[A-Z])", " ", name_without_suffix)
                resolved_uuid = self._get_characteristic_uuid_by_name(sig_name)
                if resolved_uuid is None:
                    return None
                char_uuid = resolved_uuid
        else:
            resolved_uuid = self._get_characteristic_uuid_by_name(characteristic_name)
            if resolved_uuid is None:
                return None
            char_uuid = resolved_uuid

        return ctx.other_characteristics.get(str(char_uuid))
