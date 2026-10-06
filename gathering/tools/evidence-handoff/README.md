# Evidence handoff

Combine Line 2's ZTO allowance inspection and Line 3's contract evidence at
one canonical Ethereum mainnet block hash. Attach Line 1's portable inventory
of the actual source used, plus a SHA-256 digest of the bundle. Python standard
library only; run from the repository root. No installation is needed.

One offline command:

```sh
python3 -B gathering/tools/evidence-handoff/evidence_handoff.py --self-test
```

The self-test uses explicitly synthetic RPC responses, exercises both real
readers and the inventory, and checks wrong-chain, unpinned-read and transaction
method rejection. It passed on 2026-10-06. It never claims fixture data is live.

Live command (only public JSON-RPC reads):

```sh
python3 -B gathering/tools/evidence-handoff/evidence_handoff.py --live
```

Tried successfully against `https://ethereum.publicnode.com`: both readers
reported mainnet block 26135233 and the same block hash. The ZTO allowance of
PoolManager to itself was zero; all three contracts returned deployed code.
`gathering/live-evidence.json` retains a later successful observation with a
source inventory including this README. The default owner/spender is an
inspection example, not a recommendation to approve PoolManager. Set `--owner`
and `--spender` to public addresses for your own inspection. ZTO is used first;
IMD is included in the contract evidence.

The bridge imports the reviewed line modules without writing bytecode and
adapts their RPC functions in memory. `shared/pinned_rpc.py` substitutes a single
EIP-1898 canonical block hash for Line 3's block-number reads. A failed call
produces no partial bundle. This requires an endpoint supporting EIP-1898.
No wallet, keys, signing, transaction submission, environment discovery or
non-workspace file reads are implemented. Output goes to stdout only.

Limits: an RPC provider can lie; hashes establish consistency, not truth or
authorship. A canonical block can later be reorganized. This is ETH balance,
bytecode and one ERC-20 allowance observation, not a full audit or approval
discovery. Inventory reads require a quiet workspace; dependencies must be
reviewed before executing the bridge. Source changes intentionally invalidate
an old inventory. To copy this tool elsewhere, include the two imported line
tool directories and `shared/handoff.py` and `shared/pinned_rpc.py` at the same
relative paths. Nothing depends on this cave's artwork or records.
