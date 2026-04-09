from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_MAX_TURNS_PER_SIDE
from .interfaces import FriendAgent, RoleCard, VictimAgent


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def run_conversation(
    role_card: RoleCard,
    output_path: str | Path,
    victim_agent: VictimAgent,
    friend_agent: FriendAgent,
    run_id: str,
    conversation_id: str,
    max_turns_per_side: int = DEFAULT_MAX_TURNS_PER_SIDE,
) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []

    opening_text = victim_agent.opening_message(role_card)
    messages.append({"speaker": "victim", "turn_index": 1, "text": opening_text})

    victim_turn_index = 1
    friend_turn_index = 0

    while friend_turn_index < max_turns_per_side:
        friend_turn_index += 1
        friend_text = friend_agent.reply(messages)
        messages.append(
            {"speaker": "friend", "turn_index": friend_turn_index, "text": friend_text}
        )

        if friend_turn_index >= max_turns_per_side:
            break

        victim_turn_index += 1
        victim_text = victim_agent.reply(role_card, messages)
        messages.append(
            {"speaker": "victim", "turn_index": victim_turn_index, "text": victim_text}
        )

    transcript = {
        "run_id": run_id,
        "conversation_id": conversation_id,
        "role_card_id": role_card["role_card_id"],
        "role_card_version": role_card.get("metadata", {}).get(
            "version", "role_card_v1"
        ),
        "victim_prompt_version": victim_agent.version,
        "friend_prompt_version": friend_agent.version,
        "models": {
            "victim": victim_agent.name,
            "friend": friend_agent.name,
        },
        "generation_config": {
            "victim_temperature": 0.0,
            "friend_temperature": 0.0,
            "max_turns_per_side": max_turns_per_side,
        },
        "termination": {
            "stop_reason": "completed_turn_limit",
            "completed_friend_turns": friend_turn_index,
            "completed_victim_turns": victim_turn_index,
        },
        "messages": messages,
        "status": "completed",
        "created_at": _utc_now(),
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(transcript, indent=2) + "\n", encoding="utf-8")
    return transcript
