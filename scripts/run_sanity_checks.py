"""
run_sanity_checks.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 14

Runs all statistical sanity checks defined in:
docs/data-quality/statistical_sanity_checks.md

Run: python scripts/run_sanity_checks.py

Outputs:
  data/processed/sanity_check_report.json
  data/processed/failed_rows.csv
"""

import collections
import csv
import json
import re
import math
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).resolve().parent.parent
SYN         = ROOT / "data" / "synthetic"
PROC        = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

REPORT_JSON = PROC / "sanity_check_report.json"
FAILED_CSV  = PROC / "failed_rows.csv"

# ── CSV loader ────────────────────────────────────────────────────────────────

def load(filename: str) -> list[dict[str, str]]:
    path = SYN / filename
    if not path.exists():
        alt = PROC / filename
        if not alt.exists():
            return []
        path = alt
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_proc(filename: str) -> list[dict[str, str]]:
    path = PROC / filename
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ── Result helpers ────────────────────────────────────────────────────────────

class Result:
    def __init__(self, name: str):
        self.name      = name
        self.passed    = True
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.detail:   dict      = {}

    def fail(self, msg: str) -> None:
        self.passed = False
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "check":    self.name,
            "passed":   self.passed,
            "failures": self.failures,
            "warnings": self.warnings,
            "detail":   self.detail,
        }

# ── Check implementations ─────────────────────────────────────────────────────

def check_class_balance() -> Result:
    r = Result("class_balance_target_labels")
    rows = load_proc("profile_feature_scores.csv")
    if not rows:
        r.fail("profile_feature_scores.csv not found or empty")
        return r

    n = len(rows)
    for label, lo, hi in [
        ("success_prediction_label", 0.35, 0.65),
        ("at_risk_label",            0.20, 0.50),
    ]:
        vals = [row.get(label, "") for row in rows]
        if any(v == "" for v in vals):
            r.fail(f"{label}: missing values in some rows")
            continue
        try:
            pos   = sum(1 for v in vals if int(v) == 1)
            ratio = pos / n
        except ValueError:
            r.fail(f"{label}: non-integer values found")
            continue

        r.detail[label] = {"positive_count": pos, "total": n, "ratio": round(ratio, 4)}

        if pos == 0:
            r.fail(f"{label}: all zeros — degenerate label")
        elif pos == n:
            r.fail(f"{label}: all ones — degenerate label")
        elif pos < math.ceil(lo * n):
                r.fail(f"{label}: positive ratio {ratio:.4f} below minimum {lo} "
                f"(need {math.ceil(lo * n)} positives, have {pos})")
        elif ratio > hi:
            r.fail(f"{label}: positive ratio {ratio:.4f} above maximum {hi}")

    return r


def check_null_scans() -> tuple[Result, list[dict]]:
    r            = Result("null_scans_required_columns")
    failed_rows: list[dict] = []

    required: dict[str, tuple[str, list[str]]] = {
        "student_profiles.csv": ("SYN", [
            "student_id", "full_name", "email", "role", "department", "skills"
        ]),
        "alumni_profiles.csv": ("SYN", [
            "alumni_id", "full_name", "email", "role", "graduation_year"
        ]),
        "startup_profiles.csv": ("SYN", [
            "startup_id", "sector", "funding_stage", "trl_level", "pitch_summary"
        ]),
        "investor_mentor_profiles.csv": ("SYN", [
            "profile_id", "role", "mandate_text", "sector_focus"
        ]),
        "interaction_edges.csv": ("SYN", [
            "edge_id", "source_profile_id", "target_profile_id", "edge_type"
        ]),
        "profile_feature_scores.csv": ("PROC", [
            "profile_id", "ais_normalized", "grit_normalized", "review_flag"
        ]),
    }

    for filename, (src, cols) in required.items():
        rows = load(filename) if src == "SYN" else load_proc(filename)
        if not rows:
            r.warn(f"{filename}: not found or empty — skipping null scan")
            continue

        file_nulls = 0
        for i, row in enumerate(rows):
            for col in cols:
                val = row.get(col, None)
                if val is None or str(val).strip() == "":
                    file_nulls += 1
                    failed_rows.append({
                        "file": filename, "row_index": i,
                        "column": col, "value": repr(val),
                        "check": "null_scan",
                    })
        if file_nulls > 0:
            r.fail(f"{filename}: {file_nulls} null(s) in required columns")
        else:
            r.detail[filename] = "OK"

    return r, failed_rows


