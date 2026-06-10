# LearnLanka — Requirements Document

> **Author:** Buddhika Amarasinghe
> **Version:** v0.1 (Day 1)
> **Status:** Draft for founder review — contains open assumptions (see §5)

---

## 1. Problem Statement

O/L and A/L students in Sri Lanka struggle to find trustworthy, subject-specific
tutors who teach in their preferred language (Sinhala, Tamil, or English) and fit
their budget, while qualified tutors lack a simple way to advertise availability,
get paid reliably, and build a reputation. Today this matching happens through
word-of-mouth, scattered Facebook groups, and cash payments with no quality
signal or recourse. LearnLanka exists to connect a vetted tutor to the right
student for one-to-one online sessions, handle scheduling and payment end-to-end,
and let both sides rate each other so quality becomes visible and trust compounds
over time.

---

## 2. Personas

### Persona A — Nethmi, the Student (and her parent as payer)
- **Who:** A/L Combined Maths student in Gampaha; studies on an Android phone over mobile data. Her mother often makes the actual payment.
- **Goals:**
  - Find a tutor for a specific subject + grade in Sinhala within her family's budget.
  - Book a session at a time that fits around school, without phone-tag.
  - Feel safe that the tutor is genuine and that her card details aren't at risk.
- **Frustrations:**
  - Facebook tutor ads have no verified credentials or real reviews.
  - Data is expensive — a slow or heavy app on 3G is a dealbreaker.
  - Unsure who to complain to if a tutor no-shows.

### Persona B — Suresh, the Tutor
- **Who:** A part-time A/L Physics teacher in Jaffna who teaches in Tamil and English and wants extra income in evenings.
- **Goals:**
  - Publish the exact evening/weekend slots he is free, and stop double-bookings.
  - Get paid reliably and on time without chasing students for cash.
  - Build a star rating that wins him more bookings.
- **Frustrations:**
  - Students cancel last-minute and he loses the slot's income.
  - Manual scheduling across WhatsApp is chaotic.
  - No clarity on when/how much he gets paid after commission.

### Persona C — Dilani, the Operations Admin
- **Who:** LearnLanka staff member in Colombo responsible for tutor vetting, payouts, and dispute handling.
- **Goals:**
  - Vet and approve tutors before they appear in search.
  - Run the weekly payout cycle and reconcile commission accurately.
  - Resolve disputes (no-shows, refund requests) and act on PDPA deletion requests.
- **Frustrations:**
  - No single dashboard — data is scattered across the payment gateway and bank.
  - Hard to prove what happened in a dispute without a session record.
  - Manual, error-prone payout calculation.

---

## 3. Functional Requirements

> Each requirement is written as a testable capability and avoids prescribing a
> specific UI or implementation. IDs are grouped by persona.

### Student (FR-S)
- **FR-S1** A student can search the tutor catalogue and filter by **subject**, **grade**, **language** (Sinhala / Tamil / English), and **price band**.
- **FR-S2** A student can view a tutor's profile including verified subjects, languages, hourly rate, and aggregate rating.
- **FR-S3** A student can book a **1-hour** session against a tutor's published available slot.
- **FR-S4** A student can pay for a booking by **card** or **eZ Cash** before the session is confirmed.
- **FR-S5** A student can rate the tutor (**1–5 stars**) and leave a **one-line comment** after a completed session.
- **FR-S6** A student can view their upcoming and past bookings and join the video session at the scheduled time.

### Tutor (FR-T)
- **FR-T1** A tutor can publish, edit, and remove **availability slots**.
- **FR-T2** A tutor can **accept or decline** a booking request.
- **FR-T3** A tutor can **cancel** a confirmed booking provided it is **at least 12 hours** before the start time.
- **FR-T4** A tutor can rate the student (**1–5 stars**) and leave a **one-line comment** after a completed session.
- **FR-T5** A tutor can view their weekly earnings statement showing gross fees, the 15% commission deducted, and the net payout amount.

