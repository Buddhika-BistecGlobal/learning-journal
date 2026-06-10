# BookSwap — Observability Plan

> **Author:** Buddhika Amarasinghe
> **Stack (constraint):** Azure **Application Insights** (metrics + distributed traces),
> **Azure Monitor Logs** (logs). No new vendors. Every SLO in
> `buddhika-day3-slo-map.md` must be protected by at least one alert here.

---

## Setup

### Logs — Azure Monitor Logs
- **Schema:** structured JSON log lines → `traces` / custom tables. Every log line carries `requestId` (W3C `traceparent`), `memberId` (Entra `oid`), `route`, `resultCode`, `event` (e.g. `auth.failed`, `loan.created`, `loan.returned`).
- **Audit coverage (N8):** `auth.failed`, `loan.created`, `loan.returned` are emitted as explicit events with `requestId` + `memberId` — 100% required.
- **Retention:** 90 days hot for app logs; audit events exported to a separate, longer-retention (e.g. 1 year, immutable) table for compliance.
- **Redaction rules (PII):** an App Insights **TelemetryProcessor** strips `authorization`, `email`, `phone`, `address` from all telemetry **before egress**. We log **`memberId`, never email**. Request bodies and the `Authorization` header are **never** logged. (See security review §3.)

### Metrics — Application Insights
- Built-in `requests` (duration, resultCode, success, name) and `dependencies` (SQL, Redis, Service Bus, Blob, ACS).
- **Custom metrics:** `notify.latency_ms` (event→in-app delivery), `listing.duplicate` (idempotency-key reuse), `redis.error`.

### Traces — Application Insights distributed tracing
- W3C trace context propagated edge→API→SQL/Redis/Service Bus, so one `requestId` stitches a full request.
- **Sample rate:** 100% for **errors and dependencies > 1 s**; **adaptive/10%** for normal successful requests to control cost at 10× Sunday volume (errors are never sampled out).

---

## Signal catalogue (3 pillars, ≥2 each)

| # | Signal type | Source | What it answers | Sample query / metric name |
|---|-------------|--------|-----------------|----------------------------|
| 1 | Metric | App Insights | Search latency p95 (N1) | `requests \| where name=="GET /books" \| summarize percentile(duration,95) by bin(timestamp,1m)` |
| 2 | Metric | App Insights | Listing creation success rate (N3) | `requests \| where name=="POST /books" \| summarize sr=100.0*countif(success)/count() by bin(timestamp,5m)` |
| 3 | Metric | Service Bus | Notify/digest queue depth (N9) | `ActiveMessageCount` (namespace metric), alert > 10,000 |
| 4 | Log | App Insights `traces` | Auth failures with member ID (N5/N8) | `traces \| where customDimensions.event=="auth.failed" \| project timestamp, customDimensions.requestId, customDimensions.memberId` |
| 5 | Log | Azure Monitor Logs | Loan create/return audit completeness (N8) | `traces \| where customDimensions.event in ("loan.created","loan.returned") \| summarize cnt=count(), withIds=countif(isnotempty(customDimensions.memberId) and isnotempty(customDimensions.requestId))` |
| 6 | Trace | App Insights | Slow-request breakdown across DB + Redis (N1/N2) | `dependencies \| where duration>500 \| summarize avg(duration) by type, target` |
| 7 | Trace | App Insights | End-to-end p95 by dependency for a slow `GET /books` | open the operation by `requestId`; inspect SQL vs Redis spans |
| 8 | Metric | Azure Monitor (availability test) | Is the listings endpoint up? (N7) | availability test on `POST /books` health probe → `availabilityResults` |

---

## Results Summary

| Metric | Target | Achieved |
|--------|--------|----------|
| SLOs covered by an alert | 100% | **100%** (N1–N11 each mapped below) |
| Alerts with a clear runbook link | 100% | **100%** (every alert links to `reliability/runbook.md#…`) |
| Dashboards for ops | 1 health, 1 business | **2** (Health: availability, p95, error rate, dependency health, queue depth; Business: listings/day, borrows, active loans, overdue) |

---

## Alert proposal (each maps to an SLO)

| Alert | SLO | Condition | Severity | Notification | Runbook |
|-------|-----|-----------|----------|--------------|---------|
| Listings endpoint down | N7 | availability test on `POST /books` fails 2 consecutive 1-min checks (≤ ~3 min) | **Sev1** | Pager + Teams | `reliability/runbook.md#failure-1` |
| Search SLO burn | N1 | p95 `GET /books` > 800 ms for 10 min, OR fast-burn: 2% error budget in 1 h | **Sev2** | Pager + Teams | `reliability/runbook.md#failure-3` |
| Listing success drop | N3 | `POST /books` success rate < 99.9% over 30 min | **Sev2** | Pager + Teams | `reliability/runbook.md#failure-1` |
| Duplicate listing detected | N3b | any `listing.duplicate` event in 5 min | **Sev3** | Teams | security/runbook (idempotency) |
| SQL dependency failing | N3/N1 | SQL dependency failure rate > 25% over 2 min | **Sev1** | Pager | `reliability/runbook.md#failure-1` |
| Redis degraded | N2 | Redis dependency failure rate > 50% over 3 min | **Sev2** | Pager | `reliability/runbook.md#failure-2` |
| Auth-failure spike | N5 | `auth.failed` count > 5× 7-day baseline over 5 min (possible attack) | **Sev2** | Pager + Security | security-review.md |
| Audit gap | N8 | loan/auth events with missing `memberId`/`requestId` > 0 over 1 h | **Sev3** | Teams | observability-plan.md |
| Notify latency breach | N9 | < 95% of `notify.latency_ms` under 2 s over 15 min | **Sev3** | Teams | `reliability/runbook.md#failure-3` |
| Queue backlog | N9 | Service Bus `ActiveMessageCount` > 10,000 for 10 min | **Sev3** | Teams | `reliability/runbook.md#failure-3` |
| App Service saturation | N1 | CPU > 75% for 5 min (autoscale early-warning) | **Sev3** | Teams | `reliability/runbook.md#failure-3` |

> Machine-readable version in `observability/alerts.yaml`.

---

## What we are deliberately NOT alerting on

1. **Single slow search requests / individual 4xx.** A lone request over 800 ms or a 404/422 is normal — we alert on the **SLO burn over a window**, not per-request, to avoid pager fatigue.
2. **Email digest delays / best-effort email failures.** Email is best-effort (N9 email path); a late or failed digest is a dashboard line, not a page. We only page on the **in-app** notify path and on queue backlog (which threatens in-app latency).
3. **Redis cache misses on their own.** A cache miss is expected (cold keys); we alert on Redis **dependency failures** (the cache being *down*), not on miss ratio in normal operation.
4. **CPU between 60–75% during the known Sunday window.** Expected under planned 10× load and handled by pre-scale/autoscale; alerting here would fire the whole event for no action.

---

## PII handling (restated for the reviewer)
Before any telemetry leaves the process, `authorization`, `email`, `phone`, and `address` are stripped; logs carry **`memberId`, never email**; request bodies and bearer tokens are never logged. Audit events store IDs sufficient to reconstruct who did what (N8) without storing contact PII.
