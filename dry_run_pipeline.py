from __future__ import annotations

import json
from pathlib import Path

from pipeline.runner import run_conversation
from pipeline.simple_components import (
    HeuristicTurnTagger,
    SimpleFriendAgent,
    SimpleVictimAgent,
)
from pipeline.tagger import tag_transcript_file


BASE_DIR = Path(__file__).resolve().parent
RUN_ID = "run_demo_simple"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    role_cards_path = BASE_DIR / "sample_role_cards.json"
    role_cards = json.loads(role_cards_path.read_text(encoding="utf-8"))

    run_dir = BASE_DIR / "runs" / RUN_ID
    config_dir = run_dir / "config"
    role_card_dir = run_dir / "role-cards"
    conversations_dir = run_dir / "conversations"
    tags_dir = run_dir / "tags"

    write_text(
        config_dir / "run-config.json",
        json.dumps(
            {
                "run_id": RUN_ID,
                "victim_agent": "simple_victim",
                "friend_agent": "simple_friend",
                "tagger": "heuristic_tagger",
                "max_turns_per_side": 3,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        config_dir / "victim-prompt.txt",
        "Simple deterministic victim stub. Swap `SimpleVictimAgent.reply()` for an AI-backed method later.\n",
    )
    write_text(
        config_dir / "friend-prompt.txt",
        "Respond naturally, briefly, and conversationally. Do not analyze the conversation or explain what technique you are using. Keep the exchange going. Reply with plain conversational text only.\n",
    )
    write_text(config_dir / "taxonomy-version.txt", "taxonomy_v1\n")
    write_text(
        role_card_dir / "role_cards.snapshot.json",
        json.dumps(role_cards, indent=2) + "\n",
    )

    victim_agent = SimpleVictimAgent()
    friend_agent = SimpleFriendAgent()
    turn_tagger = HeuristicTurnTagger()

    for index, role_card in enumerate(role_cards, start=1):
        conversation_id = f"conv_{index:04d}"
        transcript_path = conversations_dir / f"{conversation_id}.json"
        tag_path = tags_dir / f"{conversation_id}.tags.json"

        run_conversation(
            role_card=role_card,
            output_path=transcript_path,
            victim_agent=victim_agent,
            friend_agent=friend_agent,
            run_id=RUN_ID,
            conversation_id=conversation_id,
        )
        tag_transcript_file(
            transcript_path=transcript_path, output_path=tag_path, tagger=turn_tagger
        )

    print(f"Wrote {len(role_cards)} conversations to {conversations_dir}")
    print(f"Wrote {len(role_cards)} tag files to {tags_dir}")


if __name__ == "__main__":
    main()
