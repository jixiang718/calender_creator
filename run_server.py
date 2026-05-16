from __future__ import annotations

import argparse

from schedule_backend.api import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the schedule backend API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

