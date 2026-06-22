"""Tests for Generic Voice Assistant Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.generic_voice_assistant import (  # type: ignore[import-untyped]
    GenericVoiceAssistantService,
)
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestGenericVoiceAssistantService(CommonServiceTests):
    @pytest.fixture
    def service(self) -> GenericVoiceAssistantService:
        return GenericVoiceAssistantService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "185F"

    def test_expected_characteristics_count(self, service: GenericVoiceAssistantService) -> None:
        assert len(service.get_expected_characteristics()) == 9

    def test_required_characteristics_match_vas_table(self, service: GenericVoiceAssistantService) -> None:
        required = service.get_required_characteristics()
        assert CharacteristicName.VOICE_ASSISTANT_NAME in required
        assert CharacteristicName.CONTENT_CONTROL_ID in required
        assert CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES in required
        assert CharacteristicName.VOICE_ASSISTANT_SUPPORTED_LANGUAGES not in required
