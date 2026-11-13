# C redesign: generate many candidate gaps, then narrow them down (2026-11-12)

## Why
The investigator judged S1 and S2 of SUID report v2 unusable: the gaps restate the literature (a known risk factor × PCA windows). The causes are in C (HANDOFF §4 item 5f):
- The C prompt says to prefer extending the manuscripts' frameworks.
- C sees only the 66 variables B mapped to manuscript concepts, out of about 5,800 documented.
- Every gap must cite a supporting claim.
- C is one call at temperature 0, which returns the most likely answer.

## Decisions (investigator, 2026-11-12)
- Shortlist 10 candidates; the investigator picks 5 for D.
- Supporting claims become optional; `prior_art` stays mandatory and must name the closest tested work in the inputs, or say there is none.
- Try `qwen2.5:32b` for C1 alone (the machine has 32 GB).
- Build C0 and C1 first, and review the raw ideas before building C3 and C4. This replaces the temperature-only experiment.
- Evaluation protocol amendments A–I approved (see `docs/evaluation_protocol.md`).

## Steps
| Step | What | Model, temperature | Status |
|---|---|---|---|
| C0 data inventory | Every source's variables in consecutive blocks (`c_inventory_block_vars`, 150); the model splits each block into 1–8 contiguous topic domains by naming each domain's first variable. Coverage is complete by construction. Domains record which variables B mapped (`used`). | `model`, `temperature` (0) | Built (`c_ideas.build_inventory`) |
| C1 ideas | One free-text-style call per (lens, seed): 6 lenses × seeds `[0, 1, 2]` × 5 ideas = 90 candidates. Input is the findings, limitations and future work of each manuscript (no quotes or methods) plus the C0 inventory. A failed call is recorded and skipped. | `c_ideation_model` (default `model`), `c_ideation_temperature` (0.9) | Built (`c_ideas.generate_ideas`) |
| C2 dedupe | Embed with `mxbai-embed-large`; group near-duplicates; keep one per group. | none | To build |
| C3 grounding | Each idea becomes a `KnowledgeGap`. Allowed variables are the idea's nearest variables among all ~5,800 (embedding search), not B's mapped set. The current validators apply. | `model`, 0 | To build |
| C4 scoring | Novelty: embedding distance from every extracted claim (computed in code). Feasibility: passed the checks, a denominator, variables with levels. Importance: a model rating 1–5 that can only filter. Selection rule fixed in advance. | `model`, 0 | To build |
| C5 review | `review_C.md` shows the shortlist of 10; the investigator picks 5. | none | To build |

## Design notes
- **Lenses:** `unused_data`, `tensions`, `inversion`, `mechanism`, `cross_source`, `design`. Their text names no SUID-specific idea (a unit test enforces it): an example would steer every run toward it and contaminate the novelty measure and the B0 baseline.
- **C1 uses a light JSON schema, not unconstrained text.** The schema has only strings and a list of source ids, so constrained decoding barely limits the model, and the existing logging, retry and checkpoint code still applies. Only source ids are validated.
- **No `top_p` setting.** Ollama's default (0.9) applies. Adding it would change the `LLMClient` protocol for every backend and the replay client.
- **Not part of `mmf run` yet.** `mmf ideate CONFIG --run-dir DIR` runs C0 and C1 on a run whose B is approved and writes `C_inventory.json`, `C_ideas.json` and `C_ideas.md`. Each call is checkpointed under `checkpoints/C_inventory` and `checkpoints/C_ideas`.
- **`cdc_codenames` is still in the config,** so it appears in the inventory. It goes at the next full B rerun.

## First run
On a copy of `runs/suid_poc_20261103` (`runs/suid_poc_20261103_ideas`), so the approved B and C stay untouched.
1. C0 and C1 with `qwen2.5:14b`, then keep `C_ideas.md` as `C_ideas.14b.md`.
2. C1 again with `c_ideation_model: qwen2.5:32b`; C0 is a cache hit.

Estimate (not measured): about 44 inventory calls, 30–40 minutes; 18 idea calls, about 35 minutes at 14B and roughly twice that at 32B.

## Run log
- **Thu 15:29 PST, 14B:** stopped at 15:49 on `C_inventory_ncfrp_v51_11` after 4 attempts. In every attempt the model started its last domain at `INCTimeOfIncident` (position 4 in the block) when it meant `INCtimeofincqual` (position 91). This NCFRP block is ordered alphabetically, not by topic.
  - **Fix:** the retry message now gives the positions and warns that names differing in case or suffix are different variables.
  - **Fallback:** on the final attempt, domains whose start is unknown or out of order are dropped. Their variables fall into the previous domain, and the drop is recorded in the call's `dropped` list.
  - The 11 finished blocks resume from checkpoints.
- **Thu 15:50 PST, 14B resumed; done 16:42.**
  - C0: 338 domains covering 6,035 variables; 309 domains contain no variable the manuscripts use.
  - C1: 90 ideas from 18 calls, all accepted on the first attempt.
  - Recurring themes: obesity/BMI 23, smoking 23, PCA 20, SES 15. Eleven rely on something no source records (inner-ear dysfunction, chronic intermittent hypoxia, progesterone, decades).
  - Most questions take the form "does X affect SUID?". The model treats PRAMS as if it records deaths.
  - Saved as `C_ideas.14b.{md,json}`.
- **Thu 16:43 PST, 32B C1 (C0 cache hit); done Fri 01:45.**
  - About 9 hours, roughly 30 minutes per call, against an estimate of about 70 minutes. Memory is tight with 32 GB at a 32k context.
  - 90 ideas, all accepted on the first attempt. Recurring themes: obesity 16, smoking 19, PCA 14, SES 10. Two rely on unmeasured things.
  - Better grounded, and somewhat more varied in form: SUID compared with other causes of death, how consistently sleep environment is recorded across jurisdictions, documentation practices over time.
  - Still mostly "does X affect SUID?". The PRAMS-as-outcome error appears in every cross-source idea.
  - Saved as `C_ideas.32b.{md,json}`.
