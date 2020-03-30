import csv
import orodja

tekme = []
with open('obdelani-podatki/tekme.csv') as csvFile:
    reader = csv.reader(csvFile)
    header = next(reader)
    for row in reader:
        tekma = {}
        for i in range(len(header)):
            tekma[header[i]] = row[i]
        tekme.append(tekma)

uporabniki = []
with open('obdelani-podatki/uporabniki.csv') as csvFile:
    reader = csv.reader(csvFile)
    header = next(reader)
    for row in reader:
        uporabnik = {}
        for i in range(len(header)):
            uporabnik[header[i]] = row[i]
        uporabniki.append(uporabnik)

## zgenerirajmo napovedi
import random

def napoved():
    a = round(random.gauss(1,1.5))
    b = round(random.gauss(1,1.3))
    if a >= 0 and b >= 0:
        return (a,b)
    # else:
    #     print("Ni napovedi")

def tockuj(napoved, rezultat):
    if napoved == rezultat:
        return (5, 0)
    a = napoved[0]
    b = napoved[1]
    c = rezultat[0]
    d = rezultat[1]
    if a - b == c - d:
        return (3, 0)
    elif (a > b and c > d) or (b > a and d > c):
        return (2, abs(a - b - (c - d)))
    else:
        return (0, abs(a - b) + abs(c - d))

napovedi = []


for tekma in tekme:
    for uporabnik in uporabniki:
        nap = napoved()
        if nap:
            try:
                rezultat = (int(tekma["rezultat"][0]), int(tekma["rezultat"][-1]))
                tocke = tockuj(rezultat, nap)
                napovedi.append({
                    "uporabnik": uporabnik["id"],
                    "tekma": tekma["stevilka"],
                    "rez_dom": nap[0],
                    "rez_gos": nap[1],
                    "tocke": tocke[0],
                    "gol_razlika": tocke[1]
                })
            except:
                napovedi.append({
                    "uporabnik": uporabnik["id"],
                    "tekma": tekma["stevilka"],
                    "rez_dom": nap[0],
                    "rez_gos": nap[1],
                    "tocke": None,
                    "gol_razlika": None
                })

orodja.zapisi_csv(
    napovedi,
    ["uporabnik", "tekma", "rez_dom", "rez_gos", "tocke", "gol_razlika"],
    "obdelani-podatki/napovedi.csv"
)