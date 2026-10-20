"""Load and save the desk file.

The file is JSON, which is just labeled text. You can open data/desk.json
in any editor and read the tasks.
"""

import json
from pathlib import Path

from focusdesk.tasks import MAX_TEXT


def empty_desk():
    """Return a new desk with no tasks and no sessions."""
    return {
        "next_id": 1,
        "tasks": [],
        "sessions": [],
    }


def is_whole_number(value):
    """Return True for 0, 1, 2, and so on.

    Python treats True as the number 1. A yes/no value should not be
    accepted as a task id or a minute count, so booleans are rejected.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return False


def clean_task(item, seen_ids):
    """Return a task dictionary, or None if this entry cannot be shown."""
    if not isinstance(item, dict):
        return None

    task_id = item.get("id")
    title = item.get("title")
    if not is_whole_number(task_id) or not isinstance(title, str):
        return None
    if task_id in seen_ids:
        return None

    title = title.strip()
    if title == "":
        return None
    if len(title) > MAX_TEXT:
        title = title[:MAX_TEXT].strip()
    if title == "":
        return None

    seen_ids.append(task_id)

    done = item.get("done", False)
    if not isinstance(done, bool):
        done = False

    done_on = item.get("done_on", "")
    created_on = item.get("created_on", "")
    if not isinstance(done_on, str):
        done_on = ""
    if not isinstance(created_on, str):
        created_on = ""
    if not done:
        done_on = ""

    return {
        "id": task_id,
        "title": title,
        "done": done,
        "done_on": done_on,
        "created_on": created_on,
    }


def clean_session(item):
    """Return a session dictionary, or None if this entry should be skipped."""
    if not isinstance(item, dict):
        return None

    minutes = item.get("minutes")
    kind = item.get("kind")
    note = item.get("note", "")
    finished_at = item.get("finished_at", "")
    finished_on = item.get("finished_on", "")

    if not is_whole_number(minutes) or minutes < 1 or minutes > 180:
        return None
    if kind != "focus" and kind != "break":
        return None
    if not isinstance(note, str):
        return None
    if not isinstance(finished_at, str) or not isinstance(finished_on, str):
        return None
    if finished_on == "":
        return None

    note = note.strip()
    if len(note) > MAX_TEXT:
        note = note[:MAX_TEXT].strip()

    return {
        "minutes": minutes,
        "kind": kind,
        "note": note,
        "finished_at": finished_at,
        "finished_on": finished_on,
    }


def clean_desk(raw):
    """Return a desk dictionary, or raise ValueError if the shape is wrong.

    A single bad task is skipped. A file that is not a desk at all is rejected
    so the caller can move it aside instead of showing nonsense.
    """
    if not isinstance(raw, dict):
        raise ValueError("The desk file is not a JSON object.")

    raw_tasks = raw.get("tasks", [])
    raw_sessions = raw.get("sessions", [])
    if not isinstance(raw_tasks, list) or not isinstance(raw_sessions, list):
        raise ValueError("Tasks and sessions must be lists.")

    data = empty_desk()
    seen_ids = []
    highest_id = 0

    for item in raw_tasks:
        task = clean_task(item, seen_ids)
        if task is None:
            continue
        data["tasks"].append(task)
        if task["id"] > highest_id:
            highest_id = task["id"]

    for item in raw_sessions:
        session = clean_session(item)
        if session is None:
            continue
        data["sessions"].append(session)

    next_id = raw.get("next_id", 1)
    if not is_whole_number(next_id) or next_id <= highest_id:
        next_id = highest_id + 1
    data["next_id"] = next_id
    return data


def move_broken_file(path):
    """Keep an unreadable save beside the original, under a different name."""
    broken_path = path.with_name("desk-broken.txt")
    if broken_path.exists():
        broken_path.unlink()
    path.replace(broken_path)


def load_desk(path):
    """Read the save file. A missing or unreadable file becomes an empty desk."""
    path = Path(path)
    if not path.exists():
        return empty_desk()

    try:
        text = path.read_text(encoding="utf-8")
        raw = json.loads(text)
        return clean_desk(raw)
    except (OSError, json.JSONDecodeError, ValueError):
        try:
            move_broken_file(path)
        except OSError:
            pass
        return empty_desk()


def save_desk(path, data):
    """Write the desk to disk.

    The bytes go to a temporary file first. The real file is replaced only
    after that write finishes, so a crash in the middle cannot leave a
    half-written desk.json.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    text = json.dumps(data, indent=2, ensure_ascii=False)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(text + "\n", encoding="utf-8")
    temporary.replace(path)
