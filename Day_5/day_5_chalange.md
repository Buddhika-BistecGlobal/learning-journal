Challenge Overview¶
The GreenChit team you designed for on Day 4 wants a small new feature: a "Receipt Categoriser" that reads the line items from an uploaded receipt and suggests an expense category. They want you to write the spec, drive an AI coding agent to implement a first cut, then critique what the agent produced. Today you write almost no code by hand — you write a spec sharp enough that the agent does the right thing the first time.

Time Allocation: 3 hours (during session) Difficulty: Intermediate

Business Requirements¶
Functional Requirements¶
Given an uploaded receipt image, the system suggests one of the categories: Meals, Travel, Lodging, Office Supplies, Other
The suggestion includes a confidence score (0.0-1.0); below 0.6 is shown as "Needs review"
The claimant can accept or change the suggestion before submitting the claim
If the receipt fails OCR or parsing, the claimant sees a clear message and the suggestion is "Other"
Every suggestion (accepted or overridden) is logged for future model evaluation
Non-Functional Requirements¶
Suggestion latency: under 4 seconds p95 from upload to displayed suggestion
The categoriser must continue to work if the LLM provider has a transient outage (fallback to rule-based)
Personally identifiable information must not leave the BISTEC Azure tenant
The cost per suggestion must not exceed LKR 5 at expected volumes (~2,000/month)
The feature must be feature-flagged so it can be turned off without a deploy
Technical Constraints¶
Azure OpenAI Service in the BISTEC tenant (gpt-4.1 family) — not public OpenAI
Receipt OCR via Azure AI Document Intelligence
Backend lives inside the existing GreenChit Claims API service from Day 4
Logging via Application Insights customEvents (event name: categoriser.suggested)
Feature flag via Azure App Configuration
Deliverables¶
1. Feature Spec — All Seven Sections (25 points)¶
File: {your-name}-day5-receipt-categoriser-spec.md

Required Sections:


# Receipt Categoriser — Feature Spec v0.1

## 1. Why
- The user / business outcome we are solving
- The metric this feature is expected to move

## 2. Scope
- In scope (1-3 bullets)
- Affects which containers / services from Day 4

## 3. Contract
### Inputs
- Receipt image (jpeg/png, <= 10 MB) plus claim ID
### Outputs
- { category: enum, confidence: float, source: "llm" | "rule-based" }
### Errors
- 400: bad input, 413: too large, 502: upstream OCR/LLM unavailable
### Side effects
- Application Insights customEvent emitted

## 4. Acceptance criteria
- See deliverable 2

## 5. Examples
- At least 3 in/out examples (happy, ambiguous, error)

## 6. Out of scope
- Multi-receipt batch upload
- Auto-submission without claimant confirmation

## 7. Open questions
- What confidence threshold should trigger "Needs review"?
- Do we want to learn from overrides (active learning) in v1?
Evaluation Criteria: - All 7 sections present and substantively filled (5 pts) - Contract is complete — inputs, outputs, errors, side effects (5 pts) - Out-of-scope explicitly names at least 3 things that could be in scope but are not (5 pts) - Open questions are genuinely open, not retroactively closed (5 pts) - Spec reads as something a reviewer could finish in 15 minutes (5 pts)

2. Acceptance Criteria Set (25 points)¶
File: {your-name}-day5-receipt-categoriser-acceptance.md

Required Content:


# Receipt Categoriser — Acceptance Criteria

## AC-01 happy path: clear meal receipt
**Given** a receipt image of a restaurant bill totalling LKR 2,400
**When** the claimant uploads it via POST /claims/{id}/receipts/categorise
**Then** the response is 200 OK with `{ "category": "Meals", "confidence": >= 0.7, "source": "llm" }`
**And** an Application Insights customEvent `categoriser.suggested` is emitted within 5 seconds

## AC-02 ambiguous receipt
**Given** a receipt with mixed items (food + stationery)
**When** ...
**Then** the suggestion includes confidence and at least one of `category` / `needs_review` is set per the threshold

## AC-03 LLM unavailable — fallback
**Given** Azure OpenAI is returning 503
**When** the claimant uploads a receipt
**Then** the response is 200 OK with `source: "rule-based"` and confidence <= 0.5

## AC-04 OCR failure
**Given** an image that Document Intelligence cannot parse
**When** ...
**Then** ...

## AC-05 oversized payload
...

## AC-06 PII boundary
**Given** a receipt with a customer name and credit card last 4
**When** the request is processed
**Then** the customEvent payload contains no PII and no full card number
Code Requirements: - At least 6 Given/When/Then criteria including: - 1 happy path - 1 ambiguous case - 1 fallback / degraded mode - 1 input error - 1 PII / privacy criterion - Each criterion is observable from outside the code (no "the function calls X internally")

Evaluation Criteria: - Required mix of criteria present (5 pts) - Each criterion is observable, not implementation-bound (5 pts) - Numbers and thresholds in criteria match the NFRs (5 pts) - Negative paths covered, not just happy path (5 pts) - Criteria can be lifted into a test framework with little rewriting (5 pts)

3. AI-Driven Implementation Report (25 points)¶
Repository Structure:


receipt-categoriser/
├── spec/
│   ├── spec.md
│   └── acceptance.md
├── src/
│   ├── categoriser.ts (or .js / .py)
│   ├── llm-categoriser.ts
│   ├── rule-based-categoriser.ts
│   └── ai-implementation-prompt.md
├── tests/
│   └── acceptance.test.ts
├── ai-session/
│   ├── prompt-1.md
│   ├── response-1.md
│   ├── prompt-2.md
│   └── response-2.md
└── README.md
Required Reviews:

