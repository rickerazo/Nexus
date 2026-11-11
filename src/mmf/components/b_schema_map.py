"""Component B: manuscript concepts -> codebook variables, per source."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, NamedTuple

from pydantic import BaseModel, Field

from mmf.components.common import source_groups, sources_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import StageInputError, generate
from mmf.schemas.dataset import ConceptMapping, DataSource, SchemaMap
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

PROMPTS = ("b_schema_map",)


def prompt_hashes() -> list[str]:
    """sha256 of every prompt this component uses; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


COMPAT = {"direct", "proxy", "derived", "none"}


class MappingOut(BaseModel):
    """LLM-facing ConceptMapping: every field required, so a grammar-constrained decoder cannot skip one."""

    concept: str
    source_id: str
    variable: str | None = Field(description="Codebook variable name, or null if no equivalent.")
    compatibility: str = Field(description="One of: direct, proxy, derived, none.")
    rationale: str


class SchemaMapOut(BaseModel):
    """LLM-facing SchemaMap. With defaults, the model returned source summaries and no mappings, and passed."""

    mappings: list[MappingOut]
    source_summaries: dict[str, str] = Field(description="Per-source capability summary.")


MapLike = SchemaMap | SchemaMapOut


class Concept(NamedTuple):
    """A concept sent to B: its name exactly as A extracted it, its role, and how it was operationalized."""

    name: str
    role: str
    operationalization: str


def canonical_concept(returned: str, batch: Sequence[Concept]) -> str | None:
    """The sent concept name that `returned` refers to, or None.

    Accepted, in order: an exact match; a case-insensitive match; the name with a trailing
    "as <role>" removed, where <role> is the role that concept was sent with. Anything else is rejected.
    """
    if any(c.name == returned for c in batch):
        return returned
    low = returned.strip().lower()
    for c in batch:
        if c.name.lower() == low:
            return c.name
    for c in batch:
        role = re.escape(c.role.lower()).replace("_", "[_ ]")
        stripped = re.sub(rf"\s+as\s+(?:an?\s+)?{role}$", "", low)
        if stripped != low and stripped == c.name.lower():
            return c.name
    return None


_SPLIT = re.compile(r"[,;]")


def split_names(value: str, source: DataSource) -> list[str]:
    """The variable names in one `variable` field: itself when it is a documented name, else its comma- or
    semicolon-separated parts (the model sometimes lists several real variables in one field)."""
    if source.lookup(value) is not None or not _SPLIT.search(value):
        return [value.strip()]
    return [p.strip() for p in _SPLIT.split(value) if p.strip()]


def map_validator(
    sources: dict[str, DataSource], batch: Sequence[Concept] | None = None
) -> Callable[[MapLike], list[str]]:
    def check(m: MapLike) -> list[str]:
        problems = []
        if batch and not m.mappings:
            problems.append("no mappings were returned; return one mapping per concept per data source listed")
        for x in m.mappings:
            if batch is not None and canonical_concept(x.concept, batch) is None:
                problems.append(f"concept {x.concept!r} was not in the list; copy the concept name exactly as given")
            if x.source_id not in sources:
                problems.append(f"mapping for {x.concept!r}: unknown source_id {x.source_id!r}")
                continue
            if x.compatibility not in COMPAT:
                problems.append(f"mapping for {x.concept!r}: compatibility must be one of {sorted(COMPAT)}")
            if x.variable is not None:
                parts = split_names(x.variable, sources[x.source_id])
                bad = [p for p in parts if sources[x.source_id].lookup(p) is None]
                if bad and len(parts) == 1:
                    problems.append(
                        f"mapping for {x.concept!r}: {x.variable!r} is not a documented variable in {x.source_id}"
                    )
                elif bad:
                    problems.append(
                        f"mapping for {x.concept!r}: {', '.join(map(repr, bad))} not documented in {x.source_id}; "
                        "put one variable name per mapping and add a separate mapping row for each additional "
                        "variable"
                    )
            if x.variable is None and x.compatibility != "none":
                problems.append(f"mapping for {x.concept!r}: null variable requires compatibility 'none'")
        if batch and m.mappings:
            problems.extend(_coverage_problems(m, sources, batch))
        return problems

    return check


def _coverage_problems(m: MapLike, sources: dict[str, DataSource], batch: Sequence[Concept]) -> list[str]:
    """Every (concept, source) pair needs a row, and no (concept, source, variable) may repeat. On 2026-11-10 the
    model filed its 'sex' rows under 'sex (male, female)': one concept doubled, the other left unmapped."""
    problems = []
    seen: set[tuple[str, str, str | None]] = set()
    dups: list[str] = []
    for x in m.mappings:
        name = canonical_concept(x.concept, batch)
        if name is None or x.source_id not in sources:
            continue  # already reported
        parts = split_names(x.variable, sources[x.source_id]) if x.variable else [None]
        for p in parts:
            key = (name, x.source_id, p.upper() if p else None)
            if key in seen and f"{name!r} / {x.source_id} / {p}" not in dups:
                dups.append(f"{name!r} / {x.source_id} / {p}")
            seen.add(key)
    if dups:
        problems.append(
            f"duplicate rows for {', '.join(dups)}; give each concept, source and variable only once, "
            "under the concept name it belongs to"
        )
    covered = {(c, s) for c, s, _ in seen}
    missing = [f"{c.name!r} / {sid}" for c in batch for sid in sources if (c.name, sid) not in covered]
    if missing:
        problems.append(
            f"no row for {', '.join(missing)}; return at least one row for every concept in every data source "
            "(variable null and compatibility 'none' when nothing matches)"
        )
    return problems


