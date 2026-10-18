"""Tests for project_checks.py.

Run: python test_project_checks.py

Every check gets both a happy-path case AND a deliberately-broken case - a
checker that only ever says "True" catches nothing. If you change
project_checks.py, run this file before trusting the new behaviour.
"""
import tempfile
import unittest
from pathlib import Path

import project_checks as pc


class TestWordCount(unittest.TestCase):
    def test_within_range_passes(self):
        result = pc.check_word_count("one two three four five", min_words=3, max_words=10)
        self.assertEqual(result["word_count"], 5)
        self.assertTrue(result["ok"])

    def test_too_short_fails(self):
        result = pc.check_word_count("one two", min_words=5, max_words=10)
        self.assertFalse(result["ok"])

    def test_too_long_fails(self):
        result = pc.check_word_count(" ".join(["word"] * 20), min_words=1, max_words=10)
        self.assertFalse(result["ok"])


class TestRequiredKeywords(unittest.TestCase):
    def test_all_present_passes(self):
        result = pc.check_required_keywords(
            "So what: invest in the north. Limitations: one year of data only.",
            keywords=["so what", "limitations"],
        )
        self.assertTrue(result["ok"])
        self.assertTrue(all(result["found"].values()))

    def test_case_insensitive(self):
        result = pc.check_required_keywords("SO WHAT comes next", keywords=["so what"])
        self.assertTrue(result["ok"])

    def test_missing_keyword_fails(self):
        result = pc.check_required_keywords(
            "This report has findings but never says what to do next.",
            keywords=["so what", "limitations"],
        )
        self.assertFalse(result["ok"])
        self.assertFalse(result["found"]["so what"])
        self.assertFalse(result["found"]["limitations"])


class TestNumericClaims(unittest.TestCase):
    def test_enough_numbers_passes(self):
        text = "Revenue was 230,001.08 across 1200 orders in 16 regions, up 55.6% and 12 more."
        result = pc.check_numeric_claims(text, min_count=5)
        self.assertGreaterEqual(result["count"], 5)
        self.assertTrue(result["ok"])

    def test_no_numbers_fails(self):
        text = "Revenue grew a lot across many regions, by a wide margin."
        result = pc.check_numeric_claims(text, min_count=1)
        self.assertEqual(result["count"], 0)
        self.assertFalse(result["ok"])


class TestForbiddenLanguage(unittest.TestCase):
    def test_clean_prose_passes(self):
        text = "27 of 1,200 orders referenced a customer who was not on file."
        result = pc.check_no_forbidden_language(text, ["_(", "df[", "import "])
        self.assertTrue(result["ok"])

    def test_code_language_fails(self):
        text = "We ran df['region'].isna().sum() and found 27 orphan orders."
        result = pc.check_no_forbidden_language(text, ["df["])
        self.assertFalse(result["ok"])
        self.assertIn("df[", result["forbidden_found"])


class TestCheckReport(unittest.TestCase):
    def test_missing_file_fails_cleanly(self):
        result = pc.check_report(
            "/tmp/this_file_should_never_exist_12345.md",
            min_words=1, max_words=1000,
        )
        self.assertFalse(result["exists"])
        self.assertFalse(result["ok"])

    def test_good_report_passes_every_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "act_report.md"
            path.write_text(
                "Revenue reached 230,001.08 across 1,200 orders. The Middle zone led "
                "with 24,269.81 in profit, a 28.2% margin, while Northern's 29.7% margin "
                "was the highest of the three zones. So what: prioritise Northern's volume "
                "growth given its stronger margin. Limitations: this covers 2023 only."
            )
            result = pc.check_report(
                path, min_words=10, max_words=200,
                required_keywords=["so what", "limitations"],
                min_numeric_claims=3,
            )
            self.assertTrue(result["ok"], result)

    def test_report_missing_keyword_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "act_report.md"
            path.write_text("Revenue reached 230,001.08. Profit was 65,886.38 and margin was 28.6%.")
            result = pc.check_report(
                path, min_words=1, max_words=200,
                required_keywords=["so what", "limitations"],
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["keywords"]["ok"])

    def test_report_with_code_language_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrangle_report.md"
            path.write_text("We ran df['region'].isna().sum() and got 27.")
            result = pc.check_report(
                path, min_words=1, max_words=200,
                forbidden_substrings=["df["],
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["forbidden_language"]["ok"])


