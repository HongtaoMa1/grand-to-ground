---
name: g2g-status
description: Report the health of a Grand-to-Ground research programme — cycle history, question registry, hard-core attack accumulation, declared-assumption ledger, re-scoring queue, pending decisions with what they block, a Lakatosian progressive-vs-degenerating audit, and — when the programme has a proposition graph (07_theory/) — graph health, i.e. node counts by status, target-theorem support closure, orphans and dangling predecessors, the [INTERP] queue, dead ends, the conjecture pool, cadence due, the last unattended run, and the budget account. Read-only. Use when the user says "G2G status", "programme audit", "how is my research programme doing", "review the hard core", "graph health", or resumes work after time away. g2g-go (the one-line entry) calls this report when nothing else is due.
---

# G2G Status

Read the `g2g/` workspace and report programme health. If it does not exist, say so and point to g2g-setup. This skill writes nothing into `g2g/` — it reads, tallies, and proposes; the human disposes.

## Report structure (≤35 lines; ≤45 when the graph section applies)

1. **Charter recap** — vision in one line, layers, hard-core version, severity default, programme modes (cycle / forge / both), current phase (from `00_programme.md`, `04_log.md` last entries, latest plan in `05_plans/`, latest `07_theory/forge-log.md` entry if any).
2. **Registry summary** — counts by status (candidate / active / converged / archived-in-progress / stalled / covered-by-literature); flag any question stuck in `active` across 2+ sessions.
3. **Scorecard trend** — conclusion cards with five-axis totals in order; note trajectory (improving / flat / declining); cards bridged into the graph show their Node ID.
4. **Re-scoring queue** — archived-in-progress cards whose re-scoring triggers may have fired (compare triggers against recent records); list each with its trigger and what evidence would move it. Re-scoring is proposed here, decided by the user.
5. **Rotation compliance, two axes** — framework family AND data domain per cycle (the genealogy line); flag consecutive repeats on either axis and logged waivers.
6. **Hard-core audit** (the part most tools skip):
   - Tally `Attacks on the core` by axiom and direction.
   - **Trigger rule:** any axiom with ≥3 accumulated same-direction attacks gets a formal review: present the attacks verbatim, the evidence, and three options — revise (bump hard-core version), demote to the belt, or keep with written justification. The user decides; record the decision.
   - **Lakatos verdict:** progressive (recent cycles produced novel, falsifiable predictions that survived grounding) or degenerating (recent cycles mostly patched the belt)? Judge from the last 3 cards — and, in a Forge programme, from whether the target theorem's support closure grew over the last M rounds; be blunt — a degenerating verdict with reasons is worth more than reassurance.
   - **Formal axiom list** (if `07_theory/axioms.md` exists): counts of ratified vs pending A- and D- IDs; any verified node citing a pending ID is a violation (name it).