### Operations Admin (FR-O)
- **FR-O1** An admin can review and **approve or reject** a tutor application before the tutor becomes searchable.
- **FR-O2** The platform **calculates and records a 15% commission** on every *completed* session.
- **FR-O3** The platform **aggregates net amounts owed per tutor weekly** and an admin can trigger/confirm the **bank-transfer payout** run.
- **FR-O4** An admin can view a session/dispute record and **issue a refund or adjustment** within policy.
- **FR-O5** An admin can action a **PDPA data-deletion request** and record a **consent-capture** event at signup.

---

## 4. Non-Functional Requirements

| # | Category | Metric (SLI) | Target (SLO) | How we'll measure it |
|---|----------|--------------|--------------|----------------------|
| NFR-1 | Performance (Latency) | Tutor-search API response time, p95, from a Sri Lankan ISP | < 800 ms | Azure Application Insights + synthetic probe on Dialog/SLT network |
| NFR-2 | Availability | Successful-response % of the `/book` endpoint | 99.5% per calendar month | Azure Monitor availability test + synthetic transactions |
| NFR-3 | Scalability (Concurrency) | Active simultaneous video sessions supported | ≥ 200 within first 6 months | Daily.co / 100ms dashboard + load test before launch |
| NFR-4 | Privacy & Compliance | PDPA consent captured at signup; deletion request fulfilled within SLA | 100% consent capture; deletion completed ≤ 30 days | Audit log review; deletion-request ticket SLA report |
| NFR-5 | Payment Security | Cardholder data stored on LearnLanka servers | Zero (0) — all card data handled by PCI-DSS gateway (PayHere) | PCI-DSS SAQ; code/data-flow review confirming no PAN persisted |
| NFR-6 | Mobile Experience | Usable on mid-range Android over 3G | Largest Contentful Paint < 3 s on 3G profile; ≥ 80% flows verified on Android | Lighthouse mobile audit + real-device testing |
| NFR-7 | Localisation | UI strings available in all three languages at launch | 100% of strings translated (si / ta / en) | i18n coverage report (no missing-key fallbacks) |

---

## 5. Assumptions

Made because the brief was silent on these points:

1. **Authentication** is via mobile-number + OTP (SMS), since an SMS gateway is implied by the diagram hints but never specified.
2. **"Completed session"** means the scheduled 1-hour slot elapsed and at least one party joined the video room; this is the trigger for commission and payout.
3. **Cancellation/refund policy:** if a *tutor* cancels (≥12h) or no-shows, the student is fully refunded; student cancellation rules and any cancellation fee are **undefined** and assumed "full refund if ≥12h before".
4. **Currency** is LKR throughout; price bands and payouts are in LKR.
5. **Tutor vetting** is a manual admin process (credential/document check); no automated verification is assumed for v1.
6. **Weekly payout** runs on a fixed weekday (assume Monday) for the prior Sun–Sat period; minimum payout threshold is assumed to be zero (pay any positive balance).
7. **One subject per booking, one-to-one only** — no group sessions or packages/subscriptions.
8. **Ratings are visible publicly** in aggregate; individual student→tutor and tutor→student comments visibility rules are assumed (tutor ratings public, student ratings admin-only).
9. **eZ Cash** is reachable through the same gateway flow or a separate integration — integration owner is unspecified; assumed routed via PayHere where supported.
10. **Time zone** is Sri Lanka Standard Time (UTC+5:30) for all slots and the 12-hour cancellation window.

---

## 6. Out of Scope (for this version)

Things that could plausibly be in scope but are explicitly **not** being built now:

1. **In-house video calling** — outsourced to Daily.co / 100ms.
2. **Group / many-to-many classes, recorded courses, or subscription packages** — v1 is one-to-one, pay-per-session only.
3. **Native iOS app** — mobile-first responsive web / Android is the launch focus.
4. **In-app messaging / chat** between student and tutor outside of booking.
5. **Automated tutor credential verification** (e.g., document OCR) — vetting stays manual.
6. **Homework, content library, whiteboard, or learning materials** hosting.
7. **Promotions, referral codes, or discount engine.**
8. **Multi-currency / international tutors or students.**

---

### Open questions
See `buddhika-day1-ambiguity-log.md` for the full clarification list to take to the founders.
