#!/usr/bin/env python3
"""cadence_check.py - the cycle-mode cadence check of a Grand-to-Ground (G2G) programme.

Every M cycles (M as in the charter's macro-audit line, default 4) g2g-cycle runs this script and
writes its first line into the log: were the last M questions all from salvage or earlier cards
rather than from the queue, the plan or the Vision?  If so the verdict is "steer" (draw the next
question from the queue, the plan or the Vision); otherwise "no steer", with the split; with fewer
than M cycles in the log, "no verdict".  It only reports - it never stops a run - and it does not
need ``07_theory/``.

What it reads, all in the ``g2g/`` workspace:

- ``00_programme.md``: M from the macro-audit line (``M = n``); 4 when the charter has none.
- ``04_log.md``: the last M ``CYCLE #n · question Sk`` keyword lines (a cycle logged more than
  once, e.g. paused and then resumed, counts once, with its latest line).
- ``02_question-registry.md``: the source of each question's seed row - the tag
  ``[source: queue | plan | vision | salvage | card C-xxx]``, or on rows written before the tag
  the markers ``parent:`` / ``父：`` / ``SALVAGE`` / ``打捞``.  Anything else is "source unknown",
  never counted as salvage.

Pure standard library, Python >= 3.10, UTF-8 file IO (a BOM and CRLF line ends are fine); nothing
is ever written.  Usage::

    python "${CLAUDE_PLUGIN_ROOT}/scripts/cadence_check.py" g2g   # the form the skills use; cwd = the project root
    python scripts/cadence_check.py <workspace> [--json] [--m N]

``<workspace>`` is the ``g2g/`` folder or the folder that contains it.  Exit code: 0 = no steer
(or no verdict), 1 = steer, 2 = usage or IO error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VERSION = "0.4.0"
CHARTER, LOG, REGISTRY = "00_programme.md", "04_log.md", "02_question-registry.md"
DEFAULT_M = 4
EXIT_NO_STEER, EXIT_STEER, EXIT_USAGE = 0, 1, 2
SALVAGE, NOT_SALVAGE, UNKNOWN = "salvage", "not salvage", "unknown"
LABELS = {SALVAGE: "salvage or earlier card", NOT_SALVAGE: "queue, plan or Vision", UNKNOWN: "source unknown"}
#: The charter's macro-audit line ("macro audit every M = {4} rounds or cycles") and its M.
MACRO_RE = re.compile(r"macro[ -]audit|宏观审计", re.I)
M_RE = re.compile(r"(?<![A-Za-z])M\s*[=＝]\s*\{?\s*(\d+)")
#: A cycle keyword line of 04_log.md (g2g-go Step 6): "CYCLE #n · question Sk · severity …".
CYCLE_RE = re.compile(r"^[ \t>*_`-]*CYCLE\s*#\s*(\d+)\b(.*)$", re.M)
QUESTION_RE = re.compile(r"\bquestion\s+[`*\"']*([^\s·,;:`*\"']+)", re.I)
#: The registry's source tag on a seed row, and the markers of old rows that came from salvage
#: or an earlier card.
SOURCE_TAG_RE = re.compile(r"\[\s*source\s*:\s*([^\]]*?)\s*\]", re.I)
LEGACY_RE = re.compile(r"(?<![A-Za-z])(?:(?i:parent)\s*[:：]|SALVAGE(?![A-Za-z]))|父\s*[:：]|打捞")
#: Output glyphs and their ASCII fallback, used when stdout could not be switched to UTF-8.
ASCII_FALLBACK = (("—", "-"), ("·", ","), ("→", "->"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def detect_workspace(arg: Path) -> Path:
    """The ``g2g/`` folder: the argument itself or its ``g2g/`` child, whichever holds 04_log.md."""
    p = arg.resolve()
    for folder in (p / "g2g", p):
        if (folder / LOG).is_file():
            return folder
    raise FileNotFoundError(f"no {LOG} found in {arg} or {arg / 'g2g'} (expected the g2g/ workspace)")


def charter_m(text: str) -> int | None:
    """M from the first macro-audit line of the charter that states one."""
    for line in text.splitlines():
        if MACRO_RE.search(line):
            m = M_RE.search(line)
            if m and int(m.group(1)) > 0:
                return int(m.group(1))
    return None


def logged_cycles(text: str) -> list[tuple[int, str]]:
    """``(cycle number, question ID or "")`` per cycle, ordered by each cycle's latest keyword line."""
    latest: dict[int, tuple[int, str]] = {}
    for order, m in enumerate(CYCLE_RE.finditer(text)):
        q = QUESTION_RE.search(m.group(2))
        latest[int(m.group(1))] = (order, q.group(1).rstrip(".") if q else "")
    return [(n, qid) for n, (_, qid) in sorted(latest.items(), key=lambda item: item[1][0])]


