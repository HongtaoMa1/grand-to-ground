# G2G workspace file templates

Fill `{placeholders}` from the intake interview. Keep files in English unless the user works in another language — then mirror their language.

## 00_programme.md

```markdown
# G2G Programme Charter

**Initialized:** {date} · **Discipline:** {discipline} · **Status:** {phase}

## Vision (P0, verbatim)
{user's vision text, unedited}

## Framework layers
{layer1} → {layer2} → {layer3}
(Every accepted conclusion must link at least two layers.)

## Thresholds
Pass line: {14}/20 total with falsifiability ≥ {3}/5 · Tribunal rounds per question: max {3} · Critics: {3}

## Rotation menu (theoretical framework families)
{list — from rotation-menus.md, edited by user}

## Evidence environment
{datasets / archives / natural experiments, or "TBD at first grounding"}
```

## 01_hard-core.md

```markdown
# Hard core and protective belt

**Version:** 1.0 · **Ratified by user:** {date}
Rule: critics may attack the belt every round. Attacks on the core are logged, not adjudicated on the spot; review at every 3rd accumulated same-direction attack (see g2g-status).

## Hard core (protected assumptions)
- **A1** {assumption} — RATIFIED {date}
- **A2** {assumption} — RATIFIED {date}

## Protective belt (auxiliary hypotheses — attackable, replaceable)
- {specific mechanisms, case interpretations, model choices}

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

## Registry (anti-repetition: check before every cycle)
| ID | question | framework family | status | card | expected cross-level mechanism |
|---|---|---|---|---|---|

Status values: candidate / active / converged / stalled-archived / covered-by-literature (learning mode)

## Seeds (from the vision; harvest new ones each cycle)
- S1 {seed}
```

## 03_records/contradiction-log.md

```markdown
# Contradiction log (append-only)

Format: `[date] [question-ID] [round] — contradiction / keeper / open item · one line`
```

## Conclusion card (03_records/card-CXXX.md)

```markdown
# Conclusion card C-{XXX}

**Date/cycle:** · **Question ID:** · **Framework family:** (rotation check: differs from previous cycle?) · **Hard-core version:**

## Surviving conclusions (post-tribunal, post-defense)
1. …

## Tribunal record
- Killed: {conclusion — by which critic, which objection}
- Defended: {how, within axioms}
- Attacks on the core: {logged verbatim, not adjudicated}

## Grounding (three questions, per surviving conclusion)
- Observable prediction:
- What data would refute it:
- Natural experiment / dataset:

## Scores
Internal consistency _/5 · Empirical compatibility _/5 · Falsifiability _/5 · Novelty _/5 · **Total _/20** (pass ≥{14} and falsifiability ≥{3})

## Framework linkage (MANDATORY — blank = the cycle is void)
{what this means for the other layers; the mechanism in one sentence}

## Next steps
{derived questions → registry; axiom proposals → pending queue}
```

## 04_log.md

```markdown
# Session log (newest last; a resuming agent reads the last 3 entries)

## {date} · {agent/model}
{what was done, what is pending, handoff notes}
```
