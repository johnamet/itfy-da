"""Dataset-agnostic structural checks for the Topic 23 capstone.

Every prior topic's assignment checked specific numbers against a dataset
everyone shared. The capstone has no shared dataset - everyone picks their
own - so these checks test STRUCTURE instead: did the report mention enough
specific numbers, does it have the sections a reader needs, does the right
number of chart files exist. None of this checks whether the report is any
good - a report can pass every check here and still be badly argued. It
catches "forgot the Limitations section" and "wrote three sentences," not
"wrote something true" - that part still needs a human reader.

Used by capstone_project/assignments/topic23_capstone_project_brief.ipynb
and instructor_solutions/capstone_project/example_capstone_walkthrough.ipynb.
"""
from pathlib import Path
import re


def word_count(text):
    return len(text.split())


def check_word_count(text, min_words, max_words):
    n = word_count(text)
    return {
        "word_count": n,
        "min_words": min_words,
        "max_words": max_words,
        "ok": min_words <= n <= max_words,
    }


def check_required_keywords(text, keywords):
    """Case-insensitive substring check - every keyword must appear somewhere."""
    text_lower = text.lower()
    found = {keyword: (keyword.lower() in text_lower) for keyword in keywords}
    return {"found": found, "ok": all(found.values())}


def check_numeric_claims(text, min_count=1):
    """Counts number-like tokens (1200, 3.5, 12,345.67) as a proxy for 'how
    many specific claims does this report make,' not a measure of truth."""
    numbers = re.findall(r"\d[\d,]*\.?\d*", text)
    return {"count": len(numbers), "min_count": min_count, "ok": len(numbers) >= min_count}


def check_no_forbidden_language(text, forbidden_substrings):
    """For the wrangling report: no code, column names, or library names -
    a reader who has never opened Jupyter should still follow every sentence."""
    present = [s for s in forbidden_substrings if s in text]
    return {"forbidden_found": present, "ok": len(present) == 0}


def check_file_exists(path):
    path = Path(path)
    return {"path": str(path), "exists": path.exists()}


def check_report(path, min_words, max_words, required_keywords=None,
                  forbidden_substrings=None, min_numeric_claims=None):
    """Read a report file from disk and run every applicable check on it.

    Returns a dict with one sub-result per check performed, plus a top-level
    "ok" that is True only if every sub-check passed.
    """
    path = Path(path)
    if not path.exists():
        return {"path": str(path), "exists": False, "ok": False}

    text = path.read_text(encoding="utf-8")
    result = {"path": str(path), "exists": True}
    result["word_count"] = check_word_count(text, min_words, max_words)
    if required_keywords:
        result["keywords"] = check_required_keywords(text, required_keywords)
    if forbidden_substrings:
        result["forbidden_language"] = check_no_forbidden_language(text, forbidden_substrings)
    if min_numeric_claims is not None:
        result["numeric_claims"] = check_numeric_claims(text, min_numeric_claims)

    sub_oks = [v["ok"] for v in result.values() if isinstance(v, dict) and "ok" in v]
    result["ok"] = bool(sub_oks) and all(sub_oks)
    return result


def check_chart_count(charts_dir, min_count):
    charts_dir = Path(charts_dir)
    if not charts_dir.exists():
        return {"path": str(charts_dir), "exists": False, "count": 0,
                "min_count": min_count, "ok": False}
    files = sorted(p.name for p in charts_dir.glob("*.png"))
    return {
        "path": str(charts_dir), "exists": True, "count": len(files), "files": files,
        "min_count": min_count, "ok": len(files) >= min_count,
    }


def run_capstone_checks(project_dir, min_chart_count=5,
                         wrangle_report_name="wrangle_report.md",
                         act_report_name="act_report.md",
                         charts_dirname="charts"):
    """One call, the whole structural checklist, for any project directory -
    whatever dataset the student picked. Run this cell on your own project."""
    project_dir = Path(project_dir)

    results = {}
    results["wrangle_report"] = check_report(
        project_dir / wrangle_report_name,
        min_words=120, max_words=500,
        forbidden_substrings=["_(", "df[", "import ", ".py"],
    )
    results["act_report"] = check_report(
        project_dir / act_report_name,
        min_words=120, max_words=450,
        required_keywords=["so what", "limitation"],
        min_numeric_claims=5,
    )
    results["charts"] = check_chart_count(project_dir / charts_dirname, min_chart_count)
    results["all_ok"] = all(r.get("ok", False) for r in results.values())
    return results
