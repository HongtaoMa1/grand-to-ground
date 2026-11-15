#!/usr/bin/env python3
"""pg_check.py - proposition-graph check script for the Grand-to-Ground (G2G) Theory Forge.

Implements the "authority by construction" check list of docs/METHODOLOGY.md 3b.5 over a
programme workspace (``g2g/07_theory/``): the graph is acyclic; no dangling predecessors;
no ``proposed`` node in the formal directory; every ``verified`` node has a passing
verification record; every ``verified`` node's newly introduced symbols (``glossary_introduces``)
are registered; revocations and supersessions have cascaded;
bare IDs P-xxxx resolve to the current revision; no ``verified`` node cites a pending
axiom or base definition; ``conditional_on`` is inherited; the closure test for theorems;
neither ``[SIG]`` nor a non-empty ``conditional_on`` in the support closure of a node tagged
``faithful``; the one gate-exempt revision (the mechanical ``conditional on CJ-xx`` ->
``by A-xx`` swap of 3b.8) changed nothing else; the overview table is regenerated
(``--regen-index``) and each node's ``content_sha`` is filled (``--fill-sha``).
``--report`` adds informational findings (never counted), among them ``DANGLING_FIELD`` for a
``revision_of`` / ``supersedes`` that names no node.  ``--pregate P-ID ...`` runs only the
pre-gate registration check on the named candidates, before each verifier dispatch: a
``glossary_introduces`` entry that reuses a glossary name, a term defined with ``:=`` or in bold
that is not listed, an unlisted dual / strict part / inverse of an introduced order symbol.

Pure standard library, Python >= 3.10, UTF-8 file IO.  Usage::

    python scripts/pg_check.py <programme_root> [--report] [--regen-index] [--fill-sha] [--json]
    python scripts/pg_check.py <programme_root> --pregate P-ID [P-ID ...] [--json]
    python "${CLAUDE_PLUGIN_ROOT}/scripts/pg_check.py" g2g --report   # the form the skills use; cwd = the project root

``<programme_root>`` may be the folder that contains ``g2g/``, the ``g2g/`` folder itself,
or the ``07_theory/`` folder.  Exit code = number of violations (0 = clean), capped at 255
(with ``--pregate``: the number of findings for the named candidates); 2 on a usage or IO
error.  Without ``--regen-index`` / ``--fill-sha`` no file is modified; nothing is ever deleted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.4.0"
THEORY_DIRNAME = "07_theory"
NODE_DIRS = ("candidates", "propositions")
REQUIRED_FIELDS = ("id", "kind", "status", "predecessors")
STATUSES = ("proposed", "verified", "revoked", "superseded")
DEAD_STATUSES = ("revoked", "superseded")
EXIT_CAP = 255
EXIT_USAGE = 2
CADENCE_DEFAULTS = {"K": 10, "M": 4, "T": 25}
INDEX_COLUMNS = ("ID", "one-liner", "kind", "status", "empirical_status",
                 "predecessors", "A/D/DA used", "verification", "layer")
#: Violation codes (counted in the exit code), in the order the checks run.
CODES = ("BAD_FRONTMATTER", "ID_FORMAT", "DANGLING", "CYCLE", "PROPOSED_IN_PROPOSITIONS",
         "VERIFIED_IN_CANDIDATES", "VERIFIED_NO_PASS", "UNVERIFIED_PREDECESSOR",
         "REVOKE_NOT_CASCADED", "PENDING_AXIOM_CITED", "UNREGISTERED_SYMBOL",
         "CONDITIONAL_NOT_INHERITED", "CONDITIONAL_WITHOUT_GUESS", "FAITHFUL_WITH_SIG",
         "FAITHFUL_WITH_CONDITION", "EXEMPT_REVISION_CHANGED", "MISSING_SHA", "STALE_SHA")
#: Informational codes (``--report`` only, never counted).
INFO_CODES = ("CLOSURE_NOT_CLOSED", "SCOPE_MISMATCH", "DUPLICATE_SHA", "DANGLING_FIELD")
#: Pre-gate codes (``--pregate`` only, on the named candidates).  Never part of the default run,
#: where candidates stay exempt at round start.
PREGATE_CODES = ("SYMBOL_COLLISION", "UNLISTED_DEFINITION", "UNLISTED_ORDER_DERIVATIVE")

NODE_ID_RE = re.compile(r"^P-\d{4}(?:\.\d+)?$")
NODE_REF_RE = re.compile(r"P-\d{4}(?:\.\d+)?")
AXIOM_REF_RE = re.compile(r"[AD]-\d{2,}")
CJ_REF_RE = re.compile(r"CJ-\d{2,}")
VREC_REF_RE = re.compile(r"V-\d{4,}")
SHA_RE = re.compile(r"^[0-9a-f]{12}$")
#: The one gate-exempt revision (3b.8 / 3b.9): the premise it may replace, and the axiom it may
#: replace it with.  Anything else in the Statement or the Derivation opens a verifier.
EXEMPT_PREMISE_RE = re.compile(r"([Cc])onditional on (CJ-\d{2,})\s*\(\[GUESS\]\)")
EXEMPT_AXIOM_RE = re.compile(r"\bA-\d{2,}\b")
FM_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*)\s*:\s?(.*)$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
AXIOM_ENTRY_RE = re.compile(r"^\s*(?:[|\-*#>+]+\s*)*[`*_]*([AD]-\d{2,})\b")
CJ_ENTRY_RE = re.compile(r"^\s*(?:[|\-*#>+]+\s*)*[`*_]*(CJ-\d{2,})\b")
AXIOM_STATUS_RE = re.compile(
    r"(?P<ratified>ratified|已批准|已批)|(?P<pending>pending|待批准|待批)"
    r"|(?P<revoked>revoked|withdrawn|已撤销|撤销)", re.I)
CJ_STATUS_RE = re.compile(
    r"(?P<open>\bopen\b|开放)|(?P<promoted>promoted|已证)|(?P<ratified>ratified|已批)"
    r"|(?P<dropped>dropped|放弃|撤销)", re.I)
STATUS_KEY_RE = re.compile(r"status|状态", re.I)
#: Forge-log entry title, the only place a round number is read from (never prose).
FORGE_ROUND_RE = re.compile(r"^##\s*Round\s+(\d+)", re.I | re.M)
#: Pre-gate, inside Statement and Derivation only: a term defined with ``:=`` (or ``≔``) is the
#: token left of it; a term defined in bold is the ``**…**`` span.  No other symbol scan.
DEFINE_RE = re.compile(r"(\S+)\s*(?::=|≔)")
BOLD_RE = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
#: Order symbols for the pre-gate's dual / strict-part / inverse rule: each string is one family
#: (non-strict, inverse, strict part, strict inverse); a glyph's variants are the rest of its families.
ORDER_FAMILIES = ("≤≥<>", "≼≽≺≻", "⪯⪰≺≻", "⊑⊒⊏⊐", "⊆⊇⊂⊃⊊⊋")
ORDER_VARIANTS = {g: "".join(sorted(set("".join(f for f in ORDER_FAMILIES if g in f)) - {g}))
                  for g in "".join(ORDER_FAMILIES)}
#: Reason category of a revocation (``revoked_by: <category> · <reason> · <date>``) and of a
#: revision (``revision_of: P-xxxx · <category>``); none written = uncategorised.
REASON_CATEGORIES = ("gate-miss", "cascade", "human-ruling", "mechanical")
REASON_RE = re.compile(r"[\s\[(`*·:,—–-]*(" + "|".join(REASON_CATEGORIES) + r")(?![\w-])", re.I)  # at the start
UNCATEGORISED = "uncategorised"
#: Report glyphs and their ASCII fallback, used when stdout could not be switched to UTF-8.
ASCII_FALLBACK = (("→", "->"), ("—", "-"), ("·", ","))


# --------------------------------------------------------------------------- data model
@dataclass
class Violation:
    """One check failure; ``file`` is relative to the programme root (posix form)."""
    code: str
    file: str
    message: str

    def line(self) -> str:
        return f"{self.code}  {self.file}  {self.message}"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "file": self.file, "message": self.message}


@dataclass
class Node:
    """A proposition node (candidate or formal) parsed from ``P-xxxx.md``."""
    id: str
    path: Path
    rel: str
    dirname: str
    fm: dict[str, object]
    sections: dict[str, str]
    missing_fields: list[str]
    title: str = ""
    kind: str = ""
    status: str = ""
    empirical_status: str = ""
    layer: str = ""
    scope: str = ""
    predecessors: list[str] = field(default_factory=list)
    axioms_used: list[str] = field(default_factory=list)
    definitions_used: list[str] = field(default_factory=list)
    assumptions_used: list[str] = field(default_factory=list)
    conditional_on: list[str] = field(default_factory=list)
    glossary_introduces: list[str] = field(default_factory=list)
    operationalization: str = ""
    markers: set[str] = field(default_factory=set)
    verification_raw: str = ""
    verification_id: str = ""
    revision_of: str = ""
    revision_category: str = ""
    supersedes: str = ""
    revoked_category: str = ""
    content_sha: str = ""
    resolved: dict[str, "Node | None"] = field(default_factory=dict)

    @property
    def base(self) -> str:
        """Family ID without the revision suffix (P-0007.1 -> P-0007)."""
        return self.id.split(".")[0]

    @property
    def rev(self) -> int:
        return int(self.id.split(".")[1]) if "." in self.id and self.id.split(".")[1].isdigit() else 0

    @property
    def live(self) -> bool:
        return self.status not in DEAD_STATUSES


@dataclass
class VRecord:
    """A verification record ``V-xxxx.md`` (only id, candidate and verdict are used)."""
    id: str
    rel: str
    candidate: str
    verdict: str


@dataclass
class Programme:
    """Everything the checks need, loaded once from ``07_theory/``."""
    root: Path
    theory: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    families: dict[str, list[Node]] = field(default_factory=dict)
    edges: dict[str, list[str]] = field(default_factory=dict)
    vrecords: list[VRecord] = field(default_factory=list)
    axioms: dict[str, str] = field(default_factory=dict)
    conjectures: dict[str, str] = field(default_factory=dict)
    glossary: set[str] = field(default_factory=set)
    glossary_origin: dict[str, list[str]] = field(default_factory=dict)
    forge_log: str | None = None
    load_violations: list[Violation] = field(default_factory=list)


# --------------------------------------------------------------------------- parsing
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def read_optional(path: Path) -> str:
    return read_text(path) if path.is_file() else ""


def relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _strip_comment(raw: str) -> str:
    """Cut a trailing ``# comment`` (outside brackets / backticks, preceded by whitespace)."""
    depth, tick = 0, False
    for i, ch in enumerate(raw):
        if ch == "`":
            tick = not tick
        elif ch in "[(":
            depth += 1
        elif ch in "])":
            depth = max(0, depth - 1)
        elif ch == "#" and not tick and depth == 0 and (i == 0 or raw[i - 1].isspace()):
            return raw[:i]
    return raw


