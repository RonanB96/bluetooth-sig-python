"""Types for Bluetooth SIG GSS Characteristic registry."""

from __future__ import annotations

import re

import msgspec


class SpecialValue(msgspec.Struct, frozen=True):
    """A special sentinel value with its meaning.

    Used for values like 0x8000 meaning "value is not known".

    Attributes:
        raw_value: The raw integer sentinel value (e.g., 0x8000).
        meaning: Human-readable meaning (e.g., "value is not known").
    """

    raw_value: int
    meaning: str


class FieldSpec(msgspec.Struct, frozen=True, kw_only=True):
    """Specification for a field in a characteristic structure.

    Parses rich metadata from the description field including:
    - Unit ID (org.bluetooth.unit.*)
    - Resolution from M, d, b notation
    - Value range from "Allowed range is: X to Y"
    - Special values like "0x8000 represents 'value is not known'"
    - Presence conditions from "Present if bit N..."
    """

    field: str
    type: str
    size: str
    description: str

    @property
    def python_name(self) -> str:
        """Convert field name to Python snake_case identifier.

        Examples:
            "Instantaneous Speed" -> "instantaneous_speed"
            "Location - Latitude" -> "location_latitude"
        """
        name = self.field.lower()
        # Replace separators with underscores
        name = re.sub(r"[\s\-]+", "_", name)
        # Remove parentheses and their contents
        name = re.sub(r"\([^)]*\)", "", name)
        # Remove non-alphanumeric characters except underscores
        name = re.sub(r"[^\w]", "", name)
        # Collapse multiple underscores
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

    @property
    def is_optional(self) -> bool:
        """True if field size indicates optional presence (e.g., '0 or 2')."""
        return self.size.startswith("0 or") or self.size.lower() == "variable"

    @property
    def fixed_size(self) -> int | None:
        """Extract fixed byte size if determinable, None for variable/optional."""
        if self.is_optional:
            # For "0 or N", extract N as the size when present
            match = re.search(r"0 or (\d+)", self.size)
            if match:
                return int(match.group(1))
            return None
        # Try to parse as simple integer
        try:
            return int(self.size.strip('"'))
        except ValueError:
            return None

    @property
    def unit_id(self) -> str | None:
        """Extract org.bluetooth.unit.* identifier from description.

        Handles various formats:
        - "Base Unit:" or "Base unit:" (case-insensitive)
        - "Unit:" or "Unit;" (colon or semicolon)
        - Inline "or org.bluetooth.unit.*" patterns
        - Spaces after "org.bluetooth.unit." (YAML formatting issues)

        Returns:
            Unit ID string (e.g., "thermodynamic_temperature.degree_celsius"), or None.
        """
        # Remove spaces around dots to handle "org.bluetooth.unit. foo" -> "org.bluetooth.unit.foo"
        normalized = re.sub(r"org\.bluetooth\.unit\.\s*", "org.bluetooth.unit.", self.description)

        # Extract org.bluetooth.unit.* pattern
        match = re.search(r"org\.bluetooth\.unit\.([a-z0-9_.]+)", normalized, re.IGNORECASE)
        if match:
            return match.group(1).rstrip(".")

        return None

    @property
    def resolution(self) -> float | None:
        """Extract resolution from 'M = X, d = Y, b = Z' notation.

        The formula is: actual_value = raw_value * M * 10^d + b
        For most cases M=1 and b=0, so resolution = 10^d

        Handles variations:
        - "M = 1, d = -2, b = 0"
        - "M = 1, d = 3, and b = 0" (with "and")
        - "M = 1, d = - 7, b = 0" (space between sign and number)

        Returns:
            Resolution multiplier (e.g., 0.01 for d=-2), or None if not found.
        """
        # Pattern handles: spaces in numbers (d = - 7), "and" separator, comma separator
        match = re.search(
            r"M\s*=\s*([+-]?\s*\d+)\s*,\s*d\s*=\s*([+-]?\s*\d+)\s*(?:,\s*and\s*|,\s*|and\s+)b\s*=\s*([+-]?\s*\d+)",
            self.description,
            re.IGNORECASE,
        )
        if match:
            # Remove internal spaces from captured values
            m_val = int(match.group(1).replace(" ", ""))
            d_val = int(match.group(2).replace(" ", ""))
            # b_val = int(match.group(3).replace(" ", ""))  # Offset, not used
            return float(m_val * (10**d_val))
        return None

    @property
    def value_range(self) -> tuple[float, float] | None:
        """Extract value range from description.

        Looks for patterns like:
        - "Allowed range is: -273.15 to 327.67"
        - "Minimum: X" and "Maximum: Y"
        """
        # Pattern: "Allowed range is: X to Y"
        match = re.search(
            r"Allowed range[^:]*:\s*([+-]?\d+\.?\d*)\s*to\s*([+-]?\d+\.?\d*)",
            self.description,
            re.IGNORECASE,
        )
        if match:
            return float(match.group(1)), float(match.group(2))

        # Pattern: Minimum/Maximum on separate lines
        min_match = re.search(r"Minimum:\s*([+-]?\d+\.?\d*)", self.description)
        max_match = re.search(r"Maximum:\s*([+-]?\d+\.?\d*)", self.description)
        if min_match and max_match:
            min_val = min_match.group(1)
            max_val = max_match.group(1)
            # Only return if we captured actual numeric values
            if min_val and max_val:
                try:
                    return float(min_val), float(max_val)
                except ValueError:
                    pass

        return None

    @property
    def special_values(self) -> tuple[SpecialValue, ...]:
        """Extract special value meanings from description.

        Looks for patterns like:
        - 'A value of 0x8000 represents "value is not known"'
        - '0xFF represents "unknown user"'
        - 'The special value of 0xFF for User ID represents "unknown user"'
        - '0xFFFFFF represents: Unknown' (colon format)

        Returns:
            Tuple of SpecialValue structs (immutable, hashable).
        """
        result: list[SpecialValue] = []
        seen: set[int] = set()  # Avoid duplicates

        # Normalize Unicode curly quotes to ASCII for consistent matching
        desc = self.description
        desc = desc.replace("\u201c", '"').replace("\u201d", '"')  # " "
        desc = desc.replace("\u2018", "'").replace("\u2019", "'")  # ' '

        # Pattern 1: 0xXXXX ... represents "meaning" (flexible, captures hex before represents)
        pattern1 = r"(0x[0-9A-Fa-f]+)[^\n]*?represents\s*[\"']([^\"']+)[\"']"
        for match in re.finditer(pattern1, desc, re.MULTILINE | re.IGNORECASE):
            hex_val = int(match.group(1), 16)
            if hex_val not in seen:
                seen.add(hex_val)
                result.append(SpecialValue(raw_value=hex_val, meaning=match.group(2)))

        # Pattern 2: "0xXXXX represents: Meaning" (colon format, meaning is next word/phrase)
        pattern2 = r"(0x[0-9A-Fa-f]+)\s*represents:\s*([A-Za-z][A-Za-z\s]*)"
        for match in re.finditer(pattern2, desc, re.MULTILINE | re.IGNORECASE):
            hex_val = int(match.group(1), 16)
            if hex_val not in seen:
                seen.add(hex_val)
                meaning = match.group(2).strip()
                result.append(SpecialValue(raw_value=hex_val, meaning=meaning))

        return tuple(result)

    @property
    def presence_condition(self) -> str | None:
        """Extract presence condition from description.

        Looks for patterns like:
        - "Present if bit 0 of Flags field is set to 1"
        - "Present if bit 1 of Flags field is set to 0"
        """
        match = re.search(
            r"Present if bit (\d+) of (\w+) field is set to ([01])",
            self.description,
            re.IGNORECASE,
        )
        if match:
            bit_num = match.group(1)
            field_name = match.group(2)
            bit_value = match.group(3)
            return f"bit {bit_num} of {field_name} == {bit_value}"
        return None

    @property
    def presence_flag_bit(self) -> int | None:
        """Extract the flag bit number for optional field presence.

        Returns:
            Bit number (0-indexed) if field presence depends on a flag bit, None otherwise
        """
        match = re.search(
            r"Present if bit (\d+)",
            self.description,
            re.IGNORECASE,
        )
        if match:
            return int(match.group(1))
        return None


