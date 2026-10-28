"""
Export data/cases.json to data/cases.csv (opens in Excel or Google Sheets).

    python scripts/to_csv.py              # all cases
    python scripts/to_csv.py --verified   # verified cases only

Uses only the Python standard library.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLS = ["id", "status", "organisation", "org_type", "state", "cause_area", "category", "use_case",
        "partner", "stage", "quote", "sources", "first_seen", "last_seen", "review_reason"]


def main() -> None:
    db = json.loads((ROOT / "data" / "cases.json").read_text(encoding="utf-8"))
    cases = db["cases"]
    if "--verified" in sys.argv:
        cases = [c for c in cases if c.get("status") == "tracker"]
    out = ROOT / "data" / "cases.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:  # -sig so Excel reads accents correctly
        w = csv.writer(f)
        w.writerow(COLS)
        for c in cases:
            w.writerow([" | ".join(s.get("url", "") for s in c.get("sources", [])) if k == "sources" else c.get(k, "")
                        for k in COLS])
    print(f"Wrote {len(cases)} cases to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
