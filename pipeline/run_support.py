from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_MAX_TURNS_PER_SIDE


def timestamped_run_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


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
    skip_existing: bool = False,
    start_from: int | None = None,
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

    first_index = max(start_from or 1, 1)
    for index, role_card in enumerate(role_cards, start=1):
        if index < first_index:
            continue
        conversation_id = f"conv_{index:04d}"
        transcript_path = conversations_dir / f"{conversation_id}.json"
        tag_path = tags_dir / f"{conversation_id}.tags.json"
        if skip_existing and transcript_path.is_file() and tag_path.is_file():
            if verbose:
                print(f"Skipping {conversation_id} (already complete)", flush=True)
            continue
        if skip_existing and transcript_path.is_file() and not tag_path.is_file():
            if verbose:
                print(f"Tagging {conversation_id} (transcript exists)...", flush=True)
            tag_transcript_file(
                transcript_path=transcript_path, output_path=tag_path, tagger=turn_tagger
            )
            if verbose:
                print(
                    f"  -> tagged ({transcript_path.stat().st_size} bytes)",
                    flush=True,
                )
            continue
        if verbose:
            print(f"Running {conversation_id}...", flush=True)
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
            print(
                f"  -> completed ({transcript_path.stat().st_size} bytes)",
                flush=True,
            )


def resume_tagged_run(
    run_dir: Path,
    victim_agent: Any,
    friend_agent: Any,
    turn_tagger: Any,
    *,
    verbose: bool = False,
    max_turns_per_side: int | None = None,
    start_from: int | None = None,
) -> Path:
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    config_path = run_dir / "config" / "run-config.json"
    snapshot_path = run_dir / "role-cards" / "role_cards.snapshot.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing run config: {config_path}")
    if not snapshot_path.is_file():
        raise FileNotFoundError(f"Missing role card snapshot: {snapshot_path}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_id = config["run_id"]
    role_cards = json.loads(snapshot_path.read_text(encoding="utf-8"))
    limit = max_turns_per_side
    if limit is None and "max_turns_per_side" in config:
        limit = int(config["max_turns_per_side"])
    run_tagged_conversations(
        run_dir,
        run_id,
        role_cards,
        victim_agent,
        friend_agent,
        turn_tagger,
        verbose=verbose,
        max_turns_per_side=limit,
        skip_existing=start_from is None,
        start_from=start_from,
    )
    n = len(role_cards)
    print(f"Run directory: {run_dir}", flush=True)
    print(f"Wrote up to {n} conversations under {run_dir / 'conversations'}", flush=True)
    print(f"Wrote up to {n} tag files under {run_dir / 'tags'}", flush=True)
    return run_dir


def execute_timestamped_tagged_run(
    base_dir: Path,
    run_prefix: str,
    role_cards: list[dict[str, Any]],
    *,
    victim_agent_key: str,
    friend_agent_key: str,
    tagger_key: str,
    victim_prompt: str,
    friend_prompt: str,
    victim_agent: Any,
    friend_agent: Any,
    turn_tagger: Any,
    verbose: bool = False,
    max_turns_per_side: int | None = None,
) -> Path:
    run_id = timestamped_run_id(run_prefix)
    run_dir = base_dir / "runs" / run_id
    write_run_tree(
        run_dir,
        run_id=run_id,
        victim_agent_key=victim_agent_key,
        friend_agent_key=friend_agent_key,
        tagger_key=tagger_key,
        victim_prompt=victim_prompt,
        friend_prompt=friend_prompt,
        role_cards=role_cards,
        max_turns_per_side=max_turns_per_side,
    )
    run_tagged_conversations(
        run_dir,
        run_id,
        role_cards,
        victim_agent,
        friend_agent,
        turn_tagger,
        verbose=verbose,
        max_turns_per_side=max_turns_per_side,
    )
    n = len(role_cards)
    print(f"Run directory: {run_dir.resolve()}", flush=True)
    print(f"Wrote {n} conversations to {run_dir / 'conversations'}", flush=True)
    print(f"Wrote {n} tag files to {run_dir / 'tags'}", flush=True)
    return run_dir
