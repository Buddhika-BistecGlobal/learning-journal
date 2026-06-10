"use strict";
// LLM categoriser — the primary path. Wraps an injected Azure OpenAI client so the
// orchestrator and tests stay provider-agnostic. The client is expected to call the
// BISTEC-tenant Azure OpenAI (gpt-4.1 family); it must THROW on a transient outage
// (e.g. err.status === 503) so the orchestrator can fall back to the rule-based path.

const { CATEGORIES } = require("./rule-based-categoriser");

function clamp(n, lo, hi) {
  if (typeof n !== "number" || Number.isNaN(n)) return lo;
  return Math.max(lo, Math.min(hi, n));
}

/**
 * @param {string} text       OCR text from the receipt
 * @param {{classify: (text: string) => Promise<{category: string, confidence: number}>}} llmClient
 * @returns {Promise<{category: string, confidence: number, source: "llm"}>}
 * @throws  propagates the client error (e.g. 503) so the caller can fall back
 */
async function llmCategorise(text, llmClient) {
  const res = await llmClient.classify(text); // may throw on outage — intentionally not caught here
  const category = CATEGORIES.includes(res && res.category) ? res.category : "Other";
  const confidence = clamp(res && res.confidence, 0, 1);
  return { category, confidence: Number(confidence.toFixed(2)), source: "llm" };
}

// Reference prompt the real Azure OpenAI client should send. Kept here so the contract
// (closed category set, JSON-only output, no PII echoed back) lives next to the code.
const SYSTEM_PROMPT = [
  "You categorise a single expense receipt into exactly one of:",
  "Meals, Travel, Lodging, Office Supplies, Other.",
  "Return ONLY JSON: {\"category\": <one of the five>, \"confidence\": <0.0-1.0>}.",
  "Base it on the dominant spend by amount when line amounts are available, else by item",
  "count / keywords. If genuinely mixed or unclear, lower the",
  "confidence. Do not echo back any names, card numbers, or raw text.",
].join(" ");

module.exports = { llmCategorise, SYSTEM_PROMPT };
