"""Document loading with page provenance and content-hash caching.

Replaces the legacy `Document` / `process_pdf_directory` (PyPDF2, no page numbers, silent
100k-char truncation). Supports PDF (pymupdf), .docx (python-docx) and plain .md/.txt.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

SUPPORTED = {".pdf", ".docx", ".md", ".txt"}


class Page(BaseModel):
    number: int = Field(description="1-based page number (docx/txt: a single page 1).")
    text: str


class Document(BaseModel):
    path: str
    sha256: str
    title: str
    pages: list[Page]

    @property
    def text(self) -> str:
        return "\n\n".join(p.text for p in self.pages)

    @property
    def n_chars(self) -> int:
        return sum(len(p.text) for p in self.pages)

    def page_text(self, number: int) -> str | None:
        for p in self.pages:
            if p.number == number:
                return p.text
        return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_pdf(path: Path) -> tuple[str, list[Page]]:
    import pymupdf

    pages: list[Page] = []
    with pymupdf.open(path) as doc:  # type: ignore[no-untyped-call]
        title = (doc.metadata or {}).get("title") or path.stem
        for i, page in enumerate(doc, start=1):
            pages.append(Page(number=i, text=page.get_text("text")))
    return title, pages


def _load_docx(path: Path) -> tuple[str, list[Page]]:
    import docx

    d = docx.Document(str(path))
    paras = [p.text for p in d.paragraphs]
    for table in d.tables:
        for row in table.rows:
            paras.append(" | ".join(c.text for c in row.cells))
    title = (d.core_properties.title or "").strip() or path.stem
    return title, [Page(number=1, text="\n".join(paras))]


def _load_text(path: Path) -> tuple[str, list[Page]]:
    text = path.read_text(encoding="utf-8")
    first = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.strip()), path.stem)
    return first, [Page(number=1, text=text)]


def load_document(path: Path | str, cache_dir: Path | None = None) -> Document:
    """Load a document, using a sha256-keyed JSON cache if `cache_dir` is given."""
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported document type {path.suffix!r}: {path}")
    digest = sha256_file(path)
    if cache_dir is not None:
        cached = cache_dir / f"{digest}.json"
        if cached.exists():
            return Document.model_validate_json(cached.read_text())

    loader = {".pdf": _load_pdf, ".docx": _load_docx}.get(path.suffix.lower(), _load_text)
    title, pages = loader(path)
    doc = Document(path=str(path), sha256=digest, title=title, pages=pages)
    log.info("loaded %s (%d pages, %d chars)", path.name, len(pages), doc.n_chars)

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / f"{digest}.json").write_text(doc.model_dump_json())
    return doc


def load_directory(directory: Path | str, cache_dir: Path | None = None) -> list[Document]:
    directory = Path(directory)
    docs = []
    for p in sorted(directory.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED and not p.name.startswith("."):
            docs.append(load_document(p, cache_dir))
    return docs


def write_manifest(paths: list[Path], out: Path) -> None:
    out.write_text(json.dumps({str(p): sha256_file(p) for p in paths}, indent=2) + "\n")
