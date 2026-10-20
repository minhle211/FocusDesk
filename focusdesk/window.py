"""Draw the Focus Desk window and connect clicks to the other files.

This file does not own the rules. tasks.py changes the list, timer.py
counts down, storage.py writes the save file, and clock.py reads the date.
After each change, the window draws the screen again.
"""

import tkinter as tk

from focusdesk.clock import now_text, today_text
from focusdesk.storage import load_desk, save_desk
from focusdesk.tasks import (
    add_session,
    add_task,
    amount,
    finished_today_text,
    mark_task_done,
    ordered_tasks,
    remove_task,
    summary_text,
    task_line,
)
from focusdesk.timer import BREAK_5, FOCUS_1, FOCUS_25, FOCUS_50, FocusTimer


PAPER = "#f4f1ea"
CARD = "#fffdf8"
INK = "#1c1917"
MUTED = "#57534e"
GREEN = "#166534"
GREEN_DARK = "#14532d"
LINE = "#e7e5e4"
WARNING = "#9f1239"
BUTTON = "#f5f5f4"
BUTTON_ACTIVE = "#e7e5e4"

FONT = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
TITLE_FONT = ("Segoe UI", 22, "bold")
CLOCK_FONT = ("Segoe UI", 30, "bold")
SMALL_FONT = ("Segoe UI", 10)


def make_button(parent, text, command, primary=False, width=None):
    """Create a flat button. primary=True uses the green fill."""
    if primary:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=GREEN,
            fg="white",
            activebackground=GREEN_DARK,
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            font=FONT,
            cursor="hand2",
            borderwidth=0,
        )
    else:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=BUTTON,
            fg=INK,
            activebackground=BUTTON_ACTIVE,
            activeforeground=INK,
            relief="flat",
            padx=12,
            pady=6,
            font=FONT,
            cursor="hand2",
            highlightbackground=LINE,
            highlightthickness=1,
        )
    if width is not None:
        button.config(width=width)
    return button


def make_card(parent):
    """Return the outer border and the inner area of a panel."""
    shell = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=LINE,
        highlightthickness=1,
    )
    inner = tk.Frame(shell, bg=CARD)
    inner.pack(fill="both", expand=True, padx=14, pady=14)
    return shell, inner


def center_window(root, width, height):
    """Place the window in the middle of the screen."""
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    root.geometry(str(width) + "x" + str(height) + "+" + str(x) + "+" + str(y))


