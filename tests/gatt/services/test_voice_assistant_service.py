"""Tests for Voice Assistant Service."""

from __future__ import annotations

import pytest

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
        assert len(service.get_expected_characteristics()) == 8

    def test_required_characteristics_include_control_point(self, service: VoiceAssistantService) -> None:
        required = service.get_required_characteristics()
        assert CharacteristicName.VOICE_ASSISTANT_SERVICE_CONTROL_POINT in required