def _clean(item: str) -> str:
    return item.strip().strip("\"'").strip()


def _split_list(inner: str) -> list[str]:
    """Split ``a, [b], c(d, e)`` at top-level commas (a full-width ``（…）`` note is one level too)."""
    items, buf, depth = [], [], 0
    for ch in inner:
        if ch in "[(（":
            depth += 1
        elif ch in "])）":
            depth -= 1
        if ch == "," and depth <= 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return [_clean(x) for x in items if _clean(x)]


def parse_value(raw: str) -> str | list[str]:
    value = _strip_comment(raw).strip()
    if value.startswith("[") and value.endswith("]"):
        return _split_list(value[1:-1])
    return value.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict[str, object] | None, str]:
    """Parse a ``---`` delimited ``key: value`` block; return (fields, body) or (None, text)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    fm: dict[str, object] = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return fm, "\n".join(lines[i + 1:])
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = FM_KEY_RE.match(line)
        if m:
            fm[m.group(1)] = parse_value(m.group(2))
    return None, text


def split_sections(body: str) -> dict[str, str]:
    """Map lower-cased ``## Heading`` names to their text (``###`` stays inside its section)."""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        m = SECTION_RE.match(line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = m.group(1).strip().lower(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def digest_text(sections: dict[str, str]) -> str:
    """The Statement + Derivation texts with line endings and trailing whitespace normalised —
    what the content digest is taken over, and what the gate-exempt revision test compares."""
    parts = []
    for name in ("statement", "derivation"):
        text = sections.get(name, "")
        parts.append("\n".join(l.rstrip() for l in text.strip().splitlines()))
    return "\n".join(parts)


def compute_sha(sections: dict[str, str]) -> str:
    """First 12 hex of sha256 over the Statement + Derivation texts (line endings and
    trailing whitespace normalised, so the digest is platform-independent)."""
    return hashlib.sha256(digest_text(sections).encode("utf-8")).hexdigest()[:12]


def swap_premise(text: str, cj: str, axiom: str) -> tuple[str, int]:
    """Apply the licensed substitution ``conditional on CJ-xx ([GUESS])`` -> ``by A-xx`` (3b.9)
    to ``text``, keeping a sentence-initial capital; returns the new text and the match count."""
    pattern = re.compile(r"([Cc])onditional on " + re.escape(cj) + r"\s*\(\[GUESS\]\)")
    return pattern.subn(lambda m: ("By " if m.group(1) == "C" else "by ") + axiom, text)


def _as_str(fm: dict[str, object], key: str) -> str:
    value = fm.get(key, "")
    return ", ".join(value) if isinstance(value, list) else str(value).strip()


def _as_list(fm: dict[str, object], key: str) -> list[str]:
    value = fm.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if text.lower() in ("", "none", "-", "[]", "null", "~"):
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


def _ref(item: str, pattern: re.Pattern[str]) -> str:
    """Normalise a reference such as ``P-0003 (statement only)`` to its bare ID."""
    m = pattern.search(item)
    return m.group(0) if m else item.strip()


