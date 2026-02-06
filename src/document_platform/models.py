from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldCandidate:
    name: str
    value: str
    confidence: float


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    requires_manual_review: bool
    failed_rules: list[str]
    score: float
