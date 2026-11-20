"""Regenerate the literature documents from PubMed (NCBI E-utilities, no credentials needed).

    uv run python scripts/fetch_pubmed.py --out data/manuscripts/literature

Writes:
  ramirez_lavista_bibliography.md   all records (reference, not a pipeline input)
  suid_literature_abstracts.md      SUID + respiratory-development abstracts (pipeline input, Component A)
  suid_literature_pmids.json        PMIDs included in the abstracts document
  records.json                      raw records as fetched (title, abstract, ids, MeSH)
Abstract text is used as retrieved; claims extracted from it are abstract-level and must be verified
against full texts before implementation.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = {
    "ramirez": 'Ramirez JM[Author] AND (Seattle[Affiliation] OR "Seattle Children"[Affiliation] OR Washington[Affiliation] '
    "OR sudden infant death OR SIDS OR SUID OR breathing OR respiration OR preBotzinger OR apnea OR hypoxia OR brainstem)",
    "lavista": 'Lavista Ferres J[Author] OR "Lavista Ferres JM"[Author]',
}
KW_SUID = ("sudden infant", "sids", "suid", "sudden unexpected", "infant death", "infant mortality")
KW_RESP = (
    "breathing",
    "respirat",
    "prebötzinger",
    "prebotzinger",
    "apnea",
    "hypoxia",
    "brainstem",
    "arousal",
    "serotonin",
    "chemosensitiv",
    "gasping",
    "autoresuscitation",
    "development",
)
KW_RESP_INFANT = ("infant", "neonat", "postnatal", "develop", "sex", "hypoxia", "arousal")


def esearch(term: str) -> list[str]:
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": 1000, "retmode": "json"})
    with urllib.request.urlopen(BASE + "esearch.fcgi?" + q, timeout=60) as r:
        ids: list[str] = json.load(r)["esearchresult"]["idlist"]
    return ids


def efetch(ids: list[str]) -> list[dict[str, Any]]:
    recs = []
    for i in range(0, len(ids), 100):
        q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids[i : i + 100]), "retmode": "xml"})
        with urllib.request.urlopen(BASE + "efetch.fcgi?" + q, timeout=120) as r:
            root = ET.fromstring(r.read())
        for art in root.findall(".//PubmedArticle"):
            t = art.find(".//ArticleTitle")
            ids_ = {a.get("IdType"): a.text for a in art.findall(".//ArticleIdList/ArticleId")}
            recs.append(
                {
                    "pmid": art.findtext(".//PMID"),
                    "title": "".join(t.itertext()) if t is not None else "",
                    "abstract": " ".join(
                        "".join(a.itertext()).strip() for a in art.findall(".//Abstract/AbstractText")
                    ),
                    "year": art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate") or "",
                    "journal": art.findtext(".//Journal/Title") or "",
                    "authors": [
                        f"{a.findtext('LastName')} {a.findtext('Initials') or ''}".strip()
                        for a in art.findall(".//AuthorList/Author")
                        if a.findtext("LastName")
                    ],
                    "pmc": ids_.get("pmc"),
                    "doi": ids_.get("doi"),
                    "mesh": [m.findtext("DescriptorName") for m in art.findall(".//MeshHeading")],
                }
            )
        time.sleep(0.4)
    return recs


def year(r: dict[str, Any]) -> int:
    m = re.search(r"\d{4}", r["year"] or "")
    return int(m.group()) if m else 0


def tags(r: dict[str, Any]) -> tuple[bool, bool]:
    t = (r["title"] + " " + r["abstract"]).lower()
    return any(k in t for k in KW_SUID), any(k in t for k in KW_RESP)


def fmt(r: dict[str, Any]) -> str:
    au = ", ".join(r["authors"][:6]) + (" et al." if len(r["authors"]) > 6 else "")
    ids = f"PMID {r['pmid']}" + (f"; PMC {r['pmc']}" if r["pmc"] else "") + (f"; doi:{r['doi']}" if r["doi"] else "")
    s = f"### {r['title']}\n{au}. *{r['journal']}* ({year(r)}). {ids}\n"
    if r["abstract"]:
        s += f"\n{r['abstract']}\n"
    return s + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/manuscripts/literature"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    ids = {k: esearch(v) for k, v in QUERIES.items()}
    allids = sorted(set().union(*ids.values()), key=int)
    recs = efetch(allids)
    for r in recs:
        r["groups"] = [k for k, v in ids.items() if r["pmid"] in v]
    (args.out / "records.json").write_text(json.dumps(recs, indent=1))
    today = datetime.now(UTC).date().isoformat()
    recs.sort(key=year, reverse=True)

    out = [
        f"# Publication record: Jan-Marino Ramirez lab and Juan M. Lavista Ferres (PubMed, retrieved {today})\n",
        f"{len(recs)} records. Tags: SUID = sudden unexpected infant death related; RESP = respiratory control / brainstem development.\n",
    ]
    by_year: dict[int, list[dict[str, Any]]] = {}
    for r in recs:
        by_year.setdefault(year(r), []).append(r)
    for y in sorted(by_year, reverse=True):
        out.append(f"\n## {y}\n")
        for r in by_year[y]:
            su, re_ = tags(r)
            tag = " ".join(t for t, on in (("[SUID]", su), ("[RESP]", re_)) if on)
            out.append(fmt(r).replace("### ", f"### {tag} " if tag else "### ", 1))
    (args.out / "ramirez_lavista_bibliography.md").write_text("".join(out))

    suid = [r for r in recs if tags(r)[0] and r["abstract"]]
    resp = [
        r
        for r in recs
        if not tags(r)[0]
        and tags(r)[1]
        and r["abstract"]
        and year(r) >= 2015
        and any(k in (r["title"] + r["abstract"]).lower() for k in KW_RESP_INFANT)
    ]
    out = [
        f"# SUID literature from the Ramirez lab and Lavista Ferres group: abstracts (PubMed, retrieved {today})\n",
        "This document compiles abstracts only; claims extracted from it are abstract-level and should be verified against full texts before implementation. Section 1 lists SUID epidemiology and mechanism papers; Section 2 lists respiratory-control and brainstem development papers from the same groups that bear on SUID mechanisms.\n",
        f"\n# Section 1. SUID studies ({len(suid)} papers)\n",
        *[fmt(r) for r in suid],
        f"\n# Section 2. Respiratory control and development studies ({len(resp)} papers)\n",
        *[fmt(r) for r in resp],
    ]
    (args.out / "suid_literature_abstracts.md").write_text("".join(out))
    (args.out / "suid_literature_pmids.json").write_text(json.dumps([r["pmid"] for r in suid + resp]))
    print(f"records {len(recs)} | SUID {len(suid)} | respiratory {len(resp)} -> {args.out}")


if __name__ == "__main__":
    main()
