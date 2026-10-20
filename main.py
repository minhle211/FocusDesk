"""Start Focus Desk."""

from pathlib import Path

from focusdesk.window import open_desk


def sharpen_on_windows():
    """Ask Windows to draw this app sharply on high-resolution screens.

    This must run before the window is created. If it is not Windows, or
    Windows refuses the request, the app still opens.
    """
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, ImportError):
        return


def main():
    sharpen_on_windows()
    # Save beside this project, in data/desk.json, not in a hidden system folder.
    app_folder = Path(__file__).resolve().parent
    save_path = app_folder / "data" / "desk.json"
    open_desk(save_path)


if __name__ == "__main__":
    main()
