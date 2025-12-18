"""Tests for DictKeyProvider - additional functional tests.

Tests missing coverage paths in encryption.py including:
- get_key() logging/warning paths
- set_key() warning clear
- remove_key() operations
"""

from __future__ import annotations

import logging

import pytest

from bluetooth_sig.advertising.encryption import DictKeyProvider
from bluetooth_sig.types.ead import EADKeyMaterial


class TestDictKeyProviderGetKeyLogging:
    """Tests for DictKeyProvider.get_key() logging behaviour."""

    def test_get_key_logs_warning_once(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that missing key warning is logged only once per MAC."""
        provider = DictKeyProvider()

        with caplog.at_level(logging.DEBUG):
            # First call should log
            result1 = provider.get_key("AA:BB:CC:DD:EE:FF")
            # Second call should not log again
            result2 = provider.get_key("AA:BB:CC:DD:EE:FF")

        assert result1 is None
        assert result2 is None
        # Should only have one debug message for this MAC (masked: **:**:**:**:EE:FF)
        debug_messages = [r.message for r in caplog.records if "EE:FF" in r.message]
        assert len(debug_messages) == 1

    def test_get_key_logs_for_each_different_mac(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that warning is logged for each unique missing MAC."""
        provider = DictKeyProvider()

        with caplog.at_level(logging.DEBUG):
            provider.get_key("AA:BB:CC:DD:EE:FF")
            provider.get_key("11:22:33:44:55:66")

        # Should have warnings for both MACs (masked: last 5 chars visible)
        messages = [r.message for r in caplog.records]
        assert any("EE:FF" in m for m in messages)
        assert any("55:66" in m for m in messages)


class TestDictKeyProviderSetKey:
    """Tests for DictKeyProvider.set_key() method."""

    def test_set_key_basic(self) -> None:
        """Test setting a key for a device."""
        provider = DictKeyProvider()
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")

        provider.set_key("AA:BB:CC:DD:EE:FF", key)

        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key

    def test_set_key_normalizes_mac(self) -> None:
        """Test that set_key normalizes MAC to uppercase."""
        provider = DictKeyProvider()
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")

        provider.set_key("aa:bb:cc:dd:ee:ff", key)

        # Should be accessible with uppercase
        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key

    def test_set_key_clears_warning_status(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that setting a key clears the warning status for that MAC."""
        provider = DictKeyProvider()
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")

        with caplog.at_level(logging.DEBUG):
            # First get triggers warning
            provider.get_key("AA:BB:CC:DD:EE:FF")

        caplog.clear()

        # Set a key
        provider.set_key("AA:BB:CC:DD:EE:FF", key)
        # Remove it
        provider.remove_key("AA:BB:CC:DD:EE:FF")

        with caplog.at_level(logging.DEBUG):
            # Get again should trigger warning again (status was cleared by set)
            provider.get_key("AA:BB:CC:DD:EE:FF")

        # Should have a new warning (masked: **:**:**:**:EE:FF)
        messages = [r.message for r in caplog.records]
        assert any("EE:FF" in m for m in messages)

    def test_set_key_overwrites_existing(self) -> None:
        """Test that set_key overwrites existing key."""
        provider = DictKeyProvider()
        key1 = bytes.fromhex("0123456789abcdef0123456789abcdef")
        key2 = bytes.fromhex("fedcba9876543210fedcba9876543210")

        provider.set_key("AA:BB:CC:DD:EE:FF", key1)
        provider.set_key("AA:BB:CC:DD:EE:FF", key2)

        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key2


class TestDictKeyProviderRemoveKey:
    """Tests for DictKeyProvider.remove_key() method."""

    def test_remove_key_basic(self) -> None:
        """Test removing an existing key."""
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider = DictKeyProvider(keys={"AA:BB:CC:DD:EE:FF": key})

        provider.remove_key("AA:BB:CC:DD:EE:FF")

        assert provider.get_key("AA:BB:CC:DD:EE:FF") is None

    def test_remove_key_nonexistent(self) -> None:
        """Test removing a key that doesn't exist doesn't raise."""
        provider = DictKeyProvider()

        # Should not raise
        provider.remove_key("AA:BB:CC:DD:EE:FF")

    def test_remove_key_normalizes_mac(self) -> None:
        """Test that remove_key normalizes MAC to uppercase."""
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider = DictKeyProvider(keys={"AA:BB:CC:DD:EE:FF": key})

        provider.remove_key("aa:bb:cc:dd:ee:ff")

        assert provider.get_key("AA:BB:CC:DD:EE:FF") is None


class TestDictKeyProviderGetEadKeyLogging:
    """Tests for DictKeyProvider.get_ead_key() logging behaviour."""

    def test_get_ead_key_logs_warning_once(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that missing EAD key warning is logged only once per MAC."""
        provider = DictKeyProvider()

        with caplog.at_level(logging.DEBUG):
            result1 = provider.get_ead_key("AA:BB:CC:DD:EE:FF")
            result2 = provider.get_ead_key("AA:BB:CC:DD:EE:FF")

        assert result1 is None
        assert result2 is None
        # Should only have one debug message for this MAC (masked: **:**:**:**:EE:FF)
        debug_messages = [r.message for r in caplog.records if "EE:FF" in r.message]
        assert len(debug_messages) == 1


class TestDictKeyProviderSetEadKey:
    """Tests for DictKeyProvider.set_ead_key() method."""

    def test_set_ead_key_basic(self) -> None:
        """Test setting an EAD key for a device."""
        provider = DictKeyProvider()
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        provider.set_ead_key("AA:BB:CC:DD:EE:FF", key_material)

        result = provider.get_ead_key("AA:BB:CC:DD:EE:FF")
        assert result is not None
        assert result.session_key == session_key

    def test_set_ead_key_clears_warning_status(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that setting an EAD key clears the warning status."""
        provider = DictKeyProvider()
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        with caplog.at_level(logging.DEBUG):
            provider.get_ead_key("AA:BB:CC:DD:EE:FF")  # Triggers warning

        caplog.clear()

        provider.set_ead_key("AA:BB:CC:DD:EE:FF", key_material)
        provider.remove_ead_key("AA:BB:CC:DD:EE:FF")

        with caplog.at_level(logging.DEBUG):
            provider.get_ead_key("AA:BB:CC:DD:EE:FF")  # Should trigger warning again

        # Should have a new warning (masked: **:**:**:**:EE:FF)
        messages = [r.message for r in caplog.records]
        assert any("EE:FF" in m for m in messages)


class TestDictKeyProviderRemoveEadKey:
    """Tests for DictKeyProvider.remove_ead_key() method."""

    def test_remove_ead_key_basic(self) -> None:
        """Test removing an existing EAD key."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)
        provider = DictKeyProvider(ead_keys={"AA:BB:CC:DD:EE:FF": key_material})

        provider.remove_ead_key("AA:BB:CC:DD:EE:FF")

        assert provider.get_ead_key("AA:BB:CC:DD:EE:FF") is None

    def test_remove_ead_key_nonexistent(self) -> None:
        """Test removing an EAD key that doesn't exist doesn't raise."""
        provider = DictKeyProvider()

        # Should not raise
        provider.remove_ead_key("AA:BB:CC:DD:EE:FF")


class TestDictKeyProviderMixedKeys:
    """Tests for DictKeyProvider with mixed key types."""

    def test_legacy_and_ead_keys_independent(self) -> None:
        """Test that legacy and EAD keys are stored independently."""
        legacy_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        session_key = bytes.fromhex("fedcba9876543210fedcba9876543210")
        iv = bytes.fromhex("0102030405060708")
        ead_key = EADKeyMaterial(session_key=session_key, iv=iv)

        provider = DictKeyProvider()
        provider.set_key("AA:BB:CC:DD:EE:FF", legacy_key)
        provider.set_ead_key("AA:BB:CC:DD:EE:FF", ead_key)

        # Both should be present
        assert provider.get_key("AA:BB:CC:DD:EE:FF") == legacy_key
        result = provider.get_ead_key("AA:BB:CC:DD:EE:FF")
        assert result is not None
        assert result.session_key == session_key

        # Removing one shouldn't affect the other
        provider.remove_key("AA:BB:CC:DD:EE:FF")
        assert provider.get_key("AA:BB:CC:DD:EE:FF") is None
        assert provider.get_ead_key("AA:BB:CC:DD:EE:FF") is not None

    def test_shared_warning_tracking(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that warning tracking is shared between key types."""
        provider = DictKeyProvider()

        with caplog.at_level(logging.DEBUG):
            # First call for legacy key triggers warning
            provider.get_key("AA:BB:CC:DD:EE:FF")

        caplog.clear()

        with caplog.at_level(logging.DEBUG):
            # EAD key for same MAC should NOT trigger warning (already warned)
            provider.get_ead_key("AA:BB:CC:DD:EE:FF")

        # No new warnings should be logged for this MAC
        messages = [r.message for r in caplog.records if "AA:BB:CC:DD:EE:FF" in r.message]
        assert len(messages) == 0
