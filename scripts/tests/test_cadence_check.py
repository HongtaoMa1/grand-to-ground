"""Unit tests for scripts/cadence_check.py (the cycle-mode cadence check).

Run from the plugin root:  python -m pytest -q scripts/tests

All three fixtures are fictional workspaces without 07_theory/:
fixture_cadence_steer/  - tag-form seed rows; M = 3 in the charter; cycle #4 logged twice (paused,
                          then resumed); the last 3 questions came from salvage or an earlier card
fixture_cadence_mixed/  - no macro-audit line (M = 4 by default); English and Chinese legacy
                          markers, a row without a marker, a queue tag, a question with no seed row
fixture_cadence_legacy/ - rows written before the tag, salvage markers only; M = {4} placeholder
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
import cadence_check as cc  # noqa: E402

STEER = HERE / "fixture_cadence_steer"
MIXED = HERE / "fixture_cadence_mixed"
LEGACY = HERE / "fixture_cadence_legacy"


def run(workspace: Path, m: int | None = None) -> dict:
    return cc.check(cc.detect_workspace(workspace), m)


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, str(SCRIPTS / "cadence_check.py"), *args], capture_output=True,
                          env=env if env is not None else {**os.environ, "PYTHONIOENCODING": "utf-8"})


class TempCopyMixin:
    def copy_fixture(self, src: Path) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="cadence_check_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        dst = tmp / src.name
        shutil.copytree(src, dst)
        return dst


class ParserTests(unittest.TestCase):
    def test_tag_form(self):
        for row, expected in (("- S3 seed [source: salvage]", (cc.SALVAGE, "[source: salvage]")),
                              ("- S4 seed [source: card C-012]", (cc.SALVAGE, "[source: card C-012]")),
                              ("- S5 seed [Source: Queue]", (cc.NOT_SALVAGE, "[Source: Queue]")),
                              ("- S6 seed [source: plan]", (cc.NOT_SALVAGE, "[source: plan]")),
                              ("- S7 seed [source: vision]", (cc.NOT_SALVAGE, "[source: vision]")),
                              ("- S8 seed [source: tribunal]", (cc.UNKNOWN, "unrecognised [source: tribunal]"))):
            self.assertEqual(cc.classify([row]), expected, row)

    def test_english_and_chinese_legacy_markers(self):
        for row, marker in (("- S1 seed (parent: C-001)", "parent:"), ("- S2 种子（父：C-001）", "父："),
                            ("- S3 seed SALVAGE from cycle #02", "SALVAGE"), ("- S4 种子（第 3 轮打捞）", "打捞")):
            self.assertEqual(cc.classify([row]), (cc.SALVAGE, marker), row)

    def test_unknown_rows_are_never_salvage(self):
        self.assertEqual(cc.classify([]), (cc.UNKNOWN, "no seed row"))
        for row in ("- S5 a plain seed", "- S6 the salvage value of a ship", "- S7 a transparent: rule",
                    "- S8 [来源: 队列]"):
            self.assertEqual(cc.classify([row])[0], cc.UNKNOWN, row)

    def test_seed_rows_match_the_whole_id(self):
        registry = "- S1 first (parent: C-001)\n- S10 tenth [source: queue]\n| S1 | table row | x |\n"
        self.assertEqual(cc.seed_rows(registry, "S1"), ["- S1 first (parent: C-001)", "| S1 | table row | x |"])
        self.assertEqual(cc.seed_rows(registry, "S10"), ["- S10 tenth [source: queue]"])

    def test_charter_m(self):
        self.assertEqual(cc.charter_m("Forge cadence — control beat every K = 10 · macro audit every M = 6 rounds"), 6)
        self.assertEqual(cc.charter_m("· macro audit every M = {4} rounds or cycles ·"), 4)
        self.assertIsNone(cc.charter_m("## Programme modes\nmodes: cycle\n"))
        self.assertIsNone(cc.charter_m("macro audit every M = 0 rounds"))

    def test_cycle_lines_and_duplicates(self):
        log = ("## entry\nCYCLE #1 · question S1 · severity exploratory\n"
               "## entry\nCYCLE #2 · question S2 · verdict: paused\n"
               "## entry\nRUN open · 2026-09-09 10:00 · launch instruction: none\nresume: landed CYCLE #2 card\n"
               "## entry\nCYCLE #2 · question S2 · verdict: alive 1\n"
               "## entry\n**CYCLE #3** · question `S7` · severity standard\n")
        self.assertEqual(cc.logged_cycles(log), [(1, "S1"), (2, "S2"), (3, "S7")])


class FixtureTests(unittest.TestCase):
    def test_all_salvage_or_card_steers_with_m_from_the_charter(self):
        result = run(STEER)
        self.assertEqual((result["m"], result["m_from"], result["cycles_logged"]), (3, "charter", 5))
        self.assertEqual(result["verdict"], "steer")
        self.assertEqual([(q["cycle"], q["question"]) for q in result["questions"]], [(3, "S3"), (4, "S4"), (5, "S5")])
        self.assertEqual(result["exit_code"], cc.EXIT_STEER)
        self.assertTrue(result["line"].startswith("Cadence (M = 3): the last 3 questions all came from salvage"))

    def test_mixed_does_not_steer_and_gives_the_split(self):
        result = run(MIXED)
        self.assertEqual((result["m"], result["m_from"]), (4, "default"))
        self.assertEqual(result["verdict"], "no steer")
        self.assertEqual(result["counts"], {"salvage": 2, "not_salvage": 1, "unknown": 1})
        self.assertIn("(salvage or cards 2 · queue, plan or Vision 1 · source unknown 1) — no steer.", result["line"])
        self.assertEqual(result["exit_code"], cc.EXIT_NO_STEER)

    def test_every_question_has_its_evidence(self):
        result = run(MIXED, m=7)
        self.assertEqual([(q["question"], q["class"], q["evidence"]) for q in result["questions"]],
                         [("S1", cc.SALVAGE, "parent:"), ("S2", cc.SALVAGE, "父："), ("S9", cc.UNKNOWN, "no seed row"),
                          ("S3", cc.SALVAGE, "SALVAGE"), ("S4", cc.SALVAGE, "打捞"),
                          ("S5", cc.UNKNOWN, "no source marker"), ("S6", cc.NOT_SALVAGE, "[source: queue]")])

    def test_legacy_rows_only_and_placeholder_m(self):
        result = run(LEGACY)
        self.assertEqual((result["m"], result["m_from"], result["verdict"]), (4, "charter", "steer"))
        self.assertEqual(run(LEGACY, m=5)["verdict"], "no steer")  # S1 has no marker: unknown, not salvage

    def test_fewer_than_m_cycles_gives_no_verdict(self):
        result = run(STEER, m=6)
        self.assertEqual((result["verdict"], result["exit_code"]), ("no verdict", cc.EXIT_NO_STEER))
        self.assertEqual(result["line"], "Cadence (M = 6): 5 cycle(s) in the log, fewer than M — no verdict.")
        self.assertEqual(len(result["questions"]), 5)

    def test_no_theory_folder_needed(self):
        for fixture in (STEER, MIXED, LEGACY):
            self.assertFalse((fixture / "g2g" / "07_theory").exists())
        self.assertEqual(cc.detect_workspace(STEER), cc.detect_workspace(STEER / "g2g"))


class FileTests(TempCopyMixin, unittest.TestCase):
    def test_m_defaults_to_4_without_a_charter(self):
        root = self.copy_fixture(STEER)
        (root / "g2g" / "00_programme.md").unlink()
        result = run(root)
        self.assertEqual((result["m"], result["m_from"]), (4, "default"))
        self.assertEqual(result["verdict"], "no steer")  # the window now reaches S2 (plan)

    def test_crlf_and_bom(self):
        root = self.copy_fixture(MIXED)
        for path in (root / "g2g").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            path.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
        expected = run(MIXED, m=7)
        self.assertEqual({k: v for k, v in run(root, m=7).items() if k != "workspace"},
                         {k: v for k, v in expected.items() if k != "workspace"})
        charter = root / "g2g" / "00_programme.md"
        charter.write_bytes(b"\xef\xbb\xbf# Charter\r\nmacro audit every M = 2 rounds or cycles\r\n")
        self.assertEqual((run(root)["m"], run(root)["verdict"]), (2, "no steer"))

    def test_missing_files_are_io_errors(self):
        self.assertEqual(run_cli(str(HERE)).returncode, cc.EXIT_USAGE)
        root = self.copy_fixture(STEER)
        (root / "g2g" / "02_question-registry.md").unlink()
        result = run_cli(str(root))
        self.assertEqual((result.returncode, result.stdout), (cc.EXIT_USAGE, b""))
        self.assertIn(b"error:", result.stderr)

    def test_nothing_is_written(self):
        before = {p: p.read_bytes() for p in STEER.rglob("*") if p.is_file()}
        run_cli(str(STEER))
        self.assertEqual(before, {p: p.read_bytes() for p in STEER.rglob("*") if p.is_file()})


class CliTests(unittest.TestCase):
    def test_text_output_and_exit_codes(self):
        result = run_cli(str(STEER))
        self.assertEqual(result.returncode, cc.EXIT_STEER, result.stderr)
        lines = result.stdout.decode("utf-8").splitlines()
        self.assertEqual(lines[0], run(STEER)["line"])
        self.assertEqual(lines[1:], ["  #3 · S3 · salvage or earlier card · [source: salvage]",
                                     "  #4 · S4 · salvage or earlier card · [source: card C-003]",
                                     "  #5 · S5 · salvage or earlier card · [source: salvage]"])
        self.assertFalse(cc.CYCLE_RE.search(result.stdout.decode("utf-8")), "a copied line must not read as a cycle")
        self.assertEqual(run_cli(str(MIXED / "g2g")).returncode, cc.EXIT_NO_STEER)
        self.assertEqual(run_cli(str(STEER), "--m", "0").returncode, cc.EXIT_USAGE)

    def test_json(self):
        result = run_cli(str(MIXED), "--json")
        data = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(set(data), {"version", "workspace", "m", "m_from", "cycles_logged", "verdict", "line",
                                     "counts", "questions", "exit_code"})
        self.assertEqual((data["verdict"], data["exit_code"], result.returncode), ("no steer", 0, 0))
        self.assertEqual(set(data["questions"][0]), {"cycle", "question", "class", "evidence"})

    def test_utf8_without_pythonioencoding(self):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
        result = run_cli(str(MIXED), "--m", "7", env=env)
        self.assertEqual(result.returncode, cc.EXIT_NO_STEER, result.stderr)
        self.assertIn("· 父：".encode("utf-8"), result.stdout)

    def test_console_fallback_never_raises(self):
        # A console that could not be switched to UTF-8 gets ASCII glyphs and "?" for what its code page lacks.
        with mock.patch.object(sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="cp1252")):
            self.assertEqual(cc._console_safe("#2 · S2 · 父： — no steer", False), "#2 , S2 , ?? - no steer")


if __name__ == "__main__":
    unittest.main()
