"use strict";
// Rule-based categoriser — the deterministic fallback used when the LLM path is
// unavailable or degraded. Keyword/score based. Confidence is intentionally CAPPED at
// 0.5 so a rule-based suggestion always reads as "Needs review" (spec §7 / AC-03).

const CATEGORIES = ["Meals", "Travel", "Lodging", "Office Supplies", "Other"];

const RULES = [
  { category: "Lodging", keywords: ["hotel", "resort", "inn", "lodge", "room night", "check-in", "check out", "nights stay"] },
  { category: "Travel", keywords: ["taxi", "uber", "pickme", "airline", "flight", "train", "bus ticket", "fuel", "petrol", "diesel", "parking", "toll", "boarding"] },
  { category: "Meals", keywords: ["restaurant", "cafe", "café", "coffee", "barista", "bakery", "sandwich", "lunch", "dinner", "kottu", "rice and curry", "meal", "bar & grill", "pizza", "burger"] },
  { category: "Office Supplies", keywords: ["paper", "a4", "pen", "pens", "stationery", "stationary", "printer", "ink", "toner", "notebook", "staple", "folder", "cartridge", "marker"] },
];

const RULE_CONFIDENCE_CEILING = 0.5;

/**
 * @param {string} text  OCR text from the receipt
 * @returns {{category: string, confidence: number}}
 */
function ruleBasedCategorise(text) {
  if (!text || !text.trim()) return { category: "Other", confidence: 0.0 };
  const t = text.toLowerCase();

  let best = { category: "Other", hits: 0 };
  for (const rule of RULES) {
    const hits = rule.keywords.reduce((n, k) => n + (t.includes(k) ? 1 : 0), 0);
    if (hits > best.hits) best = { category: rule.category, hits };
  }
  if (best.hits === 0) return { category: "Other", confidence: 0.0 };

  const confidence = Math.min(RULE_CONFIDENCE_CEILING, 0.3 + 0.1 * best.hits);
  return { category: best.category, confidence: Number(confidence.toFixed(2)) };
}

module.exports = { ruleBasedCategorise, CATEGORIES, RULE_CONFIDENCE_CEILING };
