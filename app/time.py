from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .config import TZ_KEY, YEAR
import os

TZ = ZoneInfo(TZ_KEY)


def now():
    """Return current time in configured TZ.

    If TEST_NOW is set (ISO timestamp), parse and return that time (useful for tests).
    """
    test_now = os.environ.get("TEST_NOW")
    if test_now:
        try:
            # parse ISO format and localize to configured TZ if naive
            dt = datetime.fromisoformat(test_now)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ)
            else:
                dt = dt.astimezone(TZ)
            return dt
        except Exception:
            # fall back to real now on parse error
            pass
    return datetime.now(TZ)

def week_monday(date: datetime) -> datetime:
    date = date.astimezone(TZ)
    return (date - timedelta(days=date.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

def is_sunday(date: datetime) -> bool:
    return date.weekday() == 6

def is_2026_week(date: datetime) -> bool:
    return week_monday(date).year == YEAR

def can_write(date: datetime) -> bool:
    # For safety the default rule is: only allow writes on Sundays in 2026.
    # For local testing you can set environment variable ALLOW_WRITE=1 to bypass
    # the Sunday restriction (do NOT enable in production).
    if os.environ.get("ALLOW_WRITE") == "1":
        return is_2026_week(date)
    return is_sunday(date) and is_2026_week(date)

def all_2026_weeks():
    d = datetime(2026, 1, 1, tzinfo=TZ)
    d = week_monday(d)
    weeks = []
    while d.year <= 2026:
        weeks.append(d)
        d += timedelta(days=7)
    return weeks