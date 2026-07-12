"""
run_generator_review.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 14

Auto-checks every programmatically verifiable item from:
docs/data-quality/generator_review_checklist.md

Items that require human eyes are flagged MANUAL.

Run: python scripts/run_generator_review.py

Outputs:
  data/processed/generator_review_report.json
  Console checklist with PASS / FAIL / WARN / MANUAL per item
"""

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).resolve().parent.parent
SYN         = ROOT / "data" / "synthetic"
PROC        = ROOT / "data" / "processed"
SCRIPTS_DIR = ROOT / "scripts"
PROC.mkdir(parents=True, exist_ok=True)

REPORT_JSON = PROC / "generator_review_report.json"

# ── Result ────────────────────────────────────────────────────────────────────

PASS   = "PASS"
FAIL   = "FAIL"
WARN   = "WARN"
MANUAL = "MANUAL"

class Item:
    def __init__(self, section: str, name: str):
        self.section = section
        self.name    = name
        self.status  = PASS
        self.detail  = ""

    def set(self, status: str, detail: str = "") -> "Item":
        self.status = status
        self.detail = detail
        return self

    def to_dict(self) -> dict:
        return {"section": self.section, "item": self.name,
                "status": self.status, "detail": self.detail}

# ── CSV helpers ───────────────────────────────────────────────────────────────

def _load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _syn(filename: str) -> list[dict]:
    return _load(SYN / filename)

def _proc(filename: str) -> list[dict]:
    return _load(PROC / filename)

# ── Script source helpers ─────────────────────────────────────────────────────

def _script_text(filename: str) -> str:
    path = SCRIPTS_DIR / filename
    if not path.exists():
        path = ROOT / "data" / "generation" / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def _script_hash(filename: str) -> str:
    txt = _script_text(filename)
    return hashlib.md5(txt.encode()).hexdigest() if txt else ""

GENERATOR_SCRIPTS = [
    "generate_ecosystem_data.py",
    "generate_startup_data.py",
    "generate_interaction_data.py",
    "compute_feature_scores.py",
]

# ── Check functions ───────────────────────────────────────────────────────────

# -- Schema alignment --

def check_startup_schema() -> Item:
    it   = Item("schema_alignment", "startup_profiles.csv has required columns")
    rows = _syn("startup_profiles.csv")
    if not rows:
        return it.set(FAIL, "startup_profiles.csv not found")
    required = {"startup_id", "sector", "funding_stage", "trl_level",
                "pitch_summary", "founder_count"}
    missing  = required - set(rows[0].keys())
    return it.set(PASS) if not missing else it.set(FAIL, f"Missing: {missing}")

def check_feature_schema() -> Item:
    it   = Item("schema_alignment", "profile_feature_scores.csv has required columns")
    rows = _proc("profile_feature_scores.csv")
    if not rows:
        return it.set(FAIL, "profile_feature_scores.csv not found")
    required = {"profile_id", "ais_normalized", "grit_normalized",
                "review_flag", "success_prediction_label", "at_risk_label"}
    missing  = required - set(rows[0].keys())
    return it.set(PASS) if not missing else it.set(FAIL, f"Missing: {missing}")

def check_json_summary_files() -> Item:
    it    = Item("schema_alignment", "JSON summary files exist with generated_files key")
    names = [
        SYN  / "generation_summary.json",
        SYN  / "startup_generation_summary.json",
        SYN  / "interaction_generation_summary.json",
    ]
    missing = [p.name for p in names if not p.exists()]
    if missing:
        return it.set(WARN, f"Not found: {missing}")
    bad = []
    for p in names:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            if "generated_files" not in obj:
                bad.append(p.name)
        except json.JSONDecodeError:
            bad.append(p.name)
    return it.set(PASS) if not bad else it.set(FAIL, f"Missing 'generated_files' key: {bad}")

def check_column_snake_case() -> Item:
    it      = Item("schema_alignment", "All CSV columns use snake_case (no spaces, no camelCase)")
    bad     = []
    files   = list(SYN.glob("*.csv")) + list(PROC.glob("*.csv"))
    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    for fp in files:
        rows = _load(fp)
        if not rows:
            continue
        for col in rows[0].keys():
            if not pattern.match(col):
                bad.append(f"{fp.name}: '{col}'")
    return it.set(PASS) if not bad else it.set(FAIL, f"{len(bad)} non-snake_case column(s): {bad[:5]}")

# -- Determinism --

