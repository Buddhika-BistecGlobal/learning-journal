# Day 2 Challenge — BookSwap

## Challenge Overview

BookSwap is a small community marketplace where neighbours in a Colombo apartment block trade or lend books with each other. The product manager has handed you a feature list and asked for a backend design — REST API, storage choices, and where to use a cache or a queue. No code today — just a design that another developer could implement on Day 3 of their week.

- **Time Allocation:** 3 hours (during session)
- **Difficulty:** Beginner

---

## Business Requirements

### Functional Requirements

- Members can list a book they own (title, author, ISBN, condition, photo, available/unavailable).
- Members can search the catalogue by title, author, or ISBN and filter by condition.
- Members can request to borrow a book; the owner gets a notification and can accept or decline.
- The system tracks loans (out, returned, overdue beyond 30 days) and shows a borrower history per book.
- A weekly digest emails every member the 10 most recently added books in the building.

### Non-Functional Requirements

- **Catalogue search response time:** under 300 ms p95 for a building with up to 5,000 books.
- **Listing creation:** must succeed even if the email service is down (do not block the user).
- **Photo uploads:** up to 5 MB JPEG/PNG; never stored in the application database.
- **Notifications:** in-app must arrive within 2 seconds; email digest is best-effort.
- **Privacy:** addresses and phone numbers are never returned in API responses (members only).

### Technical Constraints

- Backend will be built in Node.js (Express or Fastify) on Azure App Service.
- Choose Azure-managed databases where possible (Azure SQL, Cosmos DB, Cache for Redis, Blob Storage).
- Email is sent via Azure Communication Services Email.
- Authentication will be handled by Microsoft Entra External ID — assume a valid JWT arrives in `Authorization: Bearer ...` for every request.

---

## Deliverables

### 1. OpenAPI Specification (25 points)

**File:** `{your-name}-day2-bookswap-openapi.yaml`

**Required Sections:**

```yaml
openapi: 3.1.0
info:
  title: BookSwap API
  version: 0.1.0
  description: |
    Short description of the API and which user need it serves.

servers:
  - url: https://api.bookswap.local

paths:
  /books:
    get:
      summary: List books in the building
      parameters:
        - name: search
          in: query
        - name: condition
          in: query
        - name: page
          in: query
        - name: pageSize
          in: query
      responses:
        "200": { description: Page of books }
        "401": { description: Missing or invalid token }
    post:
      summary: List a new book
      ...

  /books/{bookId}/borrow-requests:
    post:
      summary: Request to borrow this book
      ...

  /loans/{loanId}:
    patch:
      summary: Mark a loan returned
      ...

components:
  schemas:
    Book: { ... }
    BorrowRequest: { ... }
    Loan: { ... }
    Page: { ... }
```

**Evaluation Criteria:**

- Resources are nouns; HTTP verbs map correctly to actions (5 pts)
- At least 4 distinct status codes are used appropriately across endpoints (5 pts)
- Every list endpoint supports pagination with `page` and `pageSize` or a cursor (5 pts)
- Schemas defined under `components.schemas` and reused via `$ref` (no copy-paste duplication) (5 pts)
- The spec is valid — `npx @apidevtools/swagger-cli validate` returns no errors (5 pts)

---

### 2. Storage and Cache Decision Doc (25 points)

**File:** `{your-name}-day2-storage-decisions.md`

**Required Content:**

```markdown
# BookSwap — Storage and Cache Decisions

## 1. Data inventory
| Data type | Example record | Volume estimate (1y) | Read/write ratio |
|-----------|----------------|----------------------|------------------|
| Book listing | one row per book | ~50,000 across all buildings | read-heavy |
| ...

## 2. Storage selection
| Data type | Chosen store | Why this store | Why not the alternatives |
|-----------|--------------|----------------|--------------------------|
| Book listing | Azure SQL | Relational with FK to member | Document DB unnecessary, relational joins useful |
| Book photo | Azure Blob Storage | Binary, big | Database BLOBs would bloat backups |
| ...

## 3. Cache plan
- What is hot enough to cache?
- Cache-aside pattern in pseudocode
- TTL choice and invalidation strategy

## 4. Queue plan
- Which work goes on a queue and why
- What happens if the consumer is down for 30 minutes
```

**Code Requirements:**

- Cache-aside pseudocode block included
- A clear answer to "what is the source of truth for each piece of data"
- At least one example of when *not* to cache

**Evaluation Criteria:**

- Every data type has a primary store with reasoning (5 pts)
- "Why not the alternative" is specific, not generic (5 pts)
- Cache plan names what to cache and TTL with rationale (5 pts)
- Queue plan identifies failure mode (consumer down, retry, DLQ) (5 pts)
- Decision doc reads as a memo a senior engineer could approve, not as a homework dump (5 pts)

---

### 3. Container Diagram (C4 Level 2) (25 points)

**Repository Structure:**

```text
bookswap-design/
├── diagrams/
│   ├── container-diagram.png
│   └── container-diagram.drawio
├── openapi/
│   └── bookswap-openapi.yaml
├── decisions/
│   └── storage-decisions.md
└── README.md
```

