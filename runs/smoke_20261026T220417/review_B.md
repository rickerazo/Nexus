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
      "concept": "Age at death",
      "source_id": "cdc",
      "variable": "AGED",
      "compatibility": "direct",
      "rationale": "The variable AGED directly measures the age at death in days, which is compatible with the concept of age at death."
    },
    {
      "concept": "Cigarette smoking during pregnancy",
      "source_id": "cdc",
      "variable": "CIG_REC",
      "compatibility": "direct",
      "rationale": "The variable CIG_REC directly measures cigarette smoking during pregnancy, which is compatible with the concept."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "cdc",
      "variable": "COMBGEST",
      "compatibility": "direct",
      "rationale": "The variable COMBGEST directly measures combined gestation in weeks, which is compatible with the concept of gestational age."
    },
    {
      "concept": "Mother's age at birth",
      "source_id": "cdc",
      "variable": "MAGER9",
      "compatibility": "direct",
      "rationale": "The variable MAGER9 directly measures mother's age recode, which is compatible with the concept of mother's age."
    },
    {
      "concept": "Sex of infant",
      "source_id": "cdc",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable SEX directly measures the sex of the infant, which is compatible with the concept."
    },
    {
      "concept": "Cause of death",
      "source_id": "cdc",
      "variable": "UCOD",
      "compatibility": "direct",
      "rationale": "The variable UCOD directly measures the underlying cause of death using ICD-10 codes, which is compatible with the concept."
    }
  ],
  "source_summaries": {}
}
```