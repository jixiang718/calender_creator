from __future__ import annotations

import json
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from schedule_backend.parser import ParseError
from schedule_backend.service import ScheduleService


class ScheduleRequestHandler(BaseHTTPRequestHandler):
    service = ScheduleService()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/health":
            self._send_json({"status": "ok"})
            return

        if parsed_url.path == "/calendar/month":
            params = parse_qs(parsed_url.query)
            try:
                year = int(_first(params, "year"))
                month = int(_first(params, "month"))
                if month < 1 or month > 12:
                    raise ValueError
            except (TypeError, ValueError):
                self._send_json(
                    {"error": "Query parameters 'year' and 'month' are required."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(self.service.get_month(year, month))
            return

        self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/schedule":
            self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            text = payload["text"]
            today = _parse_today(payload.get("today"))
            response = self.service.add_from_natural_language(text, today=today)
        except KeyError:
            self._send_json({"error": "JSON body must include 'text'."}, status=HTTPStatus.BAD_REQUEST)
            return
        except (json.JSONDecodeError, TypeError):
            self._send_json({"error": "Request body must be valid JSON."}, status=HTTPStatus.BAD_REQUEST)
            return
        except (ParseError, ValueError) as error:
            self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json(response, status=HTTPStatus.CREATED)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def _send_json(self, payload: dict[str, object], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ScheduleRequestHandler)
    print(f"Schedule backend listening on http://{host}:{port}")
    server.serve_forever()


def _first(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    if not values:
        return None
    return values[0]


def _parse_today(value: object) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("'today' must be an ISO date string.")
    return date.fromisoformat(value)