7. **Declared-assumption ledger** — this is the audit where the silent ledger speaks: per declared assumption (and per ratified A-/D-), the tally of exempt-logged attacks accumulated since declaration, "false" and "unproven" classes alike. No adjudication — present the tally and remind the user of their three options (keep as declared; promote to hard core; convert to a hypothesis in the belt). Ten cycles of silence would defeat the ledger's purpose; this section is its voice.
8. **Standing rulings recap** — the U-series register, one line each, so the user remembers what is currently non-receivable and can retire stale rulings. Collision precedents on file (`03_records/collision-precedents.md`, CR-n) in one line.
9. **Defense pieces** — numbered DP-n arguments on file, one line each (reusable in task briefs).
10. **Graph health** (only when `07_theory/` exists; from `graph-index.md`, the node files, `verifications/`, the latest `elaborations/E-nnn.md`, `dead-ends.md`, `conjectures.md`, `guidance.md`, `forge-log.md`):
    - **Node counts** by logical status: verified / proposed (candidates) / revoked / superseded; by empirical status: untested / grounded / contested / refuted-in-data; kinds in one line. Revoked or superseded nodes with dependents not yet rebuilt = the rebuild backlog.
    - **Target theorem and support closure** — the current scope (layer / branch / target theorem, as the human set it in the latest guidance). *Before the target theorem passes the gate*, the closure is not computable — report **the orchestrator's judgement from the latest elaboration**: the verified, `conditional_on`-free nodes it lists as leading toward the target, and the bridge lemmas it names as missing. *After it passes*, report the **computed** closure (walk predecessors back from the theorem; `python "${CLAUDE_PLUGIN_ROOT}/scripts/pg_check.py" g2g --report` prints it) and whether it matches the last elaboration's judgement — a mismatch is a route-judgement error for the next macro audit. Closure closed (verified, `conditional_on` empty) = milestone; closure stalled while the theorem has not passed = stagnation, say so.
    - **Orphans and dangling predecessors** — verified nodes nothing cites that are not the target theorem (a signal of busyness, not a violation; list the count), and predecessor IDs that resolve to no file or to a non-verified node (a violation; name each).
    - **`[INTERP]` queue** — I-numbers awaiting the human's ruling (the programme-wide queue is `01_hard-core.md → Interpretive readings awaiting ruling (I-series)`; cross-check the node headers' `interp_pending` and the latest elaboration), each with the sentence and the reading in one line; at submission severity, name the results these are holding out of the frozen registry.
    - **Dead-end library** — DE- count by kind (dead_end / obstacle / refuted_step / excluded_family / superseded); obstacles whose candidate is still parked (repair limit used up) with the guidance's stated intent for them.
    - **Conjecture pool** — CJ- counts by status (open / promoted / ratified / dropped); open conjectures currently pushed as provisional premises, with how many conditional nodes hang on each (none of which count as progress).
    - **Cadence due** — against the charter's K / M / T (defaults 10 / 4 / 25): submissions since the last control beat, rounds since the last macro audit, verified nodes since the last theory tribunal; say which beat is due or overdue.
    - **Last unattended run** — from the last `forge-log.md` and `04_log.md` entries: round, deducers dispatched, submitted / passed / returned, repair returns, stop reason (completed / 80% wrap-up / ceiling / preflight failed / "requires new axiom" stops / injection flagged), merge timing recorded.
    - **Budget account** — the forge-log's estimate for the last round against the charter's per-round ceiling, and the cumulative estimate against the period share; flag a round whose log carries no account line (the estimate is not a meter, but its absence is a defect).
    - **Check script** — if the seat can run scripts, run `python "${CLAUDE_PLUGIN_ROOT}/scripts/pg_check.py" g2g --report` (cwd = the project root; exit code = violation count) and quote its summary; otherwise say so and suggest the human run it on a seat with a local execution environment, or that the next Forge round check the manual list in g2g-forge's `references/forge-protocol.md`.
11. **Pending user decisions, with blocking** — unratified axiom proposals (pending A-/D- entries in `07_theory/axioms.md`, with their pointers — or, without `axioms.md`, the proposals themselves — in `01_hard-core.md → Pending axiom proposals`), `[INTERP]` rulings, "requires new axiom" stops, un-ticked plan modules, an unfilled decision pack, unreviewed verdicts (#NN / ST-NN / TT-NN), TT disposition items (change an axiom / add a declared assumption / accept "not seen in reality"), conjecture ratifications, scope changes the last handover suggested, undecided re-scorings — each in one line **with what it blocks** while it waits. This is the single list the returning user acts on.

## Hygiene checks (run silently, report only failures)

- Cards with an empty "Framework linkage" field (void — flag for repair or deletion).
- Contradiction-log entries missing for cycles that have cards.
- Registry rows missing either genealogy axis (family or data domain) or the expected cross-level mechanism.
- Guesses (`[GUESS]`), agent signatures (`[SIG]`), or interpretive readings (`[INTERP]`) that migrated into later documents without their marks; a criterion number with neither a power/precision derivation nor a `[GUESS]` mark.
- Citations without their verbatim original and location in cards, verdicts, or node files.
- Archived-in-progress cards with no re-scoring trigger written.
- Cards, verdicts, or forge-log entries missing the merge-timing line or the dispatch-mode line.
- Entry-point files (project `CLAUDE.md` or equivalent) containing hard-coded version or round numbers — the rule is "highest version is current".
- ID series used but absent from the legend in `00_programme.md`; primes accumulated where dotted revisions belong (R″2 → R2.1); the v2 "H/A-n" notation still in use where v3 splits hard-core Hn from formal A-NN.
- Graph (when `07_theory/` exists): a file in `propositions/` with `status: proposed`; a verified node without a passing V- record; a verified node citing a pending A-/D-; a node with empty `conditional_on` citing a predecessor whose `conditional_on` is non-empty; a node tagged `faithful` with `[SIG]` or a non-empty `conditional_on` anywhere in its support closure; a symbol used but registered neither in `glossary.md` nor in a `glossary_introduces` header; a cycle in the dependency edges; a Forge round with neither a script run nor a "checked by hand this round" line; a branch that failed with no dead-end entry (R5).
- Charter sections v3 expects but the workspace lacks (programme modes, model tiering, pre-authorized defaults, unattended dispositions) — point to g2g-setup's migration.

## Tone

This skill is the programme's mirror, not its cheerleader. State what the records show; where records are silent, say "no evidence either way" rather than filling gaps with optimism. Progress in a Forge programme is the growth of the support closure — never the node count; say which one moved. Scores and tallies inform; the human disposes.
