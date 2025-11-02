"""Async context manager for device parsing sessions."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, cast

from ..types import CharacteristicContext
from .async_translator import AsyncBluetoothSIGTranslator

if TYPE_CHECKING:
    from ..types import CharacteristicData, CharacteristicDataProtocol


class AsyncParsingSession:
    """Async context manager for parsing sessions.

    Maintains parsing context across multiple async operations.

    Example:
        ```python
        async with AsyncParsingSession() as session:
            result1 = await session.parse("2A19", data1)
            result2 = await session.parse("2A6E", data2)
            # Context automatically shared between parses
        ```
    """

    def __init__(
        self,
        translator: AsyncBluetoothSIGTranslator,
        ctx: CharacteristicContext | None = None,
    ) -> None:
        """Initialize parsing session.

        Args:
            translator: Translator instance to use for parsing
            ctx: Optional initial context
        """
        self.translator = translator
        self.context = ctx
        self.results: dict[str, CharacteristicData] = {}

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

    async def parse(
        self,
        uuid: str,
        data: bytes,
        descriptor_data: dict[str, bytes] | None = None,
    ) -> CharacteristicData:
        """Parse characteristic with accumulated context.

        Args:
            uuid: Characteristic UUID
            data: Raw bytes
            descriptor_data: Optional descriptor data

        Returns:
            CharacteristicData
        """
        # Update context with previous results
        results_mapping = cast("dict[str, CharacteristicDataProtocol]", self.results)

        if self.context is None:
            self.context = CharacteristicContext(other_characteristics=results_mapping)
        else:
            self.context = CharacteristicContext(
                device_info=self.context.device_info,
                advertisement=self.context.advertisement,
                other_characteristics=results_mapping,
                raw_service=self.context.raw_service,
            )

        # Parse with context
        result = await self.translator.parse_characteristic_async(uuid, data, self.context, descriptor_data)

        # Store result for future context
        self.results[uuid] = result

        return result
