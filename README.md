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