def _strip_note(sym: str) -> str:
    """Drop one trailing parenthetical note: a full-width ``（…）`` always, an ASCII ``(…)`` only
    when whitespace precedes it - so ``𝒫（…）`` and ``𝒫 (…)`` give ``𝒫`` while ``f(x)`` stays."""
    for opener, closer, spaced in (("（", "）", False), ("(", ")", True)):
        if not sym.endswith(closer):
            continue
        depth = 0
        for i in range(len(sym) - 1, -1, -1):
            if sym[i] == closer:
                depth += 1
            elif sym[i] == opener:
                depth -= 1
                if depth == 0:
                    head = sym[:i]
                    if head.strip() and (not spaced or head[-1].isspace()):
                        return head.rstrip()
                    break
    return sym


def norm_symbol(sym: str) -> str:
    """The bare symbol: ``\\|`` read as a literal ``|``; backticks, ``$``, ``*``, a trailing colon
    and one trailing parenthetical note (``_strip_note``) dropped."""
    s = sym.replace("\\|", "|")
    while True:
        bare = _strip_note(s.strip().strip("`$*").strip().rstrip(":").strip())
        if bare == s:
            return bare
        s = bare


def _category(text: str) -> str:
    """The reason category at the start of a ``revoked_by`` value or right after the ID of ``revision_of``."""
    m = REASON_RE.match(text)
    return m.group(1).lower() if m else ""


def make_node(path: Path, rel: str, dirname: str, fm: dict[str, object], body: str) -> Node:
    missing = [k for k in REQUIRED_FIELDS
               if k not in fm or (k != "predecessors" and not _as_str(fm, k))]
    node = Node(id=_as_str(fm, "id") or path.stem, path=path, rel=rel, dirname=dirname, fm=fm,
                sections=split_sections(body), missing_fields=missing)
    node.title = _as_str(fm, "title")
    node.kind = _as_str(fm, "kind").lower()
    node.status = _as_str(fm, "status").lower()
    node.empirical_status = _as_str(fm, "empirical_status").lower()
    node.layer = _as_str(fm, "layer")
    node.scope = _as_str(fm, "scope")
    node.predecessors = [_ref(x, NODE_REF_RE) for x in _as_list(fm, "predecessors")]
    node.axioms_used = [_ref(x, AXIOM_REF_RE) for x in _as_list(fm, "axioms_used")]
    node.definitions_used = [_ref(x, AXIOM_REF_RE) for x in _as_list(fm, "definitions_used")]
    node.assumptions_used = _as_list(fm, "assumptions_used")
    node.conditional_on = [_ref(x, CJ_REF_RE) for x in _as_list(fm, "conditional_on")]
    node.glossary_introduces = [norm_symbol(x) for x in _as_list(fm, "glossary_introduces")]
    node.operationalization = _as_str(fm, "operationalization").lower()
    node.markers = {m.strip("[] ").upper() for m in _as_list(fm, "markers")}
    node.verification_raw = _as_str(fm, "verification")
    vm = VREC_REF_RE.search(node.verification_raw)
    node.verification_id = vm.group(0) if vm else ""
    revision = _as_str(fm, "revision_of")
    rm = NODE_REF_RE.search(revision)
    node.revision_of = rm.group(0) if rm else ""
    node.revision_category = _category(revision[rm.end():]) if rm else ""
    sm = NODE_REF_RE.search(_as_str(fm, "supersedes"))
    node.supersedes = sm.group(0) if sm else ""
    node.revoked_category = _category(_as_str(fm, "revoked_by"))
    node.content_sha = _as_str(fm, "content_sha").lower()
    if not node.title:
        first = node.sections.get("statement", "").strip().splitlines()
        node.title = first[0][:120] if first else ""
    return node


def _status_after(text: str, status_re: re.Pattern[str]) -> str | None:
    """First status word after ``status`` (if that key appears) or after the entry ID."""
    k = STATUS_KEY_RE.search(text)
    m = status_re.search(text[k.end():] if k else text)
    return m.lastgroup if m else None


def parse_registry(text: str, entry_re: re.Pattern[str], status_re: re.Pattern[str]) -> dict[str, str]:
    """``{id: status}`` from a loose Markdown list or table (axioms.md / conjectures.md):
    an entry is a line that starts (after bullets, pipes, hashes, bold) with the ID; its status
    is the first status word after ``status:`` or after the ID, else looked up in the next
    lines that mention ``status``; the first definition of an ID wins."""
    lines = text.splitlines()
    out: dict[str, str] = {}
    for i, line in enumerate(lines):
        m = entry_re.match(line)
        if not m:
            continue
        status = _status_after(line[m.end():], status_re)
        if status is None:
            for follow in lines[i + 1:i + 9]:
                if entry_re.match(follow) or follow.startswith("#"):
                    break
                if STATUS_KEY_RE.search(follow):
                    status = _status_after(follow, status_re)
                    if status:
                        break
        out.setdefault(m.group(1), status or "unknown")
    return out


def _cells(row: str) -> list[str]:
    """The cells of a Markdown table row, split on unescaped ``|`` only (``\\|`` is a literal pipe)."""
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def _is_sep_row(line: str) -> bool:
    cells = _cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def glossary_entries(text: str) -> list[tuple[str, str]]:
    """``(symbol, introduced by)`` per glossary entry: the first column of any table (header row
    skipped; "introduced by" is the column whose header says so, else the fourth) or a
    ``- symbol · …`` bullet (introduced by = the first P- ID after the symbol, if any)."""
    lines = text.splitlines()
    entries: list[tuple[str, str]] = []
    origin_col: int | None = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("|"):
            if _is_sep_row(s):
                continue
            cells = _cells(s)
            if i + 1 < len(lines) and _is_sep_row(lines[i + 1]):
                origin_col = next((k for k, c in enumerate(cells) if re.search(r"introduced|引入", c, re.I)),
                                  3 if len(cells) > 3 else None)
                continue
            origin = cells[origin_col] if origin_col is not None and origin_col < len(cells) else ""
            entries.append((norm_symbol(cells[0]), origin))
        elif s[:2] in ("- ", "* ", "+ "):
            parts = re.split(r"\s+[·—–:|]\s*|:\s|\t|\s{2,}", s[2:].strip(), maxsplit=1)
            ref = NODE_REF_RE.search(parts[1]) if len(parts) > 1 else None
            entries.append((norm_symbol(parts[0]), ref.group(0) if ref else ""))
    return [(sym, origin) for sym, origin in entries if sym]


def parse_glossary(text: str) -> set[str]:
    """Registered symbols: first column of any table (header row skipped) or ``- symbol`` bullets."""
    return {sym for sym, _ in glossary_entries(text)}


def parse_forge_log(text: str) -> dict[str, int]:
    """Cadence counters from forge-log.md: the highest round number and the cumulative
    submitted / passed counts.  The round number is read **only from entry title lines**
    matching ``## Round n`` (case-insensitive) - never from prose, so a Cadence line saying
    "macro audit at round 4" does not count as round 4.  Submitted / passed come from the
    a / b / c triple of the "Submitted" line (or a table cell holding such a triple)."""
    rounds = [int(x) for x in FORGE_ROUND_RE.findall(text)]
    submitted = passed = 0
    triple = re.compile(r"(\d+)\s*/\s*(\d+)\s*/\s*(\d+)")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            for c in cells:
                m = triple.fullmatch(c)
                if m:
                    submitted, passed = submitted + int(m[1]), passed + int(m[2])
        elif re.search(r"submitted", s, re.I):
            m = triple.search(s)
            if m:
                submitted, passed = submitted + int(m[1]), passed + int(m[2])
            else:
                submitted += sum(int(x) for x in re.findall(r"submitted\s*[:=]?\s*(\d+)", s, re.I))
                passed += sum(int(x) for x in re.findall(r"\bpassed\s*[:=]?\s*(\d+)", s, re.I))
    return {"rounds": max(rounds) if rounds else 0, "submitted": submitted, "passed": passed}


