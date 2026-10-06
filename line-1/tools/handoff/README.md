# Handoff inventory

A Python standard-library tool that snapshots relative file paths, byte counts and
SHA-256 digests, then checks a later copy. Directory scopes also detect new files.
It works offline and reads only paths within the current working directory.
It never reads environment variables, uses a wallet, or sends anything.

From the repository root, see it verify this delivered tool:

```sh
python3 line-1/tools/handoff/handoff.py verify artifacts/line-1/handoff.json
```

Create a handoff for your own work with `python3 line-1/tools/handoff/handoff.py
snapshot path/to/deliverables`. Redirect stdout to a manifest **outside the
snapshotted directories**, then transfer both. Run verification from the receiving
workspace root. Do not put secrets in a scope. The tool intentionally does not
skip hidden files. Empty directories and metadata such as permissions are not
recorded. Missing scope roots fail verification as an error.

Exit codes: 0 success, 1 inventory differs, 2 invalid input or read failure.
Absolute paths, dot components, parent traversal and symlinks are rejected.
Operate on a quiet workspace: this is not protection against another process
swapping files during reads. Hashes detect differences, not authorship or safe
code; review code before running it. An attacker who replaces both manifest and
files can produce a matching pair. No dependencies or network needed.

Local trial: generated an inventory of the real tool directory and verified it.
Tests exercise edits, additions, deletions, duplicate entries, traversal and
symlink rejection, malformed digests and deterministic output. Run them with
`python3 line-1/tools/handoff/test_handoff.py`; temporary fixtures stay under
`test/scratch/` and are removed afterwards.

Next useful steps: document a receiving worker's entry point and prerequisites,
then validate that handoff metadata without executing the received code.
