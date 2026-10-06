"""Small public Ethereum reader: no proxy discovery, credentials or writes."""
import json
import re
import urllib.request

DEFAULT_RPC = 'https://ethereum.publicnode.com'
READS = {'eth_chainId', 'eth_getBlockByNumber', 'eth_getCode',
         'eth_getBalance', 'eth_call'}


def transport(url, method, params):
    if method not in READS:
        raise ValueError('Only explicitly allowed read methods are supported')
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Expected public HTTPS endpoint without credentials')
    request = urllib.request.Request(url, json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params
    }).encode(), {'Content-Type': 'application/json',
                 'User-Agent': 'evidence-handoff/1.0'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=20) as response:
        raw = response.read(1048577)
    if len(raw) > 1048576:
        raise ValueError('RPC response exceeds 1 MiB')
    reply = json.loads(raw)
    if not isinstance(reply, dict) or reply.get('id') != 1 or 'error' in reply or 'result' not in reply:
        raise ValueError('Invalid or failed RPC reply')
    return reply['result']


class PinnedRPC:
    """Adapt number-based readers to one mainnet canonical block hash."""
    def __init__(self, url=DEFAULT_RPC, read=transport):
        self.url, self.read = url, read
        if read(url, 'eth_chainId', []) != '0x1':
            raise ValueError('Expected Ethereum mainnet')
        self.block = read(url, 'eth_getBlockByNumber', ['latest', False])
        if not isinstance(self.block, dict) or not re.fullmatch(
                r'0x[0-9a-fA-F]{64}', self.block.get('hash', '')):
            raise ValueError('Invalid block hash')
        for key in ('number', 'timestamp'):
            if not re.fullmatch(r'0x[0-9a-fA-F]+', self.block.get(key, '')):
                raise ValueError('Invalid block ' + key)
        self.at = {'blockHash': self.block['hash'], 'requireCanonical': True}

    def rpc(self, method, params):
        if method == 'eth_chainId' and params == []:
            return '0x1'
        if method == 'eth_getBlockByNumber' and params == ['latest', False]:
            return dict(self.block)
        if method in {'eth_getCode', 'eth_getBalance', 'eth_call'} and len(params) == 2:
            if params[1] != self.block['number'] and params[1] != self.at:
                raise ValueError('Reader attempted a different block')
            return self.read(self.url, method, [params[0], dict(self.at)])
        raise ValueError('Unsupported read operation')
