"""Base registry class for Bluetooth SIG registries."""

from __future__ import annotations

import threading
from typing import Callable, Generic, TypeVar

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

    def _lazy_load(self, loaded_flag: bool, loader: Callable[[], None]) -> bool:
        """Thread-safe lazy loading helper using double-checked locking pattern.

        Args:
            loaded_flag: Boolean indicating if data is already loaded
            loader: Callable that performs the actual loading

        Returns:
            True if loading was performed, False if already loaded
        """
        if loaded_flag:
            return False

        with self._lock:
            # Double-check after acquiring lock for thread safety
            if loaded_flag:
                return False  # type: ignore[unreachable]  # Double-checked locking pattern

            loader()
            return True
