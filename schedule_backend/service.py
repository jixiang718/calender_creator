from __future__ import annotations

from datetime import date
from typing import Any

from schedule_backend.calendar import generate_month_calendar
from schedule_backend.models import ScheduleEntry
from schedule_backend.parser import parse_schedule_input
from schedule_backend.store import ScheduleStore


class ScheduleService:
    def __init__(self, store: ScheduleStore | None = None) -> None:
        self.store = store or ScheduleStore()

    def get_month(self, year: int, month: int) -> dict[str, Any]:
        entries = self.store.list_entries(year=year, month=month)
        days = generate_month_calendar(
            year,
            month,
            entries=entries,
            conflict_dates=self.store.conflict_dates(),
        )
        return {
            "year": year,
            "month": month,
            "days": [day.to_dict() for day in days],
        }

    def add_from_natural_language(self, text: str, *, today: date | None = None) -> dict[str, Any]:
        parsed = parse_schedule_input(text, today=today)
        entry = ScheduleEntry.create(
            title=parsed.title,
            entry_date=parsed.date,
            start_time=parsed.start_time,
            end_time=parsed.end_time,
            source_text=text,
        )

        conflicts = self.store.find_conflicts(entry)
        self.store.add(entry)

        return {
            "entry": entry.to_dict(),
            "conflicts": [conflict.to_dict() for conflict in conflicts],
            "has_conflict": bool(conflicts),
            "message": _build_message(entry, conflicts),
        }


def _build_message(entry: ScheduleEntry, conflicts: list[ScheduleEntry]) -> str:
    if not conflicts:
        return f"Added '{entry.title}' to {entry.date.isoformat()}."
    return (
        f"Added '{entry.title}' to {entry.date.isoformat()} and found "
        f"{len(conflicts)} conflict(s). Conflicting entries are stacked on the same date."
    )

