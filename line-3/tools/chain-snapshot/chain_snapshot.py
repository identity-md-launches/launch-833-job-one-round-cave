#!/usr/bin/env python3
"""Make a small, deterministic evidence bundle from public Ethereum JSON-RPC."""

import argparse
import hashlib
import json
import sys
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

DEFAULT_RPC = "https://ethereum.publicnode.com"
ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"
IMD = "0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7"
POOL_MANAGER = "0x000000000004444c5dc75cB358380D2e3dE08A90"
POOL_ID = "0x888b07bd282f587d3c6b0fcb23e7fc55bbb33abe8910dd7492db815dc8dc5592"


def rpc(url, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                          "params": params}, separators=(",", ":")).encode("utf-8")
    request = Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "chain-snapshot/1.0 (read-only evidence tool)",
    })
    try:
        with urlopen(request, timeout=20) as response:
            reply = json.loads(response.read().decode("utf-8"))
    except (URLError, HTTPError, TimeoutError, ValueError) as exc:
        raise RuntimeError("RPC request failed: " + str(exc)) from exc
    if reply.get("error"):
        raise RuntimeError("RPC error: " + json.dumps(reply["error"], sort_keys=True))
    return reply["result"]


def normal_address(value):
    value = value.lower()
    if len(value) != 42 or not value.startswith("0x") or any(c not in "0123456789abcdef" for c in value[2:]):
        raise argparse.ArgumentTypeError("address must be a 20-byte 0x hex value")
    return value


def snapshot(rpc_url, addresses, include_pool):
    block = rpc(rpc_url, "eth_getBlockByNumber", ["latest", False])
    block_number = block["number"]
    records = []
    for address in addresses:
        code = rpc(rpc_url, "eth_getCode", [address, block_number])
        balance = rpc(rpc_url, "eth_getBalance", [address, block_number])
        records.append({
            "address": address,
            "balance_wei": str(int(balance, 16)),
            "code_bytes": max(0, (len(code) - 2) // 2),
            "code_sha256": hashlib.sha256(bytes.fromhex(code[2:])).hexdigest(),
        })
    evidence = {
        "schema": "chain-snapshot/v1",
        "chain_id": int(rpc(rpc_url, "eth_chainId", []), 16),
        "block": {"number": int(block_number, 16), "hash": block["hash"], "timestamp": int(block["timestamp"], 16)},
        "contracts": records,
    }
    if include_pool:
        evidence["named_reference"] = {
            "zto": ZTO, "imd": IMD, "uniswap_v4_pool_manager": POOL_MANAGER,
            "zto_imd_pool_id": POOL_ID,
        }
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
    evidence["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
    return evidence


def main():
    parser = argparse.ArgumentParser(description="Create block-pinned, read-only Ethereum contract evidence.")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="public Ethereum JSON-RPC URL")
    parser.add_argument("--address", action="append", type=normal_address, help="contract/address to record (repeatable)")
    parser.add_argument("--zto-imd", action="store_true", help="snapshot ZTO, IMD, and their Uniswap v4 PoolManager")
    args = parser.parse_args()
    addresses = args.address or ([] if args.zto_imd else [ZTO, IMD, POOL_MANAGER])
    if args.zto_imd:
        addresses.extend([ZTO, IMD, POOL_MANAGER])
    addresses = list(dict.fromkeys(addresses))
    if not addresses:
        parser.error("provide --address or use --zto-imd")
    try:
        print(json.dumps(snapshot(args.rpc, addresses, args.zto_imd), sort_keys=True, indent=2))
    except RuntimeError as exc:
        print("chain-snapshot: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
