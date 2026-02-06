from datetime import datetime, timezone
from uuid import uuid4

from document_pipeline.events import DocumentFinalized, EventEnvelope
from document_pipeline.read_model import DocumentState, apply_event


def test_idempotent_by_event_id() -> None:
    event_id = uuid4()
    envelope = EventEnvelope(
        event_id=event_id,
        event_type="DocumentFinalized",
        event_version=1,
        occurred_at_utc=datetime.now(timezone.utc),
        correlation_id=uuid4(),
        causation_id=None,
        document_id=uuid4(),
        payload=DocumentFinalized(
            final_json_uri="s3://bucket/final.json",
            finalized_by="system",
            quality_gate="auto",
        ),
    )
    state = DocumentState(document_id=str(envelope.document_id))

    apply_event(state, envelope)
    apply_event(state, envelope)

    assert len(state.processed_event_ids) == 1
    assert state.finalized is True


def test_ignores_events_after_finalization() -> None:
    doc_id = uuid4()
    finalized = EventEnvelope(
        event_id=uuid4(),
        event_type="DocumentFinalized",
        event_version=1,
        occurred_at_utc=datetime.now(timezone.utc),
        correlation_id=uuid4(),
        causation_id=None,
        document_id=doc_id,
        payload=DocumentFinalized(
            final_json_uri="s3://bucket/final.json",
            finalized_by="system",
            quality_gate="auto",
        ),
    )
    later_event = EventEnvelope(
        event_id=uuid4(),
        event_type="ValidationCompleted",
        event_version=1,
        occurred_at_utc=datetime.now(timezone.utc),
        correlation_id=uuid4(),
        causation_id=None,
        document_id=doc_id,
        payload={"isValid": True},
    )

    state = DocumentState(document_id=str(doc_id))
    apply_event(state, finalized)
    apply_event(state, later_event)

    assert state.latest_stage == "DocumentFinalized"
    assert "ValidationCompleted" not in state.data
