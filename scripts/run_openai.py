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
from pipeline.prompts import BRIEF_FRIEND_PROMPT, OPENAI_ROLEPLAY_VICTIM_PROMPT
from pipeline.role_cards import all_role_cards
from pipeline.run_support import execute_timestamped_tagged_run


BASE_DIR = _REPO_ROOT
RUN_PREFIX = "run_demo_openai"


def main() -> None:
    role_cards = all_role_cards()
    execute_timestamped_tagged_run(
        BASE_DIR,
        RUN_PREFIX,
        role_cards,
        victim_agent_key="openai_victim",
        friend_agent_key="openai_friend",
        tagger_key="openai_tagger",
        victim_prompt=OPENAI_ROLEPLAY_VICTIM_PROMPT,
        friend_prompt=BRIEF_FRIEND_PROMPT,
        victim_agent=OpenAIVictimAgent(),
        friend_agent=OpenAIFriendAgent(),
        turn_tagger=OpenAITurnTagger(),
        verbose=True,
    )


if __name__ == "__main__":
    main()
