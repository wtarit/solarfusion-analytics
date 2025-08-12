from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
from zoneinfo import ZoneInfo
from dotenv import load_dotenv


def download_energy_balance(
    date_str: str, cookie: str, output_dir: str = "output"
) -> str:
    """Download energy-balance data for a given Bangkok-local date/time and save to JSON.

    Args:
        date_str: Date string like "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" (Bangkok local time).
        cookie: The Cookie header value to authenticate the request.
        output_dir: Directory to write the JSON file into. Created if missing.

    Returns:
        The absolute path to the saved JSON file.
    """

    if " " in date_str:
        parsed_local_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    else:
        parsed_local_datetime = datetime.strptime(date_str, "%Y-%m-%d")
        parsed_local_datetime = parsed_local_datetime.replace(
            hour=0, minute=0, second=0
        )

    bangkok_timezone = ZoneInfo("Asia/Bangkok")
    localized_datetime = parsed_local_datetime.replace(tzinfo=bangkok_timezone)

    query_time_ms = int(localized_datetime.timestamp() * 1000)
    canonical_date_str = localized_datetime.strftime("%Y-%m-%d %H:%M:%S")
    date_part_for_filename = localized_datetime.strftime("%Y-%m-%d")

    base_url = "https://sg5.fusionsolar.huawei.com/rest/pvms/web/station/v3/overview/energy-balance"

    request_params: Dict[str, Any] = {
        "stationDn": "NE=50999304",
        "timeDim": "2",
        "timeZone": "7.0",
        "timeZoneStr": "Asia/Bangkok",
        "queryTime": str(query_time_ms),
        "dateStr": canonical_date_str,
        "_": str(int(time.time() * 1000)),
    }

    request_headers = {
        "Cookie": cookie,
        "Accept": "application/json, text/plain, */*",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://sg5.fusionsolar.huawei.com/",
        "Origin": "https://sg5.fusionsolar.huawei.com",
    }

    response = requests.get(
        base_url, headers=request_headers, params=request_params, timeout=30
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError("Response was not valid JSON") from exc

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.abspath(
        os.path.join(output_dir, f"{date_part_for_filename}.json")
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return output_path


def download_energy_balance_range(
    start_date: str,
    end_date: str,
    cookie: str,
    output_dir: str = "output",
    delay_seconds: float = 2.0,
) -> list[str]:
    """Download energy-balance data for each day in an inclusive date range.

    Args:
        start_date: Start date in YYYY-MM-DD.
        end_date: End date in YYYY-MM-DD (inclusive).
        cookie: Cookie header value for authentication.
        output_dir: Directory to write JSON files.
        delay_seconds: Seconds to sleep between requests.

    Returns:
        List of absolute file paths of downloaded JSON files.
    """

    current = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    saved_paths: list[str] = []
    while current <= end:
        path = download_energy_balance(current.isoformat(), cookie, output_dir)
        saved_paths.append(path)
        if current < end and delay_seconds > 0:
            time.sleep(delay_seconds)
        current += timedelta(days=1)

    return saved_paths


__all__ = ["download_energy_balance", "download_energy_balance_range"]


if __name__ == "__main__":
    load_dotenv()
    cookie_value = os.environ["FUSIONSOLAR_COOKIE"]
    if not cookie_value:
        raise RuntimeError(
            "Set the FUSIONSOLAR_COOKIE environment variable with your session cookie."
        )

    files = download_energy_balance_range(
        start_date="2025-08-12",
        end_date="2025-08-12",
        cookie=cookie_value,
        output_dir="output",
        delay_seconds=2.0,
    )
    print(f"Downloaded {len(files)} files into 'output'")
