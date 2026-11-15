"""Unit tests for scripts/pg_check.py.

Run from the plugin root:  python -m pytest -q scripts/tests

fixture_ok/  - a minimal clean Forge programme (must produce zero violations)
fixture_bad/ - one programme that trips every violation code at least once; it also carries the
               positive control for the gate-exempt revision (P-0038 -> P-0038.1), which must
               trip nothing at all
The pre-gate, DANGLING_FIELD, reason-category and current / historical tests write fictional
nodes into temporary copies of fixture_ok; the fixtures themselves are never modified.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))
import pg_check as pg  # noqa: E402

FIXTURE_OK = HERE / "fixture_ok"
FIXTURE_BAD = HERE / "fixture_bad"
T = "g2g/07_theory/"

#: Exact (code, file) pairs fixture_bad must produce - nothing more, nothing less.
EXPECTED_BAD = sorted([
    ("BAD_FRONTMATTER", T + "propositions/P-0090.md"),
    ("BAD_FRONTMATTER", T + "propositions/stray-note.md"),
    ("ID_FORMAT", T + "candidates/P-91.md"),
    ("CYCLE", T + "propositions/P-0010.md"),
    ("DANGLING", T + "propositions/P-0012.md"),
    ("PROPOSED_IN_PROPOSITIONS", T + "propositions/P-0013.md"),
    ("VERIFIED_IN_CANDIDATES", T + "candidates/P-0014.md"),
    ("VERIFIED_NO_PASS", T + "propositions/P-0015.md"),
    ("UNVERIFIED_PREDECESSOR", T + "propositions/P-0016.md"),
    ("UNREGISTERED_SYMBOL", T + "propositions/P-0018.md"),
    ("REVOKE_NOT_CASCADED", T + "propositions/P-0020.md"),   # revoked predecessor
    ("REVOKE_NOT_CASCADED", T + "propositions/P-0022.md"),   # superseded predecessor
    ("REVOKE_NOT_CASCADED", T + "propositions/P-0023.md"),   # dropped conjecture
    ("REVOKE_NOT_CASCADED", T + "propositions/P-0035.md"),   # revoked axiom
    ("PENDING_AXIOM_CITED", T + "propositions/P-0026.md"),   # A-09 pending
    ("PENDING_AXIOM_CITED", T + "propositions/P-0026.md"),   # D-09 unknown
    ("CONDITIONAL_NOT_INHERITED", T + "propositions/P-0027.md"),
    ("CONDITIONAL_WITHOUT_GUESS", T + "propositions/P-0029.md"),
    ("FAITHFUL_WITH_SIG", T + "propositions/P-0030.md"),     # own [SIG]
    ("FAITHFUL_WITH_SIG", T + "propositions/P-0031.md"),     # inherited from P-0030
    ("FAITHFUL_WITH_CONDITION", T + "propositions/P-0036.md"),      # faithful over a provisional premise
    ("EXEMPT_REVISION_CHANGED", T + "propositions/P-0037.1.md"),    # kept V-0037 but added a step
    ("MISSING_SHA", T + "propositions/P-0033.md"),
    ("STALE_SHA", T + "propositions/P-0034.md"),
])


def check(root: Path) -> tuple[pg.Programme, list[pg.Violation]]:
    r, t = pg.detect_dirs(root)
    prog = pg.load_programme(r, t)
    return prog, pg.run_checks(prog)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(SCRIPTS / "pg_check.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env)


class TempCopyMixin:
    def copy_fixture(self, src: Path) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="pg_check_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        dst = tmp / src.name
        shutil.copytree(src, dst)
        return dst


class ParserTests(unittest.TestCase):
    def test_frontmatter_lists_comments_nested_brackets(self):
        text = ("---\nid: P-0007\npredecessors: [P-0003, P-0005]   # dependency edges\n"
                "markers: [[SIG], [GUESS]]\nconditional_on: []\ntitle: ratio x_i/r_i (#1 case)\n"
                "content_sha: (filled by the script)\n---\n## Statement\nS\n\n## Derivation\nD\n### sub\nmore\n")
        fm, body = pg.parse_frontmatter(text)
        self.assertEqual(fm["predecessors"], ["P-0003", "P-0005"])
        self.assertEqual(fm["markers"], ["[SIG]", "[GUESS]"])
        self.assertEqual(fm["conditional_on"], [])
        self.assertEqual(fm["title"], "ratio x_i/r_i (#1 case)")
        sections = pg.split_sections(body)
        self.assertEqual(sections["statement"].strip(), "S")
        self.assertEqual(sections["derivation"].strip(), "D\n### sub\nmore")

    def test_frontmatter_absent_or_unterminated(self):
        self.assertIsNone(pg.parse_frontmatter("# heading only\n")[0])
        self.assertIsNone(pg.parse_frontmatter("---\nid: P-0001\n")[0])

    def test_registry_parser_axioms_and_conjectures(self):
        axioms = pg.parse_registry(
            "- **A-01** · stmt · status: RATIFIED 2026-09-09\n- **A-02** · stmt · status: PENDING\n"
            "## A-03 heading form\nstatus: 已批\n\n| 2026-09-09 | A-01 | pending → ratified |\n"
            "- **D-01** · defn · status: revoked 2026-09-13\n", pg.AXIOM_ENTRY_RE, pg.AXIOM_STATUS_RE)
        self.assertEqual(axioms, {"A-01": "ratified", "A-02": "pending", "A-03": "ratified", "D-01": "revoked"})
        cjs = pg.parse_registry(
            "- CJ-01 · open-economy claim · source: x · status dropped (its negation was ratified as A-05)\n"
            "- CJ-02 · s · source: y · status open\n", pg.CJ_ENTRY_RE, pg.CJ_STATUS_RE)
        self.assertEqual(cjs, {"CJ-01": "dropped", "CJ-02": "open"})

    def test_glossary_parser_tables_and_bullets(self):
        glossary = pg.parse_glossary(
            "| symbol | meaning |\n|---|---|\n| `ρ_i` | relative position |\n| x_i | consumption |\n\n"
            "- λ · shadow price\n- κ: curvature\n")
        self.assertEqual(glossary, {"ρ_i", "x_i", "λ", "κ"})

    def test_glossary_parser_escaped_pipe_and_parenthetical_notes(self):
        # A literal pipe is written \| inside a table cell; a trailing note is ignored - a full-width
        # one always, an ASCII one only after whitespace, so f(x) stays f(x).
        text = ("| symbol / term | meaning | dimension or range of values | introduced by (A-/D-/P- ID) | first occurrence |\n"
                "|---|---|---|---|---|\n"
                "| ω\\|ℓ | ω restricted to ℓ | set | P-0021 | P-0021 Statement |\n"
                "| 𝒬（可行集） | feasible set | set | P-0011 | P-0011 Statement |\n"
                "| `Θ` (type space) | types | set | A-02 | axioms.md |\n"
                "| f(x) | payoff at x | real | D-01 | axioms.md |\n")
        self.assertEqual(pg.parse_glossary(text), {"ω|ℓ", "𝒬", "Θ", "f(x)"})
        self.assertEqual(pg.glossary_entries(text)[0], ("ω|ℓ", "P-0021"))
        for raw, bare in (("ω\\|ℓ", "ω|ℓ"), ("ω|ℓ", "ω|ℓ"), ("𝒬（可行集）", "𝒬"), ("𝒬 (feasible set)", "𝒬"),
                          ("`𝒬` (feasible set):", "𝒬"), ("f(x)", "f(x)"), ("(a, b)", "(a, b)"), ("`κ`:", "κ")):
            self.assertEqual(pg.norm_symbol(raw), bare, raw)
        fm, _ = pg.parse_frontmatter("---\nglossary_introduces: [𝒬（可行集, 有限）, ω\\|ℓ]\n---\n")
        self.assertEqual([pg.norm_symbol(x) for x in fm["glossary_introduces"]], ["𝒬", "ω|ℓ"])

    def test_compute_sha_ignores_line_endings_trailing_space_and_notes(self):
        a = pg.split_sections("## Statement\nS\n## Derivation\nD\n## Notes\nN1\n")
        b = pg.split_sections("## Statement\r\nS   \r\n## Derivation\r\nD\r\n## Notes\r\nN2\r\n")
        self.assertEqual(pg.compute_sha(a), pg.compute_sha(b))
        self.assertRegex(pg.compute_sha(a), r"^[0-9a-f]{12}$")
        self.assertNotEqual(pg.compute_sha(a), pg.compute_sha(pg.split_sections("## Statement\nS2\n## Derivation\nD\n")))

    def test_forge_log_counters(self):
        counters = pg.parse_forge_log((FIXTURE_OK / T / "forge-log.md").read_text(encoding="utf-8"))
        self.assertEqual(counters, {"rounds": 2, "submitted": 7, "passed": 6})

    def test_forge_log_rounds_only_from_entry_titles(self):
        # Prose mentioning "round 4" (a Cadence line, a task description) must not count as a round;
        # only "## Round n" entry titles do. Defect 1 of the pre-release trial Forge round (2026-09-14).
        log = ("# Forge log (append-only)\n\n"
               "## Round 1 · 2026-09-10 · scope: micro\n"
               "- Deducers & tasks: deducer-1 (opus) → bridge lemma (parked since round 4 of the old plan)\n"
               "- Submitted / passed / returned: 2 / 2 / 0\n"
               "- Cadence due: rounds since macro audit 1/M=4 · next macro audit at round 4\n\n"
               "## round 2 · 2026-09-12 · scope: micro\n"
               "- Submitted / passed / returned: 1 / 0 / 1\n"
               "- Cadence due: next macro audit at round 4 · theory tribunal round 25 at the earliest\n")
        self.assertEqual(pg.parse_forge_log(log), {"rounds": 2, "submitted": 3, "passed": 2})
        self.assertEqual(pg.parse_forge_log("no entries yet; macro audit at round 4\n")["rounds"], 0)


class FixtureOkTests(unittest.TestCase):
    def test_clean(self):
        prog, violations = check(FIXTURE_OK)
        self.assertEqual([v.line() for v in violations], [])
        self.assertEqual(len(prog.nodes), 7)

    def test_root_detection_variants(self):
        expected = (FIXTURE_OK.resolve(), (FIXTURE_OK / "g2g" / "07_theory").resolve())
        for arg in (FIXTURE_OK, FIXTURE_OK / "g2g", FIXTURE_OK / "g2g" / "07_theory"):
            self.assertEqual(pg.detect_dirs(arg), expected, arg)
        with self.assertRaises(FileNotFoundError):
            pg.detect_dirs(HERE)
        self.assertEqual(run_cli(str(HERE)).returncode, pg.EXIT_USAGE)

    def test_bare_id_resolves_to_current_revision(self):
        prog, _ = check(FIXTURE_OK)
        self.assertEqual(prog.nodes["P-0004"].resolved["P-0002"].id, "P-0002.1")
        self.assertEqual(pg.closure(prog, "P-0004"), ["P-0001", "P-0002.1", "P-0003"])
        self.assertEqual(pg.resolve_ref(prog, "P-0002.1").id, "P-0002.1")
        self.assertIsNone(pg.resolve_ref(prog, "P-0002.9"))

    def test_report_theorem_closed_and_cadence(self):
        prog, violations = check(FIXTURE_OK)
        rep = pg.build_report(prog, violations)
        theorem = rep["theorems"][0]
        self.assertEqual(theorem["id"], "P-0004")
        self.assertTrue(theorem["closed"])
        self.assertEqual((theorem["closure_size"], theorem["unconditional_size"]), (3, 3))
        self.assertEqual(rep["informational"], [])
        self.assertEqual((rep["cadence"]["rounds"], rep["cadence"]["submitted"]), (2, 7))
        self.assertFalse(rep["cadence"]["forge_log_behind"])
        text = pg.render_report(rep, FIXTURE_OK)
        self.assertIn("CLOSED", text)
        self.assertNotIn("forge-log has no entry", text)

    def test_report_flags_forge_log_behind_the_nodes_on_disk(self):
        # Nodes landed but the round entry not written yet: 0 submissions / 0 passed vs 6 verified on disk.
        # Defect 12 of the pre-release trial Forge round (2026-09-14).  The cadence count is current
        # revisions only: 5, since P-0002 is historical beside P-0002.1.
        prog, violations = check(FIXTURE_OK)
        prog.forge_log = "# Forge log (append-only)\n"
        rep = pg.build_report(prog, violations)
        self.assertEqual((rep["cadence"]["submitted"], rep["cadence"]["passed"], rep["cadence"]["verified"]), (0, 0, 5))
        self.assertTrue(rep["cadence"]["forge_log_behind"])
        self.assertIn("(forge-log has no entry for the nodes on disk yet — write the round entry)",
                      pg.render_report(rep, FIXTURE_OK))

    def test_render_report_ascii_fallback(self):
        prog, violations = check(FIXTURE_OK)
        rep = pg.build_report(prog, violations)
        unicode_text = pg.render_report(rep, FIXTURE_OK)
        ascii_text = pg.render_report(rep, FIXTURE_OK, ascii_only=True)
        self.assertIn("→", unicode_text)
        for glyph, _ in pg.ASCII_FALLBACK:
            self.assertNotIn(glyph, ascii_text)
        self.assertIn("-> next macro audit", ascii_text)
        self.assertEqual(len(ascii_text.splitlines()), len(unicode_text.splitlines()))

    def test_cli_report_prints_utf8_without_pythonioencoding(self):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
        result = subprocess.run([sys.executable, str(SCRIPTS / "pg_check.py"), str(FIXTURE_OK), "--report"],
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("→ next macro audit".encode("utf-8"), result.stdout)

    def test_cli_exit_zero_and_silent(self):
        result = run_cli(str(FIXTURE_OK))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")


class FixtureBadTests(unittest.TestCase):
    def test_exact_codes(self):
        _, violations = check(FIXTURE_BAD)
        self.assertEqual(sorted((v.code, v.file) for v in violations), EXPECTED_BAD)
        self.assertEqual(set(pg.CODES), {code for code, _ in EXPECTED_BAD}, "every documented code is exercised")

    def test_closure_not_closed_is_informational_only(self):
        prog, violations = check(FIXTURE_BAD)
        rep = pg.build_report(prog, violations)
        self.assertIn("CLOSURE_NOT_CLOSED", [i["code"] for i in rep["informational"]])
        self.assertNotIn("CLOSURE_NOT_CLOSED", [v.code for v in violations])
        self.assertIn("P-0032", pg.render_report(rep, FIXTURE_BAD))

    def test_cli_exit_code_equals_line_count(self):
        result = run_cli(str(FIXTURE_BAD))
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(result.returncode, len(EXPECTED_BAD))
        self.assertEqual(len(lines), len(EXPECTED_BAD))
        self.assertEqual(sorted(tuple(line.split("  ", 2)[:2]) for line in lines), EXPECTED_BAD)

    def test_json_output(self):
        result = run_cli(str(FIXTURE_BAD), "--json", "--report")
        data = json.loads(result.stdout)
        self.assertEqual(data["violation_count"], len(EXPECTED_BAD))
        self.assertEqual(data["exit_code"], result.returncode)
        self.assertIn("CLOSURE_NOT_CLOSED", [i["code"] for i in data["report"]["informational"]])

    def test_check_only_modifies_nothing(self):
        before = {p: p.read_bytes() for p in FIXTURE_BAD.rglob("*.md")}
        run_cli(str(FIXTURE_BAD), "--report")
        self.assertEqual(before, {p: p.read_bytes() for p in FIXTURE_BAD.rglob("*.md")})


class FaithfulWithConditionTests(TempCopyMixin, unittest.TestCase):
    """3b.4, the ``conditional_on`` half: a provisional premise is not a shape present in the
    ratified axioms, so a conditional node is at least strengthened (verdict ST-03, K9)."""

    def test_conditional_node_tagged_strengthened_is_clean(self):
        prog, violations = check(FIXTURE_OK)
        self.assertEqual(prog.nodes["P-0005"].conditional_on, ["CJ-01"])
        self.assertEqual(prog.nodes["P-0005"].operationalization, "strengthened")
        self.assertEqual([v.line() for v in violations], [])

    def test_faithful_tag_on_a_conditional_node_trips_exactly_the_new_code(self):
        root = self.copy_fixture(FIXTURE_OK)
        target = root / T / "propositions" / "P-0005.md"
        target.write_text(target.read_text(encoding="utf-8").replace(
            "operationalization: strengthened", "operationalization: faithful"),
            encoding="utf-8", newline="\n")
        _, violations = check(root)
        self.assertEqual([(v.code, v.file) for v in violations],
                         [("FAITHFUL_WITH_CONDITION", T + "propositions/P-0005.md")])
        self.assertIn("CJ-01", violations[0].message)

    def test_inherited_condition_is_found_by_walking_the_closure(self):
        prog, _ = check(FIXTURE_BAD)
        node = prog.nodes["P-0036"]
        self.assertEqual(pg.closure(prog, "P-0036"), [])
        self.assertEqual(node.operationalization, "faithful")
        self.assertNotIn("FAITHFUL_WITH_SIG", [v.code for v in pg.check_conditions(prog) if v.file == node.rel])


class ExemptRevisionTests(TempCopyMixin, unittest.TestCase):
    """3b.8: the mechanical ``conditional on CJ-xx ([GUESS])`` -> ``by A-xx`` swap of 3b.9 is the
    only revision that may keep the original's V- record (verdict ST-03, K24)."""

    def test_swap_premise_keeps_a_sentence_initial_capital(self):
        self.assertEqual(pg.swap_premise("Conditional on CJ-05 ([GUESS]): x holds.", "CJ-05", "A-11"),
                         ("By A-11: x holds.", 1))
        self.assertEqual(pg.swap_premise("Step 1: conditional on CJ-05 ([GUESS]), y.", "CJ-05", "A-11"),
                         ("Step 1: by A-11, y.", 1))
        self.assertEqual(pg.swap_premise("nothing to swap here", "CJ-05", "A-11"), ("nothing to swap here", 0))

    def test_clean_swap_passes_and_an_extra_change_trips(self):
        _, violations = check(FIXTURE_BAD)
        found = {(v.code, v.file) for v in violations}
        self.assertIn(("EXEMPT_REVISION_CHANGED", T + "propositions/P-0037.1.md"), found)
        self.assertEqual([v for v in violations if v.file.endswith("P-0038.1.md")], [],
                         "the licensed swap and nothing else must trip no code")

    def test_revision_citing_a_new_record_is_not_checked_by_this_rule(self):
        # fixture_ok's P-0002.1 rewrote the Statement and cites its own V-0006: it passed the gate,
        # so it never claims the exemption and the comparison does not apply to it.
        prog, violations = check(FIXTURE_OK)
        self.assertEqual((prog.nodes["P-0002"].verification_id, prog.nodes["P-0002.1"].verification_id),
                         ("V-0002", "V-0006"))
        self.assertEqual([v.line() for v in violations], [])

    def test_same_record_without_the_licensed_swap_trips(self):
        # Point that same revision at the original's record: now the exemption is claimed, and the
        # two bodies differ by more than the licensed substitution.
        root = self.copy_fixture(FIXTURE_OK)
        target = root / T / "propositions" / "P-0002.1.md"
        target.write_text(target.read_text(encoding="utf-8").replace(
            "verification: V-0006 (pass, 2026-09-12)", "verification: V-0002 (pass, 2026-09-10)"),
            encoding="utf-8", newline="\n")
        _, violations = check(root)
        self.assertEqual([(v.code, v.file) for v in violations],
                         [("EXEMPT_REVISION_CHANGED", T + "propositions/P-0002.1.md")])


