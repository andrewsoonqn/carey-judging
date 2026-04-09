from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.role_cards import all_role_cards
from pipeline.run_support import execute_timestamped_tagged_run
from pipeline.simple_components import (
    HeuristicTurnTagger,
    SimpleFriendAgent,
    SimpleVictimAgent,
)


BASE_DIR = _REPO_ROOT
RUN_PREFIX = "run_demo_simple"


def main() -> None:
    role_cards = all_role_cards()
    execute_timestamped_tagged_run(
        BASE_DIR,
        RUN_PREFIX,
        role_cards,
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
        victim_agent=SimpleVictimAgent(),
        friend_agent=SimpleFriendAgent(),
        turn_tagger=HeuristicTurnTagger(),
    )


if __name__ == "__main__":
    main()
