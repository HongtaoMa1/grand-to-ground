# G2G workspace file templates (v2)

Fill `{placeholders}` from the intake interview. Keep files in English unless the user works in another language — then mirror their language.

## 00_programme.md

```markdown
# G2G Programme Charter

**Initialized:** {date} · **Discipline:** {discipline} · **Status:** {phase} · **Methodology:** G2G v2.0

## Vision (P0, verbatim)
{user's vision text, unedited}

## Framework layers
{layer1} → {layer2} → {layer3}
(Every accepted conclusion must link at least two layers.)

## Severity default
{exploratory | standard | submission} — any single tribunal may override; the dial changes depth, never honesty.

## Field conventions
{venue norms captured at setup, e.g. "pre-registration rituals rare in empirical finance" — seeded as rulings U-1…}

## External collaborator
{name, role — or "none". Rulings archived verbatim; materials via g2g-plan.}

## Thresholds
Pass line: {18}/25 with falsifiability ≥ {3}/5 and sellability ≥ {2}/5 · Tribunal rounds & deducers: per severity tier · Critics: {3}

## Rotation menu (framework families; data domain is the second axis, partitioned per programme)
{list — from rotation-menus.md, edited by user}

## Evidence environment
{datasets / archives / natural experiments, or "TBD at first grounding"}

## ID legend (register every letter series here at first use; dotted revisions, never primes)
| Series | Meaning |
|---|---|
| C-XXX | conclusion card |
| S# | seed / registered question |
| R# / A# B#… | plan repair modules / plan offense lines |
| U-# | standing ruling |
| DP-# | defense piece (reusable defended argument) |
| #NN / ST-NN | cycle tribunal / special (plan-level) tribunal |
| H# / A-# | hard-core axiom / added axiom |
| {new} | {register before first use} |
```

## 01_hard-core.md

```markdown
# Hard core, declared assumptions, and protective belt

**Version:** 1.0 · **Ratified by user:** {date}
Rule: critics may attack the belt every round. Attacks on the core are logged, not adjudicated on the spot; review at every 3rd accumulated same-direction attack (g2g-status). Declared assumptions are exempt from refutation — attacks go to the silent ledger, surfaced only at audits.

## Hard core (protected assumptions — ratification is a human gate; fact-checked first)
- **H1** {assumption} — RATIFIED {date}
- **H2** {assumption} — RATIFIED {date}

## Declared assumptions (exempt tier — stated, not defended; quick factual scan only)
- **DA1** {assumption} — declared {date}; quick-scan {date}: {clear | corrected: …}
- (The tribunal enforces staying *inside* these and honest outward presentation *of* them; it does not litigate their truth.)

### Silent ledger (attacks on declared assumptions — append-only, uncounted, surfaced at audits)
| date | DA | attack summary | source critic |
|---|---|---|---|

## Protective belt (auxiliary hypotheses — attackable, replaceable)
- {specific mechanisms, case interpretations, model/parameter choices}

## Standing rulings (U-series — objection classes the human has closed; critics cite and stand down)
| ID | date | ruling | scope |
|---|---|---|---|
| U-1 | {date} | {e.g. "pre-registration-ritual objections not receivable; follow field convention"} | all tribunals |

## Attacks on the core (log only)
| date | axiom | attack summary | source critic |
|---|---|---|---|

## Corrected facts (deductions must not contradict these)
- {fact} — corrected {date}, source: {ref}

## Pending axiom proposals (await user ratification)
- (none)
```

## 02_question-registry.md

```markdown
# Question registry and seeds

## Registry (anti-repetition: check before every cycle; genealogy carries BOTH rotation axes)
| ID | question | framework family | data domain | status | card | expected cross-level mechanism |
|---|---|---|---|---|---|---|

Status values: candidate / active / converged / archived-in-progress / stalled / covered-by-literature (learning mode)

## Seeds (from the vision and tribunal salvage; harvest every cycle — mandatory at P8)
- S1 {seed}
```

## 03_records/contradiction-log.md

```markdown
# Contradiction log (append-only)

Format: `[date] [question-ID] [round] — contradiction / keeper / lesson / open item · one line`
Methodology-level lessons are tagged `[method]` — they are the raw material of the next methodology revision.
```

## 03_records/literature-ledger.md

```markdown
# Literature ledger (P1 incremental mode reads and updates this; full sweeps rebuild it)

| neighbor (author, year, venue) | axis (method / domain) | one-line verdict | similarity | last checked |
|---|---|---|---|---|

Stale = last checked > {90} days before a cycle that leans on it. The novelty critic reports staleness; the orchestrator updates.
```

## Conclusion card (03_records/card-CXXX.md)

