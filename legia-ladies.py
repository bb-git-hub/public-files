from datetime import datetime
from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from bs4 import BeautifulSoup
import hashlib
import re


URL = "https://www.flashscore.pl/druzyna/legia-warszawa/hhbcCAY7/"


def make_uid(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def create_calendar():
    cal = Calendar()
    cal.add("prodid", "-//Legia Ladies Calendar//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Legia Ladies")
    return cal


def parse_date(date_text):
    """
    18.10. 10:15
    """

    match = re.search(
        r"(\d{2})\.(\d{2})\.\s+(\d{2}):(\d{2})",
        date_text
    )

    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))
    hour = int(match.group(3))
    minute = int(match.group(4))

    year = datetime.now().year

    return datetime(
        year,
        month,
        day,
        hour,
        minute
    )


def main():

    print("START")

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

        with open(
            "rendered.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)

        browser.close()

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    cal = create_calendar()

    matches = soup.select(
        "div.event__match"
    )

    print("MECZE:", len(matches))

    for match in matches:

        try:

            date_node = match.select_one(
                ".event__stageTime--date"
            )

            if not date_node:
                continue

            date_text = date_node.get_text(
                " ",
                strip=True
            )

            event_date = parse_date(
                date_text
            )

            if not event_date:
                continue

            participants = match.select(
                ".wcl-name_jjfMf"
            )

            if len(participants) < 2:
                continue

            home = participants[0].get_text(
                strip=True
            )

            away = participants[1].get_text(
                strip=True
            )

            scores = match.select(
                ".event__score"
            )

            played = (
                len(scores) >= 2
                and scores[0].get_text(strip=True) != "-"
                and scores[1].get_text(strip=True) != "-"
            )

            if played:

                summary = (
                    f"{home} "
                    f"{scores[0].get_text(strip=True)}:"
                    f"{scores[1].get_text(strip=True)} "
                    f"{away}"
                )

            else:

                summary = (
                    f"{home} - {away}"
                )

            event = Event()

            uid = make_uid(
                f"{event_date}-{home}-{away}"
            )

            event.add(
                "uid",
                uid
            )

            event.add(
                "dtstart",
                event_date
            )

            event.add(
                "summary",
                summary
            )

            cal.add_component(
                event
            )

            print(summary)

        except Exception as ex:
            print(
                "BLAD MECZU:",
                ex
            )

    with open(
        "legia-ladies.ics",
        "wb"
    ) as f:
        f.write(
            cal.to_ical()
        )

    print("ZAPISANO ICS")


if __name__ == "__main__":
    main()
