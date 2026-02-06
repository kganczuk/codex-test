# Event Model

Ten dokument definiuje kontrakty zdarzeń dla pipeline przetwarzania dokumentów.

## Konwencje

- `eventId`: UUID
- `eventType`: nazwa domenowa
- `eventVersion`: semver-like integer (`1`, `2`...)
- `occurredAtUtc`: ISO-8601
- `correlationId`: UUID propagowany end-to-end
- `causationId`: eventId zdarzenia, które wywołało bieżące
- `documentId`: UUID dokumentu

## Envelope

```json
{
  "eventId": "uuid",
  "eventType": "DocumentIngested",
  "eventVersion": 1,
  "occurredAtUtc": "2026-01-10T12:34:56Z",
  "correlationId": "uuid",
  "causationId": "uuid-or-null",
  "documentId": "uuid",
  "payload": {}
}
```

## Core events

### DocumentIngested v1

```json
{
  "source": "api",
  "fileName": "invoice_123.pdf",
  "mimeType": "application/pdf",
  "storageUri": "s3://bucket/path",
  "uploadedBy": "user@company.com"
}
```

### OcrCompleted v1

```json
{
  "ocrProvider": "textract",
  "language": "pl",
  "pages": 3,
  "textUri": "s3://bucket/path/ocr.txt",
  "avgConfidence": 0.94
}
```

### AiExtractionCompleted v1

```json
{
  "provider": "openai",
  "model": "gpt-4.1",
  "attempt": 1,
  "rawOutputUri": "s3://bucket/path/ai-output.json",
  "fields": [
    {
      "name": "invoice_number",
      "value": "FV/01/2026",
      "confidence": 0.93
    },
    {
      "name": "gross_amount",
      "value": "1234.56",
      "confidence": 0.88
    }
  ],
  "estimatedCostUsd": 0.021
}
```

### ValidationCompleted v1

```json
{
  "isValid": false,
  "failedRules": ["gross_amount_matches_sum"],
  "score": 0.81,
  "requiresManualReview": true
}
```

### ManualCorrectionApplied v1

```json
{
  "reviewer": "analyst@company.com",
  "correctedFields": [
    {
      "name": "gross_amount",
      "oldValue": "1234.56",
      "newValue": "1244.56",
      "reason": "OCR misread"
    }
  ],
  "comment": "Kwota brutto nie zgadzała się z pozycjami"
}
```

### DocumentFinalized v1

```json
{
  "finalJsonUri": "s3://bucket/path/final.json",
  "finalizedBy": "system-or-user",
  "qualityGate": "auto-or-manual"
}
```

## Wersjonowanie eventów

- Każda niekompatybilna zmiana -> `eventVersion +1`.
- Consumer musi wspierać co najmniej `N` i `N-1`.
- Upcaster mapuje stare payloady do bieżącej reprezentacji read modelu.
