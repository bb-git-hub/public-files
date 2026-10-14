from datetime import datetime
from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from bs4 import BeautifulSoup
import hashlib
import re


URL = "https://www.flashscore.pl/druzyna/legia-warszawa/hhbcCAY7/"


def make_uid(value):
    return hashlib.md5(
        value.encode("utf-8")
    ).hexdigest()


def create_calendar():
    cal = Calendar()

    cal.add(
        "prodid",
        "-//Legia Ladies Calendar//"
    )

    cal.add(
        "version",
        "2.0"
    )

    cal.add(
        "x-wr-calname",
        "Legia Warszawa Kobiety"
    )

    return cal


def league_prefix(name):

    if not name:
        return "[Inne]"

    lname = name.lower()

    if "ekstraliga" in lname:
        return "[Ekstraliga]"

    if "puchar" in lname:
        return "[Puchar Polski]"

    if "towarzyskie" in lname:
        return "[Sparing]"

    return f"[{name}]"


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

    now = datetime.now()
    year = now.year

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

        page.wait_for_timeout(5000)

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

    events = []

    current_league = "Inne"

    container = soup.select_one(
        "div.leagues--static"
    )

    if not container:
        print("Nie znaleziono sekcji meczów")
        return

    all_elements = container.find_all(
        ["div"],
        recursive=True
    )

    for element in all_elements:

        classes = element.get("class", [])

        if "headerLeague__wrapper" in classes:

            league_title = element.select_one(
                ".headerLeague__title-text"
            )

            if league_title:

                current_league = (
                    league_title.get_text(
                        strip=True
                    )
                )

        if "event__match" not in classes:
            continue

        try:

            date_node = element.select_one(
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

            participants = element.select(
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

            scores = element.select(
                ".event__score"
            )

            played = (
                len(scores) >= 2
                and scores[0].get_text(strip=True) != "-"
                and scores[1].get_text(strip=True) != "-"
            )

            prefix = league_prefix(
                current_league
            )

            if played:

                home_score = scores[0].get_text(
                    strip=True
                )

                away_score = scores[1].get_text(
                    strip=True
                )

                summary = (
                    f"{prefix} "
                    f"{home} "
                    f"{home_score}:{away_score} "
                    f"{away}"
                )

            else:

                summary = (
                    f"{prefix} "
                    f"{home} - {away}"
                )

            event = Event()

            uid = make_uid(
                (
                    f"{event_date.isoformat()}|"
                    f"{home}|"
                    f"{away}"
                )
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

            event.add(
                "description",
                current_league
            )

            events.append(
                (
                    event_date,
                    event
                )
            )

            print(summary)

        except Exception as ex:

            print(
                "BLAD:",
                ex
            )

    events.sort(
        key=lambda x: x[0]
    )

    for _, event in events:
        cal.add_component(
            event
        )

    with open(
        "legia-ladies.ics",
        "wb"
    ) as f:
        f.write(
            cal.to_ical()
        )

    print(
        f"ZAPISANO {len(events)} MECZOW"
    )


if __name__ == "__main__":
    main()
