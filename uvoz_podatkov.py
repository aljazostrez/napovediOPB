# uvozimo ustrezne podatke za povezavo
import auth_baza
import csv

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

conn = psycopg2.connect(database=auth_baza.db, host=auth_baza.host, user=auth_baza.user, password=auth_baza.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def uvoziSQL(cur, datoteka):
    with open(datoteka) as f:
        koda = f.read()
        try:
            cur.execute(koda)
        except:
            cur.execute("ROLLBACK")
            cur.execute(koda)
    conn.commit()

# uvoziSQL(cur, "ustvari_bazo.sql")

def uvoziCSV(cur, tabela, datoteka):
    # vstavi v tabelo podatke iz datoteke
    with open('zajem-in-obdelava/obdelani-podatki/{}'.format(datoteka)) as csvfile:
        podatki = csv.reader(csvfile)
        vsiPodatki = [vrstica for vrstica in podatki]
        glava = vsiPodatki[0]
        vrstice = vsiPodatki[1:]
        for vrstica in vrstice:
            if vrstica[-1] == "":
                vrstica[-1] = None
                vrstica[-2] = None
            try:
                cur.execute("INSERT INTO {0} ({1}) VALUES ({2})".format(
                    tabela, ",".join(glava), ",".join(['%s']*len(glava))), vrstica)
            except:
                cur.execute("ROLLBACK")
                cur.execute("INSERT INTO {0} ({1}) VALUES ({2})".format(
                    tabela, ",".join(glava), ",".join(['%s']*len(glava))), vrstica)
    conn.commit()

# uvoziCSV(cur, "lige", "lige.csv")
# uvoziCSV(cur, "klubi", "klubi.csv")
# uvoziCSV(cur, "tekme", "tekme.csv")
# uvoziCSV(cur, "uporabniki", "uporabniki.csv")
# uvoziCSV(cur, "napovedi", "napovedi.csv")