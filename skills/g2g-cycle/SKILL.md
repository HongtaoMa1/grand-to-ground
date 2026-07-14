---
name: g2g-cycle
description: Run one full Grand-to-Ground research cycle (P1 reconnaissance → P2 formalization → P3 axiom check → P4 conjecture → P5 deduction → P6 adversarial tribunal → P7 grounding → P8 scoring and records). Use when the user says "run a G2G cycle", "start the next cycle", "g2g cycle", or asks to develop a research question from their framework. Requires an initialized g2g/ workspace (run g2g-setup first).
---

# G2G Cycle

Orchestrate one complete research cycle. Read `g2g/00_programme.md`, `g2g/01_hard-core.md`, and `g2g/02_question-registry.md` before anything else. If `g2g/` does not exist, stop and run g2g-setup.

## Anti-dogma rules (highest priority, enforce mechanically)

- **R1 Rotation.** Do not use the same theoretical-framework family in two consecutive cycles. The menu is in the charter; concepts the user emphasizes are entry points, never mandates.
- **R2 No re-cutting.** Check the registry; a registered question may not be cut again. Derived questions must name their parent and the new increment.
- **R3 Cross-level linkage.** A conclusion that cannot fill the card's "Framework linkage" field is void — a result that is elegant at one layer and meaningless to the others does not count as output.
- **R4 Mechanism first.** Each cycle must propose at least one cross-level mechanism (behavior at one layer → consequence at another). Describing preference or attitude differences is not a mechanism.

## Phase sequence

**Select the question.** Prefer user's explicit pick; otherwise propose 2–3 candidates from registry seeds (passing R1/R2), with the expected cross-level mechanism in one sentence each, and let the user choose.

**P1 Reconnaissance.** Spawn a general research subagent (fresh context) to sweep the literature: classics, last-3-years work, nearest neighbors (one-line verdicts), usable datasets, natural experiments. It must answer the gate: *is this already done, deeper?* If yes → switch to learning mode: write a learning note into `03_records/`, register the question as covered-by-literature, and end the cycle (collision sites are where innovation lives — stand on the result and harvest new seeds). If no → proceed with the stated increment.

**P2 Formalization.** Translate the relevant slice of the vision into propositions: operationalized definitions (measurable), directional claims, each tagged faithful/strengthened/extended relative to the source narrative. Propose 2–3 candidate framework skeletons from the rotation menu with trade-offs — never default to the previous cycle's family (R1).

**P3 Axiom check.** Use the ratified hard core only. Any new axiom the deduction would need goes to `01_hard-core.md → Pending axiom proposals` for user ratification — do not smuggle it in.

**P4–P5 Conjecture and deduction.** Spawn the `g2g-deducer` agent (fresh context). Give it: hard core, propositions, skeleton, and the output contract (≥4 non-trivial conclusions, ≥2 cross-level, every guess marked, self-assessment of weakest steps, ratio-vs-total check). Never deduce in the orchestrator's own context — separation is the point.

**P6 Tribunal.** Spawn the three critic agents in parallel, each in a fresh context, each seeing only the axioms and the deduction (never each other): `g2g-logic-critic`, `g2g-evidence-critic`, `g2g-novelty-critic`. Enforce quotas: each files ≥5 objections, no overall endorsement, no fix suggestions. Then run the defense: send all objections back to the deducer (continue its context if the platform allows; otherwise a fresh defense agent with full inputs). The deducer defends strictly within axioms, marking each objection defended / partly defended / conceded; what needs a new axiom stops there and goes to the pending queue. Max rounds per charter (default 3); unresolved → escalate to the user.

**P7 Grounding.** For each surviving conclusion, answer three questions: What observable prediction does it make? What data pattern would refute it? Has history already run the experiment (name the dataset/event)? Unrefutable claims are decoration — mark them so.

**P8 Score, record, hand off.** Score the cycle (internal consistency / empirical compatibility / falsifiability / novelty, 1–5 each) against the charter's pass line. Write the conclusion card (`03_records/card-CXXX.md`, template in g2g-setup references), append contradiction-log entries **as they occur, not at the end**, update the registry (including newly harvested seeds and derived questions), log attacks-on-core, update `04_log.md`. Stop rule: two consecutive rounds without score improvement = converged; budget exhaustion = archive as stalled (budget is a constraint, not a quality signal).

## Verdict to the user

End with ≤10 lines: what died (and to whom), what survived (exact sentences), scores, the framework linkage, pending decisions (axiom proposals, next-cycle priority). The user reviews the tribunal record — offer it, don't paraphrase it away.

## Failure modes to actively resist

Sycophancy and critic convergence (quotas + fresh contexts); a polluted hard core (fact-check before ratification); context drift (state lives in files, one round per context); narrative overfitting (grounding is mandatory); human rubber-stamping (surface the tribunal log, not just the card).
