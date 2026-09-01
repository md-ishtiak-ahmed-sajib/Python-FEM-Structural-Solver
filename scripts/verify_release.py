"""Execute release checks and record only observed outcomes, never physical evidence."""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    (root / "results").mkdir(exist_ok=True)
    checks = [
        ["scripts/check_docs.py"],
        ["scripts/build_learning_docs.py", "--check"],
        ["pytest", "-q", "--junitxml=results/pytest.xml"],
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
        ["mypy", "src"],
        ["pip", "check"],
        ["build"],
    ]
    records = []
    for arguments in checks:
        prefix = [] if arguments[0].endswith(".py") else ["-m"]
        completed = subprocess.run(
            [sys.executable, *prefix, *arguments], cwd=root, capture_output=True, text=True
        )
        log = completed.stdout + completed.stderr
        (root / "results" / f"check-{Path(arguments[0]).stem}.log").write_text(
            log, encoding="utf-8"
        )
        records.append(
            {
                "command": "python " + " ".join([*prefix, *arguments]),
                "exit_code": completed.returncode,
                "status": "passed" if completed.returncode == 0 else "failed",
            }
        )
        print(records[-1], flush=True)
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.system(),
        "checks": records,
        "core_source_sha256": hashlib.sha256(
            b"".join(p.read_bytes() for p in sorted((root / "src/fem_solver").glob("*.py")))
        ).hexdigest(),
        "evidence_scope": "Local automated software verification only. Not physical validation or independent-person reproduction.",
    }
    destination = root / "reports/verification/software_checks.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return int(any(record["exit_code"] != 0 for record in records))


if __name__ == "__main__":
    raise SystemExit(main())
