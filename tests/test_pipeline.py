from document_platform import (
    DocumentPipelineService,
    EventTypes,
    FieldCandidate,
    InMemoryEventStore,
    ValidationEngine,
)


def _build_service() -> tuple[DocumentPipelineService, InMemoryEventStore]:
    store = InMemoryEventStore()
    service = DocumentPipelineService(store, ValidationEngine())
    return service, store


def test_happy_path_auto_finalize() -> None:
    service, store = _build_service()
    doc_id = "doc-1"
    correlation_id = service.ingest(doc_id, "invoice.pdf", "user@example.com")

    service.process_extraction(
        document_id=doc_id,
        correlation_id=correlation_id,
        provider="openai",
        model="gpt-4.1",
        attempt=1,
        fields=[
            FieldCandidate("invoice_number", "FV/1", 0.98),
            FieldCandidate("gross_amount", "100.00", 0.95),
        ],
    )

    stream_types = [event.event_type for event in store.load_stream(doc_id)]
    assert EventTypes.DOCUMENT_FINALIZED in stream_types
    assert EventTypes.MANUAL_REVIEW_REQUESTED not in stream_types


def test_low_confidence_routes_to_manual_review() -> None:
    service, store = _build_service()
    doc_id = "doc-2"
    correlation_id = service.ingest(doc_id, "invoice.pdf", "user@example.com")

    service.process_extraction(
        document_id=doc_id,
        correlation_id=correlation_id,
        provider="openai",
        model="gpt-4.1-mini",
        attempt=1,
        fields=[
            FieldCandidate("invoice_number", "FV/2", 0.91),
            FieldCandidate("gross_amount", "100.00", 0.62),
        ],
    )

    stream_types = [event.event_type for event in store.load_stream(doc_id)]
    assert EventTypes.MANUAL_REVIEW_REQUESTED in stream_types
    assert stream_types.count(EventTypes.DOCUMENT_FINALIZED) == 0


def test_manual_correction_finalizes_document() -> None:
    service, store = _build_service()
    doc_id = "doc-3"
    correlation_id = service.ingest(doc_id, "invoice.pdf", "user@example.com")

    service.apply_manual_correction(
        document_id=doc_id,
        correlation_id=correlation_id,
        reviewer="analyst@example.com",
        corrected_fields=[
            {
                "name": "gross_amount",
                "oldValue": "100.00",
                "newValue": "101.00",
                "reason": "OCR fix",
            }
        ],
        comment="Poprawiono odczyt kwoty",
    )

    stream_types = [event.event_type for event in store.load_stream(doc_id)]
    assert EventTypes.MANUAL_CORRECTION_APPLIED in stream_types
    assert EventTypes.DOCUMENT_FINALIZED in stream_types