def check_outliers() -> tuple[Result, list[dict]]:
    r            = Result("outlier_detection_numeric_features")
    failed_rows: list[dict] = []

    # startup_profiles uses trl_level / mrl_level (not technology_readiness_level)
    startup_bounds: dict[str, tuple[float, float]] = {
        "trl_level": (1, 9),
        "mrl_level": (1, 9),
    }
    feat_bounds: dict[str, tuple[float, float]] = {
        "competitions_participated":  (0,   50),
        "competitions_won":           (0,   50),
        "ais_normalized":             (0.0, 100.0),
        "grit_normalized":            (0.0, 100.0),
    }

    for filename, bounds in [
        ("startup_profiles.csv",        startup_bounds),
        ("profile_feature_scores.csv",  feat_bounds),
    ]:
        rows = load(filename) if filename != "profile_feature_scores.csv" else load_proc(filename)
        if not rows:
            r.warn(f"{filename}: not found — skipping outlier check")
            continue

        for col, (lo, hi) in bounds.items():
            if col not in rows[0]:
                r.warn(f"{filename}: column '{col}' not present — skipping")
                continue
            for i, row in enumerate(rows):
                try:
                    val = float(row[col])
                except (ValueError, TypeError):
                    continue
                if val < lo or val > hi:
                    failed_rows.append({
                        "file": filename, "row_index": i,
                        "column": col, "value": val,
                        "check": "outlier",
                    })

    # competitions_won <= competitions_participated
    feat_rows = load_proc("profile_feature_scores.csv")
    if feat_rows and "competitions_won" in feat_rows[0] and "competitions_participated" in feat_rows[0]:
        for i, row in enumerate(feat_rows):
            try:
                w = int(row["competitions_won"])
                p = int(row["competitions_participated"])
                if w > p:
                    failed_rows.append({
                        "file": "profile_feature_scores.csv", "row_index": i,
                        "column": "competitions_won", "value": w,
                        "check": "outlier_won_gt_participated",
                    })
            except (ValueError, TypeError):
                pass

    if failed_rows:
        r.fail(f"{len(failed_rows)} outlier violation(s) found")
    else:
        r.detail["result"] = "All numeric features within declared bounds"

    return r, failed_rows


def check_referential_integrity() -> Result:
    r = Result("referential_integrity")

    startup_rows = load("startup_profiles.csv")
    if not startup_rows:
        r.warn("startup_profiles.csv not found — skipping referential integrity")
        return r

    startup_ids = {row.get("startup_id", "") for row in startup_rows}

    # Founder links
    fl_rows = load("startup_founder_links.csv")
    if fl_rows:
        missing  = [row["startup_id"] for row in fl_rows
                    if row.get("startup_id") not in startup_ids]
        if missing:
            r.fail(f"startup_founder_links: {len(missing)} startup_id(s) not in startup_profiles")
        else:
            r.detail["founder_links_startup_ids"] = "OK"

        # founder_count match
        expected_counts: dict[str, int] = {}
        for row in startup_rows:
            try:
                expected_counts[row["startup_id"]] = int(row.get("founder_count", 0))
            except ValueError:
                pass
        actual_counts: collections.Counter = collections.Counter(
            row["startup_id"] for row in fl_rows
        )
        mismatches = [
            sid for sid, exp in expected_counts.items()
            if actual_counts.get(sid, 0) != exp
        ]
        if mismatches:
            r.fail(f"founder_count mismatch for {len(mismatches)} startup(s): "
                   f"{mismatches[:5]}")
        else:
            r.detail["founder_count_integrity"] = "OK"
    else:
        r.warn("startup_founder_links.csv not found")

    # Funding timeline
    ft_rows = load("startup_funding_timeline.csv")
    if ft_rows:
        missing = [row["startup_id"] for row in ft_rows
                   if row.get("startup_id") not in startup_ids]
        if missing:
            r.fail(f"startup_funding_timeline: {len(missing)} startup_id(s) not in startup_profiles")
        else:
            r.detail["funding_timeline_startup_ids"] = "OK"
    else:
        r.warn("startup_funding_timeline.csv not found")

    # Profile ID format in competition and achievement records
    profile_id_re = re.compile(r"^(STU|ALU)-\d{4}$")
    for filename in ["competition_records.csv", "achievement_records.csv"]:
        rows = load(filename)
        if not rows:
            r.warn(f"{filename}: not found")
            continue
        bad = [row.get("profile_id", "") for row in rows
               if not profile_id_re.match(row.get("profile_id", ""))]
        if bad:
            r.fail(f"{filename}: {len(bad)} invalid profile_id format(s)")
        else:
            r.detail[f"{filename}_profile_ids"] = "OK"

    # Edge type validity
    edge_rows = load("interaction_edges.csv")
    valid_types = {"mentor_mentee", "investor_founder", "club_membership"}
    if edge_rows:
        bad_types = [row["edge_type"] for row in edge_rows
                     if row.get("edge_type") not in valid_types]
        if bad_types:
            r.fail(f"interaction_edges: {len(bad_types)} invalid edge_type value(s)")
        else:
            r.detail["edge_type_validity"] = "OK"

    return r


