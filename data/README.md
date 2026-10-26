# data/

Inputs to MMF. Everything here except this file and `manifest.json` is gitignored.

- `manuscripts/` — prior manuscripts (PDF or .docx/.md) to decompose (Component A).
- `codebooks/`   — dataset documentation only (codebooks, user guides, data dictionaries). MMF never reads row-level data.

`manifest.json` records the sha256 of every input so a run is traceable to exact documents.
Regenerate with `mmf manifest`.