def canonicalize(m: MapLike, batch: Sequence[Concept]) -> int:
    """Rewrite accepted concept names to their sent form in place; return how many were rewritten.
    Call only on output that passed `map_validator(..., batch)`."""
    n = 0
    for x in m.mappings:
        name = canonical_concept(x.concept, batch)
        if name is not None and name != x.concept:
            x.concept = name
            n += 1
    return n


def expand_multi(m: MapLike, sources: dict[str, DataSource]) -> int:
    """Replace each row naming several documented variables with one row per variable, in place; return how
    many rows were split. Call only on output that passed `map_validator`."""
    out: list[Any] = []
    n = 0
    for x in m.mappings:
        parts = split_names(x.variable, sources[x.source_id]) if x.variable else [x.variable]
        if len(parts) > 1:
            n += 1
            out.extend(x.model_copy(update={"variable": p}) for p in parts)
        else:
            out.append(x)
    m.mappings = out
    return n


def _call_key(salt: str, prompt_sha: str, user: str) -> str:
    schema = json.dumps(SchemaMapOut.model_json_schema(), sort_keys=True)
    return hashlib.sha256("\x00".join((salt, prompt_sha, user, schema)).encode()).hexdigest()


def concepts_text(batch: Sequence[Concept]) -> str:
    return "\n".join(f'- "{c.name}" (role: {c.role}) — {c.operationalization}' for c in batch)


def map_schema(
    decompositions: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    max_vars_per_call: int = 350,
    max_mappings_per_call: int = 50,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[SchemaMap, list[LLMCallRecord], list[str]]:
    """One call per (source group, concept batch); large codebooks are split into groups and long concept
    lists into batches so each call fits the context and the output cap. Mappings are merged. For a concept
    with several candidate variables in one source, every candidate is kept for human review.

    Each validated call is saved under `checkpoint_dir` (keyed by salt, prompt, rendered input and output
    schema) as soon as it finishes, so a rerun after a failure resumes instead of repeating finished calls.

    Returns (schema map, call records, warnings). Warnings record concept names rewritten to their sent form,
    rows split into one per variable, and resumed calls. A (concept, source) pair without a row, or a repeated
    row, fails validation and is retried."""
    concepts = collect_concepts(decompositions)
    if not concepts:
        raise StageInputError("B", ["no concepts to map: Component A extracted no variables from any manuscript"])
    prompt = load_prompt("b_schema_map")
    merged = SchemaMap()
    records = []
    warnings: list[str] = []
    resumed = total = 0
    for gi, group in enumerate(source_groups(sources, max_vars_per_call)):
        batch = max(1, max_mappings_per_call // len(group))
        for bi in range(0, len(concepts), batch):
            sent = concepts[bi : bi + batch]
            stage = f"B_schema_map_{gi}_{bi // batch}"
            user = prompt.render(concepts=concepts_text(sent), sources=sources_text(group))
            validator = map_validator(group, sent)
            total += 1
            ckpt = (
                checkpoint_dir / f"{stage}_{_call_key(salt, prompt.sha256, user)[:16]}.json" if checkpoint_dir else None
            )
            obj = None
            if ckpt is not None and ckpt.exists():
                obj = SchemaMapOut.model_validate_json(ckpt.read_text())
                if validator(obj):
                    obj = None  # stale or corrupted checkpoint: regenerate
                else:
                    resumed += 1
            if obj is None:
                obj, rec = generate(
                    client,
                    prompt,
                    user,
                    SchemaMapOut,
                    stage=stage,
                    seed=seed,
                    temperature=temperature,
                    validators=[validator],
                    max_retries=max_retries,
                    log_dir=log_dir,
                )
                records.append(rec)
                if ckpt is not None:
                    ckpt.parent.mkdir(parents=True, exist_ok=True)
                    ckpt.write_text(obj.model_dump_json(indent=1))
            renamed = canonicalize(obj, sent)
            if renamed:
                warnings.append(f"{stage}: {renamed} concept names canonicalized to the names sent")
            split = expand_multi(obj, group)
            if split:
                warnings.append(f"{stage}: {split} multi-variable rows split into one row per variable")
            for m in (ConceptMapping(**x.model_dump()) for x in obj.mappings):
                if m.variable is None and any(
                    x.concept == m.concept and x.source_id == m.source_id and x.variable for x in merged.mappings
                ):
                    continue  # another part of this source already mapped it
                merged.mappings.append(m)
            for sid, text in obj.source_summaries.items():
                merged.source_summaries[sid] = (merged.source_summaries.get(sid, "") + " " + text).strip()
    # drop 'none' rows for concept/source pairs that got a real mapping from another group
    mapped = {(m.concept, m.source_id) for m in merged.mappings if m.variable}
    merged.mappings = [m for m in merged.mappings if m.variable or (m.concept, m.source_id) not in mapped]
    if resumed:
        warnings.append(f"B: resumed {resumed} of {total} calls from checkpoint")
    return merged, records, warnings


def collect_concepts(decompositions: list[ManuscriptDecomposition]) -> list[Concept]:
    """Concepts across manuscripts, first occurrence wins, case-insensitive."""
    seen: dict[str, Concept] = {}
    for d in decompositions:
        for v in d.variables:
            seen.setdefault(v.concept.strip().lower(), Concept(v.concept.strip(), str(v.role), v.operationalization))
    return list(seen.values())
