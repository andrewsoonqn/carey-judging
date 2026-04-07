from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .openai_client import OpenAIChatClient


ALLOWED_STRUCTURES = {"question", "reflection", "suggestion", "hybrid"}
ALLOWED_PRIMARY_STRATEGIES = {
    "probe",
    "reflect",
    "validate",
    "reframe",
    "suggest",
    "plan",
    "support",
    "other",
}


@dataclass
class OpenAITurnTagger:
    name: str = "openai_tagger"
    version: str = "tagger_openai_v1"
    taxonomy_version: str = "taxonomy_v1"
    model: str = "gpt-5.4-nano"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 60
    max_validation_retries: int = 2

    def __post_init__(self) -> None:
        self.client = OpenAIChatClient(
            model=self.model,
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
        )

    def tag_turn(
        self,
        transcript: list[dict[str, Any]],
        friend_message: dict[str, Any],
        message_position_1_based: int,
    ) -> dict[str, Any]:
        prompt = self._build_prompt(transcript, friend_message)

        last_error: Exception | None = None
        for attempt in range(self.max_validation_retries + 1):
            content = self.client.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict JSON tagger for friend conversation turns. "
                            "Return only valid JSON matching the requested schema."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            try:
                parsed = self._parse_json(content)
                validated = self._validate_payload(parsed)
                return {
                    "friend_turn_index": friend_message["turn_index"],
                    "message_position_1_based": message_position_1_based,
                    "text": friend_message["text"],
                    "structure": validated["structure"],
                    "primary_strategy": validated["primary_strategy"],
                    "secondary_strategies": validated["secondary_strategies"],
                    "notes": validated["notes"],
                    "confidence": validated["confidence"],
                }
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt >= self.max_validation_retries:
                    raise ValueError(
                        f"OpenAI tagger returned invalid output: {exc}"
                    ) from exc

        if last_error is not None:
            raise ValueError(f"OpenAI tagger returned invalid output: {last_error}")
        raise ValueError("OpenAI tagger returned invalid output.")

    def _build_prompt(
        self, transcript: list[dict[str, Any]], friend_message: dict[str, Any]
    ) -> str:
        transcript_json = json.dumps(transcript, indent=2)
        return f"""
Tag the final friend turn in the transcript.

Allowed structure labels:
- question
- reflection
- suggestion
- hybrid

Allowed primary_strategy labels:
- probe
- reflect
- validate
- reframe
- suggest
- plan
- support
- other

Rules:
- Choose exactly one structure.
- Choose exactly one primary_strategy.
- secondary_strategies must be a JSON array and may be empty.
- Do not repeat the primary strategy inside secondary_strategies.
- confidence must be a number between 0 and 1.
- Prefer the simplest valid annotation.
- Return JSON only.

Transcript so far:
{transcript_json}

Target friend turn text:
{friend_message["text"]}

Return this JSON shape:
{{
  "structure": "...",
  "primary_strategy": "...",
  "secondary_strategies": ["..."],
  "notes": "short explanation",
  "confidence": 0.0
}}
""".strip()

    def _parse_json(self, content: str) -> dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            lines = [
                line for line in content.splitlines() if not line.startswith("```")
            ]
            content = "\n".join(lines).strip()
        return json.loads(content)

    def _validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        structure = payload["structure"]
        primary_strategy = payload["primary_strategy"]
        secondary_strategies = payload.get("secondary_strategies", [])
        notes = payload.get("notes", "")
        confidence = payload.get("confidence", 0.0)

        if structure not in ALLOWED_STRUCTURES:
            raise ValueError(f"invalid structure: {structure}")
        if primary_strategy not in ALLOWED_PRIMARY_STRATEGIES:
            raise ValueError(f"invalid primary_strategy: {primary_strategy}")
        if not isinstance(secondary_strategies, list):
            raise ValueError("secondary_strategies must be a list")

        normalized_secondary: list[str] = []
        for value in secondary_strategies:
            if value not in ALLOWED_PRIMARY_STRATEGIES:
                raise ValueError(f"invalid secondary strategy: {value}")
            if value == primary_strategy:
                raise ValueError("secondary_strategies cannot repeat primary_strategy")
            if value not in normalized_secondary:
                normalized_secondary.append(value)

        if not isinstance(notes, str):
            raise ValueError("notes must be a string")
        if not isinstance(confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        return {
            "structure": structure,
            "primary_strategy": primary_strategy,
            "secondary_strategies": normalized_secondary,
            "notes": notes,
            "confidence": confidence,
        }
