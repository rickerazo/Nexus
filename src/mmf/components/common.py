"""Shared helpers for components."""

from __future__ import annotations

from mmf.schemas.dataset import DataSource, VariableRef


def allowed_refs_text(sources: dict[str, DataSource], with_labels: bool = False) -> str:
    lines = []
    for sid, src in sources.items():
        for v in src.variables:
            lines.append(f"({sid}, {v.name}): {v.label}" if with_labels else f"({sid}, {v.name})")
    return "\n".join(lines)


def sources_text(sources: dict[str, DataSource]) -> str:
    blocks = []
    for sid, src in sources.items():
        vars_ = "\n".join(f"  {v.name}: {v.label}" for v in src.variables)
        blocks.append(f"source_id: {sid}  ({src.title})\n{vars_}")
    return "\n\n".join(blocks)


def refs_text(refs: list[VariableRef]) -> str:
    return ", ".join(f"({r.source_id}, {r.name})" for r in refs)
