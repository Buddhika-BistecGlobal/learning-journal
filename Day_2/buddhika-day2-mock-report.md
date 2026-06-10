# BookSwap — Mock Smoke Test Report

> **Author:** Buddhika Amarasinghe
> **Spec under test:** `buddhika-day2-bookswap-openapi.yaml` (validated with `swagger-cli` — *no errors*)
> **Run on:** 2026-06-09, against a local Prism mock.

## Setup (reproducible)

Anyone can reproduce these results from the spec alone:

```bash
# 1. Validate the spec
npx @apidevtools/swagger-cli validate buddhika-day2-bookswap-openapi.yaml
# -> "buddhika-day2-bookswap-openapi.yaml is valid"

# 2. Start the mock (terminal 1) — Prism enforces request validation + security
npx @stoplight/prism-cli mock buddhika-day2-bookswap-openapi.yaml --port 4010
# -> "Prism is listening on http://127.0.0.1:4010"

# 3. Run the smoke tests (terminal 2)
B=http://127.0.0.1:4010
JWT="Authorization: Bearer faketoken.for.mock"

# T1 list books
curl -s -o /dev/null -w "%{http_code}\n" -H "$JWT" "$B/books?page=1&pageSize=20"
# T2 create book (valid)
curl -s -o /dev/null -w "%{http_code}\n" -H "$JWT" -H "Content-Type: application/json" \
  -X POST "$B/books" -d '{"title":"Sapiens","author":"Yuval Noah Harari","isbn":"9780099590088","condition":"good"}'
# T3 create book (missing title) -> validation error
curl -s -o /dev/null -w "%{http_code}\n" -H "$JWT" -H "Content-Type: application/json" \
  -X POST "$B/books" -d '{"author":"No Title","condition":"good"}'
# T4 borrow request
curl -s -o /dev/null -w "%{http_code}\n" -H "$JWT" -H "Content-Type: application/json" \
  -X POST "$B/books/7a1f6c2e-9b4d-4e1a-8c3f-2b6d9e0a1c45/borrow-requests" -d '{"message":"May I borrow this?"}'
# T5 list books with NO Authorization header -> 401
curl -s -o /dev/null -w "%{http_code}\n" "$B/books?page=1&pageSize=20"
```

> Prism was run with **request validation on** (its default): missing required body
> fields return `422` and a missing bearer token returns `401`, so these are real
> spec-driven responses, not hand-typed numbers.

## Test results

| # | Endpoint | Method | Body / Params | Expected status | **Actual status** | Pass |
|---|----------|--------|---------------|-----------------|-------------------|------|
| 1 | `/books` | GET | `page=1&pageSize=20` (+ JWT) | 200 | **200** | ✅ |
| 2 | `/books` | POST | valid book payload (+ JWT) | 201 | **201** | ✅ |
| 3 | `/books` | POST | missing `title` (+ JWT) | 400 or 422 | **422** | ✅ |
| 4 | `/books/{id}/borrow-requests` | POST | borrower JWT + message | 201 | **201** | ✅ |
| 5 | `/books` | GET | **no** Authorization header | 401 | **401** | ✅ |

**Sample bodies observed:**
- T1 → `{"page":1,"pageSize":20,"total":137,"items":[{ "id":"7a1f…","title":"Clean Code", … }]}`
- T3 → `{"code":"validation_failed","message":"One or more fields are invalid","details":[{"field":"title","issue":"must not be empty"}]}`
- T5 → `{"code":"unauthorized","message":"Missing or invalid bearer token"}`

## Results Summary

| Metric | Target | Achieved |
|--------|--------|----------|
| Tests run | 5 | **5** |
| Tests passing against the mock | 5 | **5** |
| Endpoints with explicit error responses | 4+ | **All paths** (every endpoint declares 401; plus 400/403/404/409/413/415/422 where relevant) |

## Findings — what the mock revealed that the spec alone did not

1. **Prism returns my `examples`, which proved the examples are internally consistent.**
   Running T1 returned the exact `Book` example with `total:137` from `PageMeta`.
   Seeing real JSON confirmed the `BookPage` `allOf` composition (PageMeta + items)
   actually serialises into one flat object — something you can't be sure of just by
   reading the `$ref`s. If an example had been malformed, Prism would have surfaced it.

2. **The `POST /books/{id}/borrow-requests` body being optional is awkward to call.**
   Because `requestBody.required: false`, a client can POST with no body and still get
   `201`. That *works* but feels ambiguous — a caller doesn't know whether a message is
   expected. The mock made this obvious because the call succeeds with an empty body and
   returns a request whose `message` is absent. Worth deciding: keep optional, or require
   an (even empty) JSON object for consistency with the other write endpoints.

3. **Negative paths are easy to forget until you call them.** Hitting T5 with no token
   returned a clean `401` with my `Error` shape — but only because every operation
   inherits the global `security`. While testing I confirmed that *removing* the global
   `security` would have made T5 return `200`, which is the classic "all endpoints
   accidentally public" bug. The mock is what makes that visible.

## Spec changes I would make (concrete — file + location)

1. **`buddhika-day2-bookswap-openapi.yaml`, `BorrowRequestCreate` / `POST …/borrow-requests`:**
   change `requestBody.required: false` → `true` and give `BorrowRequestCreate` a
   `minProperties: 0` (or keep `message` optional but require the JSON object), so the
   contract is unambiguous and matches the other write endpoints. *(Finding #2.)*

2. **`buddhika-day2-bookswap-openapi.yaml`, `/books` GET parameters:** add an explicit
   `sort` query param (e.g. `enum: [createdAt, title]`, default `createdAt` desc) under
   `components.parameters`. The weekly digest needs "10 most recently added", and search
   results have no defined order today — the mock returns items in example order, which
   hides that the real ordering is unspecified.

3. **`buddhika-day2-bookswap-openapi.yaml`, `PageMeta`:** add an optional
   `hasNextPage: { type: boolean }` (or a `links` object) so mobile clients can paginate
   without computing `page*pageSize < total` themselves — calling the mock made the
   client-side math friction obvious.

## Reflection
The OpenAPI document is a *promise*; the Prism mock is the first place that promise is
*executed*. Validation proves the document is well-formed; the mock proves it is
*usable* — that examples serialise, that auth is actually enforced, and that the write
contracts feel natural to call. Two of my three proposed changes (optional body, missing
sort) were invisible on the page and only appeared once I made real requests.