**Required Containers:**

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| Mobile app | React Native | Member-facing UI |
| API service | Node.js Express on Azure App Service | REST API |
| Database | Azure SQL | System of record |
| Cache | Azure Cache for Redis | Hot read paths |
| Object store | Azure Blob Storage | Book photos |
| Queue | Azure Service Bus | Email digest, notifications |
| Email | Azure Communication Services | Outbound digest |
| Identity | Microsoft Entra External ID | Authn / JWT issue |

**Minimum Functionality:**

- [ ] Every container box shows technology + responsibility
- [ ] Every arrow has protocol (HTTPS/AMQP/SMTP/SQL) and a verb-led label
- [ ] User actor is shown calling the mobile app, not the API directly
- [ ] One arrow demonstrates a synchronous call, another an asynchronous queue message
- [ ] README explains how to read the diagram in 5 sentences

**Evaluation Criteria:**

- All containers from the storage decisions appear in the diagram (5 pts)
- Sync vs async paths are visually distinct (line style / colour / label) (5 pts)
- Cache and queue are placed where the decisions doc says they belong (5 pts)
- Diagram readable when shrunk to A5 size (visual hygiene) (5 pts)
- README walkthrough explains the diagram clearly (5 pts)

---

### 4. Mock and Smoke Test Report (25 points)

**File:** `{your-name}-day2-mock-report.md`

**Required Tests/Validations:**

| # | Endpoint | Method | Body / Params | Expected status | Actual status |
|---|----------|--------|---------------|-----------------|---------------|
| 1 | `/books` | GET | `page=1&pageSize=20` | 200 | ? |
| 2 | `/books` | POST | valid book payload | 201 | ? |
| 3 | `/books` | POST | missing title | 400 or 422 | ? |
| 4 | `/books/999/borrow-requests` | POST | borrower JWT | 201 | ? |
| 5 | `/books` | GET | (no Authorization header) | 401 | ? |

**Report Format:**

```markdown
# BookSwap — Mock Smoke Test Report

## Setup
- Prism command used (`npx @stoplight/prism mock bookswap-openapi.yaml`)
- Postman / Bruno collection link or screenshot

## Results Summary
| Metric | Target | Achieved |
|--------|--------|----------|
| Tests run | 5 | ? |
| Tests passing against the mock | 5 | ? |
| Endpoints with explicit error responses | 4+ | ? |

## Findings
- What did the mock reveal that the OpenAPI on its own did not?
- Which endpoints feel awkward to call?

## Spec changes you would make
1. ...
2. ...
```

**Evaluation Criteria:**

- All 5 tests run and reported with actual status codes (5 pts)
- Negative tests (missing field, missing token) are present (5 pts)
- At least two real findings from running the mock are written up (5 pts)
- Spec changes proposed are concrete (file + line, not "better errors") (5 pts)
- Report is reproducible — another intern can re-run from the instructions (5 pts)

---

## Submission Guidelines

### File Naming Convention

```text
{your-name}-day2-bookswap-openapi.yaml
{your-name}-day2-storage-decisions.md
{your-name}-day2-container-diagram.png
{your-name}-day2-mock-report.md
{your-name}-day2-bookswap-design/  (zipped repository)
```

### Submission Checklist

- [ ] OpenAPI spec validates with no errors
- [ ] Storage decision doc covers all data types with reasoning
- [ ] Container diagram exported as PNG with source file alongside
- [ ] Mock smoke test report with results table populated
- [ ] All files follow naming convention

---

## Scoring Guide

| Grade | Score | Description |
|-------|-------|-------------|
| Exceptional | 90–100 | OpenAPI is a pleasure to read; storage choices defended with numbers; diagram could be the basis of a real Sprint 0 |
| Proficient | 75–89 | API design is clean and conventional; storage choices reasonable with clear reasoning; diagram complete |
| Developing | 60–74 | API design has verb-in-URL or status-code mistakes; one or two storage choices unclear; diagram missing arrows or labels |
| Beginning | <60 | API uses random verbs or all 200s; storage choices not justified; diagram a free-form sketch with no notation |

**Passing Score:** 75%

---

## Hints and Tips

### Pagination — pick one and stick with it

```yaml
# offset-based, simple
parameters:
  - name: page
    in: query
    schema: { type: integer, minimum: 1, default: 1 }
  - name: pageSize
    in: query
    schema: { type: integer, minimum: 1, maximum: 100, default: 20 }

responses:
  "200":
    content:
      application/json:
        schema:
          type: object
          properties:
            items:
              type: array
              items: { $ref: "#/components/schemas/Book" }
            page: { type: integer }
            pageSize: { type: integer }
            total: { type: integer }
```

### Cache-aside pattern in pseudocode

```javascript
async function getBook(bookId) {
  const cacheKey = `book:${bookId}`;
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const row = await db.query("SELECT * FROM books WHERE id = $1", [bookId]);
  if (!row) return null;

  // TTL chosen because: book metadata rarely changes; ok to be 60s stale
  await redis.set(cacheKey, JSON.stringify(row), "EX", 60);
  return row;
}

async function updateBook(bookId, patch) {
  const updated = await db.update("books", bookId, patch);
  await redis.del(`book:${bookId}`); // invalidate so next read repopulates
  return updated;
}
```

### Validate the spec from the command line

```bash
npx @apidevtools/swagger-cli validate bookswap-openapi.yaml
npx @stoplight/prism mock bookswap-openapi.yaml --port 4010
# In another terminal:
curl -s http://localhost:4010/books?page=1\&pageSize=5 | jq
```
