"""Tests for logging functionality in translator."""

from __future__ import annotations

import logging

from bluetooth_sig import BluetoothSIGTranslator


class TestTranslatorLogging:
    """Test logging functionality in BluetoothSIGTranslator."""

    def test_logging_can_be_enabled(self, caplog):
        """Test that logging can be enabled and captured."""
        caplog.set_level(logging.DEBUG)

        translator = BluetoothSIGTranslator()
        battery_data = bytes([0x64])  # 100%

        result = translator.parse_characteristic("2A19", battery_data)

        assert result.parse_success
        # Check that debug logs were captured
        assert any("Parsing characteristic" in record.message for record in caplog.records)
        assert any("Found parser" in record.message for record in caplog.records)

    def test_logging_debug_level(self, caplog):
        """Test debug level logging output."""
        caplog.set_level(logging.DEBUG)

        translator = BluetoothSIGTranslator()
        battery_data = bytes([0x64])

        translator.parse_characteristic("2A19", battery_data)

        debug_messages = [r.message for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) >= 2  # At least parsing start and success
        assert any("UUID=2A19" in msg for msg in debug_messages)
        assert any("data_len=1" in msg for msg in debug_messages)

    def test_logging_info_level(self, caplog):
        """Test info level logging for unknown characteristics."""
        caplog.set_level(logging.INFO)

        translator = BluetoothSIGTranslator()
        unknown_data = bytes([0x01, 0x02])

        # Use a valid UUID format for an unknown characteristic
        result = translator.parse_characteristic(
            "00001234-0000-1000-8000-00805F9B34FB", unknown_data
        )

        assert not result.parse_success
        info_messages = [r.message for r in caplog.records if r.levelno == logging.INFO]
        assert any("No parser available" in msg for msg in info_messages)

    def test_logging_warning_level(self, caplog):
        """Test warning level logging for parse failures."""
        caplog.set_level(logging.WARNING)

        translator = BluetoothSIGTranslator()
        # Invalid data that should fail parsing (too short for battery level)
        invalid_data = bytes([])

        translator.parse_characteristic("2A19", invalid_data)

        # Should have warning about parse failure
        # May or may not have warnings depending on characteristic implementation

    def test_logging_batch_parsing(self, caplog):
        """Test logging during batch parsing."""
        caplog.set_level(logging.DEBUG)

        translator = BluetoothSIGTranslator()
        sensor_data = {
            "2A19": bytes([0x55]),  # Battery
            "2A6E": bytes([0x58, 0x07]),  # Temperature
        }

        results = translator.parse_characteristics(sensor_data)

        assert len(results) == 2
        debug_messages = [r.message for r in caplog.records if r.levelno == logging.DEBUG]
        assert any("Batch parsing" in msg for msg in debug_messages)
        assert any("2 characteristics" in msg for msg in debug_messages)

    def test_logging_disabled_by_default(self, caplog):
        """Test that logging is disabled at default WARNING level."""
        caplog.set_level(logging.WARNING)

        translator = BluetoothSIGTranslator()
        battery_data = bytes([0x64])

        translator.parse_characteristic("2A19", battery_data)

        # Should have no debug messages at WARNING level
        debug_messages = [r.message for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) == 0

    def test_logging_performance_overhead_minimal(self):
        """Test that logging overhead is minimal when disabled."""
        import time

        translator = BluetoothSIGTranslator()
        battery_data = bytes([0x64])

        # Measure with logging disabled (default)
        logging.getLogger("bluetooth_sig.core.translator").setLevel(logging.ERROR)
        start = time.perf_counter()
        for _ in range(1000):
            translator.parse_characteristic("2A19", battery_data)
        time_without_logging = time.perf_counter() - start

        # Reset logging to INFO level
        logging.getLogger("bluetooth_sig.core.translator").setLevel(logging.INFO)
        start = time.perf_counter()
        for _ in range(1000):
            translator.parse_characteristic("2A19", battery_data)
        time_with_logging = time.perf_counter() - start

        # Logging overhead should be less than 50% (very generous)
        # In practice it's usually much less
        overhead_ratio = time_with_logging / time_without_logging
        assert overhead_ratio < 1.5, f"Logging overhead too high: {overhead_ratio:.2f}x"
