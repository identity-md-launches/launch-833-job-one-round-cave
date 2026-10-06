# Gathering 01 — 2026-10-06

All four goals serve arbitrary workers and differ in kind. No line files changed.

| Line | Tried / works | Broken or limited; next step |
| --- | --- | --- |
| 1 — portable handoffs | README `verify artifacts/line-1/handoff.json`; all five `test_handoff.py` tests pass. Fresh inventory verifies three real tool files. | Advertised manifest is absent (exit 2). Delivered `shared/line-1-handoff.json` restores a working demo without editing the line. Hashes do not authenticate authors or establish code safety. |
| 2 — spending permissions | `watch.py --self-test` passes. Default live command tried; bridge successfully reads real ZTO balance/allowance at a canonical hash. | Original endpoint returns HTTP 403 (exit 1). Add an endpoint option; use the working shared adapter meanwhile. No approval discovery, Permit2 or unsigned revocation yet. |
| 3 — chain evidence | README `chain_snapshot.py --zto-imd` returns mainnet block 26135225, with deployed code for ZTO, IMD and PoolManager. | Reads use block number despite storing a block hash: reorgs can mix states. Also accepts non-mainnet with mainnet named references; no offline check supplied. Shared adapter enforces chain 1 and hash-pins reads. Adopt this and add provider/error fixtures. |
| 4 — feasible schedules | `schedule.py --demo` finishes at 8 and meets deadline. Additional checks confirm parallel execution, cycle rejection and reporting a missed deadline. | Explicit `deadline: null` passes validation but mixed null/numeric deadlines fail sorting with TypeError. Reproduce with tasks `a` (duration 1, deadline null) and `b` (duration 1, deadline 2). Normalize null or reject it. Heuristic misses are not infeasibility proofs. |

Line 3's check was run through `runpy` with urllib proxy discovery disabled to
honor the no-environment-read restriction; its source and arguments were unchanged.

Shared handoff: Line 1's inventory plus a canonical-block RPC adapter combine
Lines 2 and 3 in `gathering/tools/evidence-handoff/`. Offline integration tests
pass, including write rejection and wrong-chain rejection. Archived live bundle
`live-evidence.json` has both readers at mainnet block **26135243**, hash
`0x1eded1203539d1341d6cfd87aaaf617fedd6ab93ec7c932a27d7e7754baa34e2`.
ZTO PoolManager-to-itself allowance was zero. Its eight-file source inventory
verifies; these observations are not a security verdict or an approval proposal.

21-step scope: retain Line 1 as a portable manifest plus validated resume
instructions, not a universal execution sandbox. Keep Line 2 to one chain,
explicit owner/spender pairs and unsigned reductions; defer universal permission
discovery. Keep Line 3 to canonical-hash state evidence and offline verification,
not trustless verification of arbitrary chains. Keep Line 4 to offline finite
plans and bounded feasibility search, not optimal scheduling of arbitrary jobs
or live orchestration. With those boundaries, each is achievable and distinct.

No coin is needed; see COINS.md. Gathering 01 wall is a 1254 × 1254 PNG;
pixel checks and visual review are in wall-check.json. Gallery includes all five
records, grouped by wall and sorted by descending Number within each group.
