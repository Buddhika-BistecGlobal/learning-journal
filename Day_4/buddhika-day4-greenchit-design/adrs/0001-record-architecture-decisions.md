# ADR 0001: Record architecture decisions using ADRs

## Status
Accepted (date: 2026-06-10)

## Context
- GreenChit will be handed between interns and, later, a real BISTEC team. Decisions
  made now (hosting, database, receipts) carry long-lived consequences but the *reasons*
  evaporate from memory and chat threads within weeks.
- New joiners repeatedly ask "why is it built this way?"; without a record, we either
  guess or re-litigate settled questions.
- We don't yet know how long GreenChit lives or how big the team grows — so the cost of
  *losing* rationale is unknown but asymmetric (cheap to write now, expensive to recover later).

## Decision
We record every architecturally significant decision as a short, numbered,
**Nygard-style ADR** in `adrs/NNNN-title.md`, committed alongside the code. An ADR is
**immutable once Accepted**; to change a decision we add a new ADR that supersedes the
old one (and mark the old one `Superseded by ADR-XXXX`). "Architecturally significant"
means it affects structure, a cross-cutting quality (security, cost, availability), or
is hard to reverse.

## Consequences
- **Easier:** onboarding (read the ADR log), design reviews (point at the ADR), and
  avoiding repeated debates on settled questions.
- **Harder:** there is a small, ongoing discipline cost — every significant change needs
  a few paragraphs written and reviewed, and the team must resist editing history.
- **Different:** decisions become artefacts we review in PRs, not hallway agreements.

## Alternatives considered
- **A wiki / Confluence page of decisions** — rejected: drifts from the code, no version
  history tied to the change that implemented it, and easy to silently edit.
- **No formal record (rely on commit messages + memory)** — rejected: commit messages
  explain *what* changed, rarely the *forces* behind a structural choice, and don't
  survive as a browsable log.
