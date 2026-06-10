# ADR 0003: Use Azure SQL as the system of record

## Status
Accepted (date: 2026-06-10)

## Context
- **Forces / data shape:** the domain is **relational and transactional** — a claim
  belongs to a claimant, references a manager, has many receipts, and produces an
  append-only stream of audit rows. Submit/approve must update claim state **and** write
  an audit row **atomically**. Finance needs **set-based queries and CSV export** over
  approved claims.
- **Team skills:** the team knows **SQL and EF Core** well; nobody has production Cosmos
  DB modelling/partition-key experience.
- **Constraints:** audit log must be **tamper-evident and kept 7 years**; only specific
  roles may read a claim (enforced in the app, but the store must support clean joins and
  row-level filtering).
- **What we don't yet know:** exact long-term row volumes — but even pessimistically this
  is thousands of claims/month, trivial for Azure SQL.

## Decision
We use **Azure SQL Database** as the single system of record for claims, receipt
metadata, and the audit log. We model claims/receipts/audit as related tables, wrap each
state transition (claim update + audit insert) in **one transaction**, and use
**EF Core** for data access. The audit table is **append-only** (no UPDATE/DELETE
granted to the app principal); tamper-evidence is provided via SQL **temporal/ledger
features** plus a periodic export to immutable (WORM) Blob storage for the 7-year hold.

## Consequences
- **Easier:** transactional integrity between claim and audit; straightforward joins and
  CSV/reporting queries; the team is immediately productive with EF Core; backups and PITR
  are managed.
- **Harder:** we own schema migrations and capacity/DTU sizing; horizontal write scaling is
  limited (acceptable at this load); the 7-year retention means a deliberate archive/cost
  strategy (move old partitions to cheaper tiers).
- **Different:** the data model is schema-first; adding fields means a migration, not just
  writing a new document shape.

## Alternatives considered
- **Azure Cosmos DB:** rejected — the data is relational with multi-entity transactions
  and reporting needs; Cosmos would force denormalisation, hand-rolled cross-document
  consistency for the claim+audit invariant, and a partition-key design the team has no
  experience with. Its global-distribution / massive-scale strengths are irrelevant to an
  internal tool with a few RPS.
- **Blob/table storage for the audit log only:** rejected as the *primary* store — it
  can't participate in the claim-update transaction, so claim state and audit could
  diverge. (We *do* use immutable Blob as the downstream 7-year archive, not the live store.)
