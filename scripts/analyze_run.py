from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.analysis import analyze_run


BASE_DIR = _REPO_ROOT
RUN_ID = os.environ.get("PIPELINE_RUN_ID", "run_demo_simple")


def main() -> None:
    run_dir = BASE_DIR / "runs" / RUN_ID
    summary = analyze_run(run_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
