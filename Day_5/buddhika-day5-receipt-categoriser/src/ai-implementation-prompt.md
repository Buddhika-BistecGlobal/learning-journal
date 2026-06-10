# AI implementation prompt (master, spec-led)

This is the reusable prompt template used to drive the coding agent. The full
turn-by-turn session is in `../ai-session/`. The principle: **paste the spec, then
instruct narrowly** — the agent implements the contract, it does not get to invent it.

```
You are implementing a feature in JavaScript (Node, CommonJS) for the GreenChit
Claims API. Below is the COMPLETE spec and acceptance criteria. Implement the feature
so that every acceptance criterion can be made to pass with the Node built-in test
runner (`node --test`), using NO external dependencies.

Constraints:
- Create only: src/categoriser.js, src/llm-categoriser.js, src/rule-based-categoriser.js,
  tests/acceptance.test.js.
- All external providers (OCR / Document Intelligence, the Azure OpenAI client,
  telemetry, the feature flag, the clock) MUST be injected as dependencies so every
  criterion is observable from outside without real Azure calls.
- Keep the LLM path and the rule-based path in separate files.
- Do NOT invent fields, endpoints, or behaviour that are not in the spec.
- PII must never be written to telemetry.
- Before writing code, list any ambiguities in the spec you would want clarified.

[paste spec/spec.md]
[paste spec/acceptance.md]
```
