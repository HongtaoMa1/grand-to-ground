---
name: g2g-status
description: Report the health of a Grand-to-Ground research programme — cycle history, question registry, hard-core attack accumulation, and a Lakatosian progressive-vs-degenerating audit. Use when the user says "G2G status", "programme audit", "how is my research programme doing", "review the hard core", or resumes work after time away.
---

# G2G Status

Read the `g2g/` workspace and report programme health. If it does not exist, say so and point to g2g-setup.

## Report structure (≤25 lines total)

1. **Charter recap** — vision in one line, layers, hard-core version, current phase (from `00_programme.md`, `04_log.md` last entries).
2. **Registry summary** — counts by status (candidate / active / converged / stalled / covered-by-literature); flag any question stuck in `active` across 2+ sessions.
3. **Scorecard trend** — list conclusion cards with total scores in order; note trajectory (improving / flat / declining).
4. **Rotation compliance** — framework families used per cycle; flag consecutive repeats and logged waivers.
5. **Hard-core audit** (the part most tools skip):
   - Tally `Attacks on the core` by axiom and direction.
   - **Trigger rule:** any axiom with ≥3 accumulated same-direction attacks gets a formal review: present the attacks verbatim, the evidence, and three options — revise the axiom (bump hard-core version), demote it to the protective belt, or keep with written justification. The user decides; record the decision.
   - **Lakatos verdict:** is the programme *progressive* (recent cycles produced novel, falsifiable predictions that survived grounding) or *degenerating* (recent cycles mostly patched the belt to absorb refutations)? Judge from the last 3 cards: count novel predictions vs. patches, and say which. Be blunt — a degenerating verdict with reasons is worth more than reassurance.
6. **Pending user decisions** — unratified axiom proposals, next-cycle priority, unreviewed tribunal records.

## Hygiene checks (run silently, report only failures)

- Cards with an empty "Framework linkage" field (they are void — flag for repair or deletion).
- Contradiction-log entries missing for cycles that have cards.
- Registry rows whose "expected cross-level mechanism" is blank.
- Guesses that migrated into later documents without their guess-mark.

## Tone

This skill is the programme's mirror, not its cheerleader. State what the records show; where records are silent, say "no evidence either way" rather than filling gaps with optimism.
