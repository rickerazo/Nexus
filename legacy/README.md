# legacy/

`ai_for_science/` is the exploratory prototype that preceded MMF. It is kept for the record, read-only and unmaintained. MMF (`src/mmf/`) does not import or depend on it.

**Do not run these scripts.**
- They read a personal OpenAI API key from `.env` (`OPENAI_API_KEY` via `python-dotenv`). This project no longer allows that: only institutional credentials, only through MMF's `MMF_*` environment variables, and only with an explicit `allow_cloud: true` per run.
- They need packages that are not in `pyproject.toml` (`openai`, `python-dotenv`, `beautifulsoup4`, `PyPDF2`, `IPython`, `requests`).

Contents:
- `ai_forResearch.py`, `gpt_science.py`, `pdf_journal_articles.py`, `scrape_journal_articles.py`: prototype scripts.
- `bibliography_respirationSD*`, `epidemiology_NB/`, `molecular_refs_01/`, `PRAMS_doc/`: reference folders from the prototype.
- Slide decks and a poster from earlier talks.

Not in git: third-party journal PDFs (copyrighted) and one 102 MB slide deck (`Soria Moria 2024 closer to final.pptx`). They exist only on the original machine.
