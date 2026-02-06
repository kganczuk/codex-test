"""Core domain primitives for the document processing pipeline."""

from .events import (
    EventEnvelope,
    DocumentIngested,
    OcrCompleted,
    AiExtractionCompleted,
    ValidationCompleted,
    ManualCorrectionApplied,
    DocumentFinalized,
)
from .policy import NextStep, ProcessingPolicy, decide_next_step
from .read_model import DocumentState, apply_event

__all__ = [
    "EventEnvelope",
    "DocumentIngested",
    "OcrCompleted",
    "AiExtractionCompleted",
    "ValidationCompleted",
    "ManualCorrectionApplied",
    "DocumentFinalized",
    "NextStep",
    "ProcessingPolicy",
    "decide_next_step",
    "DocumentState",
    "apply_event",
]
