"""Minimal tests for data parsing to ensure file parses correctly."""

from typing import Any

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator


@pytest.fixture
def empty_services() -> dict[str, Any]:
    """Provide an empty services mapping for basic parser sanity checks."""
    return {}


def test_translator_handles_empty_services(empty_services: dict[str, Any]) -> None:
    """Translator should accept an empty services dict without crashing."""
    translator = BluetoothSIGTranslator()
    translator.clear_services()
    translator.process_services(empty_services)
    # No services discovered when input is empty
    assert isinstance(translator.discovered_services, list)
    assert len(translator.discovered_services) == 0
