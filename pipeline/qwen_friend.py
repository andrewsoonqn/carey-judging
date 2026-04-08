from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class QwenCaregiverFriendAgent:
    name: str = "qwen_caregiver_friend"
    version: str = "friend_qwen_caregiver_v1"
    model_path: str = "runs/run_demo_openai/qwen-caregiver-model"
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_new_tokens: int = 128
    temperature: float = 0.7
    _pipeline: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        from peft import PeftModel

        model_path = self.model_path
        if not Path(model_path).is_absolute():
            model_path = str(Path(__file__).resolve().parent.parent / model_path)

        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            trust_remote_code=True,
        )
        base = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(base, model_path)
        model.eval()

        self._pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",
        )

    def reply(self, transcript: list[dict[str, Any]]) -> str:
        messages = [
            {
                "role": "system",
                "content": "Respond naturally, briefly, and conversationally; do not analyze; keep the exchange going.",
            },
            {"role": "user", "content": self._build_prompt(transcript)},
        ]

        result = self._pipeline(
            messages,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            return_full_text=False,
        )

        return result[0]["generated_text"].strip()

    def _build_prompt(self, transcript: list[dict[str, Any]]) -> str:
        transcript_text = "\n".join(
            f"{msg['speaker']}: {msg['text']}" for msg in transcript
        )
        return f"Continue the conversation.\n\n{transcript_text}"
