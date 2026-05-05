"""PromptShield CLI scanner.

Usage:
    python -m promptshield.scan "your prompt here"

Returns a JSON verdict with score, severity, and matched patterns.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def load_patterns(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parent.parent / "patterns.json"
    with path.open() as f:
        return json.load(f)


def scan(prompt: str, patterns: dict[str, Any] | None = None) -> dict[str, Any]:
    if patterns is None:
        patterns = load_patterns()

    matched = []
    score = 0
    for p in patterns["patterns"]:
        try:
            if re.search(p["regex"], prompt):
                matched.append({"id": p["id"], "name": p["name"], "category": p["category"]})
                score += int(p["weight"])
        except re.error:
            continue

    score = min(score, 100)
    if score >= 50:
        severity = "high"
    elif score >= 25:
        severity = "medium"
    elif score > 0:
        severity = "low"
    else:
        severity = "clean"

    return {
        "score": score,
        "severity": severity,
        "matched_patterns": matched,
        "pattern_library_version": patterns.get("version"),
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m promptshield.scan <prompt>", file=sys.stderr)
        return 2
    result = scan(" ".join(argv))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
