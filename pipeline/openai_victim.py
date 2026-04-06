from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .openai_client import OpenAIChatClient


@dataclass
class OpenAIVictimAgent:
    name: str = "openai_victim"
    version: str = "victim_openai_v1"
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 60
    temperature: float = 0.7
    max_validation_retries: int = 2

    def __post_init__(self) -> None:
        self.client = OpenAIChatClient(
            model=self.model,
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
        )

    def opening_message(self, role_card: dict[str, Any]) -> str:
        return role_card["conversation_seed"]["opening_message"]

    def reply(self, role_card: dict[str, Any], transcript: list[dict[str, Any]]) -> str:
        prompt = self._build_prompt(role_card, transcript)
        last_error: Exception | None = None
        for attempt in range(self.max_validation_retries + 1):
            content = self.client.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are simulating a human conversation partner based on a structured role card. "
                            "Speak naturally, stay emotionally consistent, respond directly to the friend, "
                            "and do not artificially repeat the same complaint unless it fits the situation. "
                            "Do not mention being an AI or simulation. Return plain conversational text only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            ).strip()
            try:
                return self._validate_reply(content)
            except ValueError as exc:
                last_error = exc
                if attempt >= self.max_validation_retries:
                    raise ValueError(
                        f"OpenAI victim returned invalid output: {exc}"
                    ) from exc

        if last_error is not None:
            raise ValueError(f"OpenAI victim returned invalid output: {last_error}")
        raise ValueError("OpenAI victim returned invalid output.")

    def _build_prompt(
        self, role_card: dict[str, Any], transcript: list[dict[str, Any]]
    ) -> str:
        role_card_json = json.dumps(role_card, indent=2)
        transcript_json = json.dumps(transcript, indent=2)
        return f"""
Role card:
{role_card_json}

Conversation so far:
{transcript_json}

Write the victim's next reply.

Rules:
- Stay in character.
- Keep the reply concise, usually 1 to 3 sentences.
- Respond directly to the latest friend message.
- Be realistic, emotionally coherent, and conversational.
- Do not use labels, bullets, or JSON.
""".strip()

    def _validate_reply(self, text: str) -> str:
        if not text:
            raise ValueError("empty reply")
        if len(text.split()) > 120:
            raise ValueError("reply is too long")
        blocked_markers = [
            "as an ai",
            "i am an ai",
            "language model",
            "role card",
            "json",
            "simulation",
            "assistant:",
            "victim:",
        ]
        lowered = text.lower()
        for marker in blocked_markers:
            if marker in lowered:
                raise ValueError(f"reply contains blocked marker: {marker}")
        return text
