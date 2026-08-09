---
name: g2g-tribunal
description: Run a standalone adversarial tribunal on any argument, draft, theory, research plan, or set of claims — three independent critics (logic, evidence, novelty) with anti-sycophancy quotas at a chosen severity tier, then a defense round (independent defender with data recomputation at submission severity). Has a plan-tribunal mode (ST series) for reviewing research plans and outward materials before they freeze or ship. Use when the user says "run a tribunal on this", "adversarial review", "attack this argument", "stress-test my theory/draft/hypothesis/plan", or "g2g tribunal". Works without an initialized G2G programme; integrates with one if present.
---

# G2G Tribunal (standalone)

Subject any piece of reasoning to the G2G adversarial court. This skill is the plugin's entry drug: it needs no setup and works on a paragraph, a paper draft, a model sketch, a research plan, or a business argument.

## Step 0 — Set the severity

Ask (or infer from stakes, stating your inference): **exploratory** (hunches, essays — ≥3 objections per critic, 1 defense round, exploratory tone) / **standard** (working research — ≥5, up to 2 rounds, independent defender optional) / **submission** (anything leaving the building — ≥5, up to 3 rounds, independent defender with data recomputation mandatory, translation-layer check mandatory). If a `g2g/` workspace exists, its charter default applies unless overridden. The dial changes depth, never honesty: endorsement stays forbidden at every tier.

## Step 1 — Frame the case

Identify from the user's input: (a) the **claims** under review, numbered; (b) the **assumption set** the author treats as given (ask if unclear — the defense may only use these); (c) the **domain**, so the evidence critic knows where to search and which conventions apply. If a `g2g/` workspace exists, read `01_hard-core.md`: ratified axioms and **declared assumptions** form the assumption set (declared assumptions are exempt from refutation — attacks on them get ledgered, not litigated); load the **standing rulings** register (objection classes covered by a ruling are not receivable — critics cite the ruling and stand down).

**Plan-tribunal mode.** When the object is a research plan, a proposition set headed for a frozen registry, or outward-facing material (a one-pager, an abstract, a briefing): the target is **the new shapes and mappings** — the formalizations, framings, and translations the document adds — *not* the already-frozen results it cites (those were tried in their own tribunals; re-trying them is double jeopardy). Number the verdict in the **special series (ST-01, ST-02, …)**, never consuming cycle-tribunal numbers. Field experience: the first plan tribunal found fourteen dead sentences, all in the plan-to-outward-text translation layer — precisely where no gate had stood.

## Step 2 — Convene three critics in parallel, fresh contexts

Spawn `g2g-logic-critic`, `g2g-evidence-critic`, and `g2g-novelty-critic` as parallel subagents. Each receives ONLY: the numbered claims + the assumption set (hard core and declared assumptions, labeled) + the rulings register + the domain and its conventions + the severity tier. Never show critics each other's output or prior conversation. Enforce the contract in each prompt: the tier's minimum objections, ranked, pinned to claim numbers (escape valve: a critic that cannot reach quota with receivable objections says "receivable surface exhausted" rather than fabricating); no overall endorsement, no praise, no fix suggestions; evidence critic cites sources or marks "unverifiable"; novelty critic names nearest prior work with similarity ratings; attacks on declared assumptions filed under `LOGGED (exempt)`, uncounted.

## Step 3 — Defense round

At exploratory severity, a fresh defense agent argues from the stated assumptions. At standard and above, prefer the **`g2g-defender`** agent: fresh context, receives claims + assumptions + ALL objections + (if available) the primary data file paths, with the **recomputation obligation** — every computable allegation is settled by recomputing from primary files, not by argument, and errors found on the defended side are reported with equal prominence. Contract: answer every objection **defended / partly defended / conceded** with one-line reasons; defenses only from stated assumptions; needing a new assumption = concede and say so; a defense that restates the claim is a concession; propose replacement language for killed sentences.

## Step 4 — Verdict

Deliver to the user, in this order:

1. **Plain-language digest** — 3–5 sentences, no jargon: what died, what survived, what it means.
2. **Kill table, sentence-level** — each dead sentence with its cause, its killer, and **replacement language**; this table is the binding wording baseline for all downstream writing. Patrol the five overreach verbs: *confirm, guarantee, falsify, vindicate, co-move*. Verdict language is three-valued: **alive / dead / undecidable (+reason)** — "not detected" never becomes "refuted".
3. **Survivors** — the exact sentences still standing (quote them; do not paraphrase stronger).
4. **Weak points** — partly-defended items, worth strengthening before publication.
5. **Assumption exposure** — which conclusions hang on which assumptions; attacks on protected axioms and on declared assumptions (append to `01_hard-core.md` core-attack log and silent ledger respectively, if a programme exists).
6. **Collisions** — where critics contradicted each other, and the provisional adjudication (recorded and surfaced for the human, who can re-decide: collisions are the adversarial system calibrating itself).
7. **Cross-proposition registration** — for each major piece of evidence, what *other* propositions it could support or refute (verdicts are relative to wording; don't waste a number on one framing).
8. **Defense pieces** — numbered reusable arguments that survived (DP-n).
9. **Salvage** — genuinely open gaps the critics' own findings revealed.

At **submission severity**, additionally run the **translation-layer check**: align every outward results sentence with its frozen/internal wording, sentence by sentence; qualifiers that vanished in translation are kill-table entries. And the red line is absolute: a test added after results were known is never described outward as pre-specified — not mentioning timing is legitimate; reversing it is fraud.

Offer the full tribunal transcript; never summarize it out of existence. If a `g2g/` workspace exists, append one line per major finding to the contradiction log and archive the verdict (`tribunal-XX.md` or `tribunal-ST-XX.md`).

## Calibration

Severity tracks stakes, chosen by the human — never soften objections because the user seems attached to the idea, and never escalate beyond the chosen tier to seem thorough. The plugin's value is that it does not flatter; its discipline is that the human sets the depth. Scores and verdicts inform; the human disposes.
