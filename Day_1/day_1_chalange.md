Challenge Overview¶
LearnLanka is a Colombo-based startup that connects O/L and A/L students with vetted tutors for one-to-one online sessions. They have a one-paragraph brief, no diagrams, and three contradictory expectations from the founders. Your job is to turn the brief into a clear requirements document, a C4 Context diagram, a user story set, and a list of clarification questions the team should ask before any code is written.

Time Allocation: 3 hours (during session) Difficulty: Beginner

Business Requirements¶
Functional Requirements¶
Students must be able to search for tutors by subject, grade, language (Sinhala, Tamil, English), and price band
Students must be able to book a 1-hour session with a tutor and pay via card or eZ Cash
Tutors must be able to publish availability slots, accept or decline bookings, and cancel with at least 12 hours notice
The platform must charge a 15% commission on every completed session and pay tutors weekly via bank transfer
Both parties must be able to rate each other (1-5 stars) and leave a one-line comment after the session
Non-Functional Requirements¶
Tutor search results: returned in under 800 ms at the 95th percentile from a Sri Lankan ISP
Availability: 99.5% monthly uptime, measured against the booking endpoint
Concurrent sessions: support 200 simultaneous video sessions in the first 6 months
Privacy: comply with Sri Lanka Personal Data Protection Act 2022 — consent capture, deletion request flow
Payment data: never stored on LearnLanka servers — must use a PCI-DSS compliant gateway
Technical Constraints¶
Mobile-first product — at least 80% of usage is expected on Android devices
The team has Azure credits; preferred cloud is Azure (App Service, Azure SQL, Blob Storage)
Video calling will be outsourced to a third-party (Daily.co or 100ms) — not built in-house
Payment gateway will be PayHere; bank payouts will be Sampath Vishwa
All UI strings must support Sinhala, Tamil, and English from launch
Deliverables¶
1. Requirements Document (25 points)¶
File: {your-name}-day1-requirements.md

Required Sections:


# LearnLanka — Requirements Document

## 1. Problem Statement
- One paragraph describing the user problem in your own words

## 2. Personas
- Three personas (Student, Tutor, Operations Admin) with goals and frustrations

## 3. Functional Requirements
- Numbered list, grouped by persona, each requirement testable

## 4. Non-Functional Requirements
- Table with columns: Category, Metric, Target, How we'll measure it

## 5. Assumptions
- Numbered list of every assumption you made because the brief was silent

## 6. Out of Scope
- What you are explicitly NOT building in this version
Evaluation Criteria: - Each functional requirement is testable and free of solution bias (5 pts) - Non-functional requirements have measurable targets (no "fast", "secure", "user-friendly" without numbers) (5 pts) - Personas are distinct and have specific goals, not generic descriptions (5 pts) - Assumptions section captures at least 6 silent gaps in the brief (5 pts) - Out-of-scope section names at least 4 things that could be in scope but are not (5 pts)

2. C4 Context Diagram (25 points)¶
File: {your-name}-day1-context-diagram.png (exported from draw.io or Excalidraw) plus the source .drawio or .excalidraw file

Required Diagram Elements:

Element	Notation	Examples in this scenario
Person	Stick figure with role label	Student, Tutor, Ops Admin
System in scope	Single labelled box at the centre	"LearnLanka Platform"
External system	Differently-shaded box	PayHere, Daily.co, Sampath Vishwa, SMS gateway
Relationship	Labelled arrow with verb + protocol	"Books session via HTTPS", "Sends OTP via SMS"
Minimum Functionality: - [ ] Three person actors are present and labelled with role - [ ] LearnLanka Platform is the only "system in scope" box - [ ] At least four external systems are shown - [ ] Every arrow has a verb-led label and an indication of protocol or channel - [ ] A short legend explains the notation used

Evaluation Criteria: - All actors and external systems from the brief are present (5 pts) - Boundary between "in scope" and "external" is unambiguous (5 pts) - Every relationship has a verb + protocol label (5 pts) - Diagram readable when shrunk to A5 size (visual hygiene) (5 pts) - Legend is accurate and matches notation used in the diagram (5 pts)

3. User Story Set (25 points)¶
File: {your-name}-day1-user-stories.md

Required Content:


# LearnLanka — User Story Set v0.1

## Story 1: {Short title}
**As a** {persona}
**I want** {capability}
**So that** {outcome}

### Acceptance Criteria
- **Given** {context} **when** {action} **then** {observable outcome}
- **Given** ... **when** ... **then** ...

### INVEST self-check
- [ ] Independent
- [ ] Negotiable
- [ ] Valuable
- [ ] Estimable
- [ ] Small
- [ ] Testable

