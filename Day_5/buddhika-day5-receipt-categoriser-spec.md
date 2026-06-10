# Receipt Categoriser — Feature Spec v0.1

> **Author:** Buddhika Amarasinghe · **Date:** 2026-06-10 · **Status:** Draft for review
> Sits inside the GreenChit Claims API (Day 4). Reviewer should be able to finish this in ~15 minutes.

## 1. Why
- **User outcome:** when a claimant uploads a receipt, GreenChit pre-fills the expense
  **category** so they don't have to choose from a dropdown and guess — fewer taps,
  fewer mis-categorised claims for finance to correct.
- **Business outcome:** less manual correction work for finance and cleaner expense
  reporting.
- **Metric this is expected to move:** **% of submitted claims whose category is the
  one finance keeps (i.e. not changed during approval/export)**. We first **establish the
  current baseline in week 1** (today this is unmeasured), then target **baseline +
  ≥ 15 percentage points within 2 months**. Secondary: median time on the "category" step
  of the submit flow. *(Baseline note added after spec review — smell #7.)*

## 2. Scope
- **In scope:** suggest **one** category (`Meals | Travel | Lodging | Office Supplies |
  Other`) with a **confidence score** for a **single** uploaded receipt; show "Needs
  review" below the threshold; let the claimant accept or change it; log every suggestion.
- **Affects (from Day 4):** the **Claims API** container (new internal `categorise`
  component + endpoint), the **Web App** (shows the suggestion), **Blob Storage** (reads
  the already-uploaded receipt), and adds two dependencies — **Azure AI Document
  Intelligence** (OCR) and **Azure OpenAI** (classification). Logging via **Application
  Insights**; flag via **Azure App Configuration**. No DB schema change beyond storing the
  chosen category on the claim (already exists).

## 3. Contract

### Inputs
- `claimId` — the owning claim (string, must belong to the caller).
- A receipt image **already in Blob Storage** for that claim: **JPEG or PNG, ≤ 10 MB**.
- Endpoint: `POST /claims/{claimId}/receipts/{receiptId}/categorise` (JWT required).

### Outputs (200 OK)
```json
{
  "category": "Meals | Travel | Lodging | Office Supplies | Other",
  "confidence": 0.0,
  "source": "llm | rule-based",
  "needsReview": true
}
```
- `confidence` ∈ [0.0, 1.0]. `needsReview` is `true` when `confidence < 0.6`.
- `source` is `"llm"` normally, `"rule-based"` when the LLM path was unavailable/degraded.

### Errors
- **400** bad input (missing/invalid `claimId` or `receiptId`, unsupported content type).
- **413** payload too large (> 10 MB).
- **502** upstream OCR **and** rule-based fallback both impossible (should be rare — OCR
  failure alone degrades to `Other`, it does not 502; see §5 example 3).
- **403** caller is not the claim owner. **404** claim/receipt not found.

### Side effects
- Exactly **one** Application Insights `customEvent` named **`categoriser.suggested`** per
  call, with **no PII** (see §5 example 3 / AC-06): properties `claimId`, `receiptId`,
  `category`, `confidence`, `source`, `needsReview`, `latencyMs`, `ocrChars` (count only),
  `requestId`. **Never** the OCR text, merchant name, customer name, or card digits.
- No write to the claim record here — the claimant's accept/change is a separate call.

## 4. Acceptance criteria
See `buddhika-day5-receipt-categoriser-acceptance.md` (AC-01 … AC-08).

## 5. Examples

**Example 1 — happy path (clear meal):**
```
In:  receipt OCR = "Barista Colombo … Cappuccino 1,200 … Club Sandwich 1,200 … TOTAL LKR 2,400"
Out: { "category": "Meals", "confidence": 0.88, "source": "llm", "needsReview": false }
```

**Example 2 — ambiguous (food + stationery):**
```
In:  receipt OCR = "SuperMart … Sandwich 600 … A4 Paper ream 1,800 … Pens x5 500 … TOTAL 2,900"
Out: { "category": "Office Supplies", "confidence": 0.52, "source": "llm", "needsReview": true }
     (dominant by amount where line amounts are available — here stationery — else by
      item-count / keyword weight; mixed → low confidence → Needs review.
      Wording fixed after spec review — smell #6.)
```

**Example 3 — error (OCR cannot parse a blurry photo):**
```
In:  unreadable image (Document Intelligence returns no text / low quality)
Out: { "category": "Other", "confidence": 0.0, "source": "rule-based", "needsReview": true }
UI:  "We couldn't read this receipt — please pick a category."   (HTTP 200, not an error code)
```

## 6. Out of scope (could be in scope, deliberately is not)
1. **Multi-receipt / batch upload** categorisation in one call.
2. **Auto-submission** of the claim without the claimant confirming the category.
3. **Line-item splitting** (one receipt → multiple categories / split claims).
4. **Active learning** — automatically retraining or adjusting the model from overrides
   (we *log* overrides for later, but do not learn from them in v1; see §7).
5. **Non-LKR / multi-currency** amount normalisation and **non-English** receipts.
6. **Editing the OCR text** or a manual "re-run OCR" button.

## 7. Open questions (genuinely open)
1. **Confidence threshold:** is **0.6** the right "Needs review" cut-off, or should we tune
   it from the first month of logged suggestions vs overrides? (Currently a guess.)
2. **Active learning:** do we want v2 to learn from claimant overrides, and if so what's
   the governance/approval for changing a finance-facing model?
3. **Category for tips/service charge / mixed meals+travel** (e.g. a hotel bill with a
   restaurant line) — single category may be genuinely wrong; revisit with line-item split.
4. **Cost guard:** at ~2,000/month the LKR 5 ceiling is comfortable, but what is the hard
   monthly spend cap and who is alerted if a retry storm blows it?
5. **Rule-based confidence ceiling:** we cap fallback confidence at ≤ 0.5 so it always
   reads as "Needs review" — is that the desired UX, or should a very strong keyword
   match (e.g. "HOTEL") be allowed higher?
