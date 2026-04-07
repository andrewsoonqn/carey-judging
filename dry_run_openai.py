from __future__ import annotations

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from pipeline.runner import run_conversation
from pipeline.tagger import tag_transcript_file
from pipeline.openai_friend import OpenAIFriendAgent
from pipeline.openai_victim import OpenAIVictimAgent
from pipeline.openai_tagger import OpenAITurnTagger


BASE_DIR = Path(__file__).resolve().parent
RUN_ID = "run_demo_openai"


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
                "victim_agent": "openai_victim",
                "friend_agent": "openai_friend",
                "tagger": "openai_tagger",
                "max_turns_per_side": 3,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        config_dir / "victim-prompt.txt",
        "You are simulating a human conversation partner based on a structured role card. "
        "Speak naturally, stay emotionally consistent, respond directly to the friend, "
        "and do not artificially repeat the same complaint unless it fits the situation. "
        "Do not mention being an AI or simulation. Return plain conversational text only.\n",
    )
    write_text(
        config_dir / "friend-prompt.txt",
        "Respond naturally, briefly, and conversationally; do not analyze; keep the exchange going.\n",
    )
    write_text(config_dir / "taxonomy-version.txt", "taxonomy_v1\n")
    write_text(
        role_card_dir / "role_cards.snapshot.json",
        json.dumps(role_cards, indent=2) + "\n",
    )

    victim_agent = OpenAIVictimAgent()
    friend_agent = OpenAIFriendAgent()
    turn_tagger = OpenAITurnTagger()

    for index, role_card in enumerate(role_cards, start=1):
        conversation_id = f"conv_{index:04d}"
        transcript_path = conversations_dir / f"{conversation_id}.json"
        tag_path = tags_dir / f"{conversation_id}.tags.json"

        print(f"Running {conversation_id}...")
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
        print(f"  -> completed ({transcript_path.stat().st_size} bytes)")

    print(f"Wrote {len(role_cards)} conversations to {conversations_dir}")
    print(f"Wrote {len(role_cards)} tag files to {tags_dir}")


if __name__ == "__main__":
    main()
