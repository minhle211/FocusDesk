"""Turn the computer clock into the text this app stores.

A day is stored as 2026-10-20.
A moment is stored as 2026-10-20 18:30.
"""

from datetime import datetime


def pad(number):
    """Turn 7 into 07. Leave 10 as 10."""
    if number < 10:
        return "0" + str(number)
    return str(number)


def day_text(moment):
    """Return a date as year-month-day."""
    return str(moment.year) + "-" + pad(moment.month) + "-" + pad(moment.day)


def clock_stamp(moment):
    """Return a date and a time as 2026-10-20 18:30."""
    return day_text(moment) + " " + pad(moment.hour) + ":" + pad(moment.minute)


def today_text():
    """Return today's date from the computer clock."""
    return day_text(datetime.now())


def now_text():
    """Return the current date and time from the computer clock."""
    return clock_stamp(datetime.now())
