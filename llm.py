"""Client for a local open-weight model served by Ollama. Free: cost is always 0."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    model: str
    tokens: int = 0
    cost: float = 0.0


class OllamaLLM:
    def __init__(self, model: str | None = None, host: str | None = None, timeout: int = 600):
        self.model = model or os.environ.get("LLM_MODEL", "qwen3:8b")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    def __call__(self, system: str, prompt: str) -> LLMResult:
        body = json.dumps({
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(f"{self.host}/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
        tokens = data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
        return LLMResult(text=data["message"]["content"], model=self.model, tokens=tokens)


def parse_json(text: str) -> dict:
    """Extract the first JSON object from a model reply (drops <think> blocks)."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("model reply contained no JSON object")
    return json.loads(text[start:end + 1])
