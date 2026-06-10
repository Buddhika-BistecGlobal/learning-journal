# ADR 0004: Store receipts in Blob Storage via SAS, scanned by Defender for Storage

## Status
Accepted (date: 2026-06-10)

## Context
- **Forces:** receipts are **up to 10 MB × up to 5 files per claim**; uploads must
  **succeed over intermittent office Wi-Fi**; the submit round-trip must stay **under
  1.5 s p95**; receipts are **untrusted user files** entering an internal finance system.
- **Constraints:** receipts must use **Azure Blob Storage with a signed-URL pattern**
  (mandated); cardholder/PII data and large binaries must not bloat the SQL database.
- **What we don't yet know:** real-world malware hit-rate on staff uploads (expected ~0,
  but a single infected receipt reaching a finance reviewer is unacceptable).

## Decision
The Web App uploads receipts **directly to Azure Blob Storage using short-lived,
per-file SAS URLs** issued by the Claims API (write-only, ~15-min expiry, scoped to one
blob path). Large files therefore **never transit the API**, protecting the submit SLO.
**Microsoft Defender for Storage** scans every uploaded blob; a receipt is marked
`scan=clean` before it becomes viewable/approvable. The API stores only the blob
reference + scan status in SQL. Client uploads are **chunked/resumable** to survive
flaky Wi-Fi.

## Consequences
- **Easier:** the API stays small and fast; storage scales independently; SAS gives
  least-privilege, time-boxed access; backups stay lean (no BLOBs in SQL).
- **Harder (genuinely uncomfortable):** scanning is **asynchronous**, so a receipt can sit
  in a **"pending scan"** limbo for seconds-to-minutes after upload — the claimant may tap
  Submit before the receipt is cleared, so the UX must handle "submitted, receipts still
  scanning," and the manager must not approve until clean. This adds real state and edge
  cases (what if scan never returns? what if it flags a false positive?). We accept this
  complexity as the cost of not shipping malware into finance.
- **Different:** receipt availability is **eventually consistent** with claim creation;
  the happy path has a scan gate that the sequence diagram must (and does) model.

## Alternatives considered
- **Upload receipts through the Claims API (API streams to Blob):** rejected — 50 MB of
  files per claim crossing the API blows the 1.5 s submit SLO and wastes App Service
  bandwidth/CPU; the SAS direct-upload pattern is mandated precisely to avoid this.
- **No malware scanning (trust internal users):** rejected — "internal" is not "trusted";
  one infected receipt opened by a finance reviewer is a serious incident, and Defender
  for Storage is a low-effort managed control.
- **A custom AV scan function (ClamAV in a container):** rejected for v1 — more code and
  ops than Defender for Storage for no added benefit at this scale (revisit only if
  Defender cost or coverage becomes a problem).
