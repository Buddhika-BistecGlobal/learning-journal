# Receipt Categoriser — AI-driven implementation

> **Author:** Buddhika Amarasinghe
> A spec-driven first cut of GreenChit's Receipt Categoriser. Today's exercise: write a
> spec sharp enough that an AI coding agent implements it correctly, then critique the
> result. The full driving session is in `ai-session/`.

## Run the tests (zero dependencies)
```bash
# Requires Node >= 18 (built-in test runner). No npm install needed.
cd buddhika-day5-receipt-categoriser
node --test
# → 8 passing (AC-01 … AC-08)
```

## Layout
```
spec/           spec.md, acceptance.md (the contract the agent implemented)
src/            categoriser.js (orchestrator), llm-categoriser.js, rule-based-categoriser.js,
                ai-implementation-prompt.md (the master spec-led prompt)
tests/          acceptance.test.js (8 ACs, observable-only assertions)
ai-session/     prompt-1/response-1 (first cut + deviations), prompt-2/response-2 (fixes)
```

## How it works
`categorise(input, deps)` runs: **feature flag → validate → OCR → LLM (fallback to
rule-based) → confidence threshold → emit `categoriser.suggested`**. Every external
provider (OCR, Azure OpenAI client, telemetry, feature flag, clock) is **injected**, so
all acceptance criteria are observable without real Azure calls. The LLM path and the
rule-based fallback live in separate files.

## AI implementation report

| # | What I asked the AI | What it produced | Matched the spec? | My fix / follow-up |
|---|---------------------|------------------|-------------------|--------------------|
| 1 | First implementation pass from spec + acceptance (prompt-1) | Clean LLM/rule-based split; correct flag→validate→OCR→LLM→fallback→threshold logic; raised 3 good ambiguity questions first | **Partial** — invented a `tags` field not in §3; **leaked PII** (logged raw OCR text + `merchantName` into the customEvent); no PII test | Documented both deviations in `ai-session/response-1.md`; issued prompt-2 to remove `tags`, strip PII to an `ocrChars` count, and add a PII test |
| 2 | Remove `tags`, close the PII leak, add AC-06 PII test, re-run (prompt-2) | Output trimmed to the exact contract; event now logs labels/counts only; added AC-02/06/07/08 | **Yes** | Re-ran `node --test` → **8/8 pass**; this is the committed code |
| 3 | (Verification) confirm fallback + flag-off make no upstream calls | AC-03 fallback and AC-08 flag-off assert `source` and that OCR/LLM were never called | **Yes** | Kept as regression guards |

**Honest note:** in this exercise I acted as both the spec author (Buddhika) and the
coding agent. The deviations in pass 1 are real failure modes of agent coding —
scope-creep fields and "helpful" debug logging that breaks a privacy NFR — captured here
rather than airbrushed out.

## What a real deployment still needs (not in this spike)
- Wire the injected `ocr` to **Azure AI Document Intelligence**, `llmClient` to **Azure
  OpenAI (gpt-4.1, BISTEC tenant)**, `telemetry` to **Application Insights**, `featureFlag`
  to **Azure App Configuration**.
- The HTTP controller maps `CategoriserError.status` (400/413) to responses; 502 only when
  OCR *and* fallback are both impossible.
