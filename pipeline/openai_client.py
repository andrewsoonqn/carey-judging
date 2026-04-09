from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from typing import Any


def _strip_chat_completions_suffix(url: str) -> str:
    u = url.rstrip("/")
    suffix = "/chat/completions"
    if u.endswith(suffix):
        return u[: -len(suffix)].rstrip("/") or u
    return u


class OpenAIChatClient:
    def __init__(
        self,
        *,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: int = 60,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
    ) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        raw_model = os.environ.get("OPENAI_MODEL", model)
        self.model = str(raw_model).strip() if raw_model is not None else ""
        raw_base = os.environ.get("OPENAI_BASE_URL", base_url)
        self.base_url = _strip_chat_completions_suffix(str(raw_base).strip())
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def create_chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float = 0,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        if not self.model:
            raise RuntimeError("OpenAI model name is empty (check OPENAI_MODEL).")

        temp = float(temperature)
        if not math.isfinite(temp):
            raise RuntimeError("OpenAI temperature must be a finite number.")

        normalized_messages: list[dict[str, str]] = []
        for i, m in enumerate(messages):
            role = m.get("role")
            content = m.get("content")
            if not isinstance(role, str):
                raise RuntimeError(
                    f"messages[{i}].role must be str, not {type(role).__name__}"
                )
            if not isinstance(content, str):
                raise RuntimeError(
                    f"messages[{i}].content must be str, not {type(content).__name__}"
                )
            normalized_messages.append({"role": role, "content": content})

        payload = {
            "model": self.model,
            "temperature": temp,
            "messages": normalized_messages,
        }
        response_json = self._post_json(f"{self.base_url}/chat/completions", payload)
        return response_json["choices"][0]["message"]["content"]

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                text = json.dumps(
                    payload,
                    ensure_ascii=True,
                    allow_nan=False,
                    separators=(",", ":"),
                )
            except (TypeError, ValueError) as exc:
                raise RuntimeError(
                    f"OpenAI request body is not JSON-serializable: {exc}"
                ) from exc
            data = text.encode("utf-8")
            request = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(
                    request, timeout=self.timeout_seconds
                ) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:  # pragma: no cover - network path
                body = exc.read().decode("utf-8", errors="replace")
                last_error = RuntimeError(f"OpenAI API error {exc.code}: {body}")
                if (
                    not self._is_retryable_status(exc.code)
                    or attempt >= self.max_retries
                ):
                    raise last_error from exc
            except urllib.error.URLError as exc:  # pragma: no cover - network path
                last_error = RuntimeError(f"OpenAI API connection error: {exc.reason}")
                if attempt >= self.max_retries:
                    raise last_error from exc

            time.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))

        if last_error is not None:
            raise last_error
        raise RuntimeError("OpenAI API request failed without an explicit error.")

    def _is_retryable_status(self, status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code < 600
