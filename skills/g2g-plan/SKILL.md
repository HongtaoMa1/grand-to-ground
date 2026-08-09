---
name: g2g-plan
description: Draft or iterate a versioned research plan — the G2G steering artifact between cycles and execution. Produces modular, tick-to-approve plans (repair line + offense lines) with a plain-language digest, a four-line decision bar annotated with what each pending decision blocks, and self-contained objection summaries; runs the plan-level tribunal gate before a plan freezes or goes to an external collaborator; prepares collaborator materials (one-page brief, call notes). Supports plan-first mode (iterate plans on feedback without running empirics). Use when the user says "draft a research plan", "update the plan", "next version of the plan", "plan the next round", "g2g plan", or "prepare materials for my supervisor/co-author".
---

# G2G Plan

The versioned research plan is the steering wheel of a G2G programme: it translates tribunal verdicts into next actions, carries the human's approvals, and briefs whoever executes. This skill writes and iterates plans in `g2g/05_plans/` (`plan-v001.md`, `plan-v002.md`, …). Requires an initialized `g2g/` workspace; without one, offer to run g2g-setup or produce a standalone plan using the same anatomy.

## Step 1 — Read the state

Read, in order: `00_programme.md` (charter, severity, ID legend, collaborator), the highest-numbered plan in `05_plans/` (its approval record at the file end is the baseline — never renumber or reinterpret recorded approvals), the latest tribunal verdict(s) and cards in `03_records/` (the substitution tables there are the **binding wording baseline**), and `02_question-registry.md` (seeds and genealogy for offense candidates).

## Step 2 — Draft plan vN+1

Anatomy, in this order:

1. **Header** — version, date, status (`draft — awaiting ticks`), inputs (which verdicts/rulings/feedback this version digests).
2. **Plain-language digest (§0)** — half a page the human reads first. No internal jargon, no IDs without a gloss. What happened, what this version changes, what they need to do. Write it last, place it first.
3. **Module lines, tick-to-approve:**
   - **Repair line R1…Rn (mandatory):** one module per accepted tribunal finding. **Self-containment rule:** every module that responds to an objection carries a one-line plain restatement of that objection — *"R3: (critic found the control window overlaps the event window, so the placebo is contaminated) → re-draw windows disjoint."* A plan that says "fix per L8, see tribunal file" has outsourced its own comprehensibility; the human must be able to review without a decoder.
   - **Offense lines A/B/C… (optional):** from tribunal salvage and registry seeds, each with its expected cross-level mechanism in one sentence and its rotation-compliance note (both axes).
   - Every module gets a tick box. Approval is a tick: "R1 ✓ R2 ✓ A skip" completes review.
4. **Decision bar** — every open decision in the **four-line format**: *what was done* (one sentence of context) / *what you must decide* (a concrete choice, never an open question) / *default* ("takes effect unless changed", genuinely executable) / *cost of not deciding* — plus a **blocks** column naming what stalls while it waits. Three prohibitions: no "see §X" pointers that make the human fetch context; no missing defaults; no undefined jargon inside a decision item. Adequacy standard: decidable from this screen alone.
5. **Frozen-wording appendix** — sentences this plan carries forward from verdicts, quoted exactly from the substitution tables (qualifiers included). The plan may compress logistics, never wording.
6. **Approval record (file end)** — dated ticks and rulings as the human writes them. Append-only.

## Step 3 — Version discipline

- Generating vN+1 triggers the **archive prompt**: list vN's handover items (task briefs, start prompts) that should move to the executed round's directory, and remind the human. Do not delete anything yourself.
- **Entry files never name versions.** If the project's `CLAUDE.md` (or equivalent) references plans, the phrasing is "highest version is current" — a hard-coded round number in an entry file once silently pointed a whole execution round at the previous round's spec.
- IDs follow the programme legend (`00_programme.md`); new series must be registered there first. Revisions use dotted numbers (R2.1), never accumulated primes.

## Step 4 — The plan tribunal gate

Before a plan's propositions enter a frozen registry, or the plan (or any material derived from it) goes to an external collaborator: **the plan stands tribunal** — invoke g2g-tribunal in plan mode (ST series). The target is the new shapes and mappings this plan adds (formalizations, framings, outward translations), not the frozen results it cites. Exemptions: purely editorial revisions (wording, layout) don't trigger; a small change to an already-tried plan (no new shapes) doesn't trigger, but is logged. Field record: the first plan tribunal found fourteen dead sentences, all in the translation layer — the gate exists because that layer had no other guard.

## Step 5 — Collaborator materials (when the charter names one)

- **One-page brief:** the plan's story in the collaborator's professional language — **standard field terminology only**; internal pet names never leave the building. Every results sentence passes the **step-down rule**: aligned sentence-by-sentence with frozen verdict wording, qualifiers intact.
- **Call notes card:** the questions to ask, the answers to have ready (including the standard answer to any question previously fumbled), decisions wanted from the call.
- **Rulings archive:** after contact, record the collaborator's decisions *verbatim and dated* in the plan's inputs section (and as standing rulings if they are standing) — collaborator rulings are argued with the human, never silently re-litigated by agents. A collaborator's spoken story receives the P2 treatment when formalized: multi-operationalization, `[SIG]` marks — their intuition has the same rank as the user's; the signature dies, not the story.
- **Discipline invisibility:** outward materials never showcase the internal machinery (frozen registries, tribunals, substitution tables) — results, nulls, caveats, and data gaps are reported in full; process narrative is not. **Red line: a test added after results were known is never described outward as pre-specified. "Not saying" ≠ "saying the reverse."**

## Plan-first mode

On request ("plan-first", "no empirics yet", or a collaborator gate in force): iterate plan → digest → human/collaborator feedback → plan vN+1, with no empirical execution, until the frame is agreed. Each iteration still passes Step 4 before going outward. Cheaper than running studies nobody has agreed to want.

## Handoff

End every run with: the digest, the tick list, the decision bar (with blocks), and — if an execution seat exists — the handover kit per `references/collaboration-protocol.md`. One session, one plan version; write the state, then stop.
