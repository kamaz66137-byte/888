#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DeepSeek availability healthcheck")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Only validate environment variables and config, no network call",
    )
    return parser.parse_args()


def preflight() -> tuple[bool, list[str]]:
    issues: list[str] = []
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        issues.append("Missing env: DEEPSEEK_API_KEY")

    settings_path = os.path.join(".vscode", "settings.json")
    if not os.path.exists(settings_path):
        issues.append("Missing config: .vscode/settings.json")
    else:
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            path = settings.get("python.defaultInterpreterPath", "")
            if not isinstance(path, str) or not path.strip():
                issues.append("Missing python.defaultInterpreterPath in .vscode/settings.json")
        except Exception as exc:
            issues.append(f"Invalid .vscode/settings.json: {exc}")

    return (len(issues) == 0, issues)


def live_call(base_url: str, model: str, timeout: int) -> tuple[bool, str]:
    api_key = os.environ["DEEPSEEK_API_KEY"].strip()
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            body = json.loads(raw)
        msg = (
            body.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        preview = msg[:80] if msg else "(empty content)"
        return True, f"HTTP {resp.status}, model={body.get('model', model)}, preview={preview}"
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, f"HTTPError {exc.code}: {detail[:300]}"
    except urllib.error.URLError as exc:
        return False, f"URLError: {exc.reason}"
    except Exception as exc:
        return False, f"Unexpected error: {exc}"


def main() -> int:
    # Auto-load root .env to support local testing without manual export.
    load_dotenv(dotenv_path=".env", override=False)

    args = parse_args()

    ok, issues = preflight()
    if not ok:
        print("[FAIL] preflight")
        for issue in issues:
            print(f"- {issue}")
        return 2

    print("[OK] preflight")

    if args.preflight_only:
        print("[SKIP] live call (--preflight-only)")
        return 0

    success, message = live_call(args.base_url, args.model, args.timeout)
    if not success:
        print("[FAIL] live call")
        print(message)
        return 3

    print("[OK] live call")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
