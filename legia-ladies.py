import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid

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


def create_calendar():
    cal = Calendar()
    cal.add("prodid", "-//Legia Ladies Calendar//")
    cal.add("version", "2.0")
    return cal


def add_event(cal, summary, start_date, all_day=False):
    event = Event()

    event.add("uid", str(uuid.uuid4()))

    if all_day:
        event.add("dtstart", start_date.date())
        event.add("dtend", (start_date + timedelta(days=1)).date())
    else:
        event.add("dtstart", start_date)

    event.add("summary", summary)

    cal.add_component(event)


def main():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    html = response.text

    cal = create_calendar()

    #
    # Wersja startowa.
    # Najpierw zapisujemy HTML do debugowania,
    # żeby zobaczyć dokładną strukturę.
    #
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Pobrano stronę.")
    print("Zapisano debug.html")

    with open("legia-ladies.ics", "wb") as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    main()
