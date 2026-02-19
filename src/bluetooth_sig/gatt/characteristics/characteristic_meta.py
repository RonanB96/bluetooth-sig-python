"""Helper classes for GATT characteristic infrastructure.

Contains the SIG resolver, validation configuration, and metaclass used by
:class:`BaseCharacteristic`.  Extracted to keep the base module focused on
the characteristic API itself.
"""

from __future__ import annotations

from abc import ABCMeta
from typing import Any

import msgspec

from ...registry.uuids.units import units_registry
from ...types import CharacteristicInfo
from ...types.gatt_enums import DataType
from ...types.registry import CharacteristicSpec
from ..exceptions import UUIDResolutionError
from ..resolver import CharacteristicRegistrySearch, NameNormalizer, NameVariantGenerator
from ..uuid_registry import uuid_registry

# ---------------------------------------------------------------------------
# Validation configuration
# ---------------------------------------------------------------------------


class ValidationConfig(msgspec.Struct, kw_only=True):
    """Configuration for characteristic validation constraints.

    Groups validation parameters into a single, optional configuration object
    to simplify BaseCharacteristic constructor signatures.
    """

    min_value: int | float | None = None
    max_value: int | float | None = None
    expected_length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    allow_variable_length: bool = False
    expected_type: type | None = None


# ---------------------------------------------------------------------------
# SIG characteristic resolver
# ---------------------------------------------------------------------------


class SIGCharacteristicResolver:
    """Resolves SIG characteristic information from YAML and registry.

    This class handles all SIG characteristic resolution logic, separating
    concerns from the BaseCharacteristic constructor.  Uses shared utilities
    from the resolver module to avoid code duplication.
    """

    camel_case_to_display_name = staticmethod(NameNormalizer.camel_case_to_display_name)

    @staticmethod
    def resolve_for_class(char_class: type) -> CharacteristicInfo:
        """Resolve CharacteristicInfo for a SIG characteristic class.

        Args:
            char_class: The characteristic class to resolve info for.

        Returns:
            CharacteristicInfo with resolved UUID, name, value_type, unit.

        Raises:
            UUIDResolutionError: If no UUID can be resolved for the class.

        """
        yaml_spec = SIGCharacteristicResolver.resolve_yaml_spec_for_class(char_class)
        if yaml_spec:
            return SIGCharacteristicResolver._create_info_from_yaml(yaml_spec, char_class)

        registry_info = SIGCharacteristicResolver.resolve_from_registry(char_class)
        if registry_info:
            return registry_info

        raise UUIDResolutionError(char_class.__name__, [char_class.__name__])

    @staticmethod
    def resolve_yaml_spec_for_class(char_class: type) -> CharacteristicSpec | None:
        """Resolve YAML spec for a characteristic class using shared name variant logic."""
        characteristic_name = getattr(char_class, "_characteristic_name", None)
        names_to_try = NameVariantGenerator.generate_characteristic_variants(char_class.__name__, characteristic_name)

        for try_name in names_to_try:
            spec = uuid_registry.resolve_characteristic_spec(try_name)
            if spec:
                return spec

        return None

    @staticmethod
    def _create_info_from_yaml(yaml_spec: CharacteristicSpec, char_class: type) -> CharacteristicInfo:
        """Create CharacteristicInfo from YAML spec, resolving metadata via registry classes."""
        value_type = DataType.from_string(yaml_spec.data_type).to_value_type()

        unit_info = None
        unit_name = getattr(yaml_spec, "unit_symbol", None) or getattr(yaml_spec, "unit", None)
        if unit_name:
            unit_info = units_registry.get_unit_info_by_name(unit_name)
        if unit_info:
            unit_symbol = str(getattr(unit_info, "symbol", getattr(unit_info, "name", unit_name)))
        else:
            unit_symbol = str(unit_name or "")

        return CharacteristicInfo(
            uuid=yaml_spec.uuid,
            name=yaml_spec.name or char_class.__name__,
            unit=unit_symbol,
            value_type=value_type,
        )

    @staticmethod
    def resolve_from_registry(char_class: type) -> CharacteristicInfo | None:
        """Fallback to registry resolution using shared search strategy."""
        search_strategy = CharacteristicRegistrySearch()
        characteristic_name = getattr(char_class, "_characteristic_name", None)
        return search_strategy.search(char_class, characteristic_name)


# ---------------------------------------------------------------------------
# Metaclass
# ---------------------------------------------------------------------------


class CharacteristicMeta(ABCMeta):
    """Metaclass to automatically handle template flags for characteristics."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401  # Metaclass receives arbitrary keyword arguments
    ) -> type:
        """Create the characteristic class and handle template markers.

        This metaclass hook ensures template classes and concrete
        implementations are correctly annotated with the ``_is_template``
        attribute before the class object is created.
        """
        if bases:
            module_name = namespace.get("__module__", "")
            is_in_templates = "templates" in module_name

            if not is_in_templates and not namespace.get("_is_template_override", False):
                has_template_parent = any(getattr(base, "_is_template", False) for base in bases)
                if has_template_parent and "_is_template" not in namespace:
                    namespace["_is_template"] = False

        return super().__new__(mcs, name, bases, namespace, **kwargs)
