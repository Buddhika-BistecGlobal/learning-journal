# LearnLanka — Ambiguity Hunt Log

> **Author:** Buddhika Amarasinghe

## Brief reference

> "LearnLanka is a Colombo-based startup that connects O/L and A/L students with
> vetted tutors for one-to-one online sessions. Students must be able to **search
> for tutors by subject, grade, language (Sinhala, Tamil, English), and price
> band**... book a **1-hour session** and **pay via card or eZ Cash**. Tutors...
> **publish availability slots, accept or decline bookings, and cancel with at
> least 12 hours notice**. The platform must **charge a 15% commission on every
> completed session and pay tutors weekly via bank transfer**. Both parties must
> be able to **rate each other (1-5 stars)** and leave a one-line comment.
> ...support **200 simultaneous video sessions**... comply with **Sri Lanka PDPA
> 2022 — consent capture, deletion request flow**... payment data **never stored
> on LearnLanka servers**."

*(Ambiguous phrases highlighted in bold above are unpacked below.)*

## Findings

| # | Quote | Why ambiguous | Clarification question | Priority |
|---|-------|---------------|------------------------|----------|
| 1 | "**vetted** tutors" | "Vetted" has no defined criteria, owner, or process — manual vs automated, what documents, who approves. | What are the exact tutor-vetting steps and acceptance criteria, and who owns approval? | H |
| 2 | "charge 15% commission on every **completed session**" | "Completed" is undefined — does a no-show, partial join, or technical failure count? This gates revenue and payouts. | What event marks a session "completed" for the purpose of commission and payout? | H |
| 3 | "cancel with at least **12 hours notice**" | Only the *tutor* side is stated. Student cancellation rules, fees, and refund handling are silent. | What are the student-side cancellation, refund, and no-show rules (and any fee)? | H |
| 4 | "pay tutors **weekly** via bank transfer" | "Weekly" lacks a cutoff day, period boundary, currency, and minimum-payout threshold. | Which day does the payout run, what period does it cover, and is there a minimum payout amount? | M |
| 5 | "pay via **card or eZ Cash**" | eZ Cash is a separate mobile-money rail; brief says gateway is PayHere but doesn't say eZ Cash routes through it. | Does eZ Cash go through PayHere, or is it a separate integration we must build/own? | H |
| 6 | "**price band**" | Price band is undefined — fixed buckets, tutor-set, or platform-set? Affects search and pricing model. | What are the price bands, who sets the hourly rate, and is it tutor-set or platform-controlled? | M |
| 7 | "**rate each other** ... one-line comment" | Visibility, moderation, and editability of ratings/comments are unspecified — esp. student→tutor vs tutor→student. | Who can see each rating/comment, can they be edited or moderated, and are they tied to identity? | M |
| 8 | "support **200 simultaneous video sessions**" | Concurrency target given, but peak distribution (exam season) and growth beyond 6 months are silent. | What is the expected daily/seasonal peak pattern, and the 12-month concurrency growth target? | M |
| 9 | "comply with **PDPA 2022 — deletion request flow**" | No SLA, no scope (which data, financial records exempt?), no verification of requester identity. | What is the deletion SLA, which records are exempt (e.g., financial/tax), and how do we verify the requester? | H |
| 10 | "payment data **never stored** on LearnLanka servers" | Boundary unclear — does this include last-4 digits, tokens, payout bank details, transaction IDs? | Which data fields are forbidden vs allowed (tokens, last-4, bank account for payouts)? | M |
| 11 | "**search by ... language** (Sinhala, Tamil, English)" | Is language the *tutor's teaching language*, the *UI language*, or both? They are different concepts. | Does the language filter mean the tutor teaches in that language, or the session/UI language? | L |
| 12 | "**one-to-one** online sessions" / "1-hour session" | Fixed 1-hour only? No 30-min or 2-hour options, no group, no recurring packages — needs confirming. | Is session length fixed at exactly 1 hour, and are recurring bookings or packages ever in scope? | L |
| 13 | "connects **O/L and A/L students**" | Are students under 18 (minors)? PDPA + payments by a parent raise consent and guardian-account questions. | Are accounts for minors, and does a parent/guardian own the account and consent? | H |

## Results Summary

| Metric | Target | Achieved |
|--------|--------|----------|
| Items found | 10+ | 13 |
| High-priority items | 3+ | 5 (#1, #2, #3, #5, #9, #13 → 6) |
| Items convertible to test cases | 5+ | 8 (#2, #3, #4, #5, #6, #8, #10, #12) |

## Top 3 questions to ask the founders

1. **What event marks a session "completed"?** (Item #2) — it gates commission, tutor payouts, and refunds; nothing about money works until this is pinned down.
2. **Does eZ Cash route through PayHere or is it a separate integration we own?** (Item #5) — this is a build-vs-integrate decision that changes scope and timeline.
3. **Are students minors, and does a parent/guardian own the account and provide consent?** (Item #13) — drives PDPA consent design, payment ownership, and account model.

## Reflection

- **What kind of ambiguity tripped me up most?** Words that *sound* concrete but hide a process — "vetted" and "completed session." They read as done decisions, but each conceals an entire workflow with money and trust attached.
- **Which question most likely changes the architecture?** The eZ Cash routing question (#5). If it's a separate rail, we need a second payment integration, a different reconciliation path, and possibly a payment-abstraction layer — versus one gateway flow if PayHere covers it. The minors/guardian question (#13) is a close second because it reshapes the account and consent model. Ambiguity is expensive because each unanswered word here can mean weeks of rework if assumed wrong — far cheaper to ask before any code is written.
