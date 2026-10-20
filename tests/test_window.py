"""Click through the window without leaving it on screen."""

import tempfile
import unittest
from pathlib import Path
import tkinter as tk

from focusdesk.storage import load_desk
from focusdesk.window import MUTED, DeskWindow


class WindowTests(unittest.TestCase):
    def test_add_finish_and_remove(self):
        root = None
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest("No desktop window: " + str(error))

        root.withdraw()
        folder = tempfile.TemporaryDirectory()
        path = Path(folder.name) / "desk.json"
        window = DeskWindow(root, path)

        try:
            self.assertEqual(window.clock_label.cget("text"), "25:00")
            self.assertEqual(window.timer_message.cget("text"), "Ready to focus.")

            window.add_button.invoke()
            self.assertEqual(window.task_message.cget("text"), "Type a task first.")

            window.task_entry.insert(0, "Read a chapter")
            window.add_button.invoke()
            self.assertEqual(window.task_list.size(), 1)
            self.assertEqual(window.task_list.get(0), "[ ]  Read a chapter")
            self.assertTrue(path.exists())

            window.remove_button.invoke()
            self.assertEqual(window.task_message.cget("text"), "Select a task first.")

            window.task_list.selection_set(0)
            window.done_button.invoke()
            self.assertEqual(window.task_list.get(0), "[x]  Read a chapter")
            self.assertEqual(window.task_list.itemcget(0, "fg"), MUTED)
            self.assertEqual(window.data["tasks"][0]["done"], True)

            window.start_button.invoke()
            self.assertEqual(window.timer_message.cget("text"), "Focus is running.")
            self.assertEqual(window.start_button.cget("text"), "Pause")

            window.button_5.invoke()
            self.assertEqual(
                window.timer_message.cget("text"),
                "Pause the timer before switching.",
            )
            self.assertEqual(window.timer.kind, "focus")

            window.start_button.invoke()
            window.button_1.invoke()
            self.assertEqual(window.clock_label.cget("text"), "01:00")
            self.assertEqual(window.timer_message.cget("text"), "Ready to focus.")

            window.start_button.invoke()
            window.timer.remaining = 1
            window.note_entry.insert(0, "chapter 3")
            # on_tick is what the window calls by itself every second.
            window.on_tick()

            self.assertEqual(window.clock_label.cget("text"), "00:00")
            self.assertEqual(window.timer_message.cget("text"), "Saved 1 minute of focus.")
            self.assertEqual(window.note_entry.get(), "")
            self.assertEqual(len(window.data["sessions"]), 1)
            self.assertEqual(window.data["sessions"][0]["note"], "chapter 3")
            self.assertEqual(window.data["sessions"][0]["kind"], "focus")
            self.assertIn("1 minute of focus", window.summary_label.cget("text"))
            self.assertIn("1 min focus - chapter 3", window.session_label.cget("text"))

            window.task_list.selection_set(0)
            window.remove_button.invoke()
            self.assertEqual(window.task_list.size(), 0)

            window.on_close()
            root = None

            loaded = load_desk(path)
            self.assertEqual(loaded["tasks"], [])
            self.assertEqual(loaded["sessions"][0]["minutes"], 1)
        finally:
            if root is not None:
                root.destroy()
            folder.cleanup()


if __name__ == "__main__":
    unittest.main()
