# Intern Onboarding — Deliverables Index

> **Author:** Buddhika Amarasinghe (`buddhika@bistecglobal.com`)
> A five-day TL-track onboarding progressing from requirements → API design → reliability
> → architecture → spec-driven AI development. Every diagram is rendered, every spec is
> validated/tested where tooling allows — see the **Verified** column.

## The thread across the week
Three products carry the arc: **LearnLanka** (Day 1 requirements), **BookSwap**
(Day 2 design → Day 3 hardened for scale), and **GreenChit** (Day 4 architecture →
Day 5 a new AI feature). Each day builds on the last.

| Day | Theme | Product | Passing bar | Status |
|----|-------|---------|-------------|--------|
| [1](Day_1/) | Requirements & ambiguity | LearnLanka | 75% | ✅ complete |
| [2](Day_2/) | API design, storage & cache | BookSwap | 75% | ✅ complete |
| [3](Day_3/) | SLOs, reliability, security, observability | BookSwap @ scale | 75% | ✅ complete |
| [4](Day_4/) | C4 diagrams, ADRs, trade-offs | GreenChit | 75% | ✅ complete |
| [5](Day_5/) | Spec-driven AI implementation | GreenChit feature | 75% | ✅ complete |

---

## Day 1 — LearnLanka: Requirements & Ambiguity
*Turn a vague brief into a requirements doc, C4 context diagram, user stories, and an ambiguity log.*

| Deliverable | File | Verified |
|---|---|---|
| Requirements document | [Day_1/buddhika-day1-requirements.md](Day_1/buddhika-day1-requirements.md) | 7 measurable NFRs, 10 assumptions, 8 out-of-scope |
| C4 Context diagram (PNG) | [Day_1/buddhika-day1-context-diagram.png](Day_1/buddhika-day1-context-diagram.png) | rendered |
| C4 Context diagram (source + notes) | [.drawio](Day_1/buddhika-day1-context-diagram.drawio) · [.md](Day_1/buddhika-day1-context-diagram.md) | |
| User stories | [Day_1/buddhika-day1-user-stories.md](Day_1/buddhika-day1-user-stories.md) | 8 stories, honest INVEST checks |
| Ambiguity hunt log | [Day_1/buddhika-day1-ambiguity-log.md](Day_1/buddhika-day1-ambiguity-log.md) | 13 ambiguities (6 high-priority) |

## Day 2 — BookSwap: API Design, Storage & Cache
*REST contract, storage/cache/queue decisions, C4 container diagram, and a mock smoke test.*

| Deliverable | File | Verified |
|---|---|---|
| OpenAPI 3.1 spec | [Day_2/buddhika-day2-bookswap-openapi.yaml](Day_2/buddhika-day2-bookswap-openapi.yaml) | ✅ `swagger-cli validate` — valid |
| Storage / cache / queue memo | [Day_2/buddhika-day2-storage-decisions.md](Day_2/buddhika-day2-storage-decisions.md) | cache-aside pseudocode, DLQ failure mode |
| Container diagram (PNG + source) | [.png](Day_2/buddhika-day2-container-diagram.png) · [.drawio](Day_2/buddhika-day2-container-diagram.drawio) | rendered; sync vs async distinct |
| Mock smoke test report | [Day_2/buddhika-day2-mock-report.md](Day_2/buddhika-day2-mock-report.md) | ✅ 5/5 tests on live Prism mock |
| Zipped repo | [Day_2/buddhika-day2-bookswap-design.zip](Day_2/buddhika-day2-bookswap-design.zip) | |

## Day 3 — BookSwap @ Scale: Quality Attributes
*SLO map, reliability runbook, security review (+ real ZAP scan), observability plan.*

