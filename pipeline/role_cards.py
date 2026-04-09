from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def all_role_cards() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "sample_role_cards.json"
    return json.loads(path.read_text(encoding="utf-8"))
