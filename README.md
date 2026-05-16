# Schedule App Backend

This project aims to build the backend for a schedule management application.

The backend will provide the core services, APIs, data handling, and integration layer needed to support calendar-based scheduling workflows.

## Product Goals

- Provide a basic monthly calendar view.
- Show every date in the month together with its day of week.
- Allow users to describe a schedule item in natural language.
- Parse the user's natural-language request into a dated schedule entry.
- Attach the schedule entry to the matching date automatically.
- Detect schedule conflicts when multiple entries overlap.
- Notify the user when a conflict is found.
- Keep conflicting entries visible by stacking them on the same date instead of dropping or replacing either entry.

## Initial Scope

The first backend version should focus on the core calendar and scheduling flow:

1. Generate a monthly calendar with dates and weekdays.
2. Accept natural-language schedule input from a user.
3. Resolve the intended date and schedule details.
4. Store the schedule entry under the resolved date.
5. Detect overlapping entries for the same date and time range.
6. Return conflict information while preserving all conflicting entries.

## Running the Backend

This first implementation uses only the Python standard library.

```bash
python3 run_server.py --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Get a monthly calendar:

```bash
curl "http://127.0.0.1:8000/calendar/month?year=2026&month=5"
```

Add a schedule entry from natural language:

```bash
curl -X POST http://127.0.0.1:8000/schedule \
  -H "Content-Type: application/json" \
  -d '{"text":"2026-05-20 14:00-15:00 backend planning"}'
```

## Development

Run the test suite:

```bash
python3 -m unittest discover -s tests
```
