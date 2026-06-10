# BookSwap — Storage and Cache Decisions

> **Author:** Buddhika Amarasinghe
> **Audience:** the Day-3 implementing developer + reviewing senior
> **Scope:** one Express/Fastify API on Azure App Service, Azure-managed backing services.

---

## 1. Data inventory

Volume math is grounded in the brief: a building holds **up to 5,000 books**; the
weekly digest and loan tracking imply a few hundred active members per building.
Estimates below assume the product reaches **~10 buildings in year one**.

| Data type | Example record | Volume estimate (1y) | Read/write ratio |
|-----------|----------------|----------------------|------------------|
| Book listing | `{id, title, author, isbn, condition, available, photoUrl, ownerId}` | ~50,000 rows (5k × 10 buildings) | **Read-heavy** (search dominates; ~50:1) |
| Book photo | one JPEG/PNG ≤ 5 MB per book | ~50,000 blobs, ~50–100 GB total | Write-once, read-many |
| Member | `{id, name, buildingId, email, phone, address}` | ~2,000 rows | Read-heavy; PII fields rarely change |
| Borrow request | `{id, bookId, borrowerId, status, createdAt}` | ~30,000/yr (transient → resolved) | Balanced; bursty writes |
| Loan | `{id, bookId, borrowerId, ownerId, status, borrowedAt, dueAt, returnedAt}` | ~20,000/yr | Write on create/return; read for history |
| Notification | in-app message `{id, memberId, type, payload, readAt}` | ~100,000/yr | Write-heavy, short-lived reads |
| Digest job | "send weekly digest for building X" message | ~520/yr (10 buildings × 52 wk) | Queue message, not stored long-term |

---

## 2. Storage selection

| Data type | Chosen store | Why this store | Why **not** the alternatives |
|-----------|--------------|----------------|------------------------------|
| Book listing | **Azure SQL** | Naturally relational — FK from book → member (owner), loans → book/member; search + condition filter + pagination are trivial SQL with indexes; 50k rows is tiny for SQL. | **Cosmos DB:** no relational joins, would need denormalisation and we'd hand-roll cross-document consistency for loans — overkill for 50k rows. **Blob:** not queryable. |
| Book photo | **Azure Blob Storage** | Binary up to 5 MB, write-once read-many; brief explicitly forbids storing photos in the app DB; serve via CDN later. | **Azure SQL BLOB column:** bloats backups, slows restores, wastes DB IOPS/storage on bytes a CDN should serve — the brief rules this out. |
| Member (incl. PII) | **Azure SQL** | Same relational graph as books; row-level columns let us *project away* `phone`/`address` so the API never returns them (NFR privacy). | **Cosmos:** no relational benefit; **Entra External ID:** holds identity/auth claims, not app profile data like buildingId. |
| Borrow request | **Azure SQL** | Short-lived state machine (`pending→accepted/declined`) with FKs to book + member; transactional with the loan it spawns. | **Queue:** a request is queryable state the owner lists, not fire-and-forget work. **Cosmos:** no need. |
| Loan | **Azure SQL** | System-of-record for the loan lifecycle and overdue calc; "borrower history per book" is a simple indexed query; needs a transaction with book.available. | **Cosmos/Blob:** lose transactional integrity between loan + book availability. |
| Notification (in-app) | **Azure SQL** (table) + **Service Bus** (delivery) | Must persist so the app can list unread; the 2s delivery is achieved by enqueueing on Service Bus and a worker writing the row + pushing. | **Redis only:** would lose notifications on eviction/restart — not durable enough for an inbox. |
| Digest / email work | **Azure Service Bus** (queue) | Decouples slow/best-effort email from the request path; survives email outage (NFR: listing must succeed even if email is down). | **Synchronous SMTP call:** blocks the user and fails the listing if ACS is down — violates the brief. |

**Source of truth (one line each):**
- **Book / Member / BorrowRequest / Loan / Notification record → Azure SQL.**
- **Book photo bytes → Azure Blob Storage** (SQL holds only the `photoUrl`).
- **Identity & auth claims (who you are) → Microsoft Entra External ID** (the JWT); the app DB holds only the app profile keyed by the Entra subject id.
- **Cached values in Redis are never authoritative** — they are a disposable copy of SQL and may be dropped at any time.

---

## 3. Cache plan

**What is hot enough to cache?**
The brief's hard target is **catalogue search < 300 ms p95 over 5,000 books**. Two read paths dominate and are cache-worthy:

