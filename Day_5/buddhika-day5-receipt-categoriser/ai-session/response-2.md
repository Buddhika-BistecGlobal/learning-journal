# Response 2 — corrected (this is what is committed in `src/` and `tests/`)

## What changed
- **Removed `tags`** from the response. The result object is now exactly
  `{ category, confidence, source, needsReview }` (+ `message` only on the OCR-failure
  path), matching the §3 contract.
- **Closed the PII leak.** The `categoriser.suggested` event no longer contains `ocrText`
  or `merchantName`. It now emits labels/counts only:
  ```js
  telemetry.trackEvent("categoriser.suggested", {
    claimId, receiptId, category, confidence, source, needsReview,
    latencyMs, ocrChars: text ? text.length : 0, requestId: input.requestId || null,
  });
  ```
- **Added AC-06** to `tests/acceptance.test.js` (PII boundary), plus AC-02 (ambiguous) and
  AC-07 (bad input) and AC-08 (flag off) for full coverage of the required mix.

## Test run (actual)
```
$ node --test
...
1..8
# tests 8
# pass 8
# fail 0
# duration_ms ~224
```

## Reviewer note
The agent fixed exactly what was asked and nothing more — no new scope crept in on the
second pass. The lesson captured: **the spec's contract is a closed list**; an agent will
helpfully add "useful" fields and debug logging unless the prompt explicitly forbids it,
and a privacy NFR needs its own *test* (AC-06) or it silently regresses.
