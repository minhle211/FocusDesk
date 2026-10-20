"""Rules for the task list and the saved focus blocks.

Nothing in this file opens a window or touches a file. Pass in the desk
dictionary, get back the updated desk dictionary.
"""

MAX_TEXT = 80


def add_task(data, title, today):
    """Add a task and return it. Return None if the title is blank."""
    if not isinstance(title, str):
        return None

    clean = title.strip()
    if clean == "":
        return None
    if len(clean) > MAX_TEXT:
        clean = clean[:MAX_TEXT].strip()
    if clean == "":
        return None

    task = {
        "id": data["next_id"],
        "title": clean,
        "done": False,
        "done_on": "",
        "created_on": today,
    }
    data["next_id"] = data["next_id"] + 1
    data["tasks"].append(task)
    return task


def find_task(data, task_id):
    """Return the task with this id, or None."""
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def mark_task_done(data, task_id, done, today):
    """Mark one task done or not done. Return it, or None if the id is missing."""
    task = find_task(data, task_id)
    if task is None:
        return None

    if done:
        task["done"] = True
        task["done_on"] = today
    else:
        task["done"] = False
        task["done_on"] = ""
    return task


def remove_task(data, task_id):
    """Remove one task. Return True if it was in the list."""
    kept = []
    found = False
    for task in data["tasks"]:
        if task["id"] == task_id:
            found = True
        else:
            kept.append(task)
    data["tasks"] = kept
    return found


def ordered_tasks(data):
    """Return open tasks first, then finished ones. Each group keeps its order."""
    open_tasks = []
    done_tasks = []
    for task in data["tasks"]:
        if task["done"]:
            done_tasks.append(task)
        else:
            open_tasks.append(task)
    return open_tasks + done_tasks


def add_session(data, minutes, kind, note, finished_at, finished_on):
    """Remember one finished focus block or break."""
    clean_note = note.strip()
    if len(clean_note) > MAX_TEXT:
        clean_note = clean_note[:MAX_TEXT].strip()

    session = {
        "minutes": minutes,
        "kind": kind,
        "note": clean_note,
        "finished_at": finished_at,
        "finished_on": finished_on,
    }
    data["sessions"].append(session)
    return session


def count_finished_tasks(data, day):
    """Count tasks marked done on this day."""
    total = 0
    for task in data["tasks"]:
        if task["done"] and task["done_on"] == day:
            total = total + 1
    return total


def count_focus_minutes(data, day):
    """Add up finished focus minutes for this day. Breaks are not included."""
    total = 0
    for session in data["sessions"]:
        if session["finished_on"] == day and session["kind"] == "focus":
            total = total + session["minutes"]
    return total


def sessions_on_day(data, day):
    """Return that day's blocks, newest first."""
    found = []
    for session in data["sessions"]:
        if session["finished_on"] == day:
            found.append(session)
    found.reverse()
    return found


def task_line(task):
    """Return the row text for one task."""
    if task["done"]:
        box = "[x]"
    else:
        box = "[ ]"
    return box + "  " + task["title"]


def session_line(session):
    """Return one finished block as a single line."""
    if session["kind"] == "break":
        label = str(session["minutes"]) + " min break"
    else:
        label = str(session["minutes"]) + " min focus"
    if session["note"] == "":
        return label
    return label + " - " + session["note"]


def amount(count, singular, plural):
    """Return '1 task' or '2 tasks'."""
    if count == 1:
        return "1 " + singular
    return str(count) + " " + plural


def summary_text(data, day):
    """Return the footer sentence for this day."""
    task_count = count_finished_tasks(data, day)
    minute_count = count_focus_minutes(data, day)
    tasks = amount(task_count, "task", "tasks")
    minutes = amount(minute_count, "minute", "minutes")
    return "Today: " + tasks + " finished, " + minutes + " of focus"


def finished_today_text(data, day):
    """Return the lines shown under Finished today."""
    sessions = sessions_on_day(data, day)
    if len(sessions) == 0:
        return "No finished blocks yet today."

    lines = []
    shown = 0
    for session in sessions:
        if shown == 6:
            lines.append("Older blocks are still saved.")
            break
        lines.append(session_line(session))
        shown = shown + 1
    return "\n".join(lines)
