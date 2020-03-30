import orodja

lige = {"england": "premier-league",
        "italy": "serie-a",
        "germany": "bundesliga",
        "spain": "primera-division",
        "france": "ligue-1"
        }

for drzava, liga in lige.items():
    url = (
        r'https://int.soccerway.com/national/{}/{}/20192020'
    ).format(drzava, liga)
    orodja.shrani_spletno_stran(url, 'spletne-strani/{}-{}.html'.format(drzava, liga))