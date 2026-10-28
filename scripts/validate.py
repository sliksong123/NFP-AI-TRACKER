"""
Check data/cases.json before you commit it.

    python scripts/validate.py

Reads the rules from data/schema.json (required fields, allowed values,
id pattern) and also checks things a schema can't: unique ids, real dates,
http(s) source links, and that the id matches the organisation + category.
Uses only the Python standard library. Exits with code 1 if anything is wrong.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "cases.json"
SCHEMA = ROOT / "data" / "schema.json"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def is_date(s: str) -> bool:
    try:
        date.fromisoformat(s)
        return len(s) == 10
    except (TypeError, ValueError):
        return False


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        db = json.loads(DB.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"data/cases.json is not valid JSON: line {e.lineno}, column {e.colno}: {e.msg}")
        return 1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    case_schema = schema["$defs"]["case"]
    props = case_schema["properties"]
    required = case_schema["required"]
    id_pattern = re.compile(props["id"]["pattern"])

    if not isinstance(db, dict) or "cases" not in db or "meta" not in db:
        print('data/cases.json must be an object with "meta" and "cases".')
        return 1
    if not is_date(db["meta"].get("last_updated", "")):
        errors.append('meta.last_updated must be a date like "2026-10-29"')

    seen: dict[str, int] = {}
    for i, c in enumerate(db["cases"]):
        where = f'case {i + 1} ({c.get("id") or c.get("organisation") or "no id"})'
        if not isinstance(c, dict):
            errors.append(f"{where}: must be an object")
            continue
        for k in required:
            if k not in c or c[k] in ("", None, []):
                errors.append(f"{where}: missing {k}")
        for k in c:
            if k not in props:
                errors.append(f'{where}: unknown field "{k}" (check spelling, or add it to schema.json)')
        for k, spec in props.items():
            v = c.get(k)
            if v is None:
                continue
            if "enum" in spec and v not in spec["enum"]:
                errors.append(f'{where}: {k} "{v}" is not one of: {", ".join(repr(x) for x in spec["enum"])}')
            if spec.get("type") == "string" and not isinstance(v, str):
                errors.append(f"{where}: {k} must be text")
        cid = c.get("id", "")
        if cid:
            if not id_pattern.match(cid):
                errors.append(f'{where}: id "{cid}" must look like "organisation-name--category-word"')
            if cid in seen:
                errors.append(f'{where}: duplicate id, also used by case {seen[cid]}')
            seen[cid] = i + 1
            first_word = slug(c.get("organisation", "")).split("-")[0]
            if first_word and not cid.startswith(first_word):
                warnings.append(f'{where}: id doesn\'t start with the organisation name ("{slug(c["organisation"])}")')
        for k in ("first_seen", "last_seen"):
            if c.get(k) and not is_date(c[k]):
                errors.append(f'{where}: {k} "{c[k]}" must be a date like 2026-10-29')
        if is_date(c.get("first_seen", "")) and is_date(c.get("last_seen", "")) and c["last_seen"] < c["first_seen"]:
            errors.append(f"{where}: last_seen is before first_seen")
        srcs = c.get("sources", [])
        if not isinstance(srcs, list):
            errors.append(f"{where}: sources must be a list")
        else:
            for s in srcs:
                if not isinstance(s, dict) or not re.match(r"^https?://", str(s.get("url", ""))):
                    errors.append(f"{where}: each source needs a url starting with http:// or https://")
        if c.get("status") == "review" and not c.get("review_reason"):
            warnings.append(f"{where}: unverified case has no review_reason")
        if c.get("status") == "tracker" and c.get("review_reason"):
            warnings.append(f"{where}: verified case still has a review_reason")

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    n = len(db["cases"])
    verified = sum(1 for c in db["cases"] if isinstance(c, dict) and c.get("status") == "tracker")
    if errors:
        print(f"\n{len(errors)} error(s) in {n} cases. Fix them before committing.")
        return 1
    print(f"OK: {n} cases ({verified} verified, {n - verified} not yet verified), {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
