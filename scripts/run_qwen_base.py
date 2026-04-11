from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

load_dotenv()

from pipeline.openai_tagger import OpenAITurnTagger
from pipeline.openai_victim import OpenAIVictimAgent
from pipeline.prompts import BRIEF_FRIEND_PROMPT, OPENAI_ROLEPLAY_VICTIM_PROMPT
from pipeline.qwen_friend import QwenCaregiverFriendAgent
from pipeline.role_cards import all_role_cards
from pipeline.run_support import execute_timestamped_tagged_run, resume_tagged_run


BASE_DIR = _REPO_ROOT
RUN_PREFIX = "run_demo_qwen_base"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Qwen2.5-7B-Instruct base (no PEFT) friend + OpenAI victim/tagger pipeline."
    )
    parser.add_argument(
        "--resume",
        type=Path,
        metavar="RUN_DIR",
        help="Resume a run (path under runs/, e.g. runs/run_demo_qwen_base_20260101_120000_000000)",
    )
    parser.add_argument(
        "--start",
        type=int,
        metavar="N",
        help="Start from conversation N (1-based). Requires --resume to identify the run directory.",
    )
    args = parser.parse_args()

    if args.start is not None and args.resume is None:
        parser.error("--start requires --resume to identify the run directory")

    victim_agent = OpenAIVictimAgent()
    friend_agent = QwenCaregiverFriendAgent(
        use_peft_adapter=False,
        name="qwen_base_friend",
        version="friend_qwen_base_v1",
    )
    turn_tagger = OpenAITurnTagger()

    if args.resume is not None:
        run_dir = args.resume
        if not run_dir.is_absolute():
            run_dir = BASE_DIR / run_dir
        resume_tagged_run(
            run_dir,
            victim_agent,
            friend_agent,
            turn_tagger,
            verbose=True,
            start_from=args.start,
        )
        return

    role_cards = all_role_cards()
    execute_timestamped_tagged_run(
        BASE_DIR,
        RUN_PREFIX,
        role_cards,
        victim_agent_key="openai_victim",
        friend_agent_key="qwen_base_friend",
        tagger_key="openai_tagger",
        victim_prompt=OPENAI_ROLEPLAY_VICTIM_PROMPT,
        friend_prompt=BRIEF_FRIEND_PROMPT,
        victim_agent=victim_agent,
        friend_agent=friend_agent,
        turn_tagger=turn_tagger,
        verbose=True,
    )


if __name__ == "__main__":
    main()
