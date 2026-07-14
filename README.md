# Grand-to-Ground (G2G)

**An adversarial, Lakatos-inspired research loop for AI-assisted social science.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](.claude-plugin/plugin.json)
[![Methodology](https://img.shields.io/badge/methodology-G2G%20v1.0-navy.svg)](docs/METHODOLOGY.md)

AI research systems that work in biology and machine learning assume a lab exists to close the loop. Social science has no lab — its experiments are history, its theories are built by deduction, and its hardest step is choosing the right question. G2G is a research methodology, packaged as a Claude plugin, for exactly that space: treat your grand framework as a **question generator**, converge each cycle onto one **identifiable, falsifiable question**, and let independent AI critics attack everything except the axioms you explicitly chose to protect.

Built for economics and finance first; the loop generalizes to any social science.

```
P0 vision → P1 recon (gate) → P2 formalize → P3 axiomatize (hard core + belt)
→ P4 conjecture → P5 deduce → P6 tribunal (3 critics ⇄ defense)
→ P7 ground (3 questions) → P8 score · record · loop
                └── convergence cut: the identifiable small question ──┘
```

## What's inside

| Component | Name | What it does |
|---|---|---|
| Skill | `g2g-setup` | Intake interview (vision, layers, protected assumptions, thresholds) + scaffolds the `g2g/` state workspace |
| Skill | `g2g-cycle` | Orchestrates one full research cycle, P1→P8, spawning the agents below with enforced isolation |
| Skill | `g2g-tribunal` | Standalone adversarial review of any argument or draft — works without setup |
| Skill | `g2g-status` | Programme health: registry, score trends, hard-core attack tally, Lakatosian progressive-vs-degenerating audit |
| Agent | `g2g-deducer` | Derives consequences strictly inside your axioms; marks every guess; defends within axioms only |
| Agent | `g2g-logic-critic` | Internal validity only; ≥5 objections, endorsement forbidden |
| Agent | `g2g-evidence-critic` | Conflicts with data and history (live search); sole privilege to attack the hard core (logged, not adjudicated) |
| Agent | `g2g-novelty-critic` | Collision check against the literature; similarity ratings; salvage list of genuine gaps |

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

1. Install, then say: **“Set up G2G.”** You'll be asked for your research vision (rambling is fine), your framework's layers, and the 2–5 assumptions you want protected. Everything else has defaults.
2. Say: **“Run a G2G cycle.”** Pick a question, then watch it get deduced, attacked by three isolated critics, defended, grounded, and scored. Expect casualties — the first cycle usually kills most conclusions. What survives is real, and the tribunal's own findings point at the nearest unoccupied research ground.
3. Anytime: **“G2G status”** for programme health, or **“Run a tribunal on this draft”** to stress-test anything — no setup needed.

## Design principles

- **AI proposes; the human disposes.** You ratify axioms, arbitrate disputes, and review every verdict. Nothing enters the hard core unverified.
- **Anti-sycophancy is mechanical, not aspirational.** Critics carry minimum-objection quotas, endorsement bans, and fresh contexts per round — agents sharing one long conversation converge, and the entire point is that they must not.
- **Anti-dogma rules (R1–R4).** Framework families rotate between cycles; registered questions can't be re-cut; every conclusion must link at least two layers of your framework; every cycle must propose a cross-level mechanism. Your favorite model is an entry point, never a mandate.
- **Lakatos, operationalized.** A protected hard core plus an attackable belt; attacks on the core are logged and periodically audited — the status skill will tell you, bluntly, whether your programme is progressive or degenerating.
- **Falsifiability is scored, every round.** A claim nothing could refute is decoration, not research.

## What G2G is not

Not autonomous science — it will not write your paper or replace your judgment. Not a cheerleader — the tribunal does not flatter, by construction. Not a model picker — it is a discipline for the loop *around* whatever models you use. The methodology is the cheap part; the discipline — verify, ground, stop — is the work.

## Methodology

The full methodology paper is in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md). Related work: Google DeepMind's Co-Scientist (*Nature*, 2026), Sakana's AI Scientist-v2, Korinek's *AI Agents for Economic Research* (NBER w34202), and the Stanford ideation study (arXiv:2409.04109). G2G differs by targeting deduction-first, lab-free disciplines and by making the human gates and anti-dogma rules mechanical.

## Provenance

This plugin was designed and built with AI research agents, using the loop it implements — the methodology's first test subject was itself.

## Citation

If G2G helps your research, cite it (see [`CITATION.cff`](CITATION.cff)):

> Ma, R. (2026). *Grand-to-Ground (G2G): An adversarial, Lakatos-inspired research loop for AI-assisted social science* (v0.1.0). https://github.com/HongtaoMa1/grand-to-ground

## License

[MIT](LICENSE) © 2026 Rick Ma
