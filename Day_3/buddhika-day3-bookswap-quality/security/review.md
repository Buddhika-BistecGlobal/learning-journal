# BookSwap — Security Review of the API

> **Author:** Buddhika Amarasinghe
> **Target:** the Day 2 BookSwap API contract (`buddhika-day2-bookswap-openapi.yaml`)
> running behind Azure Front Door → App Service, with Entra External ID auth.
> **Method:** manual contract/design review across 7 categories + an OWASP ZAP
> baseline scan against the Prism mock (`security/zap-baseline-report.html`).
> Severity scale: **H** = exploitable, real data/impact · **M** = real but limited/conditional · **L** = hardening/defence-in-depth.

---

## 1. Review matrix

| Category | Question | Finding | Severity | Mitigation |
|----------|----------|---------|----------|------------|
| **Authn** | Is every non-public endpoint protected by JWT? | The OpenAPI applies `security: [bearerAuth]` **globally**, which is correct — but `/health` (required to be the *only* anonymous route, NFR N5) is not yet in the spec. Risk that it's added later **without** a `security: []` override, or that a new route silently inherits/loses protection. | **M** | Keep global `security`; add `/health` with explicit `security: []`. Add a CI contract test asserting every path except `/health` returns 401 with no token (we already proved `GET /books` → 401). Enforce JWT validation at App Service **and** validate `aud`/`iss`/`exp` (≤ 1 h) against Entra JWKS. |
| **Authz** | Does every `/{id}`-shaped endpoint check object ownership? | **No ownership check is expressed.** `GET /books/{bookId}/loans` (borrower history) and `GET /loans/{loanId}` return another member's loan/borrower data to any authenticated caller — a classic **BOLA** (see §2). Violates N6 ("never see another member's loan history/address"). | **H** | Server-side object-level check on every `/{id}` route: load the row, assert `caller.sub == resource.ownerId` (or `borrowerId` for loans), else **404** (not 403 — don't confirm existence). Centralise in middleware; add tests with two members. |
| **Injection** | Are all DB queries parameterised? | Day 2 storage doc uses parameterised queries (`WHERE id = @id`). **Risk area:** the free-text `search` over title/author/ISBN — if built with string concatenation or a raw `LIKE '%' + input + '%'`, it's SQL-injectable. | **M** | Use parameterised queries / an ORM everywhere; for search use a parameter and server-side `LIKE @q` binding, or Azure SQL full-text search. Never concatenate `search` into SQL. Add a lint/review gate. |
| **Secrets** | Where are connection strings stored? | Constraint requires **Key Vault, never `.env` in prod**. Finding: ensure App Service reads SQL/Redis/Service Bus/Blob/ACS connection strings via **Key Vault references + Managed Identity**, not plaintext App Settings, and that no secret is logged. | **L** | App Service **system-assigned Managed Identity** with `@Microsoft.KeyVault(SecretUri=...)` references; rotate keys; deny secret values in logs; `.env` only for local dev (git-ignored). |
| **Transport** | Is TLS enforced at Front Door? | Front Door terminates TLS, but need to confirm **HTTPS-only redirect**, **min TLS 1.2**, and **HSTS**. The ZAP baseline flags **missing `Strict-Transport-Security`** and other security headers (see §4). | **M** | Front Door: "HTTPS only" + redirect HTTP→HTTPS; minimum TLS 1.2; origin accepts traffic only from Front Door (`X-Azure-FDID` check + private link). Emit `Strict-Transport-Security: max-age=31536000; includeSubDomains`. |
| **Rate limit** | Are auth and write endpoints rate-limited? | **No rate limiting on write/auth paths.** `POST /books/{bookId}/borrow-requests` can be spammed — flooding an owner with in-app notifications and Service Bus messages (abuse + cost). Token-validation/login paths can be brute-forced from the edge. | **M** | Azure Front Door **rate-limit rules**: e.g. 100 req/min/IP on writes & auth, higher on read search; plus a per-user app-level cap (e.g. max 5 open borrow requests / member / hour). Return **429 + `Retry-After`**. |
| **PII** | What PII appears in responses, logs, or queues? | Two real risks: (a) **PII in telemetry** — if the API logs the `Authorization` header or full request bodies, the **JWT (email claim)** and member email land in Application Insights, readable by anyone with workspace access (see §3). (b) **Queue payloads** — digest/notify Service Bus messages must carry `memberId`, not email/address. Responses already correctly omit `phone`/`address`. | **H** | Never log `Authorization` or raw bodies; log **`memberId` (Entra `sub`/oid), not email**. Add an App Insights **TelemetryProcessor** that strips `authorization`, `email`, `phone`, `address` from `customDimensions`. Queue messages reference IDs only; the worker resolves email at send time. |

---

## 2. BOLA scenario (concrete URL + request)

**Broken Object Level Authorization — reading another member's borrower history.**

