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
        "https://www.flashscore.pl/druzyna/legia-warszawa/hhbcCAY7/",
        headers=headers,
        timeout=30
    )

    print(f"Status: {response.status_code}")
    print(f"Długość HTML: {len(response.text)}")

    if response.status_code != 200:
        print("Nie udało się pobrać strony")
        return

    with open("page.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("Zapisano page.html")
