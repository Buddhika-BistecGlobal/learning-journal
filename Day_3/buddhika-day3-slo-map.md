# BookSwap — SLI/SLO Map

> **Author:** Buddhika Amarasinghe
> **Context:** rolled out to 200 buildings; a tabloid feature lands next Sunday
> (expected 10× normal RPS, sustained ~4 hours). This maps every Day 2 / Day 3 NFR
> to a measurable SLI, an SLO target, and an error budget.

---

## 1. NFR inventory

| # | NFR (Day 2 + Day 3) | User-visible behaviour |
|---|---------------------|------------------------|
| N1 | Catalogue search: 99% < 800 ms over rolling 28 days, even at 10× RPS | "I search and results appear almost instantly, even on the busy Sunday." |
| N2 | Search stays useful when the cache is cold/unavailable | "Search still works (a bit slower) even if Redis is down." |
| N3 | Listing creation: 99.9% success; retryable without duplicate listings | "I can add a book and it (almost) never fails; if I retry I don't get two copies." |
| N4 | Listing creation succeeds even if email service is down | "Adding a book works even when digest emails are broken." |
| N5 | Auth: every endpoint except `/health` requires a valid JWT; tokens expire ≤ 1 h | "I must be signed in; a stolen token stops working within an hour." |
| N6 | Authorization/privacy: a member never sees another member's loan history or address/phone | "I can only ever see my own private data." |
| N7 | Detection: full outage of the listings endpoint pages on-call within 3 min | (Ops-visible) "We find out about a listings outage in minutes, not from Twitter." |
| N8 | Audit: every auth failure and every loan create/return logged with request ID + member ID | (Ops/compliance-visible) "We can reconstruct who borrowed/returned what, and every failed login." |
| N9 | Notifications: in-app within 2 s; email digest best-effort | "Borrow requests notify the owner almost immediately; the weekly email can be late." |
| N10 | Photo upload ≤ 5 MB JPEG/PNG, never stored in the app DB | "I can attach a photo; large/odd files are rejected cleanly." |
| N11 | Ops can confirm system health in < 5 minutes | (Ops-visible) "One dashboard tells me green/red fast." |

---

## 2. SLI / SLO table

> Each SLI is written so another engineer can paste the query and get a number.
> Sources: **AI** = Application Insights, **AML** = Azure Monitor Logs, **SB** = Service Bus metrics, **AFD** = Azure Front Door.

| # | SLI definition | Measurement source | SLO target | Window | Error budget |
|---|----------------|--------------------|-----------|--------|--------------|
| N1 | % of `GET /books` requests that return 2xx in < 800 ms | AI `requests` table | ≥ 99% | rolling 28 d | 1% (≈ 403 min of "slow/failed" if 28 d of traffic) |
| N2 | % of `GET /books` requests returning 2xx in < 1500 ms **while Redis is unavailable** (degraded SLO) | AI `requests` + `dependencies` (redis health) | ≥ 99% under 1500 ms during cache-down windows | per incident | n/a (degraded-mode target, not budgeted) |
| N3 | % of `POST /books` requests that succeed (2xx) | AI `requests` table | ≥ 99.9% | rolling 28 d | 0.1% (≈ 43 min/28 d) |
| N3b | Duplicate-listing rate from client retries (listings created with same Idempotency-Key > 1) | AML custom log `listing.duplicate` | = 0 | rolling 28 d | 0 — hard invariant |
| N4 | % of `POST /books` that succeed while ACS Email dependency is failing | AI `requests` filtered to email-outage windows | ≥ 99.9% (email outage must not affect it) | per incident | n/a |
| N5 | % of non-`/health` requests reaching the API without a valid JWT that are rejected with 401 | AI `requests` where `resultCode==401` vs unauthenticated attempts | 100% rejection (no unauthenticated 2xx) | continuous | 0 — security invariant |
| N6 | Count of responses where caller `memberId` ≠ resource owner/borrower and PII/loan data was returned | AML query over audit log + access checks | 0 | continuous | 0 — security invariant |
| N7 | Time from listings-endpoint availability test failing to on-call page sent | Azure Monitor availability test + alert action group | ≤ 3 min, 100% of outages | per incident | 0 — detection invariant |
| N8 | % of auth-failure and loan create/return events that have a log row with both `requestId` and `memberId` | AML `traces`/custom table coverage check | 100% | rolling 7 d | 0 — audit invariant |
| N9 | % of borrow-request in-app notifications delivered within 2 s of the event | AI custom metric `notify.latency_ms` | ≥ 95% < 2 s | rolling 7 d | 5% |
| N10 | % of photo uploads correctly accepted (≤5 MB JPEG/PNG) or rejected (413/415) — no 5xx | AI `requests` for `PUT /books/{id}/photo` | ≥ 99.5% | rolling 28 d | 0.5% |
| N11 | Time for an on-call to read green/red from the health dashboard | manual / synthetic | < 5 min | per check | n/a (UX of the dashboard) |

**Why these targets (not "99.9 everything"):**
- **Search (N1) is 99%, not 99.9%** — it is read-only and a single slow search is a minor annoyance; spending engineering effort to chase 99.9% here is not worth it. The Sunday spike is exactly when a looser-but-honest target matters.
- **Listing creation (N3) is 99.9%** — a failed *write* loses user content and trust, so it earns a tighter budget than search.
- **Security/audit/detection (N5–N8) are invariants (0 budget)** — "a member must never see another member's address" is not a thing you spend 0.1% of the month violating. These are pass/fail, not budgeted.

---

## 3. Error budget policy

**Trigger:** an SLO's error budget for its window is exhausted (e.g. search N1 burns its 1% over 28 days, or listing N3 burns its 0.1%).

**What the team stops doing (concrete halt-and-fix):**
1. **Freeze all non-essential deploys to the affected service.** Only changes that *reduce* the burn (reliability fixes, rollbacks) ship until the budget recovers. Feature work for that service pauses.
2. **The next sprint's top priority becomes the reliability fix** that addresses the dominant burn cause (from the incident review), not new features.
3. For an **invariant breach** (N5/N6/N7/N8 — a real auth bypass, PII leak, missed page, or audit gap), it is treated as a **Sev1 incident immediately**, not a budget conversation: stop, contain, and fix before anything else.

**Who owns the decision:** the **service's tech lead** owns declaring "budget exhausted → freeze," in consultation with the **on-call/SRE**. The **engineering manager** can authorise an exception (e.g. a security patch must still ship during a freeze). The decision and rationale are recorded in the incident channel.

---

## 4. Out of budget right now

**The SLO I would bet we cannot meet today is N1 — search 99% < 800 ms at 10× RPS — because the design's 800 ms search target was validated for a *single building of 5,000 books with a warm cache*, and we have never load-tested 200 buildings at 10× RPS with a cold Redis (N2 path); the moment Front Door/App Service autoscale lags the Sunday spike, p95 search latency will blow past 800 ms until scaling catches up.** The honest mitigation is a pre-Sunday load test plus pre-scaled instances, not faith in autoscale reacting in time.
