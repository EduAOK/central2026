import requests
import datetime
from zoneinfo import ZoneInfo

AFA_URL = "https://api.sofascore.com/api/v1/team/4411/events/next/0"  # Rosario Central ID en Sofascore
CONMEBOL_URL = "https://api.sofascore.com/api/v1/team/4411/events/next/1"

OUTPUT_FILE = "docs/rosario-central.ics"

def fetch_events(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("events", [])
    except:
        return []

def filter_relevant(events):
    filtered = []
    for e in events:
        comp = e["tournament"]["name"].lower()
        if ("libertadores" in comp) or ("liga profesional" in comp) or ("copa de la liga" in comp):
            filtered.append(e)
    return filtered

def to_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EduAOK//Rosario Central//ES",
        "CALSCALE:GREGORIAN"
    ]

    for e in events:
        start = datetime.datetime.fromtimestamp(e["startTimestamp"], tz=ZoneInfo("America/Argentina/Buenos_Aires"))
        dt = start.strftime("%Y%m%dT%H%M%S")

        home = e["homeTeam"]["name"]
        away = e["awayTeam"]["name"]
        title = f"{home} vs {away}"

        url = f"https://www.sofascore.com{e['slug']}/{e['id']}"

        lines += [
            "BEGIN:VEVENT",
            f"UID:{e['id']}@rosariocentral",
            f"DTSTAMP:{dt}",
            f"DTSTART:{dt}",
            f"SUMMARY:{title}",
            f"DESCRIPTION:Partido oficial - {e['tournament']['name']}\\n{url}",
            "END:VEVENT"
        ]

    lines.append("END:VCALENDAR")
    return "\n".join(lines)

def main():
    events = fetch_events(AFA_URL) + fetch_events(CONMEBOL_URL)
    events = filter_relevant(events)

    future = []
    now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    for e in events:
        if e["startTimestamp"] > now.timestamp():
            future.append(e)

    ics = to_ics(future)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(ics)

if __name__ == "__main__":
    main()
