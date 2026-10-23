"""A phrase rule that does not apply to this schema version."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Unsupported:
    """Why a phrase or characteristic stops for this schema version."""

    rule: str
    detail: str
