# Response 1 — agent's first pass (as produced, before review)

## Ambiguities the agent raised first (good — spec-led behaviour)
1. "Below 0.6 is *Needs review*" — is `needsReview` a field on the response, or only a UI
   concern? **(I answered: put it on the response, `needsReview: confidence < 0.6`.)**
2. When OCR fails, the spec says category `Other` — should that count as `source:"llm"` or
   `"rule-based"`? **(I answered: `rule-based`, since no LLM call happened.)**
3. Does feature-flag-off still emit the telemetry event? **(I answered: no — no event, no
   OCR/LLM call.)**

## What it produced (first cut)
- `rule-based-categoriser.js` and `llm-categoriser.js` cleanly separated — **matched spec.**
- Orchestrator with feature-flag → validate → OCR → LLM → fallback → threshold — **matched spec.**
- **DEVIATION A (invented field):** the output object included an extra **`tags: string[]`**
  field ("to help the UI") that is **not in the §3 contract**:
  ```js
  return { category, confidence, source, needsReview, tags };  // <-- tags not in spec
  ```
- **DEVIATION B (PII leak in telemetry):** the `categoriser.suggested` event logged the raw
  OCR text and a `merchantName` for "debuggability":
  ```js
  telemetry.trackEvent("categoriser.suggested", {
    claimId, category, confidence, source,
    ocrText: text,            // <-- raw receipt text (PII!) leaving the tenant
    merchantName: merchant,   // <-- PII
  });
  ```
  This directly violates NFR "PII must not leave the tenant" and would fail AC-06.
- It wrote tests for AC-01, AC-03, AC-04, AC-05 but **not** an AC-06 PII test (so the leak
  would have shipped green).

## My verdict
Structure and happy/fallback logic were correct first try. But the agent **added behaviour
not in the spec** (Deviation A) and **broke a privacy NFR** (Deviation B) — classic
"helpful" over-reach. Both must go. Follow-up in `prompt-2.md`.
