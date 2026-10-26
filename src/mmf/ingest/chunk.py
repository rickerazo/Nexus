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


def _split_page(text: str, max_tokens: int) -> list[str]:
    """Split one page's text at paragraph (then line) boundaries so each part fits max_tokens."""
    if approx_tokens(text) <= max_tokens:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for para in text.split("\n\n"):
        t = approx_tokens(para) + 1
        if t > max_tokens:  # a single huge paragraph: fall back to lines
            for line in para.splitlines():
                lt = approx_tokens(line) + 1
                if buf and size + lt > max_tokens:
                    parts.append("\n".join(buf))
                    buf, size = [], 0
                buf.append(line)
                size += lt
            continue
        if buf and size + t > max_tokens:
            parts.append("\n\n".join(buf))
            buf, size = [], 0
        buf.append(para)
        size += t
    if buf:
        parts.append("\n\n".join(buf))
    return parts


def chunk_document(doc: Document, max_tokens: int) -> list[Chunk]:
    """Page-aligned chunks; a page larger than max_tokens is split at paragraph boundaries and
    every part keeps that page's number (provenance is still exact at page level)."""
    chunks: list[Chunk] = []
    buf: list[str] = []
    first = None
    last = None
    size = 0
    for page in doc.pages:
        header = f"\n[page {page.number}]\n"
        for part in _split_page(page.text, max_tokens - approx_tokens(header)):
            t = approx_tokens(header + part)
            if buf and size + t > max_tokens:
                chunks.append(Chunk(index=len(chunks), first_page=first or 1, last_page=last or 1, text="".join(buf)))
                buf, size, first = [], 0, None
            if first is None:
                first = page.number
            buf.append(header + part)
            last = page.number
            size += t
    if buf:
        chunks.append(Chunk(index=len(chunks), first_page=first or 1, last_page=last or 1, text="".join(buf)))
    return chunks
