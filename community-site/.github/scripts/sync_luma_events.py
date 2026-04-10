#!/usr/bin/env python3
"""
Fetches events from a Luma ICS calendar feed and updates events/index.html.
Only future events are included. Existing non-Luma events (manual entries) are preserved.
"""

import urllib.request
import re
import html
from datetime import datetime, timezone
from collections import defaultdict

ICS_URL = "https://api2.luma.com/ics/get?entity=calendar&id=cal-A2dwFnQTrIufWtY"
EVENTS_HTML = "events/index.html"
START_MARKER = "<!-- LUMA-EVENTS-START -->"
END_MARKER = "<!-- LUMA-EVENTS-END -->"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_FULL = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
MONTH_ABBR = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def parse_ics(ics_text):
    """Parse ICS text into a list of event dicts."""
    events = []
    current = None

    # Unfold continuation lines (lines starting with space/tab)
    lines = ics_text.replace("\r\n ", "").replace("\r\n\t", "").split("\r\n")
    if len(lines) <= 1:
        lines = ics_text.replace("\n ", "").replace("\n\t", "").split("\n")

    for line in lines:
        if line.strip() == "BEGIN:VEVENT":
            current = {}
        elif line.strip() == "END:VEVENT" and current is not None:
            events.append(current)
            current = None
        elif current is not None and ":" in line:
            key, _, value = line.partition(":")
            # Strip parameters (e.g., DTSTART;VALUE=DATE:20260101)
            key = key.split(";")[0]
            current[key] = value

    return events


