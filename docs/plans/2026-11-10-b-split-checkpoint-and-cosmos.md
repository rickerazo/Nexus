# Plan: B multi-variable split + per-call checkpoints, and Epic Cosmos addendum (2026-11-10)

Approved by the user on Tue 2026-11-10. Times are PST.

## Context
- Monday's restart of `runs/suid_poc_20261103` (at commit `f351764`) failed Mon 2026-11-09 at 16:03 PST.
  The failing call was `B_schema_map_3_0` (ncfrp_v51), the 9th of about 28 B calls.
- All four attempts listed several real variables in one `variable` field (`'INF3chlamydia, INF3gonorrhea'`,
  `'CIG0_R, CIG1_R, CIG2_R, CIG3_R'`). Every one of those names is documented. The validator still called the
  whole string undocumented, so the model was never told what to fix.
- B saved nothing until all its calls finished, so the 8 calls that had passed were lost.
- The user also asked to add Epic Cosmos as a data source. Its Data Dictionary is only available after logging
  into cosmos.epic.com. The user chose **Both**: a cited public stub now, and the real dictionary once they
  export it.

## Steps and status
| # | Step | Status |
|---|---|---|
| 1 | Validator: a multi-name `variable` passes if every part is documented. Otherwise it names only the bad parts and says "one variable name per mapping". | Done, `9d78c98` |
| 2 | `expand_multi`: split such rows into one row per variable (copying compatibility and rationale) and add a warning. | Done, `9d78c98` |
| 3 | Prompt: "`variable` holds exactly one name; write a separate mapping for each". | Done, `9d78c98` |
| 4 | Per-call checkpoints in `run_dir/checkpoints/B/<stage>_<key16>.json`, keyed by model, seed, temperature, num_ctx, prompt hash, rendered input and output schema. A hit is re-validated. A warning reports "resumed N of M". | Done, `9d78c98` |
| 5 | Tests: split, partly-undocumented rejection, a checkpoint surviving a failure, resume equal to a fresh run. Results: 52 pass, ruff and mypy clean. | Done |
| 6 | Offline replay of the failed call: attempt 1 now passes (4 rows split); attempt 4 is still rejected on 2 truly undocumented names. | Done |
| 7 | Preserve the failed logs (`runs/suid_poc_20261103.mon-failed.log`, `.driver.mon-failed.log`). Restart without `--auto-approve`. | Done, Tue 2026-11-10 14:09 PST |
| 8 | Cosmos public stub: [../data_sources/epic_cosmos.md](../data_sources/epic_cosmos.md). It is kept out of `codebooks:`. | Done, `483e06e` |
| 9 | Wait for `Stopped at review B` in `runs/suid_poc_20261103.driver.log` (about 4–5 h). If it fails, rerun the same command and B resumes from the checkpoints. | **Pending** |
| 10 | Rerun once without approving: `uv run mmf run configs/suid.yaml --run-dir runs/suid_poc_20261103`. B is a cache hit; this adds `B_check.json` and the cross-check section in `review_B.md`. | Pending |
| 11 | Propose a B edit list: cross-check flags first, then wrong or stretched mappings (e.g. SUID → infection variables), near-duplicates, and deleting the mouse/neuron concepts. **No edits to `B_schema.json` until the user approves.** | Pending |
| 12 | Approve, then run to C. Review C the same way, with no edits to `C_gaps.json` without approval. Before D runs, propose making D's `Strategy` LLM-facing fields required and nullable, and get the user's go-ahead. Then D, E, the report and HANDOFF. | Pending |
| 13 | Cosmos, real dictionary: the user exports it (CSV or Excel) into `data/documentation/`. Check whether `pass1_table` handles `Table.Column` names; if not, add a Cosmos branch, bump `PARSER_VERSION` and add tests. Add `epic_cosmos` to `configs/suid.yaml`. This re-runs B in full. | Waiting on the user |

## Rules
- Never push; the user pushes with the deploy key's passphrase.
- Local Ollama only. Start `ollama serve` if it is down.
- State all times in PST.

## Verification
- `uv run pytest`, `uv run ruff check src tests scripts`, `uv run mypy src`.
- `ls runs/suid_poc_20261103/checkpoints/B | wc -l` grows toward about 28.
- `tail -3 runs/suid_poc_20261103.driver.log` shows `Stopped at review B`.
