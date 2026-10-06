#!/usr/bin/env python3
"""Read-only Ethereum ERC-20 allowance snapshot; standard library only."""
import argparse
import json
import re
import urllib.request

ZTO = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'
IMD = '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7'
POOL_MANAGER = '0x000000000004444c5dc75cb358380d2e3de08a90'
RPC = 'https://ethereum-rpc.publicnode.com'
MAX = 2**256 - 1


def address(value):
    if not re.fullmatch(r'0x[0-9a-fA-F]{40}', value):
        raise ValueError('Expected a 20-byte 0x address')
    return value.lower()


def calldata(selector, *addresses):
    return '0x' + selector + ''.join(address(a)[2:].rjust(64, '0') for a in addresses)


def uint(value):
    if not isinstance(value, str) or not re.fullmatch(r'0x[0-9a-fA-F]{64}', value):
        raise ValueError('Expected exactly one ABI uint256 word')
    return int(value, 16)


def rpc(method, params):
    # No signing, wallet, file, environment, or transaction submission access.
    request = urllib.request.Request(RPC, json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params
    }).encode(), {'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=15) as response:
        result = json.load(response)
    if 'error' in result:
        raise ValueError('RPC error: ' + json.dumps(result['error']))
    return result['result']


def summarize(balance, allowance):
    return {'balance_raw': str(balance), 'allowance_raw': str(allowance),
            'currently_spendable_raw': str(min(balance, allowance)),
            'unlimited_allowance': allowance == MAX,
            'future_deposits_exposed': allowance > balance}


def snapshot(owner, spender, token):
    owner, spender, token = map(address, (owner, spender, token))
    if int(rpc('eth_chainId', []), 16) != 1:
        raise ValueError('Expected Ethereum mainnet')
    block = rpc('eth_getBlockByNumber', ['latest', False])
    # EIP-1898 pins every read to the same canonical block hash.
    at = {'blockHash': block['hash'], 'requireCanonical': True}
    def call(data):
        return uint(rpc('eth_call', [{'to': token, 'data': data}, at]))
    result = summarize(call(calldata('70a08231', owner)),
                       call(calldata('dd62ed3e', owner, spender)))
    result.update(chain_id=1, block_number=int(block['number'], 16),
                  block_hash=block['hash'], token=token, owner=owner, spender=spender)
    return result


def self_test():
    assert calldata('70a08231', ZTO) == '0x70a08231' + ZTO[2:].rjust(64, '0')
    assert len(calldata('dd62ed3e', ZTO, POOL_MANAGER)) == 138
    assert uint('0x' + 'f' * 64) == MAX
    assert summarize(9, 4)['currently_spendable_raw'] == '4'
    assert summarize(4, MAX)['future_deposits_exposed']
    assert not summarize(4, 0)['unlimited_allowance']
    for bad in ('0x1', '0x' + 'g' * 40):
        try:
            address(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid address accepted')
    for bad in ('0x', '0x01', '0x' + '0' * 128):
        try:
            uint(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid ABI accepted')
    print('PASS: ABI encoding, malformed input rejection, exposure arithmetic')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--owner', default=POOL_MANAGER)
    parser.add_argument('--spender', default=POOL_MANAGER)
    parser.add_argument('--token', choices=['ZTO', 'IMD'], default='ZTO')
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            print(json.dumps(snapshot(args.owner, args.spender,
                                      ZTO if args.token == 'ZTO' else IMD), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, 'Snapshot failed: ' + str(exc) + '\n')