class RegenIndexTests(TempCopyMixin, unittest.TestCase):
    def test_regen_index_rows_and_idempotence(self):
        root = self.copy_fixture(FIXTURE_OK)
        index = root / T / "graph-index.md"
        index.write_text("stale\n", encoding="utf-8")
        first = run_cli(str(root), "--regen-index")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("written", first.stderr)
        text = index.read_text(encoding="utf-8")
        self.assertIn("| " + " | ".join(pg.INDEX_COLUMNS) + " |", text)
        rows = [line for line in text.splitlines() if line.startswith("| P-")]
        self.assertEqual([row.split(" | ")[0][2:] for row in rows],
                         ["P-0001", "P-0002", "P-0002.1", "P-0003", "P-0004", "P-0005", "P-0006"])
        self.assertIn("| P-0004 | Under the relative-position shape, any consumption gain that raises ρ_i raises "
                      "utility | theorem | verified | untested | P-0002, P-0003 | A-01, A-02, D-01 | V-0004 | micro |", text)
        second = run_cli(str(root), "--regen-index")
        self.assertIn("unchanged", second.stderr)
        self.assertEqual(index.read_text(encoding="utf-8"), text)
        self.assertEqual(text, (FIXTURE_OK / T / "graph-index.md").read_text(encoding="utf-8"))


