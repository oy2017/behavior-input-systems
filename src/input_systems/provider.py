"""Gemini (OpenAI-compatible endpoint) client with thinking off, retries, concurrency and a JSONL cache."""

from __future__ import annotations

import hashlib
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


class GeminiClient:
    def __init__(self, model: str = "gemini-3.5-flash", cache_dir: Path = Path("outputs/cache"),
                 workers: int = 8, thinking: bool = False, max_retries: int = 14):
        self.model, self.workers, self.max_retries = model, workers, max_retries
        # Pro and Gemma models only run with thinking on (they reject reasoning_effort=none); Flash models default to off.
        self.thinking = thinking or any(t in model for t in ("pro", "gemma"))
        self.key = os.environ.get("GEMINI_API_KEY") or _read_env_key()
        if not self.key:
            raise RuntimeError("GEMINI_API_KEY not set (put it in .env)")
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / f"{model}.jsonl"
        self._lock = threading.Lock()
        self._cache: dict[str, str] = {}
        if self.cache_path.exists():
            for line in self.cache_path.read_text().splitlines():
                try:
                    d = json.loads(line); self._cache[d["k"]] = d["text"]
                except Exception:
                    pass
        self.calls = 0

    def _key(self, system: str, user: str, sample: int) -> str:
        return hashlib.sha1(f"{self.model}\x1f{self.thinking}\x1f{system}\x1f{user}\x1f{sample}".encode()).hexdigest()

    def _post(self, system: str, user: str) -> str:
        body = {"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if not self.thinking:
            body["reasoning_effort"] = "none"
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=(60 if self.thinking else 120)) as r:  # Pro calls occasionally stall; a normal Pro answer takes ~4 s
                    d = json.load(r)
                return d["choices"][0]["message"]["content"] or ""
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self.max_retries - 1:
                    time.sleep(min(120, 2 ** attempt) * (0.5 + random.random()))
                    continue
                raise
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt < self.max_retries - 1:
                    time.sleep(min(60, 2 ** attempt)); continue
                raise

    def complete(self, system: str, user: str, sample: int = 0) -> str:
        k = self._key(system, user, sample)
        with self._lock:
            if k in self._cache:
                return self._cache[k]
        text = self._post(system, user)
        with self._lock:
            self._cache[k] = text; self.calls += 1
            with open(self.cache_path, "a") as f:
                f.write(json.dumps({"k": k, "text": text}) + "\n")
        return text

    def map(self, jobs, fn):
        """jobs: iterable of items; fn(item) -> result (calls self.complete). Preserves order."""
        with ThreadPoolExecutor(self.workers) as ex:
            return list(ex.map(fn, jobs))


def _read_env_key() -> str | None:
    p = Path(__file__).resolve().parents[2] / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None