def check_distribution_realism() -> Result:
    r = Result("distribution_realism")

    # Funding stage — no single stage > 60%
    startup_rows = load("startup_profiles.csv")
    if startup_rows:
        counter: collections.Counter = collections.Counter(
            row.get("funding_stage", "") for row in startup_rows
        )
        n = len(startup_rows)
        for stage, count in counter.items():
            ratio = count / n
            if ratio > 0.60:
                r.fail(f"funding_stage '{stage}' = {ratio:.2%} of all startups (> 60%)")
        r.detail["funding_stage_counts"] = dict(counter)

    # Unique pitch text ratio
    if startup_rows and "pitch_summary" in (startup_rows[0] if startup_rows else {}):
        texts  = [row.get("pitch_summary", "") for row in startup_rows]
        unique = len(set(texts))
        ratio  = unique / len(texts) if texts else 0
        r.detail["pitch_unique_ratio"] = round(ratio, 4)
        if ratio < 0.80:
            r.warn(f"pitch_summary unique ratio = {ratio:.2%} (below 0.80 soft threshold)")

    # Interaction graph avg degree
    edge_rows = load("interaction_edges.csv")
    if edge_rows:
        degree: collections.Counter = collections.Counter()
        for e in edge_rows:
            degree[e.get("source_profile_id", "")] += 1
            degree[e.get("target_profile_id", "")]  += 1
        avg_deg = sum(degree.values()) / len(degree) if degree else 0
        r.detail["graph_avg_degree"] = round(avg_deg, 2)
        if avg_deg < 2.0:
            r.warn(f"graph average degree = {avg_deg:.2f} (below 2.0 soft threshold)")

    return r

# ── Writer ────────────────────────────────────────────────────────────────────

def write_failed_csv(rows: list[dict]) -> None:
    if not rows:
        FAILED_CSV.write_text("no_failures\n", encoding="utf-8")
        return
    with open(FAILED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "row_index", "column", "value", "check"])
        writer.writeheader()
        writer.writerows(rows)

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 Day 14 — Sanity Checks\n")

    results:     list[dict]        = []
    all_failed:  list[dict]        = []

    # Run checks
    r1          = check_class_balance()
    r2, f2      = check_null_scans()
    r3, f3      = check_outliers()
    r4          = check_referential_integrity()
    r5          = check_distribution_realism()

    all_failed.extend(f2)
    all_failed.extend(f3)

    for res in [r1, r2, r3, r4, r5]:
        results.append(res.to_dict())
        icon = "✓" if res.passed else "✗"
        print(f"  {icon} {res.name}")
        for msg in res.failures:
            print(f"      FAIL: {msg}")
        for msg in res.warnings:
            print(f"      WARN: {msg}")

    passed  = sum(1 for res in results if res["passed"])
    failed  = len(results) - passed
    total_w = sum(len(res["warnings"]) for res in results)

    summary = {
        "project":        "Campus Innovation & Engagement Intelligence Hub",
        "phase":          "1 — Day 14",
        "total_checks":   len(results),
        "passed":         passed,
        "failed":         failed,
        "total_warnings": total_w,
        "checks":         results,
    }

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    write_failed_csv(all_failed)

    print(f"\n  Total: {len(results)}  Passed: {passed}  Failed: {failed}  Warnings: {total_w}")
    print(f"  Report  → {REPORT_JSON}")
    print(f"  Failures→ {FAILED_CSV}")

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()