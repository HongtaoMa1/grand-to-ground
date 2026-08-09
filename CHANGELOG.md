# Changelog

## v0.2.0 — 2026-08-09 · the field-hardened release

Methodology v1.0 → **v2.0**; plugin v0.1.0 → **v0.2.0**. Every change below traces to a logged defect or logged success from one month of intensive live use (five tribunals, three full cycles, six conclusion cards, six research-plan generations, a contradiction log, and a process-defects file). Problem IDs (A1–F2) reference the internal v2 update plan.

### Methodology v2.0 (docs/METHODOLOGY.md — single source; bilingual PDF regenerated from it)

- **Re-aimed firepower** (the release's thesis): field evidence showed tribunals kill agent-added shapes and translation-layer oversells, almost never the researcher's story. v2 aims there: `[SIG]` marks, sentence-level verdicts, step-down rule. (C1, E9)
- **Declared-assumptions tier** — exempt working premises between hard core and belt; one-time factual quick-scan; silent attack ledger surfaced at audits. (B2)
- **Severity dial** — exploratory / standard / submission tiers governing quotas, rounds, deducers, defender; depth changes, honesty doesn't. (B1, B6)
- **Parallel deduction** — N independent deducers, falsification-surface inventory first, late merge via divergence list; counters LLM path dependence. (C2, C3)
- **Verdict machinery** — three-value language (alive/dead/undecidable), sentence-level kill tables with replacement language, five overreach verbs patrol, critic-collision adjudication, cross-proposition registration, numbered defense pieces. (D1, D2, D6, D7, C5)
- **Independent defender with data recomputation.** (D3)
- **Five-axis scoring** — adds sellability; pass line 18/25; **scores inform, the human disposes**; re-scoring triggers on archived cards. (F1, B3, D5)
- **The plan layer** (new §6) — versioned tick-to-approve plans, self-containment rule, decision bar with blocking, plan-tribunal gate (ST series), plan-first mode. (A2, A4, A5, D4, E7)
- **Working with the human** (new §7) — four-line decision format, ID legend + dotted revisions, session hygiene, two-seat protocol. (A1, A3, E1–E4)
- **External interface** (new §8) — collaborator rulings verbatim, standard terminology outward, discipline invisibility with the pre-specified red line, step-down rule. (E8, E9)
- **Division of responsibility** (§2) — errors belong to the human; AI pride = fidelity, divergence, professionalism. (B4)
- **P1 three modes** (full/incremental/delegated) with a literature ledger; two-axis sweeps. (E6, D8)
- **R1 rotation on two axes** — framework family AND data domain. (E5)
- **Standing rulings (U-series)** and field-convention calibration. (B5, B6)
- Six new failure modes documented with their guardrails. (§9)

### Plugin

- **New skill `g2g-plan`** — the steering artifact: modular plans, four-line decision bar, plan tribunals, collaborator one-pagers, plan-first mode.
- **New agent `g2g-defender`** — recomputes every computable allegation from primary files; reports own-side errors with equal prominence.
- `g2g-setup` — intake adds declared assumptions, severity default, field conventions, collaborator; scaffolds `05_plans/`, `06_process-defects.md`, literature ledger, ID legend, standing rulings; v1→v2 workspace migration; optional entry-file integration (no version numbers ever).
- `g2g-cycle` — multi-operationalized P2 with carrier checks; parallel P5 with merge protocol; severity-tiered P6 with exemption rule; verdict assembly with kill tables; five-axis P8 with mandatory salvage harvest; plain-language digest + decision bar in every user verdict.
- `g2g-tribunal` — severity dial; plan-tribunal mode (ST series); rulings and exemption handling; nine-part verdict; translation-layer check at submission tier.
- `g2g-status` — re-scoring queue, silent-ledger audit (where the ledger speaks), rulings recap, defense-piece list, pending decisions with blocking, two-axis rotation audit, expanded hygiene checks.
- Critics — quotas parameterized by severity; exemption rule (`LOGGED (exempt)`); standing-ruling stand-downs; carrier checks (evidence); two-axis search and pre-coded claim grading (novelty); collision non-avoidance (all).
- `templates.md` — new templates: verdict, research plan, literature ledger, one-pager/call notes, process-defects file, ID legend, silent ledger, rulings register; card gains five axes, disposition, re-scoring triggers, pre-coded novelty claim.
- `rotation-menus.md` — data-domain axis; learning/time-varying-parameters family added.

### Migration

Running `g2g-setup` (or any v2 skill) on a v1 `g2g/` workspace offers automatic migration: missing files and charter fields are added with defaults; existing records are never rewritten. Old cards keep their /20 scores; new cards score /25.

## v0.1.0 — 2026-07-13

Initial release: methodology v1.0 (bilingual PDF), skills g2g-setup / g2g-cycle / g2g-tribunal / g2g-status, agents g2g-deducer / g2g-logic-critic / g2g-evidence-critic / g2g-novelty-critic.
