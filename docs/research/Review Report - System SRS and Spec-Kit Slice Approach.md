# Review Report: System SRS and Spec-Kit Slice Approach

> **Status (2026-11-05).** Point-in-time review from 2026-10-17 against then-current drafts. Where this report conflicts with [Requirements Method and Governance](../system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md) Draft 0.6 (or later), Governance wins. Do not treat findings here as current baseline.

*Prepared for Phan Duy · Reviewer: Claude · Review round 1 · 17 October 2026 · Project: DP Stock-Investment Assistant*

## 1. Executive summary

**Verdict.** The direction is right: a slim, system-wide SRS in the agent-SRS format, cut into spec-kit slices that cite requirement IDs, with EARS statements, Given/When/Then acceptance and one coverage file. It suits a project whose hardest rules (the Decision gate, identity, evidence integrity) cross domains and need testable wording. What exists today is a good skeleton, not yet load-bearing: it covers 3 of the 7 Phase 1 P0 deliverables, covers none of the riskiest rules, and several documents already disagree with each other.

**Overall: 3.0 / 5, a promising foundation.** Scores are my judgment on the documents I could read (section 2).

**Five findings that matter most**

1. Identity is the prerequisite for every Core write (architecture §1.2), yet the SRS defers it (OI-1) and has no identity requirement. SR-9.1.1 and SNR-3.2.1 cannot be verified, and the first slice has nothing to cite.
2. The riskiest Phase 1 rules have no requirement: atomic Pass, a Decision record on both outcomes, Position only via Pass, and the Sandbox never mutating Portfolio risk (architecture quality goal 1; Spec §4.7 #4 and #8).
3. 24 of the 32 P0 lines are the legacy chat platform, written as an as-built baseline. Only 8 P0 lines express the Phase 1 product, and priority and phase share one column.
4. Verifiability is thin: 6 lines in an EARS pattern, no Given/When/Then, and “Spec Coverage” is “—” on all 43 SR rows. Several lines (“contextually relevant”, “normal load”, “confidence”) cannot be tested as written.
5. Documents drift: the SRS cites the agent SRS as v2.2 / 302 items (you report v2.9 / 438), Spec §6 still describes the pre-SRS hierarchy, version pointers are stale, and the SRS, README and architecture disagree on Socket.IO and container shape.

**Five actions, in order** (detail in section 8): add the identity and gate/Position requirement families before the first slice; fix the drift items in one pass; split Priority from Phase and Status; adopt the slice template plus a small ID and coverage lint; write success criteria for this experiment.

## 2. Scope and evidence

| Material | How I used it |
| --- | --- |
| System SRS Draft 0.2.2 (uploaded) | Read in full; counted IDs, priorities, EARS patterns |
| Product Specification v1.7.4 (uploaded) and v1.7.2 (pasted) | Read in full; v1.7.4 used for the §5.3 trace column and §6 |
| IA map v1.0.1, Journeys v1.0.2, Architecture overview v0.8.4, AGENTS.md, README | Read in full from the pasted text |
| Agent SRS v2.9 and `SRS_SPEC_TRACEABILITY.md` v3.4 | Known only from your message (438 items, 226 linked, 212 not) |
| Requirements method and governance doc, methodology doc, constitution, ADRs, `specs/`, registry, code | Not seen. Findings about them are limited to how the documents I did see refer to them |

## 3. The approach as a chain

| Link in the chain | State today |
| --- | --- |
| Spec §5.3 deliverable → SRS IDs | Done for 3 of 7 Phase 1 P0 items (Requirements column, Spec v1.7.3). The other 4 say “pending”. P1 and Phases 2–4 are empty |
| SRS ID → slice `spec.md` | No slice cites an ID yet. The Spec Coverage column is “—” on all 43 SR rows |
| Slice → EARS and Given/When/Then | No template yet. The SRS has 6 EARS-pattern lines (all pilot lines) and 0 Given/When/Then |
| Registry rows | Deferred for pilot IDs until a slice first cites them (SRS §9.1) |
| Registry → code and tests | `sync_spec_status.py` exists per README; not seen |

## 4. Scorecard

| Aspect | Score | One-line reason |
| --- | --- | --- |
| Approach selection and rationale | 4.0 | The hybrid fits the gate, identity and evidence rules; the feature-ranking layer already exists in Spec §5.3 |
| Document hierarchy and authority | 3.5 | Clear split of owners; no Spec-versus-SRS conflict rule |
| SRS structure and ID design | 3.5 | Stable anchors and domain allocation; mixed row shapes |
| Requirement quality (verifiability) | 2.5 | Many lines untestable as written |
| Phase 1 coverage | 2.0 | 3 of 7 P0 deliverables; none of the gate rules |
| Traceability design | 3.0 | Right chain, but three coverage records and no automated check |
| Cross-document consistency | 2.5 | At least 18 drift items (Appendix A) |
| Non-functional requirement quality | 2.5 | No thresholds, no NFR for the architecture’s top goals |
| Fit with SDD and agentic workflow | 3.5 | AGENTS.md is strong; slice template and ID rule not yet in it |
| Governance proportionality and delivery risk | 3.0 | Heavy document churn while all six Core modules are still absent |

## 5. What works well

- **Reuse of a known pattern.** The agent SRS already proves the format (ID, priority, allocation, traceability file), so the team is not learning a new method.
- **Slim by design.** SRS lines hold an ID, one sentence, priority and a References column pointing to Spec, IA, Journeys and architecture anchors. Meaning is not copied, so it cannot fork.
- **Domain allocation per line.** The Primary and Contributing columns make ownership visible, which suits a Backend-owns-Core, Agent-advises design.
- **Pilot first.** Seeding only the first three P0 items and deferring registry rows until a slice needs them is a sensible way to learn before committing the whole product.
- **Honest dependency and uncertainty marks.** SR-9.1.1 states its dependency on the identity slice; SR-4.4 is marked draft; OI-6 admits “confidence” is undefined.
- **Machine-checkable anchors.** `<a id>` tags let the Spec §5.3 table link straight to SRS lines, so the Spec → SRS hop is real, not prose.
- **Strong single homes.** One glossary (Spec §0.2), one ontology (§4.6), one layout lock (IA §2.6), one agent write rule (architecture §4.2.2). This is what lets a short SRS stay short.
- **Agent-safe working rules.** AGENTS.md forbids edits on the main tree, commits without approval, and promotes content to `docs/` only after verification.

## 6. Findings by aspect

### 6.1 Approach selection

- Option 1 (agent SRS only) cannot hold Core objects, identity or the gate. Option 6 duplicates what exists: the feature pitch is the Spec §5.3 table, and its Requirements column is the feature map. Option 7 is largely the Journeys (J-TFI-1 and J-TFI-2 are step-by-step) and is weak on non-functional requirements.
- So the hybrid is justified, but do not add a separate “pitch” document. Use Spec §5.3 for value ranking, SRS for testable lines, Journeys steps as the source of Given/When/Then.
- On “link or fold” the agent SRS: link it. Folding 438 items into a 67-line master would swamp it and create two numbering schemes (SR and FR) in one file. Add an allocation rule instead: every FR cites a parent SR, or is marked domain-local.

### 6.2 Hierarchy and authority

- Four documents state an authority order (Spec §0.1, SRS §3.1, architecture §1.6, AGENTS.md). They are compatible, but SRS §3.1 has no rule for a conflict between Spec and SRS. Suggested rule: Spec wins on meaning (what and why); the SRS is amended to match; the SRS owns the testable “SHALL” wording.
- Spec §0.1 still lists the SRS as “out of scope for this conceptual lane”, and Spec §6.1, §6.2 and §6.4 describe Spec → domain specs → tasks with no SRS tier and no “Requirements covered”, EARS or Given/When/Then in the skeleton. The Spec’s own derivation guidance is now out of date.
- SRS §3 describes the Spec as a “master charter” with “360° company lenses”. That is the Capabilities charter’s description, not the Spec’s.
- Term collisions: in the SRS, “workspace”, “session” and “portfolio” mean stored records; in the Spec, the Adaptive Workspace is the UI shell. Architecture risk R6 already warns about this. Add the same “Spec glossary wins” rule to the SRS.

### 6.3 SRS structure and ID design

- **Priority carries phase.** SR-1.3.3 reads “P2 (Future, not Phase 1)”. Add separate Phase and Status columns so “Phase 1 P0” is a query, and “*(draft)*” leaves the titles.
- **Two row shapes in one family.** Pilot lines have a References column; legacy lines do not. SNR-3 has References, other SNR tables do not.
- **One owner per line.** SR-4.4.1 has two primaries (Backend, Data). Pick one and list the other as contributing.
- **Atomicity.** SR-9.1.1 joins two requirements (capture evidence; owner-scoped). Split them so each can pass or fail alone.
- **Coverage column.** “Spec Coverage” duplicates the registry, the SNR tables have no such column, and the agent traceability file is a third record. Make the registry the only source and generate the rest.

### 6.4 Requirement quality and verifiability

| Line | Problem |
| --- | --- |
| SR-1.3.2 “preserve the context of the open work” | “Context” is undefined; no observable check |
| SR-3.1.1 “contextually relevant analysis” | Not testable |
| SR-4.4.2 “source, timestamp and confidence” | “Confidence” undefined (OI-6); blocks the line |
| SNR-1.1.1, SNR-1.1.2 “under normal load” | Load not defined. Architecture §1.2 says latency targets are “owner to supply”, so the 2 s and 5 s figures are unowned |
| SNR-1.2.1 “appropriate TTLs” | No value, no test |

Every P0 line for Phase 1 needs three things: an EARS sentence, up to three Given/When/Then scenarios in its slice, and a stated verification method (test, inspection or demo). The Journeys steps (for example J-TFI-1.3 and J-TFI-2.3) are ready-made scenario sources.

### 6.5 Phase 1 coverage and priority balance

| Spec §5.3 P0 deliverable | SRS today | Gap |
| --- | --- | --- |
| Adaptive Visual Canvas | SR-1.3.1, 1.3.2, 1.3.4 | Reasonable; saved presets are P1 and absent |
| Vietnam-first Data Hub and provenance | SR-4.4.1–3 (draft) | No licence rule (R4), no stale or degraded display, “confidence” undefined |
| Insights foundation | SR-9.1.1–2, SNR-3.2.1 | Blocked by identity |
| Dual-Track Workspace IA | None (SR-1.3.1 only partly) | “Sandbox never mutates Portfolio risk” (Spec §4.7 #4) has no line |
| Living Thesis and Bull/Bear | None | Versioning, recoverable versions, two stances, AI-assisted tag |
| Decision gate and checklist | None | Checklist fixed at open, Pass only when mandatory items met, atomic Pass, idempotency, Decision record on both outcomes |
| Portfolio, Position, optional Case | None | Legacy SR-4.3.2 (“create portfolios and track positions”, P2) conflicts with “only Pass creates a Position” (Spec §4.6 #3) |

The five architecture quality goals map poorly to SNRs: goal 1 (gate atomicity) and goal 4 (a degraded answer is never a wrong one) have none; goal 2 (isolation) is SNR-3.2.1 but unverifiable; goal 3 (evidence integrity) is only partly SR-4.4.2. Read as a whole, the SRS currently looks like a chat platform baseline with a small Phase 1 pilot attached; mark legacy lines as “as-built baseline” so they do not dilute the Phase 1 P0 list.

### 6.6 Traceability

- The chain is right, and deferring registry rows during a pilot is acceptable. The risk is that nothing enforces it. The agent SRS (226 of 438 linked) shows how coverage drifts without a gate.
- Aim for “100% of Phase 1 P0 IDs linked before their slice starts”, not an overall percentage.
- Status gates are named differently: SRS §9.1 says `analyzed → planned → implemented → verified`; README §4.3 says `clarified → planned → implemented → verified`. Pick one.
- SRS §9.2 says requirements are verified through slice acceptance, not SRS-level tests. That makes the Given/When/Then in slices the only evidence, so “verified” must require executable evidence.

### 6.7 Cross-document consistency

The full register is in Appendix A. The pattern: version pointers and footers lag headers; the SRS still describes the as-built platform (Socket.IO, an Agent shown as its own domain, a 3-container README) where the architecture overview has already moved to four containers with the Agent in-process; and two roadmaps exist (README milestones M3–M7 against Spec Phases 1–4; README puts long-term memory in “Q3 2026”, which has passed, while the Spec puts it in Phase 4).

### 6.8 Non-functional requirements

- Missing lines that the architecture already treats as high risk: atomic gate and idempotency (R2, rated H/H), degraded-not-wrong output, privacy and retention (R11), data minimisation to model providers (R10), prompt-injection handling (R3) and rate limiting (OI-2, against R1 rated H/H).
- No authentication requirement exists even though Auth0 is accepted in part (ADR-SYS-001).
- SNR-6.1.3 (56% coverage) is a process gate from AGENTS.md rather than a product quality; keep it, but label it as a delivery gate.
- Define “normal load” once and reference it.

### 6.9 Fit with SDD and agent workflow

- AGENTS.md covers the flow, the safety rules and the promotion rule well. It does not yet say: cite SRS IDs in every slice, write EARS and Given/When/Then, or use the slice template. Ensure `speckit.specify` includes a “Requirements covered” section and `speckit.analyze` checks that cited IDs exist.
- **Context cost.** The SRS is about 9k tokens, the Spec about 14k, the architecture overview larger still. Give each slice a compact context pack: its `spec.md`, the cited SRS rows, and the cited Spec and IA anchors only.
- **Slice order follows requirement dependencies:**

| Order | Slice | Depends on | Requirements |
| --- | --- | --- | --- |
| S0a | Identity and per-user isolation | ADR-SYS-001 open items (token storage, role map) | New identity family; SNR-3.2.1 |
| S0b | Datastore ready for atomic writes | ADR-SYS-002 (replica set; `mongo:5.0` is past end of life) | New atomicity SNR |
| S1 | Workspace shell and zones | None | SR-1.3.1, 1.3.2 |
| S2 | Data hub and provenance | OI-6, ADR-SYS-004, licence rule | SR-4.4.1–3 |
| S3 | Insights | S0a, S2 | SR-9.1.1–2 |
| S4 | Working Thesis with Bull/Bear | S3 | To add |
| S5 | Decision gate and Position | S0a, S0b, S4 | To add; SR-1.3.4 |

S1 and S2 can run in parallel with S0.

### 6.10 Governance proportionality and delivery risk

- **Churn.** The Spec went through 7 versions in 22 days (v1.5.0 on 24 Sep to v1.7.4 on 16 Oct). The architecture overview had 6 versions between 9 and 14 October. The SRS went from 0.1.0 (April) to 0.2.2 in a single day, 16 October.
- **Document-heavy, code-light.** Architecture §5.1 marks all six Core modules “Absent”. Spec §5.2 runs Phase 1 from October with Phase 2 starting in December, and team capacity and LLM budget are still “owner to supply”.
- **Review roles.** The multi-role reviews (Chief of Staff, Designer, SAA) produce real fixes, but reviewers share blind spots. A typo from the original draft (“configureed”) and a stale version note survived three rounds. Use deterministic lints for what machines can check, and keep human review for meaning.
- **Change control.** The seven-step flow is heavy for a pilot. Use the Patch and Minor lanes with sampled review until the first slices ship.
- **Mitigation.** Write requirements just in time: only for slices to be built in the next 4–6 weeks.

## 7. Options compared

| Criterion | 1: Agent SRS only | 5: System SRS | 6: PRD + feature map | 7: Story map | Hybrid (5+1, slim) |
| --- | --- | --- | --- | --- | --- |
| Testability | High (agent only) | High | Low–Med | Low | High |
| Covers NFR and cross-cutting | System: Low | High | Low | Low | Med–High |
| Traceability to slices | High | High | Med | Med | High |
| Upkeep cost (lower is better) | Low | High | Low | Low–Med | Med if slim |
| Agent-friendliness | High | Med–High | Med | Med | High |
| Value ranking | Low | Low | High | High | Med (via Spec §5.3) |
| Reuses existing assets | High | High | High | High | High |
| Fit for a small team | High | Med–Low | High | High | Med–High |

The hybrid wins on rigour where it matters. Its weakness is upkeep, which is why “slim” and “just in time” are conditions, not preferences.

## 8. Recommendations

### Now (before the first slice is specified)

1. **Add an identity family** (sign-in, token verification, owner = subject, 401/403/404 behaviour) as P0, grounded in ADR-SYS-001. Move OI-1 from “Deferred” to “Open, in progress”.
2. **Add the gate and Position family** (suggested SR-9.2 to SR-9.4) before slice work on Thesis or the gate. Draft lines are below.
3. **Fix the drift items** in one pass: SRS 0.2.3, Spec 1.7.5, and footers and links per Appendix A.
4. **Add Phase and Status columns**; keep Pri to P0–P3 only.
5. **Add two rules to SRS §3.1:** Spec wins on meaning; the Spec glossary wins on terms.
6. **Resolve OI-6.** One option: confidence is a categorical source grade (official filing, licensed feed, news, user-entered, AI-generated) plus a freshness flag, set by the ingestion pipeline by source class, never by the model. No numeric score in Phase 1.

**Draft lines to seed the gate family** (wording for you to edit):

| Draft ID | EARS statement | Given / When / Then |
| --- | --- | --- |
| SR-9.2.1 Atomic Pass | When the user chooses Pass and every mandatory checklist item is met, the system SHALL create the Decision record and the Position as one atomic operation. | Given all mandatory items met and idempotency key K, when Pass is submitted twice with K or is interrupted mid-write, then exactly one Decision record and one Position exist, or neither |
| SR-9.2.2 Revise records Fail | While any mandatory item is unmet, the system SHALL keep Pass unavailable; when the user chooses Revise, the system SHALL record a Decision record with outcome Fail listing the unmet items and SHALL NOT create a Position. | Given one unmet mandatory item, when the user chooses Revise, then a Fail record lists that item, no Position exists, and Portfolio risk figures are unchanged |
| SR-9.2.3 Sandbox isolation | The system SHALL NOT create or change a Position, size or stop from any Research Sandbox action other than Pass. | Given a Working Thesis in the Sandbox, when the user edits it or runs any Sandbox action, then Portfolio risk figures are unchanged |
| SR-9.2.4 Checklist fixed at open | When the Decision gate opens, the system SHALL fix the checklist for that gate instance. | Given an open gate, when checklist defaults change, then the open gate keeps its original items |
| SNR-3.2.2 Cross-user refusal | If a user requests another user’s record by id, the system SHALL refuse and SHALL NOT return any field of the record. | Given user A’s Insight, when user B requests it by id, then the response is 404 with no record content |

### Next (before the third slice)

7. **Slice template** for `spec.md`: Requirements covered (IDs), Deferred IDs, EARS statements, Given/When/Then scenarios, Verification method, Dependencies.
8. **Lint in `sync_spec_status.py`:** every cited ID has an anchor; every Phase 1 P0 ID has a slice or a deferral note; header and link version pointers match the target document; ID format is valid.
9. **Agent SRS allocation rule:** each FR cites a parent SR or is marked domain-local. Link, do not fold.
10. **Map the five architecture quality goals to SNR IDs.** Add NFRs for atomicity, degraded output, privacy, data minimisation and injection handling.
11. **Align status-gate names** across the SRS, README and registry.
12. **Update Spec §0.1, §6.1, §6.2, §6.4** to include the SRS tier and the new skeleton.

### Later

13. Retire or generate the “Spec Coverage” column.
14. Replace the README milestone roadmap with a pointer to Spec §5.
15. Hold a retrospective after the first three slices (section 9).

## 9. How to judge the experiment

| Measure | Why | Suggested target |
| --- | --- | --- |
| Phase 1 P0 IDs linked to a slice before it starts | Tests the chain | 100% |
| SRS edits per slice (minor versus patch) | Tests whether requirements are stable enough to write ahead | At most one minor per slice |
| Clarify questions per slice traced to SRS wording | Tests verifiability | Falling slice by slice |
| Review findings per round | Tests authoring quality | Falling; a lint should catch the mechanical ones |
| Hours of authoring and review per requirement line | Tests upkeep cost | Set a ceiling after the first slice |
| Slices where an agent plans and tasks without being re-told requirements | Tests agent-friendliness | Most slices |
| Time to the first verified slice | Tests delivery pace | Set after slice S1 |

**Decision rule.** After three verified slices: continue if the first two measures hold and cost is within the ceiling; simplify (drop the Coverage column, merge families) if cost is high but the chain works; revert to Spec-plus-slices if edits per slice stay high.

## 10. Decisions needed from you

1. Link or fold the agent SRS (my recommendation: link).
2. Is the identity slice first, and when will the open ADR-SYS-001 items (token storage, role mapping) be settled?
3. Will the datastore move to a replica set before the gate slice (ADR-SYS-002), given `mongo:5.0` is past end of life?
4. Who authors the default gate checklist (the open question in Spec §7)? The gate requirements depend on it.
5. What are the real team capacity and Phase 1 dates?
6. How long does the experiment run, and what are the exit criteria in section 9?

## Appendix A. Inconsistency register

Severity: H high, M medium, L low.

| # | Where | Issue | Suggested fix | Sev |
| --- | --- | --- | --- | --- |
| 1 | SRS §8.2 | Agent SRS shown as v2.2, 302 items; you report v2.9, 438 | Update, and state that the subordinate SRS is checked against this one | M |
| 2 | SR-4.3.2 | “Create portfolios and track positions” (P2) conflicts with Position only via Pass (Spec §4.6 #3) and the P0 Position deliverable | Rewrite or retire | M |
| 3 | SRS §4.2–4.3, SR-5.2.x vs architecture §4.6, R8 and README | SRS and README treat Socket.IO as a chat interface; architecture says the companion path is SSE and Socket.IO is a test page | Decide, then demote or retire SR-5.2 | M |
| 4 | SRS §4.2 | Agent drawn as its own domain with a Backend tool loop; architecture draws it in-process; README draws a separate container on port 7000 | Align the SRS diagram to the architecture | M |
| 5 | README §2.1, §3.1 vs architecture §4.2, §4.8 | README shows 3 containers and Redis as short-term memory; architecture shows 4 containers, session memory in MongoDB, Redis cache only | Apply the doc fixes the architecture already lists | M |
| 6 | README §6.2 vs Spec §5 | Two roadmaps; long-term memory in “Q3 2026” (past) vs Phase 4 | Point README to Spec §5 | M |
| 7 | Spec §0.1, §6.1, §6.2, §6.4 | Hierarchy has no SRS tier; SRS called “out of scope” | Update (action 12) | M |
| 8 | Spec §4.6 #2 | The “only normative” gate text omits that Fail keeps a Decision record, while §0.4 and §4.7 #8 say it (ADR-SYS-002 also notes this) | Add the sentence to §4.6 #2 | M |
| 9 | SRS §9.1 vs README §4.3 | Status gates `analyzed` vs `clarified` | Pick one | L |
| 10 | SRS §3 | Spec described as a “master charter” with “360° company lenses” | Reword | L |
| 11 | SRS §2.4, §3, §8.1 vs README | OpenAPI at `docs/domains/backend/api/openapi.yaml` vs `docs/openapi.yaml` | Verify the real path | L |
| 12 | Spec v1.7.4 header, §0.6, §7 | Points to IA v1.0.0 and Journeys v1.0.0/v1.0.1; current are IA v1.0.1 and Journeys v1.0.2 | Update pointers | L |
| 13 | IA map and Journeys footers (v1.0.0 and v1.0.1 against headers v1.0.1 and v1.0.2) | Footers lag headers | Align | L |
| 14 | Architecture header | Pins Spec v1.7.2; Spec is v1.7.4 | Re-pin after checking §4.4 and §5.3 changes | L |
| 15 | SNR-2.2.2 | Typo “configureed” | Fix | L |
| 16 | SRS file | CRLF line endings; AGENTS.md runs `git diff --check` | Add `.gitattributes` | L |
| 17 | Journeys §6 #3 | W4 and W6 snapshots lag the text (Pass-disabled state, unmet items, light status cue) | Re-export frames | L |
| 18 | SRS table “Pri” | Priority mixed with phase | See 6.3 | M |

## Appendix B. SRS measurements (Draft 0.2.2)

| Metric | Value |
| --- | --- |
| Requirement IDs | 67 (43 SR, 24 SNR) |
| Priority split | P0 32, P1 28, P2 7 (one marked Future) |
| Lines new in the pilot | 9 (SR-1.3.1–4, SR-4.4.1–3, SR-9.1.1–2): 8 P0 and 1 P2; SNR-3.2.1 widened |
| Legacy P0 lines | 24 |
| Lines with a References column | Pilot lines and the SNR-3 table |
| SR rows with Spec Coverage filled | 0 of 43 |
| EARS-pattern lines | 6 (all pilot) |
| Given/When/Then scenarios | 0 |
| Phase 1 P0 deliverables with SRS IDs | 3 of 7 |
| Open issues | 6 (OI-1 to OI-6) |
