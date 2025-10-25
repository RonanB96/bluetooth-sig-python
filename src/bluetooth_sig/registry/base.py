"""Base registry class for Bluetooth SIG registries."""

from __future__ import annotations

import threading
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """Base class for Bluetooth SIG registries with singleton pattern and thread safety."""

    _instance: BaseRegistry[T] | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry."""
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> BaseRegistry[T]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
