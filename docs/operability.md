# Operability: SLO, koszt i recovery

## SLO (MVP)

- 95% dokumentów przetworzone < 120 sekund.
- < 2% dokumentów kończy w DLQ.
- 99.5% event publish success (rolling 24h).

## Error budget

- miesięczny budżet błędów: 0.5% dla krytycznej ścieżki finalize.
- przekroczenie budżetu automatycznie wyłącza eksperymentalne modele AI.

## Cost guardrails

- limit kosztu AI na dokument: `0.10 USD` (hard cap).
- fallback do tańszego modelu przy przekroczeniu miesięcznego budgetu.
- sampling pełnych promptów tylko dla części dokumentów (privacy + koszt).

## Retry matrix

| Step | Błąd transient | Max retry | Strategia |
|---|---:|---:|---|
| OCR | Tak | 5 | exp backoff + jitter |
| AI extraction | Tak | 3 | provider fallback po 2. próbie |
| Validation | Nie (zwykle) | 1 | fail-fast + review |
| Finalize write | Tak | 5 | idempotent upsert |

## Runbook (skrót)

1. Sprawdź trace po `correlationId`.
2. Zweryfikuj ostatni event i etap, na którym pipeline utknął.
3. Jeśli AI timeout/failure: replay od `AiExtractionRequested`.
4. Jeśli konflikt danych: wymuś `ManualReviewRequested`.
5. Po naprawie zaktualizuj read model przez replay streamu.

## Security & compliance

- PII redaction w logach i telemetry.
- szyfrowanie S3/DynamoDB/KMS.
- retention policy: surowe artefakty 30 dni, event stream 12 miesięcy.
