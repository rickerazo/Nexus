"""B's embedding cross-check, with a deterministic keyword embedder (no model)."""

from pathlib import Path

from mmf.components.b_crosscheck import check_schema, variable_fingerprint
from mmf.report.markdown import render_review
from mmf.schemas import ConceptMapping, DataSource, ManuscriptDecomposition, SchemaMap, Variable, VariableMention

VOCAB = ("sex", "smok", "gestation", "neuron")


class KeywordEmbedder:
    """Each text becomes keyword counts over VOCAB plus a small constant, so cosine is predictable."""

    model = "fake-embed"

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def model_digest(self) -> str:
        return "fakedigest"

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(t.lower().count(w)) for w in VOCAB] + [0.05] for t in texts]


def _inputs():
    src = DataSource(
        id="cdc",
        title="t",
        document_path="p",
        document_sha256="0" * 64,
        variables=[
            Variable(name="SEX", label="Sex of infant", levels=["M=Male", "F=Female"], page=1),
            Variable(name="CIG_0", label="Cigarettes smoked before pregnancy", page=1),
            Variable(name="COMBGEST", label="Combined gestation in weeks", page=1),
            Variable(name="MAGER9", label="Mother's age recode", page=1),
        ],
    )
    concepts = [
        ("infant sex", "effect_modifier", "sex recorded"),
        ("maternal smoking", "exposure", "any smoking"),
        ("gestational age", "covariate", "gestation in weeks"),
        ("neuron density", "outcome", "neuron counts in mice"),
    ]
    dec = ManuscriptDecomposition(
        manuscript_id="m",
        title="t",
        document_sha256="0" * 64,
        variables=[VariableMention(concept=c, role=r, operationalization=o, quote="q" * 20) for c, r, o in concepts],
    )
    smap = SchemaMap(
        mappings=[
            ConceptMapping(concept="infant sex", source_id="cdc", variable="SEX", compatibility="direct"),
            ConceptMapping(concept="maternal smoking", source_id="cdc", variable="MAGER9", compatibility="proxy"),
            ConceptMapping(concept="gestational age", source_id="cdc", variable=None, compatibility="none"),
            ConceptMapping(concept="neuron density", source_id="cdc", variable=None, compatibility="none"),
        ]
    )
    return smap, [dec], {"cdc": src}


def test_verdicts_cover_all_four_cases(tmp_path: Path):
    smap, decs, sources = _inputs()
    check = check_schema(smap, decs, sources, KeywordEmbedder(), top_k=1, miss_threshold=0.5, cache_dir=tmp_path)
    by = {r.concept: r for r in check.records}
    assert by["infant sex"].verdict == "agree" and by["infant sex"].top[0].name == "SEX"
    assert by["maternal smoking"].verdict == "llm_outside_topk" and by["maternal smoking"].outside == ["MAGER9"]
    assert by["maternal smoking"].top[0].name == "CIG_0"
    assert by["gestational age"].verdict == "possible_miss" and by["gestational age"].top[0].name == "COMBGEST"
    assert by["neuron density"].verdict == "both_none"
    assert check.counts() == {"agree": 1, "llm_outside_topk": 1, "possible_miss": 1, "both_none": 1}


def test_vectors_are_cached_on_disk(tmp_path: Path):
    smap, decs, sources = _inputs()
    emb = KeywordEmbedder()
    first = check_schema(smap, decs, sources, emb, top_k=2, miss_threshold=0.5, cache_dir=tmp_path)
    n = len(emb.calls)
    second = check_schema(smap, decs, sources, emb, top_k=2, miss_threshold=0.5, cache_dir=tmp_path)
    assert len(emb.calls) == n  # nothing re-embedded
    assert first == second


def test_variable_fingerprint_uses_label_and_levels_not_layout_notes():
    v = Variable(name="BFED", label="Infant being breastfed", levels=["Y=Yes", "N=No"], notes="position=1; file=P,G")
    assert variable_fingerprint(v) == "BFED: Infant being breastfed. Values: Y=Yes; N=No."


def test_review_lists_disagreements_first(tmp_path: Path):
    smap, decs, sources = _inputs()
    check = check_schema(smap, decs, sources, KeywordEmbedder(), top_k=1, miss_threshold=0.5, cache_dir=tmp_path)
    text = render_review("B", "Schema map", smap, check)
    assert "## Cross-check (embedding vs LLM)" in text
    section = text.split("## Cross-check")[1].split("```json")[0]
    assert section.index("llm_outside_topk | cdc | maternal smoking") < section.index(
        "possible_miss | cdc | gestational"
    )
    assert "neuron density" not in section  # both_none is not flagged
    assert "approved: false" in render_review("B", "Schema map", smap)  # still renders without a check
