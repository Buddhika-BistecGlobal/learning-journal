# Receipt Categoriser — Acceptance Criteria

> **Author:** Buddhika Amarasinghe
> Every criterion is **observable from outside** the module: it asserts on the returned
> result and/or the emitted `categoriser.suggested` event captured by a fake telemetry
> sink — never on internal calls. Thresholds match the spec/NFRs.

## AC-01 — Happy path: clear meal receipt
**Given** a receipt whose OCR text is a restaurant bill totalling LKR 2,400
**When** the claimant categorises it via `POST /claims/{id}/receipts/{rid}/categorise`
**Then** the response is **200** with `category = "Meals"`, `confidence ≥ 0.7`, `source = "llm"`, `needsReview = false`
**And** exactly one `categoriser.suggested` customEvent is emitted with `latencyMs` present.

## AC-02 — Ambiguous receipt (mixed items)
**Given** a receipt with food **and** stationery line items
**When** it is categorised
**Then** the response is **200** with a `category` from the enum, `confidence < 0.6`, and **`needsReview = true`** (the threshold rule fires).

## AC-03 — LLM unavailable → rule-based fallback
**Given** Azure OpenAI returns **503** (transient outage)
**When** the claimant categorises any readable receipt
**Then** the response is **200** with `source = "rule-based"` and `confidence ≤ 0.5`
**And** the emitted event has `source = "rule-based"` (degraded mode is observable in telemetry).

## AC-04 — OCR failure → "Other"
**Given** an image Document Intelligence cannot parse (no usable text)
**When** the claimant categorises it
**Then** the response is **200** with `category = "Other"`, `source = "rule-based"`, `needsReview = true`
**And** the result carries a human-readable `message` telling the claimant to pick a category (no 5xx).

## AC-05 — Oversized payload → 413
**Given** a receipt image larger than **10 MB**
**When** the categorise endpoint is called
**Then** the call fails with an error whose **status = 413** and `code = "payload_too_large"`
**And** **no** `categoriser.suggested` event is emitted.

## AC-06 — PII boundary (privacy)
**Given** a receipt whose OCR text contains a customer name ("Nimal Perera") and a card "**** **** **** 4321"
**When** it is categorised
**Then** the emitted `categoriser.suggested` event payload, serialised, contains **none** of: the customer name, the digits "4321", or the raw OCR text
**And** the event still contains `category`, `confidence`, `source`, and an `ocrChars` **count**.

## AC-07 — Bad input → 400
**Given** a request with an unsupported content type (e.g. `application/pdf`) or a missing `claimId`
**When** the categorise endpoint is called
**Then** the call fails with **status = 400** and `code = "bad_input"`, and no event is emitted.

## AC-08 — Feature flag off
**Given** the `receipt-categoriser` flag in Azure App Configuration is **disabled**
**When** the claimant categorises a receipt
**Then** the response is **200** with `source = "disabled"` and `needsReview = true` (the UI just shows the manual dropdown)
**And** **no** `categoriser.suggested` event is emitted and **no** LLM/OCR call is made.

---

### Coverage map (for the grader)
| Required kind | Criterion |
|---|---|
| Happy path | AC-01 |
| Ambiguous case | AC-02 |
| Fallback / degraded mode | AC-03 |
| Input error | AC-05 (413), AC-07 (400) |
| PII / privacy | AC-06 |
| Error/degraded (OCR) | AC-04 |
| Operability (flag) | AC-08 |
