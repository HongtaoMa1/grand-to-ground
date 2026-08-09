---
name: g2g-status
description: Report the health of a Grand-to-Ground research programme — cycle history, question registry, hard-core attack accumulation, declared-assumption ledger, re-scoring queue, pending decisions with what they block, and a Lakatosian progressive-vs-degenerating audit. Use when the user says "G2G status", "programme audit", "how is my research programme doing", "review the hard core", or resumes work after time away.
---

# G2G Status

Read the `g2g/` workspace and report programme health. If it does not exist, say so and point to g2g-setup.

## Report structure (≤35 lines total)

1. **Charter recap** — vision in one line, layers, hard-core version, severity default, current phase (from `00_programme.md`, `04_log.md` last entries, latest plan in `05_plans/`).
2. **Registry summary** — counts by status (candidate / active / converged / archived-in-progress / stalled / covered-by-literature); flag any question stuck in `active` across 2+ sessions.
3. **Scorecard trend** — conclusion cards with five-axis totals in order; note trajectory (improving / flat / declining).
4. **Re-scoring queue** — archived-in-progress cards whose re-scoring triggers may have fired (compare triggers against recent records); list each with its trigger and what evidence would move it. Re-scoring is proposed here, decided by the user.
5. **Rotation compliance, two axes** — framework family AND data domain per cycle (the genealogy line); flag consecutive repeats on either axis and logged waivers.
6. **Hard-core audit** (the part most tools skip):
   - Tally `Attacks on the core` by axiom and direction.
   - **Trigger rule:** any axiom with ≥3 accumulated same-direction attacks gets a formal review: present the attacks verbatim, the evidence, and three options — revise (bump hard-core version), demote to the belt, or keep with written justification. The user decides; record the decision.
   - **Lakatos verdict:** progressive (recent cycles produced novel, falsifiable predictions that survived grounding) or degenerating (recent cycles mostly patched the belt)? Judge from the last 3 cards; be blunt — a degenerating verdict with reasons is worth more than reassurance.
7. **Declared-assumption ledger** — this is the audit where the silent ledger speaks: per declared assumption, the tally of exempt-logged attacks accumulated since declaration. No adjudication — present the tally and remind the user of their three options (keep as declared; promote to hard core; convert to a hypothesis in the belt). Ten cycles of silence would defeat the ledger's purpose; this section is its voice.
8. **Standing rulings recap** — the U-series register, one line each, so the user remembers what is currently non-receivable and can retire stale rulings.
9. **Defense pieces** — numbered DP-n arguments on file, one line each (reusable in task briefs).
10. **Pending user decisions, with blocking** — unratified axiom proposals, un-ticked plan modules, unreviewed verdicts, undecided re-scorings — each in one line **with what it blocks** while it waits. This is the single list the returning user acts on.

## Hygiene checks (run silently, report only failures)

- Cards with an empty "Framework linkage" field (void — flag for repair or deletion).
- Contradiction-log entries missing for cycles that have cards.
- Registry rows missing either genealogy axis (family or data domain) or the expected cross-level mechanism.
- Guesses (`[GUESS]`) or agent signatures (`[SIG]`) that migrated into later documents without their marks.
- Archived-in-progress cards with no re-scoring trigger written.
- Entry-point files (project `CLAUDE.md` or equivalent) containing hard-coded version or round numbers — the rule is "highest version is current".
- ID series used but absent from the legend in `00_programme.md`; primes accumulated where dotted revisions belong (R″2 → R2.1).

## Tone

This skill is the programme's mirror, not its cheerleader. State what the records show; where records are silent, say "no evidence either way" rather than filling gaps with optimism. Scores and tallies inform; the human disposes.
