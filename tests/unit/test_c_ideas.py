"""C redesign steps C0 (data inventory) and C1 (idea generation), with a fake client."""

import json
from pathlib import Path

from tests.unit.test_structured import FakeClient

from mmf.components import c_ideas
from mmf.schemas.dataset import DataSource
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
    assert "'SEX' is variable 1 of the list, not after the previous domain's start (variable 3)" in problems
    assert check(BlockDomains(domains=[])) == ["return at least one domain"]


def test_misplaced_domains_are_dropped_on_the_final_attempt(sources):
    block = _block(sources)
    out = BlockDomains(
        domains=[
            BlockDomain(start="SEX", name="Births", summary="s"),
            BlockDomain(start="UCOD", name="Deaths", summary="d"),
            BlockDomain(start="CIG_REC", name="Smoking", summary="x"),  # out of order (2026-11-12 NCFRP block 11)
            BlockDomain(start="NOPE", name="Ghost", summary="x"),
        ]
    )
    pruned, dropped = c_ideas.drop_misplaced_domains(block)(out, [])
    assert [d.start for d in pruned.domains] == ["SEX", "UCOD"]
    assert dropped == ["domain 'Smoking' (start 'CIG_REC')", "domain 'Ghost' (start 'NOPE')"]
    assert c_ideas.block_validator(block)(pruned) == []


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
    text = c_ideas.inventory_text(inv, sources, {"cdc": ["case", "denominator"]})
    assert "## cdc: mini (case series and denominator)" in text
    assert "- cdc / Births [5 variables, 1 used by the manuscripts]: Birth record items." in text
    assert "- cdc / Deaths [NEW, 2 variables, none used by the manuscripts]" in text
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


ROLES = {"cdc": ["case", "denominator"], "ncfrp": ["case"], "prams": ["reference"], "names": []}


def _idea(q, case=("ncfrp",), reference=("prams",), denominator=(), domains=("ncfrp / Scene",)):
    return Idea(
        question=q,
        comparison="cases vs population",
        why_open="w",
        case_sources=list(case),
        reference_sources=list(reference),
        denominator_sources=list(denominator),
        domains=list(domains),
        data="d",
    )


def test_ideas_validator_checks_roles_and_design_needs():
    rates = c_ideas.DESIGNS["exposure_rates"]
    check = c_ideas.ideas_validator(2, rates, ROLES)
    assert check(IdeaBatch(ideas=[_idea("a?", denominator=["cdc"]), _idea("b?", denominator=["cdc"])])) == []
    problems = " | ".join(
        check(
            IdeaBatch(
                ideas=[
                    _idea("a?", denominator=["cdc"]),
                    _idea("A?", denominator=["cdc"]),  # repeat
                    _idea("c?", reference=["ncfrp"], denominator=["cdc"]),  # a case series used as reference
                    _idea("d?", case=["ghost"]),  # unknown source, and no denominator
                ]
            )
        )
    )
    assert "return exactly 2 ideas, got 4" in problems
    assert "idea 2: repeats an earlier idea" in problems
    assert "idea 3: ncfrp is listed as a population reference source but its role is case series" in problems
    assert "idea 3: this design needs at least 1 population reference source(s)" in problems
    assert "idea 4: unknown source id 'ghost'" in problems
    assert "idea 4: this design needs at least 1 denominator source(s)" in problems


def test_measurement_design_needs_two_sources():
    check = c_ideas.ideas_validator(1, c_ideas.DESIGNS["measurement"], ROLES)
    assert "at least 2 different sources" in " ".join(check(IdeaBatch(ideas=[_idea("a?", reference=[])])))
    assert check(IdeaBatch(ideas=[_idea("a?")])) == []


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


def _inv():
    from mmf.schemas.ideas import DataInventory, InventoryDomain

    return DataInventory(
        domains=[
            InventoryDomain(source_id="ncfrp", name="Scene", summary="sleep surface", variables=["A"], used=[]),
            InventoryDomain(source_id="ncfrp", name="Birth", summary="gestation", variables=["B"], used=["B"]),
            InventoryDomain(source_id="prams", name="Practices", summary="sleep surface", variables=["C"], used=[]),
            InventoryDomain(source_id="prams", name="Smoking", summary="smoking", variables=["D"], used=["D"]),
        ]
    )


def test_ideas_validator_checks_domain_labels_and_new_domains():
    inv = _inv()
    labels = {c_ideas.domain_label(d) for d in inv.domains}
    new = c_ideas.new_domain_labels(inv)
    assert new == {"ncfrp / Scene", "prams / Practices"}
    check = c_ideas.ideas_validator(2, c_ideas.DESIGNS["case_population"], ROLES, labels, new, min_new=2)
    assert check(IdeaBatch(ideas=[_idea("a?"), _idea("b?", domains=["prams / Practices", "ncfrp / Birth"])])) == []
    problems = " | ".join(
        check(
            IdeaBatch(
                ideas=[
                    _idea("a?", domains=["ncfrp / Birth"]),
                    _idea("b?", domains=["NCFRP/scene", "cdc / Births"]),
                ]
            )
        )
    )
    assert "domain 'NCFRP/scene' is not in the inventory" in problems
    assert "only 0 idea(s) use a domain marked NEW; at least 2" in problems


