---
stage: B
approved: true
---
# Review checkpoint: Schema map (stage B)

MMF proposed the structured output below. Review it, edit `B_*.json` in this run directory
if anything is wrong, then set `approved: true` above (or run `mmf approve <run_dir> B`) and
re-run `mmf run`. Downstream stages use the JSON file, not this rendering.

## Cross-check (embedding vs LLM)

An independent embedding pathway (`mxbai-embed-large`) ranked each source's variables for every concept.
It does not change the mappings; it flags where the two pathways disagree. Counts: agree 5.

- **llm_outside_topk**: the LLM's variable is not in the embedding top 10. Possible stretch or wrong mapping.
- **possible_miss**: the LLM mapped nothing, but an embedding candidate scores at least 0.65.

No disagreements.

Full records, including agreements: `B_check.json`.

```json
{
  "mappings": [
    {
      "concept": "outcome",
      "source_id": "cdc",
      "variable": "UCOD",
      "compatibility": "direct",
      "rationale": "The UCOD variable in the CDC data source includes codes R95, R99, and W75 which correspond to SIDS (Sudden Infant Death Syndrome), unspecified cause of death, and accidental suffocation respectively. These are the underlying cause of death codes specified as outcomes."
    },
    {
      "concept": "age at outcome",
      "source_id": "cdc",
      "variable": "AGED",
      "compatibility": "direct",
      "rationale": "The AGED variable in the CDC data source represents age at death in days, which directly corresponds to the concept of 'age at outcome'."
    },
    {
      "concept": "postconceptional age",
      "source_id": "cdc",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "The COMBGEST variable in the CDC data source represents combined gestation in weeks. To derive postconceptional age, one would need to add this value (converted from weeks to days) to the chronological age at death (which is not directly provided but can be inferred from AGED)."
    },
    {
      "concept": "male sex",
      "source_id": "cdc",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The SEX variable in the CDC data source indicates the sex of the infant, which can be used to stratify by male or female."
    },
    {
      "concept": "prenatal smoking",
      "source_id": "cdc",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The CIG_REC variable in the CDC data source indicates cigarette smoking during pregnancy, which is a proxy for prenatal smoking exposure."
    }
  ],
  "source_summaries": {
    "cdc": "The CDC data source provides variables that directly or indirectly support the concepts of outcome (UCOD), age at death (AGED), and sex (SEX). It also offers a variable (CIG_REC) to indicate prenatal smoking, which can be used as a proxy for exposure. However, deriving postconceptional age requires combining gestational weeks with chronological age data not directly provided."
  }
}
```