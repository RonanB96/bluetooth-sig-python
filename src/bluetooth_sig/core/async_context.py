"""Async context manager for device parsing sessions."""

from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any, TypeVar, cast, overload

from ..gatt.characteristics.base import BaseCharacteristic
from ..types import CharacteristicContext
from ..types.uuid import BluetoothUUID
from .translator import BluetoothSIGTranslator

# Type variable for generic characteristic return types
T = TypeVar("T")


class AsyncParsingSession:
    """Async context manager for parsing sessions.

    Maintains parsing context across multiple async operations.

    Example::

        async with AsyncParsingSession() as session:
            result1 = await session.parse("2A19", data1)
            result2 = await session.parse("2A6E", data2)
            # Context automatically shared between parses
    """

    def __init__(
        self,
        translator: BluetoothSIGTranslator,
        ctx: CharacteristicContext | None = None,
    ) -> None:
        """Initialize parsing session.

        Args:
            translator: Translator instance to use for parsing
            ctx: Optional initial context
        """
        self.translator = translator
        self.context = ctx
        # Store parsed characteristic values for context sharing
        self.results: dict[str, Any] = {}

    async def __aenter__(self) -> AsyncParsingSession:
        """Enter async context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Exit async context."""
        # Cleanup if needed
        return False

    @overload
    async def parse(
        self,
        char: type[BaseCharacteristic[T]],
        data: bytes,
    ) -> T: ...

    @overload
    async def parse(
        self,
        char: str | BluetoothUUID,
        data: bytes,
    ) -> Any: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    async def parse(
        self,
        char: str | BluetoothUUID | type[BaseCharacteristic[T]],
        data: bytes,
    ) -> T | Any:  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        """Parse characteristic with accumulated context.

        Args:
            char: Characteristic class (type-safe) or UUID string/BluetoothUUID (not type-safe).
            data: Raw bytes

        Returns:
            Parsed characteristic value. Return type is inferred when passing characteristic class.
        """
        # Update context with previous results
        # Cast dict to Mapping to satisfy CharacteristicContext type requirements
        results_as_mapping = cast(Mapping[str, Any], self.results)

        if self.context is None:
            self.context = CharacteristicContext(other_characteristics=results_as_mapping)
        else:
            self.context = CharacteristicContext(
                device_info=self.context.device_info,
                advertisement=self.context.advertisement,
                other_characteristics=results_as_mapping,
                raw_service=self.context.raw_service,
            )

        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            result = await self.translator.parse_characteristic_async(char, data, self.context)
            # Store result using UUID string key
            char_instance = char()
            uuid_str = str(char_instance.uuid)
            self.results[uuid_str] = result
            return result

        # Parse with context (not type-safe path)
        uuid_str = str(char) if isinstance(char, BluetoothUUID) else char
        result = await self.translator.parse_characteristic_async(uuid_str, data, self.context)

        # Store result for future context using string UUID key
        self.results[uuid_str] = result

        return result
