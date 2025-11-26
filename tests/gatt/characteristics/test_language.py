"""Tests for Language characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LanguageCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLanguageCharacteristic(CommonCharacteristicTests):
    """Test suite for Language characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds language-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> LanguageCharacteristic:
        """Return a Language characteristic instance."""
        return LanguageCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Language characteristic."""
        return "2AA2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for language."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"en"), expected_value="en", description="English language code"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"fr"), expected_value="fr", description="French language code"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"es"), expected_value="es", description="Spanish language code"
            ),
        ]

    # === Language-Specific Tests ===

    @pytest.mark.parametrize(
        "language_code",
        [
            "en",
            "fr",
            "es",
            "de",
            "it",
            "pt",
            "zh",
            "ja",
            "ko",
        ],
    )
    def test_language_values(self, characteristic: LanguageCharacteristic, language_code: str) -> None:
        """Test language with various valid language codes."""
        data = bytearray(language_code.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == language_code

    def test_language_empty(self, characteristic: LanguageCharacteristic) -> None:
        """Test empty language."""
        result = characteristic.decode_value(bytearray())
        assert result == ""

    def test_language_long_code(self, characteristic: LanguageCharacteristic) -> None:
        """Test language with longer language tag."""
        language = "en-US"
        data = bytearray(language.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == language
