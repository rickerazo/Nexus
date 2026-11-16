from mmf.llm.prompts import load_prompt
from mmf.validate.vocab import vocab_text

NAMES = [
    "codebook_extract",
    "a_profile",
    "a_claims",
    "b_schema_map",
    "c_gaps",
    "c_inventory",
    "d_strategy",
    "e_caveats",
]


def test_all_prompts_load_and_hash():
    hashes = {n: load_prompt(n).sha256 for n in NAMES}
    assert len(set(hashes.values())) == len(NAMES)


def test_vocab_rendered_into_prompts():
    p = load_prompt("d_strategy")
    assert (
        "negative_binomial" in p.bind(vocab=vocab_text()).system and "$vocab" not in p.bind(vocab=vocab_text()).system
    )
