---
stage: B
approved: true
---
# Review checkpoint: Schema map (stage B)

MMF proposed the structured output below. Review it, edit `B_*.json` in this run directory
if anything is wrong, then set `approved: true` above (or run `mmf approve <run_dir> B`) and
re-run `mmf run`. Downstream stages use the JSON file, not this rendering.

```json
{
  "mappings": [
    {
      "concept": "outcome",
      "source_id": "cdc",
      "variable": "UCOD",
      "compatibility": "direct",
      "rationale": "The variable UCOD in the CDC data source captures the underlying cause of death using ICD-10 codes, which directly matches the manuscript's operationalization of outcome with specific codes R95 (SIDS), R99 (unspecified), and W75 (accidental suffocation)."
    },
    {
      "concept": "age at outcome",
      "source_id": "cdc",
      "variable": "AGED",
      "compatibility": "direct",
      "rationale": "The variable AGED in the CDC data source captures age at death in days, which directly corresponds to the manuscript's operationalization of age at outcome."
    },
    {
      "concept": "postconceptional age",
      "source_id": "cdc",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "The variable COMBGEST in the CDC data source captures combined gestation in weeks, which can be used to derive postconceptional age by adding it to the chronological age after birth. However, since the exact chronological age is not provided, this mapping is derived and requires additional information."
    },
    {
      "concept": "male sex",
      "source_id": "cdc",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable SEX in the CDC data source captures the sex of the infant, which directly corresponds to the manuscript's operationalization of male sex as a stratifying variable."
    },
    {
      "concept": "prenatal smoking",
      "source_id": "cdc",
      "variable": "CIG_REC",
      "compatibility": "direct",
      "rationale": "The variable CIG_REC in the CDC data source captures cigarette smoking during pregnancy, which directly corresponds to the manuscript's operationalization of prenatal smoking as an exposure variable."
    }
  ],
  "source_summaries": {
    "cdc": "The CDC data source provides variables that capture age at death (AGED), underlying cause of death (UCOD), combined gestation in weeks (COMBGEST), sex of infant (SEX), and cigarette smoking during pregnancy (CIG_REC). These variables directly or derivatively support the concepts of outcome, age at outcome, postconceptional age, male sex, and prenatal smoking as described in the manuscripts. However, for postconceptional age, additional information on chronological age after birth is needed to compute this derived variable accurately."
  }
}
```