# Scripts that are deterministic but use no randomness — exempt from seed check
SEEDLESS_SCRIPTS = {"compute_feature_scores.py"}

def check_seed_in_scripts() -> Item:
    it  = Item("determinism", "All generator scripts define a SEED constant")
    bad = []
    for name in GENERATOR_SCRIPTS:
        if name in SEEDLESS_SCRIPTS:
            continue   # deterministic pure-computation script; no RNG, no seed needed
        txt = _script_text(name)
        if not txt:
            bad.append(f"{name}: not found")
            continue
        if "SEED" not in txt and "seed" not in txt:
            bad.append(f"{name}: no seed reference")
    return it.set(PASS) if not bad else it.set(FAIL, str(bad))

def check_seed_in_json_summary() -> Item:
    it   = Item("determinism", "JSON summaries record the seed used")
    bad  = []
    for p in [SYN / "generation_summary.json",
              SYN / "startup_generation_summary.json",
              SYN / "interaction_generation_summary.json"]:
        if not p.exists():
            bad.append(f"{p.name}: not found")
            continue
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            if "seed" not in obj:
                bad.append(f"{p.name}: no 'seed' key")
        except json.JSONDecodeError:
            bad.append(f"{p.name}: invalid JSON")
    return it.set(PASS) if not bad else it.set(WARN, str(bad))

def check_no_datetime_now() -> Item:
    it   = Item("determinism", "No datetime.now() or uuid4() without seed in generators")
    bad  = []
    for name in GENERATOR_SCRIPTS:
        txt = _script_text(name)
        if "datetime.now()" in txt:
            bad.append(f"{name}: uses datetime.now()")
        if "uuid4()" in txt:
            bad.append(f"{name}: uses uuid4() — verify it is seeded")
    return it.set(PASS) if not bad else it.set(WARN, str(bad))

def check_reproducibility() -> Item:
    """Runs generate_ecosystem_data.py twice and compares MD5 of student_profiles.csv."""
    it   = Item("determinism", "generate_ecosystem_data.py produces byte-identical output on repeat runs")
    path = SCRIPTS_DIR / "generate_ecosystem_data.py"
    if not path.exists():
        return it.set(WARN, "generate_ecosystem_data.py not found — skipping")

    target = SYN / "student_profiles.csv"

    def _run_and_hash() -> str:
        subprocess.run([sys.executable, str(path)],
                       capture_output=True, check=False)
        if not target.exists():
            return ""
        return hashlib.md5(target.read_bytes()).hexdigest()

    h1 = _run_and_hash()
    h2 = _run_and_hash()

    if not h1:
        return it.set(WARN, "student_profiles.csv not produced — cannot check reproducibility")
    if h1 == h2:
        return it.set(PASS, f"MD5 stable: {h1}")
    return it.set(FAIL, f"Output differs between runs: {h1} vs {h2}")

# -- Referential integrity --

def check_founder_count_integrity() -> Item:
    it      = Item("referential_integrity", "founder_count in startup_profiles matches founder_link rows")
    s_rows  = _syn("startup_profiles.csv")
    fl_rows = _syn("startup_founder_links.csv")
    if not s_rows or not fl_rows:
        return it.set(WARN, "startup_profiles.csv or startup_founder_links.csv not found")

    import collections
    actual: collections.Counter = collections.Counter(r["startup_id"] for r in fl_rows)
    mismatches = []
    for row in s_rows:
        try:
            expected = int(row.get("founder_count", 0))
        except ValueError:
            continue
        sid = row["startup_id"]
        if actual.get(sid, 0) != expected:
            mismatches.append(sid)
    return (it.set(PASS, f"All {len(s_rows)} startups match")
            if not mismatches
            else it.set(FAIL, f"{len(mismatches)} mismatch(es): {mismatches[:3]}"))

def check_funding_timeline_ids() -> Item:
    it      = Item("referential_integrity", "startup_funding_timeline startup_ids all exist in startup_profiles")
    s_rows  = _syn("startup_profiles.csv")
    ft_rows = _syn("startup_funding_timeline.csv")
    if not s_rows or not ft_rows:
        return it.set(WARN, "One or both files not found")
    valid   = {r["startup_id"] for r in s_rows}
    orphans = [r["startup_id"] for r in ft_rows if r.get("startup_id") not in valid]
    return (it.set(PASS) if not orphans
            else it.set(FAIL, f"{len(orphans)} orphan startup_id(s)"))

