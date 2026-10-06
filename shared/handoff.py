#!/usr/bin/env python3
"""Portable file inventory. Standard library only; all paths relative to cwd."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

SCHEMA = "swarm-handoff/v1"


def safe_path(root, name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("path must be a nonempty POSIX relative path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
        raise ValueError("unsafe path: " + name)
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink refused: " + name)
    return current


def inventory(root, scopes):
    if not isinstance(scopes, list) or not scopes:
        raise ValueError("at least one scope required")
    files = {}

    def visit(name):
        p = safe_path(root, name)
        if p.is_dir():
            for child in sorted(p.iterdir()):
                visit(child.relative_to(root).as_posix())
        elif p.is_file():
            digest = hashlib.sha256()
            size = 0
            with p.open("rb") as stream:
                for chunk in iter(lambda: stream.read(65536), b""):
                    size += len(chunk)
                    digest.update(chunk)
            files[name] = {"path": name, "bytes": size, "sha256": digest.hexdigest()}
        else:
            raise ValueError("missing or non-regular path: " + name)

    for name in scopes:
        visit(name)
    return [files[name] for name in sorted(files)]


def snapshot(root, scopes):
    # Validate before sorting so malformed input has a controlled error.
    for name in scopes:
        safe_path(root, name)
    scopes = sorted(set(scopes))
    return {"schema": SCHEMA, "scopes": scopes, "files": inventory(root, scopes)}


def verify(root, manifest):
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "scopes", "files"}:
        raise ValueError("invalid manifest fields")
    if manifest["schema"] != SCHEMA or not isinstance(manifest["files"], list):
        raise ValueError("unsupported manifest schema")
    expected = {}
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "bytes", "sha256"}:
            raise ValueError("invalid file entry")
        name = entry["path"]
        safe_path(root, name)
        digest = entry["sha256"]
        if (type(entry["bytes"]) is not int or entry["bytes"] < 0
                or not isinstance(digest, str) or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError("invalid size or digest")
        if name in expected:
            raise ValueError("duplicate file: " + name)
        expected[name] = entry
    actual = {x["path"]: x for x in inventory(root, manifest["scopes"])}
    changes = []
    for name in sorted(expected.keys() | actual.keys()):
        if name not in actual:
            changes.append({"path": name, "status": "missing"})
        elif name not in expected:
            changes.append({"path": name, "status": "added"})
        elif expected[name] != actual[name]:
            changes.append({"path": name, "status": "changed"})
    return {"ok": not changes, "checked_files": len(actual), "changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot").add_argument("paths", nargs="+")
    sub.add_parser("verify").add_argument("manifest")
    args = parser.parse_args()
    root = Path.cwd()
    try:
        if args.command == "snapshot":
            result = snapshot(root, args.paths)
        else:
            path = safe_path(root, args.manifest)
            with path.open("rb") as stream:
                data = stream.read(4 * 1024 * 1024 + 1)
            if len(data) > 4 * 1024 * 1024:
                raise ValueError("manifest exceeds 4 MiB")
            result = verify(root, json.loads(data))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
