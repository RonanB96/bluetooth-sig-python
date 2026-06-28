"""Tests for Generic Voice Assistant Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services import GattServiceRegistry
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

    def test_required_characteristics_match_vas_table(self, service: GenericVoiceAssistantService) -> None:
        assert set(service.get_required_characteristics()) == {
            CharacteristicName.VOICE_ASSISTANT_NAME,
            CharacteristicName.VOICE_ASSISTANT_UUID,
            CharacteristicName.VOICE_ASSISTANT_SERVICE_CONTROL_POINT,
            CharacteristicName.CONTENT_CONTROL_ID,
            CharacteristicName.VOICE_ASSISTANT_SESSION_STATE,
            CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES,
        }

    def test_service_registration(self) -> None:
        assert GattServiceRegistry.get_service_class("185F") == GenericVoiceAssistantService