def check_profile_id_format() -> Item:
    it      = Item("referential_integrity", "competition/achievement profile_ids match STU-#### or ALU-#### format")
    pattern = re.compile(r"^(STU|ALU)-\d{4}$")
    bad     = []
    for filename in ["competition_records.csv", "achievement_records.csv"]:
        rows = _syn(filename)
        if not rows:
            continue
        for row in rows:
            pid = row.get("profile_id", "")
            if not pattern.match(pid):
                bad.append(f"{filename}: '{pid}'")
    return it.set(PASS) if not bad else it.set(FAIL, f"{len(bad)} invalid format(s): {bad[:3]}")

# -- Realism --

def check_funding_stage_spread() -> Item:
    it    = Item("realism", "No single funding_stage exceeds 60% of startup records")
    rows  = _syn("startup_profiles.csv")
    if not rows:
        return it.set(WARN, "startup_profiles.csv not found")
    import collections
    n       = len(rows)
    counter = collections.Counter(r.get("funding_stage", "") for r in rows)
    bad     = {k: round(v/n, 4) for k, v in counter.items() if v/n > 0.60}
    return it.set(PASS) if not bad else it.set(FAIL, f"Dominant stages: {bad}")

def check_all_stages_present() -> Item:
    it       = Item("realism", "All defined funding stages appear at least once")
    rows     = _syn("startup_profiles.csv")
    expected = {"pre-seed", "seed", "grant", "series-a", "bootstrapped"}
    if not rows:
        return it.set(WARN, "startup_profiles.csv not found")
    found   = {r.get("funding_stage", "") for r in rows}
    missing = expected - found
    return it.set(PASS) if not missing else it.set(WARN, f"Missing stages: {missing}")

def check_pitch_uniqueness() -> Item:
    it   = Item("realism", "pitch_summary unique-text ratio ≥ 0.80")
    rows = _syn("startup_profiles.csv")
    if not rows or "pitch_summary" not in rows[0]:
        return it.set(WARN, "startup_profiles.csv or pitch_summary column not found")
    texts = [r.get("pitch_summary", "") for r in rows]
    ratio = len(set(texts)) / len(texts)
    return (it.set(PASS, f"Ratio = {ratio:.4f}")
            if ratio >= 0.80
            else it.set(WARN, f"Ratio = {ratio:.4f} (below 0.80)"))

# -- Sanity checks --

def check_sanity_report_exists() -> Item:
    it   = Item("sanity_checks", "sanity_check_report.json exists and shows zero hard failures")
    path = PROC / "sanity_check_report.json"
    if not path.exists():
        return it.set(FAIL, "sanity_check_report.json not found — run run_sanity_checks.py first")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return it.set(FAIL, "sanity_check_report.json is invalid JSON")
    failed = obj.get("failed", -1)
    if failed == 0:
        return it.set(PASS, f"0 failures, {obj.get('total_warnings', 0)} warning(s)")
    return it.set(FAIL, f"{failed} hard failure(s) in report")

def check_label_balance_in_report() -> Item:
    it   = Item("sanity_checks", "class_balance_target_labels check passed in report")
    path = PROC / "sanity_check_report.json"
    if not path.exists():
        return it.set(WARN, "sanity_check_report.json not found")
    try:
        obj    = json.loads(path.read_text(encoding="utf-8"))
        checks = {c["check"]: c for c in obj.get("checks", [])}
        bal    = checks.get("class_balance_target_labels", {})
    except (json.JSONDecodeError, KeyError):
        return it.set(WARN, "Could not parse report")
    return (it.set(PASS) if bal.get("passed") else
            it.set(FAIL, str(bal.get("failures", []))))

# -- Plots --

def check_plots_exist() -> Item:
    it       = Item("plot_review", "All 6 required distribution plots exist")
    required = [
        "funding_stage_distribution.png", "ais_histogram.png",
        "degree_distribution.png", "grit_histogram.png",
        "label_balance.png", "review_flag_distribution.png",
    ]
    plots_dir = PROC / "plots"
    missing   = [name for name in required if not (plots_dir / name).exists()]
    return (it.set(PASS, f"All {len(required)} plots present")
            if not missing
            else it.set(FAIL, f"Missing: {missing}"))

def check_plot_review_manual() -> Item:
    return Item("plot_review", "Plots visually reviewed for degenerate distributions").set(
        MANUAL, "Open data/processed/plots/ and verify each plot passes review criteria "
                "in docs/data-quality/distribution_visualization_spec.md"
    )

# -- Code quality --

