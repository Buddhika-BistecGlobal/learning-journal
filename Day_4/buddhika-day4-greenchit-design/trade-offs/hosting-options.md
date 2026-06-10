# GreenChit — Hosting Options Trade-off

Referenced by **ADR-0002**. Scores are 1 (poor) – 5 (excellent) **from GreenChit's
point of view** (10-person team, internal tool, few RPS, tight first release).

| Quality attribute | A: App Service monolith | B: Container Apps split | Why (per option) |
|-------------------|:----------------------:|:-----------------------:|------------------|
| **Time-to-first-deploy** ⭐ | **5** | **2** | **A:** one ASP.NET app, `az webapp up` + a single pipeline → running in minutes. **B:** needs Dockerfiles, a container registry, Bicep/IaC for several services and ingress → days before the first green deploy. |
| **Cost (low spend)** | **5** | **2** | **A:** a single P1v3 plan hosts the web app + Functions; predictable, low, easy to reason about. **B:** multiple container apps + registry + (for latency) non-zero min replicas + more infra to run = higher total cost and more billing surfaces at this tiny load. |
| **Operability for a 10-person team** ⭐ | **4** | **3** | **A:** one app, one App Insights resource, slot-swap releases — within the team's existing skills. **B:** managed, but more services to watch, container lifecycle/registry to manage, and ops patterns the team hasn't used. |
| **Independent deploy** | **1** | **5** | **A:** monolith — any change redeploys everything (the uncomfortable consequence in ADR-0002). **B:** each service ships on its own cadence with its own blast radius. |
| **Future scaling** | **2** | **5** | **A:** scales as one unit; limited horizontal headroom. **B:** per-service horizontal scale, scale-to-zero, event-driven scaling on queue depth. |
| **Authn/authz consistency** | **4** | **3** | **A:** one codebase = one auth middleware, consistent by construction. **B:** every service must validate JWTs identically; risk of drift unless a shared library/gateway is enforced. |
| **Total** | **21** | **20** | Near-tie — see the decision note below. |

## Decision note (the scoring is an argument, not a calculator)

Totals are effectively tied (**21 vs 20**), so we explicitly **do not** let the sum
decide. We weight by what the business cares about *for this tool, now*:

- **Time-to-first-deploy (⭐)** and **Operability for a 10-person team (⭐)** are the two
  decisive attributes — a small team must ship an internal release quickly and run it
  with the skills it already has. On both, **App Service wins clearly (5 vs 2, 4 vs 3)**.
- The attributes where **Container Apps wins — Independent deploy and Future scaling —**
  are **not** GreenChit priorities at a few RPS for an internal tool. They become
  relevant only at the ADR-0002 trigger (sustained > ~200 RPS or a real independent-deploy
  need), at which point we revisit with a superseding ADR.

**Chosen: Option A — Azure App Service monolith.** Driven by time-to-first-deploy and
operability, accepting weak independent-deploy/scaling as a deliberate, revisitable trade.
