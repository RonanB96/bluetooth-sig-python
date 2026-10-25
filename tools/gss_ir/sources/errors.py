"""Errors raised while reading SIG YAML."""

from __future__ import annotations


class GssSourceError(ValueError):
    """A SIG YAML input is not a document this reader can return."""

    def __init__(self, detail: str) -> None:
        """Initialise the error with a diagnostic detail."""
        super().__init__(detail)
        self.detail = detail
