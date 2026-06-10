"use strict";
// Orchestrator for the Receipt Categoriser feature (GreenChit Claims API).
// Flow: feature flag -> validate -> OCR -> LLM (fallback rule-based) -> threshold -> emit event.
// All external providers (ocr, llmClient, telemetry, featureFlag, clock) are INJECTED so
// every acceptance criterion is observable from outside without real Azure calls.

const { llmCategorise } = require("./llm-categoriser");
const { ruleBasedCategorise, CATEGORIES } = require("./rule-based-categoriser");

const MAX_BYTES = 10 * 1024 * 1024; // 10 MB
const ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"];
const NEEDS_REVIEW_BELOW = 0.6; // spec §3 / AC-02
const FLAG_KEY = "receipt-categoriser";

class CategoriserError extends Error {
  constructor(code, status, message) {
    super(message);
    this.name = "CategoriserError";
    this.code = code;     // machine-readable: bad_input | payload_too_large | upstream_unavailable
    this.status = status; // HTTP status the controller should return
  }
}

/**
 * @param {{claimId:string, receiptId:string, contentType:string, sizeBytes?:number, requestId?:string}} input
 * @param {{
 *   ocr: {read: (input:object) => Promise<string>},
 *   llmClient: {classify: (text:string) => Promise<{category:string, confidence:number}>},
 *   telemetry?: {trackEvent: (name:string, props:object) => void},
 *   featureFlag?: {isEnabled: (key:string) => Promise<boolean>},
 *   now?: () => number,
 *   maxBytes?: number
 * }} deps
 * @returns {Promise<{category:string, confidence:number, source:string, needsReview:boolean, message?:string}>}
 */
async function categorise(input, deps) {
  const { ocr, llmClient, telemetry, featureFlag, now = () => Date.now(), maxBytes = MAX_BYTES } = deps;
  const started = now();
  const { claimId, receiptId, contentType, sizeBytes } = input || {};

  // 1) Feature flag — off ⇒ no OCR/LLM call, no event (AC-08)
  if (featureFlag && typeof featureFlag.isEnabled === "function") {
    const on = await featureFlag.isEnabled(FLAG_KEY);
    if (!on) {
      return { category: "Other", confidence: 0.0, source: "disabled", needsReview: true };
    }
  }

  // 2) Validate input — throw before any side effect (AC-05, AC-07: no event emitted)
  if (!claimId || !receiptId) {
    throw new CategoriserError("bad_input", 400, "claimId and receiptId are required");
  }
  if (!ALLOWED_CONTENT_TYPES.includes(contentType)) {
    throw new CategoriserError("bad_input", 400, `unsupported content type: ${contentType}`);
  }
  if (typeof sizeBytes === "number" && sizeBytes > maxBytes) {
    throw new CategoriserError("payload_too_large", 413, "receipt exceeds 10 MB");
  }

  // 3) OCR via Document Intelligence (injected)
  let text = "";
  let ocrFailed = false;
  try {
    text = await ocr.read(input);
  } catch (_e) {
    ocrFailed = true;
  }
  if (!text || !text.trim()) ocrFailed = true;

  // 4) Classify
  let result;
  if (ocrFailed) {
    // OCR failure degrades to "Other" — NOT a 5xx (spec §5 example 3 / AC-04)
    result = {
      category: "Other",
      confidence: 0.0,
      source: "rule-based",
      needsReview: true,
      message: "We couldn't read this receipt — please pick a category.",
    };
  } else {
    try {
      result = await llmCategorise(text, llmClient); // {category, confidence, source:"llm"}
    } catch (_e) {
      // LLM transient outage ⇒ rule-based fallback, confidence capped ≤ 0.5 (AC-03)
      const rb = ruleBasedCategorise(text);
      result = { category: rb.category, confidence: rb.confidence, source: "rule-based" };
    }
    result.needsReview = result.confidence < NEEDS_REVIEW_BELOW;
  }

  // 5) Emit telemetry — PII MUST NOT leave the tenant. We log counts/labels only,
  //    never the OCR text, merchant/customer name, or card digits (AC-06).
  const latencyMs = now() - started;
  if (telemetry && typeof telemetry.trackEvent === "function") {
    telemetry.trackEvent("categoriser.suggested", {
      claimId,
      receiptId,
      category: result.category,
      confidence: result.confidence,
      source: result.source,
      needsReview: result.needsReview,
      latencyMs,
      ocrChars: text ? text.length : 0, // a COUNT, not the text
      requestId: input.requestId || null,
    });
  }

  return result;
}

module.exports = { categorise, CategoriserError, CATEGORIES, NEEDS_REVIEW_BELOW, MAX_BYTES };
