"use strict";
// Acceptance tests — run with:  node --test
// Each test maps to an AC in spec/acceptance.md and asserts only on OBSERVABLE outputs:
// the returned result and the events captured by a fake telemetry sink.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const { categorise, CategoriserError } = require("../src/categoriser");

// ---- Fakes / fixtures -------------------------------------------------------
const MEAL_TEXT = "Barista Colombo\nCappuccino 1,200\nClub Sandwich 1,200\nTOTAL LKR 2,400";
const MIXED_TEXT = "SuperMart\nSandwich 600\nA4 Paper ream 1,800\nPens x5 500\nTOTAL 2,900";
const PII_TEXT = "Cinnamon Grand Restaurant\nGuest: Nimal Perera\nVisa **** **** **** 4321\nDinner 5,600\nTOTAL LKR 5,600";

function makeDeps(overrides = {}) {
  const events = [];
  const deps = {
    ocr: { read: async () => overrides.ocrText !== undefined ? overrides.ocrText : MEAL_TEXT },
    llmClient: { classify: async () => ({ category: "Meals", confidence: 0.88 }) },
    telemetry: { trackEvent: (name, props) => events.push({ name, props }) },
    featureFlag: { isEnabled: async () => true },
    now: (() => { let t = 1000; return () => (t += 250); })(), // deterministic clock → latencyMs = 250
    ...overrides.deps,
  };
  if (overrides.ocr) deps.ocr = overrides.ocr;
  if (overrides.llmClient) deps.llmClient = overrides.llmClient;
  if (overrides.featureFlag) deps.featureFlag = overrides.featureFlag;
  return { deps, events };
}

const goodInput = { claimId: "c1", receiptId: "r1", contentType: "image/jpeg", sizeBytes: 1024, requestId: "req-1" };

// ---- AC-01 happy path -------------------------------------------------------
test("AC-01 happy path: clear meal receipt → Meals, >=0.7, llm", async () => {
  const { deps, events } = makeDeps({ ocrText: MEAL_TEXT });
  const r = await categorise(goodInput, deps);
  assert.equal(r.category, "Meals");
  assert.ok(r.confidence >= 0.7, `confidence ${r.confidence} >= 0.7`);
  assert.equal(r.source, "llm");
  assert.equal(r.needsReview, false);
  assert.equal(events.length, 1);
  assert.equal(events[0].name, "categoriser.suggested");
  assert.ok(typeof events[0].props.latencyMs === "number");
});

// ---- AC-02 ambiguous --------------------------------------------------------
test("AC-02 ambiguous receipt → confidence < 0.6 and needsReview true", async () => {
  const { deps } = makeDeps({
    ocrText: MIXED_TEXT,
    llmClient: { classify: async () => ({ category: "Office Supplies", confidence: 0.52 }) },
  });
  const r = await categorise(goodInput, deps);
  assert.ok(["Meals", "Travel", "Lodging", "Office Supplies", "Other"].includes(r.category));
  assert.ok(r.confidence < 0.6, `confidence ${r.confidence} < 0.6`);
  assert.equal(r.needsReview, true);
});

// ---- AC-03 LLM 503 → rule-based fallback ------------------------------------
test("AC-03 LLM unavailable → source rule-based, confidence <= 0.5", async () => {
  const { deps, events } = makeDeps({
    ocrText: MEAL_TEXT,
    llmClient: { classify: async () => { const e = new Error("Service Unavailable"); e.status = 503; throw e; } },
  });
  const r = await categorise(goodInput, deps);
  assert.equal(r.source, "rule-based");
  assert.ok(r.confidence <= 0.5, `confidence ${r.confidence} <= 0.5`);
  assert.equal(events[0].props.source, "rule-based");
});

// ---- AC-04 OCR failure → Other ----------------------------------------------
test("AC-04 OCR cannot parse → Other, rule-based, needsReview, message", async () => {
  const { deps } = makeDeps({ ocr: { read: async () => { throw new Error("unreadable"); } } });
  const r = await categorise(goodInput, deps);
  assert.equal(r.category, "Other");
  assert.equal(r.source, "rule-based");
  assert.equal(r.needsReview, true);
  assert.match(r.message, /pick a category/i);
});

// ---- AC-05 oversized → 413 --------------------------------------------------
test("AC-05 oversized payload → 413, no event", async () => {
  const { deps, events } = makeDeps();
  const big = { ...goodInput, sizeBytes: 11 * 1024 * 1024 };
  await assert.rejects(
    () => categorise(big, deps),
    (err) => err instanceof CategoriserError && err.status === 413 && err.code === "payload_too_large"
  );
  assert.equal(events.length, 0);
});

// ---- AC-06 PII boundary -----------------------------------------------------
test("AC-06 emitted event contains no PII", async () => {
  const { deps, events } = makeDeps({
    ocrText: PII_TEXT,
    llmClient: { classify: async () => ({ category: "Meals", confidence: 0.9 }) },
  });
  await categorise(goodInput, deps);
  const serialised = JSON.stringify(events[0].props);
  assert.ok(!serialised.includes("Nimal Perera"), "no customer name");
  assert.ok(!serialised.includes("4321"), "no card digits");
  assert.ok(!serialised.includes("Cinnamon Grand"), "no merchant name / raw text");
  assert.ok(typeof events[0].props.ocrChars === "number", "ocrChars count present");
  assert.equal(events[0].props.category, "Meals");
});

// ---- AC-07 bad input → 400 --------------------------------------------------
test("AC-07 unsupported content type → 400, no event", async () => {
  const { deps, events } = makeDeps();
  const bad = { ...goodInput, contentType: "application/pdf" };
  await assert.rejects(
    () => categorise(bad, deps),
    (err) => err instanceof CategoriserError && err.status === 400 && err.code === "bad_input"
  );
  assert.equal(events.length, 0);
});

// ---- AC-08 feature flag off -------------------------------------------------
test("AC-08 flag off → source disabled, no event, no OCR/LLM call", async () => {
  let ocrCalled = false, llmCalled = false;
  const { deps, events } = makeDeps({
    featureFlag: { isEnabled: async () => false },
    ocr: { read: async () => { ocrCalled = true; return MEAL_TEXT; } },
    llmClient: { classify: async () => { llmCalled = true; return { category: "Meals", confidence: 0.9 }; } },
  });
  const r = await categorise(goodInput, deps);
  assert.equal(r.source, "disabled");
  assert.equal(r.needsReview, true);
  assert.equal(events.length, 0);
  assert.equal(ocrCalled, false);
  assert.equal(llmCalled, false);
});
