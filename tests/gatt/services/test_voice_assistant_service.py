"""Tests for Voice Assistant Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.gatt.services.voice_assistant import VoiceAssistantService  # type: ignore[import-untyped]
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestVoiceAssistantService(CommonServiceTests):
    @pytest.fixture
    def service(self) -> VoiceAssistantService:
        return VoiceAssistantService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "185E"

    def test_expected_characteristics_count(self, service: VoiceAssistantService) -> None:
        assert set(service.get_expected_characteristics()) == {
            CharacteristicName.VOICE_ASSISTANT_NAME,
            CharacteristicName.VOICE_ASSISTANT_UUID,
            CharacteristicName.VOICE_ASSISTANT_SERVICE_CONTROL_POINT,
            CharacteristicName.CONTENT_CONTROL_ID,
            CharacteristicName.VOICE_ASSISTANT_SESSION_STATE,
            CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES,
            CharacteristicName.INSTALLED_LOCATION,
            CharacteristicName.VOICE_ASSISTANT_SESSION_FLAG,
            CharacteristicName.VOICE_ASSISTANT_SUPPORTED_LANGUAGES,
        }

    def test_required_characteristics_match_spec(self, service: VoiceAssistantService) -> None:
        assert set(service.get_required_characteristics()) == {
            CharacteristicName.VOICE_ASSISTANT_NAME,
            CharacteristicName.VOICE_ASSISTANT_UUID,
            CharacteristicName.VOICE_ASSISTANT_SERVICE_CONTROL_POINT,
            CharacteristicName.CONTENT_CONTROL_ID,
            CharacteristicName.VOICE_ASSISTANT_SESSION_STATE,
            CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES,
        }

    def test_service_registration(self) -> None:
        assert GattServiceRegistry.get_service_class("185E") == VoiceAssistantService
