# BookSwap — Reliability Runbook v0.1

> **Author:** Buddhika Amarasinghe
> **Scope:** three named failures for the 200-building BookSwap platform.
> Conventions: all timeouts/retries below are concrete defaults the Day-3 developer
> can paste into config. "Page" = PagerDuty/Azure Monitor action group to on-call.

---

## Failure 1: Azure SQL primary unavailable for 5 minutes

### What the user sees
- **Reads** (`GET /books` search): if the requested page is **warm in Redis**, search still works (see Failure 2 inverse — cache shields reads). Cold pages return **503 "temporarily unavailable, retry"** with `Retry-After: 5`.
- **Writes** (`POST /books`, borrow/return): fail fast with **503**; the mobile app shows "Couldn't save — we'll keep your details, tap retry." No spinner-of-death because of the timeout below.

### Detection
- **Signal:** Application Insights **dependency failures** where `dependencyType == "SQL"` and `success == false`.
- **Query (AI):**
  ```kusto
  dependencies
  | where timestamp > ago(5m) and type == "SQL"
  | summarize failRate = 100.0*countif(success==false)/count()
  ```
- **Alert:** `SQL dependency failure rate > 25% over 2 min` → **Sev1 page**. Also the Azure SQL platform metric `connection_failed` spiking.

### Mitigation in design (timeouts, retries, circuit breaker, fallback)
- **Connection/command timeout:** SQL command timeout **5 s** (not the 30 s default) so a dead primary fails fast instead of piling up connections.
- **Retry (transient only):** **3 tries, exponential backoff base 200 ms, cap 2 s, ± jitter** — using the `callWithRetry` pattern; retry **only** on transient SQL error numbers (40197, 40501, 40613, 49918, 10928, 10929) and connection errors, never on a 4xx/constraint violation.
- **Circuit breaker:** open the SQL breaker after **5 consecutive failures**; while open, fail fast for **30 s** then half-open with a single probe. Prevents thundering-herd reconnects against a recovering primary.
- **Fallback:** serve **Redis-cached search pages** read-only during the outage (degraded SLO N2). Writes are **not** faked — they return 503 (never pretend a listing saved).
- **Idempotency:** because writes carry an **`Idempotency-Key`** (see Failure 3), the user retrying after the 5-minute outage **does not create a duplicate listing**.
- **HA reality:** Azure SQL has built-in HA with automatic failover (typically < 60 s); a 5-minute outage implies failover also struggled, so the above keeps us alive until it completes.

### Manual response (who is paged, what they do)
1. **On-call engineer** is paged (Sev1). Acknowledge within 5 min.
2. Check **Azure Service Health** for a SQL regional advisory; check the SQL resource's **failover/replica** state in the portal.
3. If no auto-failover, **manually trigger failover** to the geo/zone replica.
4. Post status to `#bookswap-incidents` and flip the public status page to "degraded".
5. Escalate to **DB owner / Azure support (Sev A)** if not recovering in 15 min.

### Post-incident actions
- Blameless post-mortem within 48 h; file follow-ups: (a) verify failover automation actually fires, (b) add a **chaos test** that kills the SQL connection in staging, (c) confirm the SQL breaker thresholds from real numbers, (d) check whether read-replica routing for search would have prevented user impact.

---

## Failure 2: Azure Cache for Redis is down

### What the user sees
- Search **still works** but **slower** — every `GET /books` now hits Azure SQL directly. Target degrades from < 800 ms (N1) to **< 1500 ms (N2 degraded SLO)**. No errors, just latency.
- Writes/borrows are unaffected (Redis is read-accelerator only, per Day 2 storage decisions — SQL is the source of truth).

### Detection
- **Signal:** AI dependency calls where `target` is the Redis host show `success == false` / timeouts; **Redis cache-miss ratio → ~100%**; SQL DTU/CPU rises as load shifts to it.
- **Query (AI):**
  ```kusto
  dependencies
  | where timestamp > ago(5m) and name has "redis"
  | summarize failRate = 100.0*countif(success==false)/count()
  ```
- **Alert:** `Redis dependency failure rate > 50% over 3 min` → **Sev2 page** (degraded, not down). Plus Azure Cache metric `Errors` / `Server Load > 90%`.

### Mitigation in design
- **Fail-open, never fail-closed:** the cache-aside read path **catches Redis errors and falls through to SQL** — Redis being down must never turn into a user-facing error.
  ```js
  let cached = null;
  try { cached = await redis.get(key); }       // 200 ms Redis timeout
  catch (e) { metrics.inc("redis.error"); }    // swallow, fall through to SQL
  if (cached) return JSON.parse(cached);
  const row = await db.getBook(id);            // SQL is source of truth
  ```
