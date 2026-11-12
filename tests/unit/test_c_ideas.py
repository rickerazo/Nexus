"""C redesign steps C0 (data inventory) and C1 (idea generation), with a fake client."""

import json
from pathlib import Path

from tests.unit.test_structured import FakeClient

from mmf.components import c_ideas
from mmf.schemas.ideas import BlockDomain, BlockDomains, Idea, IdeaBatch
from mmf.schemas.manuscript import Claim, ManuscriptDecomposition, VariableMention


def _block(sources):
    return sources["cdc"].variables


def test_blocks_keep_document_order(sources):
    bs = c_ideas.blocks(sources["cdc"], 3)
    assert [len(b) for b in bs] == [3, 3, 1]
    assert [v.name for b in bs for v in b] == [v.name for v in sources["cdc"].variables]


def test_block_validator(sources):
    check = c_ideas.block_validator(_block(sources))
    ok = BlockDomains(
        domains=[
            BlockDomain(start="SEX", name="Infant and mother", summary="Sex and maternal age."),
            BlockDomain(start="UCOD", name="Death", summary="Cause and age at death."),
        ]
    )
    assert check(ok) == []
    bad = BlockDomains(
        domains=[
            BlockDomain(start="MAGER9", name="Mother", summary="Age."),  # not the block's first variable
            BlockDomain(start="NOPE", name="Ghost", summary="x"),  # not in the block
            BlockDomain(start="CIG_REC", name="Late", summary="x"),
            BlockDomain(start="SEX", name="Backwards", summary="x"),  # out of order
        ]
    )
    problems = " | ".join(check(bad))
    assert "first domain must start at the block's first variable, 'SEX'" in problems
    assert "'NOPE' is not a variable name" in problems
    assert "'SEX' is not after the previous domain's start" in problems
    assert check(BlockDomains(domains=[])) == ["return at least one domain"]


def test_domains_cover_every_variable_once_and_mark_used(sources):
    out = BlockDomains(
        domains=[
            BlockDomain(start="SEX", name="Births", summary="s"),
            BlockDomain(start="UCOD", name="Deaths", summary="d"),
        ]
    )
    doms = c_ideas.domains_from_block("cdc", _block(sources), out, used={"cdc:CIG_REC", "cdc:AGED"})
    assert [d.variables for d in doms] == [
        ["SEX", "MAGER9", "CIG_REC", "COMBGEST", "BIRTHS"],
        ["UCOD", "AGED"],
    ]
    assert [d.used for d in doms] == [["CIG_REC"], ["AGED"]]


def test_build_inventory_and_text(sources, tmp_path: Path):
    answer = json.dumps(
        {
            "domains": [
                {"start": "SEX", "name": "Births", "summary": "Birth record items."},
                {"start": "UCOD", "name": "Deaths", "summary": "Death record items."},
            ]
        }
    )
    client = FakeClient([answer])
    inv, recs = c_ideas.build_inventory(
        sources,
        {"cdc:SEX"},
        client,
        populations={"cdc": "live births"},
        block_vars=150,
        seed=0,
        temperature=0,
        max_retries=0,
        log_dir=None,
        checkpoint_dir=tmp_path,
    )
    assert len(inv.domains) == 2 and len(recs) == 1
    assert "UCOD: Underlying cause of death" in client.calls[0]
    text = c_ideas.inventory_text(inv, sources, {"cdc": "live births"})
    assert "- Births (5 variables, 1 used by the manuscripts): Birth record items." in text
    assert "- Deaths (2 variables, none used by the manuscripts)" in text
    # a rerun resumes from the checkpoint instead of calling the model
    again, recs2 = c_ideas.build_inventory(
        sources,
        {"cdc:SEX"},
        FakeClient([]),
        populations={"cdc": "live births"},
        block_vars=150,
        seed=0,
        temperature=0,
        max_retries=0,
        log_dir=None,
        checkpoint_dir=tmp_path,
    )
    assert again == inv and recs2 == []


def _idea(q, sources=("cdc",)):
    return Idea(question=q, why_open="w", sources=list(sources), data="births")


def test_ideas_validator():
    check = c_ideas.ideas_validator(2, {"cdc"})
    assert check(IdeaBatch(ideas=[_idea("a?"), _idea("b?")])) == []
    problems = " | ".join(check(IdeaBatch(ideas=[_idea("a?"), _idea("A?"), _idea("c?", ["prams"])])))
    assert "return exactly 2 ideas, got 3" in problems
    assert "idea 2: repeats an earlier idea" in problems
    assert "idea 3: unknown source ids ['prams']" in problems


def _dec():
    return ManuscriptDecomposition(
        manuscript_id="m",
        title="Mini",
        document_sha256="0",
        research_questions=["Does X raise Y?"],
        claims=[
            Claim(id="C1", kind="finding", statement="X raises Y.", quote="q"),
            Claim(id="C2", kind="method", statement="Poisson model.", quote="q"),
        ],
        variables=[VariableMention(concept="X", role="exposure", operationalization="o", quote="q")],
    )


def test_manuscripts_text_lists_findings_not_methods_or_quotes():
    text = c_ideas.manuscripts_text([_dec()])
    assert "Question: Does X raise Y?" in text and "- finding: X raises Y." in text
    assert "Poisson" not in text and "Variables used: X (exposure)" in text


def test_generate_ideas_pools_every_lens_and_seed_and_skips_failed_calls(sources):
    def batch(*qs):
        return IdeaBatch(ideas=[_idea(q) for q in qs]).model_dump_json()

    lenses = {"a": "Lens A.", "b": "Lens B."}
    # lens a: seeds 0 and 1 succeed; lens b seed 0 fails on both attempts, seed 1 succeeds
    client = FakeClient([batch("q1", "q2"), batch("q3", "q4"), "not json", "still not json", batch("q5", "q6")])
    pool, recs = c_ideas.generate_ideas(
        [_dec()],
        "inventory",
        sources,
        client,
        lenses=lenses,
        seeds=[0, 1],
        n_ideas=2,
        temperature=0.9,
        max_retries=1,
        log_dir=None,
    )
    assert [c.question for c in pool.candidates] == ["q1", "q2", "q3", "q4", "q5", "q6"]
    assert [c.id for c in pool.candidates][-1] == "I6"
    assert [(c.lens, c.seed) for c in pool.candidates][4] == ("b", 1)
    assert pool.failed_calls == ["C_ideas_b_s0"]
    assert len(recs) == 4 and [r.ok for r in recs].count(False) == 1
    assert "Lens B." in client.calls[2] and "inventory" in client.calls[0]
    md = c_ideas.pool_markdown(pool)
    assert "Failed calls (no ideas): C_ideas_b_s0" in md and "**I5** (seed 1, fake-1) q5" in md


def test_lenses_carry_no_topic_specific_examples():
    text = " ".join(c_ideas.LENSES.values()).lower()
    for word in ("suid", "sids", "sleep", "infant", "pca", "postconceptional", "smoking", "bed"):
        assert word not in text, word
