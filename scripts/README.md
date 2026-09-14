# scripts/ — `pg_check.py`, the Theory Forge check script

`pg_check.py` is the pure-standard-library reinforcement of the Forge's "authority by construction" rule (`docs/METHODOLOGY.md` §3b.5): it reads `g2g/07_theory/` and reports every state the protocol forbids. It runs at the start of every Forge round (g2g-forge step 1) and in the g2g-status graph-health section; g2g-go's preflight only reports whether it can run. **If it does not pass, work does not start.** Python ≥ 3.10, no packages, Windows/macOS/Linux, UTF-8.

## CLI

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/pg_check.py" g2g --report                                  # the form every skill uses; cwd = the user's project root
python scripts/pg_check.py <programme_root> [--report] [--regen-index] [--fill-sha] [--json] [--version]   # general form (repository checkout / development)
```

`${CLAUDE_PLUGIN_ROOT}` is the installed plugin's root (a repository checkout's root when developing). `<programme_root>` is the folder containing `g2g/`, the `g2g/` folder itself, or `g2g/07_theory/` — the skills pass `g2g` with cwd = the project root. `--version` prints the script version and is g2g-go's script-availability test. Without flags it only checks and prints one line per violation: `CODE  file  message` (file relative to the programme root). `--report` appends a health summary (counts by status / kind / empirical status, axiom and conjecture statuses, support closure of every theorem-kind node, cadence hints from `forge-log.md` with defaults K=10 / M=4 / T=25, informational findings). The cadence reader takes the round number **only from entry title lines `## Round n`** (never from prose — "macro audit at round 4" in a Cadence line does not count) and the submitted / passed counts from the `a / b / c` triple of each "Submitted" line; when the log's cumulative passed count is below the number of `verified` nodes on disk (typically 0 / 0 against freshly landed nodes) the report adds one line, `(forge-log has no entry for the nodes on disk yet — write the round entry)`. `--regen-index` rewrites `graph-index.md` from the node files (columns: ID · one-liner · kind · status · empirical_status · predecessors · A/D/DA used · verification · layer). `--fill-sha` writes `content_sha` (first 12 hex of sha256 over the Statement + Derivation texts, line endings normalised) where missing or stale — into **both** `propositions/` and `candidates/`: a candidate's digest is fixed before the gate, so a Statement or Derivation that changes between submission and landing shows up as `STALE_SHA` once the file is in `propositions/` (tamper evidence across the gate); the `MISSING_SHA` / `STALE_SHA` checks themselves are raised for `propositions/` only. `--json` emits everything as one JSON document (`report` is `null` unless `--report` is also given). Only `--regen-index` and `--fill-sha` modify files; nothing is ever deleted. Output is UTF-8: the script switches stdout / stderr to UTF-8 itself (no `PYTHONIOENCODING` needed on Windows); if that fails the report falls back to ASCII glyphs (`->`, `-`, `,`).

## Exit codes

Exit code = number of violations (0 = clean), capped at 255. `2` = usage / IO error (no `07_theory/` found, unreadable file) — distinguishable from two violations by the `error:` line on stderr and the empty stdout.

## Violation codes (counted)