# --------------------------------------------------------------------------- loading
def detect_dirs(arg: Path) -> tuple[Path, Path]:
    """Return (programme_root, theory_dir) for a programme root, a ``g2g/`` folder or ``07_theory/``."""
    p = arg.resolve()
    if (p / "g2g" / THEORY_DIRNAME).is_dir():
        return p, p / "g2g" / THEORY_DIRNAME
    if (p / THEORY_DIRNAME).is_dir():
        return p.parent, p / THEORY_DIRNAME
    if p.name == THEORY_DIRNAME and p.is_dir():
        return p.parent.parent, p
    raise FileNotFoundError(f"no {THEORY_DIRNAME}/ found under {arg} "
                            f"(expected <programme_root>/g2g/{THEORY_DIRNAME}/)")


def _load_nodes(prog: Programme) -> None:
    for dirname in NODE_DIRS:
        folder = prog.theory / dirname
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            rel = relpath(path, prog.root)
            fm, body = parse_frontmatter(read_text(path))
            if fm is None:
                prog.load_violations.append(Violation(
                    "BAD_FRONTMATTER", rel, "no frontmatter block (--- ... ---) at the top of the file"))
                continue
            node = make_node(path, rel, dirname, fm, body)
            if node.missing_fields:
                prog.load_violations.append(Violation(
                    "BAD_FRONTMATTER", rel, "missing required field(s): " + ", ".join(node.missing_fields)))
            elif node.status not in STATUSES:
                prog.load_violations.append(Violation(
                    "BAD_FRONTMATTER", rel, f"status '{node.status}' is not one of {'/'.join(STATUSES)}"))
            if node.id in prog.nodes:
                prog.load_violations.append(Violation(
                    "BAD_FRONTMATTER", rel, f"duplicate id {node.id} (also in {prog.nodes[node.id].rel})"))
                continue
            if node.id != path.stem:
                prog.load_violations.append(Violation(
                    "BAD_FRONTMATTER", rel, f"id {node.id} does not match the file name {path.name}"))
            if not NODE_ID_RE.match(node.id):
                prog.load_violations.append(Violation(
                    "ID_FORMAT", rel, f"id {node.id!r} does not match P-dddd or P-dddd.n"))
            prog.nodes[node.id] = node
            prog.families.setdefault(node.base, []).append(node)


def _load_vrecords(prog: Programme) -> None:
    folder = prog.theory / "verifications"
    if not folder.is_dir():
        return
    for path in sorted(folder.glob("*.md")):
        rel = relpath(path, prog.root)
        fm, _ = parse_frontmatter(read_text(path))
        if fm is None or not all(k in fm for k in ("id", "candidate", "verdict")):
            prog.load_violations.append(Violation(
                "BAD_FRONTMATTER", rel, "verification record needs frontmatter with id, candidate, verdict"))
            continue
        prog.vrecords.append(VRecord(_as_str(fm, "id") or path.stem, rel,
                                     _ref(_as_str(fm, "candidate"), NODE_REF_RE),
                                     _as_str(fm, "verdict").lower()))


def resolve_ref(prog: Programme, ref: str) -> Node | None:
    """An explicit revision ID resolves exactly; a bare ID resolves to the current revision of its
    family: the highest verified one, else the highest not revoked / superseded, else the highest."""
    if "." in ref:
        return prog.nodes.get(ref)
    family = prog.families.get(ref)
    if not family:
        return None
    pool = ([n for n in family if n.status == "verified"]
            or [n for n in family if n.live] or family)
    return max(pool, key=lambda n: n.rev)


def _resolve_all(prog: Programme) -> None:
    for node in prog.nodes.values():
        node.resolved = {ref: resolve_ref(prog, ref) for ref in node.predecessors}
        prog.edges[node.id] = [t.id for t in node.resolved.values() if t is not None]


def load_programme(root: Path, theory: Path) -> Programme:
    prog = Programme(root=root, theory=theory)
    _load_nodes(prog)
    _load_vrecords(prog)
    prog.axioms = parse_registry(read_optional(theory / "axioms.md"), AXIOM_ENTRY_RE, AXIOM_STATUS_RE)
    prog.conjectures = parse_registry(read_optional(theory / "conjectures.md"), CJ_ENTRY_RE, CJ_STATUS_RE)
    for sym, origin in glossary_entries(read_optional(theory / "glossary.md")):
        prog.glossary.add(sym)
        prog.glossary_origin.setdefault(sym, []).append(origin)
    prog.forge_log = read_optional(theory / "forge-log.md") or None
    _resolve_all(prog)
    return prog


# --------------------------------------------------------------------------- graph helpers
def closure(prog: Programme, nid: str) -> list[str]:
    """Support closure: every node reachable from ``nid`` along predecessor edges (sorted)."""
    seen: set[str] = set()
    stack = list(prog.edges.get(nid, []))
    while stack:
        cur = stack.pop()
        if cur in seen or cur == nid:
            continue
        seen.add(cur)
        stack.extend(prog.edges.get(cur, []))
    return sorted(seen)


def find_cycles(prog: Programme) -> list[list[str]]:
    """Iterative DFS; each distinct cycle once, as a path ending where it started."""
    white, grey, black = 0, 1, 2
    colour = {nid: white for nid in prog.nodes}
    cycles: list[list[str]] = []
    seen_keys: set[frozenset[str]] = set()
    for start in sorted(prog.nodes):
        if colour[start] != white:
            continue
        colour[start] = grey
        path = [start]
        stack = [(start, iter(prog.edges.get(start, [])))]
        while stack:
            nid, it = stack[-1]
            for nxt in it:
                if colour[nxt] == white:
                    colour[nxt] = grey
                    path.append(nxt)
                    stack.append((nxt, iter(prog.edges.get(nxt, []))))
                    break
                if colour[nxt] == grey:
                    cyc = path[path.index(nxt):] + [nxt]
                    if frozenset(cyc) not in seen_keys:
                        seen_keys.add(frozenset(cyc))
                        cycles.append(cyc)
            else:
                colour[nid] = black
                path.pop()
                stack.pop()
    return cycles


def _arrow(ref: str, target: Node) -> str:
    """``P-0007 -> P-0007.1`` when a bare reference resolved to a revision, else just the ID."""
    return target.id if ref == target.id else f"{ref} -> {target.id}"


