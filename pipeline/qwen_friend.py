from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class QwenCaregiverFriendAgent:
    name: str = "qwen_caregiver_friend"
    version: str = "friend_qwen_caregiver_v1"
    model_path: str = "qwen-caregiver-model"
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_new_tokens: int = 128
    temperature: float = 0.7
    _pipeline: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        from peft import PeftModel

        model_path = str(self._resolve_model_path())

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
        model = PeftModel.from_pretrained(
            base,
            model_path,
            local_files_only=True,
        )
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

    def _resolve_model_path(self) -> Path:
        configured_path = Path(self.model_path).expanduser()
        if configured_path.is_absolute():
            candidates = [configured_path]
        else:
            repo_root = Path(__file__).resolve().parent.parent
            candidates = [
                repo_root / configured_path,
                repo_root / "runs" / "run_demo_openai" / configured_path,
                Path.cwd() / configured_path,
                Path.cwd() / "runs" / "run_demo_openai" / configured_path,
            ]

        for candidate in candidates:
            if (candidate / "adapter_config.json").is_file():
                return candidate

        searched = "\n".join(str(candidate) for candidate in candidates)
        raise FileNotFoundError(
            "Could not find qwen adapter directory containing adapter_config.json. "
            f"Checked:\n{searched}"
        )