| Code | Condition | Spec |
|---|---|---|
| `BAD_FRONTMATTER` | no `---` block; missing `id` / `kind` / `status` / `predecessors`; unknown status; id ≠ file name; duplicate id; V- record without id / candidate / verdict | App. C |
| `ID_FORMAT` | id not `P-dddd` or `P-dddd.n` | App. B |
| `DANGLING` | predecessor not found; `conditional_on` CJ not in `conjectures.md` | 3b.3 |
| `CYCLE` | dependency cycle (reported once per cycle, on its first node) | 3b.3 |
| `PROPOSED_IN_PROPOSITIONS` / `VERIFIED_IN_CANDIDATES` | status and directory disagree | 3b.3 |
| `VERIFIED_NO_PASS` | verified node without a V- record whose `candidate` matches and `verdict: pass` (a revision may keep the original's record named in `verification`) | 3b.5, 3b.8 |
| `UNVERIFIED_PREDECESSOR` | verified node cites a `proposed` node | BAN-12 |
| `REVOKE_NOT_CASCADED` | verified node cites a revoked / superseded predecessor, a revoked A-/D-, or is conditional on a `dropped` conjecture | 3b.8, 3b.9 |
| `PENDING_AXIOM_CITED` | verified node cites an A-/D- that is pending or absent from `axioms.md` | BAN-12 |
| `UNREGISTERED_SYMBOL` | verified node's `glossary_introduces` not in `glossary.md` (candidates exempt) | BAN-13 |
| `CONDITIONAL_NOT_INHERITED` | a predecessor's `conditional_on` entries are missing from the node's own | BAN-03 |
| `CONDITIONAL_WITHOUT_GUESS` | `conditional_on` non-empty but `markers` lacks GUESS | App. C |
| `FAITHFUL_WITH_SIG` | `operationalization: faithful` but SIG (or a strengthened / extended node) sits in its support closure — `markers` lists a node's **own** marks only, so inherited SIG is found by walking the predecessors, not read from the node's header | 3b.4 |
| `FAITHFUL_WITH_CONDITION` | `operationalization: faithful` but a non-empty `conditional_on` sits in its support closure (its own or a predecessor's) — a provisional premise is not a shape present in the ratified axioms, so a conditional node is at least **strengthened**. The other half of the same rule, reported under its own code so the two are told apart | 3b.4 |
| `EXEMPT_REVISION_CHANGED` | a revision (`P-xxxx.n` with `revision_of`) that keeps the **original's** verification record — the one revision 3b.8 exempts from the gate — but differs from the original by more than the licensed swap: `conditional on CJ-xx ([GUESS])` → `by A-xx` in the Statement / Derivation (a sentence-initial capital is kept) plus the removal of that one CJ from `conditional_on`. Any other difference, or a removal of no CJ or of more than one, is a revision that must open a verifier. A revision citing a **new** V- id passed the gate on its own and is not checked by this rule | 3b.8, 3b.9 |
| `MISSING_SHA` / `STALE_SHA` | `content_sha` absent or ≠ recomputed digest, nodes in `propositions/` only (`--fill-sha` also stamps `candidates/`, so the digest is fixed before the gate) | 3b.5 |

Informational, `--report` only, never counted: `CLOSURE_NOT_CLOSED` (theorem verified but `conditional_on` non-empty, 3b.7), `SCOPE_MISMATCH` (closure ≠ unconditional verified nodes tagged `scope: <theorem>`, 3b.7), `DUPLICATE_SHA` (identical Statement + Derivation digest in two live nodes).

Bare predecessor IDs resolve to the family's highest **verified** revision, else the highest not revoked / superseded, else the highest present (3b.8); an explicit `P-0007.1` resolves exactly.

## Manual checklist equivalence

Where scripts cannot run, the same list is checked by hand and the forge log says "checked by hand this round" (3b.5). The manual list is §6 of `skills/g2g-forge/references/forge-protocol.md`, 14 items, one-to-one with the codes: 1 headers well-formed → `BAD_FRONTMATTER`, `ID_FORMAT`; 2 acyclic → `CYCLE`; 3 no dangling references → `DANGLING`; 4 status and directory agree → `PROPOSED_IN_PROPOSITIONS`, `VERIFIED_IN_CANDIDATES`; 5 every verified node has a passing V- → `VERIFIED_NO_PASS`; 6 only verified bricks → `UNVERIFIED_PREDECESSOR`; 7 revocations and supersessions cascaded (bare IDs resolve to the current revision — the resolver above) → `REVOKE_NOT_CASCADED`; 8 no pending bricks → `PENDING_AXIOM_CITED`; 9 glossary complete → `UNREGISTERED_SYMBOL`; 10 condition inheritance and the GUESS mark → `CONDITIONAL_NOT_INHERITED`, `CONDITIONAL_WITHOUT_GUESS`; 11 faithful means no signature → `FAITHFUL_WITH_SIG` and, for the `conditional_on` half of the same 3b.4 rule, `FAITHFUL_WITH_CONDITION`; 12 digests filled and current → `MISSING_SHA`, `STALE_SHA` (+ informational `DUPLICATE_SHA`; `--fill-sha` fills them); 13 closure test → `--report` theorem lines, informational `CLOSURE_NOT_CLOSED` / `SCOPE_MISMATCH`; 14 overview table → `--regen-index`.

`EXEMPT_REVISION_CHANGED` has no number in that list: the gate-exempt CJ → A- swap is checked by 3b.8's own rule, and where scripts cannot run the orchestrator compares the two revisions by hand and logs one line in the forge log.

## File conventions the parsers rely on

Node frontmatter: `key: value`, lists as `[a, b]`, `# comments` allowed after a space; sections `## Statement`, `## Derivation`, `## Falsification surface`, `## Notes`. `axioms.md` / `conjectures.md`: one entry per line (bullet, bold, table row or `##` heading) starting with the ID; the status is the first status word after `status:` (or after the ID) — `RATIFIED / PENDING / REVOKED` (also 已批 / 待批 / 撤销) and `open / promoted / ratified / dropped`. `glossary.md`: first column of a table (header row skipped) or `- symbol · …` bullets; backticks and `$` are ignored. V- records: frontmatter `id`, `candidate` (first `P-` token is used), `verdict`.

- Never put a README or any other non-node `.md` inside `candidates/`, `propositions/` or `verifications/` — every `.md` there is parsed as a node or a verification record; use an empty `.gitkeep` to keep empty folders.

## Tests

```
python -m unittest discover -s scripts/tests -v
```

30 tests, all green. `scripts/tests/fixture_ok/` is a seven-node clean programme (ratified axiom pair + base definition, a derived definition, two lemmas and a wording revision that re-passed the gate on its own V- record, a target theorem with `scope`, a node conditional on an open CJ and therefore tagged `strengthened`, one returned candidate, matching V- records, glossary, forge log). `scripts/tests/fixture_bad/` trips every counted code at least once and additionally carries the positive control for the gate-exempt revision (P-0038 → P-0038.1: the licensed swap and nothing else, which must trip no code). The tests assert the exact `(code, file)` list, the exit code, `--json`, `--regen-index` output and idempotence, `--fill-sha` round trip, idempotence and CRLF preservation, the forge-log reader (round numbers from `## Round n` titles only; the "forge-log has no entry" hint), UTF-8 report output without `PYTHONIOENCODING` (plus the ASCII fallback), and — for the two checks added after tribunal ST-03 — that a conditional node passes when tagged `strengthened` and trips `FAITHFUL_WITH_CONDITION` alone when tagged `faithful`, that the licensed swap passes while an extra step trips `EXEMPT_REVISION_CHANGED`, that a revision citing a new V- id is not judged by that rule while the same revision pointed at the original's record is, and that the swap keeps a sentence-initial capital.