class FillShaTests(TempCopyMixin, unittest.TestCase):
    def test_fill_sha_round_trip_and_idempotence(self):
        root = self.copy_fixture(FIXTURE_OK)
        props = root / T / "propositions"
        originals = {p.name: p.read_bytes() for p in props.glob("*.md")}
        for p in props.glob("*.md"):
            kept = [l for l in p.read_text(encoding="utf-8").splitlines() if not l.startswith("content_sha:")]
            p.write_text("\n".join(kept) + "\n", encoding="utf-8", newline="\n")
        _, violations = check(root)
        self.assertEqual(sorted(v.code for v in violations), ["MISSING_SHA"] * 6)
        first = run_cli(str(root), "--fill-sha")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn("6 file(s) updated", first.stderr)
        self.assertEqual({p.name: p.read_bytes() for p in props.glob("*.md")}, originals)
        second = run_cli(str(root), "--fill-sha")
        self.assertIn("0 file(s) updated", second.stderr)
        self.assertEqual({p.name: p.read_bytes() for p in props.glob("*.md")}, originals)

    def test_stale_sha_detected_then_refreshed_keeping_crlf(self):
        root = self.copy_fixture(FIXTURE_OK)
        target = root / T / "propositions" / "P-0003.md"
        edited = target.read_text(encoding="utf-8").replace("Step 3: by A-02", "Step 3: by axiom A-02")
        with open(target, "w", encoding="utf-8", newline="") as fh:
            fh.write(edited.replace("\n", "\r\n"))
        _, violations = check(root)
        self.assertEqual([(v.code, v.file) for v in violations], [("STALE_SHA", T + "propositions/P-0003.md")])
        self.assertEqual(run_cli(str(root), "--fill-sha").returncode, 0)
        raw = target.read_bytes()
        self.assertIn(b"\r\ncontent_sha: ", raw)
        self.assertNotIn(b"\n\n\n", raw.replace(b"\r\n", b"\n"))
        self.assertEqual(check(root)[1], [])