def test_match_domains_pairs_case_with_reference_and_puts_new_first():
    from tests.unit.test_crosscheck import KeywordEmbedder

    from mmf.components.b_crosscheck import VectorCache

    inv = _inv()
    inv.domains[0].summary = "smok smok"  # case 'Scene' now resembles reference 'Smoking'
    inv.domains[1].summary = "sex"
    inv.domains[2].summary = "sex"
    vectors = VectorCache(KeywordEmbedder(), None).vectors
    matches = c_ideas.match_domains(inv, ROLES, vectors, threshold=0.9)
    # equal NEW count and score: case order is kept
    assert [(m.case, m.reference) for m in matches] == [
        ("ncfrp / Scene", "prams / Smoking"),
        ("ncfrp / Birth", "prams / Practices"),
    ]
    assert (matches[0].case_new, matches[0].reference_new) == (True, False)
    text = c_ideas.domain_matches_text(matches)
    assert "- ncfrp / Birth <-> prams / Practices (similarity 1.00; reference domain NEW)" in text
    assert c_ideas.match_domains(inv, {"ncfrp": ["case"]}, vectors, 0.9) == []


def test_generate_ideas_pools_every_design_and_seed_and_skips_failed_calls():
    def batch(*qs):
        return IdeaBatch(ideas=[_idea(q) for q in qs]).model_dump_json()

    designs = {k: c_ideas.DESIGNS[k] for k in ("case_population", "case_only")}
    srcs = {sid: DataSource(id=sid, title=sid, document_path="p", document_sha256="0") for sid in ("ncfrp", "prams")}
    # case_population: seeds 0 and 1 succeed; case_only seed 0 fails on both attempts, seed 1 succeeds
    client = FakeClient([batch("q1", "q2"), batch("q3", "q4"), "not json", "still not json", batch("q5", "q6")])
    pool, recs = c_ideas.generate_ideas(
        [_dec()],
        _inv(),
        srcs,
        "CROSS-ROLE",
        "MATCHES",
        "ROLES-TABLE",
        ROLES,
        client,
        designs=designs,
        seeds=[0, 1],
        n_ideas=2,
        min_new=1,
        temperature=0.9,
        max_retries=1,
        log_dir=None,
    )
    assert [c.question for c in pool.candidates] == ["q1", "q2", "q3", "q4", "q5", "q6"]
    assert [(c.design, c.seed) for c in pool.candidates][4] == ("case_only", 1)
    assert pool.failed_calls == ["C_ideas_case_only_s0"]
    assert len(recs) == 4 and [r.ok for r in recs].count(False) == 1
    first = client.calls[0]
    assert "- ncfrp / Scene [NEW, 1 variables, none used by the manuscripts]: sleep surface" in first
    assert "CROSS-ROLE" in first and "MATCHES" in first
    assert first.rstrip().endswith(designs["case_population"].instruction)
    md = c_ideas.pool_markdown(pool)
    assert "Failed calls (no ideas): C_ideas_case_only_s0" in md and "**I5** (seed 1, fake-1) q5" in md
    assert "- Sources: case series: ncfrp; population reference: prams" in md and "- Domains: ncfrp / Scene" in md


def test_ideas_prompt_is_primed_with_the_source_roles():
    from mmf.llm.prompts import load_primed_prompt

    p = load_primed_prompt("c_ideas", "ROLES-TABLE")
    assert p.system.startswith("You are a data scientist working in epidemiology study design.")
    assert p.system.rstrip().endswith("ROLES-TABLE") and "$" not in p.system
    assert "$design" in p.user_template
    assert load_primed_prompt("c_ideas", "other").sha256 == p.sha256  # hash covers the files, not the roles


def test_designs_carry_no_topic_specific_examples():
    text = " ".join(d.instruction for d in c_ideas.DESIGNS.values()).lower()
    for word in ("suid", "sids", "sleep", "infant", "pca", "postconceptional", "smoking", "bed", "prams", "ncfrp"):
        assert word not in text, word


def test_source_roles_config_and_cross_role_table(sources):
    from mmf.components import roles
    from mmf.config import SourceSpec
    from mmf.schemas.dataset import ConceptMapping, SchemaMap

    specs = [
        SourceSpec(id="cdc", path="x", denominator=True, roles=["case"], years="2015"),
        SourceSpec(id="prams", path="y", roles=["reference"], weight_variable="WTANAL"),
    ]
    assert specs[0].roles == ["case", "denominator"] and specs[0].denominator
    assert SourceSpec(id="n", path="z", roles=["denominator"]).denominator
    prams = sources["cdc"].model_copy(update={"id": "prams", "title": "survey"})
    srcs = {"cdc": sources["cdc"], "prams": prams}
    assert roles.role_problems(specs, srcs) == ["prams: weight_variable 'WTANAL' is not a documented variable"]
    text = roles.source_roles_text(specs, srcs)
    assert "- cdc (mini). Role: case series and denominator." in text and "Period: 2015." in text
    smap = SchemaMap(
        mappings=[
            ConceptMapping(concept="smoking", source_id="cdc", variable="CIG_REC", compatibility="direct"),
            ConceptMapping(concept="smoking", source_id="prams", variable="SEX", compatibility="proxy"),
            ConceptMapping(concept="age", source_id="cdc", variable="AGED", compatibility="direct"),
            ConceptMapping(concept="sex", source_id="prams", variable=None, compatibility="none"),
        ]
    )
    table = roles.cross_role_concepts(smap, specs)
    assert set(table) == {"smoking", "age"}
    lines = roles.cross_role_text(table).splitlines()
    assert lines[0].startswith("- smoking [3 role(s)]")  # case + reference comes first
    assert "population reference: prams:SEX (proxy)" in lines[0]
