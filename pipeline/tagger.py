from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .interfaces import TurnTagger


ALLOWED_STRUCTURES = {"question", "reflection", "suggestion", "hybrid"}
ALLOWED_PRIMARY_STRATEGIES = {
    "probe",
    "reflect",
    "validate",
    "reframe",
    "suggest",
    "plan",
    "support",
    "other",
}


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tag_transcript_file(
    transcript_path: str | Path,
    output_path: str | Path,
    tagger: TurnTagger,
) -> dict[str, Any]:
    transcript_path = Path(transcript_path)
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))

    friend_turn_tags = []
    for message_position_1_based, message in enumerate(transcript["messages"], start=1):
        if message["speaker"] != "friend":
            continue
        tagged_turn = _validate_tagged_turn(
            tagger.tag_turn(
                transcript=transcript["messages"][:message_position_1_based],
                friend_message=message,
                message_position_1_based=message_position_1_based,
            ),
            expected_friend_turn_index=message["turn_index"],
            expected_message_position_1_based=message_position_1_based,
            expected_text=message["text"],
        )
        friend_turn_tags.append(tagged_turn)

    tag_payload = {
        "run_id": transcript["run_id"],
        "conversation_id": transcript["conversation_id"],
        "role_card_id": transcript["role_card_id"],
        "source_transcript_path": str(transcript_path),
        "source_transcript_sha256": _sha256_file(transcript_path),
        "tagger": {
            "tagger_version": tagger.version,
            "taxonomy_version": tagger.taxonomy_version,
            "model": tagger.name,
            "temperature": 0.0,
        },
        "friend_turn_tags": friend_turn_tags,
        "status": "completed",
        "created_at": _utc_now(),
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tag_payload, indent=2) + "\n", encoding="utf-8")
    return tag_payload


def _validate_tagged_turn(
    tagged_turn: dict[str, Any],
    *,
    expected_friend_turn_index: int,
    expected_message_position_1_based: int,
    expected_text: str,
) -> dict[str, Any]:
    if tagged_turn.get("friend_turn_index") != expected_friend_turn_index:
        raise ValueError("tagged turn has incorrect friend_turn_index")
    if tagged_turn.get("message_position_1_based") != expected_message_position_1_based:
        raise ValueError("tagged turn has incorrect message_position_1_based")
    if tagged_turn.get("text") != expected_text:
        raise ValueError("tagged turn text does not match transcript")

    structure = tagged_turn.get("structure")
    primary_strategy = tagged_turn.get("primary_strategy")
    secondary_strategies = tagged_turn.get("secondary_strategies", [])
    confidence = tagged_turn.get("confidence", 0.0)
    notes = tagged_turn.get("notes", "")

    if structure not in ALLOWED_STRUCTURES:
        raise ValueError(f"invalid structure: {structure}")
    if primary_strategy not in ALLOWED_PRIMARY_STRATEGIES:
        raise ValueError(f"invalid primary_strategy: {primary_strategy}")
    if not isinstance(secondary_strategies, list):
        raise ValueError("secondary_strategies must be a list")
    if not isinstance(notes, str):
        raise ValueError("notes must be a string")
    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be numeric")

    normalized_secondary: list[str] = []
    for value in secondary_strategies:
        if value not in ALLOWED_PRIMARY_STRATEGIES:
            raise ValueError(f"invalid secondary strategy: {value}")
        if value == primary_strategy:
            raise ValueError("secondary_strategies cannot repeat primary_strategy")
        if value not in normalized_secondary:
            normalized_secondary.append(value)

    normalized_tagged_turn = dict(tagged_turn)
    normalized_tagged_turn["secondary_strategies"] = normalized_secondary
    normalized_tagged_turn["confidence"] = float(confidence)
    if not 0.0 <= normalized_tagged_turn["confidence"] <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    return normalized_tagged_turn
