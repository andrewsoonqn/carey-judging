from __future__ import annotations

import json
import os
from pathlib import Path

from pipeline.analysis import analyze_run


BASE_DIR = Path(__file__).resolve().parent
RUN_ID = os.environ.get("PIPELINE_RUN_ID", "run_demo_batch")


def main() -> None:
    run_dir = BASE_DIR / "runs" / RUN_ID
    summary = analyze_run(run_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
