from datetime import datetime, timedelta
import hashlib

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

URL = "https://www.flashscore.pl/druzyna/legia-warszawa/hhbcCAY7/"


def make_uid(value):
    return hashlib.md5(value.encode()).hexdigest()


def create_calendar():
    cal = Calendar()
    cal.add("prodid", "-//Legia Ladies Calendar//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Legia Ladies")
    return cal


def add_match_event(cal, summary, start_dt, uid):
    event = Event()

    event.add("uid", uid)
    event.add("dtstart", start_dt)
    event.add("summary", summary)

    cal.add_component(event)


def main():

    print("START")

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

    print("STATUS:", response.status_code)
    print("DLUGOSC STRONY:", len(response.text))

    if response.status_code != 200:
        print(f"BLAD HTTP: {response.status_code}")
        return

    print("POBRANO STRONE")

    with open("page.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("ZAPISANO page.html")

    soup = BeautifulSoup(response.text, "lxml")

    print("TYTUL STRONY:")
    print(soup.title.text if soup.title else "Brak tytulu")

    cal = create_calendar()

    test_date = datetime.now() + timedelta(days=1)

    add_match_event(
        cal=cal,
        summary="TEST - Legia Ladies",
        start_dt=test_date,
        uid=make_uid("TEST")
    )

    with open("legia-ladies.ics", "wb") as f:
        f.write(cal.to_ical())

    print("ZAPISANO legia-ladies.ics")
    print("KONIEC SKRYPTU")


if __name__ == "__main__":
    main()