def check_no_todos() -> Item:
    it   = Item("code_quality", "No TODO / FIXME / stub / pseudocode in generator scripts")
    bad  = []
    tags = ["TODO", "FIXME", "stub", "pseudocode", "implement later"]
    for name in GENERATOR_SCRIPTS:
        txt = _script_text(name)
        for tag in tags:
            if tag.lower() in txt.lower():
                bad.append(f"{name}: contains '{tag}'")
    return it.set(PASS) if not bad else it.set(WARN, str(bad))

def check_main_guard() -> Item:
    it  = Item("code_quality", "All generator scripts have main() and __name__ == '__main__' guard")
    bad = []
    for name in GENERATOR_SCRIPTS:
        txt = _script_text(name)
        if not txt:
            bad.append(f"{name}: not found")
            continue
        if "def main()" not in txt:
            bad.append(f"{name}: missing main()")
        if '__name__ == "__main__"' not in txt and "__name__ == '__main__'" not in txt:
            bad.append(f"{name}: missing __name__ guard")
    return it.set(PASS) if not bad else it.set(FAIL, str(bad))

def check_mkdir_in_scripts() -> Item:
    it  = Item("code_quality", "All generator scripts auto-create output directory")
    bad = []
    for name in GENERATOR_SCRIPTS:
        txt = _script_text(name)
        if txt and "mkdir" not in txt:
            bad.append(name)
    return it.set(PASS) if not bad else it.set(WARN, f"No mkdir call found in: {bad}")

def check_no_external_api() -> Item:
    it   = Item("code_quality", "No live external API or requests calls in generators")
    bad  = []
    hits = ["requests.get", "requests.post", "urllib.request.urlopen",
            "httpx", "aiohttp", "linkedin", "scrape"]
    for name in GENERATOR_SCRIPTS:
        txt = _script_text(name)
        for hit in hits:
            if hit in txt.lower():
                bad.append(f"{name}: '{hit}'")
    return it.set(PASS) if not bad else it.set(FAIL, str(bad))

def check_peer_review_manual() -> Item:
    return Item("code_quality",
                "At least one peer (or self-review comment) confirmed determinism").set(
        MANUAL, "Add a PR comment confirming you re-ran all generators independently "
                "and got byte-identical output before merging"
    )

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 Day 14 — Generator Review\n")

    all_checks: list[Callable[[], Item]] = [
        # Schema
        check_startup_schema,
        check_feature_schema,
        check_json_summary_files,
        check_column_snake_case,
        # Determinism
        check_seed_in_scripts,
        check_seed_in_json_summary,
        check_no_datetime_now,
        check_reproducibility,
        # Referential integrity
        check_founder_count_integrity,
        check_funding_timeline_ids,
        check_profile_id_format,
        # Realism
        check_funding_stage_spread,
        check_all_stages_present,
        check_pitch_uniqueness,
        # Sanity checks
        check_sanity_report_exists,
        check_label_balance_in_report,
        # Plots
        check_plots_exist,
        check_plot_review_manual,
        # Code quality
        check_no_todos,
        check_main_guard,
        check_mkdir_in_scripts,
        check_no_external_api,
        check_peer_review_manual,
    ]

    results:  list[dict] = []
    counts    = {PASS: 0, FAIL: 0, WARN: 0, MANUAL: 0}
    current_section = ""

    for fn in all_checks:
        item = fn()
        results.append(item.to_dict())
        counts[item.status] += 1

        if item.section != current_section:
            current_section = item.section
            print(f"\n  ── {current_section.upper().replace('_', ' ')} ──")

        icons = {PASS: "✓", FAIL: "✗", WARN: "!", MANUAL: "◎"}
        print(f"  {icons[item.status]} [{item.status:6s}] {item.name}")
        if item.detail and item.status != PASS:
            print(f"            {item.detail}")

    print(f"\n  PASS={counts[PASS]}  FAIL={counts[FAIL]}  "
          f"WARN={counts[WARN]}  MANUAL={counts[MANUAL]}")

    report = {
        "project": "Campus Innovation & Engagement Intelligence Hub",
        "phase":   "1 — Day 14",
        "summary": counts,
        "merge_gate_passed": counts[FAIL] == 0,
        "checks":  results,
    }

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report → {REPORT_JSON}")

    if counts[FAIL] > 0:
        print(f"\n  ✗ {counts[FAIL]} failure(s) — merge gate NOT passed")
        raise SystemExit(1)
    else:
        print(f"\n  ✓ No hard failures — MANUAL items require human sign-off before merge")


if __name__ == "__main__":
    main()