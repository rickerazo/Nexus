"""Source roles (investigator, 2026-11-16): case series, denominators and population reference.

The leverage of combining sources comes from their roles: outcomes come only from case series, exposure prevalence
in the general population from reference sources, and the population at risk from denominator sources. This module
renders the roles for the scientific primer and builds the cross-role concept table from B's mappings: which
concepts are measured in which roles, i.e. which comparisons across sources are possible at all.
"""

from __future__ import annotations

from mmf.config import SourceSpec
from mmf.schemas.dataset import DataSource, SchemaMap

ROLE_NAMES = {"case": "case series", "denominator": "denominator", "reference": "population reference"}
ROLE_MEANING = (
    "Roles: a case series records the outcome events (outcomes come only from case sources); a denominator "
    "source gives the population at risk; a population reference gives exposure prevalence in the general "
    "population and never records outcomes. Comparisons between a case series and a reference source are "
    "group-level unless a linkage is stated."
)


def specs_by_id(specs: list[SourceSpec], sources: dict[str, DataSource]) -> dict[str, SourceSpec]:
    return {s.id: s for s in specs if s.id in sources}


def ids_with_role(specs: list[SourceSpec], sources: dict[str, DataSource], role: str) -> set[str]:
    return {s.id for s in specs if s.id in sources and role in s.roles}


def source_roles_text(specs: list[SourceSpec], sources: dict[str, DataSource]) -> str:
    lines = [ROLE_MEANING, ""]
    for spec in specs:
        if spec.id not in sources:
            continue
        title = spec.title or sources[spec.id].title
        if not spec.roles:
            lines.append(f"- {spec.id} ({title}): a lookup list of names and labels, not a dataset; no role.")
            continue
        roles = " and ".join(ROLE_NAMES[r] for r in spec.roles)
        parts = [f"- {spec.id} ({title}). Role: {roles}."]
        for label, value in (
            ("One record", spec.unit),
            ("Covers", spec.population),
            ("Period", spec.years),
            ("Geography", spec.geography),
            ("Linkage", spec.linkage),
            ("Survey weight (required for any prevalence)", spec.weight_variable),
            ("Missing answers", spec.missing),
        ):
            if value:
                parts.append(f"  {label}: {value}.")
        lines.append("\n".join(parts))
    return "\n".join(lines)


def role_problems(specs: list[SourceSpec], sources: dict[str, DataSource]) -> list[str]:
    """Configuration errors that would make role-based designs wrong: a declared weight that is not documented."""
    problems = []
    for spec in specs:
        if spec.id in sources and spec.weight_variable and sources[spec.id].lookup(spec.weight_variable) is None:
            problems.append(f"{spec.id}: weight_variable {spec.weight_variable!r} is not a documented variable")
    return problems


def cross_role_concepts(smap: SchemaMap, specs: list[SourceSpec]) -> dict[str, dict[str, list[str]]]:
    """concept -> role -> ['source:VARIABLE (compatibility)'], from B's non-empty mappings."""
    roles = {s.id: s.roles for s in specs}
    table: dict[str, dict[str, list[str]]] = {}
    for m in smap.mappings:
        if not m.variable:
            continue
        for role in roles.get(m.source_id, []):
            cell = table.setdefault(m.concept, {}).setdefault(role, [])
            entry = f"{m.source_id}:{m.variable} ({m.compatibility})"
            if entry not in cell:
                cell.append(entry)
    return table


def cross_role_text(table: dict[str, dict[str, list[str]]]) -> str:
    """Concepts measured in both a case series and a population reference first (case-population comparisons),
    then by number of roles."""
    order = sorted(table, key=lambda c: (not {"case", "reference"} <= set(table[c]), -len(table[c]), c.lower()))
    lines = []
    for concept in order:
        cells = "; ".join(f"{ROLE_NAMES[r]}: {', '.join(v)}" for r, v in sorted(table[concept].items()))
        lines.append(f"- {concept} [{len(table[concept])} role(s)] {cells}")
    return "\n".join(lines) or "(no concept is mapped to any source)"
