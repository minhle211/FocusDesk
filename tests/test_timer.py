"""Examples of how the countdown behaves, with no window open."""

import unittest

from focusdesk.timer import BREAK_5, FOCUS_1, FOCUS_25, FocusTimer


class TimerTests(unittest.TestCase):
    def test_tick_does_nothing_while_paused(self):
        timer = FocusTimer(FOCUS_1)
        self.assertFalse(timer.tick())
        self.assertEqual(timer.remaining, 60)

    def test_tick_counts_down_while_running(self):
        timer = FocusTimer(FOCUS_1)
        timer.start()
        self.assertFalse(timer.tick())
        self.assertEqual(timer.remaining, 59)
        self.assertTrue(timer.running)

    def test_tick_reports_only_the_finishing_second(self):
        timer = FocusTimer(FOCUS_1)
        timer.remaining = 1
        timer.start()
        self.assertTrue(timer.tick())
        self.assertEqual(timer.remaining, 0)
        self.assertFalse(timer.running)
        self.assertFalse(timer.tick())

    def test_clock_text_splits_minutes_and_seconds(self):
        timer = FocusTimer(FOCUS_25)
        timer.remaining = 90
        self.assertEqual(timer.clock_text(), "01:30")

    def test_start_from_zero_fills_the_block_again(self):
        timer = FocusTimer(FOCUS_1)
        timer.remaining = 0
        timer.start()
        self.assertEqual(timer.remaining, 60)
        self.assertTrue(timer.running)

    def test_reset_restores_the_full_block(self):
        timer = FocusTimer(FOCUS_25)
        timer.start()
        timer.tick()
        timer.reset()
        self.assertFalse(timer.running)
        self.assertEqual(timer.remaining, 25 * 60)

    def test_cannot_switch_blocks_while_running(self):
        timer = FocusTimer(FOCUS_25)
        timer.start()
        changed = timer.set_preset(BREAK_5)
        self.assertFalse(changed)
        self.assertEqual(timer.kind, "focus")
        self.assertEqual(timer.length, 25 * 60)

    def test_switching_block_uses_the_new_length(self):
        timer = FocusTimer(FOCUS_25)
        timer.start()
        timer.pause()
        changed = timer.set_preset(BREAK_5)
        self.assertTrue(changed)
        self.assertEqual(timer.remaining, 5 * 60)
        self.assertEqual(timer.kind, "break")

    def test_clicking_the_same_block_keeps_a_paused_countdown(self):
        timer = FocusTimer(FOCUS_25)
        timer.start()
        timer.tick()
        timer.pause()
        changed = timer.set_preset(FOCUS_25)
        self.assertTrue(changed)
        self.assertEqual(timer.remaining, 25 * 60 - 1)

    def test_describe_and_button_text(self):
        timer = FocusTimer(FOCUS_25)
        self.assertEqual(timer.describe(), "Ready to focus.")
        self.assertEqual(timer.start_button_text(), "Start")

        timer.start()
        self.assertEqual(timer.describe(), "Focus is running.")
        self.assertEqual(timer.start_button_text(), "Pause")

        timer.tick()
        timer.pause()
        self.assertEqual(timer.describe(), "Paused.")

        timer.remaining = 0
        self.assertEqual(timer.describe(), "Time is up.")

        break_timer = FocusTimer(BREAK_5)
        self.assertEqual(break_timer.describe(), "Ready for a break.")
        break_timer.start()
        self.assertEqual(break_timer.describe(), "Break is running.")


if __name__ == "__main__":
    unittest.main()
