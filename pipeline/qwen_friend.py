from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ADAPTER_CONFIG_NAME = "adapter_config.json"


def _load_pretrained_with_local_fallback(
    loader: Any,
    pretrained_id: str,
    **kwargs: Any,
) -> Any:
    try:
        return loader.from_pretrained(
            pretrained_id,
            local_files_only=True,
            **kwargs,
        )
    except OSError:
        return loader.from_pretrained(pretrained_id, **kwargs)


@dataclass
class QwenCaregiverFriendAgent:
    name: str = "qwen_caregiver_friend"
    version: str = "friend_qwen_caregiver_v1"
    model_path: str = "qwen-caregiver-model"
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    use_peft_adapter: bool = True
    max_new_tokens: int = 128
    temperature: float = 0.7
    _pipeline: Any = field(default=None, init=False, repr=False)
    _tokenizer: Any = field(default=None, init=False, repr=False)
    _generation_config: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            GenerationConfig,
            pipeline,
        )

        device_map = self._get_device_map()

        self._tokenizer = self._load_tokenizer(AutoTokenizer)
        base = self._load_base_model(AutoModelForCausalLM, device_map)
        if self.use_peft_adapter:
            from peft import PeftModel

            model_path = str(self._resolve_model_path())
            model = PeftModel.from_pretrained(
                base,
                model_path,
                local_files_only=True,
            )
        else:
            model = base
        model.eval()

        self._generation_config = GenerationConfig(
            max_new_tokens=self.max_new_tokens,
            do_sample=self.temperature > 0,
            temperature=self.temperature if self.temperature > 0 else 1.0,
            eos_token_id=self._tokenizer.eos_token_id,
            pad_token_id=self._tokenizer.eos_token_id,
        )

        self._pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=self._tokenizer,
        )

    def _model_directory_candidates(self) -> list[Path]:
        configured_path = Path(self.model_path).expanduser()
        if configured_path.is_absolute():
            return [configured_path]
        repo_root = Path(__file__).resolve().parent.parent
        demo_run = Path("runs") / "run_demo_openai"
        return [
            repo_root / configured_path,
            repo_root / demo_run / configured_path,
            Path.cwd() / configured_path,
            Path.cwd() / demo_run / configured_path,
        ]

    def reply(self, transcript: list[dict[str, Any]]) -> str:
        messages = [
            {
                "role": "system",
                "content": "Respond naturally, briefly, and conversationally; do not analyze; keep the exchange going.",
            },
            {"role": "user", "content": self._build_prompt(transcript)},
        ]

        prompt = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        result = self._pipeline(
            prompt,
            generation_config=self._generation_config,
            return_full_text=False,
        )

        return result[0]["generated_text"].strip()

    def _build_prompt(self, transcript: list[dict[str, Any]]) -> str:
        transcript_text = "\n".join(
            f"{msg['speaker']}: {msg['text']}" for msg in transcript
        )
        return f"Continue the conversation.\n\n{transcript_text}"

    def _resolve_model_path(self) -> Path:
        candidates = self._model_directory_candidates()
        for candidate in candidates:
            if (candidate / ADAPTER_CONFIG_NAME).is_file():
                return candidate

        searched = "\n".join(str(candidate) for candidate in candidates)
        raise FileNotFoundError(
            "Could not find qwen adapter directory containing adapter_config.json. "
            f"Checked:\n{searched}"
        )

    def _get_device_map(self) -> str | None:
        import torch

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="CUDA initialization: The NVIDIA driver on your system is too old.*",
            )
            has_cuda = torch.cuda.is_available()

        return "auto" if has_cuda else None

    def _load_tokenizer(self, auto_tokenizer: Any) -> Any:
        return _load_pretrained_with_local_fallback(
            auto_tokenizer,
            self.base_model,
            trust_remote_code=True,
        )

    def _load_base_model(self, auto_model: Any, device_map: str | None) -> Any:
        model_kwargs: dict[str, Any] = {
            "torch_dtype": "auto",
            "trust_remote_code": True,
        }
        if device_map is not None:
            model_kwargs["device_map"] = device_map
        return _load_pretrained_with_local_fallback(
            auto_model,
            self.base_model,
            **model_kwargs,
        )
