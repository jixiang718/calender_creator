from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ScheduleEntry:
    id: str
    title: str
    date: date
    start_time: str | None = None
    end_time: str | None = None
    source_text: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        title: str,
        entry_date: date,
        start_time: str | None = None,
        end_time: str | None = None,
        source_text: str = "",
    ) -> "ScheduleEntry":
        return cls(
            id=str(uuid4()),
            title=title.strip(),
            date=entry_date,
            start_time=start_time,
            end_time=end_time,
            source_text=source_text,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.isoformat(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "source_text": self.source_text,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
        }


@dataclass(frozen=True)
class CalendarDay:
    date: date
    day_of_week: str
    entries: tuple[ScheduleEntry, ...] = ()
    has_conflicts: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "day_of_week": self.day_of_week,
            "entries": [entry.to_dict() for entry in self.entries],
            "has_conflicts": self.has_conflicts,
        }


@dataclass(frozen=True)
class ParsedScheduleInput:
    title: str
    date: date
    start_time: str | None = None
    end_time: str | None = None
