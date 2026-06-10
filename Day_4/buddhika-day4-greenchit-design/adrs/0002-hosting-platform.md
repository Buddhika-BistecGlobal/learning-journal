# ADR 0002: Host GreenChit on Azure App Service (single web app)

## Status
Accepted (date: 2026-06-10)

## Context
- **Forces:** a small (~10-person) team with limited containers/IaC experience; an
  internal tool with modest load (peak < ~50 staff submissions/hour, well under a few
  RPS); a strong BISTEC preference for Azure-native managed services; a need to ship a
  usable internal release quickly.
- **Constraints:** Azure hosting is mandated (App Service *or* Container Apps — see the
  trade-off table in `trade-offs/hosting-options.md`); 99.9% availability during business
  hours (08:00–19:00 SLST, Mon–Fri).
- **What we don't yet know:** whether GreenChit later grows features (travel, advances)
  that justify independent deploy/scale of separate services.

## Decision
We host GreenChit as a **single ASP.NET Core web app on Azure App Service (Premium v3,
P1v3)** with **deployment slots** (staging + production) for zero-downtime swaps, and the
**Notifier** as a lightweight Azure Functions app on the same plan. Autoscale: 1–3
instances, scale out at CPU > 70% for 10 min. We revisit a split into independently
deployed services in a future ADR **only when** sustained load exceeds ~200 RPS *or* a
concrete independent-deploy need appears.

## Consequences
- **Easier:** fastest time-to-first-deploy, one CI/CD pipeline, one App Insights resource,
  simple slot-swap releases — the team is productive on day one.
- **Harder (genuinely uncomfortable):** **every change redeploys the whole app.** A
  one-line fix to the finance CSV export forces a redeploy of the claims-submission path
  too — during the 08:00–19:00 business window that threatens the 99.9% SLO, so risky
  changes get squeezed into a narrow off-hours slot. We accept slower, more cautious
  releases as the price of simplicity.
- **Different:** the team will not build container/Kubernetes muscle inside this project
  (mitigation: a separate spike/PoC to cross-train, tracked outside this repo).

## Alternatives considered
- **Azure Container Apps (split web + workers):** rejected for v1 — the velocity hit from
  container build tooling + IaC + multi-service ops outweighs the scaling/independent-deploy
  benefit at this load (it wins only on *Independent deploy* and *Future scaling* in the
  trade-off table, which the business does not prioritise for a 6-week internal tool).
- **Azure Functions–only (no always-on web app):** rejected — cold starts and the
  long-tail latency of receipt-heavy submit requests jeopardise the 1.5 s p95 submit SLO,
  and a consumption plan complicates the always-available business-hours requirement.
