# Day 3 Challenge — BookSwap Quality Attributes

## Challenge Overview

BookSwap is now being trialled across 200 apartment buildings instead of one, and the team has just learned that a tabloid will feature it next Sunday. Take yesterday's design and produce a quality attribute plan: SLO targets, a reliability runbook, a security review, and an observability plan. The code does not change today — your job is to prove the design is ready (or surface what would have to change).

- **Time Allocation:** 3 hours (during session)
- **Difficulty:** Beginner-Intermediate

---

## Business Requirements

### Functional Requirements

- All Day 2 functional requirements still apply.
- The system must keep accepting new listings during a Sunday traffic spike (10× normal RPS, sustained 4 hours).
- Search results must remain useful even when the cache is cold or unavailable.
- A member must never see another member's loan history or address.
- Operations team must be able to confirm in under 5 minutes whether the system is healthy.

### Non-Functional Requirements

- **Catalogue search:** 99% of requests under 800 ms over a rolling 28 days, even at 10× normal RPS.
- **Listing creation:** 99.9% success rate; failed attempts must be retryable without creating duplicate listings.
- **Authentication:** every endpoint except `/health` requires a valid JWT; tokens expire within 1 hour.
- **Detection:** a complete outage of the listings endpoint must page the on-call within 3 minutes.
- **Audit:** every authentication failure and every loan creation/return is logged with request ID and member ID.

### Technical Constraints

- Continue to use Azure App Service, Azure SQL, Azure Cache for Redis, Azure Service Bus, Azure Blob Storage.
- Observability stack: Azure Application Insights for traces and metrics, Azure Monitor Logs for logs.
- Secrets: Azure Key Vault, never `.env` files in production.
- WAF / rate limiting: Azure Front Door in front of App Service.
- No new vendors may be introduced today — work within the Azure stack.

---

## Deliverables

### 1. NFR-to-SLI/SLO Map (25 points)

**File:** `{your-name}-day3-slo-map.md`

**Required Sections:**

```markdown
# BookSwap — SLI/SLO Map

## 1. NFR inventory
| # | NFR (from Day 2) | User-visible behaviour |
|---|------------------|------------------------|

## 2. SLI / SLO table
| # | SLI definition | Measurement source | SLO target | Window | Error budget |
|---|----------------|---------------------|------------|--------|--------------|

## 3. Error budget policy
- What the team stops doing when the budget is exhausted
- Who owns the decision

## 4. Out of budget right now
- One sentence: which SLO would you bet you cannot meet today and why
```

**Evaluation Criteria:**

- Every Day 2 NFR is mapped to at least one SLI (5 pts)
- Each SLI is unambiguous — another engineer could query it (5 pts)
- SLO targets and windows match the business risk, not arbitrary "99.9 everything" (5 pts)
- Error budget policy names a concrete halt-and-fix behaviour (5 pts)
- "Out of budget right now" answer is honest, not aspirational (5 pts)

---

### 2. Reliability Runbook for Three Failures (25 points)

**File:** `{your-name}-day3-reliability-runbook.md`

**Required Content:**

```markdown
# BookSwap — Reliability Runbook v0.1

## Failure 1: Azure SQL primary unavailable for 5 minutes
### What the user sees
### Detection
### Mitigation in design (timeouts, retries, circuit breaker, fallback)
### Manual response (who is paged, what they do)
### Post-incident actions

## Failure 2: Azure Cache for Redis is down
### What the user sees
### Detection
### Mitigation in design
### Manual response
### Post-incident actions

## Failure 3: Sunday tabloid spike — 10× sustained traffic
### What the user sees
### Detection
### Mitigation in design (autoscale, queue depth, throttling)
### Manual response
### Post-incident actions
```

**Code Requirements:**

- Each failure has a concrete timeout/retry/backoff configuration (numbers, not "configure retries")
- At least one failure uses an idempotency key as part of the mitigation
- Each failure names a specific Azure metric/alert that detects it

**Evaluation Criteria:**

- Each failure has a clearly described user-visible symptom (5 pts)
- Detection uses a specific, queryable signal (5 pts)
- Mitigations are concrete (numbers, patterns, fallbacks) (5 pts)
- Manual response identifies who and how, not vague "check things" (5 pts)
- Post-incident actions create a follow-up worth doing (5 pts)

---

### 3. Security Review of the API (25 points)

**Repository Structure:**

```text
bookswap-quality/
├── slo/
│   └── slo-map.md
├── reliability/
│   └── runbook.md
├── security/
│   ├── review.md
│   ├── threats.csv
│   └── zap-baseline-report.html
├── observability/
│   ├── plan.md
│   └── alerts.yaml
└── README.md
```

**Required Reviews:**

| Category | Question | Finding | Severity (H/M/L) | Mitigation |
|----------|----------|---------|------------------|------------|
| Authn | Is every non-public endpoint protected by JWT? | ... | ... | ... |
| Authz | Does every `/{id}`-shaped endpoint check object ownership? | ... | ... | ... |
| Injection | Are all DB queries parameterised? | ... | ... | ... |
| Secrets | Where are connection strings stored? | ... | ... | ... |
| Transport | Is TLS enforced at Front Door? | ... | ... | ... |
| Rate limit | Are auth and write endpoints rate-limited? | ... | ... | ... |
| PII | What PII appears in responses, logs, or queues? | ... | ... | ... |

