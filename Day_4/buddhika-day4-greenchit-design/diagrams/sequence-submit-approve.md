# Sequence — Submit and Approve a Claim

> Lifelines match the **container names** in the architecture pack (Web App, Claims
> API, Azure SQL, Blob Storage, Service Bus, Notifier, Teams). **Sync vs async:**
> `->>` solid = synchronous request, `-->>` dashed = synchronous reply, `-)` open
> arrowhead = **asynchronous** message (Service Bus / scan events).

## Happy path

```mermaid
sequenceDiagram
    autonumber
    actor U as Claimant
    participant FE as Web App
    participant API as Claims API
    participant DB as Azure SQL
    participant BLOB as Blob Storage
    participant AV as Defender Scan
    participant SB as Service Bus
    participant NTF as Notifier
    participant TEAMS as Teams
    actor MGR as Line Manager

    U->>FE: Tap "Submit claim" (category, amount, receipts)
    FE->>API: GET /claims/upload-urls (JWT)
    API-->>FE: 200 SAS upload URLs
    FE->>BLOB: PUT receipt files via SAS
    BLOB-)AV: Trigger malware scan (async)
    AV--)API: Scan result = clean (async)

    FE->>API: POST /claims (JWT, receipt refs)
    API->>API: Validate JWT + RBAC, check state
    API->>DB: INSERT claim (Submitted) + audit row in one TX
    API-)SB: Publish claim.submitted (async)
    API-->>FE: 201 Created (claimId)
    FE-->>U: "Submitted" confirmation

    SB-)NTF: Deliver claim.submitted (async)
    NTF->>TEAMS: POST Adaptive Card (approve/reject)
    TEAMS-->>MGR: Notification

    MGR->>API: POST /claims/{id}/approve (JWT)
    API->>API: Validate JWT + manager-of-claimant check
    API->>DB: UPDATE status=Approved + audit row in one TX
    API-)SB: Publish claim.approved (async)
    API-->>MGR: 200 OK
```

## Error path — receipt upload fails after the claim was created, + notification fallback

```mermaid
sequenceDiagram
    autonumber
    actor U as Claimant
    participant FE as Web App
    participant API as Claims API
    participant DB as Azure SQL
    participant BLOB as Blob Storage
    participant SB as Service Bus
    participant NTF as Notifier
    participant TEAMS as Teams
    participant EMAIL as Email

    U->>FE: Tap "Submit claim"
    FE->>API: POST /claims (JWT, receipt refs)
    API->>DB: INSERT claim (Submitted) + audit row

    alt receipts missing / upload failed
        API->>BLOB: HEAD receipts (verify present + scanned)
        BLOB-->>API: 404 / not all receipts found
        API->>DB: UPDATE status=Draft, reason="upload_failed" + audit row
        API-->>FE: 502 Bad Gateway (Retry-After: 5)
        FE-->>U: "Upload incomplete — tap retry"
    else receipts present and clean
        API-)SB: Publish claim.submitted (async)
        API-->>FE: 201 Created
    end

    opt Teams delivery fails
        SB-)NTF: Deliver claim.submitted (async)
        NTF->>TEAMS: POST Adaptive Card
        TEAMS-->>NTF: 5xx / timeout
        NTF->>EMAIL: Send approval email (fallback)
    end
```

### Notes
- **Receipts use the signed-URL pattern:** the Web App uploads **directly to Blob via
  SAS**, so 10 MB × 5 files never transit the API — protecting the 1.5 s submit SLO.
- **The write is one transaction:** claim row + audit row commit together, so the
  audit log can never disagree with claim state.
- **Notification is asynchronous** (`-)`): a slow/broken Teams webhook never blocks or
  fails the claimant's submit; the Notifier retries and falls back to email.