class TestChartCount(unittest.TestCase):
    def test_enough_charts_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            charts_dir = Path(tmp) / "charts"
            charts_dir.mkdir()
            for name in ["bar.png", "line.png", "hist.png", "scatter.png", "heatmap.png"]:
                (charts_dir / name).write_bytes(b"\x89PNG\r\n")
            result = pc.check_chart_count(charts_dir, min_count=5)
            self.assertTrue(result["ok"])
            self.assertEqual(result["count"], 5)

    def test_missing_directory_fails(self):
        result = pc.check_chart_count("/tmp/this_charts_dir_should_not_exist_12345", min_count=1)
        self.assertFalse(result["exists"])
        self.assertFalse(result["ok"])

    def test_too_few_charts_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            charts_dir = Path(tmp) / "charts"
            charts_dir.mkdir()
            (charts_dir / "only_one.png").write_bytes(b"\x89PNG\r\n")
            result = pc.check_chart_count(charts_dir, min_count=5)
            self.assertFalse(result["ok"])
            self.assertEqual(result["count"], 1)


class TestRunCapstoneChecks(unittest.TestCase):
    def _build_good_project(self, tmp):
        project_dir = Path(tmp)
        (project_dir / "wrangle_report.md").write_text(
            " ".join(["This dataset needed cleaning before analysis."] * 25)
        )
        (project_dir / "act_report.md").write_text(
            "Revenue reached 230,001.08 across 1,200 orders in 16 regions during 2023, "
            "up 55.6% in the final two months, almost all of it concentrated in the "
            "Middle zone. The Middle zone led every other zone with 24,269.81 in total "
            "profit, although Northern actually converted a larger share of its revenue "
            "into profit, at a 29.7% margin against Middle's 28.2%. A third of all "
            "customers, 70 of 209, accounted for 69.2% of total profit across the year, "
            "making customer retention a bigger lever than acquiring new accounts. "
            "So what: prioritise the top profit tier for a dedicated retention plan, "
            "and investigate what is limiting Northern's volume given its stronger "
            "margin. Limitations: this analysis covers 2023 only, so there is no prior "
            "year to confirm whether the November-December pattern repeats annually."
        )
        charts_dir = project_dir / "charts"
        charts_dir.mkdir()
        for name in ["bar.png", "line.png", "hist.png", "scatter.png", "heatmap.png"]:
            (charts_dir / name).write_bytes(b"\x89PNG\r\n")
        return project_dir

    def test_complete_project_passes_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = self._build_good_project(tmp)
            results = pc.run_capstone_checks(project_dir)
            self.assertTrue(results["all_ok"], results)

    def test_short_act_report_fails_overall(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = self._build_good_project(tmp)
            (project_dir / "act_report.md").write_text("Too short. So what: nothing. Limitations: none.")
            results = pc.run_capstone_checks(project_dir)
            self.assertFalse(results["all_ok"])
            self.assertFalse(results["act_report"]["ok"])

    def test_missing_charts_fails_overall(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = self._build_good_project(tmp)
            for png in (project_dir / "charts").glob("*.png"):
                png.unlink()
            results = pc.run_capstone_checks(project_dir)
            self.assertFalse(results["all_ok"])
            self.assertFalse(results["charts"]["ok"])

    def test_missing_wrangle_report_fails_overall(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = self._build_good_project(tmp)
            (project_dir / "wrangle_report.md").unlink()
            results = pc.run_capstone_checks(project_dir)
            self.assertFalse(results["all_ok"])
            self.assertFalse(results["wrangle_report"]["exists"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
