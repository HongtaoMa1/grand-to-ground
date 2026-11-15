#!/usr/bin/env python3
"""upgrade_workspace.py - upgrade the settings of a Grand-to-Ground (G2G) 0.3.0 workspace to 0.4.0.

g2g-go runs it at preflight (Step 0, item 5) once the preflight has passed and scripts can run:
first with ``--check`` (writes nothing), then, when an upgrade is due, without it.  It changes only
the recognised, mechanical 0.3.0 forms in three files of the ``g2g/`` workspace:

- ``00_programme.md`` (the charter): deletes the pre-authorized-defaults rows keyed
  ``round_token_budget_estimate`` and ``period_share``; replaces the 0.3.0 model-tiering table with
  the new one, mapping cells by role (the cells the project changed are kept); strikes every
  recognised sentence that lets the orchestrator move an agent one tier up or down for remaining
  budget; replaces the 0.3.0 budget-fence paragraph and the two 0.3.0 budget rows of the
  unattended-case dispositions; and, when it upgrades anything, sets ``Methodology: G2G v3.0`` to v3.1.
- ``01_hard-core.md``: replaces the 0.3.0 U-series title and puts the rule line under it; the old
  table, its entries and their scopes are untouched.
- ``06_process-defects.md``: deletes the rules the 0.3.0 template seeded, where they still read word
  for word as seeded, and any heading they leave empty.

Anything else is left as is; what looks like an old form but is not recognised is listed, never
guessed.  Before its first write to a file the script copies it to ``<name>.v0.3.0.md`` beside it,
once; an existing backup is never overwritten.  A second run changes nothing.

Report: line 1 is the summary for the first line of the handoff notes; then, when an upgrade is due,
one ``left as is`` line per unrecognised old form (and per kept tier cell that differs from the new
table) and the full text of every deleted line that held more than the template's own text.  With
nothing due the report is line 1 alone.

Pure standard library, Python >= 3.10, UTF-8 (a BOM and each file's line endings are kept).  Usage::

    python "${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_workspace.py" g2g --check   # g2g-go preflight: detect only
    python "${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_workspace.py" g2g           # upgrade
    python scripts/upgrade_workspace.py <workspace> [--check] [--json]

``<workspace>`` is the ``g2g/`` folder or the folder that contains it.  Exit code with ``--check``:
0 = current, 1 = upgrade due, 2 = usage or IO error; without it: 0 = upgraded (or nothing to do),
1 = upgraded with items left as is, 2 = usage or IO error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.4.0"
CHARTER, HARD_CORE, DEFECTS = "00_programme.md", "01_hard-core.md", "06_process-defects.md"
FILES = (CHARTER, HARD_CORE, DEFECTS)
BACKUP_SUFFIX = ".v0.3.0.md"
METHODOLOGY_FROM, METHODOLOGY_TO = "v3.0", "v3.1"
EXIT_OK, EXIT_DUE, EXIT_USAGE = 0, 1, 2  # EXIT_DUE: --check = upgrade due; upgrade = items left as is
QUOTE_MAX = 100

# --- New blocks, verbatim from skills/g2g-setup/references/templates.md (a test keeps them equal) ---

#: T2 - the charter's Model tiering block (table, blank line, rule line).
NEW_TIER_BLOCK = (
    "| Role | Exploratory | Standard | Submission |",
    "|---|---|---|---|",
    "| Orchestrator (main session) | inherit | inherit | inherit |",
    "| Deducer — new derivation | inherit | inherit | inherit |",
    "| Mechanical revision of a derivation that already passed the gate | opus | opus | opus |",
    "| **Verifier (gate)** | **inherit** | **inherit** | **inherit** |",
    "| Logic critic | opus | opus | opus |",
    "| Evidence critic / novelty critic | opus | opus | opus |",
    "| Defender | opus | opus | inherit |",
    "| Architecture / synthesis / final drafting | inherit | inherit | inherit |",
    "| Reading / retrieval / checking / fidelity / blind reading / bookkeeping / preflight | opus | opus | opus |",
    "",
    "Rules: the human may change any cell at any time. Tiers follow this table: once a run starts, no tier "
    "changes because of quota, up or down — if a tier's quota runs out, the run stops (budget fence) and that "
    "seat resumes at its tier after the reset; finished work is never redone, whatever tier it ran at; only an "
    "explicit instruction from the human (e.g. \"this time is special\") changes a tier. **The gate is never "
    "below the table.** A seat this table does not name takes the row closest to it, named in the dispatch.",
)
#: T3 - the budget-fence paragraph under the pre-authorized defaults table.
NEW_FENCE = (
    "Budget fence (the boundary of unattended operation is usage, not a permission gate): the usage reading is "
    "the account's all-models weekly quota. At 80% wind down — update the handoff first, finish the item in "
    "hand, open no new item (in the Forge: gate the candidates already submitted, repairs included; no new "
    "deducers). At 100%, or on any platform limit (for example one model's own quota running out first), stop "
    "— the handoff is already on disk; the human resets and resumes. If the human says at launch \"run it "
    "full\" or \"run it out\", skip the wind-down and run to the limit; \"wind down at X%\" means X. With no "
    "usage reading, run to the platform limit. Before each dispatch batch the run's resume line in `04_log.md` "
    "is overwritten in place (g2g-go Step 4), so a stop loses nothing."
)
#: T4 - the two budget rows of the unattended-case dispositions.
NEW_D3_ROWS = (
    "| Usage at 80% (the all-models weekly reading), or the X% the human named at launch | Wind down: update "
    "the handoff first, finish the item in hand (Forge: gate the candidates already submitted, repairs "
    "included), open no new item or deducer — skipped if the human said \"run it full\" or \"run it out\" at "
    "launch |",
    "| Usage at 100%, or any platform limit hit (e.g. one model's own quota) | Stop; the handoff is already on "
    "disk; the human resets and resumes |",
)
#: T1 - the U-series title of 01_hard-core.md and the rule line under it.
NEW_U = (
    "## Standing rulings (U-series — the human's standing directions)",
    "Rule: each entry points to the human's own words (file + section or line) and records the reading the "
    "human confirmed; default scope: the orchestrator and every seat. A critic whose objection falls under an "
    "entry cites it and stands down; the orchestrator follows it wherever the methodology leaves a choice — "
    "the next question, an open default, what enters a record or a digest. An entry is added only when the "
    "human says a direction is standing or confirms the AI's reading — an AI paraphrase alone never adds one. "
    "No entry switches off a step the methodology makes mandatory or leaves a wrong fact uncorrected.",
)
#: The note a struck tier-move sentence carries.
VOID_NOTE = " (void from G2G 0.4.0: tiers follow the table; no tier changes for quota once a run starts)"

# --- Old forms: templates.md as released in 0.3.0, plus the plugin's own 0.3.0 methodology variants ---

OLD_TIER_TABLE = (
    "| Role | Exploratory | Standard | Submission |",
    "|---|---|---|---|",
    "| Orchestrator (main session) | inherit | inherit | inherit |",
    "| Deducer | opus | inherit | inherit |",
    "| **Verifier (gate)** | **inherit** | **inherit** | **inherit** |",
    "| Logic critic | opus | inherit | inherit |",
    "| Evidence critic / novelty critic | opus | opus | inherit |",
    "| Defender | — (no independent defense at exploratory) | opus | inherit |",
)
OLD_TIER_RULES = (
    "Rules: the human may change any cell at any time. The orchestrator may move an individual agent one tier "
    "up or down from this table according to task difficulty and remaining budget; **the gate may not go below "
    "the table**. Principle — allocation by the **reversibility of error**: a gate error enters the graph and is "
    "undone only by cascade revocation, so the verifier is never below `inherit`; a critic's or defender's "
    "finding is a suggestion the human disposes of, so those seats may run a tier lower — except at submission "
    "severity, where the defender, the evidence critic and the novelty critic judge material about to leave the "
    "building and all run at `inherit`."
)
OLD_BUDGET_ROWS = (
    "| **Per-round budget (ceiling)** | `round_token_budget_estimate` | [to be filled by the human — **as a "
    "number of agent calls or of tokens; state the unit**, e.g. \"15 calls\" or \"800k tokens\"; the 80% / 100% "
    "rule applies in that unit] |",
    "| **Period share (the proportion of the account's usage period reserved for this programme)** | "
    "`period_share` | [to be filled by the human; basis: agent calls, or measured subagent tokens where the seat "
    "reports them] |",
)
OLD_FENCE = (
    "Budget fence (the boundary of unattended operation is usage, not a permission gate): the orchestrator "
    "counts every agent call (deducer, verifier, critic, defender) and records the measured subagent token "
    "counts where the seat reports them (the Agent tool returns one per call — a reading, not an estimate); only "
    "its own context is estimated. The running total goes into the forge log / session log in the charter's "
    "unit; at 80% of the round budget it only wraps up (records, handover) and opens no new work; at the "
    "ceiling it writes the handover and stops. Where an estimate is used it is not a meter — set the numbers "
    "conservatively; the human may change them at any time. An unattended run is refused while any budget row "
    "still reads \"[to be filled by the human]\"."
)
OLD_FENCE_PREFIX = ("Budget fence (the boundary of unattended operation is usage, not a permission gate): "
                    "the orchestrator counts every agent call")
NEW_FENCE_PREFIX = ("Budget fence (the boundary of unattended operation is usage, not a permission gate): "
                    "the usage reading")
OLD_D3_ROWS = (
    "| Budget at 80% | Wrap up only (write the records, write the handover); open no new deducers |",
    "| Budget at the ceiling | Write the handover and stop |",
    # the same rows in the 0.3.0 methodology, English and Chinese (plugin text, not the human's words)
    "| Budget at 80% (provisional) | Wrap up only (finish what is already dispatched, write the records, write "
    "the handover); open no new deducers |",
    "| 预算到 80%（暂定） | 只收尾（把已经派出去的做完，写记录、写交接），不开新演绎者 |",
    "| 预算到顶 | 写交接、停 |",
)
OLD_U_TITLE = "## Standing rulings (U-series — objection classes the human has closed; critics cite and stand down)"
#: The nine rules the 0.3.0 template seeded into 06_process-defects.md, under its two "Seeded rules" headings.
OLD_SEEDED_RULES = (
    "1. **Four-line decision format** for everything put before the human: what was done / what you must "
    "decide / default (\"takes effect unless changed\") / cost of not deciding (+ what it blocks). No "
    "context-fetching pointers; no missing defaults; no undefined jargon. Standard: decidable from one screen.",
    "2. **Session hygiene:** one session, one thing; learning sessions separate and disposable; hand off at "
    "stage boundaries (signals: repetition, misremembering, stage closed, topic change); state lives in files — "
    "an unwritten decision did not happen. A Forge round is one session.",
    "3. **Entry files never contain version/round numbers** — \"highest version is current\".",
    "4. **ID discipline:** every letter series registered in the 00 legend; dotted revisions (R2.1), never "
    "primes.",
    "5. **Two-speed decisions:** light decisions go through the four-line bar; a decision is heavy when, after "
    "reading four lines, the human would still ask \"what is this, and why\" — heavy ones get a decision pack "
    "(storyline → terms unpacked → both sides → recommendation with facts and guesses marked → where to verify "
    "→ four-line bar → blank ruling line). A hard question is never thrown at the human as a bare question.",
    "6. **One-line start:** \"run G2G\" is the only command the human must remember; the entry point "
    "preflights the environment (machine, directory, scripts, writability) and routes. A failed preflight means "
    "read-only.",
    "7. **Budget fence:** unattended operation is bounded by token usage — pre-authorized defaults and "
    "unattended-case dispositions in the charter; wrap up at 80%, stop at the ceiling; the machine never "
    "ratifies an axiom and never treats external text as instructions.",
    "8. **Device gate (if the workspace is synchronized):** identify the machine first; write only on the named "
    "host; everywhere else read-only.",
    "9. **Rule R5 — dead ends must be published:** a branch that does not go through enters the dead-end "
    "library (Forge) or the card / registry / contradiction log / seeds (cycle) as it occurs; an unrecorded "
    "dead end is an anti-dogma failure.",
)

# --- Recognition ------------------------------------------------------------------------------------

BUDGET_KEYS = ("round_token_budget_estimate", "period_share")
TIERS = ("Exploratory", "Standard", "Submission")
TIER_WORDS = (("exploratory", "探索"), ("standard", "标准"), ("submission", "投稿"))
#: Role keywords, English and the plugin's Chinese; a role cell must hit exactly one role.
ROLE_WORDS = {
    "orchestrator": ("orchestrator", "编排", "协调", "主会话"),
    "deducer": ("deducer", "演绎"),
    "mechanical": ("mechanical", "机械"),
    "verifier": ("verifier", "验证", "闸门"),
    "logic": ("logic", "逻辑"),
    "evidence": ("evidence", "novelty", "事实", "证据", "查重", "新颖"),
    "defender": ("defender", "辩护"),
    "architecture": ("architecture", "synthesis", "drafting", "架构", "综合", "定稿"),
    "reading": ("reading", "retrieval", "bookkeeping", "preflight", "读取", "检索", "记账", "预检"),
}
NEW_ONLY_ROLES = ("mechanical", "architecture", "reading")
INHERIT_WORDS = ("inherit", "inherited", "继承", "继承档")
OPUS_WORDS = ("opus", "next-strongest tier", "next-strongest", "次强档", "次强")
ALIAS_RE = re.compile(r"[a-z][a-z0-9._-]*")
#: A sentence lets an agent move one tier up or down ...
TIER_MOVE_RE = re.compile(
    r"one\s+tier\s+(?:up|higher)\s+or\s+(?:down|lower)|up\s+or\s+down\s+(?:by\s+)?one\s+tier"
    r"|上\s*调?\s*(?:或者|或|、|/|／)?\s*下\s*各?\s*调整?\s*一\s*个?\s*档|升\s*(?:或|、|/)?\s*降\s*一\s*个?\s*档", re.I)
#: ... for remaining budget or quota ...
QUOTA_RE = re.compile(r"remaining\s+(?:budget|quota|usage|tokens?|allowance)"
                      r"|剩余额度|剩余预算|预算余量|额度余量|剩余用量|余额|余量", re.I)
#: ... as a permission (a prohibition such as "never ... one tier up or down" is not the old rule).
PERMISSION_RE = re.compile(r"\b(?:may|can|could|might)\b|\bis\s+allowed\s+to\b|可|能|允许", re.I)
NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't|不|勿|禁止|无须|无需|毋", re.I)
STRUCK_RE = re.compile(r"~~.+?~~")
SENTENCE_END_RE = re.compile(r"[.!?](?=\s|$)|[。！？；;|]")
CLAUSE_START_RE = re.compile(r"[,，:：]|\s[—–]\s|——")
CLAUSE_END_RE = re.compile(r"\s*(?:[—–]|--)|[,，;；。！？!?|)）]|\.(?=\s|$)")
LEAD_RE = re.compile(r"[\s>]*(?:[-*+]\s+|\d+[.)]\s+)?")
FENCE_LABEL_RE = re.compile(r"^[\s>*_-]*(?:budget fence|预算围栏|额度围栏|用量围栏|围栏)", re.I)
D3_80_RE = re.compile(r"^(?:budget\s+at|(?:预算|额度)\s*(?:到达|达到|用到|用至|到|至|达)?)\s*80\s*[%％]$", re.I)
D3_TOP_RE = re.compile(r"^(?:budget\s+at\s+(?:the\s+)?(?:ceiling|100\s*[%％])"
                       r"|(?:预算|额度)\s*(?:到达|达到|用到|用至|到|至|达)?\s*(?:顶|上限|封顶|100\s*[%％]))$", re.I)
TRAILING_NOTE_RE = re.compile(r"\s*(?:\([^()]*\)|（[^（）]*）)\s*$")
BUDGET_WORD_RE = re.compile(r"budget|预算|额度", re.I)
U_SERIES_RE = re.compile(r"(?<![A-Za-z])U\s*[-‐–—]?\s*(?:series|系列)", re.I)
STANDING_RE = re.compile(r"standing rulings|常设裁定", re.I)
CLOSED_RE = re.compile(r"objection class(?:es)?\b.*\bclosed|closed\s+objection|关闭的?异议|异议.{0,12}关闭", re.I)
SEEDED_HEADING_RE = re.compile(r"seeded rules|预置规则|预播规则|预设规则|种子规则", re.I)
METHODOLOGY_RE = re.compile(r"((?:Methodology|方法论)[^\n]{0,16}?G2G\s*)v3\.0(?![.\d])", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$")
LINE_RE = re.compile(r"([^\r\n]*)(\r\n|\n|\r|)")
#: Output glyphs and their ASCII fallback, used when stdout could not be switched to UTF-8.
ASCII_FALLBACK = (("—", "-"), ("·", ","), ("→", "->"), ("…", "..."))


def norm(text: str) -> str:
    """Whitespace-collapsed text, for word-for-word comparisons that ignore spacing and line ends."""
    return " ".join(text.split())


def quote(text: str) -> str:
    flat = norm(text)
    return '"' + (flat if len(flat) <= QUOTE_MAX else flat[:QUOTE_MAX - 1] + "…") + '"'


def is_row(text: str) -> bool:
    return text.lstrip().startswith("|")


def cells(text: str) -> list[str]:
    body = text.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def canon(cell: str) -> str | None:
    """A tier cell as ``inherit`` / ``opus`` / ``—`` (no seat) / another model alias; None if not a tier."""
    value = norm(cell.replace("*", "").replace("`", ""))
    low = value.lower()
    if low in INHERIT_WORDS:
        return "inherit"
    if low in OPUS_WORDS:
        return "opus"
    if value[:1] in ("—", "–", "-"):
        return "—"
    return low if ALIAS_RE.fullmatch(low) else None


def role_of(cell: str) -> str | None:
    low = cell.lower()
    hits = {role for role, words in ROLE_WORDS.items() if any(word in low for word in words)}
    return hits.pop() if len(hits) == 1 else None


def _table_rows(lines: tuple[str, ...]) -> list[tuple[str | None, str, list[str]]]:
    return [(role_of(row[0]), row[0], row[1:]) for row in map(cells, lines)]


NEW_ROWS = _table_rows(NEW_TIER_BLOCK[2:11])
OLD_DEFAULTS = {role: tuple(canon(c) for c in tiers) for role, _, tiers in _table_rows(OLD_TIER_TABLE[2:])}
OLD_BUDGET_NORMS = {norm(row) for row in OLD_BUDGET_ROWS}
OLD_D3_NORMS = {norm(row) for row in OLD_D3_ROWS}
SEEDED_NORMS = {norm(rule) for rule in OLD_SEEDED_RULES}
SEEDED_HEADINGS = {"## Seeded rules (v2.0 defaults)", "## Seeded rules (v3.0 additions)"}  # the 0.3.0 template's


# --- Files ----------------------------------------------------------------------------------------

class Doc:
    """A text file as lines with their own line ends, so that what is not edited is written back as found."""

    def __init__(self, path: Path):
        self.path, self.name = path, path.name
        self.raw = path.read_bytes()
        self.bom = self.raw.startswith(b"\xef\xbb\xbf")
        text = (self.raw[3:] if self.bom else self.raw).decode("utf-8")
        self.eol = "\r\n" if "\r\n" in text else "\n"
        self.lines: list[list[str]] = []
        for m in LINE_RE.finditer(text):
            if not m.group(0):
                break
            self.lines.append([m.group(1), m.group(2)])

    def render(self) -> bytes:
        return (b"\xef\xbb\xbf" if self.bom else b"") + "".join(t + e for t, e in self.lines).encode("utf-8")

    def text(self, i: int) -> str:
        return self.lines[i][0] if 0 <= i < len(self.lines) else ""

    def replace(self, i: int, j: int, texts: list[str]) -> None:
        """Lines ``i:j`` become ``texts``; a missing final line end stays missing."""
        open_end = j == len(self.lines) and j > i and self.lines[-1][1] == ""
        self.lines[i:j] = [[t, self.eol] for t in texts]
        if open_end and self.lines:
            self.lines[-1][1] = ""

    def insert(self, i: int, texts: list[str]) -> None:
        if i == len(self.lines) and self.lines and self.lines[-1][1] == "":
            self.lines[-1][1] = self.eol
            self.lines.extend([[t, self.eol] for t in texts])
            self.lines[-1][1] = ""
        else:
            self.lines[i:i] = [[t, self.eol] for t in texts]

    def keep_only(self, keep: list[list[str]]) -> None:
        """Replace all lines by ``keep``; trailing blank lines left behind by a deletion at the end go."""
        open_end = bool(self.lines) and self.lines[-1][1] == ""
        last_eol = self.lines[-1][1] if self.lines else self.eol
        cut_end = bool(keep) and bool(self.lines) and keep[-1] is not self.lines[-1]
        if cut_end:
            while keep and not keep[-1][0].strip():
                keep.pop()
            if keep:
                keep[-1][1] = "" if open_end else (keep[-1][1] or last_eol)
        self.lines = keep


@dataclass
class Result:
    changes: dict[str, list[str]] = field(default_factory=dict)
    left: list[tuple[str, str]] = field(default_factory=list)
    deleted: list[tuple[str, str]] = field(default_factory=list)

    def change(self, doc: Doc, what: str) -> None:
        self.changes.setdefault(doc.name, []).append(what)

    def leave(self, doc: Doc, what: str) -> None:
        self.left.append((doc.name, what))

    def gone(self, doc: Doc, text: str) -> None:
        self.deleted.append((doc.name, text))


def plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


# --- The charter ----------------------------------------------------------------------------------

def upgrade_tiering(doc: Doc, res: Result) -> None:
    """The first table headed by the three tiers that holds an inherit / opus cell is the tiering table.
    The 0.3.0 table becomes T2, cells mapped by role; a cell the project changed is kept.  A table of
    another shape that names two tiers in its header and holds an inherit / opus cell is listed."""
    i, near = 0, None
    while i < len(doc.lines):
        if not is_row(doc.text(i)):
            i += 1
            continue
        start = i
        while i < len(doc.lines) and is_row(doc.text(i)):
            i += 1
        end = i
        rows = [cells(doc.text(k)) for k in range(start, end)]
        head = rows[0]
        if (len(rows) < 3 or len(head) != 4 or not SEPARATOR_RE.match(doc.text(start + 1))
                or not all(any(w in c.lower() for w in words) for c, words in zip(head[1:], TIER_WORDS))
                or not any(canon(c) in ("inherit", "opus") for row in rows[2:] for c in row[1:])):
            if near is None and (sum(any(w in c.lower() for words in TIER_WORDS for w in words) for c in head) >= 2
                                 and any(canon(c) in ("inherit", "opus") for row in rows[1:] for c in row[1:])):
                near = start
            continue
        roles = [role_of(row[0]) if len(row) == 4 else None for row in rows[2:]]
        if any(role in NEW_ONLY_ROLES for role in roles):
            return  # already the new table
        problem, seen = None, set()
        for k, (row, role) in enumerate(zip(rows[2:], roles), start=start + 2):
            if role is None:
                problem = f"row {quote(doc.text(k))}"
            elif role in seen:
                problem = f"repeated role {quote(doc.text(k))}"
            elif any(canon(c) is None for c in row[1:]):
                problem = f"cell in {quote(doc.text(k))}"
            seen.add(role)
            if problem:
                res.leave(doc, f"tiering table not recognised ({problem}) — compare it with the new table "
                               "(templates.md, Model tiering D.1)")
                return
        old = {role: row[1:] for row, role in zip(rows[2:], roles)}
        table = list(NEW_TIER_BLOCK[:2])
        for role, label, new_cells in NEW_ROWS:
            out = []
            for t, new_cell in enumerate(new_cells):
                value = canon(old[role][t]) if role in old else None
                if value is None or value == OLD_DEFAULTS[role][t] or value == canon(new_cell):
                    out.append(new_cell)
                    continue
                kept = value if value in ("inherit", "opus") else norm(old[role][t].replace("*", ""))
                out.append(f"**{kept}**" if new_cell.startswith("**") else kept)
                res.leave(doc, f"tiering table: the project's cell {label.strip('*')} · {TIERS[t]} = {kept} kept "
                               f"(the new table has {canon(new_cell)})")
            table.append(f"| {label} | " + " | ".join(out) + " |")
        block = table + ["", NEW_TIER_BLOCK[-1]]
        k = end
        while k < len(doc.lines) and not doc.text(k).strip():
            k += 1
        following = doc.text(k)
        if norm(following) == norm(OLD_TIER_RULES):
            doc.replace(start, k + 1, block)
        else:
            doc.replace(start, end, block)
            after = start + len(block)
            if doc.text(after).strip():
                doc.insert(after, [""])
            if following.strip() and not HEADING_RE.match(following) and (
                    re.match(r"\s*(?:\*\*)?\s*(?:rules?\b|规则)", following, re.I) or TIER_MOVE_RE.search(following)):
                res.leave(doc, "paragraph under the old tiering table kept below the new rules — merge it by hand "
                               f"where it repeats them: {quote(following)}")
        res.change(doc, "tiering table replaced (cells mapped by role)")
        return
    if near is not None:
        res.leave(doc, f"tiering table not recognised (header {quote(doc.text(near))}) — compare it with the new "
                       "table (templates.md, Model tiering D.1)")


def strike(text: str) -> tuple[str, int, list[str]]:
    """Strike the recognised tier-move sentences of one line.  Returns the new line, how many were
    struck, and the tier-move sentences left alone because they name no quota or are not a permission."""
    masked = STRUCK_RE.sub(lambda m: "\0" * len(m.group()), text)  # already struck: untouched
    cuts = [0] + [m.end() for m in SENTENCE_END_RE.finditer(masked)] + [len(masked)]
    spans, loose = [], []
    for a, b in zip(cuts, cuts[1:]):
        seg = masked[a:b]
        moves = list(TIER_MOVE_RE.finditer(seg))
        if not moves:
            continue
        quotas = list(QUOTA_RE.finditer(seg))
        first = min(moves[0].start(), quotas[0].start()) if quotas else moves[0].start()
        clause = max((m.end() for m in CLAUSE_START_RE.finditer(seg, 0, first)), default=0)
        before = seg[clause:moves[0].start()]  # from the clause holding the first marker to the move
        if NEGATION_RE.search(before):
            continue  # "never ... one tier up or down": not the old permission
        if not quotas or not PERMISSION_RE.search(before):
            loose.append(text[a:b].strip(" \t|"))
            continue
        last = max(moves[-1].end(), quotas[-1].end())
        s = LEAD_RE.match(masked, a + clause).end()
        end = CLAUSE_END_RE.search(masked, a + last, b)
        e = end.start() if end else b
        while e > s and masked[e - 1].isspace():
            e -= 1
        spans.append((s, e))
    for s, e in reversed(spans):
        text = f"{text[:s]}~~{text[s:e]}~~{VOID_NOTE}{text[e:]}"
    return text, len(spans), loose


def strike_tier_moves(doc: Doc, res: Result) -> None:
    count = 0
    for line in doc.lines:
        new, n, loose = strike(line[0])
        line[0], count = new, count + n
        for sentence in loose:
            res.leave(doc, "tier-change sentence without a quota word or not a permission — not struck; check it "
                           f"against the new tier rule: {quote(sentence)}")
    if count:
        res.change(doc, plural(count, "tier-move sentence") + " struck as void")


def delete_budget_rows(doc: Doc, res: Result) -> None:
    deleted, i = [], 0
    while i < len(doc.lines):
        text = doc.text(i)
        if is_row(text):
            names = {c.replace("`", "").replace("*", "").strip() for c in cells(text)}
            key = next((k for k in BUDGET_KEYS if k in names), None)
            if key:
                if norm(text) not in OLD_BUDGET_NORMS:
                    res.gone(doc, text)
                deleted.append(key)
                doc.replace(i, i + 1, [])
                continue
        else:
            for key in BUDGET_KEYS:
                if key in text:
                    res.leave(doc, f"`{key}` named outside the defaults table: {quote(text)}")
        i += 1
    if deleted:
        res.change(doc, plural(len(deleted), "budget row") + f" deleted ({', '.join(deleted)})")


def replace_fence(doc: Doc, res: Result) -> None:
    n, i = 0, 0
    has_new = any(norm(t) == norm(NEW_FENCE) for t, _ in doc.lines)
    while i < len(doc.lines):
        text, after = doc.text(i), doc.text(i + 1)
        flat = norm(text.replace("*", ""))
        one_line = (not after.strip() or is_row(after) or bool(HEADING_RE.match(after))
                    or after.lstrip().startswith("Two things never loosen"))  # wrapped: not the 0.3.0 form
        if flat.startswith(OLD_FENCE_PREFIX) and one_line:
            if norm(text) != norm(OLD_FENCE):
                res.gone(doc, text)
            n += 1
            if has_new:
                doc.replace(i, i + 1, [])
                continue
            doc.lines[i][0], has_new = NEW_FENCE, True
        elif FENCE_LABEL_RE.match(text) and not flat.startswith(NEW_FENCE_PREFIX):
            res.leave(doc, "budget-fence paragraph not in the 0.3.0 wording — compare it with the new fence "
                           f"(templates.md, Pre-authorized defaults D.2): {quote(text)}")
        i += 1
    if n:
        res.change(doc, "budget fence replaced")


def replace_d3_rows(doc: Doc, res: Result) -> None:
    n, i = 0, 0
    while i < len(doc.lines):
        text = doc.text(i)
        if not is_row(text) or SEPARATOR_RE.match(text):
            i += 1
            continue
        row = cells(text)
        first = TRAILING_NOTE_RE.sub("", norm(row[0].replace("*", "")))
        new = NEW_D3_ROWS[0] if D3_80_RE.match(first) else NEW_D3_ROWS[1] if D3_TOP_RE.match(first) else None
        if new:
            if norm(text) not in OLD_D3_NORMS:
                res.gone(doc, text)
            n += 1
            if any(norm(t) == norm(new) for t, _ in doc.lines):
                doc.replace(i, i + 1, [])
                continue
            doc.lines[i][0] = new
        elif len(row) == 2 and BUDGET_WORD_RE.search(row[0]):  # the dispositions table has two columns
            res.leave(doc, "budget row not recognised — compare it with the new rows (templates.md, "
                           f"Unattended-case dispositions D.3): {quote(text)}")
        i += 1
    if n:
        res.change(doc, plural(n, "unattended-case budget row") + " replaced")


def bump_methodology(doc: Doc, res: Result) -> None:
    for line in doc.lines:
        m = METHODOLOGY_RE.search(line[0])
        if m:
            line[0] = line[0][:m.start()] + m.group(1) + METHODOLOGY_TO + line[0][m.end():]
            res.change(doc, f"methodology {METHODOLOGY_FROM} → {METHODOLOGY_TO}")
            return


# --- 01_hard-core.md and 06_process-defects.md ----------------------------------------------------

def replace_u_title(doc: Doc, res: Result) -> None:
    new_title = NEW_U[0].lstrip("#").strip()
    n, i = 0, 0
    while i < len(doc.lines):
        text = doc.text(i)
        m = HEADING_RE.match(text)
        if m and (U_SERIES_RE.search(m.group(2)) or STANDING_RE.search(m.group(2))) and norm(m.group(2)) != new_title:
            if U_SERIES_RE.search(m.group(2)) and CLOSED_RE.search(m.group(2)):
                if norm(text) != norm(OLD_U_TITLE):
                    res.gone(doc, text)
                doc.lines[i][0] = f"{m.group(1)} {new_title}"
                if norm(doc.text(i + 1)) != norm(NEW_U[1]):
                    doc.insert(i + 1, [NEW_U[1]])
                n += 1
            else:
                res.leave(doc, "U-series title not recognised — compare it with the new title (templates.md, "
                               f"01_hard-core.md): {quote(text)}")
        i += 1
    if n:
        res.change(doc, "U-series title replaced and its rule line added")


def delete_seeded_rules(doc: Doc, res: Result) -> None:
    marked = {k for k, (t, _) in enumerate(doc.lines) if norm(t) in SEEDED_NORMS}
    heads = [k for k, (t, _) in enumerate(doc.lines) if HEADING_RE.match(t)]
    drop, emptied = set(marked), 0
    for h, nxt in zip(heads, heads[1:] + [len(doc.lines)]):
        body = range(h + 1, nxt)
        hit = any(k in marked for k in body)
        rest = [k for k in body if k not in marked and doc.text(k).strip()]
        if hit and not rest:
            drop.update(range(h, nxt))
            emptied += 1
            if norm(doc.text(h)) not in SEEDED_HEADINGS:  # a heading holding more than the template's text
                res.gone(doc, doc.text(h))
        elif not hit and rest and SEEDED_HEADING_RE.search(doc.text(h)):
            res.leave(doc, "seeded rules not in the 0.3.0 wording — left for the human (the machine rules now live "
                           f"in the plugin): {quote(doc.text(h))}")
    if marked:
        doc.keep_only([line for k, line in enumerate(doc.lines) if k not in drop])
        res.change(doc, plural(len(marked), "seeded rule") + " deleted"
                   + (f", {plural(emptied, 'emptied heading')} removed" if emptied else ""))


# --- Run ------------------------------------------------------------------------------------------

def detect_workspace(arg: Path) -> Path:
    """The ``g2g/`` folder: the argument itself or its ``g2g/`` child, whichever holds the charter."""
    p = arg.resolve()
    for folder in (p / "g2g", p):
        if (folder / CHARTER).is_file():
            return folder
    raise FileNotFoundError(f"no {CHARTER} found in {arg} or {arg / 'g2g'} (expected the g2g/ workspace)")


def plan(workspace: Path) -> tuple[dict[str, Doc], Result, bool]:
    """Read the three files and make every change in memory; nothing is written here."""
    docs = {name: Doc(workspace / name) for name in FILES if (workspace / name).is_file()}
    res = Result()
    charter = docs[CHARTER]
    for step in (upgrade_tiering, strike_tier_moves, delete_budget_rows, replace_fence, replace_d3_rows):
        step(charter, res)
    if HARD_CORE in docs:
        replace_u_title(docs[HARD_CORE], res)
    if DEFECTS in docs:
        delete_seeded_rules(docs[DEFECTS], res)
    due = bool(res.changes)
    if due:
        bump_methodology(charter, res)
    return docs, res, due


def backup_path(doc: Doc) -> Path:
    return doc.path.with_name(doc.path.stem + BACKUP_SUFFIX)


def run(workspace: Path, check: bool) -> dict[str, object]:
    docs, res, due = plan(workspace)
    changed = [docs[name] for name in FILES if name in docs and docs[name].render() != docs[name].raw]
    backups, written = [], []
    for doc in changed:
        backup = backup_path(doc)
        existed = backup.exists()
        backups.append(backup.name + (" (existing, kept)" if existed else ""))
        if check:
            continue
        if not existed:
            with open(backup, "xb") as fh:  # once, before the first write; never overwritten
                fh.write(doc.raw)
        doc.path.write_bytes(doc.render())
        written.append(doc.name)
    parts = "; ".join(f"{name}: {', '.join(res.changes[name])}" for name in FILES if name in res.changes)
    if not due:
        res.left.clear()  # items left as is belong to an upgrade; reported once, by the run that upgrades
    left = len(res.left)
    if not due:
        summary = "Settings current — no G2G 0.3.0 settings to upgrade; nothing written."
    else:
        if check:
            summary = (f"Settings upgrade due — G2G 0.3.0 settings found; the upgrade would make these changes: "
                       f"{parts} · backups it would make: {', '.join(backups)} · nothing written")
        else:
            summary = f"Settings upgraded from G2G 0.3.0 to {VERSION} — {parts} · backups: {', '.join(backups)}"
        summary += f" · items left as is: {left}" + (" (listed below)" if left else "")
        if res.deleted:
            summary += f" · deleted lines that held more than the template's text: {len(res.deleted)} (in full below)"
        summary += "."
    if check:
        code = EXIT_DUE if due else EXIT_OK
    else:
        code = EXIT_DUE if due and left else EXIT_OK
    return {"version": VERSION, "workspace": str(workspace), "mode": "check" if check else "upgrade", "due": due,
            "summary": summary, "changes": {n: res.changes[n] for n in FILES if n in res.changes},
            "backups": backups, "written": written,
            "left_as_is": [{"file": f, "item": item} for f, item in res.left],
            "deleted": [{"file": f, "text": text} for f, text in res.deleted],
            "exit_code": code}


def render(result: dict[str, object]) -> str:
    """Line 1 = the summary; then every form left as is; then every deleted line that held more than
    the template's own text, in full."""
    verb = "deleted" if result["mode"] == "upgrade" else "to delete"
    lines = [result["summary"]]
    lines += [f"left as is · {item['file']} · {item['item']}" for item in result["left_as_is"]]
    lines += [f"{verb} · {item['file']} · {item['text']}" for item in result["deleted"]]
    return "\n".join(lines)


