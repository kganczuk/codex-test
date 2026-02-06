from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .events import AiExtractionCompleted, ValidationCompleted


class NextStep(str, Enum):
    RETRY_WITH_FALLBACK_MODEL = "retry_with_fallback_model"
    REQUEST_MANUAL_REVIEW = "request_manual_review"
    FINALIZE_AUTOMATICALLY = "finalize_automatically"


@dataclass(frozen=True)
class ProcessingPolicy:
    auto_finalize_threshold: float = 0.90
    retry_threshold: float = 0.70
    max_ai_attempts: int = 3
    hard_cost_cap_usd: float = 0.10


def decide_next_step(
    extraction: AiExtractionCompleted,
    validation: ValidationCompleted,
    policy: ProcessingPolicy | None = None,
) -> NextStep:
    policy = policy or ProcessingPolicy()

    if extraction.estimated_cost_usd > policy.hard_cost_cap_usd:
        return NextStep.REQUEST_MANUAL_REVIEW

    min_confidence = min((f.confidence for f in extraction.fields), default=0.0)

    if validation.requires_manual_review or not validation.is_valid:
        if extraction.attempt < policy.max_ai_attempts and min_confidence >= policy.retry_threshold:
            return NextStep.RETRY_WITH_FALLBACK_MODEL
        return NextStep.REQUEST_MANUAL_REVIEW

    if min_confidence >= policy.auto_finalize_threshold and validation.score >= policy.auto_finalize_threshold:
        return NextStep.FINALIZE_AUTOMATICALLY

    if extraction.attempt < policy.max_ai_attempts and min_confidence >= policy.retry_threshold:
        return NextStep.RETRY_WITH_FALLBACK_MODEL

    return NextStep.REQUEST_MANUAL_REVIEW