#: A fictional candidate for the pre-gate tests (written into a temporary copy of fixture_ok).
CANDIDATE = """---
id: {nid}
title: Fictional pre-gate candidate {nid}
kind: lemma
status: proposed
empirical_status: untested
layer: micro
scope: P-0004
predecessors: [P-0004]
axioms_used: [A-01, A-02]
definitions_used: [D-01]
assumptions_used: []
external_refs: []
conditional_on: []
glossary_introduces: [{introduces}]
operationalization: strengthened
markers: [SIG]
interp_pending: []
verification:
supersedes:
revision_of: {revision_of}
revoked_by:
content_sha:
submitted_by: deducer-1 · round 3 · 2026-09-14
---
## Statement
{statement}

## Derivation
{derivation}

## Falsification surface
Fixture text.

## Notes
Fictional node for the pre-gate tests.
"""


class PregateTests(TempCopyMixin, unittest.TestCase):
    """``--pregate``: the registration check run on named candidates before each verifier."""

    def setUp(self):
        self.root = self.copy_fixture(FIXTURE_OK)

    def add(self, nid: str, introduces: str = "", statement: str = "A fictional statement.",
            derivation: str = "Step 1: by P-0004.", revision_of: str = "") -> None:
        (self.root / T / "candidates" / f"{nid}.md").write_text(
            CANDIDATE.format(nid=nid, introduces=introduces, statement=statement, derivation=derivation,
                             revision_of=revision_of), encoding="utf-8", newline="\n")

    def add_glossary_row(self, row: str) -> None:
        glossary = self.root / T / "glossary.md"
        glossary.write_text(glossary.read_text(encoding="utf-8") + row + "\n", encoding="utf-8", newline="\n")

    def codes(self, nid: str) -> list[str]:
        prog, _ = check(self.root)
        return [v.code for v in pg.pregate(prog, prog.nodes[nid])]

    def test_codes_stay_out_of_the_default_run(self):
        self.assertFalse(set(pg.PREGATE_CODES) & set(pg.CODES))
        self.assertIn("DANGLING_FIELD", pg.INFO_CODES)
        self.assertEqual(self.codes("P-0006"), [])  # fixture_ok's returned candidate lists the κ it defines
        self.add("P-0007", statement="Let θ := ρ_i / 2. We call ρ_i ≥ 1 the **upper band**.")
        self.assertEqual(check(self.root)[1], [], "candidates stay exempt at round start")

    def test_collision_with_another_familys_symbol(self):
        self.add("P-0007", introduces="ρ_i")  # ρ_i is registered, introduced by P-0001
        self.assertEqual(self.codes("P-0007"), ["SYMBOL_COLLISION"])

    def test_a_revision_relisting_its_own_familys_symbol_is_exempt(self):
        self.add("P-0001.1", introduces="ρ_i", revision_of="P-0001 · mechanical",
                 statement="The relative position **ρ_i** := x_i / r_i, restated in the new wording.")
        self.assertEqual(self.codes("P-0001.1"), [])

    def test_colon_equals_unlisted_then_listed(self):
        self.add("P-0007", statement="Let θ := ρ_i / 2 (half the position).")
        prog, _ = check(self.root)
        findings = pg.pregate(prog, prog.nodes["P-0007"])
        self.assertEqual([v.code for v in findings], ["UNLISTED_DEFINITION"])
        self.assertIn("θ", findings[0].message)
        self.add("P-0007", introduces="θ", statement="Let θ := ρ_i / 2 (half the position).")
        self.assertEqual(self.codes("P-0007"), [])

    def test_function_definition_counts_for_its_name(self):
        self.add("P-0007", introduces="g", derivation="Step 1: g(ρ) := ρ / 2 for ρ ≥ 0, by P-0004.")
        self.assertEqual(self.codes("P-0007"), [])

    def test_bold_unlisted_and_unregistered(self):
        self.add("P-0007", derivation="Step 1: we call ρ_i ≥ 1 the **upper band**, by P-0004.")
        self.assertEqual(self.codes("P-0007"), ["UNLISTED_DEFINITION"])

    def test_bold_registered_by_another_family_collides_same_family_does_not(self):
        self.add_glossary_row("| comfort band | the range 1/2 ≤ ρ_i ≤ 1 | interval | P-0003 | P-0003 Notes |")
        self.add("P-0007", statement="On the **comfort band** utility is flat.")
        self.assertEqual(self.codes("P-0007"), ["SYMBOL_COLLISION"])
        self.add("P-0003.1", revision_of="P-0003 · mechanical", statement="On the **comfort band** V' > 0.")
        self.assertEqual(self.codes("P-0003.1"), [])

    def test_order_derivatives_unlisted_then_listed(self):
        text = "For bundles a, b let a ≼_c b mean ρ(a) ≤ ρ(b); a ≺_c b is its strict part and b ≽_c a its inverse."
        self.add("P-0007", introduces="≼_c", statement=text)
        prog, _ = check(self.root)
        findings = pg.pregate(prog, prog.nodes["P-0007"])
        self.assertEqual(sorted(v.message.split()[0] for v in findings), ["≺_c", "≽_c"])
        self.assertEqual({v.code for v in findings}, {"UNLISTED_ORDER_DERIVATIVE"})
        self.add("P-0007", introduces="≼_c, ≺_c, ≽_c", statement=text)
        self.assertEqual(self.codes("P-0007"), [])

    def test_escaped_pipe_row_is_matched_by_both_spellings(self):
        self.add_glossary_row("| ω\\|ℓ | ω restricted to ℓ | set | P-0003 | P-0003 Notes |")
        prog, _ = check(self.root)
        self.assertIn("ω|ℓ", prog.glossary)
        self.add("P-0007", introduces="ω|ℓ")
        self.add("P-0008", introduces="ω\\|ℓ")
        self.assertEqual(self.codes("P-0007"), ["SYMBOL_COLLISION"])
        self.assertEqual(self.codes("P-0008"), ["SYMBOL_COLLISION"])

    def test_parenthetical_notes_and_function_notation(self):
        self.add_glossary_row("| 𝒬 | feasible set | set | P-0003 | P-0003 Notes |")
        self.add_glossary_row("| f | payoff | real | P-0003 | P-0003 Notes |")
        self.add("P-0007", introduces="𝒬（可行集）")
        self.add("P-0008", introduces="𝒬 (feasible set)")
        self.add("P-0009", introduces="f(x)")  # f(x) stays f(x): not the registered f
        self.assertEqual(self.codes("P-0007"), ["SYMBOL_COLLISION"])
        self.assertEqual(self.codes("P-0008"), ["SYMBOL_COLLISION"])
        self.assertEqual(self.codes("P-0009"), [])

    def test_cli_exit_code_json_and_errors(self):
        self.add("P-0007", introduces="ρ_i", statement="Let θ := ρ_i / 2.")      # 2 findings
        self.add("P-0008", derivation="Step 1: the **upper band**, by P-0004.")  # 1 finding
        result = run_cli(str(self.root), "--pregate", "P-0007", "P-0008")
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual((result.returncode, len(lines)), (3, 3), result.stderr)
        self.assertEqual(sorted(line.split("  ", 2)[0] for line in lines),
                         ["SYMBOL_COLLISION", "UNLISTED_DEFINITION", "UNLISTED_DEFINITION"])
        data = json.loads(run_cli(str(self.root), "--pregate", "P-0007", "--json").stdout)
        self.assertEqual(set(data), {"version", "programme_root", "theory_dir", "pregate", "findings",
                                     "finding_count", "exit_code"})
        self.assertEqual((data["pregate"], data["finding_count"], data["exit_code"]), (["P-0007"], 2, 2))
        self.assertEqual(set(data["findings"][0]), {"code", "file", "message"})
        self.assertEqual(run_cli(str(self.root), "--pregate", "P-0006").returncode, 0)
        for bad in (["--pregate", "P-0099"], ["--pregate", "P-0004"], ["--pregate", "P-0006", "--report"]):
            result = run_cli(str(self.root), *bad)
            self.assertEqual(result.returncode, pg.EXIT_USAGE, bad)
            self.assertEqual(result.stdout.strip(), "", bad)

    def test_console_fallback_never_raises(self):
        # A console that could not be switched to UTF-8 gets ASCII glyphs and "?" for what its code page lacks.
        with mock.patch.object(sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="cp1252")):
            self.assertEqual(pg._console_safe("ω|ℓ — x · y", False), "?|? - x , y")
        self.assertEqual(pg._console_safe("ω|ℓ — x", True), "ω|ℓ — x")


