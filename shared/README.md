# Shared pieces, gathering 01

- `handoff.py`: exact copy of Line 1's reviewed inventory tool. Any worker can
  use it to check evidence, plans or deliverables offline. The missing original
  demo manifest is replaced here by `line-1-handoff.json`, covering the unchanged
  Line 1 tool directory. Run `python3 -B shared/handoff.py verify shared/line-1-handoff.json`.
- `pinned_rpc.py`: gathering glue for Lines 2 and 3. It verifies mainnet once,
  selects one block, and pins all state reads to its canonical hash. It permits
  only listed read methods, uses public HTTPS without credential fields, limits
  response size and disables implicit proxy environment discovery.
- `../gathering/tools/evidence-handoff/`: runs the reviewed allowance and
  contract readers together, then inventories their source with Line 1's code.
  Its README provides offline and live commands. Line 3 can adopt this pinning
  approach; Line 2 can use its public endpoint override. Neither line was edited.

For Line 4, a saved schedule can be passed directly to `handoff.py snapshot`
along with its input plan, so another worker can verify exactly which plan was
scheduled. Place the resulting manifest outside all snapshotted scopes.

No dependencies or new currency are required. Data hashes are not signatures,
and a correct inventory is not evidence that executable code is safe.
