from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class EventEnvelope:
    event_type: str
    document_id: str
    payload: dict[str, Any]
    correlation_id: str
    causation_id: str | None = None
    event_version: int = 1
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at_utc: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )


class EventTypes:
    DOCUMENT_INGESTED = "DocumentIngested"
    OCR_COMPLETED = "OcrCompleted"
    AI_EXTRACTION_COMPLETED = "AiExtractionCompleted"
    VALIDATION_COMPLETED = "ValidationCompleted"
    MANUAL_REVIEW_REQUESTED = "ManualReviewRequested"
    MANUAL_CORRECTION_APPLIED = "ManualCorrectionApplied"
    DOCUMENT_FINALIZED = "DocumentFinalized"
