# GreenChit — Architecture Design Pack

> **Author:** Buddhika Amarasinghe · **Date:** 2026-06-10
> Internal BISTEC reimbursement-claims tool: submit with receipts → manager approval →
> finance CSV export to payroll, with a 7-year tamper-evident audit trail.

## Repository layout

```
greenchit-design/
├── README.md
├── diagrams/
│   ├── container-diagram.png        # C4 L2 (rendered)
│   ├── container-diagram.drawio     # editable source
│   ├── component-diagram.png        # C4 L3 — Claims API (rendered)
│   ├── component-diagram.drawio     # editable source
│   ├── sequence-submit-approve.md   # Mermaid (happy + error paths)
│   └── sequence-submit-approve.png  # rendered Mermaid
├── adrs/
│   ├── 0001-record-architecture-decisions.md
│   ├── 0002-hosting-platform.md
│   ├── 0003-database-choice.md
│   └── 0004-receipts-storage-and-virus-scan.md
└── trade-offs/
    └── hosting-options.md
```

The full prose design pack is the top-level `buddhika-day4-greenchit-design.md`; the
trade-off table + design-review feedback is `buddhika-day4-trade-offs-and-review.md`.

## Reading order (how to walk this pack)
1. **`buddhika-day4-greenchit-design.md` §1** — system context and the four roles.
2. **`diagrams/container-diagram.png`** — runtime pieces; follow solid (sync submit/approve)
   vs orange-dashed (async `claim.*` → Notifier → Teams/Email).
3. **`diagrams/component-diagram.png`** — zoom into the Claims API (Controllers → Auth →
   Claims Service → Receipts/Notifications/Audit/Export → Persistence).
4. **`diagrams/sequence-submit-approve.md`** — the submit-and-approve journey over time,
   including the receipt-upload error path. Lifelines match container names exactly.
5. **`adrs/`** — *why* App Service (0002), *why* Azure SQL (0003), *why* SAS + Defender
   scanning (0004); 0001 is the meta-ADR.
6. **`trade-offs/hosting-options.md`** — the scored A-vs-B argument behind ADR-0002.

## Key decisions at a glance
- **Host:** Azure App Service monolith (ADR-0002) — fastest to ship, simplest to operate
  for a 10-person team; accepts "redeploy everything" as the trade.
- **Data:** Azure SQL (ADR-0003) — relational claim+audit with one-transaction integrity.
- **Receipts:** Blob Storage via short-lived SAS, scanned by Defender for Storage
  (ADR-0004) — files bypass the API to protect the 1.5 s submit SLO.

## Reproduce the diagrams
- C4 PNGs: `python ../render_day4_diagrams.py` (Pillow).
- Sequence PNG: `npx -y @mermaid-js/mermaid-cli -i diagrams/sequence-submit-approve.mmd -o diagrams/sequence-submit-approve.png -t neutral -b white -s 2`
  (or paste the Mermaid block into <https://mermaid.live>).
