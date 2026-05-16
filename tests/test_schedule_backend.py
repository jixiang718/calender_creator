from __future__ import annotations

import unittest
from datetime import date

from schedule_backend.calendar import generate_month_calendar
from schedule_backend.parser import parse_schedule_input
from schedule_backend.service import ScheduleService


class ScheduleBackendTests(unittest.TestCase):
    def test_generate_month_calendar_includes_weekdays(self) -> None:
        days = generate_month_calendar(2026, 5)

        self.assertEqual(len(days), 31)
        self.assertEqual(days[0].date, date(2026, 5, 1))
        self.assertEqual(days[0].day_of_week, "Friday")
        self.assertEqual(days[-1].date, date(2026, 5, 31))
        self.assertEqual(days[-1].day_of_week, "Sunday")

    def test_parse_iso_date_and_time_range(self) -> None:
        parsed = parse_schedule_input("2026-05-20 14:00-15:00 backend planning")

        self.assertEqual(parsed.date, date(2026, 5, 20))
        self.assertEqual(parsed.start_time, "14:00")
        self.assertEqual(parsed.end_time, "15:00")
        self.assertEqual(parsed.title, "backend planning")

    def test_parse_relative_date_and_am_pm_time(self) -> None:
        parsed = parse_schedule_input("tomorrow at 9am daily review", today=date(2026, 5, 16))

        self.assertEqual(parsed.date, date(2026, 5, 17))
        self.assertEqual(parsed.start_time, "09:00")
        self.assertIsNone(parsed.end_time)
        self.assertEqual(parsed.title, "daily review")

    def test_add_entry_reports_conflicts_but_keeps_both_entries(self) -> None:
        service = ScheduleService()

        first = service.add_from_natural_language("2026-05-20 14:00-15:00 backend planning")
        second = service.add_from_natural_language("2026-05-20 14:30-16:00 design review")
        month = service.get_month(2026, 5)

        may_20 = next(day for day in month["days"] if day["date"] == "2026-05-20")
        titles = [entry["title"] for entry in may_20["entries"]]

        self.assertFalse(first["has_conflict"])
        self.assertTrue(second["has_conflict"])
        self.assertEqual(len(second["conflicts"]), 1)
        self.assertEqual(titles, ["backend planning", "design review"])
        self.assertTrue(may_20["has_conflicts"])

    def test_adjacent_time_ranges_do_not_conflict(self) -> None:
        service = ScheduleService()

        service.add_from_natural_language("2026-05-20 14:00-15:00 backend planning")
        second = service.add_from_natural_language("2026-05-20 15:00-16:00 design review")

        self.assertFalse(second["has_conflict"])
        self.assertEqual(second["conflicts"], [])


if __name__ == "__main__":
    unittest.main()