def has_pass_record(prog: Programme, node: Node) -> bool:
    """A pass record for this exact ID, or - for a revision that kept the original's record
    (the mechanical CJ -> A- replacement of 3b.8) - the record named in ``verification``."""
    for rec in prog.vrecords:
        if rec.verdict == "pass" and rec.candidate == node.id:
            return True
    if node.rev > 0 or node.revision_of:
        for rec in prog.vrecords:
            if (rec.verdict == "pass" and rec.id == node.verification_id
                    and rec.candidate.split(".")[0] == node.base):
                return True
    return False


# --------------------------------------------------------------------------- checks
def check_graph(prog: Programme) -> list[Violation]:
    out = []
    for node in prog.nodes.values():
        for ref, target in node.resolved.items():
            if target is None:
                out.append(Violation("DANGLING", node.rel, f"predecessor {ref} not found"))
        if node.live:
            for cj in node.conditional_on:
                if cj not in prog.conjectures:
                    out.append(Violation("DANGLING", node.rel, f"conditional_on {cj} not found in conjectures.md"))
    for cyc in find_cycles(prog):
        out.append(Violation("CYCLE", prog.nodes[cyc[0]].rel, "dependency cycle: " + " -> ".join(cyc)))
    return out


def check_placement(prog: Programme) -> list[Violation]:
    out = []
    for node in prog.nodes.values():
        if node.dirname == "propositions" and node.status == "proposed":
            out.append(Violation("PROPOSED_IN_PROPOSITIONS", node.rel,
                                 "status proposed inside propositions/ (candidates live in candidates/)"))
        if node.dirname == "candidates" and node.status == "verified":
            out.append(Violation("VERIFIED_IN_CANDIDATES", node.rel,
                                 "status verified inside candidates/ (a passed node moves to propositions/)"))
    return out


def check_truth_boundary(prog: Programme) -> list[Violation]:
    """Checks that apply to ``verified`` nodes only (BAN-12 / BAN-13 / 3b.8)."""
    out = []
    for node in prog.nodes.values():
        if node.status != "verified":
            continue
        if not has_pass_record(prog, node):
            named = f" (verification field: {node.verification_raw or 'empty'})"
            out.append(Violation("VERIFIED_NO_PASS", node.rel,
                                 f"no verification record with candidate {node.id} and verdict pass{named}"))
        for ref, target in node.resolved.items():
            if target is None:
                continue
            if target.status in DEAD_STATUSES:
                out.append(Violation("REVOKE_NOT_CASCADED", node.rel,
                                     f"predecessor {_arrow(ref, target)} is {target.status}; "
                                     "this node must be revoked or rebuilt (3b.8)"))
            elif target.status == "proposed":
                out.append(Violation("UNVERIFIED_PREDECESSOR", node.rel,
                                     f"predecessor {_arrow(ref, target)} is proposed ({target.dirname}/); "
                                     "only verified nodes are bricks (BAN-12)"))
        for aid in node.axioms_used + node.definitions_used:
            status = prog.axioms.get(aid, "unknown")
            if status == "revoked":
                out.append(Violation("REVOKE_NOT_CASCADED", node.rel,
                                     f"cites {aid} whose status is revoked; this node must be revoked or rebuilt"))
            elif status != "ratified":
                out.append(Violation("PENDING_AXIOM_CITED", node.rel,
                                     f"cites {aid} whose status is {status} (only ratified A-/D- are bricks)"))
        for cj in node.conditional_on:
            if prog.conjectures.get(cj) == "dropped":
                out.append(Violation("REVOKE_NOT_CASCADED", node.rel,
                                     f"conditional on {cj} which is dropped; this node must be revoked (3b.9)"))
        for sym in node.glossary_introduces:
            if sym not in prog.glossary:
                out.append(Violation("UNREGISTERED_SYMBOL", node.rel,
                                     f"glossary_introduces {sym} is not registered in glossary.md (BAN-13)"))
    return out


def check_conditions(prog: Programme) -> list[Violation]:
    """Inheritance of ``conditional_on``, the GUESS marker, and both halves of the faithful rule
    of 3b.4 - no ``[SIG]`` and no non-empty ``conditional_on`` in the support closure (live nodes).

    ``markers`` records only the marks in a node's **own** body (templates C.1); marks inherited
    through the support closure are not listed there but derived by rule - which is why
    FAITHFUL_WITH_SIG walks the predecessors instead of trusting the node's own ``markers``.
    FAITHFUL_WITH_CONDITION is the other half of the same rule: a provisional premise is not a
    shape present in the ratified axioms, so a conditional node is at least **strengthened**."""
    out = []
    for node in prog.nodes.values():
        if not node.live:
            continue
        for ref, target in node.resolved.items():
            if target is None:
                continue
            missing = [c for c in target.conditional_on if c not in node.conditional_on]
            if missing:
                out.append(Violation("CONDITIONAL_NOT_INHERITED", node.rel,
                                     f"predecessor {target.id} is conditional on {', '.join(missing)}; "
                                     "conditional_on must inherit it (BAN-03)"))
        if node.conditional_on and "GUESS" not in node.markers:
            out.append(Violation("CONDITIONAL_WITHOUT_GUESS", node.rel,
                                 f"conditional_on {', '.join(node.conditional_on)} but markers lack GUESS"))
        if node.operationalization == "faithful":
            carriers, conditional = [], []
            for nid in [node.id] + closure(prog, node.id):
                other = prog.nodes[nid]
                if "SIG" in other.markers:
                    carriers.append(nid)
                elif other.operationalization in ("strengthened", "extended"):
                    carriers.append(f"{nid} ({other.operationalization})")
                if other.conditional_on:
                    conditional.append(f"{nid} (conditional on {', '.join(other.conditional_on)})")
            if carriers:
                out.append(Violation("FAITHFUL_WITH_SIG", node.rel,
                                     "tagged faithful but [SIG] is in its support closure: " + ", ".join(carriers)))
            if conditional:
                out.append(Violation("FAITHFUL_WITH_CONDITION", node.rel,
                                     "tagged faithful but a provisional premise is in its support closure: "
                                     + ", ".join(conditional)
                                     + "; a conditional node is at least strengthened (3b.4)"))
    return out


def check_exempt_revisions(prog: Programme) -> list[Violation]:
    """The one revision exempt from the gate (3b.8): the mechanical replacement of
    ``conditional on CJ-xx ([GUESS])`` by ``by A-xx`` that 3b.9 licenses once the conjecture is
    ratified as an axiom.  Such a revision is recognised by its keeping the **original's**
    verification record ID, and it may then differ from the original by that substitution and by
    dropping that one CJ from ``conditional_on`` - by nothing else.  A revision that cites a new
    V- record went through the gate on its own and is not checked here."""
    out = []
    for node in prog.nodes.values():
        if not node.live or node.rev == 0 or not node.revision_of:
            continue
        original = prog.nodes.get(node.revision_of) or max(
            (n for n in prog.families.get(node.base, []) if n.rev < node.rev),
            key=lambda n: n.rev, default=None)
        if original is None or not node.verification_id or node.verification_id != original.verification_id:
            continue
        kept = f"keeps the verification record {node.verification_id} of {original.id}"
        removed = [c for c in original.conditional_on if c not in node.conditional_on]
        added = [c for c in node.conditional_on if c not in original.conditional_on]
        if len(removed) != 1 or added:
            out.append(Violation("EXEMPT_REVISION_CHANGED", node.rel,
                                 f"{kept} but conditional_on went {original.conditional_on or '[]'} -> "
                                 f"{node.conditional_on or '[]'}; the gate-exempt swap removes exactly one "
                                 "CJ (3b.8) - any other revision opens a verifier"))
            continue
        cj, rev_text = removed[0], digest_text(node.sections)
        orig_text = digest_text(original.sections)
        candidates = sorted(set(EXEMPT_AXIOM_RE.findall(rev_text)) | set(node.axioms_used))
        if not any(swapped == rev_text and count > 0
                   for swapped, count in (swap_premise(orig_text, cj, a) for a in candidates)):
            out.append(Violation("EXEMPT_REVISION_CHANGED", node.rel,
                                 f"{kept}, so the only licensed change is 'conditional on {cj} ([GUESS])' -> "
                                 f"'by A-xx'; Statement/Derivation differ from {original.id} by more than that "
                                 "(3b.8) - this revision opens a verifier"))
    return out


