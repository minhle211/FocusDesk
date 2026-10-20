"""Rules for the task list.

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
