#!/usr/bin/env python3
"""Join contract and allowance evidence at one block; inventory its source."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path.cwd()


def load(name, relative):
    path = ROOT
    for part in Path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Symlink refused: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect(session, owner, spender):
    watch = load('allowance_watch', 'line-2/tools/allowance-watch/watch.py')
    chain = load('chain_snapshot', 'line-3/tools/chain-snapshot/chain_snapshot.py')
    handoff = load('handoff', 'shared/handoff.py')
    watch.rpc = session.rpc
    chain.rpc = lambda unused_url, method, params: session.rpc(method, params)
    contracts = chain.snapshot(session.url, [chain.ZTO, chain.IMD, chain.POOL_MANAGER], True)
    allowance = watch.snapshot(owner, spender, watch.ZTO)
    if contracts['block']['hash'] != allowance['block_hash']:
        raise ValueError('Evidence does not share a block')
    result = {'schema': 'evidence-handoff/v1', 'contracts': contracts,
              'zto_allowance': allowance,
              'source_inventory': handoff.snapshot(ROOT, [
                  'line-2/tools/allowance-watch', 'line-3/tools/chain-snapshot',
                  'shared/handoff.py', 'shared/pinned_rpc.py',
                  'gathering/tools/evidence-handoff'])}
    result['bundle_sha256'] = hashlib.sha256(json.dumps(
        result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return result


def self_test(pinned):
    calls = []
    block = {'hash': '0x' + 'ab' * 32, 'number': '0x10', 'timestamp': '0x20'}
    def fixture(url, method, params):
        calls.append((method, params))
        if method == 'eth_chainId':
            return '0x1'
        if method == 'eth_getBlockByNumber':
            return dict(block)
        assert params[1] == {'blockHash': block['hash'], 'requireCanonical': True}
        if method == 'eth_getCode':
            return '0x6000'
        if method == 'eth_getBalance':
            return '0x0'
        if method == 'eth_call':
            return '0x' + format(9 if params[0]['data'].startswith('0x70a08231') else 4, '064x')
        raise AssertionError(method)
    session = pinned.PinnedRPC(read=fixture)
    result = collect(session, '0x' + '11' * 20, '0x' + '22' * 20)
    assert result['zto_allowance']['currently_spendable_raw'] == '4'
    assert len([c for c in calls if c[0] == 'eth_getBlockByNumber']) == 1
    digest = result.pop('bundle_sha256')
    assert digest == hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    handoff = load('handoff_test', 'shared/handoff.py')
    assert handoff.verify(ROOT, result['source_inventory'])['ok']
    for method, params in [('eth_getBalance', ['0x' + '11' * 20, 'latest']),
                           ('eth_sendRawTransaction', ['0x00'])]:
        try:
            session.rpc(method, params)
        except ValueError:
            pass
        else:
            raise AssertionError('Unsafe or unpinned request accepted')
    def wrong_chain(url, method, params):
        return '0xaa36a7'
    try:
        pinned.PinnedRPC(read=wrong_chain)
    except ValueError:
        pass
    else:
        raise AssertionError('Wrong chain accepted')
    print('PASS: synthetic offline fixtures; shared block, exposure, hashes, source inventory, wrong-chain and write rejection')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-test', action='store_true')
    mode.add_argument('--live', action='store_true')
    parser.add_argument('--rpc', default='https://ethereum.publicnode.com')
    parser.add_argument('--owner', default='0x000000000004444c5dc75cb358380d2e3de08a90')
    parser.add_argument('--spender', default='0x000000000004444c5dc75cb358380d2e3de08a90')
    args = parser.parse_args()
    try:
        pinned = load('pinned_rpc', 'shared/pinned_rpc.py')
        if args.self_test:
            self_test(pinned)
        else:
            watch = load('address_validation', 'line-2/tools/allowance-watch/watch.py')
            owner, spender = watch.address(args.owner), watch.address(args.spender)
            result = collect(pinned.PinnedRPC(args.rpc), owner, spender)
            print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
        print('evidence-handoff: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