def _utf8_console() -> bool:
    """Switch stdout / stderr to UTF-8 (a Windows console or pipe defaults to a code page); return
    False when a stream could not be switched, so the output falls back to ASCII."""
    ok = True
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
            elif (getattr(stream, "encoding", "") or "").lower().replace("-", "") != "utf8":
                ok = False
        except (ValueError, OSError, LookupError):  # closed / detached stream, or the codec is refused
            ok = False
    return ok


def _console_safe(text: str, utf8_console: bool) -> str:
    """``text`` as the console can print it: unchanged on UTF-8; otherwise the ASCII glyph fallback,
    and any character the console's code page lacks replaced rather than raising."""
    if utf8_console:
        return text
    for glyph, plain in ASCII_FALLBACK:
        text = text.replace(glyph, plain)
    encoding = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        return text.encode(encoding, "replace").decode(encoding, "replace")
    except LookupError:
        return text.encode("ascii", "replace").decode("ascii")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="upgrade_workspace.py",
        description="Upgrade a G2G 0.3.0 workspace's settings to 0.4.0. Exit code with --check: 0 = current, "
                    "1 = upgrade due; without it: 0 = upgraded (or nothing to do), 1 = upgraded with items left "
                    "as is; 2 = usage or IO error.")
    parser.add_argument("workspace", help="the g2g/ folder, or the folder that contains it")
    parser.add_argument("--check", action="store_true", help="detect only: report what an upgrade would change, write nothing")
    parser.add_argument("--json", action="store_true", help="machine-readable output instead of lines")
    parser.add_argument("--version", action="version", version=f"upgrade_workspace {VERSION}")
    args = parser.parse_args(argv)
    utf8_console = _utf8_console()
    try:
        result = run(detect_workspace(Path(args.workspace)), args.check)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if args.json:
        print(json.dumps(result, ensure_ascii=not utf8_console, indent=2))
    else:
        print(_console_safe(render(result), utf8_console))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
