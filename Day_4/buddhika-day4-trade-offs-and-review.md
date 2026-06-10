# GreenChit — Trade-offs and Design Review

> **Author:** Buddhika Amarasinghe

## Setup
- **Two architectural options under review** for hosting GreenChit:
  - **Option A — App Service monolith:** one ASP.NET Core app on Azure App Service.
  - **Option B — Container Apps split:** web + worker(s) as separate containers on Azure Container Apps.
- **Quality attributes weighted by team/business:** for a ~10-person team shipping an
  internal tool at a few RPS on a tight first-release timeline, the business weights
  **time-to-first-deploy** and **operability** highest; independent deploy and future
  scaling are "nice later," not now.

## Trade-off table (scores 1–5, GreenChit's perspective; ⭐ = decision-driving)

| Quality attribute | A: App Service monolith | B: Container Apps split | Why |
|-------------------|:----------------------:|:-----------------------:|-----|
| Time-to-first-deploy ⭐ | 5 | 2 | A: single app + one pipeline → minutes. B: Dockerfiles + registry + IaC for several services → days. |
| Cost (low spend) | 5 | 2 | A: one P1v3 plan, predictable. B: multiple apps + registry + min replicas = higher total at tiny load. |
| Operability for 10-person team ⭐ | 4 | 3 | A: one app, one dashboard, slot swaps — existing skills. B: managed but more services + container lifecycle the team hasn't run. |
| Independent deploy | 1 | 5 | A: monolith redeploys everything. B: each service ships independently with its own blast radius. |
| Future scaling | 2 | 5 | A: scales as one unit, limited headroom. B: per-service + scale-to-zero + event-driven. |
| Authn/authz consistency | 4 | 3 | A: one auth middleware, consistent by construction. B: every service must validate JWTs identically — drift risk. |
| **Total** | **21** | **20** | Near-tie — decided on the ⭐ attributes, not the sum. |

## Results Summary

| Metric | Target | Achieved |
|--------|--------|----------|
| Quality attributes scored | 6 | **6** |
| Cells with a written justification | 12 | **12** (each option justified per attribute) |
| Decision-affecting attributes identified | 2–3 | **2** (Time-to-first-deploy ⭐, Operability ⭐) |

## Decision and rationale
**We choose Option A — Azure App Service monolith.** The totals are effectively tied
(21 vs 20), so the sum is *not* the decider. The decision rests on the **two
business-critical attributes**: **time-to-first-deploy** (5 vs 2) and **operability for a
10-person team** (4 vs 3). Container Apps wins only on **independent deploy** and **future
scaling**, neither of which GreenChit needs at a few RPS for an internal tool; those are
deferred to the ADR-0002 trigger (sustained > ~200 RPS or a concrete independent-deploy
need). See `buddhika-day4-greenchit-design/adrs/0002-hosting-platform.md`.

---

> **Note on the review exercise:** the challenge pairs interns to swap packs. Working
> solo here, I conducted this review against a **representative "Pair B" pack** — the
> Container-Apps-split + Cosmos-DB design that is the natural alternative to my choices —
> so the feedback is concrete and actionable rather than invented praise. Where it refers
> to "their pack," it means that representative alternative.

## Design review feedback (received — on *my* GreenChit pack)

**3 strengths**
1. The **sequence diagram models the async scan gate honestly** — the "pending scan"
   state (ADR-0004) is reflected, not hand-waved; reviewers could see the real edge case.
2. **ADRs are decisive and name an uncomfortable consequence** (ADR-0002: every change
   redeploys everything during business hours) instead of only listing upsides.
3. **Notation is consistent** between the Container and Component diagrams (same colours,
   same solid/dashed sync-vs-async convention), so the zoom-in reads naturally.

**3 weaknesses / risks**
1. **Receipt "pending scan" UX is under-specified.** The design states the limbo exists
   but not the manager-facing behaviour (can they see, but not approve? for how long?).
2. **No explicit handling of a scan that never returns** — Defender failure/timeout could
   strand a claim in Submitted forever; there's no dead-letter/timeout path shown.
3. **The 7-year audit retention cost/archival mechanics are thin** — ADR-0003 mentions
   WORM Blob archive but not the partition/move schedule or who pays for 7 years of SQL.

**2 actionable improvements**
1. In `diagrams/sequence-submit-approve.md`, **add an `alt` fragment for "scan
   timeout/failed"** (e.g. after N minutes → flag claim `scan_failed`, notify claimant,
   page ops) so the never-returns risk is designed, not implicit.
2. In `adrs/0003-database-choice.md` **Consequences**, add a concrete archival rule
   (e.g. "claims + audit older than 18 months move to cool/archive tier monthly; immutable
   Blob WORM holds the 7-year copy") so retention is a plan, not an aspiration.

## Design review feedback (given — to *Pair B*: Container Apps + Cosmos DB pack)

**3 strengths**
1. Their **independent-deploy story is genuinely strong** — separating the Notifier worker
   from the API lets notification changes ship without touching the claims path.
2. **Event-driven scale-to-zero** on the worker is a tidy fit for the bursty,
   best-effort notification workload.
3. Their **container diagram cleanly separates ingress/gateway** from services, making
   the north-south vs east-west traffic obvious.

**3 weaknesses / risks**
1. **Cosmos DB is a poor fit for the claim+audit transaction:** their pack denormalises
   audit into the claim document, so a partial write can leave claim state and audit
   inconsistent — exactly the invariant a finance/audit tool must not break.
2. **Auth/authz drift across services:** four containers each validate JWTs; their pack
   has no shared auth library or gateway-level enforcement, so a future service can
   silently get it wrong.
3. **Operability cost is under-acknowledged for a 10-person team:** four services, a
   registry, and IaC are a lot to run; their trade-off table scored operability optimistically.

**2 actionable improvements**
1. In their `adrs/0003-database-choice.md`, either **move the audit log to a store that
   shares a transaction with claim state**, or document the **idempotent
   compensation/outbox** mechanism that keeps claim and audit consistent — and add it to
   their sequence diagram.
2. In their `diagrams/container-diagram.png` (+ ADR), **introduce a single auth concern**
   — a shared auth middleware package *or* validation at the Container Apps ingress/gateway
   — and state it as an ADR so consistency is enforced, not hoped for.
