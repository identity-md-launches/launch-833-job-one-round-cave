# Allowance Watch

Read-only ERC-20 spending-permission inspection for any worker. Uses Python 3 and only its standard library. ZTO is the default; IMD is the second supported token. No dependencies, credentials, wallet access, signatures, writes, payments, or transaction submissions.

One command that works without a network, from the repository root:

```sh
python3 line-2/tools/allowance-watch/watch.py --self-test
```

Live mainnet demonstration:

```sh
python3 line-2/tools/allowance-watch/watch.py
```

The default examines the real Uniswap v4 PoolManager as both owner and spender; it is an inspection example, not an assertion that this contract should receive approvals. Supply `--owner 0x… --spender 0x…` to inspect a particular pair; select IMD with `--token IMD`.

The tool checks chain ID 1, obtains the latest block hash, and pins balanceOf and allowance calls to that canonical hash using EIP-1898. It prints raw integer token units as strings, currently spendable units, maximum uint256 allowance, and whether allowance extends to future deposits. No floating-point arithmetic or token-decimal assumptions.

Tried on 2026-10-06: offline ABI encoding, malformed address/ABI rejection, and exposure arithmetic tests passed. The public RPC request returned HTTP 403 in this execution environment; no live balance or allowance was obtained. RPC access is needed only for live mode, never for the offline demonstration.

Limits: only the specified spender is checked; this does not discover all historical approvals, inspect Permit2 permissions, or assess contract behavior. The exposure estimate is min(balance, allowance) under ordinary ERC-20 semantics. A canonical block may later be reorganized. Failures produce an error and no fabricated snapshot. Future rounds can add allowance discovery and unsigned permission-reduction preparation.
