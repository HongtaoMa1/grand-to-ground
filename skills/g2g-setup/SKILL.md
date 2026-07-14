---
name: g2g-setup
description: Initialize a Grand-to-Ground (G2G) research programme in the current workspace. Use when the user says "set up G2G", "initialize my research programme", "start a new G2G project", "g2g setup", or installs the plugin and asks how to begin. Runs the intake interview (research vision, discipline, framework layers, protected assumptions, evidence environment) and scaffolds the programme state files.
---

# G2G Setup

Initialize a Grand-to-Ground research programme. G2G treats the researcher's grand theoretical framework as a question generator, and converges each cycle onto one identifiable, falsifiable question. This skill creates the persistent state that every other G2G skill reads and writes.

## Step 1 — Check for an existing programme

Look for a `g2g/` directory in the working folder. If it exists and contains `00_programme.md`, tell the user a programme already exists, summarize its charter in 3 lines, and ask whether to (a) resume it, (b) archive it and start fresh, or (c) abort. Never silently overwrite.

## Step 2 — Intake interview

Ask the user the following, in one batch (use the platform's structured-question UI if available; otherwise ask in plain text). Do not proceed until you have answers to 1–3; use stated defaults for the rest if skipped.

1. **Vision.** "Describe your grand framework or research vision in plain language — hunches, end-state claims, and all. Rambling is fine; formalization happens later." (Free text. This is the P0 input.)
2. **Discipline and layers.** "Which field is this, and what are the 2–4 layers of your framework?" Offer examples: economics/finance → micro behavior / distributional / macro; sociology → individual / institutional / societal; political science → voter / party / regime. The layer names become the programme's cross-level linkage vocabulary.
3. **Protected assumptions (hard-core candidates).** "Which 2–5 assumptions is your programme built on — the claims you want protected while everything else gets attacked?" Explain in one sentence: G2G protects a Lakatosian hard core but logs every attack on it and audits the programme's health over time.
4. **Evidence environment.** "What data, archives, or natural experiments can you plausibly access?" (Default: "to be determined during first grounding".)
5. **Budget and thresholds.** Scoring pass line (default 14/20 with falsifiability ≥ 3/5), tribunal rounds per question (default 3), critics count (default 3).
6. **Rotation menu.** Show the discipline's default theoretical-framework menu from `references/rotation-menus.md` and ask if they want to add or remove entries.

## Step 3 — Scaffold the workspace

Create the `g2g/` directory with these files, filling templates from `references/templates.md` with interview answers:

- `g2g/00_programme.md` — charter: vision verbatim, discipline, layers, thresholds, rotation menu, current phase.
- `g2g/01_hard-core.md` — protected assumptions marked `RATIFIED` (the user just stated them, but verify each against basic facts first — see Step 4), a `Protective belt` section, an `Attacks on the core` log (empty), and a `Corrected facts` section (empty).
- `g2g/02_question-registry.md` — empty registry table (ID, question, framework family used, status, card link, expected cross-level mechanism) plus a seeds section.
- `g2g/03_records/contradiction-log.md` — empty, with entry format.
- `g2g/03_records/` — conclusion cards will accumulate here as `card-CXXX.md`.
- `g2g/04_log.md` — session log; write the first entry (date, "programme initialized").

## Step 4 — Fact-check the hard core before ratifying

For each candidate assumption, run a quick web check for direct factual conflicts (a false "fact" planted in the core will be defended brilliantly forever after). Report conflicts to the user with sources and let them decide: revise, keep with a caveat, or move the claim to the protective belt as a hypothesis. Record corrections in `01_hard-core.md → Corrected facts`. Only then mark assumptions `RATIFIED`.

## Step 5 — Confirm and hand off

Summarize the charter in ≤6 lines. Tell the user: "Programme initialized. Say **run a G2G cycle** to start cycle 1, or **G2G status** anytime for programme health." Do not start a cycle without being asked.

## Invariants (apply to every G2G skill)

- The human ratifies axioms, arbitrates disputes, and reviews every verdict. AI proposes; the human disposes.
- Nothing enters the hard core unverified. All guesses are marked as guesses.
- State lives in `g2g/` as plain Markdown — portable, inspectable, versionable.