- **Redis client timeout:** **200 ms** connect/op timeout so a sick cache doesn't add latency — fail through immediately rather than waiting.
- **SQL protection under cache loss:** because all reads now hit SQL, enable a **per-instance concurrency limit** and rely on SQL connection pooling (max pool 100) so the DB isn't overwhelmed; this is the scenario that makes N2 ("useful when cache cold") a real requirement.
- **No retry storm:** do **not** retry Redis on failure (1 try, fail through) — retrying a down cache just adds latency.

### Manual response
1. **On-call** acknowledges Sev2. Confirm it's Redis (dependency map in App Insights).
2. Watch **SQL CPU/DTU** — if SQL approaches saturation, **scale up SQL tier** and/or **scale out App Service** to spread connections, and consider enabling **rate limiting at Front Door** to shed load.
3. Restart/scale the Redis instance or fail over to a replica; if unrecoverable, provision a new cache and let it repopulate lazily (cache-aside warms itself).
4. Update incident channel; close when miss-ratio normal and p95 back under 800 ms.

### Post-incident actions
- Follow-ups: (a) load-test the **cache-cold path at 10× RPS** before Sunday (directly de-risks the N1 "out of budget" bet), (b) add an alert on **SQL saturation during cache loss**, (c) evaluate a small in-process LRU as a second-level fallback for the hottest pages.

---

## Failure 3: Sunday tabloid spike — 10× sustained traffic for 4 hours

### What the user sees
- Ideally: no change — pages stay fast. Under stress before scaling catches up: brief **higher latency** and some **429 "Too many requests, retry shortly"** at the edge rather than 5xx. The app shows a friendly "We're very busy — trying again…".

### Detection
- **Signal:** Front Door / App Insights **RPS** climbs ~10×; App Service **CPU > 75%**; **HTTP queue length** rises; Service Bus **`ActiveMessageCount`** (notifications/digest) grows.
- **Query (AI):**
  ```kusto
  requests | where timestamp > ago(5m)
  | summarize rps = count()/300.0, p95 = percentile(duration,95)
  ```
- **Alerts:** `App Service CPU > 75% for 5 min` → Sev3 (autoscale should handle); `p95 search > 800 ms for 10 min` → **Sev2 page** (N1 burn); `Service Bus ActiveMessageCount > 10,000` → Sev3 (consumer falling behind).

### Mitigation in design (autoscale, queue depth, throttling)
- **Pre-scale, don't only autoscale:** schedule App Service to **pre-warm to the expected 10× instance count from Saturday night through Sunday evening**, because autoscale reacts in minutes and a sudden spike outruns it. Autoscale rule: **+2 instances when CPU > 70% for 5 min, scale-in slowly (1 instance / 10 min < 40% CPU)**, max e.g. 20 instances.
- **Throttle at the edge:** **Azure Front Door rate limiting** — e.g. **100 requests / minute / client IP** on write/auth endpoints, higher for read search; return **429 with `Retry-After`** rather than letting the origin melt. Sheds abusive/runaway clients first.
- **Protect writes with idempotency:** clients send **`Idempotency-Key`** (a UUID) on `POST /books`; the API stores the key→result for 24 h, so a user mashing "retry" during the spike **never creates duplicate listings** (satisfies N3b). This is the failure that *requires* the idempotency key.
- **Absorb async load:** notifications/digest go through **Service Bus**, which **buffers** the surge; the worker drains at its own pace. A backlog is acceptable (email is best-effort); in-app notify latency may exceed 2 s temporarily — an accepted, budgeted degradation (N9 has a 5% budget).
- **Shed non-critical work:** pause the weekly-digest send job during the 4-hour peak if queue depth is high — defer it to Sunday night.

### Manual response
1. **On-call** is the spike commander; a **secondary** is on standby (planned, since the date is known).
2. Watch the **business + health dashboards**; if autoscale lags, **manually bump min instance count**.
3. If origin is stressed, **tighten Front Door rate limits** and confirm 429s (not 5xx) are being served.
4. If Service Bus backlog grows, **scale out the worker** consumer count.
5. Keep `#bookswap-incidents` updated; stand down after traffic normalises.

### Post-incident actions
- Follow-ups: (a) capture the real peak RPS and the **actual** scaling lag to tune pre-scale numbers, (b) right-size the autoscale thresholds from observed CPU, (c) decide whether read-replica search is needed for the next spike, (d) write a reusable **"known high-traffic event" checklist** so the next feature isn't a fire drill.

---

### Cross-cutting retry helper (referenced above)
```js
// Retry ONLY transient errors (5xx, network, listed SQL transient codes)
async function callWithRetry(fn, { tries = 3, baseMs = 200, capMs = 2000 } = {}) {
  for (let i = 0; i < tries; i++) {
    try { return await fn(); }
    catch (err) {
      if (!isTransient(err) || i === tries - 1) throw err;
      const sleep = Math.min(capMs, baseMs * 2 ** i) + Math.random() * 100; // jitter
      await new Promise(r => setTimeout(r, sleep));
    }
  }
}
```
