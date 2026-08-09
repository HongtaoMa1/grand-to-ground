# The two-seat protocol — running a programme across a planning seat and an execution seat

Real programmes split the work: a **planning seat** (orchestration, G2G cycles and tribunals, records, plans, human interface) and an **execution seat** (data acquisition, computation, code, empirical production). Often these are two different AI products or sessions; the protocol is seat-based, not product-based. Every rule below was written after its absence caused a logged failure.

## Territories

| | Planning seat | Execution seat |
|---|---|---|
| Does | cycles, tribunals, plans, records, outward materials, task briefs | data, code, computation, empirical outputs, run reports |
| May write | `g2g/` workspace, plans, handover kit, shared log | current round's output directory, its own handover artifacts, shared log |
| **Forbidden zone** | **never edits empirical code or outputs** | **never edits G2G records, plans, or prior rounds' directories** |

Both seats append to a shared chronological log, each entry tagged with its seat. **History is append-only — never rewrite an existing entry.**

## Handover kits (fixed contents; a handover without its kit did not happen)

**Planning → execution:**
1. Task brief (the full spec: what to run, on what, with what frozen parameters).
2. Start prompt (a short paste-able launcher: points to paths, states the iron rules, names the deliverables — the brief holds the detail, the prompt holds the pointer).
3. Decision defaults (what the human pre-decided, so execution never stalls on a known answer).
4. Unattended dispositions (if X fails / data missing / ambiguity Y → do Z; mark N/A and report, never fabricate).

**Execution → planning:**
1. Run report (what ran, what didn't, deviations).
2. Results reading (plain-language interpretation, flagged uncertainties).
3. Objection reconciliation (how the run answered any outstanding tribunal findings assigned to it).
4. One log line in the shared log.

## Entry files and archiving

- **Entry-point files (project `CLAUDE.md` or equivalent) never contain version or round numbers.** Always "take the highest-numbered file." A hard-coded round number once silently pointed a full execution round at the previous round's spec — caught only by a pre-flight check.
- The handover directory holds **only the current round's kit**. Archiving moment = the moment the next round's brief is generated: the old kit moves into the executed round's directory. If multiple briefs are ever found, the highest round wins, and the agent proactively prompts the human to archive.

## Session switching (the mechanics, written down because human memory decays)

1. Start the execution seat **in the project root** (entry files are found by location).
2. Paste the start prompt's marked section, whole.
3. On return, the planning seat's first read is: the shared log's last three entries, then the current state file — before doing anything else.
4. **State lives in files, not in sessions. Any decision not written into a file did not happen.** (The iron rule of the whole protocol.)

## Session hygiene (the human-side rules)

- **One session, one thing.** Planning / learning / execution / writing are four session types; don't mix.
- **Learning sessions are disposable.** Understanding a concept or a result needs no project context — open, learn, discard. Teach-back matters: a deliverable the human can't explain isn't delivered yet.
- **Hand off at stage boundaries, not at context exhaustion.** Signals it's time: the agent repeats things you've heard; it misremembers an early detail; a big stage just closed; you're changing topics and the new one doesn't need the old context. Handing off = write state to files, open fresh, new session reads files.
- Don't do heavy work and tutoring in the same session — different depth settings, different sessions.
