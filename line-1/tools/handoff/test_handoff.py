import copy
from pathlib import Path
import tempfile
import unittest
import sys

sys.dont_write_bytecode = True
import handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / "test" / "scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "work").mkdir()
        (self.root / "work" / "a").write_bytes(b"worker deliverable\x00\xff")
        self.manifest = handoff.snapshot(self.root, ["work"])

    def test_roundtrip_deterministic(self):
        self.assertTrue(handoff.verify(self.root, self.manifest)["ok"])
        self.assertEqual(self.manifest, handoff.snapshot(self.root, ["work", "work"]))

    def test_changed_added_missing(self):
        (self.root / "work" / "a").write_bytes(b"modified")
        self.assertEqual(handoff.verify(self.root, self.manifest)["changes"][0]["status"], "changed")
        (self.root / "work" / "a").unlink()
        (self.root / "work" / "b").write_bytes(b"new")
        self.assertEqual([x["status"] for x in handoff.verify(self.root, self.manifest)["changes"]], ["missing", "added"])

    def test_unsafe_paths(self):
        for name in ("../escape", "/etc/passwd", "work/../escape", "work//a", "./work", "", "work\\a"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                handoff.snapshot(self.root, [name])

    def test_symlinks(self):
        (self.root / "work" / "link").symlink_to(self.root / "work" / "a")
        with self.assertRaises(ValueError):
            handoff.snapshot(self.root, ["work"])
        (self.root / "alias").symlink_to(self.root / "work", target_is_directory=True)
        with self.assertRaises(ValueError):
            handoff.snapshot(self.root, ["alias/a"])

    def test_bad_manifest(self):
        bad = copy.deepcopy(self.manifest)
        bad["files"].append(bad["files"][0])
        with self.assertRaises(ValueError):
            handoff.verify(self.root, bad)
        bad = copy.deepcopy(self.manifest)
        bad["files"][0]["sha256"] = "g" * 64
        with self.assertRaises(ValueError):
            handoff.verify(self.root, bad)
        bad["files"][0]["path"] = "../escape"
        with self.assertRaises(ValueError):
            handoff.verify(self.root, bad)


if __name__ == "__main__":
    unittest.main()