class DeskWindow:
    """The window the person actually uses."""

    def __init__(self, root, save_path):
        self.root = root
        self.save_path = save_path
        self.data = load_desk(save_path)
        self.timer = FocusTimer(FOCUS_25)
        self.visible_tasks = []
        self.tick_id = None

        root.title("Focus Desk")
        root.configure(bg=PAPER)

        self.build()
        self.draw_tasks()
        self.draw_clock()
        self.show_timer_state()
        self.paint_presets()
        self.draw_sessions()
        self.draw_summary()
        self.schedule_tick()
        self.task_entry.focus_set()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build(self):
        """Create every widget. Text is filled in afterwards."""
        outer = tk.Frame(self.root, bg=PAPER)
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        title = tk.Label(
            outer,
            text="Focus Desk",
            bg=PAPER,
            fg=INK,
            font=TITLE_FONT,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            outer,
            text="A task list and a timer for the work in front of you.",
            bg=PAPER,
            fg=MUTED,
            font=FONT,
        )
        subtitle.pack(anchor="w", pady=(2, 14))

        body = tk.Frame(outer, bg=PAPER)
        body.columnconfigure(0, weight=3, minsize=420)
        body.columnconfigure(1, weight=2, minsize=340)
        body.rowconfigure(0, weight=1)

        left_shell, left = make_card(body)
        left_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right_shell, right = make_card(body)
        right_shell.grid(row=0, column=1, sticky="nsew")

        self.build_tasks(left)
        self.build_timer(right)

        # Pack the footer before the expanding middle, so the summary
        # stays on screen when the window is short.
        footer = tk.Frame(outer, bg=PAPER)
        footer.pack(side="bottom", fill="x", pady=(12, 0))
        body.pack(fill="both", expand=True)

        self.summary_label = tk.Label(
            footer,
            text="",
            bg=PAPER,
            fg=INK,
            font=FONT_BOLD,
            anchor="w",
        )
        self.summary_label.pack(anchor="w")

        finished_heading = tk.Label(
            footer,
            text="Finished today",
            bg=PAPER,
            fg=INK,
            font=FONT_BOLD,
            anchor="w",
        )
        finished_heading.pack(anchor="w", pady=(8, 2))

        self.session_label = tk.Label(
            footer,
            text="",
            bg=PAPER,
            fg=INK,
            font=FONT,
            justify="left",
            anchor="w",
            wraplength=860,
        )
        self.session_label.pack(anchor="w", fill="x")

    def build_tasks(self, parent):
        """The left panel: type a task, then mark it done or remove it."""
        heading = tk.Label(
            parent,
            text="On your desk",
            bg=CARD,
            fg=INK,
            font=FONT_BOLD,
        )
        heading.pack(anchor="w")

        entry_row = tk.Frame(parent, bg=CARD)
        entry_row.pack(fill="x", pady=(10, 4))

        self.task_entry = tk.Entry(
            entry_row,
            font=FONT,
            bg="white",
            fg=INK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=GREEN,
            insertbackground=INK,
        )
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)
        self.task_entry.bind("<Return>", self.on_add)

        self.add_button = make_button(entry_row, "Add", self.on_add, primary=True)
        self.add_button.pack(side="left", padx=(8, 0))

        self.task_message = tk.Label(
            parent,
            text="",
            bg=CARD,
            fg=MUTED,
            font=SMALL_FONT,
            anchor="w",
            justify="left",
        )
        self.task_message.pack(anchor="w", fill="x")

        list_frame = tk.Frame(parent, bg=CARD)
        list_frame.pack(fill="both", expand=True, pady=(6, 8))

        self.task_list = tk.Listbox(
            list_frame,
            height=9,
            font=FONT,
            bg="white",
            fg=INK,
            selectbackground=GREEN,
            selectforeground="white",
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=GREEN,
            relief="flat",
            activestyle="none",
            exportselection=False,
        )
        scroll = tk.Scrollbar(list_frame, command=self.task_list.yview)
        self.task_list.config(yscrollcommand=scroll.set)
        self.task_list.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.task_list.bind("<Double-Button-1>", self.on_toggle_selected)

        buttons = tk.Frame(parent, bg=CARD)
        buttons.pack(anchor="w")
        self.done_button = make_button(buttons, "Done / undo", self.on_toggle_selected)
        self.done_button.pack(side="left")
        self.remove_button = make_button(buttons, "Remove", self.on_remove_selected)
        self.remove_button.pack(side="left", padx=(8, 0))

    def build_timer(self, parent):
        """The right panel: the countdown and a note for this block."""
        heading = tk.Label(
            parent,
            text="Timer",
            bg=CARD,
            fg=INK,
            font=FONT_BOLD,
        )
        heading.pack(anchor="w")

        self.clock_label = tk.Label(
            parent,
            text="25:00",
            bg=CARD,
            fg=GREEN,
            font=CLOCK_FONT,
        )
        self.clock_label.pack(anchor="w", pady=(8, 0))

        self.timer_message = tk.Label(
            parent,
            text="",
            bg=CARD,
            fg=MUTED,
            font=FONT,
            anchor="w",
            justify="left",
        )
        self.timer_message.pack(anchor="w", pady=(2, 8))

        controls = tk.Frame(parent, bg=CARD)
        controls.pack(anchor="w")
        self.start_button = make_button(
            controls,
            "Start",
            self.on_start_or_pause,
            primary=True,
            width=10,
        )
        self.start_button.pack(side="left")
        self.reset_button = make_button(
            controls,
            "Reset",
            self.on_reset,
            width=10,
        )
        self.reset_button.pack(side="left", padx=(8, 0))

        row_one = tk.Frame(parent, bg=CARD)
        row_one.pack(anchor="w", pady=(12, 4))
        row_two = tk.Frame(parent, bg=CARD)
        row_two.pack(anchor="w")

        self.button_25 = make_button(row_one, FOCUS_25["label"], self.on_choose_25, width=12)
        self.button_50 = make_button(row_one, FOCUS_50["label"], self.on_choose_50, width=12)
        self.button_5 = make_button(row_two, BREAK_5["label"], self.on_choose_5, width=12)
        self.button_1 = make_button(row_two, FOCUS_1["label"], self.on_choose_1, width=12)
        self.button_25.pack(side="left")
        self.button_50.pack(side="left", padx=(8, 0))
        self.button_5.pack(side="left")
        self.button_1.pack(side="left", padx=(8, 0))

        self.preset_buttons = [
            (self.button_25, FOCUS_25),
            (self.button_50, FOCUS_50),
            (self.button_5, BREAK_5),
            (self.button_1, FOCUS_1),
        ]

        note_label = tk.Label(
            parent,
            text="Note for this block",
            bg=CARD,
            fg=INK,
            font=FONT,
        )
        note_label.pack(anchor="w", pady=(14, 4))

        self.note_entry = tk.Entry(
            parent,
            font=FONT,
            bg="white",
            fg=INK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=GREEN,
            insertbackground=INK,
        )
        self.note_entry.pack(fill="x", ipady=6, ipadx=6)

        rule = tk.Label(
            parent,
            text="Saved when the clock reaches 00:00. Closing the window stops the clock.",
            bg=CARD,
            fg=MUTED,
            font=SMALL_FONT,
            justify="left",
            anchor="w",
            wraplength=320,
        )
        rule.pack(anchor="w", pady=(8, 0))

    def schedule_tick(self):
        """Ask the window to call on_tick again after one second."""
        self.cancel_tick()
        self.tick_id = self.root.after(1000, self.on_tick)

    def cancel_tick(self):
        """Drop a waiting tick, if there is one."""
        tick_id = self.tick_id
        self.tick_id = None
        if tick_id is None:
            return
        try:
            self.root.after_cancel(tick_id)
        except tk.TclError:
            return

    def on_tick(self):
        """One second passed. Move the timer, and schedule the next second."""
        # This callback is already running, so forget its id before canceling
        # any other tick that might still be waiting.
        waiting = self.tick_id
        self.tick_id = None
        if waiting is not None:
            try:
                self.root.after_cancel(waiting)
            except tk.TclError:
                pass

        finished = self.timer.tick()
        if finished:
            self.remember_finished_block()
        self.draw_clock()
        self.schedule_tick()

    def save(self):
        """Write the tasks and sessions to disk. Return True if that worked."""
        try:
            save_desk(self.save_path, self.data)
        except OSError:
            return False
        return True

    def selected_task(self):
        """Return the highlighted task, or None if the list has no highlight."""
        picked = self.task_list.curselection()
        if len(picked) == 0:
            return None
        index = picked[0]
        if index < 0 or index >= len(self.visible_tasks):
            return None
        return self.visible_tasks[index]

    def on_add(self, event=None):
        """Add the text in the box. Enter passes event; the Add button does not."""
        typed = self.task_entry.get()
        task = add_task(self.data, typed, today_text())
        if task is None:
            self.show_task_error("Type a task first.")
            return "break"

        self.task_entry.delete(0, "end")
        saved = self.save()
        self.draw_tasks()
        self.draw_summary()
        if not saved:
            self.show_task_error("Could not save the file.")
        elif len(typed.strip()) > len(task["title"]):
            self.show_task_error("I kept the first 80 characters.")
        return "break"

    def on_toggle_selected(self, event=None):
        """Mark the highlighted task done, or undo that if it is already done."""
        task = self.selected_task()
        if task is None:
            self.show_task_error("Select a task first.")
            return

        if task["done"]:
            mark_task_done(self.data, task["id"], False, today_text())
        else:
            mark_task_done(self.data, task["id"], True, today_text())

        saved = self.save()
        self.draw_tasks(keep_id=task["id"])
        self.draw_summary()
        if not saved:
            self.show_task_error("Could not save the file.")

    def on_remove_selected(self):
        """Remove the highlighted task."""
        task = self.selected_task()
        if task is None:
            self.show_task_error("Select a task first.")
            return

        remove_task(self.data, task["id"])
        saved = self.save()
        self.draw_tasks()
        self.draw_summary()
        if not saved:
            self.show_task_error("Could not save the file.")

    def on_start_or_pause(self):
        """Start the clock, or pause it if it is already running."""
        if self.timer.running:
            self.timer.pause()
        else:
            self.timer.start()
        self.draw_clock()
        self.show_timer_state()

    def on_reset(self):
        """Put the current block back to its full length and stop it."""
        self.timer.reset()
        self.draw_clock()
        self.show_timer_state()

    def on_choose_25(self):
        self.choose_preset(FOCUS_25)

    def on_choose_50(self):
        self.choose_preset(FOCUS_50)

    def on_choose_5(self):
        self.choose_preset(BREAK_5)

    def on_choose_1(self):
        self.choose_preset(FOCUS_1)

    def choose_preset(self, preset):
        """Switch to another block length when the clock is not running."""
        changed = self.timer.set_preset(preset)
        if not changed:
            self.show_timer_error("Pause the timer before switching.")
            return
        self.draw_clock()
        self.paint_presets()
        self.show_timer_state()

    def remember_finished_block(self):
        """Save the block that just hit 00:00 and tell the person."""
        # length is stored in seconds. 60 seconds is one minute.
        minutes = self.timer.length // 60
        note = self.note_entry.get()
        add_session(
            self.data,
            minutes,
            self.timer.kind,
            note,
            now_text(),
            today_text(),
        )
        self.note_entry.delete(0, "end")
        saved = self.save()
        self.chime()
        self.draw_sessions()
        self.draw_summary()

        if not saved:
            self.show_timer_error("Could not save the file.")
            return
        if self.timer.kind == "break":
            self.show_timer_success("Break is over.")
            return
        saved_text = "Saved " + amount(minutes, "minute", "minutes") + " of focus."
        self.show_timer_success(saved_text)

    def on_close(self):
        """Save one last time, then close the window."""
        self.cancel_tick()
        self.save()
        self.root.destroy()

    def chime(self):
        """Beep when a block finishes. Hidden test windows stay quiet."""
        if self.root.state() == "withdrawn":
            return
        self.root.bell()

    def show_task_error(self, text):
        self.task_message.config(text=text, fg=WARNING)

    def show_timer_error(self, text):
        self.timer_message.config(text=text, fg=WARNING)

    def show_timer_success(self, text):
        self.timer_message.config(text=text, fg=GREEN)

    def show_timer_state(self):
        """Show Ready, Running, Paused, or Time is up under the clock."""
        text = self.timer.describe()
        if self.timer.running or self.timer.remaining == 0:
            color = GREEN
        else:
            color = MUTED
        self.timer_message.config(text=text, fg=color)

    def draw_tasks(self, keep_id=None):
        """Draw the task list again from the saved tasks."""
        self.visible_tasks = ordered_tasks(self.data)
        self.task_list.delete(0, "end")

        select_at = None
        index = 0
        for task in self.visible_tasks:
            self.task_list.insert("end", task_line(task))
            if task["done"]:
                # "end" is the row that was just inserted.
                self.task_list.itemconfig("end", fg=MUTED)
            if keep_id is not None and task["id"] == keep_id:
                select_at = index
            index = index + 1

        if select_at is not None:
            self.task_list.selection_set(select_at)
            self.task_list.activate(select_at)
            self.task_list.see(select_at)

        if len(self.visible_tasks) == 0:
            hint = "Type a task and press Enter."
        else:
            hint = "Double-click a task to mark it done."
        self.task_message.config(text=hint, fg=MUTED)

    def draw_clock(self):
        """Update the digits and the Start/Pause label."""
        self.clock_label.config(text=self.timer.clock_text())
        self.start_button.config(text=self.timer.start_button_text())

    def paint_presets(self):
        """Color the button for the block that is currently selected."""
        for button, preset in self.preset_buttons:
            selected = (
                preset["seconds"] == self.timer.length
                and preset["kind"] == self.timer.kind
            )
            if selected:
                button.config(
                    bg=GREEN,
                    fg="white",
                    activebackground=GREEN_DARK,
                    activeforeground="white",
                )
            else:
                button.config(
                    bg=BUTTON,
                    fg=INK,
                    activebackground=BUTTON_ACTIVE,
                    activeforeground=INK,
                )

    def draw_sessions(self):
        text = finished_today_text(self.data, today_text())
        self.session_label.config(text=text)

    def draw_summary(self):
        text = summary_text(self.data, today_text())
        self.summary_label.config(text=text)


def open_desk(save_path):
    """Create the window and wait for clicks until it is closed."""
    root = tk.Tk()
    DeskWindow(root, save_path)
    root.update_idletasks()
    needed_w = root.winfo_reqwidth()
    needed_h = root.winfo_reqheight()
    # Do not let the window shrink smaller than its contents.
    root.minsize(needed_w, needed_h)
    width = max(needed_w, 980)
    height = max(needed_h, 700)
    center_window(root, width, height)
    root.mainloop()
