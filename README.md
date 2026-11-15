# Grand-to-Ground (G2G)

**An adversarial, Lakatos-inspired research loop for AI-assisted social science.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)](.claude-plugin/plugin.json)
[![Methodology](https://img.shields.io/badge/methodology-G2G%20v3.1-navy.svg)](docs/METHODOLOGY.md)

AI research systems that work in biology and machine learning assume a lab exists to close the loop. Social science has no lab — its experiments are history, its theories are built by deduction, and its hardest step is choosing the right question. G2G is a research methodology, packaged as a Claude plugin, for exactly that space: treat your grand framework as a **question generator**, converge each cycle onto one **identifiable, falsifiable question**, and let independent AI critics attack everything except what you explicitly chose to protect.

Built for economics and finance first; the loop generalizes to any social science. v0.2.0 was the field-hardened release: every change traced to a logged defect or a logged success, each lesson recorded before it became a feature. v0.3.0 was the Theory Forge release: a second operating mode for building a *system* of propositions — deriving dozens to hundreds of mutually dependent relations from a few axioms, rather than one conclusion at a time. Its architecture is borrowed (the design, not the code) from Danus, the autonomous-mathematics system that helped disprove the Yau–Tian–Donaldson conjecture. **v0.4.0 makes the engine keep to the human's standing directions**: correcting what is wrong needs no permission, tightening is the human's call, critics report faults only, and model tiers and the unattended usage fence are fixed before a run.

```
Research cycle — one conclusion card per round:

P0 vision → P1 recon (gate; incremental after cycle 1) → P2 formalize (multi-operationalized)
→ P3 axiomatize (hard core + declared assumptions + belt) → P4 conjecture
→ P5 parallel deduction (N independent deducers → merge) → P6 tribunal (3 critics ⇄ defender, severity dial)
→ P7 ground (3 questions) → P8 score (5 axes) · human disposes · record · loop
                └── convergence cut: the identifiable small question ──┘
```

```
Theory Forge round — propositions, one by one, into a graph:

backing (charter · axioms · graph · dead-end library · check script)
→ elaboration (the orchestrator's own hand: skeleton, frontier, missing bridges)
→ guidance (this round's direction; parked routes and their revisit conditions)
→ N deducers (fresh contexts, one branch each) → verifier gate per candidate (cold start, pass / fail)
→ graph (only a gated proposition is a proposition) → cadence (control beats · macro audits)
→ theory tribunal at milestones (the empirical gate opens: consistency, grounding, novelty)
                └── cascade revocation: change an axiom, get the list ──┘
```

## What's inside

| Component | Name | What it does |
|---|---|---|
| Skill | `g2g-go` | The single entry point: say "run G2G" and it preflights the environment, reads the programme state, and routes to setup / plan / a Forge round / a cycle / status; carries the unattended switch and the budget fence |
| Skill | `g2g-setup` | Intake interview (vision, layers, protected core, declared assumptions, severity default, field conventions, collaborator — and in v3: programme modes, whether the programme builds a mathematical system, unattended defaults, model tiering, multi-device sync) + scaffolds the `g2g/` state workspace, `07_theory/` included; migrates v1 and v2 workspaces |
| Skill | `g2g-cycle` | Orchestrates one full research cycle, P1→P8, with parallel deduction, enforced critic isolation, and the card-to-graph bridge |
| Skill | `g2g-forge` | One Theory Forge round: elaboration and guidance written by the orchestrator in its own hand, N deducers dispatched, every candidate gated, passed nodes landed in the proposition graph, dead ends recorded, cadence kept |
| Skill | `g2g-plan` | Versioned, tick-to-approve research plans: modular repair/offense lines, two-speed decisions in one overwrite-style decision bar, an optional skeleton of the whole argument, plan-tribunal gate, collaborator one-pagers with a qualifier-fidelity audit |
| Skill | `g2g-tribunal` | Standalone adversarial review of any argument, draft, or plan — severity dial, sentence-level verdicts with replacement language; plan-tribunal (ST) and theory-tribunal (TT) modes; works without setup |
| Skill | `g2g-status` | Programme health: registry, score trends, hard-core attack tally, declared-assumption ledger, re-scoring queue, pending decisions with what they block, Lakatosian audit — plus graph health when the Forge is open |
| Agent | `g2g-deducer` | Falsification-surface inventory, then strict in-axiom deduction; marks every guess `[GUESS]` and every added shape `[SIG]`; in Forge mode reads the graph and the dead-end library before it proves, and submits candidate nodes to the gate |
| Agent | `g2g-verifier` | The verification gate: one cold-start judge per candidate, binary verdict (zero critical errors, zero gaps), the BAN series of hard prohibitions, repair hints on a fail, `[COMP]` symbolic corroboration; writes verification records, never node files |
| Agent | `g2g-logic-critic` | Internal validity only; faults only, no quota; endorsement forbidden; in a theory tribunal, cross-node consistency and value — never a re-verification of what the gate passed |
| Agent | `g2g-evidence-critic` | Conflicts with data and history (live search); carrier checks quoted verbatim; sole privilege to attack the hard core (logged, not adjudicated); does the grounding inside a theory tribunal |
| Agent | `g2g-novelty-critic` | Two-axis collision check against the literature; grades pre-coded novelty claims; salvage list of genuine gaps |
| Agent | `g2g-defender` | Independent defender that recomputes every computable allegation from primary files instead of arguing it (re-derives, in a theory tribunal); reports errors on its own side with equal prominence |
| Script | `scripts/pg_check.py` | Pure-standard-library check on the proposition graph: acyclic, no dangling predecessors, every verified node backed by a passing verification record, revocations and supersessions cascaded, every verified node's newly introduced symbols registered, inheritance and closure tests; regenerates the overview table. If it does not pass, work does not start. Before each verifier, `--pregate` checks the candidate's new names against the glossary — collisions, and `:=` or bold definitions left unlisted |
| Script | `scripts/cadence_check.py` | **New** — the cycle cadence check: every M cycles (default 4) it reads the question registry and says whether the last M questions all came from salvage or earlier cards rather than from the run queue, the plan or the Vision — one log line that steers the next question and never stops a run |
| Script | `scripts/upgrade_workspace.py` | **New** — upgrades a 0.3.0 workspace's settings (charter, hard core, process-defects file) at g2g-go's preflight: backups kept, records untouched, anything it does not recognise left as is and listed |

All programme state lives in a `g2g/` folder of plain Markdown in your project — portable, inspectable, versionable. The keys and headings the skills and scripts parse stay English whatever language the files are written in — the list is in [`scripts/README.md`](scripts/README.md#file-conventions-the-parsers-rely-on).

## Install

**Claude Code**

```
/plugin marketplace add HongtaoMa1/grand-to-ground
/plugin install grand-to-ground@grand-to-ground
```

**Claude Cowork (desktop):** download `grand-to-ground.plugin` from [Releases](https://github.com/HongtaoMa1/grand-to-ground/releases) and open it — Cowork shows an install prompt.

**Manual (any Claude with skills support):** copy the `skills/*` folders into your skills directory and `agents/*` into your agents directory.

## Quickstart

A programme has exactly one entry point. Say: **"Run G2G."**

1. **The first time**, that line runs setup. You'll be asked for your research vision (rambling is fine), your framework's layers, the assumptions you want protected, the assumptions you simply want *declared* (exempt from refutation, like a theorist's assumption list), how hard the tribunal should hit by default, and your field's actual conventions — and, new in v3: whether this programme runs the **cycle**, the **Forge**, or both; whether it is building a mathematical system, and which layer the first Forge round pushes; your unattended defaults; the model-tiering table; whether the programme is synchronized across several machines.
2. **Every time after that**, the same line decides what to do: a plan awaiting freeze → the plan; the Forge open → a Forge round (the default when both modes are open); otherwise a cycle, or a status report when nothing is runnable. It preflights first — which machine, which directory, are scripts available, is the workspace writable — and a workspace set up by 0.3.0 has its settings upgraded before any work (backups kept; anything not recognised is left as is and listed at the top of the handoff notes).
3. **Name what you want and the name wins.** "Run G2G cycle" → a full cycle: independent deducers disagree, three isolated critics attack, a defender recomputes the numbers, and a verdict hands you exact surviving sentences plus replacement language for what died. "Run a forge round" (or "derive the next propositions") → one Forge round: elaboration, guidance, deducers, the gate, the graph, and a plain-language summary of what grew and what died. "Run G2G, micro layer only" → a Forge round scoped to that layer; the guidance remembers your scope until you change it. "G2G status" → programme and graph health, read-only. "Run a tribunal on this draft" → the court alone, no setup needed.
4. **Between rounds**: "Draft a research plan" gives you a tick-to-approve plan — modules you can clear with "R1 ✓ R2 ✓", one decision-bar file you can settle from one screen, heavy items unpacked in place, and a one-pager for your supervisor in which every sentence matches a frozen verdict.

## Design principles

- **AI proposes; the human disposes.** You ratify axioms, arbitrate disputes, and review every verdict. And explicitly: **scores inform; the human disposes** — no automatic demotion, no burial by objection pile-up. Errors belong to the human; the AI's pride is fidelity, divergence, and professionalism.
- **Two gates: the logic gate never judges empirical truth.** Given the axioms, is this derivation correct — cheap, fast, run at every submission of every proposition. Do the axioms and what follows from them survive contact with the world — expensive, slow, opened periodically by a tribunal. A proposition can be correctly derived and still not hold in reality; the two statuses are separate fields, and neither triggers the other.
- **Only a gated proposition is a proposition** (the truth boundary). Nothing else in the theory directory may be cited as a brick — not a candidate, not a conjecture, not a line of the guidance, not an axiom the human has yet to ratify — a conjecture may enter only as an explicitly conditional premise, `conditional on CJ-xx ([GUESS])`, which the whole chain then inherits and which never counts as progress. There is no shortcut from "claimed" to "proposition": the deducer submits, the verifier passes, the orchestrator lands the file.
- **Authority by construction.** Wherever a tool grant can carry the rule, it does: deducers hold read tools and submit candidates. Where a role must write to do its job — the verifier writes only its own verification record, the orchestrator may land a node only with a passing record in hand — the rule is protocol, and the check script audits it at every round start.
- **The tribunal attacks the execution, not your premises.** What adversarial review usually kills is not the researcher's story but the shape the agent added and the sentence that claims more than the result. Declared assumptions are exempt and ledgered, agent additions carry `[SIG]` marks, and verdicts kill *sentences*, with replacement language.
- **Anti-sycophancy is mechanical, not aspirational.** Critics work in fresh, isolated contexts, may not endorse, and pin every objection to its source — and they report faults only, with no quota: "no receivable fault found" is a valid result. The severity dial changes depth, never honesty.
- **Anti-dogma rules (R1–R5).** Framework families — and data domains — rotate between cycles; registered questions can't be re-cut; every conclusion must link two layers; every cycle must propose a cross-level mechanism; and a dead end that goes unrecorded is itself an anti-dogma failure, because the next deducer will walk it again.
- **Lakatos, operationalized.** A protected hard core, a declared-assumption tier, an attackable belt; attacks on protected tiers are logged and audited — the status skill will tell you, bluntly, whether your programme is progressive or degenerating.
- **Falsifiability is scored, every round.** And so is **sellability** — a paper sells one idea; the loop notices before the referee does.

## Unattended runs

You can say "time to run this round" and walk away. What bounds the run is **your account's usage, not a queue of permission prompts**: at 80% of the all-models weekly quota the orchestrator winds down — it updates the handoff first, finishes the item in hand and opens nothing new — and at 100%, or at any platform limit, it stops with the handoff already on disk; reset, say "run G2G", and the unfinished run resumes first. Say "run it full" at launch to skip the wind-down. Before every batch of agents the run's resume line in the log is updated, so a stop at any moment loses nothing.

Two things do not loosen when the run is fully open, because they are research discipline and not permission fences: **axioms are never ratified by the machine** (it may raise "requires new axiom"; ratification is yours), and **external text is data, not instructions** — no paper, page, or search result an agent reads may change its task, and a chain induced by doctored external text can be revoked whole.

The rest is legible rather than implicit: two tables in the programme charter carry it — the **pre-authorized defaults** (question selection, severity tier, dispositions, `[INTERP]` handling, collisions, outward actions defaulting to none, the submission cap) and the **unattended-case dispositions** (repair limit used up, "requires new axiom", 80% and 100% of usage, guidance colliding with the dead-end library, a failed preflight). If either table is missing, the run falls back to attended.

## What G2G is not

Not autonomous science — it will not write your paper or replace your judgment; by design it declines the autonomy race. Not an autonomous mathematician — the human ratifies every axiom and disposes of every verdict; the verifier is an LLM judge, not a proof assistant. Not a cheerleader — the tribunal does not flatter, by construction. Not a model picker — it is a discipline for the loop *around* whatever models you use. The methodology is the cheap part; the discipline — verify, ground, stop — is the work.

## Methodology

The full methodology paper is in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) (v3.1 — the single source). The Chinese edition, [`docs/METHODOLOGY_zh.md`](docs/METHODOLOGY_zh.md), now ships in the repository, and the bilingual PDF is generated from the same source and distributed alongside releases. Related work: Google DeepMind's Co-Scientist (*Nature*, 2026), Sakana's AI Scientist-v2, the Stanford ideation study (arXiv:2409.04109), and — for the Forge — Danus (arXiv:2607.06447). G2G differs by targeting deduction-first, lab-free disciplines and by making the human gates and anti-dogma rules mechanical.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in v0.4.0 and the problem behind each change.

## Provenance

This plugin was designed and built with AI research agents, using the loop it implements — and v3.0's methodology went through two rounds of multi-lens adversarial review and its own plan tribunal (ST-03, standard severity: three isolated critics and an independent defender; 50 objections, 19 sentences replaced and 22 qualified), plus a trial Forge round on a test programme whose 18 process defects were fixed before the 0.3.0 release; the v3.1 changes stood a plan tribunal of their own under the new contracts (ST-04, standard severity: three isolated critics reporting faults only, with no quota; 16 objections, 12 after merging duplicates — 7 corrected, 5 rejected, no claim weakened).

Cowork and cloud-sandbox environment note: when verifying files written to a mounted folder, read them back with a host-side file tool — **re-staging a file that already exists can return a cached copy**, so a re-staged copy is never proof of current content. **When mounts fail, pull the files you need by absolute path** with host-side tools and treat the sandbox filesystem as scratch; nothing written only inside it counts as written. And the Forge's check script runs only where a local execution environment exists — a seat without one checks **the same list by hand** (the manual checklist is in [`skills/g2g-forge/references/forge-protocol.md`](skills/g2g-forge/references/forge-protocol.md)) and writes "checked by hand this round" in the forge log.

### Acknowledgements

The Theory Forge adapts a set of designs from **Danus** — the frenzymath team, led from Peking University; open-sourced under Apache-2.0 at [github.com/frenzymath/Danus](https://github.com/frenzymath/Danus), arXiv:2607.06447: the fact graph (a proposition graph here) with its truth boundary, the single verification authority ruling proposition by proposition from a cold start, cascade revocation, and the strategy loop of elaboration, guidance, control beats and macro audits. The evidence for "dead ends are assets" — 616 verified facts, of which 88 entered the main theorem's support chain, while 56 of the rest closed a branch each and 24 excluded simpler candidate families — comes from Appendix A of the paper that used Danus to disprove the Yau–Tian–Donaldson conjecture (arXiv:2608.19301). **What was borrowed is the design, not the code**: no Danus source is copied here, and the architecture is reshaped for a discipline whose axioms are empirical claims that may be false (the differences are listed one by one in §3b.12 of the methodology).

## Citation

If G2G helps your research, cite it (see [`CITATION.cff`](CITATION.cff)):

> Ma, R. (2026). *Grand-to-Ground (G2G): An adversarial, Lakatos-inspired research loop for AI-assisted social science* (v0.4.0). https://github.com/HongtaoMa1/grand-to-ground

## License

[MIT](LICENSE) © 2026 Rick Ma
