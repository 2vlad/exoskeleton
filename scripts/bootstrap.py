"""Auto-detect user identity from $USER + Staff API.

Usage:
    python3 scripts/bootstrap.py
    python3 scripts/bootstrap.py --login custom_login

Reads arc token from ~/.arc/token, queries Staff API,
prints JSON with user info. Exit code 0 = success.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

STAFF_API = "https://staff-api.yandex-team.ru/v3/persons"
STAFF_FIELDS = "login,name,department_group.name,official.position"
ARC_TOKEN_PATH = Path.home() / ".arc" / "token"


def get_arc_token() -> str | None:
    if ARC_TOKEN_PATH.exists():
        return ARC_TOKEN_PATH.read_text().strip()
    return None


def fetch_staff(login: str, token: str) -> dict | None:
    url = f"{STAFF_API}?login={login}&_fields={STAFF_FIELDS}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Staff API error: {e}", file=sys.stderr)
        return None

    if not data.get("result"):
        return None

    person = data["result"][0]
    name = person.get("name", {})
    first = name.get("first", {}).get("ru") or name.get("first", {}).get("en", "")
    last = name.get("last", {}).get("ru") or name.get("last", {}).get("en", "")
    position = person.get("official", {}).get("position", {}).get("ru", "")
    department = person.get("department_group", {}).get("name", "")

    return {
        "login": login,
        "display_name": f"{first} {last}".strip(),
        "email": f"{login}@yandex-team.ru",
        "position": position,
        "department": department,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default=os.environ.get("USER", ""))
    args = parser.parse_args()

    if not args.login:
        print("Cannot detect login: $USER is empty and --login not provided", file=sys.stderr)
        sys.exit(1)

    token = get_arc_token()
    if not token:
        print(f"No arc token at {ARC_TOKEN_PATH}. Run: arc auth", file=sys.stderr)
        sys.exit(1)

    info = fetch_staff(args.login, token)
    if not info:
        print(f"Login '{args.login}' not found in Staff", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
