"""Automation IO Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService


@dataclass
class AutomationIOService(BaseGattService):
    """Automation IO Service implementation.

    Contains characteristics related to electrical power monitoring and automation:
    - Electric Current - Optional
    - Voltage - Optional
    - Average Current - Optional
    - Average Voltage - Optional
    - Electric Current Range - Optional
    - Electric Current Specification - Optional
    - Electric Current Statistics - Optional
    - Voltage Specification - Optional
    - Voltage Statistics - Optional
    - High Voltage - Optional
    - Voltage Frequency - Optional
    - Supported Power Range - Optional
    - Tx Power Level - Optional
    """

    _service_name: str = "Automation IO"

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        # Will be populated as we implement each characteristic
        return {}

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {}  # All characteristics are optional for this service