from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _load_tag_files(tags_dir: Path) -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(tags_dir.glob("*.tags.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def analyze_run(run_dir: str | Path) -> dict[str, Any]:
    run_dir = Path(run_dir)
    tags_dir = run_dir / "tags"
    tables_dir = run_dir / "tables"
    reports_dir = run_dir / "reports"

    tag_payloads = _load_tag_files(tags_dir)
    per_turn_rows: list[dict[str, Any]] = []
    conversation_rows: list[dict[str, Any]] = []

    overall_strategy_counts: Counter[str] = Counter()
    structure_by_turn: dict[int, Counter[str]] = defaultdict(Counter)
    strategy_by_turn: dict[int, Counter[str]] = defaultdict(Counter)
    same_strategy_percentages: list[float] = []
    total_friend_turns = 0

    for payload in tag_payloads:
        strategies: list[str] = []
        structures: list[str] = []
        per_conversation_strategy_counts: Counter[str] = Counter()

        for tag in payload["friend_turn_tags"]:
            per_turn_rows.append(
                {
                    "run_id": payload["run_id"],
                    "conversation_id": payload["conversation_id"],
                    "role_card_id": payload["role_card_id"],
                    "friend_turn_index": tag["friend_turn_index"],
                    "message_position_1_based": tag["message_position_1_based"],
                    "structure": tag["structure"],
                    "primary_strategy": tag["primary_strategy"],
                    "secondary_strategies": "|".join(tag["secondary_strategies"]),
                    "confidence": tag.get("confidence", ""),
                    "tagger_version": payload["tagger"]["tagger_version"],
                    "taxonomy_version": payload["tagger"]["taxonomy_version"],
                }
            )

            strategies.append(tag["primary_strategy"])
            structures.append(tag["structure"])
            per_conversation_strategy_counts[tag["primary_strategy"]] += 1
            overall_strategy_counts[tag["primary_strategy"]] += 1
            structure_by_turn[tag["friend_turn_index"]][tag["structure"]] += 1
            strategy_by_turn[tag["friend_turn_index"]][tag["primary_strategy"]] += 1
            total_friend_turns += 1

        dominant_strategy = ""
        dominant_share = 0.0
        same_primary_strategy_percentage = 0.0
        if per_conversation_strategy_counts:
            dominant_strategy, dominant_count = (
                per_conversation_strategy_counts.most_common(1)[0]
            )
            dominant_share = dominant_count / len(strategies)
            same_primary_strategy_percentage = dominant_share * 100
            same_strategy_percentages.append(same_primary_strategy_percentage)

        conversation_rows.append(
            {
                "run_id": payload["run_id"],
                "conversation_id": payload["conversation_id"],
                "role_card_id": payload["role_card_id"],
                "friend_turn_count": len(strategies),
                "unique_primary_strategies": len(set(strategies)),
                "dominant_primary_strategy": dominant_strategy,
                "dominant_primary_strategy_share": round(dominant_share, 4),
                "same_primary_strategy_percentage": round(
                    same_primary_strategy_percentage, 2
                ),
                "all_same_primary_strategy": len(set(strategies)) == 1,
                "strategy_sequence": "|".join(strategies),
                "structure_sequence": "|".join(structures),
            }
        )

    overall_strategy_share = []
    for strategy, count in sorted(overall_strategy_counts.items()):
        overall_strategy_share.append(
            {
                "primary_strategy": strategy,
                "count": count,
                "share": round(count / total_friend_turns, 4)
                if total_friend_turns
                else 0.0,
                "percentage": round((count / total_friend_turns) * 100, 2)
                if total_friend_turns
                else 0.0,
            }
        )

    turn_position_structure_share = []
    for turn_index in sorted(structure_by_turn):
        turn_total = sum(structure_by_turn[turn_index].values())
        for structure, count in sorted(structure_by_turn[turn_index].items()):
            turn_position_structure_share.append(
                {
                    "friend_turn_index": turn_index,
                    "structure": structure,
                    "count": count,
                    "share": round(count / turn_total, 4) if turn_total else 0.0,
                    "percentage": round((count / turn_total) * 100, 2)
                    if turn_total
                    else 0.0,
                }
            )

    turn_position_strategy_share = []
    for turn_index in sorted(strategy_by_turn):
        turn_total = sum(strategy_by_turn[turn_index].values())
        for strategy, count in sorted(strategy_by_turn[turn_index].items()):
            turn_position_strategy_share.append(
                {
                    "friend_turn_index": turn_index,
                    "primary_strategy": strategy,
                    "count": count,
                    "share": round(count / turn_total, 4) if turn_total else 0.0,
                    "percentage": round((count / turn_total) * 100, 2)
                    if turn_total
                    else 0.0,
                }
            )

    run_summary = {
        "run_id": run_dir.name,
        "conversation_count": len(conversation_rows),
        "friend_turn_count": total_friend_turns,
        "average_same_primary_strategy_percentage": round(
            sum(same_strategy_percentages) / len(same_strategy_percentages), 2
        )
        if same_strategy_percentages
        else 0.0,
        "overall_strategy_share": overall_strategy_share,
        "turn_position_structure_share": turn_position_structure_share,
        "turn_position_strategy_share": turn_position_strategy_share,
    }

    _write_jsonl(tables_dir / "friend_turn_tags.jsonl", per_turn_rows)
    _write_csv(
        tables_dir / "friend_turn_tags.csv",
        per_turn_rows,
        [
            "run_id",
            "conversation_id",
            "role_card_id",
            "friend_turn_index",
            "message_position_1_based",
            "structure",
            "primary_strategy",
            "secondary_strategies",
            "confidence",
            "tagger_version",
            "taxonomy_version",
        ],
    )
    _write_jsonl(tables_dir / "conversation_metrics.jsonl", conversation_rows)
    _write_csv(
        tables_dir / "conversation_metrics.csv",
        conversation_rows,
        [
            "run_id",
            "conversation_id",
            "role_card_id",
            "friend_turn_count",
            "unique_primary_strategies",
            "dominant_primary_strategy",
            "dominant_primary_strategy_share",
            "same_primary_strategy_percentage",
            "all_same_primary_strategy",
            "strategy_sequence",
            "structure_sequence",
        ],
    )
    _write_json(reports_dir / "summary.json", run_summary)
    return run_summary