def parse_dt(dt_str):
    """Parse ICS datetime string to a datetime object."""
    dt_str = dt_str.strip()
    if dt_str.endswith("Z"):
        return datetime.strptime(dt_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    elif "T" in dt_str:
        return datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
    else:
        return datetime.strptime(dt_str, "%Y%m%d")


def extract_luma_url(description):
    """Extract the luma.com event URL from the DESCRIPTION field."""
    if not description:
        return None
    match = re.search(r'https://luma\.com/[a-zA-Z0-9_-]+', description)
    if match:
        return match.group(0)
    return None


def extract_location_city(location):
    """Extract city from location string."""
    if not location:
        return "Helsinki"
    if "Helsinki" in location:
        return "Helsinki"
    if "Tampere" in location:
        return "Tampere"
    if "Oulu" in location:
        return "Oulu"
    if "http" in location:
        return "Online"
    # Try to get city from comma-separated location
    parts = [p.strip() for p in location.split(",")]
    for part in parts:
        if part and not part.isdigit() and len(part) > 2:
            return part
    return "Helsinki"


def build_event_card(event):
    """Build HTML for a single event card."""
    start = parse_dt(event.get("DTSTART", ""))
    end = parse_dt(event.get("DTEND", ""))
    summary = html.escape(event.get("SUMMARY", "Untitled Event"))
    description = event.get("DESCRIPTION", "")
    location = event.get("LOCATION", "")

    url = extract_luma_url(description)
    if not url:
        url = "#"

    city = extract_location_city(location)
    day = start.day
    month_abbr = MONTHS[start.month - 1]
    weekday = WEEKDAYS[start.weekday()]
    date_str = f"{start.year}-{start.month:02d}-{start.day:02d}"
    month_key = MONTH_ABBR[start.month - 1]

    # Time formatting — convert UTC to Helsinki (UTC+3 summer / UTC+2 winter)
    # Use +3 for Apr-Oct, +2 for Nov-Mar (simplified DST)
    tz_offset = 3 if 4 <= start.month <= 10 else 2
    from datetime import timedelta
    start_local = start + timedelta(hours=tz_offset)
    end_local = end + timedelta(hours=tz_offset)
    # Recalculate day/weekday from local time
    day = start_local.day
    weekday = WEEKDAYS[start_local.weekday()]
    month_abbr = MONTHS[start_local.month - 1]
    date_str = f"{start_local.year}-{start_local.month:02d}-{start_local.day:02d}"
    month_key = MONTH_ABBR[start_local.month - 1]

    duration_hours = (end - start).total_seconds() / 3600
    if duration_hours >= 8:
        time_str = "Full day"
    else:
        time_str = f"{start_local.strftime('%H:%M')}\u2013{end_local.strftime('%H:%M')}"

    # Clean up description for the card
    desc_clean = description.split("\\n")[0]  # First line only
    desc_clean = re.sub(r'Get up-to-date information at:.*', '', desc_clean).strip()
    if not desc_clean or desc_clean == description:
        desc_clean = ""

    # All Luma events from this calendar are free
    price_tag = '<span class="event-card__tag event-card__tag--free">Free</span>'

    return f'''    <a href="{url}" target="_blank" class="event-card" data-month="{month_key}" data-date="{date_str}" data-source="luma">
      <div class="event-card__date">
        <div class="event-card__day">{day}</div>
        <div class="event-card__month">{month_abbr}</div>
        <div class="event-card__weekday">{weekday}</div>
      </div>
      <div class="event-card__info">
        <div class="event-card__title">{summary}</div>
        {f'<p class="event-card__desc">{html.escape(desc_clean)}</p>' if desc_clean else ''}
        <div class="event-card__meta">
          <span class="event-card__tag">📍 {city}</span>
          <span class="event-card__tag">{time_str}</span>
          {price_tag}
        </div>
      </div>
      <div class="event-card__arrow">→</div>
    </a>'''


def get_manual_events(html_content):
    """Extract manually-added event cards (non-Luma) from the HTML between markers."""
    start_idx = html_content.find(START_MARKER)
    end_idx = html_content.find(END_MARKER)
    if start_idx == -1 or end_idx == -1:
        return []

    section = html_content[start_idx + len(START_MARKER):end_idx]

    # Find all event cards without data-source="luma"
    manual_cards = []
    pattern = r'(<a\s+href="(?!https://luma\.com/).*?</a>)'
    matches = re.findall(pattern, section, re.DOTALL)
    for match in matches:
        # Extract the date for sorting
        date_match = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', match)
        if date_match:
            manual_cards.append({
                'date': date_match.group(1),
                'html': match.strip()
            })

    return manual_cards


def main():
    # Fetch ICS
    req = urllib.request.Request(ICS_URL, headers={"User-Agent": "AwesomeMarketers-EventSync/1.0"})
    response = urllib.request.urlopen(req)
    ics_text = response.read().decode("utf-8")
    raw_events = parse_ics(ics_text)

    # Filter to future events only
    now = datetime.now(timezone.utc)
    future_events = []
    for ev in raw_events:
        try:
            start = parse_dt(ev.get("DTSTART", ""))
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if start > now:
                future_events.append(ev)
        except (ValueError, KeyError):
            continue

    # Sort by date
    future_events.sort(key=lambda e: parse_dt(e.get("DTSTART", "")))

    # Read current HTML
    with open(EVENTS_HTML, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Get manually-added events
    manual_events = get_manual_events(html_content)

    # Build Luma event cards with dates for merging
    luma_cards = []
    for ev in future_events:
        start = parse_dt(ev.get("DTSTART", ""))
        date_str = f"{start.year}-{start.month:02d}-{start.day:02d}"
        luma_cards.append({
            'date': date_str,
            'html': build_event_card(ev)
        })

    # Merge all events and sort by date
    all_cards = manual_events + luma_cards
    # Also filter manual events to future only
    today_str = now.strftime("%Y-%m-%d")
    all_cards = [c for c in all_cards if c['date'] >= today_str]
    all_cards.sort(key=lambda c: c['date'])

    # Group by month
    months = defaultdict(list)
    for card in all_cards:
        year_month = card['date'][:7]  # "2026-04"
        months[year_month].append(card)

    # Build the new events section
    parts = []
    for ym in sorted(months.keys()):
        year = ym[:4]
        month_num = int(ym[5:7])
        month_name = MONTH_FULL[month_num - 1]
        month_key = MONTH_ABBR[month_num - 1]
        parts.append(f'\n    <div class="events-month-label" data-group="{month_key}">{month_name} {year}</div>\n')
        for card in months[ym]:
            parts.append(card['html'])
            parts.append("")

    new_events_html = "\n".join(parts)

    # Replace the section between markers
    start_idx = html_content.find(START_MARKER)
    end_idx = html_content.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find LUMA-EVENTS markers in HTML")
        return

    new_html = (
        html_content[:start_idx + len(START_MARKER)]
        + "\n"
        + new_events_html
        + "\n    "
        + html_content[end_idx:]
    )

    with open(EVENTS_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Synced {len(luma_cards)} Luma events + {len(manual_events)} manual events")


if __name__ == "__main__":
    main()
