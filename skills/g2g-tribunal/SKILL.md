---
name: g2g-tribunal
description: Run a standalone adversarial tribunal on any argument, draft, theory, or set of claims — three independent critics (logic, evidence, novelty) with anti-sycophancy quotas, then a defense round. Use when the user says "run a tribunal on this", "adversarial review", "attack this argument", "stress-test my theory/draft/hypothesis", or "g2g tribunal". Works without an initialized G2G programme; integrates with one if present.
---

# G2G Tribunal (standalone)

Subject any piece of reasoning to the G2G adversarial court. This skill is the plugin's entry drug: it needs no setup and works on a paragraph, a paper draft, a model sketch, or a business argument.

## Step 1 — Frame the case

Identify from the user's input: (a) the **claims** under review, numbered; (b) the **assumptions** the author treats as given (ask if unclear — the defense may only use these); (c) the **domain**, so the evidence critic knows where to search. If a `g2g/` workspace exists, read `01_hard-core.md` and treat ratified axioms as the assumption set; log any attacks on them without adjudicating.

## Step 2 — Convene three critics in parallel, fresh contexts

Spawn `g2g-logic-critic`, `g2g-evidence-critic`, and `g2g-novelty-critic` as parallel subagents. Each receives ONLY: the numbered claims + the assumption set + domain. Never show critics each other's output or prior conversation. Enforce the contract in each prompt:

- minimum 5 objections, ranked by severity, each pinned to a claim number;
- no overall endorsement, no praise, no fix suggestions (critics break; building is the defender's job);
- evidence critic must cite sources or mark "unverifiable"; novelty critic must name the nearest prior work with a similarity rating.

## Step 3 — Defense round

Send all objections to a defender agent (fresh context) with the claims and assumptions. Contract: answer every objection with **defended / partly defended / conceded** plus one-line reasons; defenses may only use the stated assumptions; anything that would need a new assumption must say so explicitly and stop. No hand-waving: a defense that restates the claim is a concession.

## Step 4 — Verdict

Deliver to the user, in this order:

1. **Kill list** — claims that died, and to whom.
2. **Survivors** — the exact sentences still standing (quote them; do not paraphrase stronger).
3. **Weak points** — partly-defended items, worth strengthening before publication.
4. **Assumption exposure** — which conclusions hang on which assumptions; attacks on protected axioms (if a G2G programme exists, append these to `01_hard-core.md → Attacks on the core`).
5. **Salvage** — genuinely open gaps the critics' own findings revealed (collisions and refutations often point at the nearest unexplored question).

Offer the full tribunal transcript; never summarize it out of existence. If a `g2g/` workspace exists, append one line per major finding to the contradiction log.

## Calibration

Tribunal severity should track stakes: for a casual idea, critics still file 5 objections but the verdict tone is exploratory; for a submission-ready draft, add a second defense round. Never soften objections because the user seems attached to the idea — the plugin's value is that it does not flatter.
