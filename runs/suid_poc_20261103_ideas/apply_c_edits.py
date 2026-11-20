"""Apply the approved C edit list (2026-11-11) to runs/suid_poc_20261103/C_gaps.json.
Rebuilds from C_gaps.pre-review.json. Run from the repo root."""

import json
import shutil
from pathlib import Path

RUN = Path("runs/suid_poc_20261103")
SRC, BAK = RUN / "C_gaps.json", RUN / "C_gaps.pre-review.json"
if not BAK.exists():
    shutil.copy2(SRC, BAK)


def refs(*names: str) -> list[dict[str, str]]:
    return [{"source_id": "cdc_linkco15", "name": n} for n in names]


gaps = [
    {
        "id": "G1",
        "statement": "Whether maternal prepregnancy obesity modifies SUID incidence differently across postconceptional "
        "age (PCA) windows has not been examined.",
        "rationale": "Maternal BMI is an established SUID risk factor in the literature, but neither manuscript included "
        "it. Estimating its association separately in the early rising (36-42 weeks) and late declining (>=47 weeks) PCA "
        "windows tests whether this risk is developmentally timed, extending the PCA framework to a new exposure.",
        "prior_art": "The literature abstracts report that maternal obesity raises SUID risk, increasing with BMI "
        "(suid_literature_abstracts.C10), without any developmental alignment. The PCA manuscript defined early and late "
        "PCA windows (SUID_manuscript_v9_clean.C5) but modelled sex and smoking, not maternal BMI.",
        "supporting_claim_ids": ["suid_literature_abstracts.C10", "SUID_manuscript_v9_clean.C5"],
        "required_concepts": [
            "Maternal prepregnancy body mass index (BMI)",
            "Postconceptional age (PCA)",
            "Sudden unexpected infant death (SUID)",
        ],
        "required_variables": refs("BMI_R", "COMBGEST", "AGED", "UCOD"),
    },
    {
        "id": "G2",
        "statement": "The joint effect of maternal smoking and preterm birth on SUID incidence across PCA windows has "
        "not been estimated.",
        "rationale": "Maternal smoking and prematurity are each strong, persistent correlates of SUID incidence across "
        "PCA, and prematurity is about twice as strong early as late. Whether smoking-associated risk differs between "
        "preterm and term infants within each PCA window is untested and bears on targeting prevention.",
        "prior_art": "The bed-sharing manuscript found maternal smoking the largest and most consistent correlate in "
        "both windows (bedsharing_ms_v7.C12) and prematurity positive throughout but stronger early (C13). Its "
        "interaction terms were bed sharing by smoking and bed sharing by preterm birth (C30); smoking by preterm birth "
        "was not estimated.",
        "supporting_claim_ids": ["bedsharing_ms_v7.C12", "bedsharing_ms_v7.C13", "bedsharing_ms_v7.C30"],
        "required_concepts": [
            "Maternal smoking during pregnancy",
            "Preterm birth",
            "Postconceptional age (PCA)",
            "Sudden unexpected infant death (SUID)",
        ],
        "required_variables": refs("CIG_REC", "GESTREC3", "COMBGEST", "AGED", "UCOD"),
    },
    {
        "id": "G3",
        "statement": "Whether the rise-peak-decline pattern of SUID incidence by PCA differs across cause-of-death "
        "subtypes (SIDS R95, accidental suffocation and strangulation in bed W75, ill-defined R99) is unknown.",
        "rationale": "Certification of sudden infant deaths shifts between R95, R99 and W75 by certifier and "
        "circumstance. If the subtypes follow different PCA trajectories, the pooled SUID curve mixes distinct "
        "developmental patterns; if they share one trajectory, the pooled PCA finding is robust to the "
        "cause-of-death misclassification the PCA manuscript names as a limitation.",
        "prior_art": "The PCA manuscript found a clear rise, peak and decline in PCA-aligned SUID incidence "
        "(SUID_manuscript_v9_clean.C6) for R95, R99 and W75 pooled, and noted that vital-record data may misclassify "
        "cause of death (C12). Subtype-specific PCA trajectories were not reported.",
        "supporting_claim_ids": ["SUID_manuscript_v9_clean.C6", "SUID_manuscript_v9_clean.C12"],
        "required_concepts": ["Sudden unexpected infant death (SUID)", "Postconceptional age (PCA)"],
        "required_variables": refs("UCOD", "COMBGEST", "AGED"),
    },
]
SRC.write_text(json.dumps({"gaps": gaps}, indent=2, ensure_ascii=False) + "\n")
print("wrote", SRC)