def check_sha(prog: Programme) -> list[Violation]:
    """``content_sha`` present and current for nodes in propositions/ (candidates are exempt)."""
    out = []
    for node in prog.nodes.values():
        if node.dirname != "propositions":
            continue
        if not SHA_RE.match(node.content_sha):
            out.append(Violation("MISSING_SHA", node.rel, "content_sha missing (run --fill-sha)"))
        elif node.content_sha != compute_sha(node.sections):
            out.append(Violation("STALE_SHA", node.rel,
                                 f"content_sha {node.content_sha} != computed {compute_sha(node.sections)}: "
                                 "Statement/Derivation changed after the digest was filled"))
    return out


def run_checks(prog: Programme) -> list[Violation]:
    """All counted checks, sorted by (file, code, message) for stable output."""
    violations = list(prog.load_violations)
    for check in (check_graph, check_placement, check_truth_boundary, check_conditions,
                  check_exempt_revisions, check_sha):
        violations.extend(check(prog))
    violations.sort(key=lambda v: (v.file, v.code, v.message))
    return violations


# --------------------------------------------------------------------------- pre-gate (--pregate)
def _names(term: str) -> list[str]:
    """A defined term and, for ``f(x) := …``, the name ``f`` it defines."""
    head = term.split("(", 1)[0].rstrip()
    return [term, head] if head and head != term else [term]


def defined_terms(node: Node) -> list[tuple[str, str, str]]:
    """``(term, section, marker)`` for each term the Statement or the Derivation defines with
    ``:=`` or in bold (first occurrence only)."""
    seen: set[str] = set()
    out = []
    for section in ("statement", "derivation"):
        text = node.sections.get(section, "")
        found = [(m.start(), norm_symbol(m.group(1).lstrip("([{\"'“‘（「『")), ":=")
                 for m in DEFINE_RE.finditer(text)]
        found += [(m.start(), norm_symbol(m.group(1)).rstrip(".,;:。，；：").strip(), "bold")
                  for m in BOLD_RE.finditer(text) if ":=" not in m.group(1) and "≔" not in m.group(1)]
        for _, term, marker in sorted(found):
            if term and term not in seen:
                seen.add(term)
                out.append((term, section.capitalize(), marker))
    return out


def _same_family(prog: Programme, sym: str, node: Node) -> bool:
    """Every glossary row for ``sym`` was introduced by a node of ``node``'s own family."""
    origins = prog.glossary_origin.get(sym, [])
    refs = [NODE_REF_RE.search(o) for o in origins]
    return bool(origins) and all(r and r.group(0).split(".")[0] == node.base for r in refs)


def pregate(prog: Programme, node: Node) -> list[Violation]:
    """The pre-gate registration check of one candidate: (1) a ``glossary_introduces`` entry
    already in glossary.md, unless that row was introduced by the candidate's own family (a
    revision re-listing its symbol); (2) a term defined with ``:=`` or in bold that is not listed -
    a collision instead when glossary.md already has the name from another family; (3) the dual,
    strict part or inverse (same decoration) of an introduced order symbol, used but neither
    listed nor registered."""
    out: list[Violation] = []
    listed = set(node.glossary_introduces)

    def collides(name: str, what: str) -> bool:
        if name not in prog.glossary or _same_family(prog, name, node):
            return False
        origin = ", ".join(o for o in prog.glossary_origin.get(name, []) if o) or "not stated"
        out.append(Violation("SYMBOL_COLLISION", node.rel,
                             f"{what} is already registered in glossary.md (introduced by {origin}); "
                             "a new symbol or defined term may not reuse a glossary name"))
        return True

    for sym in dict.fromkeys(node.glossary_introduces):
        collides(sym, f"glossary_introduces {sym}")
    for term, section, marker in defined_terms(node):
        names = _names(term)
        if any(n in listed for n in names):
            continue
        if any(collides(n, f"{section} defines {term} ({marker}), but {n}") for n in names):
            continue
        if any(n in prog.glossary for n in names):
            continue  # registered by this candidate's own family
        out.append(Violation("UNLISTED_DEFINITION", node.rel,
                             f"{section} defines {term} ({marker}) but glossary_introduces does not list it"))
    for sym in dict.fromkeys(node.glossary_introduces):
        for glyph in ORDER_VARIANTS.get(sym[:1], ""):
            variant = glyph + sym[1:]
            if variant in listed or variant in prog.glossary:
                continue
            used = re.compile(re.escape(variant) + r"(?![\w'′^_{])")
            where = [s.capitalize() for s in ("statement", "derivation") if used.search(node.sections.get(s, ""))]
            if where:
                out.append(Violation("UNLISTED_ORDER_DERIVATIVE", node.rel,
                                     f"{variant} is used in the {' and '.join(where)} but neither listed nor "
                                     f"registered; the dual, strict part and inverse of the introduced order "
                                     f"symbol {sym} each count as a symbol"))
    return out


def run_pregate(prog: Programme, ids: list[str]) -> list[Violation]:
    """``pregate`` over the named candidates; raises ``LookupError`` for an ID that is not a
    proposed candidate in ``candidates/``."""
    nodes = []
    for nid in dict.fromkeys(ids):
        node = prog.nodes.get(nid)
        if node is None:
            raise LookupError(f"--pregate {nid}: no such node (a file whose frontmatter does not parse "
                              "is not loaded; run without --pregate to see why)")
        if node.dirname != "candidates" or node.status != "proposed":
            raise LookupError(f"--pregate {nid}: not a proposed candidate "
                              f"({node.dirname}/, status {node.status or 'empty'})")
        nodes.append(node)
    return [v for node in nodes for v in pregate(prog, node)]


