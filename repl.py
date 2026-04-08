from __future__ import annotations

import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from pipeline.qwen_friend import QwenCaregiverFriendAgent
from pipeline.openai_friend import OpenAIFriendAgent


def main() -> None:
    print("Loading agents...")
    qwen_agent = QwenCaregiverFriendAgent()
    openai_agent = OpenAIFriendAgent()
    print("Agents loaded.\n")

    agents = {
        "qwen": qwen_agent,
        "openai": openai_agent,
    }
    current_agent = "qwen"
    transcript: list[dict[str, str]] = []

    print(f"REPL started. Current agent: {current_agent}")
    print("Commands:")
    print("  :switch   - switch between qwen/openai")
    print("  :reset    - reset conversation transcript")
    print("  :quit     - exit")
    print("  :dump     - print transcript to console")
    print()

    while True:
        try:
            user_input = input(f"[{current_agent}] You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.startswith(":"):
            cmd = user_input[1:].lower()
            if cmd == "quit":
                print("Bye!")
                break
            elif cmd == "switch":
                current_agent = "openai" if current_agent == "qwen" else "qwen"
                print(f"Switched to {current_agent}")
            elif cmd == "reset":
                transcript = []
                print("Transcript reset.")
            elif cmd == "dump":
                print("\n--- Transcript ---")
                for msg in transcript:
                    print(f"{msg['speaker']}: {msg['text']}")
                print("--- End ---\n")
            else:
                print(f"Unknown command: {cmd}")
            continue

        transcript.append({"speaker": "user", "text": user_input})

        agent = agents[current_agent]
        print(f"[{current_agent}] Thinking...")
        try:
            response = agent.reply(transcript)
        except Exception as e:
            print(f"Error: {e}")
            transcript.pop()
            continue

        transcript.append({"speaker": "friend", "text": response})
        print(f"[{current_agent}] Friend: {response}\n")


if __name__ == "__main__":
    main()