1. **Search result pages** — the same first-page queries ("recently added", popular subjects) repeat across many members in a building. Cache the *page* keyed by normalised query.
2. **Single book reads** (`GET /books/{id}`) — opened repeatedly from search results; metadata changes rarely.

**What I will NOT cache (the "when not to cache" example):**
- **`available` / loan status changes too fast and matters too much** — caching it risks showing a book as borrowable seconds after it was lent, producing a 409 on borrow. So I cache *metadata* (title/author/condition/photoUrl) but read **availability live from SQL** (or use a very short 5–10s TTL). Stale "this book is free" is a worse user experience than an extra DB hit.
- **Per-member private data and notifications** — low reuse, privacy-sensitive, not worth the invalidation complexity.

**Cache-aside pattern (pseudocode):**

```js
// READ — cache-aside (lazy population)
async function getBook(bookId) {
  const key = `book:${bookId}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);                 // cache hit

  const row = await db.query("SELECT * FROM books WHERE id = @id", { id: bookId });
  if (!row) return null;                                  // do NOT cache misses (or cache a short null-sentinel)

  // TTL = 300s: book metadata rarely changes; 5 min stale title/author is harmless.
  await redis.set(key, JSON.stringify(row), "EX", 300);
  return row;
}

// SEARCH — cache the page, short TTL because the catalogue grows
async function searchBooks(q, page, pageSize) {
  const key = `search:${normalise(q)}:${page}:${pageSize}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const result = await db.searchBooks(q, page, pageSize);
  await redis.set(key, JSON.stringify(result), "EX", 60); // 60s: tolerate slightly stale lists
  return result;
}

// WRITE — write-through-by-invalidation: SQL is source of truth, then drop stale keys
async function updateBook(bookId, patch) {
  const updated = await db.update("books", bookId, patch);  // SQL commits first
  await redis.del(`book:${bookId}`);                        // invalidate the single-book entry
  await redis.del(...await redis.keys("search:*"));         // search pages may now be stale
  return updated;
}
```

**TTL choice & invalidation strategy:**
- `book:{id}` → **300s** TTL **+ explicit `DEL` on update/borrow/return.** TTL is the safety net; invalidation is the primary mechanism so reads are fresh right after a write.
- `search:*` → **60s** TTL only (no precise invalidation — a new listing should appear within a minute, which satisfies "weekly digest of recently added" UX without complex fan-out). In production prefer a tagged/versioned key (`search:{buildingId}:v{n}`) and bump the version on any listing change instead of `KEYS *` (which is O(n) and discouraged on Redis).

---

## 4. Queue plan

**Which work goes on a queue and why** — anything slow, best-effort, or that must not
fail the user's request goes on **Azure Service Bus**:

1. **Weekly digest email** — a timer (Azure Function / cron) enqueues one "build digest for building X" message per building; a consumer queries the 10 most-recent books and calls ACS Email. Slow + best-effort → must not be on the request path.
2. **In-app + email notifications on borrow events** — `POST borrow-request` and accept/decline write the DB row, then enqueue a notify message. This keeps the API response fast and decouples delivery (NFR: in-app within 2s is met by a worker draining the queue continuously).
3. **Listing-time side effects** — the brief says *listing creation must succeed even if email is down.* The create writes to SQL and **enqueues** any follow-up email; it never calls ACS inline. So a dead email service can never fail a listing.

**Failure mode — consumer down for 30 minutes:**
- Messages **accumulate durably** in the Service Bus queue (default TTL is days, far beyond 30 min) — nothing is lost while the worker is offline.
- When the consumer restarts it **drains the backlog** in order. Email is best-effort, so a 30-min delay on a digest is acceptable; in-app notifications arrive late but are not dropped.
- **Retries:** Service Bus redelivers on processing failure using `MaxDeliveryCount` (e.g. 5). A message that keeps failing (poison message — e.g. a deleted member) is moved to the **dead-letter queue (DLQ)** instead of blocking the queue.
- **Operability:** alert on **queue depth** and **DLQ count**; a human/redrive job reprocesses DLQ messages after fixing the root cause.
- **Idempotency:** consumers must be idempotent (e.g. dedupe on `notificationId`) because at-least-once delivery means a message can be processed more than once after a retry.

---

### Summary for the reviewer
Azure SQL is the single system of record for all relational/transactional data;
Blob holds photos; Redis is a disposable read accelerator for the 300 ms search SLO
(metadata only — never availability); Service Bus absorbs all slow/best-effort work
so the user-facing request path stays fast and survives an email outage.
