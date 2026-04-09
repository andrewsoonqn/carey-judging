from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

load_dotenv()

from pipeline.openai_friend import OpenAIFriendAgent
from pipeline.openai_tagger import OpenAITurnTagger
from pipeline.openai_victim import OpenAIVictimAgent
from pipeline.role_cards import all_role_cards
from pipeline.run_support import run_tagged_conversations, write_run_tree


BASE_DIR = _REPO_ROOT
RUN_ID = "run_demo_openai"


def main() -> None:
    role_cards = all_role_cards()
    run_dir = BASE_DIR / "runs" / RUN_ID

    write_run_tree(
        run_dir,
        run_id=RUN_ID,
        victim_agent_key="openai_victim",
        friend_agent_key="openai_friend",
        tagger_key="openai_tagger",
        victim_prompt=(
            "You are simulating a human conversation partner based on a structured role card. "
            "Speak naturally, stay emotionally consistent, respond directly to the friend, "
            "and do not artificially repeat the same complaint unless it fits the situation. "
            "Do not mention being an AI or simulation. Return plain conversational text only.\n"
        ),
        friend_prompt=(
            "Respond naturally, briefly, and conversationally; do not analyze; "
            "keep the exchange going.\n"
        ),
        role_cards=role_cards,
    )

    run_tagged_conversations(
        run_dir,
        RUN_ID,
        role_cards,
        OpenAIVictimAgent(),
        OpenAIFriendAgent(),
        OpenAITurnTagger(),
        verbose=True,
    )

    conversations_dir = run_dir / "conversations"
    tags_dir = run_dir / "tags"
    print(f"Wrote {len(role_cards)} conversations to {conversations_dir}")
    print(f"Wrote {len(role_cards)} tag files to {tags_dir}")


if __name__ == "__main__":
    main()