class DanglingFieldTests(TempCopyMixin, unittest.TestCase):
    """Informational DANGLING_FIELD: ``revision_of`` / ``supersedes`` naming no node."""

    def test_fields_naming_no_node_are_reported_not_counted(self):
        root = self.copy_fixture(FIXTURE_OK)
        rev = root / T / "propositions" / "P-0002.1.md"
        rev.write_text(rev.read_text(encoding="utf-8").replace("revision_of: P-0002", "revision_of: P-0098"),
                       encoding="utf-8", newline="\n")
        cand = root / T / "candidates" / "P-0006.md"
        cand.write_text(cand.read_text(encoding="utf-8").replace("supersedes:\n", "supersedes: P-0099\n"),
                        encoding="utf-8", newline="\n")
        prog, violations = check(root)
        self.assertEqual(violations, [])
        info = [(i["code"], i["file"], i["message"]) for i in pg.build_report(prog, violations)["informational"]]
        self.assertEqual(info, [("DANGLING_FIELD", T + "propositions/P-0002.1.md", "revision_of P-0098 names no node"),
                                ("DANGLING_FIELD", T + "candidates/P-0006.md", "supersedes P-0099 names no node")])

    def test_a_revision_does_not_name_its_own_family_by_itself(self):
        root = self.copy_fixture(FIXTURE_OK)
        src = (root / T / "propositions" / "P-0002.1.md").read_text(encoding="utf-8")
        (root / T / "propositions" / "P-0002.md").unlink()
        prog, violations = check(root)
        info = [i["code"] for i in pg.build_report(prog, violations)["informational"]]
        self.assertIn("revision_of: P-0002", src)
        self.assertIn("DANGLING_FIELD", info)