def seed_rows(registry: str, qid: str) -> list[str]:
    """Registry lines whose leading token is the question ID (seed bullet, table row, heading)."""
    row = re.compile(r"^[ \t>|#*+`_-]*" + re.escape(qid) + r"(?!\w)(?!\.\w)")
    return [line for line in registry.splitlines() if row.match(line)]


def classify(rows: list[str]) -> tuple[str, str]:
    """``(class, evidence)`` from a question's registry rows: a recognised ``[source: …]`` tag first,
    then a salvage marker of an old row; anything else is unknown."""
    if not rows:
        return UNKNOWN, "no seed row"
    tags = [m for m in (SOURCE_TAG_RE.search(r) for r in rows) if m]
    for tag in tags:
        value = tag.group(1).strip().lower()
        if value == "salvage" or re.match(r"card\b", value):
            return SALVAGE, tag.group(0)
        if value in ("queue", "plan", "vision"):
            return NOT_SALVAGE, tag.group(0)
    for row in rows:
        marker = LEGACY_RE.search(row)
        if marker:
            return SALVAGE, marker.group(0)
    return UNKNOWN, f"unrecognised {tags[0].group(0)}" if tags else "no source marker"


def check(workspace: Path, m_override: int | None = None) -> dict[str, object]:
    charter = workspace / CHARTER
    log, registry = read_text(workspace / LOG), read_text(workspace / REGISTRY)
    m = m_override or (charter_m(read_text(charter)) if charter.is_file() else None)
    m_from = "--m" if m_override else ("charter" if m else "default")
    m = m or DEFAULT_M
    cycles = logged_cycles(log)
    questions = []
    for n, qid in cycles[-m:]:
        cls, evidence = classify(seed_rows(registry, qid)) if qid else (UNKNOWN, "no question ID in the keyword line")
        questions.append({"cycle": n, "question": qid, "class": cls, "evidence": evidence})
    counts = {cls: sum(1 for q in questions if q["class"] == cls) for cls in (SALVAGE, NOT_SALVAGE, UNKNOWN)}
    head = f"Cadence (M = {m}):"
    if len(cycles) < m:
        verdict = "no verdict"
        line = f"{head} {len(cycles)} cycle(s) in the log, fewer than M — no verdict."
    elif counts[SALVAGE] == m:
        verdict = "steer"
        line = (f"{head} the last {m} questions all came from salvage or earlier cards — steer: draw the next "
                "question from the queue, the plan or the Vision.")
    else:
        verdict = "no steer"
        line = (f"{head} the last {m} questions were not all from salvage or earlier cards (salvage or cards "
                f"{counts[SALVAGE]} · queue, plan or Vision {counts[NOT_SALVAGE]} · source unknown "
                f"{counts[UNKNOWN]}) — no steer.")
    return {"version": VERSION, "workspace": str(workspace), "m": m, "m_from": m_from,
            "cycles_logged": len(cycles), "verdict": verdict, "line": line,
            "counts": {"salvage": counts[SALVAGE], "not_salvage": counts[NOT_SALVAGE], "unknown": counts[UNKNOWN]},
            "questions": questions, "exit_code": EXIT_STEER if verdict == "steer" else EXIT_NO_STEER}


def render(result: dict[str, object]) -> str:
    """The verdict line (for the orchestrator to copy into the log), then one line per question.
    The question lines never start with ``CYCLE #``, so a copy of them is not read as a cycle."""
    lines = [result["line"]]
    lines += [f"  #{q['cycle']} · {q['question'] or '?'} · {LABELS[q['class']]} · {q['evidence']}"
              for q in result["questions"]]
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
        prog="cadence_check.py",
        description="G2G cycle cadence check: were the last M questions all from salvage or earlier cards? "
                    "Exit code 0 = no steer (or no verdict), 1 = steer, 2 = usage or IO error.")
    parser.add_argument("workspace", help="the g2g/ folder, or the folder that contains it")
    parser.add_argument("--json", action="store_true", help="machine-readable output instead of lines")
    parser.add_argument("--m", type=int, metavar="N", help="override M (testing; default: the charter's macro-audit line, else 4)")
    parser.add_argument("--version", action="version", version=f"cadence_check {VERSION}")
    args = parser.parse_args(argv)
    if args.m is not None and args.m < 1:
        parser.error("--m must be at least 1")
    utf8_console = _utf8_console()
    try:
        result = check(detect_workspace(Path(args.workspace)), args.m)
    except (FileNotFoundError, OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if args.json:
        print(json.dumps(result, ensure_ascii=not utf8_console, indent=2))
    else:
        print(_console_safe(render(result), utf8_console))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
