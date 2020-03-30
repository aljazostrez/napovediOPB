import re
import orodja
import os


vzorec_bloka = re.compile(
    r'<tr class=".*?"  id="team_rank_row_\d*?" data-team_id="\d*?">.*?'
    r'</tr>',
    flags=re.DOTALL
)


podatki_ekipe = re.compile(
    r'<tr class=".*?"  id="team_rank_row_\d*?" data-team_id="(?P<id>\d*?)">.*?'
    r'<td class="text team large-link"><a href=".*?" title="(?P<ime_ekipe>.*?)">.*?</a></td>',
    flags=re.DOTALL
)

def izloci_podatke_ekipe(blok):
    try:
        ekipa = podatki_ekipe.search(blok).groupdict()
        ekipa['id'] = int(ekipa['id'])
        return ekipa
    except:
        return None

def ekipe_iz_lige(drzava, liga):
    ime_datoteke = 'spletne-strani/{}-{}.html'.format(drzava, liga)
    vsebina = orodja.vsebina_datoteke(ime_datoteke)
    ekipe = []
    for blok in vzorec_bloka.finditer(vsebina):
        ekipe.append(blok.group(0))
    return ekipe

lige = {"england": "premier-league",
        "italy": "serie-a",
        "germany": "bundesliga",
        "spain": "primera-division",
        "france": "ligue-1"
        }

def id_lige(liga):
    if liga == "premier-league":
        return 1
    elif liga == "serie-a":
        return 2
    elif liga == "bundesliga":
        return 3
    elif liga == "primera-division":
        return 4
    elif liga == "ligue-1":
        return 5

ekipe = []
for drzava, liga in lige.items():
    for ekipa in ekipe_iz_lige(drzava, liga):
        podatki = izloci_podatke_ekipe(ekipa)
        if podatki and podatki['id'] not in [ekipa['id'] for ekipa in ekipe]:
            podatki["liga"] = id_lige(liga)
            ekipe.append(podatki)


orodja.zapisi_csv(
    ekipe, ['id', 'ime_ekipe', 'liga'], 'obdelani-podatki/klubi.csv'
    )

orodja.zapisi_json(ekipe, 'obdelani-podatki/klubi.json')

lige_top5 = []
for drzava, liga in lige.items():
    liga_i = {}
    liga_i["id"] = id_lige(liga)
    if drzava == "england" and liga == "premier-league":
        liga_i["drzava"] = "Anglija"
        liga_i["ime"] = "Premier League"
    elif drzava == "italy" and liga == "serie-a":
        liga_i["drzava"] = "Italija"
        liga_i["ime"] = "Serie A"
    elif drzava == "germany" and liga == "bundesliga":
        liga_i["drzava"] = "Nemčija"
        liga_i["ime"] = "Bundesliga"
    elif drzava == "spain" and liga == "primera-division":
        liga_i["drzava"] = "Španija"
        liga_i["ime"] = "Primera Division"
    elif drzava == "france" and liga == "ligue-1":
        liga_i["drzava"] = "Francija"
        liga_i["ime"] = "Ligue 1"
    lige_top5.append(liga_i)

orodja.zapisi_csv(
    lige_top5, ['id', 'drzava', 'ime'], 'obdelani-podatki/lige.csv'
    )