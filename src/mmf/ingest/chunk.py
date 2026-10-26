"""Chunk a Document into page-aligned windows that fit a model context.

Chunks never split a page, so every chunk carries exact page provenance.
"""

from __future__ import annotations

from pydantic import BaseModel

from mmf.ingest.pdf import Document


class Chunk(BaseModel):
    index: int
    first_page: int
    last_page: int
    text: str


def approx_tokens(text: str) -> int:
    # Conservative heuristic (~3.5 chars/token for English prose with codes).
    return len(text) // 3 + 1


def chunk_document(doc: Document, max_tokens: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    buf: list[str] = []
    first = None
    last = None
    size = 0
    for page in doc.pages:
        header = f"\n[page {page.number}]\n"
        t = approx_tokens(header + page.text)
        if buf and size + t > max_tokens:
            chunks.append(Chunk(index=len(chunks), first_page=first or 1, last_page=last or 1, text="".join(buf)))
            buf, size, first = [], 0, None
        if first is None:
            first = page.number
        buf.append(header + page.text)
        last = page.number
        size += t
    if buf:
        chunks.append(Chunk(index=len(chunks), first_page=first or 1, last_page=last or 1, text="".join(buf)))
    return chunks
