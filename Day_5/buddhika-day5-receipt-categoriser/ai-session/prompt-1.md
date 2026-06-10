# Prompt 1 (verbatim) — initial implementation

> Sent to the coding agent (Claude). The spec + acceptance files were pasted in full
> below the instruction block; they are omitted here for brevity (see
> `../spec/spec.md` and `../spec/acceptance.md`).

```
You are implementing a feature in JavaScript (Node, CommonJS) for the GreenChit
Claims API. Below is the COMPLETE spec and acceptance criteria. Implement the feature
so that every acceptance criterion can be made to pass with the Node built-in test
runner (`node --test`), using NO external dependencies.

Constraints:
- Create only: src/categoriser.js, src/llm-categoriser.js, src/rule-based-categoriser.js,
  tests/acceptance.test.js.
- All external providers (OCR, the Azure OpenAI client, telemetry, the feature flag,
  the clock) MUST be injected as dependencies so every criterion is observable from
  outside without real Azure calls.
- Keep the LLM path and the rule-based path in separate files.
- Do NOT invent fields, endpoints, or behaviour that are not in the spec.
- PII must never be written to telemetry.
- Before writing code, list any ambiguities you would want clarified.

[pasted: spec/spec.md]
[pasted: spec/acceptance.md]
```
