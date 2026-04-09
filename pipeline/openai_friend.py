from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .openai_client import OpenAIChatClient


@dataclass
class OpenAIFriendAgent:
    name: str = "openai_friend"
    version: str = "friend_openai_v1"
    model: str = "gpt-5.4-mini"
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

    def reply(self, transcript: list[dict[str, Any]]) -> str:
        prompt = self._build_prompt(transcript)
        last_error: Exception | None = None
        for attempt in range(self.max_validation_retries + 1):
            content = self.client.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Respond naturally, briefly, and conversationally; do not analyze; keep the exchange going.",
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
                        f"OpenAI friend returned invalid output: {exc}"
                    ) from exc

        if last_error is not None:
            raise ValueError(f"OpenAI friend returned invalid output: {last_error}")
        raise ValueError("OpenAI friend returned invalid output.")

    def _build_prompt(self, transcript: list[dict[str, Any]]) -> str:
        transcript_json = "\n".join(
            f"{msg['speaker']}: {msg['text']}" for msg in transcript
        )
        return f"""Continue the conversation.

{transcript_json}"""

    def _validate_reply(self, text: str) -> str:
        if not text:
            raise ValueError("empty reply")
        return text