```markdown
# Conclusion card C-{XXX}

**Date/cycle:** · **Question ID:** · **Family / data domain:** (rotation check, both axes: differ from previous cycle?) · **Hard-core version:** · **Severity tier:**

## Pre-coded novelty claim (registered BEFORE the tribunal sat)
{the increment as claimed ex ante — the novelty critic grades this exact sentence}

## Surviving conclusions (post-tribunal, post-defense; exact sentences, qualifiers intact)
1. …

## Tribunal record
- Verdict file: {tribunal-NN.md} · Killed: {sentence — by which critic, which objection} · Replacement language applied: {yes/no}
- Defended: {how, within axioms; DP-n pieces earned}
- Attacks on the core / on declared assumptions: {logged verbatim, not adjudicated}

## Grounding (three questions, per surviving conclusion)
- Observable prediction:
- What data would refute it:
- Natural experiment / dataset:
- Programmatic reconciliation (if entering a frozen registry): {machine-checkable counts/ranges}

## Scores (five axes)
Internal consistency _/5 · Empirical compatibility _/5 · Falsifiability _/5 · Novelty _/5 · Sellability _/5 · **Total _/25** (pass ≥{18}, falsifiability ≥{3}, sellability ≥{2})
Sellability = one clearly stated contribution, venue-shaped, retellable in two sentences.

## Disposition (scores inform; the human disposes)
{user's call: advance / archived-in-progress / demote / bury} — {date}
**Re-scoring triggers (mandatory if archived-in-progress):** {what evidence, if it lands, reopens this card}

## Framework linkage (MANDATORY — blank = the cycle is void)
{what this means for the other layers; the mechanism in one sentence}

## Next steps
{derived questions → registry; axiom proposals → pending queue; salvage → seeds}
```

## Tribunal verdict (03_records/tribunal-NN.md or tribunal-ST-NN.md)

```markdown
# Tribunal {#NN | ST-NN}: {object} · {date}

**Mode:** {cycle | plan} · **Severity:** {tier} · **Configuration:** {N critics, quotas; defender: none / fresh / g2g-defender+data} · **Rulings in force:** {U-…}
War report: {X} objections (logic {}/evidence {}/novelty {}) + {Y} attacks on core + {Z} exempt-logged. Defense: defended {} / partly {} / conceded {}.

## I. Kill table (sentence-level; THIS TABLE IS THE BINDING WORDING BASELINE downstream)
| # | dead sentence | cause | killer | replacement language |
|---|---|---|---|---|
(Patrol the five overreach verbs: confirm, guarantee, falsify, vindicate, co-move. Three-value discipline: alive / dead / undecidable(+reason); "not detected" never becomes "refuted".)

## II. Survivors (exact sentences, quoted — never paraphrased stronger)

## III. Weak points (partly defended — strengthen before publication)

## IV. Assumption exposure
- Which conclusions hang on which axioms/assumptions
- Attacks on the core → appended to 01 log · Exempt-logged attacks → silent ledger

## V. Collisions (critic vs critic; orchestrator's adjudication — recorded, it is the system calibrating itself)

## VI. Cross-proposition registration (what else could each major number support or refute?)

## VII. Defense pieces earned (DP-n, one line each)

## VIII. Salvage (→ seed registry, mandatory)

{Submission severity only:} ## IX. Translation-layer check (outward sentence ↔ frozen wording alignment; dropped qualifiers are kill-table entries)
```

## Research plan (05_plans/plan-vNNN.md)

```markdown
# Research plan v{NNN} — {programme}

**Date:** · **Status:** draft — awaiting ticks · **Inputs:** {verdicts/rulings/feedback digested by this version}

## §0 Plain-language digest (read this first)
{half a page, no undefined jargon: what happened, what this version changes, what you need to do}

## Repair line (mandatory; one module per accepted finding; tick to approve)
- [ ] **R1** ({one-line plain restatement of the objection}) → {the fix}
- [ ] **R2** (…) → …

## Offense lines (optional)
- [ ] **A** {item} — expected cross-level mechanism: {one sentence} — rotation check (family/domain): {ok?}

## Decision bar (four-line format; defaults take effect unless changed)
| # | what was done | what you must decide | default | cost of not deciding | blocks |
|---|---|---|---|---|---|

## Frozen-wording appendix (quoted exactly from substitution tables; qualifiers intact)

## Approval record (append-only; dated)
{e.g. "2026-XX-XX: R1 ✓ R2 ✓ A skip — {user}"}
```

## Collaborator one-pager + call notes (via g2g-plan, when a collaborator is on charter)

```markdown
# One-page brief — {topic} ({date})
{the story in standard field terminology; every results sentence step-down-checked against frozen wording; assumptions presented as assumptions; no internal machinery, no internal pet names}

# Call notes — {date}
- Questions to ask: …
- Answers to have ready (incl. the standard answer to previously fumbled questions): …
- Decisions wanted from this call: …
- (After the call: record their rulings VERBATIM, dated → plan inputs / standing rulings.)
```

## 06_process-defects.md

```markdown
# Process defects and human-side rules (living file — mostly FOR the human)

> When a process defect costs time twice, it gets an entry: defect → rule. These entries feed methodology revisions.

## Seeded rules (v2.0 defaults)
1. **Four-line decision format** for everything put before the human: what was done / what you must decide / default ("takes effect unless changed") / cost of not deciding (+ what it blocks). No context-fetching pointers; no missing defaults; no undefined jargon. Standard: decidable from one screen.
2. **Session hygiene:** one session, one thing; learning sessions separate and disposable; hand off at stage boundaries (signals: repetition, misremembering, stage closed, topic change); state lives in files — an unwritten decision did not happen.
3. **Entry files never contain version/round numbers** — "highest version is current".
4. **ID discipline:** every letter series registered in the 00 legend; dotted revisions (R2.1), never primes.

## Logged defects (append-only)
| date | defect | rule adopted |
|---|---|---|
```

## 04_log.md

```markdown
# Session log (newest last; a resuming agent reads the last 3 entries)

## {date} · {agent/model} · {seat: planning | execution}
{what was done, what is pending, handoff notes}
```
