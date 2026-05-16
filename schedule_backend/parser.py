from __future__ import annotations

import re
from datetime import date, timedelta

from schedule_backend.models import ParsedScheduleInput


DATE_RE = re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\b")
MONTH_DAY_RE = re.compile(
    r"\b(?P<month>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|sept|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?\b",
    re.IGNORECASE,
)
SLASH_DATE_RE = re.compile(r"\b(?P<month>\d{1,2})/(?P<day>\d{1,2})(?:/(?P<year>\d{2,4}))?\b")
TIME_RANGE_RE = re.compile(
    r"\b(?P<start>\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*(?:-|to|until)\s*"
    r"(?P<end>\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b",
    re.IGNORECASE,
)
AT_TIME_RE = re.compile(r"\b(?:at\s+)?(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm))\b", re.IGNORECASE)
FILLER_RE = re.compile(
    r"\b(?:on|at|from|to|until|schedule|add|create|insert|event|meeting|appointment|for)\b",
    re.IGNORECASE,
)

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


class ParseError(ValueError):
    pass


def parse_schedule_input(text: str, *, today: date | None = None) -> ParsedScheduleInput:
    if not text or not text.strip():
        raise ParseError("Schedule text cannot be empty.")

    today = today or date.today()
    original = text.strip()
    working = original

    entry_date, working = _extract_date(working, today)
    start_time, end_time, working = _extract_time(working)
    title = _clean_title(working)

    if not title:
        title = "Untitled schedule item"

    return ParsedScheduleInput(
        title=title,
        date=entry_date,
        start_time=start_time,
        end_time=end_time,
    )


def _extract_date(text: str, today: date) -> tuple[date, str]:
    lower = text.lower()
    if "day after tomorrow" in lower:
        return today + timedelta(days=2), _remove_phrase(text, "day after tomorrow")
    if "tomorrow" in lower:
        return today + timedelta(days=1), _remove_phrase(text, "tomorrow")
    if "today" in lower:
        return today, _remove_phrase(text, "today")

    match = DATE_RE.search(text)
    if match:
        entry_date = date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
        return entry_date, _remove_match(text, match)

    match = SLASH_DATE_RE.search(text)
    if match:
        year_text = match.group("year")
        year = _normalize_year(year_text, today.year) if year_text else today.year
        entry_date = date(year, int(match.group("month")), int(match.group("day")))
        return entry_date, _remove_match(text, match)

    match = MONTH_DAY_RE.search(text)
    if match:
        month = MONTHS[match.group("month").lower()]
        entry_date = date(today.year, month, int(match.group("day")))
        return entry_date, _remove_match(text, match)

    raise ParseError("Could not find a date in the schedule text.")


def _extract_time(text: str) -> tuple[str | None, str | None, str]:
    match = TIME_RANGE_RE.search(text)
    if match:
        start = _normalize_time(match.group("start"))
        end = _normalize_time(match.group("end"), reference=start)
        return start, end, _remove_match(text, match)

    match = AT_TIME_RE.search(text)
    if match:
        return _normalize_time(match.group("time")), None, _remove_match(text, match)

    return None, None, text


def _normalize_time(value: str, *, reference: str | None = None) -> str:
    value = value.strip().lower().replace(" ", "")
    am_pm = None
    if value.endswith("am") or value.endswith("pm"):
        am_pm = value[-2:]
        value = value[:-2]

    if ":" in value:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    else:
        hour = int(value)
        minute = 0

    if am_pm == "pm" and hour != 12:
        hour += 12
    elif am_pm == "am" and hour == 12:
        hour = 0
    elif am_pm is None and reference and int(reference[:2]) >= 12 and hour < 12:
        hour += 12

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ParseError(f"Invalid time: {value}")

    return f"{hour:02d}:{minute:02d}"


def _normalize_year(value: str, default_year: int) -> int:
    if not value:
        return default_year
    year = int(value)
    if year < 100:
        return 2000 + year
    return year


def _clean_title(text: str) -> str:
    cleaned = FILLER_RE.sub(" ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.;")
    return cleaned


def _remove_phrase(text: str, phrase: str) -> str:
    return re.sub(re.escape(phrase), " ", text, count=1, flags=re.IGNORECASE)


def _remove_match(text: str, match: re.Match[str]) -> str:
    return text[: match.start()] + " " + text[match.end() :]

