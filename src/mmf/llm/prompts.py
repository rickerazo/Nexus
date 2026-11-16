"""Prompts are files under mmf/prompts/, versioned and hashed into the run manifest."""

from __future__ import annotations

import hashlib
from importlib import resources
from string import Template

from pydantic import BaseModel

PROMPT_DIR = resources.files("mmf") / "prompts"


class Prompt(BaseModel):
    name: str
    system: str
    user_template: str
    sha256: str

    def render(self, **kwargs: str) -> str:
        """Render the user message. Placeholders in `system` must be bound first with `bind`."""
        return Template(self.user_template).safe_substitute(**kwargs)

    def bind(self, **kwargs: str) -> Prompt:
        """Return a copy with placeholders substituted in both sections (e.g. the vocabulary)."""
        return self.model_copy(
            update={
                "system": Template(self.system).safe_substitute(**kwargs),
                "user_template": Template(self.user_template).safe_substitute(**kwargs),
            }
        )


def load_prompt(name: str) -> Prompt:
    """Load `<name>.md`. The file has a `## system` section and a `## user` section."""
    text = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    system, user = _split(text)
    return Prompt(
        name=name,
        system=system,
        user_template=user,
        sha256=hashlib.sha256(text.encode()).hexdigest(),
    )


PRIMER = "science_primer"


def load_primed_prompt(name: str, source_roles: str) -> Prompt:
    """A two-layer prompt: the shared scientific primer as the system message (with the source-role table
    substituted) and `<name>.md`, which has only a `## user` section, as the task. The hash covers both files."""
    primer = (PROMPT_DIR / f"{PRIMER}.md").read_text(encoding="utf-8")
    task = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    if any(line.strip().lower() == "## system" for line in task.splitlines()):
        raise ValueError(f"{name}.md is a primed task prompt: it must not have a '## system' section")
    _, user = _split("## system\n-\n" + task)
    return Prompt(
        name=name,
        system=Template(primer.strip()).safe_substitute(source_roles=source_roles),
        user_template=user,
        sha256=hashlib.sha256((primer + "\x00" + task).encode()).hexdigest(),
    )


def _split(text: str) -> tuple[str, str]:
    parts: dict[str, list[str]] = {"system": [], "user": []}
    current: str | None = None
    for line in text.splitlines():
        if line.strip().lower() in ("## system", "## user"):
            current = line.strip()[3:].lower()
            continue
        if current:
            parts[current].append(line)
    if not parts["system"] or not parts["user"]:
        raise ValueError("prompt file must contain '## system' and '## user' sections")
    return "\n".join(parts["system"]).strip(), "\n".join(parts["user"]).strip()
