from __future__ import annotations

from uuid import uuid4

from .event_store import InMemoryEventStore
from .events import EventEnvelope, EventTypes
from .models import FieldCandidate
from .validation import ValidationEngine


class DocumentPipelineService:
    def __init__(self, event_store: InMemoryEventStore, validation: ValidationEngine):
        self.event_store = event_store
        self.validation = validation

    def ingest(self, document_id: str, file_name: str, uploaded_by: str) -> str:
        correlation_id = str(uuid4())
        event = EventEnvelope(
            event_type=EventTypes.DOCUMENT_INGESTED,
            document_id=document_id,
            correlation_id=correlation_id,
            payload={
                "source": "api",
                "fileName": file_name,
                "uploadedBy": uploaded_by,
            },
        )
        self.event_store.append(event)
        return correlation_id

    def process_extraction(
        self,
        document_id: str,
        correlation_id: str,
        provider: str,
        model: str,
        fields: list[FieldCandidate],
        attempt: int,
    ) -> None:
        ai_event = EventEnvelope(
            event_type=EventTypes.AI_EXTRACTION_COMPLETED,
            document_id=document_id,
            correlation_id=correlation_id,
            payload={
                "provider": provider,
                "model": model,
                "attempt": attempt,
                "fields": [f.__dict__ for f in fields],
            },
        )
        self.event_store.append(ai_event)

        validation_result = self.validation.validate(fields)
        validation_event = EventEnvelope(
            event_type=EventTypes.VALIDATION_COMPLETED,
            document_id=document_id,
            correlation_id=correlation_id,
            causation_id=ai_event.event_id,
            payload={
                "isValid": validation_result.is_valid,
                "requiresManualReview": validation_result.requires_manual_review,
                "failedRules": validation_result.failed_rules,
                "score": validation_result.score,
            },
        )
        self.event_store.append(validation_event)

        if validation_result.requires_manual_review:
            self.event_store.append(
                EventEnvelope(
                    event_type=EventTypes.MANUAL_REVIEW_REQUESTED,
                    document_id=document_id,
                    correlation_id=correlation_id,
                    causation_id=validation_event.event_id,
                    payload={"reason": "validation_or_confidence_policy"},
                )
            )
            return

        self.event_store.append(
            EventEnvelope(
                event_type=EventTypes.DOCUMENT_FINALIZED,
                document_id=document_id,
                correlation_id=correlation_id,
                causation_id=validation_event.event_id,
                payload={
                    "finalizedBy": "system",
                    "qualityGate": "auto",
                },
            )
        )

    def apply_manual_correction(
        self,
        document_id: str,
        correlation_id: str,
        reviewer: str,
        corrected_fields: list[dict[str, str]],
        comment: str,
    ) -> None:
        correction_event = EventEnvelope(
            event_type=EventTypes.MANUAL_CORRECTION_APPLIED,
            document_id=document_id,
            correlation_id=correlation_id,
            payload={
                "reviewer": reviewer,
                "correctedFields": corrected_fields,
                "comment": comment,
            },
        )
        self.event_store.append(correction_event)

        self.event_store.append(
            EventEnvelope(
                event_type=EventTypes.DOCUMENT_FINALIZED,
                document_id=document_id,
                correlation_id=correlation_id,
                causation_id=correction_event.event_id,
                payload={
                    "finalizedBy": reviewer,
                    "qualityGate": "manual",
                },
            )
        )
