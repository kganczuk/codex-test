from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from uuid import UUID

PayloadT = TypeVar("PayloadT")


@dataclass(frozen=True)
class EventEnvelope(Generic[PayloadT]):
    event_id: UUID
    event_type: str
    event_version: int
    occurred_at_utc: datetime
    correlation_id: UUID
    causation_id: Optional[UUID]
    document_id: UUID
    payload: PayloadT

    def __post_init__(self) -> None:
        if self.event_version < 1:
            raise ValueError("event_version must be >= 1")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")
        if self.occurred_at_utc.tzinfo != timezone.utc:
            raise ValueError("occurred_at_utc must be in UTC")


@dataclass(frozen=True)
class DocumentIngested:
    source: str
    file_name: str
    mime_type: str
    storage_uri: str
    uploaded_by: str


@dataclass(frozen=True)
class OcrCompleted:
    ocr_provider: str
    language: str
    pages: int
    text_uri: str
    avg_confidence: float

    def __post_init__(self) -> None:
        if self.pages < 1:
            raise ValueError("pages must be >= 1")
        _validate_confidence(self.avg_confidence, "avg_confidence")


@dataclass(frozen=True)
class ExtractedField:
    name: str
    value: str
    confidence: float

    def __post_init__(self) -> None:
        _validate_confidence(self.confidence, f"field:{self.name}")


@dataclass(frozen=True)
class AiExtractionCompleted:
    provider: str
    model: str
    attempt: int
    raw_output_uri: str
    fields: list[ExtractedField]
    estimated_cost_usd: float

    def __post_init__(self) -> None:
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1")
        if self.estimated_cost_usd < 0:
            raise ValueError("estimated_cost_usd must be >= 0")


@dataclass(frozen=True)
class ValidationCompleted:
    is_valid: bool
    failed_rules: list[str]
    score: float
    requires_manual_review: bool

    def __post_init__(self) -> None:
        _validate_confidence(self.score, "score")


@dataclass(frozen=True)
class CorrectedField:
    name: str
    old_value: str
    new_value: str
    reason: str


@dataclass(frozen=True)
class ManualCorrectionApplied:
    reviewer: str
    corrected_fields: list[CorrectedField]
    comment: str


@dataclass(frozen=True)
class DocumentFinalized:
    final_json_uri: str
    finalized_by: str
    quality_gate: str


def _validate_confidence(value: float, field_name: str) -> None:
    if value < 0 or value > 1:
        raise ValueError(f"{field_name} must be between 0 and 1")
