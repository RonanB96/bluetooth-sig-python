"""Parse trace utility for debugging characteristic parsing."""

from __future__ import annotations


class ParseTrace:
    """Manages parse traces with built-in enable/disable logic.

    This class encapsulates the trace collection logic to avoid manual
    if checks throughout the parsing code, improving performance when
    tracing is disabled.

    Example:
        trace = ParseTrace(enabled=True)
        trace.append("Starting parse")
        trace.append("Validation complete")
        result = trace.get_trace()  # Returns list of strings
    """

    def __init__(self, enabled: bool = True):
        """Initialize parse trace collector.

        Args:
            enabled: Whether to collect trace messages (default: True)
        """
        self._enabled = enabled
        self._trace: list[str] = []

    def append(self, message: str) -> None:
        """Append a message to the trace if tracing is enabled.

        Args:
            message: Trace message to append
        """
        if self._enabled:
            self._trace.append(message)

    def get_trace(self) -> list[str]:
        """Get the collected trace messages.

        Returns:
            List of trace messages if enabled, empty list otherwise
        """
        return self._trace if self._enabled else []

    @property
    def enabled(self) -> bool:
        """Check if tracing is enabled.

        Returns:
            True if tracing is enabled, False otherwise
        """
        return self._enabled
