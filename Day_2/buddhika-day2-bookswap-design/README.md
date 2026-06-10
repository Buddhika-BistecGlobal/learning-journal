# BookSwap — Backend Design (Day 2)

> **Author:** Buddhika Amarasinghe
> A backend design for BookSwap, a community book-lending marketplace for a Colombo
> apartment block. No application code — this is the design another developer can
> implement on Day 3: REST contract, storage choices, and the container architecture.

## Repository layout

```
buddhika-day2-bookswap-design/
├── diagrams/
│   ├── container-diagram.png      # C4 Level 2 container diagram (exported)
│   └── container-diagram.drawio   # editable source
├── openapi/
│   └── bookswap-openapi.yaml       # OpenAPI 3.1 contract (validates clean)
├── decisions/
│   └── storage-decisions.md        # storage, cache, and queue decision memo
└── README.md
```

(The same files are also present at the `Day_2/` top level under the
`buddhika-day2-*` submission naming convention.)

## How to read the container diagram (5 sentences)

1. The **Member** (a person) only ever talks to the **Mobile App** — never to the API directly — which is the human-facing edge of the system.
2. The **Mobile App** signs the member in against **Microsoft Entra External ID** to obtain a JWT, then makes **synchronous HTTPS** calls to the **API Service**, sending that JWT as a Bearer token.
3. The **API Service** is the hub: it reads/writes the **Azure SQL** system of record, accelerates hot reads through **Azure Cache for Redis**, and stores book photos in **Azure Blob Storage** — all synchronous calls drawn as **solid dark arrows**.
4. For slow or best-effort work the API does *not* block the user: it **enqueues** notification and weekly-digest jobs onto **Azure Service Bus** — an **asynchronous** hop drawn as an **orange dashed arrow** — and a separate **Worker** consumes those messages, writes notification rows back to SQL, and sends mail via **Azure Communication Services**.
5. **Colour = ownership** (blue = containers we build/run, green = managed data stores, grey = external/managed services) and **line style = call type** (solid = synchronous request/response, orange dashed = asynchronous queue message), as the legend states.

## How to validate & mock the API

```bash
# from openapi/
npx @apidevtools/swagger-cli validate bookswap-openapi.yaml
npx @stoplight/prism-cli mock bookswap-openapi.yaml --port 4010
```

See the top-level `buddhika-day2-mock-report.md` for the smoke-test results (5/5 passing).

## Design highlights

- **REST:** resources are nouns (`/books`, `/loans`, `/borrow-requests`); verbs map to HTTP methods; every list endpoint is paginated; schemas are defined once and reused via `$ref`.
- **Storage:** Azure SQL is the single system of record; Blob holds photos; Redis is a disposable read accelerator for the 300 ms search SLO; Service Bus absorbs all slow/best-effort work so listing succeeds even when email is down.
- **Privacy:** member `phone`/`address` are never projected into API responses (NFR).
