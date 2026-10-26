"""Replay recorded LLM transcripts so the full pipeline runs in CI without a model.

A cassette directory is a copy of a run's `llm_log/`. Each file holds one stage's transcript
(attempts in order). `ReplayClient` serves the recorded responses for a stage in order; any
request for a stage with no recording, or more attempts than recorded, fails loudly.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from mmf.llm.base import LLMResponse


class ReplayClient:
    backend = "replay"

    def __init__(self, cassette_dir: Path, model: str = "replay") -> None:
        self.model = model
        self._by_system: dict[str, list[str]] = defaultdict(list)
        self._pos: dict[str, int] = defaultdict(int)
        for f in sorted(cassette_dir.glob("*.json")):
            d = json.loads(f.read_text())
            for t in d["transcript"]:
                self._by_system[d["stage"]].append(t["response"])
        self._stage_order = [json.loads(f.read_text())["stage"] for f in sorted(cassette_dir.glob("*.json"))]
        self._cursor = 0

    def model_digest(self) -> str | None:
        return "replay"

    def complete_json(
        self, system: str, user: str, json_schema: dict[str, Any], *, seed: int, temperature: float
    ) -> LLMResponse:
        # Stages are consumed in recorded order; within a stage, attempts in order.
        while self._cursor < len(self._stage_order):
            stage = self._stage_order[self._cursor]
            if self._pos[stage] < len(self._by_system[stage]):
                text = self._by_system[stage][self._pos[stage]]
                self._pos[stage] += 1
                if self._pos[stage] == len(self._by_system[stage]):
                    self._cursor += 1
                return LLMResponse(text=text, model=self.model, model_digest="replay")
            self._cursor += 1
        raise RuntimeError("cassette exhausted: pipeline requested more LLM calls than were recorded")
