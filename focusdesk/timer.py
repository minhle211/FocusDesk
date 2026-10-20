"""Count down a focus block or a break.

The timer does not know about buttons or windows. The window asks it,
once a second, whether one second has passed.
"""

from focusdesk.clock import pad


FOCUS_25 = {"label": "25 min", "seconds": 25 * 60, "kind": "focus"}
FOCUS_50 = {"label": "50 min", "seconds": 50 * 60, "kind": "focus"}
BREAK_5 = {"label": "5 min break", "seconds": 5 * 60, "kind": "break"}
FOCUS_1 = {"label": "1 min", "seconds": 60, "kind": "focus"}

PRESETS = [FOCUS_25, FOCUS_50, BREAK_5, FOCUS_1]


class FocusTimer:
    """A countdown you can start, pause, and reset."""

    def __init__(self, preset):
        self.length = preset["seconds"]
        self.kind = preset["kind"]
        self.remaining = preset["seconds"]
        self.running = False

    def start(self):
        """Start, or continue. If the clock is already at 00:00, fill it again."""
        if self.remaining <= 0:
            self.remaining = self.length
        self.running = True

    def pause(self):
        """Stop the countdown without changing the time left."""
        self.running = False

    def reset(self):
        """Stop and return to the full length of the current block."""
        self.running = False
        self.remaining = self.length

    def set_preset(self, preset):
        """Switch block length. Refuse while the clock is running.

        Choosing the block that is already selected does not throw away
        a paused countdown. Choosing a different block starts that block
        from its full length.
        """
        if self.running:
            return False

        same_block = self.length == preset["seconds"] and self.kind == preset["kind"]
        self.length = preset["seconds"]
        self.kind = preset["kind"]
        if not same_block:
            self.remaining = preset["seconds"]
        return True

    def tick(self):
        """Move one second forward. Return True only on the second that hits zero."""
        if not self.running:
            return False
        if self.remaining <= 0:
            self.running = False
            return False

        self.remaining = self.remaining - 1
        if self.remaining == 0:
            self.running = False
            return True
        return False

    def clock_text(self):
        """Return the time left as 25:00."""
        # 90 // 60 is 1 (whole minutes). 90 % 60 is 30 (leftover seconds).
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        return pad(minutes) + ":" + pad(seconds)

    def describe(self):
        """Return a short sentence for the line under the clock."""
        if self.remaining == 0 and not self.running:
            return "Time is up."
        if self.running and self.kind == "break":
            return "Break is running."
        if self.running:
            return "Focus is running."
        if self.remaining != self.length:
            return "Paused."
        if self.kind == "break":
            return "Ready for a break."
        return "Ready to focus."

    def start_button_text(self):
        """Return Pause while the clock is moving, otherwise Start."""
        if self.running:
            return "Pause"
        return "Start"
