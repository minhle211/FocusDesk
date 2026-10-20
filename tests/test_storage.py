"""Examples of saving the desk and skipping damaged data."""

import json
import tempfile
import unittest
from pathlib import Path

from focusdesk.storage import clean_desk, empty_desk, load_desk, save_desk
from focusdesk.tasks import add_task


class StorageTests(unittest.TestCase):
    def test_missing_file_is_an_empty_desk(self):
        with tempfile.TemporaryDirectory() as folder:
            loaded = load_desk(Path(folder) / "desk.json")
        self.assertEqual(loaded, empty_desk())

    def test_round_trip_keeps_accented_letters(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "desk.json"
            data = empty_desk()
            add_task(data, "Café notes", "2026-10-20")
            save_desk(path, data)

            raw = path.read_text(encoding="utf-8")
            self.assertIn("Café notes", raw)
            self.assertFalse(path.with_suffix(".tmp").exists())

            loaded = load_desk(path)
            self.assertEqual(loaded["tasks"][0]["title"], "Café notes")

    def test_broken_json_is_moved_aside(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "desk.json"
            path.write_text("{ this is not json", encoding="utf-8")
            loaded = load_desk(path)
            self.assertEqual(loaded["tasks"], [])
            self.assertFalse(path.exists())
            self.assertTrue((Path(folder) / "desk-broken.txt").exists())

    def test_a_file_that_is_not_a_desk_is_moved_aside(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "desk.json"
            path.write_text("[1, 2, 3]\n", encoding="utf-8")
            loaded = load_desk(path)
            self.assertEqual(loaded, empty_desk())
            self.assertTrue((Path(folder) / "desk-broken.txt").exists())

    def test_bad_rows_are_skipped_and_the_next_id_is_repaired(self):
        raw = {
            "next_id": 1,
            "tasks": [
                {
                    "id": 5,
                    "title": "  Keep me  ",
                    "done": False,
                    "done_on": "",
                    "created_on": "2026-10-20",
                },
                {"id": True, "title": "Not an id"},
                {"id": 5, "title": "Duplicate"},
                "not a task",
            ],
            "sessions": [
                {
                    "minutes": 25,
                    "kind": "focus",
                    "note": "ok",
                    "finished_at": "2026-10-20 10:00",
                    "finished_on": "2026-10-20",
                },
                {
                    "minutes": 0,
                    "kind": "focus",
                    "note": "",
                    "finished_at": "",
                    "finished_on": "2026-10-20",
                },
                {
                    "minutes": 999,
                    "kind": "focus",
                    "note": "",
                    "finished_at": "",
                    "finished_on": "2026-10-20",
                },
            ],
        }
        data = clean_desk(raw)
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["title"], "Keep me")
        self.assertEqual(data["next_id"], 6)
        self.assertEqual(len(data["sessions"]), 1)
        self.assertEqual(data["sessions"][0]["minutes"], 25)

    def test_save_writes_readable_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "desk.json"
            save_desk(path, empty_desk())
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["next_id"], 1)
            self.assertEqual(raw["tasks"], [])


if __name__ == "__main__":
    unittest.main()
