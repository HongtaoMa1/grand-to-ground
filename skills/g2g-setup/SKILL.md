---
name: g2g-setup
description: Initialize a Grand-to-Ground (G2G) research programme in the current workspace. Use when the user says "set up G2G", "initialize my research programme", "start a new G2G project", "g2g setup", or installs the plugin and asks how to begin. Runs the intake interview (research vision, discipline, framework layers, protected assumptions, declared assumptions, severity default, field conventions, external collaborator, evidence environment) and scaffolds the programme state files. Also migrates a v1 workspace to the v2 layout.
---

# G2G Setup

Initialize a Grand-to-Ground research programme. G2G treats the researcher's grand theoretical framework as a question generator, and converges each cycle onto one identifiable, falsifiable question. This skill creates the persistent state that every other G2G skill reads and writes.

## Step 1 — Check for an existing programme

Look for a `g2g/` directory in the working folder. If it exists and contains `00_programme.md`, tell the user a programme already exists, summarize its charter in 3 lines, and ask whether to (a) resume it, (b) archive it and start fresh, or (c) abort. Never silently overwrite. **v1 → v2 migration:** if the programme predates v2 (no severity tier in the charter, no `05_plans/`), offer to migrate: add the missing files and charter fields with defaults, touch nothing that exists. Old records are never rewritten.

## Step 2 — Intake interview

Ask the user the following, in one batch (use the platform's structured-question UI if available; otherwise plain text). Do not proceed until you have answers to 1–3; use stated defaults for the rest if skipped.

1. **Vision.** "Describe your grand framework or research vision in plain language — hunches, end-state claims, and all. Rambling is fine; formalization happens later." (Free text. This is the P0 input.)
2. **Discipline and layers.** "Which field is this, and what are the 2–4 layers of your framework?" Offer examples: economics/finance → micro behavior / distributional / macro; sociology → individual / institutional / societal; political science → voter / party / regime.
3. **Protected assumptions (hard-core candidates).** "Which 2–5 assumptions is your programme built on — the claims you want protected while everything else gets attacked?" Explain in one sentence: G2G protects a Lakatosian hard core but logs every attack on it and audits programme health over time.
4. **Declared assumptions (exempt working premises).** "Beyond the core: any working assumptions you want to *declare* rather than defend — premises you'd list at the top of a paper, the way a theorist assumes purchasing-power parity? These are exempt from refutation: the tribunal only checks that reasoning stays inside them." (Default: none; they can be declared any time later.)
5. **Severity default.** "How hard should the tribunal hit by default? **exploratory** (hunches and essays — 3 objections per critic, one defense round) / **standard** (working research — 5 objections, two rounds) / **submission** (anything leaving the building — 5 objections, three rounds, independent defender with data recomputation)." (Default: standard. Any single tribunal can override.)
6. **Field conventions.** "What are your target venue's actual conventions — anything reviewers there never do or always expect? (e.g., 'pre-registration rituals are rare in empirical finance')." Seed each answer as a standing ruling so critics calibrate to the venue. (Default: none.)
7. **External collaborator.** "Is there a supervisor or co-author whose rulings should be archived and whose materials (one-pagers, call notes) the plan skill should prepare? Name and role." (Default: none.)
8. **Evidence environment.** "What data, archives, or natural experiments can you plausibly access?" (Default: "to be determined during first grounding".)
9. **Budget and thresholds.** Scoring pass line (default **18/25 with falsifiability ≥ 3/5 and sellability ≥ 2/5**), tribunal rounds per question (per severity tier), critics count (default 3).
10. **Rotation menu.** Show the discipline's default theoretical-framework menu from `references/rotation-menus.md` and ask if they want to add or remove entries. Note that rotation runs on two axes: framework family AND data domain.

## Step 3 — Scaffold the workspace

Create the `g2g/` directory with these files, filling templates from `references/templates.md` with interview answers:

- `g2g/00_programme.md` — charter: vision verbatim, discipline, layers, severity default, field conventions, collaborator, thresholds, rotation menu (two-axis), **ID legend** (pre-filled with the reserved series; every new letter series must be registered here at first use), current phase.
- `g2g/01_hard-core.md` — hard core marked `RATIFIED` after Step 4; **Declared assumptions** section (exempt tier, with quick-scan dates and the silent attack ledger); `Protective belt`; `Attacks on the core` log; **Standing rulings** register (U-series, seeded from question 6); `Corrected facts`; `Pending axiom proposals`.
- `g2g/02_question-registry.md` — registry table (ID, question, framework family, **data domain**, status, card link, expected cross-level mechanism) plus a seeds section. The two-axis genealogy line lives here.
- `g2g/03_records/contradiction-log.md` — empty, with entry format.
- `g2g/03_records/literature-ledger.md` — the P1 incremental-mode asset: nearest neighbors, one-line verdicts, last-checked dates.
- `g2g/03_records/` — conclusion cards accumulate as `card-CXXX.md`; tribunal verdicts as `tribunal-XX.md` / `tribunal-ST-XX.md`; re-score appendices alongside their cards.
- `g2g/04_log.md` — session log; write the first entry (date, "programme initialized").
- `g2g/05_plans/` — versioned research plans (`plan-v001.md`, …) from the g2g-plan skill.
- `g2g/06_process-defects.md` — a living file, mostly written *for the human*: process defects discovered in use, and the human-side rules that fix them. Pre-seed it with the four-line decision format and session-hygiene rules from the template.

## Step 4 — Fact-check before ratifying

**Hard core:** for each candidate axiom, run a quick web check for direct factual conflicts (a false "fact" planted in the core will be defended brilliantly forever after). Report conflicts with sources and let the user decide: revise, keep with a caveat, or demote to the belt. Record corrections. Only then mark `RATIFIED`.

**Declared assumptions:** run a lighter one-time screen — factual howlers and carrier errors only (does the named institution/channel/mechanism exist and carry what the assumption needs?). Do not litigate plausibility; that is the whole point of the tier. Record the scan date. After this, attacks on these assumptions go to the silent ledger only.

## Step 5 — Optional: project entry-point integration

Offer to append a short G2G section to the project's `CLAUDE.md` (or equivalent entry file) so any future session finds the programme. The snippet must follow the entry-file rule: **no version or round numbers ever** — always "the highest-numbered file is current"; and it should name the reading order (`00_programme.md` → latest plan → latest verdict).

## Step 6 — Confirm and hand off

Summarize the charter in ≤6 lines (include severity default and any rulings seeded). Tell the user: "Programme initialized. Say **run a G2G cycle** to start cycle 1, **draft a research plan** for the plan layer, or **G2G status** anytime for programme health." Do not start a cycle without being asked.

## Invariants (apply to every G2G skill)

- The human ratifies axioms, arbitrates disputes, and reviews every verdict. AI proposes; the human disposes — and **scores inform; the human disposes** too: no automatic demotion or burial.
- Errors belong to the human; the AI's pride is fidelity, divergence, and professionalism — never holding the same view as most of the world.
- Nothing enters the hard core unverified. All guesses are marked as guesses; all agent-added shapes are marked `[SIG]`.
- Declared assumptions are exempt from refutation; deviations from them are not.
- State lives in `g2g/` as plain Markdown — portable, inspectable, versionable. Any decision not written into a file did not happen.