# --------------------------------------------------------------------------- report
def build_report(prog: Programme, violations: list[Violation]) -> dict[str, object]:
    nodes = list(prog.nodes.values())
    info: list[Violation] = []
    theorems = []
    # current revisions only (what a bare ID resolves to); a bare ID in `scope` means the current revision
    for node in sorted((n for n in nodes if n.kind == "theorem" and resolve_ref(prog, n.base) is n),
                       key=lambda n: n.id):
        cl = closure(prog, node.id)
        uncond = [c for c in cl if prog.nodes[c].status == "verified" and not prog.nodes[c].conditional_on]
        closed = node.status == "verified" and not node.conditional_on
        tagged = sorted(m.id for m in nodes if m.base != node.base and m.status == "verified" and not m.conditional_on
                        and getattr(resolve_ref(prog, _ref(m.scope, NODE_REF_RE)), "id", None) == node.id)
        theorems.append({"id": node.id, "status": node.status, "conditional_on": node.conditional_on,
                         "closure": cl, "closure_size": len(cl), "unconditional_size": len(uncond),
                         "closed": closed, "scope_tagged": tagged})
        if node.status == "verified" and node.conditional_on:
            info.append(Violation("CLOSURE_NOT_CLOSED", node.rel,
                                  f"theorem verified but conditional on {', '.join(node.conditional_on)}: "
                                  "the support closure is not closed (3b.7)"))
        if node.status == "verified" and {c.split(".")[0] for c in cl} != {t.split(".")[0] for t in tagged}:
            info.append(Violation("SCOPE_MISMATCH", node.rel,
                                  f"closure {cl} differs from the verified nodes whose scope holds this target "
                                  f"theorem's ID {node.id} {tagged}: the elaboration's route judgment and the "
                                  "graph disagree (3b.7; conditional nodes excluded)"))
    by_sha: dict[str, list[str]] = {}
    for node in nodes:
        if node.live and SHA_RE.match(node.content_sha):
            by_sha.setdefault(node.content_sha, []).append(node.id)
    for sha, ids in sorted(by_sha.items()):
        if len(ids) > 1:
            info.append(Violation("DUPLICATE_SHA", prog.nodes[ids[0]].rel,
                                  f"identical Statement+Derivation digest {sha} in {', '.join(ids)}"))
    for node in sorted(nodes, key=_sort_key):
        for key, ref in (("revision_of", node.revision_of), ("supersedes", node.supersedes)):
            named = ref in prog.nodes or ("." not in ref and any(
                n.id != node.id for n in prog.families.get(ref, [])))
            if ref and not named:
                info.append(Violation("DANGLING_FIELD", node.rel, f"{key} {ref} names no node"))
    # the current revision of a family is what its bare ID resolves to; the others are historical
    current = {r.id for r in (resolve_ref(prog, base) for base in prog.families) if r is not None}
    revocations = Counter(n.revoked_category or UNCATEGORISED for n in nodes if n.status == "revoked")
    revisions = Counter(n.revision_category or UNCATEGORISED for n in nodes if n.rev > 0 or n.revision_of)
    cadence = None
    if prog.forge_log is not None:
        counters = parse_forge_log(prog.forge_log)
        k, m, t = CADENCE_DEFAULTS["K"], CADENCE_DEFAULTS["M"], CADENCE_DEFAULTS["T"]
        verified = sum(1 for n in nodes if n.status == "verified" and n.id in current)
        cadence = {**counters, "verified": verified, "defaults": CADENCE_DEFAULTS,
                   # more verified nodes on disk (revisions included: each passed the gate) than the log
                   # says passed: the round entry is not written yet
                   "forge_log_behind": sum(1 for n in nodes if n.status == "verified") > counters["passed"],
                   "control_beats_due": counters["submitted"] // k,
                   "next_control_beat_at": (counters["submitted"] // k + 1) * k,
                   "next_macro_audit_round": (counters["rounds"] // m + 1) * m,
                   "next_theory_tribunal_at": (verified // t + 1) * t}
    return {"nodes": {"total": len(nodes),
                      "propositions": sum(1 for n in nodes if n.dirname == "propositions"),
                      "candidates": sum(1 for n in nodes if n.dirname == "candidates")},
            # a revision still under the gate (proposed) counts with the current ones, not as history
            "status": {"current": dict(sorted(Counter(n.status for n in nodes
                                                      if n.id in current or n.status == "proposed").items())),
                       "historical": dict(sorted(Counter(n.status for n in nodes
                                                         if n.id not in current and n.status != "proposed").items()))},
            "reasons": {"revocations": dict(sorted(revocations.items())),
                        "revisions": dict(sorted(revisions.items())),
                        "gate_misses": revocations["gate-miss"] + revisions["gate-miss"]},
            "empirical_status": dict(sorted(Counter(n.empirical_status or "-" for n in nodes).items())),
            "kind": dict(sorted(Counter(n.kind or "-" for n in nodes).items())),
            "axioms": dict(sorted(Counter(prog.axioms.values()).items())),
            "conjectures": dict(sorted(Counter(prog.conjectures.values()).items())),
            "glossary_symbols": len(prog.glossary),
            "theorems": theorems, "cadence": cadence,
            "informational": [v.as_dict() for v in info],
            "violations": len(violations)}


def render_report(rep: dict[str, object], root: Path, ascii_only: bool = False) -> str:
    """Human-readable report; ``ascii_only`` swaps the arrows and dots for ASCII (used when the
    console could not be switched to UTF-8, e.g. a Windows code-page pipe)."""
    def fmt(d: dict[str, int]) -> str:
        return " · ".join(f"{k} {v}" for k, v in d.items()) or "-"

    n, r = rep["nodes"], rep["reasons"]
    lines = [f"== G2G proposition-graph report: {root} ==",
             f"nodes: {n['total']} (propositions/ {n['propositions']} · candidates/ {n['candidates']})",
             f"status (current revisions — what a bare ID resolves to — and candidates): "
             f"{fmt(rep['status']['current'])}",
             f"status (historical revisions): {fmt(rep['status']['historical'])}",
             f"revocations by reason: {fmt(r['revocations'])}", f"revisions by reason: {fmt(r['revisions'])}",
             f"gate misses (revocations and revisions): {r['gate_misses']}",
             f"empirical_status: {fmt(rep['empirical_status'])}",
             f"kind: {fmt(rep['kind'])}", f"axioms.md (A-/D-): {fmt(rep['axioms'])}",
             f"conjectures.md: {fmt(rep['conjectures'])}", f"glossary symbols: {rep['glossary_symbols']}",
             "theorems (support closure):"]
    for t in rep["theorems"]:
        state = "CLOSED" if t["closed"] else ("conditional on " + ", ".join(t["conditional_on"])
                                              if t["conditional_on"] else "not passed")
        lines.append(f"  {t['id']} [{t['status']}] closure {t['closure_size']} node(s), unconditional "
                     f"{t['unconditional_size']} — {state}; scope-tagged verified nodes: {len(t['scope_tagged'])}")
    if not rep["theorems"]:
        lines.append("  (no theorem-kind node yet)")
    c = rep["cadence"]
    if c:
        d = c["defaults"]
        lines += [f"cadence hints (forge-log.md; defaults K={d['K']} M={d['M']} T={d['T']}):",
                  f"  rounds logged {c['rounds']} → next macro audit at round {c['next_macro_audit_round']}",
                  f"  cumulative submissions {c['submitted']} (passed {c['passed']}) → control beats due so far "
                  f"{c['control_beats_due']}, next at {c['next_control_beat_at']}",
                  f"  verified nodes (current revisions) {c['verified']} → next theory tribunal at "
                  f"{c['next_theory_tribunal_at']} (or when a target theorem closes)"]
        if c.get("forge_log_behind"):
            lines.append("  (forge-log has no entry for the nodes on disk yet — write the round entry)")
    else:
        lines.append("cadence: forge-log.md not found")
    lines.append("informational (not counted):")
    lines += [f"  {i['code']}  {i['file']}  {i['message']}" for i in rep["informational"]] or ["  none"]
    lines.append(f"violations: {rep['violations']}")
    text = "\n".join(lines)
    if ascii_only:
        for glyph, plain in ASCII_FALLBACK:
            text = text.replace(glyph, plain)
    return text


# --------------------------------------------------------------------------- writers
def _sort_key(node: Node) -> tuple[int, int, str]:
    m = re.match(r"P-(\d+)", node.id)
    return (int(m.group(1)) if m else 10 ** 9, node.rev, node.id)


def render_index(prog: Programme) -> str:
    def esc(text: str) -> str:
        return text.replace("|", "\\|").replace("\n", " ").strip() or "-"

    rows = []
    for n in sorted(prog.nodes.values(), key=_sort_key):
        used = n.axioms_used + n.definitions_used + n.assumptions_used
        rows.append("| " + " | ".join([n.id, esc(n.title), esc(n.kind), esc(n.status), esc(n.empirical_status),
                                        esc(", ".join(n.predecessors)), esc(", ".join(used)),
                                        esc(n.verification_id or n.verification_raw), esc(n.layer)]) + " |")
    total = len(prog.nodes)
    cands = sum(1 for n in prog.nodes.values() if n.dirname == "candidates")
    head = ["# Proposition graph — overview table", "",
            "Regenerated by `python scripts/pg_check.py <programme_root> --regen-index` at the start of every "
            "round; maintained by hand where scripts cannot run (the forge log then says \"checked by hand this "
            "round\"). Bare IDs P-xxxx resolve to the current revision. Rows with status `proposed` are "
            "candidates (not bricks).", "",
            f"Nodes: {total} (propositions/ {total - cands} · candidates/ {cands})", "",
            "| " + " | ".join(INDEX_COLUMNS) + " |", "|" + "---|" * len(INDEX_COLUMNS)]
    return "\n".join(head + rows) + "\n"


def regen_index(prog: Programme) -> bool:
    """Rewrite ``graph-index.md``; return True when the file content changed."""
    target = prog.theory / "graph-index.md"
    content = render_index(prog)
    if target.is_file() and read_text(target) == content:
        return False
    target.write_text(content, encoding="utf-8", newline="\n")
    return True


def rewrite_content_sha(path: Path, sha: str) -> bool:
    """Set ``content_sha`` in the frontmatter, touching nothing else (line endings kept)."""
    with open(path, encoding="utf-8", newline="") as fh:
        lines = fh.read().splitlines(keepends=True)
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return False
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return False
    eol = "\r\n" if lines[end].endswith("\r\n") else "\n"
    new_line = f"content_sha: {sha}{eol}"
    for i in range(1, end):
        if re.match(r"^content_sha\s*:", lines[i]):
            if lines[i] == new_line:
                return False
            lines[i] = new_line
            break
    else:
        at = next((i for i in range(1, end) if lines[i].startswith("submitted_by")), end)
        lines.insert(at, new_line)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(lines))
    return True


def fill_sha(prog: Programme) -> list[str]:
    """Fill missing or stale ``content_sha`` in every node file; return the files changed."""
    changed = []
    for node in sorted(prog.nodes.values(), key=_sort_key):
        want = compute_sha(node.sections)
        if node.content_sha != want and rewrite_content_sha(node.path, want):
            node.content_sha = want
            changed.append(node.rel)
    return changed


# --------------------------------------------------------------------------- CLI
def _utf8_console() -> bool:
    """Switch stdout / stderr to UTF-8 (a Windows pipe or console without PYTHONIOENCODING
    defaults to a code page that mangles the report's arrows); return False when a stream
    could not be switched, in which case the report falls back to ASCII glyphs."""
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
        prog="pg_check.py",
        description="G2G Theory Forge proposition-graph check (METHODOLOGY.md 3b.5). "
                    "Exit code = number of violations (0 = clean), capped at 255.")
    parser.add_argument("programme_root", help="folder containing g2g/, or the g2g/ folder, or 07_theory/")
    parser.add_argument("--report", action="store_true", help="print a health summary after the violations")
    parser.add_argument("--regen-index", action="store_true", help="rewrite g2g/07_theory/graph-index.md")
    parser.add_argument("--fill-sha", action="store_true", help="write missing / stale content_sha into node files")
    parser.add_argument("--json", action="store_true", help="machine-readable output instead of lines")
    parser.add_argument("--pregate", nargs="+", metavar="P-ID",
                        help="run only the pre-gate registration check on these proposed candidates, "
                             "before each verifier dispatch (exit code = number of findings)")
    parser.add_argument("--version", action="version", version=f"pg_check {VERSION}")
    args = parser.parse_args(argv)
    if args.pregate and (args.report or args.regen_index or args.fill_sha):
        parser.error("--pregate runs alone (not with --report, --regen-index or --fill-sha)")
    utf8_console = _utf8_console()
    try:
        root, theory = detect_dirs(Path(args.programme_root))
        prog = load_programme(root, theory)
    except (FileNotFoundError, OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if args.pregate:
        try:
            findings = run_pregate(prog, args.pregate)
        except LookupError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return EXIT_USAGE
        exit_code = min(len(findings), EXIT_CAP)
        if args.json:
            print(json.dumps({"version": VERSION, "programme_root": str(root), "theory_dir": str(theory),
                              "pregate": list(dict.fromkeys(args.pregate)),
                              "findings": [v.as_dict() for v in findings], "finding_count": len(findings),
                              "exit_code": exit_code}, ensure_ascii=False, indent=2))
        else:
            for v in findings:
                print(_console_safe(v.line(), utf8_console))
        return exit_code
    actions: dict[str, object] = {}
    if args.fill_sha:
        actions["fill_sha"] = fill_sha(prog)
    violations = run_checks(prog)
    if args.regen_index:
        actions["regen_index"] = "written" if regen_index(prog) else "unchanged"
    report = build_report(prog, violations) if args.report else None
    exit_code = min(len(violations), EXIT_CAP)
    if args.json:
        print(json.dumps({"version": VERSION, "programme_root": str(root), "theory_dir": str(theory),
                          "violations": [v.as_dict() for v in violations], "violation_count": len(violations),
                          "exit_code": exit_code, "actions": actions, "report": report},
                         ensure_ascii=False, indent=2))
        return exit_code
    for v in violations:
        print(v.line())
    if report is not None:
        print(render_report(report, root, ascii_only=not utf8_console))
    if "fill_sha" in actions:
        files = actions["fill_sha"]
        print(f"fill-sha: {len(files)} file(s) updated" + (": " + ", ".join(files) if files else ""),
              file=sys.stderr)
    if "regen_index" in actions:
        print(f"regen-index: graph-index.md {actions['regen_index']}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