#	What you asked the AI	What it produced	Did it match the spec?	Your fix / follow-up
1	First implementation pass	...	partial — invented a tags field not in the spec	removed tags, added test
2	Add fallback when LLM 503	...	...	...
3	...	...	...	...
Minimum Functionality: - [ ] At least 2 prompts to the AI captured verbatim in ai-session/ - [ ] At least one moment where the AI deviated from the spec is documented - [ ] The acceptance test file imports the module and exercises at least 3 of the 6 criteria - [ ] README explains how to run the tests in 5 lines or fewer - [ ] You commit the prompts and responses, not just the final code

Evaluation Criteria: - Prompts are spec-led, not chatty (5 pts) - At least one AI deviation is captured honestly with what you did about it (5 pts) - Tests run and at least 3 acceptance criteria pass (5 pts) - Code structure separates LLM and rule-based paths cleanly (5 pts) - README is reproducible by another intern (5 pts)

4. Spec Review Feedback (25 points)¶
File: {your-name}-day5-spec-review.md

Required Tests/Validations:

#	Reviewer	Section	Smell type (vague / hidden assumption / embedded solution)	Quote	Suggested rewrite
1	given to	Contract	embedded solution	...	...
2	given to	Acceptance criteria	vague	...	...
3	received from	Why	hidden assumption	...	...
Report Format:


# Receipt Categoriser — Spec Review

## Setup
- Reviewer pair: {names}
- Spec version reviewed: {their commit hash}

## Results Summary
| Metric | Target | Achieved |
|--------|--------|----------|
| Smells found in their spec | 5+ | ? |
| Smells found in mine | 3+ | ? |
| Acceptance criteria you pushed back on | 1+ | ? |
| Reviewer disagreements that produced a real change | 1+ | ? |

## Feedback given (their spec)
- Strengths (3 bullets)
- Risks (3 bullets)
- Concrete rewrites (3 quoted before/after pairs)

## Feedback received (my spec)
- Strengths
- Risks
- Concrete rewrites I accepted vs pushed back on, and why

## Reflection
- Which class of smell did your spec suffer most from?
- Which class did you find easiest to spot in someone else's?
Evaluation Criteria: - At least 5 smells identified across given+received (5 pts) - Smells are correctly classified (vague / hidden / embedded) (5 pts) - Each smell has a quoted rewrite, not just "be more specific" (5 pts) - Reflection demonstrates real learning, not boilerplate (5 pts) - At least one disagreement with a reviewer is documented honestly (5 pts)

Submission Guidelines¶
File Naming Convention¶

{your-name}-day5-receipt-categoriser-spec.md
{your-name}-day5-receipt-categoriser-acceptance.md
{your-name}-day5-receipt-categoriser/  (zipped repository, includes ai-session/)
{your-name}-day5-spec-review.md
Submission Checklist¶
Spec covers all 7 sections
At least 6 acceptance criteria including negatives and a PII case
AI session prompts and responses checked into ai-session/
Tests run; README is reproducible
Spec review given AND received documented
Scoring Guide¶
Grade	Score	Description
Exceptional	90-100	Spec is reviewable in 15 min and the AI implements correctly first try; honest write-up of where the agent went wrong; review feedback is genuinely useful
Proficient	75-89	All seven sections present and substantive; AI driven by the spec, not by chat; review feedback specific and respectful
Developing	60-74	Some sections thin or missing; AI session shows chat-driven iteration rather than spec-driven; review feedback general
Beginning	<60	Spec is a wishlist; AI session is "make it work"; review feedback is "looks good"
Passing Score: 75%

Hints and Tips¶
Spec-led prompt — paste the spec, then instruct narrowly¶

You are implementing a feature in TypeScript. Below is the complete spec
and acceptance criteria. Implement the feature so that all acceptance
criteria can be made to pass with a small test runner.

Constraints:
- Touch only files under `src/categoriser/` and `tests/`
- Use the existing logger; do not add new dependencies
- Do NOT invent fields, endpoints, or behaviour not in the spec
- Before writing code, list any ambiguities in the spec you would want clarified

[paste spec.md]
[paste acceptance.md]
Acceptance test scaffolding the AI can fill in¶

import { categorise } from "../src/categoriser";

test("AC-01 happy path: clear meal receipt", async () => {
  const result = await categorise(loadFixture("meal-receipt.png"));
  expect(result.category).toBe("Meals");
  expect(result.confidence).toBeGreaterThanOrEqual(0.7);
  expect(result.source).toBe("llm");
});

test("AC-03 LLM unavailable falls back to rule-based", async () => {
  withFakeLLM({ status: 503 }, async () => {
    const result = await categorise(loadFixture("any-receipt.png"));
    expect(result.source).toBe("rule-based");
    expect(result.confidence).toBeLessThanOrEqual(0.5);
  });
});
Smell-spotting rewrites — show before and after¶

Before: "The system should be fast and handle many users."
Smell:  vagueness
After:  "Suggestion endpoint returns within 4 s p95 at 50 concurrent claimants
        per the load test in tests/load/categoriser.k6.js."

Before: "Use Redis to cache categoriser responses."
Smell:  embedded solution
After:  "(moved to Open question) Cache categoriser responses if hit rate >= 30%
        in shadow traffic. Choice of cache deferred to ADR."
