# Prompt 2 (verbatim) — correct the deviations + lock the PII boundary with a test

```
Two problems with the first pass — fix both and do not add anything else:

1. Remove the `tags` field from the response object. The §3 contract is exactly
   { category, confidence, source, needsReview } (+ an optional `message` only on the
   OCR-failure path). No other fields.

2. The telemetry event leaks PII. Remove `ocrText` and `merchantName` from the
   `categoriser.suggested` event entirely. Log ONLY: claimId, receiptId, category,
   confidence, source, needsReview, latencyMs, requestId, and an `ocrChars` COUNT
   (text.length) — never the text itself.

Then ADD an acceptance test AC-06 that:
- feeds OCR text containing "Nimal Perera" and a card "**** **** **** 4321",
- runs categorise,
- serialises the emitted event props and asserts it contains none of: "Nimal Perera",
  "4321", "Cinnamon Grand", and that `ocrChars` is a number.

Re-run `node --test` and confirm all criteria pass. Do not change anything else.
```
