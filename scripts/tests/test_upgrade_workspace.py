"""Unit tests for scripts/upgrade_workspace.py (the G2G 0.3.0 -> 0.4.0 settings upgrade).

Run from the plugin root:  python -m pytest -q scripts/tests

All fixtures are fictional workspaces; every test that writes works on a temporary copy.
fixture_upgrade_en/           - an English 0.3.0 workspace filled from the 0.3.0 templates: charter, 01 and 06,
                                plus 02 and 04, which the upgrade must not touch; expected/ holds the upgraded
                                00, 01 and 06
fixture_upgrade_zh/           - a Chinese 0.3.0 workspace: the plugin's Chinese tiering table (rows reordered,
                                one changed cell kept, one kept cell that conflicts), localized tier-move
                                sentences (one already struck, one a prohibition), the localized D.3 rows and U
                                title, no fence paragraph, a translated 06
fixture_upgrade_unrecognised/ - forms the script does not recognise (an extra tier row, a tier sentence without a
                                quota word, another fence paragraph, another budget row, another U title); only
                                the period_share row is recognised
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
TEMPLATES = SCRIPTS.parent / "skills" / "g2g-setup" / "references" / "templates.md"
sys.path.insert(0, str(SCRIPTS))
import upgrade_workspace as uw  # noqa: E402

EN = HERE / "fixture_upgrade_en"
ZH = HERE / "fixture_upgrade_zh"
UNRECOGNISED = HERE / "fixture_upgrade_unrecognised"
UPGRADED = ("00_programme.md", "01_hard-core.md", "06_process-defects.md")
BACKUPS = ("00_programme.v0.3.0.md", "01_hard-core.v0.3.0.md", "06_process-defects.v0.3.0.md")


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, str(SCRIPTS / "upgrade_workspace.py"), *args], capture_output=True,
                          env=env if env is not None else {**os.environ, "PYTHONIOENCODING": "utf-8"})


def files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TempMixin:
    def copy_fixture(self, src: Path) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="upgrade_workspace_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(src / "g2g", tmp / "g2g")
        return tmp

    def workspace(self, charter: str, **others: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="upgrade_workspace_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "g2g").mkdir()
        (tmp / "g2g" / uw.CHARTER).write_text(charter, encoding="utf-8", newline="\n")
        for name, body in others.items():
            (tmp / "g2g" / name).write_text(body, encoding="utf-8", newline="\n")
        return tmp / "g2g"


def old_charter(table: list[str], rules: str = uw.OLD_TIER_RULES) -> str:
    return "# Charter\n**Methodology:** G2G v3.0\n\n## Model tiering\n" + "\n".join(table) + f"\n\n{rules}\n\n## Device gate\ndevice_gate: none\n"


class ConstantTests(unittest.TestCase):
    def test_inserted_blocks_are_the_templates_text(self):
        templates = TEMPLATES.read_text(encoding="utf-8").replace("\r\n", "\n")
        for name, block in (("T1", "\n".join(uw.NEW_U)), ("T2", "\n".join(uw.NEW_TIER_BLOCK)),
                            ("T3", uw.NEW_FENCE), ("T4", "\n".join(uw.NEW_D3_ROWS))):
            self.assertIn(block, templates, f"{name} differs from templates.md")
        self.assertTrue(uw.NEW_FENCE.startswith(uw.NEW_FENCE_PREFIX))

    def test_old_forms_are_gone_from_the_templates(self):
        templates = TEMPLATES.read_text(encoding="utf-8").replace("\r\n", "\n")
        for old in (uw.OLD_TIER_RULES, uw.OLD_FENCE_PREFIX, uw.OLD_U_TITLE, *uw.OLD_BUDGET_ROWS, *uw.OLD_D3_ROWS,
                    *uw.OLD_SEEDED_RULES):
            self.assertNotIn(old, templates)

    def test_the_english_fixture_carries_the_0_3_0_forms(self):
        fixture = "\n".join(text(EN / "g2g" / name) for name in UPGRADED)
        for old in ("\n".join(uw.OLD_TIER_TABLE) + "\n\n" + uw.OLD_TIER_RULES, uw.OLD_BUDGET_ROWS[1], uw.OLD_FENCE,
                    "\n".join(uw.OLD_D3_ROWS[:2]), uw.OLD_U_TITLE, "\n".join(uw.OLD_SEEDED_RULES[:4]),
                    "\n".join(uw.OLD_SEEDED_RULES[4:])):
            self.assertIn(old, fixture)
        self.assertTrue(uw.OLD_FENCE.startswith(uw.OLD_FENCE_PREFIX))

    def test_roles(self):
        roles = [role for role, _, _ in uw.NEW_ROWS]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertLessEqual(set(uw.OLD_DEFAULTS), set(roles))
        self.assertEqual(uw.OLD_DEFAULTS["deducer"], ("opus", "inherit", "inherit"))
        self.assertEqual(uw.OLD_DEFAULTS["defender"], ("—", "opus", "inherit"))
        for cell, role in (("演绎者", "deducer"), ("**验证者（闸门）**", "verifier"), ("事实警察 / 查重警察", "evidence"),
                           ("辩护人", "defender"), ("Deducer — new derivation", "deducer"), ("Archive scout", None)):
            self.assertEqual(uw.role_of(cell), role, cell)
        for cell, value in (("**继承**", "inherit"), ("次强档", "opus"), ("next-strongest tier", "opus"),
                            ("—（探索档无独立辩护）", "—"), ("custom", "custom"), ("强", None), ("1", None)):
            self.assertEqual(uw.canon(cell), value, cell)


class StrikeTests(unittest.TestCase):
    def assert_struck(self, line: str, clause: str):
        new, n, loose = uw.strike(line)
        self.assertEqual((n, loose), (1, []), line)
        self.assertEqual(new, line.replace(clause, f"~~{clause}~~{uw.VOID_NOTE}"))

    def test_the_0_3_0_english_sentences(self):
        for line, clause in (
                (uw.OLD_TIER_RULES, "The orchestrator may move an individual agent one tier up or down from this table "
                                    "according to task difficulty and remaining budget"),
                ('"next-strongest tier" = one tier below it. The orchestrator may move an individual agent one tier up '
                 "or down from the table according to task difficulty and remaining budget; **the gate may not go below "
                 "the table**.", "The orchestrator may move an individual agent one tier up or down from the table "
                                 "according to task difficulty and remaining budget"),
                ("The orchestrator may move an individual agent one tier up or down for task difficulty or remaining "
                 "budget — **the verifier never goes below `inherit`**.", "The orchestrator may move an individual "
                 "agent one tier up or down for task difficulty or remaining budget"),
                ("- **Model** per the tiering table. You may move one deducer one tier up or down for task difficulty "
                 "or remaining budget.", "You may move one deducer one tier up or down for task difficulty or "
                 "remaining budget"),
                ("Two rules are not negotiable: the gate may not be set below `inherit`, and the orchestrator may later "
                 "move an individual agent one tier up or down by task difficulty and remaining budget — the gate "
                 "excepted.", "and the orchestrator may later move an individual agent one tier up or down by task "
                 "difficulty and remaining budget")):
            self.assert_struck(line, clause)

    def test_localized_sentences(self):
        for line, clause in (
                ("编排者可按任务难度与预算余量把单个代理在表的上下各调一档，**闸门不得低于表**。",
                 "编排者可按任务难度与预算余量把单个代理在表的上下各调一档"),
                ("编排者可视难度与余额将某个代理上下调一档，闸门不低于本表。", "编排者可视难度与余额将某个代理上下调一档"),
                ("- 协调者也可视任务难度和剩余额度，把个别代理上调或下调一档。", "协调者也可视任务难度和剩余额度，把个别代理上调或下调一档")):
            self.assert_struck(line, clause)

    def test_struck_sentences_and_prohibitions_are_untouched(self):
        for line in ("- ~~编排者可按任务难度与余额将单个代理上下调一档~~（已作废）",
                     f"~~The orchestrator may move one agent one tier up or down for remaining budget~~{uw.VOID_NOTE}.",
                     "- 开跑之后不因剩余额度上下调一档。",
                     "The orchestrator never moves an agent one tier up or down for remaining budget.",
                     uw.NEW_TIER_BLOCK[-1]):
            self.assertEqual(uw.strike(line), (line, 0, []), line)

    def test_a_tier_sentence_without_a_quota_word_is_listed_not_struck(self):
        line = "The orchestrator may move an agent one tier up or down when a task is unusually hard; the gate stays."
        self.assertEqual(uw.strike(line), (line, 0, ["The orchestrator may move an agent one tier up or down when a "
                                                     "task is unusually hard;"]))


class TieringTests(TempMixin, unittest.TestCase):
    def upgrade(self, charter: str) -> tuple[dict, str]:
        ws = self.workspace(charter)
        result = uw.run(ws, check=False)
        return result, text(ws / uw.CHARTER)

    def test_cells_are_mapped_by_role_not_by_line(self):
        rows = list(uw.OLD_TIER_TABLE)
        table = rows[:2] + [rows[7], rows[5], rows[2], rows[6], rows[4], rows[3]]  # defender first, deducer last
        result, charter = self.upgrade(old_charter(table))
        self.assertIn("\n".join(uw.NEW_TIER_BLOCK) + "\n\n## Device gate", charter)
        self.assertEqual((result["left_as_is"], result["exit_code"]), ([], uw.EXIT_OK))

    def test_changed_cells_are_kept_and_conflicts_listed(self):
        table = list(uw.OLD_TIER_TABLE)
        table[3] = "| Deducer | inherit | inherit | opus |"  # exploratory as the new table; submission conflicts
        table[5] = "| Logic critic | opus | opus | inherit |"  # standard as the new table
        table[6] = "| Evidence critic / novelty critic | opus | opus | custom |"  # kept, conflicts
        result, charter = self.upgrade(old_charter(table))
        self.assertIn("| Deducer — new derivation | inherit | inherit | opus |\n"
                      "| Mechanical revision of a derivation that already passed the gate | opus | opus | opus |", charter)
        self.assertIn("| Logic critic | opus | opus | opus |\n| Evidence critic / novelty critic | opus | opus | custom |",
                      charter)
        self.assertEqual([item["item"] for item in result["left_as_is"]], [
            "tiering table: the project's cell Deducer — new derivation · Submission = opus kept (the new table has inherit)",
            "tiering table: the project's cell Evidence critic / novelty critic · Submission = custom kept (the new table has opus)"])
        self.assertEqual(result["exit_code"], uw.EXIT_DUE)

    def test_an_unrecognised_table_is_left_as_is(self):
        table = list(uw.OLD_TIER_TABLE)
        table[4] = "| **Verifier (gate)** | **inherit** | **强** | **inherit** |"
        result, charter = self.upgrade(old_charter(table))
        self.assertIn("\n".join(table) + "\n\nRules: the human may change any cell at any time. ~~The orchestrator may", charter)
        self.assertTrue(result["left_as_is"][0]["item"].startswith('tiering table not recognised (cell in "| **Verifier'))
        table = [uw.OLD_TIER_TABLE[0] + " Notes |", uw.OLD_TIER_TABLE[1] + "---|"] + [r + " |" for r in uw.OLD_TIER_TABLE[2:]]
        result, charter = self.upgrade(old_charter(table))  # another shape: a fifth column
        self.assertIn("\n".join(table) + "\n\nRules: the human may change any cell at any time. ~~The orchestrator may", charter)
        self.assertTrue(result["left_as_is"][0]["item"].startswith('tiering table not recognised (header "| Role |'))

    def test_the_new_table_is_untouched(self):
        charter = old_charter(list(uw.NEW_TIER_BLOCK[:-2]), uw.NEW_TIER_BLOCK[-1])
        result, after = self.upgrade(charter)
        self.assertEqual((after, result["due"], result["summary"]), (charter, False, "Settings current — no G2G 0.3.0 "
                                                                     "settings to upgrade; nothing written."))


class RowAndTitleTests(TempMixin, unittest.TestCase):
    def test_d3_rows(self):
        symbol_row = "| budget share | b | share of the household budget |"  # three columns: not a disposition row
        for row, new, reported in ((uw.OLD_D3_ROWS[0], 0, False), (uw.OLD_D3_ROWS[2], 0, False), (uw.OLD_D3_ROWS[3], 0, False),
                                   ("| **额度用到 80%** | 只收尾，写交接 |", 0, True), (uw.OLD_D3_ROWS[1], 1, False),
                                   ("| 预算到达上限 | 停 |", 1, True)):
            ws = self.workspace(f"# Charter\n\n| Situation | Disposition |\n|---|---|\n{row}\n| Outward actions | none |\n\n"
                                f"| symbol | meaning | note |\n|---|---|---|\n{symbol_row}\n")
            result = uw.run(ws, check=False)
            self.assertIn(f"|---|---|\n{uw.NEW_D3_ROWS[new]}\n| Outward actions", text(ws / uw.CHARTER), row)
            self.assertEqual(result["deleted"], [{"file": uw.CHARTER, "text": row}] if reported else [], row)
            self.assertEqual(result["left_as_is"], [], row)
        ws = self.workspace(f"# Charter\n\n| Situation | Disposition |\n|---|---|\n| Budget exhausted | stop |\n\n"
                            f"| symbol | meaning | note |\n|---|---|---|\n{symbol_row}\n| x | `period_share` | 1 |\n")
        result = uw.run(ws, check=False)
        self.assertEqual([i["item"] for i in result["left_as_is"]], [
            'budget row not recognised — compare it with the new rows (templates.md, Unattended-case dispositions D.3): '
            '"| Budget exhausted | stop |"'])

    def test_u_titles(self):
        body = "| ID | date | ruling | scope |\n|---|---|---|---|\n"
        for title, expected, reported in (
                (uw.OLD_U_TITLE, uw.NEW_U[0], False),
                ("### 常设裁定（Standing rulings · U 系列；人已经关闭的异议类别，批评者引用即止）", "#" + uw.NEW_U[0], True),
                ("## Standing rulings (U series: objection classes closed by the human)", uw.NEW_U[0], True)):
            ws = self.workspace("# Charter\n", **{uw.HARD_CORE: f"# Hard core\n\n{title}\n{body}"})
            result = uw.run(ws, check=False)
            self.assertEqual(text(ws / uw.HARD_CORE), f"# Hard core\n\n{expected}\n{uw.NEW_U[1]}\n{body}", title)
            self.assertEqual(result["deleted"], [{"file": uw.HARD_CORE, "text": title}] if reported else [], title)
        for title in ("## Standing rulings (U-series — the human's standing directions)", "## 常设裁定（U 系列）"):
            ws = self.workspace("# Charter\n", **{uw.HARD_CORE: f"# Hard core\n\n{title}\n{body}"})
            before = (ws / uw.HARD_CORE).read_bytes()
            result = uw.run(ws, check=False)
            self.assertEqual(((ws / uw.HARD_CORE).read_bytes(), result["due"]), (before, False), title)

    def test_an_emptied_heading_with_more_than_the_template_text_is_reported(self):
        heading = "## Seeded rules (v2.0 defaults) — kept on purpose, the human 2026-03-05"
        ws = self.workspace("# Charter\n", **{uw.DEFECTS: f"# Process defects\n\n{heading}\n" + "\n".join(uw.OLD_SEEDED_RULES[:4]) + "\n"})
        result = uw.run(ws, check=False)
        self.assertEqual(text(ws / uw.DEFECTS), "# Process defects\n")
        self.assertEqual(result["deleted"], [{"file": uw.DEFECTS, "text": heading}])


class FixtureTests(TempMixin, unittest.TestCase):
    def test_english_workspace_upgrades_to_the_expected_files(self):
        root = self.copy_fixture(EN)
        result = uw.run(root / "g2g", check=False)
        for name in UPGRADED:
            self.assertEqual((root / "g2g" / name).read_bytes(), (EN / "expected" / name).read_bytes(), name)
        for name, backup in zip(UPGRADED, BACKUPS):
            self.assertEqual((root / "g2g" / backup).read_bytes(), (EN / "g2g" / name).read_bytes(), backup)
        self.assertEqual((result["exit_code"], result["left_as_is"], result["backups"]), (uw.EXIT_OK, [], list(BACKUPS)))
        self.assertEqual(result["deleted"], [{"file": uw.CHARTER, "text": "| **Per-round budget (ceiling)** | "
                         "`round_token_budget_estimate` | 40 agent calls — the human, 2026-03-02: \"small rounds until "
                         "the first trial run has been read\" |"}])
        self.assertEqual(result["changes"][uw.DEFECTS], ["9 seeded rules deleted, 1 emptied heading removed"])

    def test_other_files_are_untouched(self):
        root = self.copy_fixture(EN)
        before = files(root)
        uw.run(root / "g2g", check=False)
        after = files(root)
        self.assertEqual(set(after) - set(before), {f"g2g/{b}" for b in BACKUPS})
        for name in ("g2g/02_question-registry.md", "g2g/04_log.md"):
            self.assertEqual(after[name], before[name])

    def test_chinese_workspace(self):
        root = self.copy_fixture(ZH)
        result = uw.run(root / "g2g", check=False)
        charter = text(root / "g2g" / uw.CHARTER)
        self.assertIn("| Defender | opus | opus | opus |", charter)  # the changed submission cell kept
        self.assertIn("| Deducer — new derivation | inherit | inherit | inherit |", charter)
        self.assertIn(uw.NEW_TIER_BLOCK[-1] + "\n\n\"继承\" = 人启动会话时开的那个模型", charter)
        self.assertIn(f"~~编排者可按任务难度与预算余量把单个代理在表的上下各调一档~~{uw.VOID_NOTE}，**闸门不得低于表**。", charter)
        self.assertIn(f"- ~~协调者也可视任务难度和剩余额度，把个别代理上调或下调一档~~{uw.VOID_NOTE}。", charter)
        self.assertIn("- ~~编排者可按任务难度与余额将单个代理上下调一档~~（2026-04-20 人已作废：档位照表走）\n"
                      "- 开跑之后不因剩余额度上下调一档。\n", charter)
        self.assertIn("\n".join(uw.NEW_D3_ROWS), charter)
        self.assertNotIn("Budget fence", charter)  # a charter without a fence paragraph gets none
        self.assertNotIn("round_token_budget_estimate", charter)
        self.assertNotIn("period_share", charter)
        self.assertIn("**方法论：** G2G v3.1", charter)
        self.assertIn("\n".join(uw.NEW_U) + "\n| 编号 | 日期 | 裁定 | 范围 |", text(root / "g2g" / uw.HARD_CORE))
        self.assertEqual((root / "g2g" / uw.DEFECTS).read_bytes(), (ZH / "g2g" / uw.DEFECTS).read_bytes())
        self.assertFalse((root / "g2g" / BACKUPS[2]).exists())
        self.assertEqual([i["item"].split(" — ")[0].split(":")[0] for i in result["left_as_is"]],
                         ["tiering table", "paragraph under the old tiering table kept below the new rules",
                          "seeded rules not in the 0.3.0 wording"])
        self.assertEqual([d["text"].split(" | ")[1] for d in result["deleted"][:2]],
                         ["`round_token_budget_estimate`", "`period_share`"])
        self.assertEqual(result["deleted"][2], {"file": uw.HARD_CORE,
                                                "text": "## 常设裁定（U 系列 · 人已关闭的异议类别；批评者援引后即收手）"})
        self.assertEqual(result["exit_code"], uw.EXIT_DUE)

    def test_unrecognised_forms_are_left_and_listed(self):
        root = self.copy_fixture(UNRECOGNISED)
        before = files(root)
        result = uw.run(root / "g2g", check=False)
        self.assertEqual(result["exit_code"], uw.EXIT_DUE)
        self.assertEqual(result["changes"], {uw.CHARTER: ["1 budget row deleted (period_share)", "methodology v3.0 → v3.1"]})
        self.assertEqual([i["item"].split(" (")[0].split(" — ")[0] for i in result["left_as_is"]],
                         ["tiering table not recognised", "tier-change sentence without a quota word or not a permission",
                          "budget-fence paragraph not in the 0.3.0 wording", "budget row not recognised",
                          "U-series title not recognised"])
        old = before["g2g/00_programme.md"].decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
        new = text(root / "g2g" / uw.CHARTER).splitlines(keepends=True)
        self.assertEqual([line for line in old if line not in new],
                         [old[2], "| **Period share** | `period_share` | a third of the weekly usage — the human, 2026-05-05 |\n"])
        self.assertEqual((root / "g2g" / uw.HARD_CORE).read_bytes(), before["g2g/01_hard-core.md"])
        self.assertEqual(set(files(root)) - set(before), {"g2g/00_programme.v0.3.0.md"})
        wrapped = uw.OLD_FENCE.replace(" defender) and records", "\ndefender) and records")  # hard-wrapped: not the 0.3.0 form
        ws = self.workspace(f"# Charter\n\n{wrapped}\nTwo things never loosen.\n\n| Situation | Disposition |\n|---|---|\n"
                            f"{uw.OLD_D3_ROWS[1]}\n")
        result = uw.run(ws, check=False)
        self.assertIn(wrapped, text(ws / uw.CHARTER))
        self.assertEqual([i["item"].split(" — ")[0] for i in result["left_as_is"]],
                         ["budget-fence paragraph not in the 0.3.0 wording"])

    def test_a_second_run_changes_nothing(self):
        for fixture in (EN, ZH, UNRECOGNISED):
            root = self.copy_fixture(fixture)
            uw.run(root / "g2g", check=False)
            before = files(root)
            result = uw.run(root / "g2g", check=False)
            self.assertEqual(files(root), before, fixture.name)  # no change, no second backup
            self.assertEqual((result["due"], result["exit_code"], result["left_as_is"], result["written"]),
                             (False, uw.EXIT_OK, [], []), fixture.name)
            for backup, original in ((b, n) for b, n in zip(BACKUPS, UPGRADED) if (root / "g2g" / b).exists()):
                self.assertEqual(before[f"g2g/{backup}"], (fixture / "g2g" / original).read_bytes())

    def test_check_writes_nothing(self):
        root = self.copy_fixture(EN)
        before = files(root)
        result = run_cli(str(root), "--check")
        self.assertEqual((result.returncode, files(root)), (uw.EXIT_DUE, before))
        self.assertIn(b"nothing written", result.stdout.splitlines()[0])
        self.assertEqual(run_cli(str(root)).returncode, uw.EXIT_OK)
        self.assertEqual(run_cli(str(root / "g2g"), "--check").returncode, uw.EXIT_OK)

    def test_crlf_and_bom_are_kept(self):
        root = self.copy_fixture(EN)
        for path in (root / "g2g").glob("*.md"):
            path.write_bytes(b"\xef\xbb\xbf" + text(path).replace("\n", "\r\n").encode("utf-8"))
        uw.run(root / "g2g", check=False)
        for name in UPGRADED:
            data = (root / "g2g" / name).read_bytes()
            self.assertTrue(data.startswith(b"\xef\xbb\xbf"), name)
            self.assertNotIn(b"\n", data.replace(b"\r\n", b""), name)
            self.assertEqual(data[3:].replace(b"\r\n", b"\n"),
                             (EN / "expected" / name).read_bytes().replace(b"\r\n", b"\n"), name)

    def test_an_existing_backup_is_never_overwritten(self):
        root = self.copy_fixture(EN)
        (root / "g2g" / BACKUPS[0]).write_bytes(b"an earlier backup\n")
        result = uw.run(root / "g2g", check=False)
        self.assertEqual((root / "g2g" / BACKUPS[0]).read_bytes(), b"an earlier backup\n")
        self.assertEqual(result["backups"][0], f"{BACKUPS[0]} (existing, kept)")
        self.assertEqual((root / "g2g" / uw.CHARTER).read_bytes(), (EN / "expected" / uw.CHARTER).read_bytes())

    def test_01_and_06_are_optional_and_a_missing_final_newline_stays_missing(self):
        root = self.copy_fixture(EN)
        (root / "g2g" / uw.HARD_CORE).unlink()
        (root / "g2g" / uw.DEFECTS).write_text("# Process defects\n\n## Logged defects\n| date | defect |\n|---|---|\n\n"
                                               "## Seeded rules (v2.0 defaults)\n" + uw.OLD_SEEDED_RULES[2],
                                               encoding="utf-8", newline="\n")
        result = uw.run(root / "g2g", check=False)
        self.assertEqual(text(root / "g2g" / uw.DEFECTS), "# Process defects\n\n## Logged defects\n| date | defect |\n|---|---|")
        self.assertEqual(set(result["changes"]), {uw.CHARTER, uw.DEFECTS})


class CliTests(TempMixin, unittest.TestCase):
    def test_report_layout(self):
        root = self.copy_fixture(ZH)
        result = run_cli(str(root))
        self.assertEqual(result.returncode, uw.EXIT_DUE, result.stderr)
        lines = result.stdout.decode("utf-8").splitlines()
        self.assertTrue(lines[0].startswith("Settings upgraded from G2G 0.3.0 to 0.4.0 — 00_programme.md: "))
        self.assertIn("· backups: 00_programme.v0.3.0.md, 01_hard-core.v0.3.0.md · items left as is: 3 (listed below) · "
                      "deleted lines that held more than the template's text: 3 (in full below).", lines[0])
        self.assertEqual([line.split(" · ")[0] for line in lines[1:]], ["left as is"] * 3 + ["deleted"] * 3)
        self.assertEqual(lines[4], "deleted · 00_programme.md · | **每轮预算（上限）** | `round_token_budget_estimate` | "
                                   "120 次代理调用（负责人 2026-04-01：先这样跑，第一次试跑之后再定） |")

    def test_json(self):
        root = self.copy_fixture(EN)
        data = json.loads(run_cli(str(root), "--check", "--json").stdout.decode("utf-8"))
        self.assertEqual(set(data), {"version", "workspace", "mode", "due", "summary", "changes", "backups", "written",
                                     "left_as_is", "deleted", "exit_code"})
        self.assertEqual((data["mode"], data["due"], data["written"], data["exit_code"]), ("check", True, [], 1))
        data = json.loads(run_cli(str(root), "--json").stdout.decode("utf-8"))
        self.assertEqual((data["mode"], data["written"], data["exit_code"]), ("upgrade", list(UPGRADED), 0))
        self.assertEqual(data["deleted"][0]["file"], uw.CHARTER)

    def test_usage_and_io_errors(self):
        result = run_cli(str(HERE))
        self.assertEqual((result.returncode, result.stdout), (uw.EXIT_USAGE, b""))
        self.assertIn(b"error:", result.stderr)
        root = self.copy_fixture(EN)
        (root / "g2g" / uw.HARD_CORE).write_bytes(b"\xff\xfe not UTF-8")
        before = files(root)
        result = run_cli(str(root))
        self.assertEqual((result.returncode, files(root)), (uw.EXIT_USAGE, before))
        self.assertEqual(run_cli("--version").stdout.decode("utf-8").strip(), f"upgrade_workspace {uw.VERSION}")

    def test_utf8_without_pythonioencoding(self):
        root = self.copy_fixture(ZH)
        env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
        result = run_cli(str(root), "--check", env=env)
        self.assertEqual(result.returncode, uw.EXIT_DUE, result.stderr)
        self.assertIn("周期份额".encode("utf-8"), result.stdout)

    def test_console_fallback_never_raises(self):
        with mock.patch.object(sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="cp1252")):
            self.assertEqual(uw._console_safe("deleted · 00 · 周期 — v3.0 → v3.1 …", False),
                             "deleted , 00 , ?? - v3.0 -> v3.1 ...")


if __name__ == "__main__":
    unittest.main()
