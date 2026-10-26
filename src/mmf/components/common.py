"""Shared helpers for components."""

from __future__ import annotations

from mmf.schemas.dataset import DataSource, VariableRef


def allowed_refs_text(sources: dict[str, DataSource], with_labels: bool = False, only: set[str] | None = None) -> str:
    """List (source_id, name) pairs; `only` restricts to keys 'source_id:NAME' (e.g. those mapped in B)."""
    lines = []
    for sid, src in sources.items():
        for v in src.variables:
            if only is not None and f"{sid}:{v.name.upper()}" not in only:
                continue
            lines.append(f"({sid}, {v.name}): {v.label}" if with_labels else f"({sid}, {v.name})")
    return "\n".join(lines)


def restrict_sources(sources: dict[str, DataSource], only: set[str]) -> dict[str, DataSource]:
    """Copies of the sources containing only variables whose key is in `only`."""
    out = {}
    for sid, src in sources.items():
        keep = [v for v in src.variables if f"{sid}:{v.name.upper()}" in only]
        if keep:
            out[sid] = src.model_copy(update={"variables": keep})
    return out


def source_groups(sources: dict[str, DataSource], max_vars: int) -> list[dict[str, DataSource]]:
    """Split sources into groups of at most `max_vars` variables so each fits one prompt.
    A large source is split into several partial copies with the same id."""
    groups: list[dict[str, DataSource]] = []
    for sid, src in sources.items():
        vars_ = src.variables
        for i in range(0, max(1, len(vars_)), max_vars):
            groups.append({sid: src.model_copy(update={"variables": vars_[i : i + max_vars]})})
    return groups


def sources_text(sources: dict[str, DataSource]) -> str:
    blocks = []
    for sid, src in sources.items():
        vars_ = "\n".join(f"  {v.name}: {v.label}" for v in src.variables)
        blocks.append(f"source_id: {sid}  ({src.title})\n{vars_}")
    return "\n\n".join(blocks)


def refs_text(refs: list[VariableRef]) -> str:
    return ", ".join(f"({r.source_id}, {r.name})" for r in refs)


def mapped_keys(schema_map: object) -> set[str]:
    """Keys 'source_id:NAME' of every variable mapped (non-null) in a SchemaMap."""
    return {f"{m.source_id}:{m.variable.upper()}" for m in getattr(schema_map, "mappings", []) if m.variable}
