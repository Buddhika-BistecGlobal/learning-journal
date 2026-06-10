# LearnLanka — User Story Set v0.1

> **Author:** Buddhika Amarasinghe
> Personas covered: **Student**, **Tutor**, **Operations Admin**.
> INVEST boxes are checked honestly — unticked boxes carry a one-line note.

---

## Story 1: Search & filter tutors
**As a** Student
**I want** to filter the tutor list by subject, grade, language, and price band
**So that** I quickly find a tutor who matches my exact need and budget

### Acceptance Criteria
- **Given** a student on the search screen **when** they set subject = "Combined Maths", grade = "A/L", language = "Sinhala" and tap Search **then** only tutors matching all four filters are returned.
- **Given** an active filter set **when** no tutor matches **then** an empty-state message is shown with a suggestion to relax a filter.
- **Given** a price-band filter **when** results return **then** every result card shows the tutor's hourly rate within that band.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [x] Small
- [x] Testable

---

## Story 2: Search results are fast (non-functional)
**As a** Student on mobile data
**I want** search results to come back quickly
**So that** I'm not wasting expensive data waiting on a slow screen

### Acceptance Criteria
- **Given** a logged-in student on a Sri Lankan ISP **when** they tap Search **then** the first page of results loads within **800 ms at p95**.
- **Given** results returned **then** each card shows tutor name, language, hourly rate, and rating.
- **Given** a slow network (3G profile) **when** results are loading **then** a skeleton/loading state appears within 300 ms.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [ ] Estimable — *latency target depends on data volume and search tech not yet chosen; estimate is rough.*
- [x] Small
- [x] Testable

---

## Story 3: Book and pay for a session
**As a** Student
**I want** to book a 1-hour slot and pay by card or eZ Cash
**So that** my session is confirmed and the tutor is reserved for me

### Acceptance Criteria
- **Given** a tutor with an open slot **when** the student selects it and completes payment **then** the booking moves to "Confirmed" and the slot is no longer bookable by others.
- **Given** a payment that fails or is abandoned **when** the student exits **then** the slot is released and no booking is created.
- **Given** a confirmed booking **then** the student receives a confirmation (SMS/in-app) with the session time and join link.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [ ] Small — *bundles slot-locking + payment; likely splits into "reserve slot" and "take payment" during planning.*
- [x] Testable

---

## Story 4: Publish availability and manage bookings
**As a** Tutor
**I want** to publish my available slots and accept or decline requests
**So that** I control my schedule and avoid double-bookings

### Acceptance Criteria
- **Given** a tutor on their calendar **when** they add a free slot **then** it becomes visible/bookable to students.
- **Given** an incoming booking request **when** the tutor accepts **then** it is confirmed; **when** they decline **then** the slot reopens and the student is notified.
- **Given** a confirmed booking **when** the tutor attempts to cancel **then** cancellation is only allowed if it is **≥ 12 hours** before start time.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [ ] Small — *covers publish + accept/decline + cancel; should be three stories in a sprint.*
- [x] Testable

---

## Story 5: See weekly earnings and get paid
**As a** Tutor
**I want** to see my net earnings after the 15% commission and receive weekly bank payouts
**So that** I trust the platform pays me correctly and on time

### Acceptance Criteria
- **Given** completed sessions in a week **when** the tutor opens earnings **then** they see gross fees, 15% commission deducted, and net payable.
- **Given** the weekly payout run **when** it completes **then** the net amount is transferred via bank and the statement is marked "Paid" with a reference.
- **Given** a cancelled or no-show session **then** it is excluded from the payout total.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [ ] Estimable — *depends on Sampath Vishwa payout integration details still unknown.*
- [x] Small
- [x] Testable

---

## Story 6: Vet tutors before they go live
**As an** Operations Admin
**I want** to review and approve tutor applications before they appear in search
**So that** only vetted tutors are offered to students and platform trust is protected

### Acceptance Criteria
- **Given** a new tutor application **when** the admin approves it **then** the tutor becomes searchable and is notified.
- **Given** an application **when** the admin rejects it with a reason **then** the tutor is notified and does not appear in search.
- **Given** a pending application **then** it never appears in student search results.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [x] Small
- [x] Testable

---

## Story 7: Rate each other after a session
**As a** Student or Tutor
**I want** to rate the other party 1–5 stars with a one-line comment after the session
**So that** quality becomes visible and future matches are better informed

### Acceptance Criteria
- **Given** a completed session **when** the participant submits a 1–5 star rating and one-line comment **then** it is saved and reflected in the aggregate rating.
- **Given** a session that has not completed **then** the rating action is unavailable.
- **Given** a participant has already rated **when** they revisit **then** they cannot submit a second rating for the same session.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [x] Small
- [x] Testable

---

## Story 8: PDPA consent & deletion (compliance)
**As an** Operations Admin
**I want** consent captured at signup and a way to fulfil deletion requests
**So that** LearnLanka complies with Sri Lanka's PDPA 2022

### Acceptance Criteria
- **Given** a new user signing up **when** they complete signup **then** an explicit consent event is recorded with timestamp and version.
- **Given** a verified deletion request **when** the admin actions it **then** the user's personal data is deleted/anonymised within the SLA and an audit record is kept.

### INVEST self-check
- [x] Independent
- [x] Negotiable
- [x] Valuable
- [x] Estimable
- [x] Small
- [x] Testable
