import orodja

# vemo zacetek range-a, konec = zacetek + stevilo_tekem - 1
lige = {"premier-league": range(3029073, 3029073+380),
        "serie-a": range(3111700, 3111700+380),
        "bundesliga": range(3047020, 3047020+306),
        "primera-division": range(3058810, 3058810+380),
        "ligue-1": range(3030547, 3030547+380)
        }

link = r"https://int.soccerway.com/matches/0000/00/00/_/_/_/_/{}/"

for liga, rang in lige.items():
    for i in rang:
        url = (
        link
        ).format(str(i))
        orodja.shrani_spletno_stran(url, 'spletne-strani-tekem/{}-{}.html'.format(liga, (i-rang[0])+1))