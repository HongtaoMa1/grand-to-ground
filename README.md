# Grand-to-Ground (G2G)

**An adversarial, Lakatos-inspired research loop for AI-assisted social science.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](.claude-plugin/plugin.json)
[![Methodology](https://img.shields.io/badge/methodology-G2G%20v2.0-navy.svg)](docs/METHODOLOGY.md)

AI research systems that work in biology and machine learning assume a lab exists to close the loop. Social science has no lab — its experiments are history, its theories are built by deduction, and its hardest step is choosing the right question. G2G is a research methodology, packaged as a Claude plugin, for exactly that space: treat your grand framework as a **question generator**, converge each cycle onto one **identifiable, falsifiable question**, and let independent AI critics attack everything except what you explicitly chose to protect.

Built for economics and finance first; the loop generalizes to any social science. **v0.2.0 is the field-hardened release**: every change comes from one month of intensive live use on a live finance research programme — five tribunals, three full cycles, six conclusion cards, six generations of research plans — with each lesson logged before it became a feature.

```
P0 vision → P1 recon (gate; incremental after cycle 1) → P2 formalize (multi-operationalized)
→ P3 axiomatize (hard core + declared assumptions + belt) → P4 conjecture
→ P5 parallel deduction (N independent deducers → merge) → P6 tribunal (3 critics ⇄ defender, severity dial)
→ P7 ground (3 questions) → P8 score (5 axes) · human disposes · record · loop
                └── convergence cut: the identifiable small question ──┘
```

## What's inside

| Component | Name | What it does |
|---|---|---|
| Skill | `g2g-setup` | Intake interview (vision, layers, protected core, declared assumptions, severity default, field conventions, collaborator) + scaffolds the `g2g/` state workspace; migrates v1 workspaces |
| Skill | `g2g-cycle` | Orchestrates one full research cycle, P1→P8, with parallel deduction and enforced critic isolation |
| Skill | `g2g-plan` | **New** — versioned, tick-to-approve research plans: modular repair/offense lines, four-line decision bar, plan-tribunal gate, collaborator one-pagers |
| Skill | `g2g-tribunal` | Standalone adversarial review of any argument, draft, or plan — severity dial, sentence-level verdicts with replacement language; works without setup |
| Skill | `g2g-status` | Programme health: registry, score trends, hard-core attack tally, declared-assumption ledger, re-scoring queue, pending decisions with what they block, Lakatosian audit |
| Agent | `g2g-deducer` | Falsification-surface inventory, then strict in-axiom deduction; marks every guess `[GUESS]` and every added shape `[SIG]`; runs solo or as one of N in parallel |
| Agent | `g2g-logic-critic` | Internal validity only; quota by severity; endorsement forbidden |
| Agent | `g2g-evidence-critic` | Conflicts with data and history (live search); carrier checks on institutional anchors; sole privilege to attack the hard core (logged, not adjudicated) |
| Agent | `g2g-novelty-critic` | Two-axis collision check against the literature; grades pre-coded novelty claims; salvage list of genuine gaps |
| Agent | `g2g-defender` | **New** — independent defender that recomputes every computable allegation from primary files instead of arguing it; reports errors on its own side with equal prominence |

All programme state lives in a `g2g/` folder of plain Markdown in your project — portable, inspectable, versionable.

## Install

**Claude Code**

```
/plugin marketplace add HongtaoMa1/grand-to-ground
/plugin install grand-to-ground@grand-to-ground
```

**Claude Cowork (desktop):** download `grand-to-ground.plugin` from [Releases](https://github.com/HongtaoMa1/grand-to-ground/releases) and open it — Cowork shows an install prompt.

**Manual (any Claude with skills support):** copy the `skills/*` folders into your skills directory and `agents/*` into your agents directory.

## Quickstart

1. Install, then say: **"Set up G2G."** You'll be asked for your research vision (rambling is fine), your framework's layers, the assumptions you want protected — and, new in v2: the assumptions you simply want *declared* (exempt from refutation, like a theorist's assumption list), how hard the tribunal should hit by default, and your field's actual conventions.
2. Say: **"Run a G2G cycle."** Watch independent deducers disagree, three isolated critics attack, a defender recompute the numbers, and a verdict hand you exact surviving sentences — plus replacement language for what died.
3. Say: **"Draft a research plan."** You get a tick-to-approve plan: modules you can clear with "R1 ✓ R2 ✓", a decision bar you can settle from one screen, and a one-pager for your supervisor in which every sentence matches a frozen verdict.
4. Anytime: **"G2G status"** for programme health, or **"Run a tribunal on this draft"** to stress-test anything — no setup needed.

## Design principles

- **AI proposes; the human disposes.** You ratify axioms, arbitrate disputes, and review every verdict. And in v2, explicitly: **scores inform; the human disposes** — no automatic demotion, no burial by objection pile-up. Errors belong to the human; the AI's pride is fidelity, divergence, and professionalism.
- **The tribunal attacks the execution, not your premises.** Field evidence was unambiguous: what dies under adversarial review is almost never the researcher's story — it is the shape the agent added and the qualifier the summary dropped. v2 aims the firepower there: declared assumptions are exempt and ledgered, agent additions carry `[SIG]` marks, and verdicts kill *sentences*, with replacement language.
- **Anti-sycophancy is mechanical, not aspirational.** Critics carry minimum-objection quotas, endorsement bans, and fresh contexts per round. The severity dial changes depth, never honesty.
- **Anti-dogma rules (R1–R4).** Framework families — and now data domains — rotate between cycles; registered questions can't be re-cut; every conclusion must link two layers; every cycle must propose a cross-level mechanism.
- **Lakatos, operationalized.** A protected hard core, a declared-assumption tier, an attackable belt; attacks on protected tiers are logged and audited — the status skill will tell you, bluntly, whether your programme is progressive or degenerating.
- **Falsifiability is scored, every round.** And so, now, is **sellability** — a paper sells one idea; the loop notices before the referee does.

## What G2G is not

Not autonomous science — it will not write your paper or replace your judgment; by design it declines the autonomy race. Not a cheerleader — the tribunal does not flatter, by construction. Not a model picker — it is a discipline for the loop *around* whatever models you use. The methodology is the cheap part; the discipline — verify, ground, stop — is the work.

## Methodology

The full methodology paper is in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) (v2.0; the bilingual PDF is distributed alongside releases). Related work: Google DeepMind's Co-Scientist (*Nature*, 2026), Sakana's AI Scientist-v2, Korinek's *AI Agents for Economic Research* (NBER w34202), and the Stanford ideation study (arXiv:2409.04109). G2G differs by targeting deduction-first, lab-free disciplines and by making the human gates and anti-dogma rules mechanical.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in v0.2.0 and the field evidence behind each change.

## Provenance

This plugin was designed and built with AI research agents, using the loop it implements — and v2.0 was revised the same way: the methodology draft stood its own tribunal before release. Cowork environment note: when verifying files written to a mounted folder, read them back with a host-side file tool — re-staging a file that already exists can return a cached copy.

## Citation

If G2G helps your research, cite it (see [`CITATION.cff`](CITATION.cff)):

> Ma, R. (2026). *Grand-to-Ground (G2G): An adversarial, Lakatos-inspired research loop for AI-assisted social science* (v0.2.0). https://github.com/HongtaoMa1/grand-to-ground

## License

[MIT](LICENSE) © 2026 Rick Ma