class ReasonCategoryTests(TempCopyMixin, unittest.TestCase):
    """Reason categories of revocations and revisions (category first in ``revoked_by``, after the
    ID in ``revision_of``); a value without one counts as uncategorised; gate misses on their own line."""

    def node(self, revoked_by: str = "", revision_of: str = "") -> pg.Node:
        fm, body = pg.parse_frontmatter(f"---\nid: P-0009\nkind: lemma\nstatus: revoked\npredecessors: []\n"
                                        f"revoked_by: {revoked_by}\nrevision_of: {revision_of}\n---\n## Statement\nS\n")
        return pg.make_node(Path("P-0009.md"), "P-0009.md", "propositions", fm, body)

    def test_parsing(self):
        self.assertEqual(self.node("cascade · predecessor P-0003 revoked · 2026-10-01").revoked_category, "cascade")
        self.assertEqual(self.node("gate-miss · TT-02 counterexample · 2026-10-02").revoked_category, "gate-miss")
        self.assertEqual(self.node("A-08 revoked · 2026-09-13").revoked_category, "")
        self.assertEqual(self.node("algebra slip (a mechanical error) · 2026-11-01").revoked_category, "")
        self.assertEqual(self.node(revision_of="P-0004 (fixes the cascade note)").revision_category, "")
        rev = self.node(revision_of="P-0004 · human-ruling")
        self.assertEqual((rev.revision_of, rev.revision_category), ("P-0004", "human-ruling"))
        self.assertEqual(self.node(revision_of="P-0004").revision_category, "")

    def test_report_counts(self):
        prog, violations = check(FIXTURE_OK)
        reasons = pg.build_report(prog, violations)["reasons"]
        self.assertEqual(reasons, {"revocations": {}, "revisions": {"uncategorised": 1}, "gate_misses": 0})
        root = self.copy_fixture(FIXTURE_OK)
        rev = root / T / "propositions" / "P-0002.1.md"
        rev.write_text(rev.read_text(encoding="utf-8").replace("revision_of: P-0002", "revision_of: P-0002 · gate-miss"),
                       encoding="utf-8", newline="\n")
        node = root / T / "propositions" / "P-0005.md"
        node.write_text(node.read_text(encoding="utf-8").replace("status: verified", "status: revoked").replace(
            "revoked_by:\n", "revoked_by: human-ruling · the human replaced the premise · 2026-09-14\n"),
            encoding="utf-8", newline="\n")
        prog, violations = check(root)
        self.assertEqual(violations, [])
        rep = pg.build_report(prog, violations)
        self.assertEqual(rep["reasons"], {"revocations": {"human-ruling": 1}, "revisions": {"gate-miss": 1},
                                          "gate_misses": 1})
        text = pg.render_report(rep, root)
        for line in ("revocations by reason: human-ruling 1", "revisions by reason: gate-miss 1",
                     "gate misses (revocations and revisions): 1"):
            self.assertIn(line, text)


