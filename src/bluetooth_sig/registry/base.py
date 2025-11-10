"""Base registry class for Bluetooth SIG registries."""

from __future__ import annotations

import threading
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """Base class for Bluetooth SIG registries with singleton pattern and thread safety.

    Subclasses should:
    1. Call super().__init__() in their __init__ (base class sets self._loaded = False)
    2. Implement _load() to perform actual data loading (must set self._loaded = True when done)
    3. Call _ensure_loaded() before accessing data (provided by base class)
    """

    _instance: BaseRegistry[T] | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry."""
        self._lock = threading.RLock()
        self._loaded: bool = False  # Initialized in base class, accessed by subclasses

    @classmethod
    def get_instance(cls) -> BaseRegistry[T]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _lazy_load(self, loaded_check: Callable[[], bool], loader: Callable[[], None]) -> bool:
        """Thread-safe lazy loading helper using double-checked locking pattern.

        Args:
            loaded_check: Callable that returns True if data is already loaded
            loader: Callable that performs the actual loading

        Returns:
            True if loading was performed, False if already loaded
        """
        if loaded_check():
            return False

        with self._lock:
            # Double-check after acquiring lock for thread safety
            if loaded_check():
                return False

            loader()
            return True

    def _ensure_loaded(self) -> None:
        """Ensure the registry is loaded (thread-safe lazy loading).

        This is a standard implementation that subclasses can use.
        It calls _lazy_load with self._loaded check and self._load as the loader.
        Subclasses that need custom behavior can override this method.
        """
        self._lazy_load(lambda: self._loaded, self._load)

    def _load(self) -> None:
        """Perform the actual loading of registry data.

        Subclasses MUST implement this method to load their specific data.
        This method should set self._loaded = True when complete.
        """
        raise NotImplementedError("Subclasses must implement _load()")
