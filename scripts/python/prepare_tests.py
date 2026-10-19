"""Generate explicit, reviewed test vectors. No production logic as oracle."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Each event: time in ms, temperature, valid, expected fan, expected fault.
# Expected values are authored from docs/05-test-specification.md.
CASES = [
    ("TC-001", [(0,93,1,0,0)]),
    ("TC-002", [(0,94.9,1,0,0)]),
    ("TC-003", [(0,95,1,1,0)]),
    ("TC-004", [(0,95.1,1,1,0)]),
    ("TC-005", [(0,95,1,1,0),(100,90.1,1,1,0)]),
    ("TC-006", [(0,95,1,1,0),(100,90,1,0,0)]),
    ("TC-007", [(0,95,1,1,0),(100,89.9,1,0,0)]),
    ("TC-008", [(0,85,1,0,0),(100,91,1,0,0),(200,93,1,0,0),(300,94,1,0,0)]),
    ("TC-009", [(0,96,1,1,0),(100,94,1,1,0),(200,93,1,1,0),(300,91,1,1,0)]),
    ("TC-010", [(0,85,1,0,0),(100,93,1,0,0),(200,95,1,1,0),(300,93,1,1,0),(400,90,1,0,0)]),
    ("TC-011", [(0,85,0,1,1)]),
    ("TC-012", [(0,85,1,0,0),(100,85,0,1,1)]),
    ("TC-013", [(0,93,1,0,0),(100,93,0,1,1)]),
    ("TC-014", [(0,96,1,1,0),(100,96,0,1,1)]),
    ("TC-015", [(0,85,0,1,1),(100,93,0,1,1),(200,96,0,1,1),(300,85,0,1,1)]),
    ("TC-016", [(0,85,0,1,1),(100,85,1,0,0)]),
    ("TC-017", [(0,93,0,1,1),(100,93,1,1,0)]),
    ("TC-018", [(0,96,0,1,1),(100,96,1,1,0)]),
    ("TC-019", [(0,85,1,0,0),(50,95,1,0,0),(100,95,1,1,0)]),
    ("TC-020", [(0,95,1,1,0),(50,90,1,1,0),(100,90,1,0,0)]),
    ("TC-021", [(0,85,1,0,0),(50,85,0,0,0),(100,85,0,1,1)]),
    ("TC-022", [(0,85,0,1,1),(50,85,1,1,1),(100,85,1,0,0)]),
    ("TC-023", [(0,85,1,0,0),(50,95,1,0,0),(100,95,1,1,0),
                (150,90,1,1,0),(200,90,1,0,0),(250,95,1,0,0),(300,95,1,1,0)]),
]


def generate():
    for folder in ("tests/inputs", "tests/expected"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    manifest = []
    for test_id, events in CASES:
        # Observe the final state for an additional full control period.
        stop_ms = events[-1][0] + 100
        rows = []
        index = 0
        for tick in range(0, stop_ms + 1, 10):
            while index + 1 < len(events) and events[index + 1][0] <= tick:
                index += 1
            _, temp, valid, fan, fault = events[index]
            rows.append((tick / 1000, temp, valid, fan, fault))
        for folder, fields, indices in (
            ("inputs", ["time","temperature","sensor_valid"], (0,1,2)),
            ("expected", ["time","fan_cmd","fault_flag"], (0,3,4)),
        ):
            with (ROOT / "tests" / folder / f"{test_id}.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(fields)
                writer.writerows(tuple(row[i] for i in indices) for row in rows)
        manifest.append({"id": test_id, "stop_time": stop_ms / 1000})
    (ROOT / "tests/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(manifest)} test cases")


if __name__ == "__main__":
    generate()
