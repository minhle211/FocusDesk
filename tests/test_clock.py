"""Examples of how the clock text is built."""

import unittest
from datetime import datetime

from focusdesk.clock import clock_stamp, day_text, pad


class ClockTests(unittest.TestCase):
    def test_pad_adds_a_zero_under_ten(self):
        self.assertEqual(pad(7), "07")
        self.assertEqual(pad(10), "10")

    def test_day_and_time_text(self):
        moment = datetime(2026, 1, 5, 9, 7)
        self.assertEqual(day_text(moment), "2026-01-05")
        self.assertEqual(clock_stamp(moment), "2026-01-05 09:07")


if __name__ == "__main__":
    unittest.main()
