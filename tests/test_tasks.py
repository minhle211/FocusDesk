"""Examples of the task-list rules, with no window open."""

import unittest

from focusdesk.storage import empty_desk
from focusdesk.tasks import (
    add_session,
    add_task,
    count_finished_tasks,
    count_focus_minutes,
    finished_today_text,
    mark_task_done,
    ordered_tasks,
    remove_task,
    session_line,
    summary_text,
    task_line,
)


class TaskTests(unittest.TestCase):
    def test_blank_title_is_refused(self):
        data = empty_desk()
        self.assertIsNone(add_task(data, "   ", "2026-10-20"))
        self.assertEqual(data["tasks"], [])
        self.assertEqual(data["next_id"], 1)

    def test_add_trims_spaces_and_gives_the_next_id(self):
        data = empty_desk()
        first = add_task(data, "  Read a chapter  ", "2026-10-20")
        second = add_task(data, "Practice", "2026-10-20")
        self.assertEqual(first["id"], 1)
        self.assertEqual(first["title"], "Read a chapter")
        self.assertEqual(second["id"], 2)
        self.assertEqual(data["next_id"], 3)

    def test_long_title_keeps_the_first_80_characters(self):
        data = empty_desk()
        task = add_task(data, "a" * 100, "2026-10-20")
        self.assertEqual(len(task["title"]), 80)

    def test_done_stores_the_day_and_undo_clears_it(self):
        data = empty_desk()
        add_task(data, "Read a chapter", "2026-10-20")
        mark_task_done(data, 1, True, "2026-10-20")
        self.assertTrue(data["tasks"][0]["done"])
        self.assertEqual(data["tasks"][0]["done_on"], "2026-10-20")

        mark_task_done(data, 1, False, "2026-10-20")
        self.assertFalse(data["tasks"][0]["done"])
        self.assertEqual(data["tasks"][0]["done_on"], "")

    def test_missing_task_is_left_alone(self):
        data = empty_desk()
        self.assertIsNone(mark_task_done(data, 9, True, "2026-10-20"))
        self.assertFalse(remove_task(data, 9))

    def test_remove_keeps_the_other_tasks(self):
        data = empty_desk()
        add_task(data, "Keep", "2026-10-20")
        add_task(data, "Drop", "2026-10-20")
        self.assertTrue(remove_task(data, 2))
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["title"], "Keep")

    def test_open_tasks_stay_above_finished_ones(self):
        data = empty_desk()
        add_task(data, "First", "2026-10-20")
        add_task(data, "Second", "2026-10-20")
        add_task(data, "Third", "2026-10-20")
        mark_task_done(data, 1, True, "2026-10-20")
        titles = []
        for task in ordered_tasks(data):
            titles.append(task["title"])
        self.assertEqual(titles, ["Second", "Third", "First"])

    def test_counts_ignore_other_days_and_breaks(self):
        data = empty_desk()
        add_task(data, "Write", "2026-10-20")
        mark_task_done(data, 1, True, "2026-10-20")
        add_task(data, "Yesterday", "2026-10-19")
        mark_task_done(data, 2, True, "2026-10-19")
        add_session(data, 25, "focus", "chapter", "2026-10-20 10:00", "2026-10-20")
        add_session(data, 5, "break", "", "2026-10-20 10:05", "2026-10-20")
        add_session(data, 50, "focus", "", "2026-10-19 09:00", "2026-10-19")

        self.assertEqual(count_finished_tasks(data, "2026-10-20"), 1)
        self.assertEqual(count_focus_minutes(data, "2026-10-20"), 25)
        self.assertEqual(
            summary_text(data, "2026-10-20"),
            "Today: 1 task finished, 25 minutes of focus",
        )

    def test_summary_uses_plurals_for_zero(self):
        data = empty_desk()
        self.assertEqual(
            summary_text(data, "2026-10-20"),
            "Today: 0 tasks finished, 0 minutes of focus",
        )

    def test_lines_and_the_today_list(self):
        data = empty_desk()
        task = add_task(data, "Read a chapter", "2026-10-20")
        self.assertEqual(task_line(task), "[ ]  Read a chapter")
        mark_task_done(data, task["id"], True, "2026-10-20")
        self.assertEqual(task_line(task), "[x]  Read a chapter")

        early = add_session(data, 25, "focus", "chapter", "2026-10-20 10:00", "2026-10-20")
        later = add_session(data, 5, "break", "", "2026-10-20 10:05", "2026-10-20")
        self.assertEqual(session_line(early), "25 min focus - chapter")
        self.assertEqual(session_line(later), "5 min break")

        number = 0
        while number < 5:
            add_session(data, 1, "focus", "", "2026-10-20 11:00", "2026-10-20")
            number = number + 1

        text = finished_today_text(data, "2026-10-20")
        self.assertTrue(text.startswith("1 min focus"))
        self.assertIn("Older blocks are still saved.", text)
        self.assertNotIn("25 min focus - chapter", text)


if __name__ == "__main__":
    unittest.main()