**Minimum Findings:**

- [ ] At least one Broken Object Level Authorization scenario is described
- [ ] At least one PII leak via logs or telemetry is identified
- [ ] At least one missing rate-limit on a sensitive endpoint
- [ ] OWASP ZAP baseline scan against the Prism mock attached as HTML
- [ ] A `threats.csv` lists each finding with category, severity, and mitigation owner

**Evaluation Criteria:**

- All 7 categories addressed with specific findings (5 pts)
- At least one BOLA scenario described with a concrete URL and request (5 pts)
- ZAP baseline scan attached and at least one finding from it discussed (5 pts)
- Severities reflect realistic impact — not all "High" (5 pts)
- Mitigations are implementable (specific config or code, not "improve security") (5 pts)

---

### 4. Observability Plan and Alert Proposal (25 points)

**File:** `{your-name}-day3-observability-plan.md`

**Required Tests/Validations:**

| # | Signal type | Source | What it answers | Sample query / metric name |
|---|-------------|--------|-----------------|----------------------------|
| 1 | Metric | Application Insights | Search latency p95 | `requests \| summarize percentile(duration, 95) by bin(timestamp, 1m)` |
| 2 | Metric | App Insights | Listing creation success rate | ... |
| 3 | Log | App Insights traces | Authn failures with member ID | `traces \| where customDimensions.event == "auth.failed"` |
| 4 | Trace | App Insights | Slow request breakdown across DB and Redis | ... |
| 5 | Metric | Service Bus | Email digest queue depth | ... |

**Report Format:**

```markdown
# BookSwap — Observability Plan

## Setup
- Logs: Azure Monitor Logs — schema, retention, redaction rules
- Metrics: Azure Application Insights — request, dependency, custom
- Traces: Application Insights distributed tracing — sample rate

## Results Summary
| Metric | Target | Achieved |
|--------|--------|----------|
| SLOs covered by an alert | 100% | ? |
| Alerts with a clear runbook link | 100% | ? |
| Dashboards for ops | 1 health, 1 business | ? |

## Alert proposal
| Alert | Condition | Severity | Notification | Runbook |
|-------|-----------|----------|--------------|---------|
| Search SLO burn | error rate > 1% over 5 min | Sev2 | Pager + Teams | reliability/runbook.md#search |

## What we are deliberately NOT alerting on
1. ...
2. ...
```

**Evaluation Criteria:**

- All three pillars (logs, metrics, traces) are present with at least 2 entries each (5 pts)
- Every SLO has at least one alert that protects it (5 pts)
- Alert severities, channels, and runbook links are filled in (5 pts)
- "What we are NOT alerting on" shows discipline — not everything is a page (5 pts)
- Plan respects PII — clearly states what is redacted before logging (5 pts)

---

## Submission Guidelines

### File Naming Convention

```text
{your-name}-day3-slo-map.md
{your-name}-day3-reliability-runbook.md
{your-name}-day3-security-review.md
{your-name}-day3-threats.csv
{your-name}-day3-zap-baseline-report.html
{your-name}-day3-observability-plan.md
{your-name}-day3-bookswap-quality/  (zipped repository)
```

### Submission Checklist

- [ ] SLO map covers every Day 2 NFR
- [ ] Reliability runbook addresses 3 named failures with numbers
- [ ] Security review covers all 7 categories with severities
- [ ] ZAP baseline scan attached
- [ ] Observability plan has alerts mapped to SLOs

---

## Scoring Guide

| Grade | Score | Description |
|-------|-------|-------------|
| Exceptional | 90–100 | Plan reads like a small SRE handover; alerts are specific; security findings include real BOLA paths and PII concerns |
| Proficient | 75–89 | SLOs are measurable; runbook is concrete; security review surfaces real issues; observability plan ties to SLOs |
| Developing | 60–74 | SLOs vague; runbook generic; security review surface-level; alerts not mapped to SLOs |
| Beginning | <60 | "99.9% availability" with no measurement; runbook is "page someone"; no security findings; observability is "we will use App Insights" |

**Passing Score:** 75%

---

## Hints and Tips

### Define an SLI in plain language first, then code it

```text
SLI: of all /books search requests in the last 28 days, the percentage that returned 2xx in under 800 ms
Source: Application Insights `requests` table
Target: >= 99%
```

```kusto
// Azure Monitor Log Analytics / Application Insights
requests
| where timestamp > ago(28d)
| where name == "GET /books"
| summarize
    good = countif(success == true and duration < 800),
    total = count()
| extend sli = 100.0 * good / total
```

### Retry with exponential backoff and a maximum

```javascript
// Pseudocode — retry only on transient errors (5xx, network)
async function callWithRetry(fn, { tries = 3, baseMs = 200, capMs = 2000 } = {}) {
  for (let i = 0; i < tries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (!isTransient(err) || i === tries - 1) throw err;
      const sleep = Math.min(capMs, baseMs * 2 ** i) + Math.random() * 100;
      await new Promise(r => setTimeout(r, sleep));
    }
  }
}
```

### A quick OWASP ZAP baseline scan against the mock

```bash
docker run --rm -t \
  -v "$PWD:/zap/wrk" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:4010 \
                  -r zap-baseline-report.html
# Open zap-baseline-report.html in your browser. Pick at least one
# finding to discuss in your security review, even if it's a false positive.
```
