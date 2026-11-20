"""Apply the approved B edit list (E1-E15, decision 2: drop cdc_codenames) to runs/suid_poc_20261103/B_schema.json.
Approved by the investigator on 2026-11-11. Writes a backup first. Run from the repo root with `uv run python`."""

import json
import shutil
import sys
from pathlib import Path

RUN = Path("runs/suid_poc_20261103")
SRC = RUN / "B_schema.json"
BAK = RUN / "B_schema.pre-review.json"
TAG = "[review 2026-11-11] "
SOURCES = ["cdc_linkco15", "cdc_natl15", "ncfrp_v51", "prams_p8_arf", "prams_p8_std2", "prams_p7_arf"]

if not BAK.exists():
    shutil.copy2(SRC, BAK)
doc = json.loads(BAK.read_text())  # always rebuild from the unedited model output
rows = doc["mappings"]

# Decision 2: cdc_codenames is no longer a mapping source.
rows = [r for r in rows if r["source_id"] != "cdc_codenames"]

# E1: drop concepts with no real mapping anywhere (the 32 mouse/neuron/cell concepts); keep chronological age.
real = {r["concept"] for r in rows if r["compatibility"] != "none"}
mouse = sorted({r["concept"] for r in rows} - real - {"chronological age"})
assert len(mouse) == 32, mouse
rows = [r for r in rows if r["concept"] not in mouse]

SEX = ["Infant sex", "sex (male, female)", "sex"]
SUID = ["Sudden unexpected infant death (SUID)", "SUID"]
PCA = ["Postconceptional age (PCA)", "postconceptional age", "PCA (postconceptional age)"]
BW = ["birthweight (low, non-low)", "birthweight"]
SMOKE = ["Maternal smoking during pregnancy", "maternal smoking status (smoking, non-smoking)"]


def keep(concept: str, source: str, var: str) -> tuple[str, str, str]:
    """Keep the model's own row (compatibility and rationale) for this variable."""
    (r,) = [x for x in doc["mappings"] if x["concept"] == concept and x["source_id"] == source and x["variable"] == var][:1]
    return (var, r["compatibility"], r["rationale"])


SPEC: dict[tuple[str, str], list[tuple[str, str, str]]] = {}


def setrows(concepts: list[str], source: str, items: list[tuple[str, str, str]]) -> None:
    for c in concepts:
        SPEC[(c, source)] = items


# E2 + E3: sex, one row per variable (fixes the rows filed under "sex (male, female)").
d = "direct"
setrows(SEX, "cdc_linkco15", [("SEX", d, TAG + "Sex of infant.")])
setrows(SEX, "cdc_natl15", [("SEX", d, TAG + "Sex of infant.")])
setrows(SEX, "ncfrp_v51", [("INFsex", d, TAG + "Sex of the deceased child. RES1sex/RES2sex (caregivers), ACTcausex (person who caused the death) and INFgenderid (gender identity) removed.")])
setrows(SEX, "prams_p8_arf", [("SEX", d, TAG + "Gender of infant.")])
setrows(SEX, "prams_p7_arf", [("SEX", d, TAG + "Gender of infant.")])
setrows(SEX, "prams_p8_std2", [])
# E4: SUID.
for c in SUID:
    SPEC[(c, "ncfrp_v51")] = [
        ("REGsuidcat", d, TAG + "SUID Case Registry categorization of the death."),
        ("CAUicdcode", d, TAG + "ICD-10 cause-of-death code from vital records; permits R95/R99/W75."),
        ("CAUdcimmcau", "proxy", TAG + "Immediate cause of death from the death certificate; not coded to the SUID definition."),
    ]
    SPEC[(c, "cdc_linkco15")] = [
        ("UCOD", d, TAG + "ICD-10 underlying cause of death; permits the exact R95/R99/W75 definition."),
        keep(c, "cdc_linkco15", "UCODR130"),
    ]
# E5: PCA = gestational age at birth + postnatal age.
for c in PCA:
    SPEC[(c, "cdc_linkco15")] = [
        ("COMBGEST", "derived", TAG + "PCA (weeks) = COMBGEST + AGED/7."),
        ("AGED", "derived", TAG + "Age at death in days; PCA = COMBGEST + AGED/7."),
    ]
    SPEC[(c, "cdc_natl15")] = [
        ("COMBGEST", "derived", TAG + "Births by gestational age, the person-time denominator by PCA; natality has no death age."),
    ]
    SPEC[(c, "ncfrp_v51")] = [
        ("INFgestage", "derived", TAG + "PCA (weeks) = INFgestage + INFdayslive/7."),
        ("INFdayslive", "derived", TAG + "Days lived; PCA = INFgestage + INFdayslive/7."),
    ]
# E6, E7: age at death.
SPEC[("chronological age", "cdc_linkco15")] = [("AGED", d, TAG + "Age at death in days.")]
SPEC[("chronological age", "ncfrp_v51")] = [("INFdayslive", d, TAG + "Days lived (from DOB and DOD).")]
SPEC[("Age of death in SUID cases", "cdc_linkco15")] = [("AGED", d, TAG + "Age at death in days.")]
# E8: gestational age, preterm birth.
for s in ["prams_p8_arf", "prams_p7_arf"]:
    SPEC[("Gestational age at birth", s)] = [("GEST_WK_PU", "proxy", TAG + "Clinical estimate in weeks, top/bottom coded at 27 and 43.")]
    SPEC[("Preterm birth", s)] = [("GEST_WK_PU", "derived", TAG + "Preterm = GEST_WK_PU < 37.")]