class VersionSplitTests(TempCopyMixin, unittest.TestCase):
    """Status counts split into current revisions (what a bare ID resolves to) and historical ones;
    the theory-tribunal hint counts current verified nodes."""

    def test_fixture_ok_split(self):
        prog, violations = check(FIXTURE_OK)
        rep = pg.build_report(prog, violations)
        self.assertEqual(rep["status"], {"current": {"proposed": 1, "verified": 5}, "historical": {"verified": 1}})
        self.assertEqual((rep["cadence"]["verified"], rep["cadence"]["next_theory_tribunal_at"]), (5, 25))
        text = pg.render_report(rep, FIXTURE_OK)
        self.assertIn("status (historical revisions): verified 1", text)
        self.assertIn("verified nodes (current revisions) 5 → next theory tribunal at 25", text)
        root = self.copy_fixture(FIXTURE_OK)  # a revision still under the gate is not history
        (root / T / "candidates" / "P-0003.1.md").write_text(
            (root / T / "propositions" / "P-0003.md").read_text(encoding="utf-8").replace("id: P-0003\n", "id: P-0003.1\n")
            .replace("status: verified", "status: proposed").replace("revision_of:\n", "revision_of: P-0003 · mechanical\n"),
            encoding="utf-8", newline="\n")
        prog, violations = check(root)
        self.assertEqual(pg.build_report(prog, violations)["status"],
                         {"current": {"proposed": 2, "verified": 5}, "historical": {"verified": 1}})

    def test_scope_mismatch_message_names_the_target_theorem_id(self):
        root = self.copy_fixture(FIXTURE_OK)
        node = root / T / "propositions" / "P-0001.md"
        node.write_text(node.read_text(encoding="utf-8").replace("scope: P-0004", "scope: micro layer"),
                        encoding="utf-8", newline="\n")
        prog, violations = check(root)
        info = [i for i in pg.build_report(prog, violations)["informational"] if i["code"] == "SCOPE_MISMATCH"]
        self.assertEqual(len(info), 1)
        self.assertIn("whose scope holds this target theorem's ID P-0004", info[0]["message"])

    def test_a_revised_target_theorem_is_listed_once_and_bare_scopes_resolve_to_it(self):
        root = self.copy_fixture(FIXTURE_OK)
        props, vrecs = root / T / "propositions", root / T / "verifications"
        (props / "P-0004.1.md").write_text((props / "P-0004.md").read_text(encoding="utf-8").replace(
            "id: P-0004\n", "id: P-0004.1\n").replace("V-0004 (pass", "V-0008 (pass").replace(
            "revision_of:\n", "revision_of: P-0004 · gate-miss\n"), encoding="utf-8", newline="\n")
        (vrecs / "V-0008.md").write_text((vrecs / "V-0004.md").read_text(encoding="utf-8").replace(
            "id: V-0004", "id: V-0008").replace("candidate: P-0004 ", "candidate: P-0004.1 "),
            encoding="utf-8", newline="\n")
        prog, violations = check(root)
        rep = pg.build_report(prog, violations)
        self.assertEqual((violations, [t["id"] for t in rep["theorems"]]), ([], ["P-0004.1"]))
        self.assertNotIn("SCOPE_MISMATCH", [i["code"] for i in rep["informational"]])


if __name__ == "__main__":
    unittest.main()
