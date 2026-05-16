from __future__ import annotations

import calendar as calendar_lib
from datetime import date

from schedule_backend.models import CalendarDay, ScheduleEntry


def generate_month_calendar(
    year: int,
    month: int,
    entries: list[ScheduleEntry] | None = None,
    conflict_dates: set[date] | None = None,
) -> list[CalendarDay]:
    entries_by_date: dict[date, list[ScheduleEntry]] = {}
    for entry in entries or []:
        entries_by_date.setdefault(entry.date, []).append(entry)

    conflict_dates = conflict_dates or set()
    _, days_in_month = calendar_lib.monthrange(year, month)
    days: list[CalendarDay] = []

    for day_number in range(1, days_in_month + 1):
        day = date(year, month, day_number)
        day_entries = tuple(
            sorted(
                entries_by_date.get(day, []),
                key=lambda entry: (entry.start_time or "", entry.created_at),
            )
        )
        days.append(
            CalendarDay(
                date=day,
                day_of_week=calendar_lib.day_name[day.weekday()],
                entries=day_entries,
                has_conflicts=day in conflict_dates,
            )
        )

    return days