- **Setup:** Member **B** is authenticated (valid JWT, `sub = member-B`). A book `7a1f6c2e-9b4d-4e1a-8c3f-2b6d9e0a1c45` is owned by Member **A**.
- **Malicious request:**
  ```http
  GET /books/7a1f6c2e-9b4d-4e1a-8c3f-2b6d9e0a1c45/loans?page=1&pageSize=20 HTTP/1.1
  Host: api.bookswap.local
  Authorization: Bearer <member-B's valid token>
  ```
- **Current behaviour:** returns a `LoanPage` — every loan for that book including each **borrower's `memberId`**, borrow/return timestamps — i.e. *who in the building borrowed what and when*. Member B is neither the owner nor a borrower, yet gets the full history. The same flaw lets B walk `GET /loans/{loanId}` by guessing/enumerating UUIDs.
- **Why it matters:** directly violates N6 ("a member must never see another member's loan history or address"); leaks neighbour activity/identity. UUIDs reduce but do not eliminate enumeration (they leak via shared links, logs, referrers).
- **Fix:** in the handler, load the book/loan and **authorize the object**: borrower history is visible only to the book's **owner**; a single loan is visible only to its **owner or borrower**. Fail with **404** when unauthorized so existence isn't confirmed. Add an automated test: Member B → 404 on Member A's book loans.

---

## 3. PII leak via logs/telemetry (concrete)

- **Where:** Application Insights request/trace telemetry. A common Express setup logs request metadata into `customDimensions`. If the **`Authorization` header** or **request body** is captured, the **JWT** (which contains the member's **email** in its claims) and any email/phone in bodies are stored in the **Logs workspace**.
- **Impact:** every engineer/operator with Log Analytics read access can run `traces | where customDimensions has "@"` and harvest member emails — a PDPA-relevant personal-data exposure, retained for the whole log retention period.
- **Fix (implementable):**
  ```js
  // App Insights telemetry processor — strip PII before egress
  appInsights.defaultClient.addTelemetryProcessor((env) => {
    const cd = env.data?.baseData?.properties ?? {};
    delete cd.authorization; delete cd.email; delete cd.phone; delete cd.address;
    return true;
  });
  ```
  Log the **`memberId`** (Entra `oid`/`sub`) for audit (N8), never the email. Set log retention per policy and restrict workspace RBAC.

---

## 4. OWASP ZAP baseline scan

- **How it was run** (reproducible):
  ```bash
  # Terminal 1 — mock the Day 2 API
  npx @stoplight/prism-cli mock buddhika-day2-bookswap-openapi.yaml --host 0.0.0.0 --port 4010
  # Terminal 2 — baseline scan from the official ZAP image
  docker run --rm -t -v "$PWD:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
    zap-baseline.py -t http://host.docker.internal:4010 -r zap-baseline-report.html -I
  ```
- **Report:** `security/zap-baseline-report.html` (attached).
- **Actual result of this run:** `FAIL-NEW: 0 · WARN-NEW: 2 · PASS: 65`. The two warnings are real and worth discussing:
  - **Cross-Domain Misconfiguration — CORS [10098]** *(the finding I'll discuss in depth)*: ZAP saw an over-permissive CORS response (`Access-Control-Allow-Origin: *`) — here it comes from the **Prism mock's default**, but it is a genuine production risk: a wildcard CORS policy on an authenticated API lets **any** website's JavaScript call BookSwap with the user's credentials/token in the browser. **Triage: Medium in production / informational against the mock.** **Mitigation:** at Front Door / middleware, set `Access-Control-Allow-Origin` to the **explicit BookSwap app origin(s) only** (never `*` for an authenticated API), and do not reflect arbitrary `Origin`.
  - **Storable and Cacheable Content [10049]:** responses are cacheable, which for authenticated/PII responses risks caching member data in shared proxies/browser caches. **Triage: Low.** **Mitigation:** send `Cache-Control: no-store` (and `Pragma: no-cache`) on all authenticated responses; only public, non-PII reads may be cached.
- **Triage discipline:** **FAIL-NEW is 0** and 65 rules passed — so this is *not* "everything is on fire." The real launch risk is the **BOLA in §2**, which the scan **cannot** see. That is the key lesson, below.
- **Note on scope / a real limitation observed:** the baseline scan is **passive** and unauthenticated; ZAP's spider only reached the API root and got `404` (the API has no `/` route), so passive checks ran mostly against error responses. It therefore did **not** (and cannot) detect the BOLA in §2 or the telemetry PII leak in §3 — those need **authenticated, business-logic** testing. The scan complements, never replaces, the manual review.

> Counts and rule IDs from this exact run are mirrored in `security/threats.csv` (T8/T10) and visible in the attached HTML.

---

## 5. Summary

The two findings that would block the Sunday launch are **H**: the **BOLA on loan/borrower-history endpoints** (§2) and **PII (email) in telemetry** (§3). Rate-limiting and TLS hardening are **M** and should ship this week. Injection and secrets are **L/M** assuming the Day-2 parameterised-query and Key Vault decisions are actually followed — both need a verifying test/gate, not just a promise.
