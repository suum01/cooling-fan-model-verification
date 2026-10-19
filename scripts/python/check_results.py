"""Fail closed on absent, incomplete, mistimed or incorrect model output."""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def compare(expected, actual):
    if not expected or len(actual) != len(expected):
        return f"sample count: expected {len(expected)}, actual {len(actual)}"
    for i, (e, a) in enumerate(zip(expected, actual)):
        try:
            t = float(a["time"])
            if not math.isfinite(t) or abs(t - float(e["time"])) > 1e-9:
                return f"sample {i}: time mismatch"
            for name in ("fan_cmd", "fault_flag"):
                value = float(a[name])
                if value not in (0.0, 1.0) or value != float(e[name]):
                    return f"t={t:g}: {name} expected {e[name]}, actual {a[name]}"
        except (ValueError, KeyError, TypeError) as exc:
            return f"sample {i}: invalid output ({exc})"
    return ""


def check(actual_dir):
    manifest = json.loads((ROOT / "tests/manifest.json").read_text(encoding="utf-8"))
    if len(manifest) != 23 or len({c["id"] for c in manifest}) != 23:
        raise ValueError("Expected 23 unique test cases")
    summary = []
    for case in manifest:
        test_id = case["id"]
        try:
            issue = compare(read_rows(ROOT / "tests/expected" / f"{test_id}.csv"),
                            read_rows(actual_dir / f"{test_id}.csv"))
        except (OSError, csv.Error) as exc:
            issue = str(exc)
        summary.append({"test_id":test_id, "status":"FAIL" if issue else "PASS", "detail":issue})
    actual_dir.mkdir(parents=True, exist_ok=True)
    with (actual_dir / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["test_id","status","detail"])
        writer.writeheader()
        writer.writerows(summary)
    passed = sum(row["status"] == "PASS" for row in summary)
    print(f"{actual_dir.name}: {passed}/{len(summary)} PASS")
    for row in summary:
        if row["status"] == "FAIL":
            print(row["test_id"], row["detail"])
    return passed == len(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual-dir", type=Path, default=ROOT / "results/actual")
    args = parser.parse_args()
    raise SystemExit(0 if check(args.actual_dir.resolve()) else 1)
