from __future__ import annotations

from datetime import date

from schedule_backend.models import ScheduleEntry


class ScheduleStore:
    def __init__(self) -> None:
        self._entries: list[ScheduleEntry] = []

    def add(self, entry: ScheduleEntry) -> None:
        self._entries.append(entry)

    def list_entries(self, *, year: int | None = None, month: int | None = None) -> list[ScheduleEntry]:
        entries = self._entries
        if year is not None:
            entries = [entry for entry in entries if entry.date.year == year]
        if month is not None:
            entries = [entry for entry in entries if entry.date.month == month]
        return sorted(entries, key=lambda entry: (entry.date, entry.start_time or "", entry.created_at))

    def entries_on(self, entry_date: date) -> list[ScheduleEntry]:
        return [entry for entry in self._entries if entry.date == entry_date]

    def conflict_dates(self) -> set[date]:
        conflicts: set[date] = set()
        for entry in self._entries:
            if self.find_conflicts(entry):
                conflicts.add(entry.date)
        return conflicts

    def find_conflicts(self, candidate: ScheduleEntry) -> list[ScheduleEntry]:
        if candidate.start_time is None:
            return []

        conflicts: list[ScheduleEntry] = []
        for entry in self.entries_on(candidate.date):
            if entry.id == candidate.id or entry.start_time is None:
                continue
            if _entries_overlap(candidate, entry):
                conflicts.append(entry)

        return sorted(conflicts, key=lambda entry: (entry.start_time or "", entry.created_at))


def _entries_overlap(first: ScheduleEntry, second: ScheduleEntry) -> bool:
    first_start = first.start_time
    second_start = second.start_time
    if first_start is None or second_start is None:
        return False

    first_end = first.end_time
    second_end = second.end_time

    if first_end is None and second_end is None:
        return first_start == second_start
    if first_end is None:
        return second_start <= first_start < second_end
    if second_end is None:
        return first_start <= second_start < first_end

    return first_start < second_end and second_start < first_end
