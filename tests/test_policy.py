from document_pipeline.events import AiExtractionCompleted, ExtractedField, ValidationCompleted
from document_pipeline.policy import NextStep, decide_next_step


def test_finalize_when_confident_and_valid() -> None:
    extraction = AiExtractionCompleted(
        provider="openai",
        model="gpt-4.1",
        attempt=1,
        raw_output_uri="s3://x",
        fields=[ExtractedField(name="invoice_number", value="1", confidence=0.95)],
        estimated_cost_usd=0.02,
    )
    validation = ValidationCompleted(
        is_valid=True,
        failed_rules=[],
        score=0.95,
        requires_manual_review=False,
    )

    assert decide_next_step(extraction, validation) == NextStep.FINALIZE_AUTOMATICALLY


def test_retry_when_mid_confidence() -> None:
    extraction = AiExtractionCompleted(
        provider="openai",
        model="gpt-4.1",
        attempt=1,
        raw_output_uri="s3://x",
        fields=[ExtractedField(name="gross_amount", value="1", confidence=0.8)],
        estimated_cost_usd=0.02,
    )
    validation = ValidationCompleted(
        is_valid=True,
        failed_rules=[],
        score=0.8,
        requires_manual_review=False,
    )

    assert decide_next_step(extraction, validation) == NextStep.RETRY_WITH_FALLBACK_MODEL


def test_manual_review_when_cost_cap_exceeded() -> None:
    extraction = AiExtractionCompleted(
        provider="openai",
        model="gpt-4.1",
        attempt=1,
        raw_output_uri="s3://x",
        fields=[ExtractedField(name="gross_amount", value="1", confidence=0.99)],
        estimated_cost_usd=0.11,
    )
    validation = ValidationCompleted(
        is_valid=True,
        failed_rules=[],
        score=0.99,
        requires_manual_review=False,
    )

    assert decide_next_step(extraction, validation) == NextStep.REQUEST_MANUAL_REVIEW
