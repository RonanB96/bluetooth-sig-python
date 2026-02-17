"""Characteristic parsing with dependency-aware batch support.

Provides single and batch characteristic parsing, including topological
dependency ordering for multi-characteristic reads. Stateless.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from graphlib import TopologicalSorter
from typing import Any, TypeVar, overload

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.exceptions import (
    CharacteristicParseError,
    MissingDependencyError,
    SpecialValueDetectedError,
)
from ..types import CharacteristicContext
from ..types.uuid import BluetoothUUID

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CharacteristicParser:
    """Stateless parser for single and batch characteristic data.

    Handles parse_characteristic (with @overload support), parse_characteristics
    (batch with dependency ordering), and all private batch helpers.
    """

    @overload
    def parse_characteristic(
        self,
        char: type[BaseCharacteristic[T]],
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = ...,
    ) -> T: ...

    @overload
    def parse_characteristic(
        self,
        char: str,
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = ...,
    ) -> Any: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    def parse_characteristic(
        self,
        char: str | type[BaseCharacteristic[T]],
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = None,
    ) -> T | Any:  # Runtime UUID dispatch cannot be type-safe
        r"""Parse a characteristic's raw data using Bluetooth SIG standards.

        Args:
            char: Characteristic class (type-safe) or UUID string (not type-safe).
            raw_data: Raw bytes from the characteristic (bytes or bytearray)
            ctx: Optional CharacteristicContext providing device-level info

        Returns:
            Parsed value. Return type is inferred when passing characteristic class.

        Raises:
            SpecialValueDetectedError: Special sentinel value detected
            CharacteristicParseError: Parse/validation failure

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            logger.debug("Parsing characteristic class=%s, data_len=%d", char.__name__, len(raw_data))
            try:
                value = char_instance.parse_value(raw_data, ctx)
                logger.debug("Successfully parsed %s: %s", char_instance.name, value)
            except SpecialValueDetectedError as e:
                logger.debug("Special value detected for %s: %s", char_instance.name, e.special_value.meaning)
                raise
            except CharacteristicParseError as e:
                logger.warning("Parse failed for %s: %s", char_instance.name, e)
                raise
            else:
                return value

        # Handle string UUID input (not type-safe path)
        logger.debug("Parsing characteristic UUID=%s, data_len=%d", char, len(raw_data))

        characteristic = CharacteristicRegistry.get_characteristic(char)

        if characteristic:
            logger.debug("Found parser for UUID=%s: %s", char, type(characteristic).__name__)
            try:
                value = characteristic.parse_value(raw_data, ctx)
                logger.debug("Successfully parsed %s: %s", characteristic.name, value)
            except SpecialValueDetectedError as e:
                logger.debug("Special value detected for %s: %s", characteristic.name, e.special_value.meaning)
                raise
            except CharacteristicParseError as e:
                logger.warning("Parse failed for %s: %s", characteristic.name, e)
                raise
            else:
                return value
        else:
            logger.info("No parser available for UUID=%s", char)
            raise CharacteristicParseError(
                message=f"No parser available for characteristic UUID: {char}",
                name="Unknown",
                uuid=BluetoothUUID(char),
                raw_data=bytes(raw_data),
            )

    def parse_characteristics(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        r"""Parse multiple characteristics at once with dependency-aware ordering.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional CharacteristicContext used as the starting context

        Returns:
            Dictionary mapping UUIDs to parsed values

        Raises:
            ValueError: If circular dependencies are detected
            CharacteristicParseError: If parsing fails for any characteristic

        """
        return self._parse_characteristics_batch(char_data, ctx)

    def _parse_characteristics_batch(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None,
    ) -> dict[str, Any]:
        """Parse multiple characteristics using dependency-aware ordering."""
        logger.debug("Batch parsing %d characteristics", len(char_data))

        uuid_to_characteristic, uuid_to_required_deps, uuid_to_optional_deps = (
            self._prepare_characteristic_dependencies(char_data)
        )

        sorted_uuids = self._resolve_dependency_order(char_data, uuid_to_required_deps, uuid_to_optional_deps)

        base_context = ctx

        results: dict[str, Any] = {}
        for uuid_str in sorted_uuids:
            raw_data = char_data[uuid_str]
            characteristic = uuid_to_characteristic.get(uuid_str)

            missing_required = self._find_missing_required_dependencies(
                uuid_str,
                uuid_to_required_deps.get(uuid_str, []),
                results,
                base_context,
            )

            if missing_required:
                raise MissingDependencyError(characteristic.name if characteristic else "Unknown", missing_required)

            self._log_optional_dependency_gaps(
                uuid_str,
                uuid_to_optional_deps.get(uuid_str, []),
                results,
                base_context,
            )

            parse_context = self._build_parse_context(base_context, results)

            value = self.parse_characteristic(uuid_str, raw_data, ctx=parse_context)
            results[uuid_str] = value

        logger.debug("Batch parsing complete: %d results", len(results))
        return results

    def _prepare_characteristic_dependencies(
        self, characteristic_data: Mapping[str, bytes]
    ) -> tuple[dict[str, BaseCharacteristic[Any]], dict[str, list[str]], dict[str, list[str]]]:
        """Instantiate characteristics once and collect declared dependencies."""
        uuid_to_characteristic: dict[str, BaseCharacteristic[Any]] = {}
        uuid_to_required_deps: dict[str, list[str]] = {}
        uuid_to_optional_deps: dict[str, list[str]] = {}

        for uuid in characteristic_data:
            characteristic = CharacteristicRegistry.get_characteristic(uuid)
            if characteristic is None:
                continue

            uuid_to_characteristic[uuid] = characteristic

            required = characteristic.required_dependencies
            optional = characteristic.optional_dependencies

            if required:
                uuid_to_required_deps[uuid] = required
                logger.debug("Characteristic %s has required dependencies: %s", uuid, required)
            if optional:
                uuid_to_optional_deps[uuid] = optional
                logger.debug("Characteristic %s has optional dependencies: %s", uuid, optional)

        return uuid_to_characteristic, uuid_to_required_deps, uuid_to_optional_deps

    @staticmethod
    def _resolve_dependency_order(
        characteristic_data: Mapping[str, bytes],
        uuid_to_required_deps: Mapping[str, list[str]],
        uuid_to_optional_deps: Mapping[str, list[str]],
    ) -> list[str]:
        """Topologically sort characteristics based on declared dependencies."""
        try:
            sorter: TopologicalSorter[str] = TopologicalSorter()
            for uuid in characteristic_data:
                all_deps = uuid_to_required_deps.get(uuid, []) + uuid_to_optional_deps.get(uuid, [])
                batch_deps = [dep for dep in all_deps if dep in characteristic_data]
                sorter.add(uuid, *batch_deps)

            sorted_sequence = sorter.static_order()
            sorted_uuids = list(sorted_sequence)
            logger.debug("Dependency-sorted parsing order: %s", sorted_uuids)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Dependency sorting failed: %s. Using original order.", exc)
            return list(characteristic_data.keys())
        else:
            return sorted_uuids

    @staticmethod
    def _find_missing_required_dependencies(
        uuid: str,
        required_deps: list[str],
        results: Mapping[str, Any],
        base_context: CharacteristicContext | None,
    ) -> list[str]:
        """Determine which required dependencies are unavailable for a characteristic."""
        if not required_deps:
            return []

        missing: list[str] = []
        other_characteristics = (
            base_context.other_characteristics if base_context and base_context.other_characteristics else None
        )

        for dep_uuid in required_deps:
            if dep_uuid in results:
                continue

            if other_characteristics and dep_uuid in other_characteristics:
                continue

            missing.append(dep_uuid)

        if missing:
            logger.debug("Characteristic %s missing required dependencies: %s", uuid, missing)

        return missing

    @staticmethod
    def _log_optional_dependency_gaps(
        uuid: str,
        optional_deps: list[str],
        results: Mapping[str, Any],
        base_context: CharacteristicContext | None,
    ) -> None:
        """Emit debug logs when optional dependencies are unavailable."""
        if not optional_deps:
            return

        other_characteristics = (
            base_context.other_characteristics if base_context and base_context.other_characteristics else None
        )

        for dep_uuid in optional_deps:
            if dep_uuid in results:
                continue
            if other_characteristics and dep_uuid in other_characteristics:
                continue
            logger.debug("Optional dependency %s not available for %s", dep_uuid, uuid)

    @staticmethod
    def _build_parse_context(
        base_context: CharacteristicContext | None,
        results: Mapping[str, Any],
    ) -> CharacteristicContext:
        """Construct the context passed to per-characteristic parsers."""
        if base_context is not None:
            return CharacteristicContext(
                device_info=base_context.device_info,
                advertisement=base_context.advertisement,
                other_characteristics=results,
                raw_service=base_context.raw_service,
            )

        return CharacteristicContext(other_characteristics=results)
