"""The single entry point for model calls: prompt -> JSON -> pydantic -> validators -> retry.

Every call is logged (request, raw response, parse/validation errors) to `log_dir`, and a
`LLMCallRecord` is returned alongside the parsed object for the run manifest.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from mmf.llm.base import LLMClient
from mmf.llm.prompts import Prompt
from mmf.schemas.run import LLMCallRecord

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

Validator = Callable[[T], list[str]]
"""Returns a list of human-readable problems; empty list means the object is accepted."""


class GenerationFailedError(RuntimeError):
    def __init__(self, stage: str, problems: list[str], attempts: int) -> None:
        super().__init__(f"{stage}: no valid output after {attempts} attempts; last problems: {problems}")
        self.stage, self.problems, self.attempts = stage, problems, attempts


def generate(
    client: LLMClient,
    prompt: Prompt,
    user_text: str,
    output_model: type[T],
    *,
    stage: str,
    seed: int,
    temperature: float,
    validators: list[Validator[T]] | None = None,
    max_retries: int = 3,
    log_dir: Path | None = None,
) -> tuple[T, LLMCallRecord]:
    validators = validators or []
    schema = output_model.model_json_schema()
    log_path = _log_path(log_dir, stage)
    transcript: list[dict[str, object]] = []
    user = user_text
    problems: list[str] = []

    for attempt in range(1, max_retries + 2):
        resp = client.complete_json(prompt.system, user, schema, seed=seed, temperature=temperature)
        entry: dict[str, object] = {
            "attempt": attempt,
            "user": user,
            "response": resp.text,
            "usage": resp.usage,
        }
        try:
            obj = output_model.model_validate_json(resp.text)
            problems = [p for v in validators for p in v(obj)]
        except (ValidationError, json.JSONDecodeError) as e:
            obj = None
            problems = [f"output did not parse as {output_model.__name__}: {e}"]
        entry["problems"] = problems
        transcript.append(entry)
        if log_path:
            log_path.write_text(
                json.dumps(
                    {
                        "stage": stage,
                        "prompt": prompt.name,
                        "system": prompt.system,
                        "transcript": transcript,
                    },
                    indent=2,
                )
            )
        if obj is not None and not problems:
            record = _record(stage, prompt, client, seed, temperature, attempt, True, log_path)
            return obj, record
        log.warning("%s attempt %d rejected: %s", stage, attempt, problems[:3])
        user = (
            user_text
            + "\n\nYour previous answer was rejected for these reasons; fix ALL of them:\n- "
            + "\n- ".join(problems)
        )

    _record(stage, prompt, client, seed, temperature, max_retries + 1, False, log_path)
    raise GenerationFailedError(stage, problems, max_retries + 1)


def _log_path(log_dir: Path | None, stage: str) -> Path | None:
    if log_dir is None:
        return None
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    return log_dir / f"{ts}_{stage}.json"


def _record(
    stage: str,
    prompt: Prompt,
    client: LLMClient,
    seed: int,
    temperature: float,
    attempts: int,
    ok: bool,
    log_path: Path | None,
) -> LLMCallRecord:
    return LLMCallRecord(
        stage=stage,
        prompt_name=prompt.name,
        prompt_sha256=prompt.sha256,
        model=client.model,
        model_digest=client.model_digest(),
        seed=seed,
        temperature=temperature,
        attempts=attempts,
        ok=ok,
        log_file=str(log_path) if log_path else "",
    )


def make_client(backend: str, model: str, *, ollama_host: str, openai_api_key: str | None, num_ctx: int) -> LLMClient:
    if backend == "ollama":
        from mmf.llm.ollama import OllamaClient

        return OllamaClient(model, host=ollama_host, num_ctx=num_ctx)
    if backend == "openai":
        from mmf.llm.openai import OpenAIClient

        return OpenAIClient(model, api_key=openai_api_key)
    raise ValueError(f"unknown backend {backend!r}")
