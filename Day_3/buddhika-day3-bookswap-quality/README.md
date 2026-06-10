# BookSwap — Quality Attribute Plan (Day 3)

> **Author:** Buddhika Amarasinghe
> BookSwap has scaled from 1 to **200 buildings** and a tabloid feature lands next
> Sunday (expected **10× RPS for ~4 hours**). The code does not change today — this
> repo proves the Day 2 design is ready for that load, or surfaces what must change.

## Repository layout

```
buddhika-day3-bookswap-quality/
├── slo/
│   └── slo-map.md              # every NFR -> SLI -> SLO -> error budget
├── reliability/
│   └── runbook.md              # 3 named failures with concrete numbers
├── security/
│   ├── review.md               # 7-category review + BOLA + PII findings
│   ├── threats.csv             # findings: category, severity, owner, mitigation
│   └── zap-baseline-report.html# real OWASP ZAP baseline scan of the Prism mock
├── observability/
│   ├── plan.md                 # logs/metrics/traces + alerts mapped to SLOs
│   └── alerts.yaml             # machine-readable alert rules
└── README.md
```

(The same documents are also at the `Day_3/` top level under the
`buddhika-day3-*` submission naming convention.)

## How to read this in 5 minutes (ops handover)

1. **`slo/slo-map.md`** — what "healthy" means in numbers, and the one SLO we honestly
   bet we cannot meet Sunday without a pre-scale + load test (search at 10× RPS).
2. **`reliability/runbook.md`** — when SQL dies, Redis dies, or the spike hits: exact
   timeouts, retry/backoff, circuit-breaker thresholds, idempotency keys, who is paged.
3. **`security/review.md` + `threats.csv`** — two launch-blockers (a **BOLA** on
   loan-history endpoints and **member email in telemetry**), plus rate-limit/TLS
   hardening; `zap-baseline-report.html` is the attached scan.
4. **`observability/plan.md` + `alerts.yaml`** — every SLO has an alert, every alert
   links to a runbook section, and a short list of what we deliberately do **not** page on.

## Reproduce the ZAP scan

```bash
# Terminal 1 — mock the Day 2 API (from the Day_2 folder)
npx @stoplight/prism-cli mock buddhika-day2-bookswap-openapi.yaml --host 0.0.0.0 --port 4010

# Terminal 2 — baseline scan from this security/ folder
docker run --rm -t -v "$PWD:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:4010 -r zap-baseline-report.html -I
```

## Headline conclusion
The design is **mostly ready**, with three must-fix items before Sunday:
**(1)** pre-scale + load-test the search path at 10× RPS (the at-risk SLO),
**(2)** fix the BOLA on `/books/{id}/loans` and `/loans/{id}`,
**(3)** strip member email/PII from telemetry. Everything else is hardening with a clear owner in `threats.csv`.
