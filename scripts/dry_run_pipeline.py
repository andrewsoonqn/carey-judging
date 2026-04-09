from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.role_cards import all_role_cards
from pipeline.run_support import run_tagged_conversations, write_run_tree
from pipeline.simple_components import (
    HeuristicTurnTagger,
    SimpleFriendAgent,
    SimpleVictimAgent,
)


BASE_DIR = _REPO_ROOT
RUN_ID = "run_demo_simple"


def main() -> None:
    role_cards = all_role_cards()
    run_dir = BASE_DIR / "runs" / RUN_ID

    write_run_tree(
        run_dir,
        run_id=RUN_ID,
        victim_agent_key="simple_victim",
        friend_agent_key="simple_friend",
        tagger_key="heuristic_tagger",
        victim_prompt=(
            "Simple deterministic victim stub. Swap `SimpleVictimAgent.reply()` "
            "for an AI-backed method later.\n"
        ),
        friend_prompt=(
            "Respond naturally, briefly, and conversationally. Do not analyze the "
            "conversation or explain what technique you are using. Keep the exchange going. "
            "Reply with plain conversational text only.\n"
        ),
        role_cards=role_cards,
    )

    run_tagged_conversations(
        run_dir,
        RUN_ID,
        role_cards,
        SimpleVictimAgent(),
        SimpleFriendAgent(),
        HeuristicTurnTagger(),
    )

    conversations_dir = run_dir / "conversations"
    tags_dir = run_dir / "tags"
    print(f"Wrote {len(role_cards)} conversations to {conversations_dir}")
    print(f"Wrote {len(role_cards)} tag files to {tags_dir}")


if __name__ == "__main__":
    main()