| Deliverable | File | Verified |
|---|---|---|
| NFR → SLI/SLO map | [Day_3/buddhika-day3-slo-map.md](Day_3/buddhika-day3-slo-map.md) | 11 NFRs, error-budget policy |
| Reliability runbook | [Day_3/buddhika-day3-reliability-runbook.md](Day_3/buddhika-day3-reliability-runbook.md) | 3 failures, concrete timeouts/retries |
| Security review | [Day_3/buddhika-day3-security-review.md](Day_3/buddhika-day3-security-review.md) | 7 categories, BOLA + PII findings |
| Threats register | [Day_3/buddhika-day3-threats.csv](Day_3/buddhika-day3-threats.csv) | 11 entries with owners |
| ZAP baseline report | [Day_3/buddhika-day3-zap-baseline-report.html](Day_3/buddhika-day3-zap-baseline-report.html) | ✅ real scan: FAIL 0 / WARN 2 / PASS 65 |
| Observability plan | [Day_3/buddhika-day3-observability-plan.md](Day_3/buddhika-day3-observability-plan.md) | every SLO → alert |
| Zipped repo | [Day_3/buddhika-day3-bookswap-quality.zip](Day_3/buddhika-day3-bookswap-quality.zip) | |

## Day 4 — GreenChit: Architecture Design Pack
*C4 container + component diagrams, a submit/approve sequence diagram, 4 ADRs, trade-off table + design review.*

| Deliverable | File | Verified |
|---|---|---|
| Design pack (context + container + component) | [Day_4/buddhika-day4-greenchit-design.md](Day_4/buddhika-day4-greenchit-design.md) | embedded PNGs, reading order |
| Trade-offs + design review | [Day_4/buddhika-day4-trade-offs-and-review.md](Day_4/buddhika-day4-trade-offs-and-review.md) | 12/12 cells justified |
| Diagrams + ADRs + sequence | [Day_4/buddhika-day4-greenchit-design.zip](Day_4/buddhika-day4-greenchit-design.zip) | ✅ Mermaid rendered (happy + error); 4 ADRs |
| Zipped repo | [Day_4/buddhika-day4-greenchit-design.zip](Day_4/buddhika-day4-greenchit-design.zip) | `diagrams/ adrs/ trade-offs/` |

## Day 5 — GreenChit: Receipt Categoriser (spec-driven AI)
*Sharp spec + acceptance criteria, AI-driven implementation with a captured session, spec review.*

| Deliverable | File | Verified |
|---|---|---|
| Feature spec (7 sections) | [Day_5/buddhika-day5-receipt-categoriser-spec.md](Day_5/buddhika-day5-receipt-categoriser-spec.md) | complete contract, open questions |
| Acceptance criteria | [Day_5/buddhika-day5-receipt-categoriser-acceptance.md](Day_5/buddhika-day5-receipt-categoriser-acceptance.md) | 8 ACs incl. PII + fallback |
| Implementation + AI session | [Day_5/buddhika-day5-receipt-categoriser.zip](Day_5/buddhika-day5-receipt-categoriser.zip) | ✅ `node --test` → 8/8 pass; honest deviation captured |
| Spec review | [Day_5/buddhika-day5-spec-review.md](Day_5/buddhika-day5-spec-review.md) | 8 smells classified, 1 disagreement |

---

## How to re-verify (tooling used)
- **OpenAPI:** `npx @apidevtools/swagger-cli validate Day_2/buddhika-day2-bookswap-openapi.yaml`
- **Mock + smoke:** `npx @stoplight/prism-cli mock <spec> --port 4010` then curl the endpoints
- **ZAP:** `docker run --rm -v <dir>:/zap/wrk ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:4010 -r report.html`
- **Mermaid PNG:** `npx -y @mermaid-js/mermaid-cli -i <file>.mmd -o <file>.png -t neutral -b white -s 2`
- **C4 PNGs:** `python Day_N/render_*.py` (Pillow)
- **Day 5 tests:** `cd Day_5/buddhika-day5-receipt-categoriser && node --test`

## Honesty notes (carried in each day's docs)
- PNG diagrams are **script/CLI-rendered**, not hand-exported from draw.io — `.drawio`/`.mmd`
  sources are kept in sync manually; re-render if you edit them.
- Day 4 design review and Day 5 spec review use a **representative "Pair B"** since the
  cohort-pairing step isn't available solo — labelled as such, not presented as a real peer.
- Day 5: I acted as **both** spec author and the AI coding agent; the captured deviation is a
  genuine agent failure mode, not airbrushed.
- Scratch dirs `C:\mmtmp` and `C:\zaptmp` were used for rendering/scanning and are
  sandbox-protected from deletion — remove manually if desired.