---

(Repeat for at least 6 stories covering Student, Tutor, and Ops Admin personas.)
Code Requirements: - At least 6 stories, covering all three personas - Each story has 2-5 Given/When/Then acceptance criteria - INVEST self-check completed honestly per story (with a one-line note if a box is not ticked)

Evaluation Criteria: - Stories follow As a / I want / So that format with no solution bias (5 pts) - Acceptance criteria use Given/When/Then and are observable (5 pts) - All three personas are represented across the set (5 pts) - INVEST self-check is honest — not all boxes blindly ticked (5 pts) - At least one story explicitly captures a non-functional concern (e.g., search latency) (5 pts)

4. Ambiguity Hunt Log (25 points)¶
File: {your-name}-day1-ambiguity-log.md

Required Tests/Validations:

#	Quote from brief	Why it is ambiguous	Clarification question	Priority (H/M/L)
1	...	...	...	H
2	...	...	...	M
...	...	...	...	...
Report Format:


# LearnLanka — Ambiguity Hunt Log

## Brief reference
- Source paragraph (paste verbatim, then highlight ambiguous phrases)

## Findings
| # | Quote | Why ambiguous | Clarification question | Priority |
|---|-------|---------------|------------------------|----------|

## Results Summary
| Metric | Target | Achieved |
|--------|--------|----------|
| Items found | 10+ | ? |
| High-priority items | 3+ | ? |
| Items convertible to test cases | 5+ | ? |

## Top 3 questions to ask the founders
- 1. ...
- 2. ...
- 3. ...

## Reflection
- What kind of ambiguity tripped you up most?
- Which question is most likely to change the architecture if answered?
Evaluation Criteria: - At least 10 distinct ambiguities identified (5 pts) - Each entry explains why it is ambiguous, not just that it is (5 pts) - Clarification questions are specific and answerable (no "tell me more about X") (5 pts) - Priority assignment matches business impact (5 pts) - Reflection demonstrates understanding of why ambiguity is expensive (5 pts)

Submission Guidelines¶
File Naming Convention¶

{your-name}-day1-requirements.md
{your-name}-day1-context-diagram.png
{your-name}-day1-context-diagram.drawio
{your-name}-day1-user-stories.md
{your-name}-day1-ambiguity-log.md
Submission Checklist¶
Requirements document complete with all 6 sections
Context diagram exported as PNG with source file alongside
User story set with at least 6 stories and INVEST checks
Ambiguity log with at least 10 entries and reflection
All files follow naming convention
Pushed to your intern-onboarding GitHub repo before midnight
Scoring Guide¶
Grade	Score	Description
Exceptional	90-100	Requirements are stakeholder-ready; diagram could be shown to a customer; ambiguity log surfaces issues a senior would have missed
Proficient	75-89	Solid grasp of functional/NFR split, INVEST stories, and C4 Context level; minor gaps in measurability or boundary clarity
Developing	60-74	Requirements present but mix solutions with needs; diagram has scope confusion; few high-priority ambiguities found
Beginning	<60	Requirements written as a wish list with no measurable NFRs; diagram missing or wrong notation; ambiguity log shallow
Passing Score: 75%

Hints and Tips¶
Use Given/When/Then so QA can lift the criteria into a test¶

Given a logged-in Student on the search screen
And the subject filter is set to "Combined Maths"
When they tap "Search"
Then the first page of results loads within 800 ms
And every result card shows tutor name, language, hourly rate, and rating
Make non-functional requirements measurable using a SLI/SLO frame¶

| Category   | Metric (SLI)                          | Target (SLO)         | Measurement source         |
|------------|----------------------------------------|----------------------|----------------------------|
| Latency    | Search API response time, p95          | < 800 ms             | Azure Application Insights |
| Availability | /book endpoint successful response % | 99.5% per calendar mo| Azure Monitor + synthetic  |
| Concurrency| Active video sessions                  | >= 200 simultaneous  | Daily.co dashboard         |
Draw the Context diagram in plain text first, then click¶

[Student] ----- searches & books -----> ( LearnLanka Platform )
[Tutor]   ----- offers slots ----------> ( LearnLanka Platform )
( LearnLanka Platform ) -- charges card via HTTPS --> [PayHere]
( LearnLanka Platform ) -- starts video room ------>  [Daily.co]
( LearnLanka Platform ) -- sends OTP via HTTPS ----> [SMS Gateway]
( LearnLanka Platform ) -- pays tutors via SFTP ---> [Sampath Vishwa]
Once the textual sketch is right, the draw.io version is just translation.