# Focus Desk

A small desktop app for the work in front of you. Write down today's tasks, start a timer, and keep the blocks you actually finish.

The list and the timer stay on this computer. The app does not use an account or the internet. Closing the window stops a running clock. Tasks and finished blocks are still there the next time you open it.

## Run it

Double-click `run.bat`, or from this folder:

```
py -3 main.py
```

You need Python 3.9 or newer from [python.org](https://www.python.org/downloads/). Keep the default install options so the window tools (tkinter) are included. There is nothing else to install.

## Use it

1. Type a task and press Enter.
2. Press Start. The button becomes Pause.
3. Pick `25 min`, `50 min`, `5 min break`, or `1 min`. Switching waits until the clock is paused.
4. A block is saved only when the digits reach `00:00`. The `1 min` block is the short one, so you can see a save without waiting.
5. Highlight a task and press `Done / undo`, or double-click it.
6. Close the window. Open the app again. The tasks are still there.

The save file is `data/desk.json`, next to `main.py`. Open it in a text editor if you want to see the raw tasks.

## Check the rules

Double-click `check.bat`, or:

```
py -3 -m unittest discover -s tests -t . -v
```

The tests call the task list, the timer, and the save code directly. One test builds the window, clicks the buttons, and closes it again.

## How the code is split

- `main.py` opens the app and chooses `data/desk.json` as the save file.
- `focusdesk/tasks.py` adds, finishes, removes, and counts tasks and blocks.
- `focusdesk/timer.py` counts down. It does not know about buttons.
- `focusdesk/storage.py` reads and writes the save file.
- `focusdesk/clock.py` turns the computer clock into `2026-10-20` and `2026-10-20 18:30`.
- `focusdesk/window.py` draws the window and calls the files above when you click.
- `tests/` holds short checks that those rules stay true.

A click takes one path. The Add button reads the text box, asks `tasks.py` to add a task, asks `storage.py` to save, then draws the list again. The window does not invent its own rules for what a blank title means. That decision lives in `add_task`.

The clock works the same way. Every second the window calls `timer.tick()`. Most seconds, that only lowers the number. The second the timer hits zero, it returns True, and only then does the window write a finished block.

## Design notes

- Only a finished countdown is saved. Resetting early does not add minutes, so the total means the clock reached zero.
- Breaks are listed under Finished today and are not added to the focus-minute total.
- A running countdown is not written to disk. Reopening the app does not resume a half-finished block.
- The save is written to `desk.tmp` and then renamed to `desk.json`. A crash during the write cannot leave a half-written save in the real file.
- If `desk.json` cannot be read, it is moved to `data/desk-broken.txt` and the app starts from an empty desk.
- `tasks.py` and `timer.py` never import the window, so their tests do not need to click anything.

## Save file

```json
{
  "next_id": 2,
  "tasks": [
    {
      "id": 1,
      "title": "Read a chapter",
      "done": true,
      "done_on": "2026-10-20",
      "created_on": "2026-10-20"
    }
  ],
  "sessions": [
    {
      "minutes": 25,
      "kind": "focus",
      "note": "chapter 3",
      "finished_at": "2026-10-20 18:30",
      "finished_on": "2026-10-20"
    }
  ]
}
```

`next_id` is the number the next new task will get. Finished tasks record the day in `done_on`, so the footer can count what was finished today and ignore an older day.
