from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
import hashlib


URL = "https://www.flashscore.pl/druzyna/legia-warszawa/hhbcCAY7/"


def make_uid(value):
    return hashlib.md5(value.encode()).hexdigest()


def create_calendar():
    cal = Calendar()
    cal.add("prodid", "-//Legia Ladies Calendar//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Legia Ladies")
    return cal


def add_event(cal, summary):
    event = Event()

    event.add(
        "dtstart",
        datetime.now() + timedelta(days=1)
    )

    event.add(
        "uid",
        make_uid(summary)
    )

    event.add(
        "summary",
        summary
    )

    cal.add_component(event)


def main():

    print("START PLAYWRIGHT")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_timeout(10000)

        html = page.content()

        print("DLUGOSC HTML:", len(html))

        with open(
            "rendered.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)

        cal = create_calendar()

        add_event(
            cal,
            "TEST PLAYWRIGHT"
        )

        with open(
            "legia-ladies.ics",
            "wb"
        ) as f:
            f.write(cal.to_ical())

        browser.close()

    print("KONIEC")


if __name__ == "__main__":
    main()