class GssCharacteristicSpec(msgspec.Struct, frozen=True, kw_only=True):
    """Specification for a Bluetooth SIG characteristic from GSS.

    Contains the full structure definition from GSS YAML files,
    enabling automatic metadata extraction for all fields.
    """

    identifier: str
    name: str
    description: str
    structure: list[FieldSpec] = msgspec.field(default_factory=list)

    def get_field(self, name: str) -> FieldSpec | None:
        """Get a field specification by name (case-insensitive).

        Args:
            name: Field name or python_name to look up

        Returns:
            FieldSpec if found, None otherwise
        """
        name_lower = name.lower()
        for field in self.structure:
            if field.field.lower() == name_lower or field.python_name == name_lower:
                return field
        return None

    @property
    def primary_field(self) -> FieldSpec | None:
        """Get the primary data field (first non-Flags field).

        For simple characteristics, this is the main value field.
        For complex characteristics, this may be the first data field.
        """
        for field in self.structure:
            if field.field.lower() != "flags" and not field.type.startswith("boolean["):
                return field
        return self.structure[0] if self.structure else None

    @property
    def has_multiple_units(self) -> bool:
        """True if structure contains fields with different units."""
        units: set[str] = set()
        for field in self.structure:
            if field.unit_id:
                units.add(field.unit_id)
        return len(units) > 1

    @property
    def field_count(self) -> int:
        """Return the number of fields in the structure."""
        return len(self.structure)
