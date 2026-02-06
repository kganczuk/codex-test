from __future__ import annotations

from .models import FieldCandidate, ValidationResult


class ValidationEngine:
    def __init__(self, auto_finalize_threshold: float = 0.90, retry_threshold: float = 0.70):
        self.auto_finalize_threshold = auto_finalize_threshold
        self.retry_threshold = retry_threshold

    def validate(self, fields: list[FieldCandidate]) -> ValidationResult:
        failed_rules: list[str] = []
        by_name = {f.name: f for f in fields}

        if "invoice_number" not in by_name:
            failed_rules.append("invoice_number_present")
        if "gross_amount" not in by_name:
            failed_rules.append("gross_amount_present")

        confidences = [f.confidence for f in fields] if fields else [0.0]
        min_confidence = min(confidences)
        score = round(sum(confidences) / len(confidences), 4)

        if min_confidence < self.retry_threshold:
            failed_rules.append("min_confidence_too_low")

        requires_manual_review = bool(failed_rules) or min_confidence < self.auto_finalize_threshold
        is_valid = not failed_rules

        return ValidationResult(
            is_valid=is_valid,
            requires_manual_review=requires_manual_review,
            failed_rules=failed_rules,
            score=score,
        )
