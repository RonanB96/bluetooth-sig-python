"""Resolver for merged special-value rules with runtime overrides.

This module provides SpecialValueResolver that centralises special-value
lookups with a priority: user overrides > class rules > spec rules.

It reuses the data types defined in `bluetooth_sig.types.special_values`.
"""

from __future__ import annotations

from bluetooth_sig.types.special_values import SpecialValueResult, SpecialValueRule

from ..types.units import SpecialValueType


class SpecialValueResolver:
    """Resolve raw integers to SpecialValueResult and provide reverse lookups.

    Behavior:
    - The resolver stores three sources:
      - spec_rules (lowest priority)
      - class_rules
      - user_overrides (highest priority)
    - Users may add rules at runtime or disable a raw value (by setting a
      sentinel None in user_overrides).
    """

    def __init__(
        self,
        spec_rules: dict[int, SpecialValueRule] | None = None,
        class_rules: dict[int, SpecialValueRule] | None = None,
    ) -> None:
        """Initialize resolver with spec and class-level rules.

        Args:
            spec_rules: Rules from Bluetooth SIG specifications (lowest priority)
            class_rules: Rules from class-level _special_values (medium priority)
        """
        self._spec_rules: dict[int, SpecialValueRule] = spec_rules or {}
        self._class_rules: dict[int, SpecialValueRule] = class_rules or {}
        # _user_overrides maps raw_value -> SpecialValueRule | None (None = disabled)
        self._user_overrides: dict[int, SpecialValueRule | None] = {}

    # ------------------------ runtime mutation API -------------------------
    def set_user_override(self, raw_value: int, rule: SpecialValueRule) -> None:
        """Set or replace a user override for a raw value."""
        self._user_overrides[raw_value] = rule

    def add_special_value(self, rule: SpecialValueRule) -> None:
        """Convenience to add a user-defined special rule."""
        self._user_overrides[rule.raw_value] = rule

    def clear_user_override(self, raw_value: int) -> None:
        """Clear any user override (fall back to class/spec)."""
        self._user_overrides.pop(raw_value, None)

    def disable_special_value(self, raw_value: int) -> None:
        """Disable special-value handling for a raw value (treat as normal data)."""
        self._user_overrides[raw_value] = None

    # -------------------------- resolution API ----------------------------
    def resolve(self, raw_value: int) -> SpecialValueResult | None:
        """Return SpecialValueResult if raw_value is special, otherwise None."""
        # Resolution priority: user_overrides > class_rules > spec_rules
        if raw_value in self._user_overrides:
            rule = self._user_overrides[raw_value]
            if rule is None:  # explicit disable
                return None
            return rule.to_result()

        if raw_value in self._class_rules:
            return self._class_rules[raw_value].to_result()

        if raw_value in self._spec_rules:
            return self._spec_rules[raw_value].to_result()

        return None

    # ----------------------- reverse lookup helpers -----------------------
    def get_raw_for_type(self, value_type: SpecialValueType) -> int | None:
        """Return the first raw value matching the given SpecialValueType.

        Search priority: user > class > spec.
        """
        for rules in (self._user_overrides, self._class_rules, self._spec_rules):
            for raw, rule in rules.items():
                if rule is not None and rule.value_type == value_type:
                    return raw
        return None

    def get_raw_for_meaning(self, meaning: str) -> int | None:
        """Return first raw value where meaning contains the given string (ci, partial)."""
        m = meaning.lower()
        for rules in (self._user_overrides, self._class_rules, self._spec_rules):
            for raw, rule in rules.items():
                if rule is None:
                    continue
                if m in rule.meaning.lower():
                    return raw
        return None

    # --------------------------- introspection ---------------------------
    def list_all_rules(self) -> dict[int, tuple[SpecialValueRule, str]]:
        """Return merged rules with source tag ('user','class','spec').

        User overrides (including disables) take precedence and may remove
        a rule by setting it to None.
        """
        result: dict[int, tuple[SpecialValueRule, str]] = {}
        # Add spec (lowest priority)
        for raw, rule in self._spec_rules.items():
            result[raw] = (rule, "spec")
        # Override with class rules
        for raw, rule in self._class_rules.items():
            result[raw] = (rule, "class")
        # Apply user overrides
        for raw, rule in self._user_overrides.items():
            if rule is None:
                result.pop(raw, None)
            else:
                result[raw] = (rule, "user")
        return result

    def is_special(self, raw_value: int) -> bool:
        """Quick boolean check whether raw_value resolves to a special rule."""
        return self.resolve(raw_value) is not None
