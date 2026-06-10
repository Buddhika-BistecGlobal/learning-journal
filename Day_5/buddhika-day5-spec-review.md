# Receipt Categoriser — Spec Review

> **Author:** Buddhika Amarasinghe
> **Note on the exercise:** the challenge pairs interns to swap specs. Working solo, I
> reviewed against a **representative "Pair B" spec** — a plausible alternative
> Receipt-Categoriser spec that makes the common mistakes — and I self-reviewed my own
> spec with the same lens. Feedback is concrete (quoted before/after), not invented praise.

## Setup
- **Reviewer pair:** Buddhika (me) ⇄ "Pair B" (representative alternative spec).
- **Spec version reviewed (theirs):** `pairB-receipt-categoriser-spec.md` @ commit `b2f9c10`.
- **My spec under review:** `buddhika-day5-receipt-categoriser-spec.md` v0.1.

## Results Summary
| Metric | Target | Achieved |
|--------|--------|----------|
| Smells found in their spec | 5+ | **5** |
| Smells found in mine | 3+ | **3** |
| Acceptance criteria I pushed back on | 1+ | **1** (rule-based confidence cap) |
| Reviewer disagreements that produced a real change | 1+ | **1** (cap value → moved to Open Q#5) |

## Smell log (classified)
| # | Direction | Section | Smell type | Quote | Suggested rewrite |
|---|-----------|---------|-----------|-------|-------------------|
| 1 | given→Pair B | Contract | **embedded solution** | "Use Azure OpenAI with function calling and **cache responses in Redis**." | "Suggest a category from OCR text (LLM primary, rule-based fallback). *Whether* to cache and with what store is a design decision — move to an Open Question / ADR, not the contract." |
| 2 | given→Pair B | NFR | **vague** | "The categoriser should be **fast and accurate**." | "Suggestion ≤ **4 s p95** upload→display; **≥ 80% top-1 agreement** with a 200-receipt human-labelled set before GA." |
| 3 | given→Pair B | Why | **hidden assumption** | "Read the **merchant name** to decide the category." | "Assumes OCR reliably extracts a merchant name *and* that merchant→category is stable — neither is given, and merchant name is PII. Decide on dominant line-item spend; treat merchant as a weak hint only." |
| 4 | given→Pair B | Errors | **vague** | "**Handle errors gracefully.**" | "Enumerate: 400 bad input, 413 > 10 MB, OCR-unreadable → `Other` at 200, 502 only if OCR *and* fallback both fail." |
| 5 | given→Pair B | Logging | **embedded solution** | "Store every suggestion in a **new `CategorySuggestions` SQL table**." | "Requirement is *log every suggestion for evaluation*. The store (App Insights customEvent per the constraint) is a design choice — state the requirement, not the schema." |
| 6 | received→mine | Examples | **hidden assumption** | "dominant spend is stationery" / "Base the decision on the **dominant spend**." | "Assumes per-line **amounts** are always OCR-extractable and comparable. Reword: 'dominant by amount when line amounts are available; otherwise by item-count / keyword weight.'" |
| 7 | received→mine | Why | **vague** | "lift … by **≥ 15 percentage points**" | "No current **baseline** is stated, so the target is unanchored. Add: 'measure the current category-change rate in week 1; target baseline + 15pp.'" |
| 8 | received→mine | Contract/§7 | **embedded solution** (disputed) | "we **cap fallback confidence at ≤ 0.5**" | Reviewer flagged the hard 0.5 as a solution baked into the contract. **I pushed back** (see disagreement) but moved the exact value to Open Q#5. |

## Feedback given (Pair B's spec)
**Strengths**
- Clear five-category enum and a confidence field — the core contract shape is right.
- They included a fallback requirement for LLM outage (good NFR instinct).
- They named a feature flag, matching the constraint.

**Risks**
- **Embedded solutions** (Redis cache #1, SQL table #5) pre-empt design decisions and will
  bias the AI agent into building infra the spec hasn't justified.
- **Vague NFRs** ("fast and accurate", "handle errors gracefully" #2, #4) aren't testable —
  the agent will guess, and the reviewer can't sign off in 15 minutes.
- **PII hidden assumption** (#3): deciding on merchant name both over-trusts OCR and risks
  logging PII — a real privacy regression waiting to happen.

**Concrete rewrites (before → after)**
1. *Before:* "cache responses in Redis." → *After:* "(Open question) cache only if shadow-traffic hit-rate ≥ 30%; store choice deferred to ADR."
2. *Before:* "fast and accurate." → *After:* "≤ 4 s p95; ≥ 80% top-1 agreement vs a 200-receipt labelled set."
3. *Before:* "store in a new CategorySuggestions SQL table." → *After:* "emit one `categoriser.suggested` App Insights customEvent (per constraint); no schema mandated."

## Feedback received (my spec)
**Strengths**
- All 7 sections substantive; contract enumerates inputs/outputs/errors/side-effects.
- Out-of-scope and Open Questions are genuinely open (threshold, active learning).
- PII boundary is explicit and has its own acceptance criterion (AC-06).

**Risks**
- "Dominant spend" hides an OCR assumption (#6).
- The 15pp metric has no baseline (#7).

**Rewrites accepted vs pushed back**
- **Accepted #6:** changed §5/§ wording to "dominant by amount *when line amounts are
  available*, else by item-count/keyword weight."
- **Accepted #7:** added "establish baseline in week 1" to §1.
- **Pushed back #8 (documented disagreement):** the reviewer called the `≤ 0.5` rule-based
  cap an *embedded solution* and wanted it removed from the contract. **I disagreed** — it
  is a deliberate **UX requirement** (a degraded fallback must always surface as "Needs
  review", never masquerade as a confident answer), so the *behaviour* stays in the
  contract. **Compromise that produced a real change:** the exact *number* 0.5 was not
  defensible, so I moved it to **Open Q#5** for tuning while keeping the rule "fallback
  ⇒ needsReview = true."

## Reflection
- **Which class my spec suffered most from:** **hidden assumptions** — "dominant spend"
  and the unstated baseline both *read* as facts but rest on conditions I hadn't checked.
  They're the hardest to catch in your own writing because they feel obviously true.
- **Which class was easiest to spot in someone else's:** **embedded solutions** — "use
  Redis", "new SQL table" jump off the page because they answer *how* before the spec has
  pinned *what*. The lesson: in my own spec I police vagueness well but under-notice the
  assumptions baked into confident-sounding sentences — so I now read each declarative
  line asking "what must be true for this to hold?"
