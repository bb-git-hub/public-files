import hashlib
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

URL = "https://regiowyniki.pl/druzyna/Pilka_Nozna/Polska/Legia_Ladies__k_/"

MONTHS = {
    "sty": 1,
    "lut": 2,
    "mar": 3,
    "kwi": 4,
    "maj": 5,
    "cze": 6,
    "lip": 7,
    "sie": 8,
    "wrz": 9,
    "paź": 10,
    "lis": 11,
    "gru": 12,
}

YEAR = datetime.now().year


def make_uid(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def create_calendar():
    cal = Calendar()
    cal.add("prodid", "-//Legia Ladies Calendar//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Legia Ladies")
    return cal


def add_match_event(cal, summary, start_dt, all_day, uid):
    event = Event()

    event.add("uid", uid)

    if all_day:
        event.add("dtstart", start_dt.date())
        event.add("dtend", (start_dt + timedelta(days=1)).date())
    else:
        event.add("dtstart", start_dt)

    event.add("summary", summary)

    cal.add_component(event)


def parse_date(day_text, time_text):
    """
    np.
    01 sie
    13:15

    lub

    31 paź
    ?:?
    """

    match = re.match(r"(\d{1,2})\s+([^\s]+)", day_text.lower())

    if not match:
        return None, None

    day = int(match.group(1))
    month_name = match.group(2)

    if month_name not in MONTHS:
        return None, None

    month = MONTHS[month_name]

    if time_text == "?:?":
        dt = datetime(YEAR, month, day)
        return dt, True

    hh, mm = time_text.split(":")
    dt = datetime(YEAR, month, day, int(hh), int(mm))

    return dt, False


def create_summary(home, away, score=None):
    if score:
        return f"{home} {score} {away}"

    return f"{home} - {away}"


def main():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # zapis strony do analizy podczas pierwszych testów
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    cal = create_calendar()

    # TODO:
    # Tutaj podłączymy właściwy parser po obejrzeniu page.html
    #
    # Przykładowe wydarzenie testowe:

    dt = datetime(YEAR, 10, 18, 12, 15)

    add_match_event(
        cal=cal,
        summary="Legia Ladies - Górnik Łęczna",
        start_dt=dt,
        all_day=False,
        uid=make_uid("Legia-Gornik-2026-10-18")
    )

    with open("legia-ladies.ics", "wb") as f:
        f.write(cal.to_ical())

    print("Utworzono legia-ladies.ics")


if __name__ == "__main__":
    main()
