from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_MAX_TURNS_PER_SIDE


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_run_tree(
    run_dir: Path,
    *,
    run_id: str,
    victim_agent_key: str,
    friend_agent_key: str,
    tagger_key: str,
    victim_prompt: str,
    friend_prompt: str,
    role_cards: list[dict[str, Any]],
    max_turns_per_side: int | None = None,
) -> None:
    limit = (
        max_turns_per_side
        if max_turns_per_side is not None
        else DEFAULT_MAX_TURNS_PER_SIDE
    )
    config_dir = run_dir / "config"
    role_card_dir = run_dir / "role-cards"
    write_text(
        config_dir / "run-config.json",
        json.dumps(
            {
                "run_id": run_id,
                "victim_agent": victim_agent_key,
                "friend_agent": friend_agent_key,
                "tagger": tagger_key,
                "max_turns_per_side": limit,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(config_dir / "victim-prompt.txt", victim_prompt)
    write_text(config_dir / "friend-prompt.txt", friend_prompt)
    write_text(config_dir / "taxonomy-version.txt", "taxonomy_v1\n")
    write_text(
        role_card_dir / "role_cards.snapshot.json",
        json.dumps(role_cards, indent=2) + "\n",
    )


def run_tagged_conversations(
    run_dir: Path,
    run_id: str,
    role_cards: list[dict[str, Any]],
    victim_agent: Any,
    friend_agent: Any,
    turn_tagger: Any,
    *,
    max_turns_per_side: int | None = None,
    verbose: bool = False,
) -> None:
    from .runner import run_conversation
    from .tagger import tag_transcript_file

    limit = (
        max_turns_per_side
        if max_turns_per_side is not None
        else DEFAULT_MAX_TURNS_PER_SIDE
    )
    conversations_dir = run_dir / "conversations"
    tags_dir = run_dir / "tags"

    for index, role_card in enumerate(role_cards, start=1):
        conversation_id = f"conv_{index:04d}"
        transcript_path = conversations_dir / f"{conversation_id}.json"
        tag_path = tags_dir / f"{conversation_id}.tags.json"
        if verbose:
            print(f"Running {conversation_id}...")
        run_conversation(
            role_card=role_card,
            output_path=transcript_path,
            victim_agent=victim_agent,
            friend_agent=friend_agent,
            run_id=run_id,
            conversation_id=conversation_id,
            max_turns_per_side=limit,
        )
        tag_transcript_file(
            transcript_path=transcript_path, output_path=tag_path, tagger=turn_tagger
        )
        if verbose:
            print(f"  -> completed ({transcript_path.stat().st_size} bytes)")
