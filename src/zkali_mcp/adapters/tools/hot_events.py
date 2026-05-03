"""tool.hot_events - Unified live event query tool."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET


def _to_target_tz(timestamp: str, tz_name: str) -> str:
    if not timestamp:
        return ""
    dt = datetime.fromisoformat(timestamp)
    dt_utc = dt.replace(tzinfo=timezone.utc)

    offset_map = {
        "UTC": 0,
        "Asia/Shanghai": 8,
        "Asia/Hong_Kong": 8,
        "Asia/Tokyo": 9,
        "Europe/London": 0,
        "America/New_York": -4,
    }
    offset_hours = offset_map.get(tz_name, 8)
    converted = dt_utc + timedelta(hours=offset_hours)
    return converted.strftime("%Y-%m-%d %H:%M:%S")


def _fetch_google_news(topic: str, date_value: str, limit: int) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "q": f"{topic} {date_value}",
            "hl": "zh-CN",
            "gl": "CN",
            "ceid": "CN:zh-Hans",
        }
    )
    url = f"https://news.google.com/rss/search?{query}"
    with urllib.request.urlopen(url, timeout=12) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[dict] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append({"title": title, "link": link, "pub_date": pub_date, "source": "Google News"})
    return items


def _fetch_hn_news(topic: str, limit: int) -> list[dict]:
    query = urllib.parse.urlencode({"q": topic, "count": limit})
    url = f"https://hnrss.org/newest?{query}"
    with urllib.request.urlopen(url, timeout=12) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[dict] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append({"title": title, "link": link, "pub_date": pub_date, "source": "Hacker News"})
    return items


def _parse_pub_date(pub_date: str, tz_name: str) -> str:
    if not pub_date:
        return ""
    try:
        dt = parsedate_to_datetime(pub_date)
        dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return _to_target_tz(dt_utc.isoformat(), tz_name)
    except Exception:
        return ""


def dispatch_hot_events_tool(name: str, arguments: dict) -> str | None:
    if name != "query/hot-events":
        return None

    topic = str(arguments.get("topic", "")).strip().lower()
    if not topic:
        return "ERR: INVALID_PARAM topic is required"

    date_value = str(arguments.get("date", "today")).strip().lower()
    if date_value == "today":
        date_value = datetime.utcnow().strftime("%Y-%m-%d")

    # Use tz_name to avoid shadowing the imported timezone module
    tz_name = str(arguments.get("timezone", "Asia/Shanghai")).strip() or "Asia/Shanghai"
    region = str(arguments.get("region", "global")).strip() or "global"
    scope = str(arguments.get("scope", "hot")).strip().lower() or "hot"
    lang = str(arguments.get("lang", "zh-CN")).strip() or "zh-CN"
    strict_mode = bool(arguments.get("strict_mode", True))

    limit_raw = int(arguments.get("limit", 10))
    limit = max(1, min(50, limit_raw))

    news_items: list[dict] = []
    sources_used: list[dict] = []
    errors: list[str] = []

    # Route to different sources based on region
    if region in ("hacker-news", "hn"):
        try:
            news_items = _fetch_hn_news(topic, limit)
            sources_used.append({"name": "Hacker News RSS", "url": "https://hnrss.org/", "note": "public hn rss"})
        except Exception as exc:
            errors.append(f"HN: {exc}")
    else:
        try:
            news_items = _fetch_google_news(topic, date_value, limit)
            sources_used.append({"name": "Google News RSS", "url": "https://news.google.com/", "note": "public news rss"})
        except Exception as exc:
            errors.append(f"Google News: {exc}")
        # If Google News fails or region == "multi", try HN as well
        if region == "multi" or (not news_items and region == "global"):
            try:
                hn_items = _fetch_hn_news(topic, limit)
                news_items.extend(hn_items)
                sources_used.append({"name": "Hacker News RSS", "url": "https://hnrss.org/", "note": "public hn rss"})
            except Exception as exc:
                errors.append(f"HN fallback: {exc}")

    if not news_items and errors:
        return f"ERR: SOURCE_UNAVAILABLE {'; '.join(errors)}"

    items: list[dict] = []
    for news in news_items:
        start_time = _parse_pub_date(news.get("pub_date") or "", tz_name)
        items.append(
            {
                "title": news.get("title", ""),
                "league": "",
                "start_time": start_time,
                "status": "upcoming",
                "score": "",
                "importance": 3,
                "source_refs": [news.get("link", "")],
                "source": news.get("source", ""),
            }
        )

    if scope == "hot":
        items = items[:limit]

    result = {
        "request_id": f"hot-{int(datetime.utcnow().timestamp())}",
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + "Z",
        "normalized_timezone": tz_name,
        "query_summary": {
            "topic": topic,
            "date": date_value,
            "region": region,
            "scope": scope,
            "limit": limit,
            "lang": lang,
            "strict_mode": strict_mode,
        },
        "sources": sources_used,
        "items": items,
        "highlights": [row["title"] for row in items[: min(5, len(items))]],
        "warnings": ([] if items else ["NO_DATA"]) + errors,
    }
    return json.dumps(result, ensure_ascii=False)
