"""Scan Interval Window characteristic data types."""

from __future__ import annotations

import msgspec


class ScanIntervalWindowData(msgspec.Struct, frozen=True, kw_only=True):
    """Scan Interval Window characteristic data.

    Contains scan interval and scan window parameters for BLE scanning.

    Attributes:
        scan_interval: Scan interval in units of 0.625ms (range: 0x0004-0x4000)
        scan_window: Scan window in units of 0.625ms (range: 0x0004-0x4000)
                     Must be less than or equal to scan_interval
    """

    # BLE scan parameter constants (in units of 0.625ms)
    SCAN_INTERVAL_MIN = 0x0004  # Minimum scan interval (2.5ms)
    SCAN_INTERVAL_MAX = 0x4000  # Maximum scan interval (10.24s)
    SCAN_WINDOW_MIN = 0x0004  # Minimum scan window (2.5ms)
    SCAN_WINDOW_MAX = 0x4000  # Maximum scan window (10.24s)

    # Time conversion constants
    UNITS_TO_MS_FACTOR = 0.625  # Convert from 0.625ms units to milliseconds
    HEX_FORMAT_WIDTH = 6  # Width for hex formatting (#06x)

    scan_interval: int
    scan_window: int

    def __post_init__(self) -> None:
        """Validate scan parameters after initialization."""
        # Validate ranges
        if not self.SCAN_INTERVAL_MIN <= self.scan_interval <= self.SCAN_INTERVAL_MAX:
            raise ValueError(
                f"Scan interval {self.scan_interval:#0{self.HEX_FORMAT_WIDTH}x} out of range "
                f"({self.SCAN_INTERVAL_MIN:#0{self.HEX_FORMAT_WIDTH}x}-{self.SCAN_INTERVAL_MAX:#0{self.HEX_FORMAT_WIDTH}x})"
            )
        if not self.SCAN_WINDOW_MIN <= self.scan_window <= self.SCAN_WINDOW_MAX:
            raise ValueError(
                f"Scan window {self.scan_window:#0{self.HEX_FORMAT_WIDTH}x} out of range "
                f"({self.SCAN_WINDOW_MIN:#0{self.HEX_FORMAT_WIDTH}x}-{self.SCAN_WINDOW_MAX:#0{self.HEX_FORMAT_WIDTH}x})"
            )
        if self.scan_window > self.scan_interval:
            raise ValueError(
                f"Scan window {self.scan_window:#0{self.HEX_FORMAT_WIDTH}x} must be <= scan interval "
                f"{self.scan_interval:#0{self.HEX_FORMAT_WIDTH}x}"
            )

    @property
    def scan_interval_ms(self) -> float:
        """Get scan interval in milliseconds."""
        return self.scan_interval * self.UNITS_TO_MS_FACTOR

    @property
    def scan_window_ms(self) -> float:
        """Get scan window in milliseconds."""
        return self.scan_window * self.UNITS_TO_MS_FACTOR