SPEC[("Preterm birth", "ncfrp_v51")] = [("INFgestage", "derived", TAG + "Preterm = INFgestage < 37.")]
# E9: birthweight.
for c in BW:
    for s in ["cdc_linkco15", "cdc_natl15"]:
        SPEC[(c, s)] = [("BWTR4", "derived", TAG + "Low birthweight = levels 1-2 (<2,500 g).")]
    SPEC[(c, "ncfrp_v51")] = [
        ("INFbirthwtcat", d, TAG + "Birth weight category."),
        ("INF3birthwtcat", d, TAG + "Birth weight category (second form section)."),
    ]
    for s in ["prams_p8_arf", "prams_p7_arf"]:
        SPEC[(c, s)] = [("GRAM_NAPHSIS", "derived", TAG + "250-g intervals; low = midpoint < 2,500 g.")]
    SPEC[(c, "prams_p8_std2")] = []
# E10: BMI.
B = "Maternal prepregnancy body mass index (BMI)"
for s in ["cdc_linkco15", "cdc_natl15"]:
    SPEC[(B, s)] = [("BMI", d, TAG + "Prepregnancy BMI."), ("BMI_R", d, TAG + "Prepregnancy BMI recode.")]
SPEC[(B, "ncfrp_v51")] = [("INF4mombmi", d, TAG + "Mother's BMI, computed from height and weight.")]
for s in ["prams_p8_arf", "prams_p7_arf"]:
    SPEC[(B, s)] = [
        ("MOM_BMI_BC", d, TAG + "Maternal BMI from the birth certificate."),
        ("MOM_BMI", "proxy", TAG + "Maternal BMI from the questionnaire (self-report)."),
    ]
# E11: infections = chlamydia, gonorrhea, hepatitis C.
I = "Maternal infections in pregnancy"
for s in ["cdc_linkco15", "cdc_natl15"]:
    SPEC[(I, s)] = [
        ("IP_CHLAM", d, TAG + "Chlamydia in pregnancy."),
        ("IP_GON", d, TAG + "Gonorrhea in pregnancy."),
        ("IP_HEPC", d, TAG + "Hepatitis C in pregnancy."),
    ]
SPEC[(I, "ncfrp_v51")] = [
    ("INF3chlamydia", d, TAG + "Pregnancy complication: chlamydia."),
    ("INF3gonorrhea", d, TAG + "Pregnancy complication: gonorrhea. NCFRP has no hepatitis C item."),
]
# E12: bed sharing.
SPEC[("bed sharing", "ncfrp_v51")] = [
    keep("bed sharing", "ncfrp_v51", "CIRsamesurf"),
    ("CIRwadult", d, TAG + "Same sleep surface with adult(s)."),
]
SPEC[("bed sharing", "prams_p7_arf")] = []  # SLEEPPOS_RAW is sleep position, not bed sharing
SPEC[("bed sharing", "prams_p8_arf")] = [("SLEEPOWN_RAW", "proxy", TAG + "How often baby sleeps alone; inverse proxy for bed sharing in live infants.")]
# E13: smoking.
for c in SMOKE:
    for s in ["cdc_linkco15", "cdc_natl15"]:
        SPEC[(c, s)] = [("CIG_REC", d, TAG + "Any cigarette smoking in pregnancy (Y/N).")]
# E14: breastfeeding at discharge.
BF = "Breastfeeding status at discharge"
for s in ["prams_p8_arf", "prams_p7_arf"]:
    SPEC[(BF, s)] = [("BF5EVER_RAW", "proxy", TAG + "Ever breastfed, not status at discharge.")]
SPEC[(BF, "ncfrp_v51")] = [("INFbreast", "proxy", TAG + "Ever breastfed, not status at discharge.")]
# E15: year.
for s in ["cdc_linkco15", "cdc_natl15"]:
    SPEC[("year of birth or death", s)] = [("DOB_YY", d, TAG + "Birth year. Death year (DOD_YY) is in the guide but not yet extracted.")]

concepts = list(dict.fromkeys(r["concept"] for r in rows))
for key in SPEC:
    assert key[0] in concepts, key
out = []
for c in concepts:
    for s in SOURCES:
        if (c, s) in SPEC:
            items = SPEC[(c, s)]
            new = [{"concept": c, "source_id": s, "variable": v, "compatibility": k, "rationale": why} for v, k, why in items]
        else:
            seen, new = set(), []
            for r in rows:
                if r["concept"] == c and r["source_id"] == s and (r["variable"], r["compatibility"]) not in seen:
                    seen.add((r["variable"], r["compatibility"]))
                    new.append(r)
        if not new:
            new = [{"concept": c, "source_id": s, "variable": None, "compatibility": "none", "rationale": TAG + "No matching variable."}]
        out.extend(new)

doc["mappings"] = out
doc["source_summaries"].pop("cdc_codenames", None)
SRC.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
print(f"mouse concepts dropped: {len(mouse)}; concepts kept: {len(concepts)}; rows {len(json.loads(BAK.read_text())['mappings'])} -> {len(out)}")
sys.exit(0)
