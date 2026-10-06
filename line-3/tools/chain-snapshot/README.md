# chain-snapshot

`chain-snapshot.py` creates a compact, deterministic evidence record for addresses on Ethereum. It first pins the latest block, then records each address's ETH balance and deployed bytecode hash at that exact block. The `evidence_sha256` is the hash of the canonical record before that field is attached, so a later worker can reproduce and compare the observation without trusting the RPC's current head. It makes only JSON-RPC read calls; it has no wallet, key, signing, or transaction behavior.

It defaults to the real ZTO token, IMD token, and the Uniswap v4 PoolManager that holds the declared ZTO/IMD pool reference. `--zto-imd` adds those named identifiers into the evidence bundle.

Run it with Python 3 (standard library only):

```sh
python3 line-3/tools/chain-snapshot/chain_snapshot.py --zto-imd
```

When tried during this step, the command returned an Ethereum mainnet, block-pinned JSON document with three code hashes and an `evidence_sha256`. The exact block naturally changes with the public chain. If the public RPC is unavailable, pass another public endpoint using `--rpc`; the tool reports a failure without producing a partial or fabricated snapshot.
