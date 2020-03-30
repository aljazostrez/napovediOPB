import re
import orodja
import os


vzorec_bloka = re.compile(
    r'<h2>Info</h2>.*$',
    flags=re.DOTALL
)

podatki_tekme = re.compile(
    r'<div class="container left">.*?<h3 class="thick">.*?'
    r'<a href=".*?/(?P<domaca_ekipa>\d+?)/">.*?'
    r'<h3 class="thick scoretime ">(?P<rezultat>.*?)</h3>.*?'
    r'<div class="container right">.*?<h3 class="thick">.*?'
    r'<a href=".*?/(?P<gostujoca_ekipa>\d+?)/">.*?'
    r'<dt>Competition</dt>.*?<dd><a href="/.*?/.*?/(?P<liga>.*?)/.*?'
    r'<dt>Date</dt>.*?<dd><a .*?><span .*?>(?P<datum>.*?)</span>.*?'
    r'<dt>Game week</dt>.*?<dd>(?P<krog>\d+?)</dd>.*?'
    r'eventId: "(?P<stevilka>\d+?)"'
    ,flags=re.DOTALL
)

kick_off = re.compile(
    r'<dt>Kick-off</dt>\s*?<dd>\s*?<span class=.*?>(?P<ura>.*?)</span>.*?',
    flags=re.DOTALL
)

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

meseci = {"jan":1 ,"feb":2, "mar":3, "apr":4,
    "may":5, "jun":6, "jul":7, "aug":8,
    "sep":9, "oct":10, "nov":11, "dec":12}

def izloci_podatke_tekme(blok):
    try:
        tekma = podatki_tekme.search(blok).groupdict()
        tekma['domaca_ekipa'] = int(tekma['domaca_ekipa'])
        tekma['gostujoca_ekipa'] = int(tekma['gostujoca_ekipa'])
        tekma['rezultat'] = tekma['rezultat'].replace("\n", "")
        tekma['rezultat'] = tekma['rezultat'].replace(" ", "")
        if len(tekma['rezultat']) > 10 or tekma['rezultat']=="":
            tekma['rezultat'] = "Neodigrana"
        if tekma['rezultat'] == "Postponed":
            tekma['rezultat'] = "Prestavljena"
        if tekma['rezultat'] not in  ["Prestavljena", "Neodigrana"]:
            tekma['ura'] = kick_off.search(blok).group(1)
        else:
            tekma['ura'] = None
        tekma['liga'] = id_lige(tekma['liga'])
        tekma['krog'] = int(tekma['krog'])
        tekma['stevilka'] = int(tekma['stevilka'])
        # uredimo datum
        datum = tekma['datum'].split(" ")[::-1]
        datum[1] = str(meseci[str.lower(datum[1])[:3]])
        datum = "-".join(datum)
        tekma['datum'] = datum
        key_order = ['stevilka', 'domaca_ekipa', 'gostujoca_ekipa',
        'rezultat', 'krog', 'datum',
        'ura', 'liga']
        tekma = {key : tekma[key] for key in key_order}
        return tekma
    except:
        return None

def tekma_i_iz_lige(stevilka, liga):
    ime_datoteke = 'spletne-strani-tekem/{}-{}.html'.format(liga, stevilka)
    vsebina = orodja.vsebina_datoteke(ime_datoteke)
    ekipe = []
    for blok in vzorec_bloka.finditer(vsebina):
        ekipe.append(blok.group(0))
    return ekipe

lige = ["premier-league",
        "serie-a",
        "bundesliga",
        "primera-division",
        "ligue-1"
]

tekme = []

# for tekma in tekma_i_iz_lige(253,lige[2]):
#     podatki = izloci_podatke_tekme(tekma)
#     if podatki:
#         tekme.append(podatki)

for lig in lige:
    st_tekem = 380 if lig != "bundesliga" else 306
    for i in range(1,st_tekem+1):
        for tekma in tekma_i_iz_lige(i,lig):
            podatki = izloci_podatke_tekme(tekma)
            if podatki:
                tekme.append(podatki)
            else:
                print("None pri", lig,i)

# print(tekme)

orodja.zapisi_csv(
    tekme,
    ['stevilka', 'domaca_ekipa', 'gostujoca_ekipa',
    'rezultat', 'krog',
    'datum', 'ura', 'liga'],
    'obdelani-podatki/tekme.csv'
    )
