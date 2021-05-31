# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import get, post, redirect, debug, template, request, run


# uvozimo ustrezne podatke za povezavo
import auth_baza

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# ostale knjiznice
import datetime
import ast
import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# sporočila o napakah
# debug(True)

def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

# tockovanje za posodobitev tock
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

# tocke se posodabljajo vedno pred zagonom. Sprememba bo, ko se bodo vnesli rezultati tekem
def posodobi_tocke():
    cur.execute(
        """
        SELECT uporabnik, tekma, rez_dom, rez_gos, rezultat FROM napovedi
        JOIN tekme ON napovedi.tekma = tekme.stevilka
        WHERE tocke IS NULL AND rezultat != 'Neodigrana' AND rezultat != 'Prestavljena'
        """
    )
    napovedi = cur.fetchall()
    for nap in napovedi:
        napoved = (nap[2], nap[3])
        rezultat = tuple(map(int, nap[4].split("-")))
        tocke, gol_razlika = tockuj(napoved,rezultat)
        cur.execute(
            """
            UPDATE napovedi SET tocke=%s, gol_razlika=%s
            WHERE uporabnik=%s AND tekma=%s
            """,
            (tocke, gol_razlika, nap[0], nap[1])
        )

#################
# ZACETNA STRAN #
#################

@get('/')
def index():
    global napaka_up_ime
    napaka_up_ime = False
    return rtemplate('predloge/zacetna.html', igralni_krog=igralni_krog, uporabnik=uporabnik)


################
# REGISTRACIJA #
################

@get('/registracija')
def registracija():
    return rtemplate('predloge/registracija.html', igralni_krog=igralni_krog, napaka_up_ime=napaka_up_ime)

@post('/registracija')
def registracija_post():
    global uporabnik, uporabnik_id, napaka_up_ime
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo
    geslo_pon = request.forms.geslo_pon
    cur.execute(
        """
        SELECT up_ime FROM uporabniki
        """
    )
    uporabniki = cur.fetchall()
    uporabniki = [up[0] for up in uporabniki]
    if up_ime in uporabniki:
        napaka_up_ime = True
        redirect('{}registracija'.format(ROOT))
    else:
        cur.execute(
            """
            INSERT INTO uporabniki (up_ime, geslo)
            VALUES (%s,%s)
            """,
            (up_ime, geslo)
        )
        cur.execute(
            """
            SELECT id, up_ime FROM uporabniki
            WHERE up_ime=%s
            """,
            (up_ime,)
        )
        trenutni_uporabnik = cur.fetchall()
        uporabnik = trenutni_uporabnik[0][1]
        uporabnik_id = trenutni_uporabnik[0][0]
        redirect('{}'.format(ROOT))


##########
# ODJAVA #
##########

@get('/odjava')
def odjava():
    global uporabnik, uporabnik_id
    uporabnik = None
    uporabnik_id = None
    redirect('{}'.format(ROOT))


###########
# PRIJAVA #
###########

@get('/prijava')
def prijava():
    return rtemplate('predloge/prijava.html', igralni_krog=igralni_krog, napaka_up_ime=napaka_up_ime)

@post('/prijava')
def prijava_post():
    global uporabnik, uporabnik_id, napaka_up_ime
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo
    cur.execute(
        """
        SELECT * FROM uporabniki
        WHERE up_ime=%s AND geslo=%s
        """,
        (up_ime, geslo)
    )
    prijava_uporabnik = cur.fetchall()
    if prijava_uporabnik == []:
        napaka_up_ime = True
        redirect('{}prijava'.format(ROOT))
    else:
        prijava_uporabnik = prijava_uporabnik[0]
        uporabnik_id = int(prijava_uporabnik[0])
        uporabnik = prijava_uporabnik[1]
        redirect('{}'.format(ROOT))


##############
# NASTAVITVE #
##############

@get('/nastavitve')
def nastavitve():
    if not uporabnik:
        redirect('{}'.format(ROOT))
    global napaka_up_ime, spremenjeno
    napaka_up_ime = False
    spremenjeno = False
    return rtemplate('predloge/nastavitve.html', igralni_krog=igralni_krog, napaka_up_ime=napaka_up_ime)

# nastavitve uporabniskega imena

@get('/up-ime')
def up_ime():
    if not uporabnik:
        redirect('{}'.format(ROOT))
    return rtemplate('predloge/up-ime.html', igralni_krog=igralni_krog, napaka_up_ime=napaka_up_ime, spremenjeno=spremenjeno)

@post('/up-ime')
def up_ime_post():
    global napaka_up_ime, uporabnik, spremenjeno
    spremenjeno = False
    napaka_up_ime = False
    up_ime = request.forms.up_ime
    if uporabnik == up_ime:
        print("napaka")
        napaka_up_ime = "Niste spremenili uporabniškega imena!"
        redirect('{}up-ime'.format(ROOT))
        return
    cur.execute(
        """
        SELECT up_ime FROM uporabniki
        """
    )
    uporabniki = cur.fetchall()
    uporabniki = [up[0] for up in uporabniki]
    if up_ime in uporabniki:
        napaka_up_ime = "Uporabniško ime že obstaja!"
        redirect('{}up-ime'.format(ROOT))
        return
    cur.execute(
        """
        UPDATE uporabniki
        SET up_ime=%s
        WHERE up_ime=%s
        """,
        (up_ime, uporabnik)
    )
    uporabnik = up_ime
    spremenjeno = True
    redirect('{}up-ime'.format(ROOT))

# nastavitve gesla

@get('/geslo')
def geslo():
    if not uporabnik:
        redirect('{}'.format(ROOT))
    return rtemplate('predloge/geslo.html', igralni_krog=igralni_krog, napaka_up_ime=napaka_up_ime, spremenjeno=spremenjeno)


@post('/geslo')
def geslo_post():
    global napaka_up_ime, spremenjeno
    spremenjeno = False
    napaka_up_ime = False
    geslo = request.forms.geslo
    cur.execute(
        """
        SELECT * FROM uporabniki
        WHERE up_ime=%s
        """,
        (uporabnik,)
    )
    trenutni_uporabnik = cur.fetchall()
    if trenutni_uporabnik == []:
        redirect('{}'.format(ROOT))
        return
    if geslo == trenutni_uporabnik[0][2]:
        napaka_up_ime = "Novo geslo je enako staremu!"
        redirect('{}geslo'.format(ROOT))
        return
    cur.execute(
        """
        UPDATE uporabniki
        SET geslo=%s
        WHERE up_ime=%s
        """,
        (geslo, uporabnik)
    )
    spremenjeno = True
    redirect('{}geslo'.format(ROOT))


######################
# DODAJANJE NAPOVEDI #
######################

@post('/dodaj-napovedi/:napovedi')
def dodaj_napovedi(napovedi):
    global napaka_pri_vnosu, napovedi_shranjene
    napovedi_shranjene = False
    if napovedi == "ni_napovedi":
        napaka_pri_vnosu = "Napovedi niso pravilno vnešene. Pri eni od tekem si napovedal samo rezultat ene od ekip."
        redirect("{}{}/{}".format(ROOT, trenutna_liga, trenuten_krog))
        return
    napovedi = ast.literal_eval(napovedi)
    nove_napovedi = []
    id_tekem = set()
    for key, val in napovedi.items():
        id_tekem.add(key[3:])
    for tekma in id_tekem:
        dom = None
        gos = None
        for key, val in napovedi.items():
            if key == "dom{}".format(tekma):
                dom = val
            elif key == "gos{}".format(tekma):
                gos = val
        try:
            nove_napovedi.append(list(map(int, [uporabnik_id, tekma, dom, gos])))
        except:
            redirect("{}{}/{}".format(ROOT, trenutna_liga, trenuten_krog))
    cur.execute(
        """
        SELECT napovedi.uporabnik, napovedi.tekma, napovedi.rez_dom, napovedi.rez_gos FROM napovedi
        JOIN tekme ON tekme.stevilka = napovedi.tekma
        JOIN uporabniki ON uporabniki.id = napovedi.uporabnik
        WHERE tekme.liga = %s AND tekme.krog = %s and uporabniki.id = %s
        ORDER BY datum
        """,
        (str(trenutna_liga),str(trenuten_krog), uporabnik_id)
    )
    napovedi = cur.fetchall()
    napovedi.sort(key=lambda x: x[1])
    nove_napovedi.sort(key=lambda x: x[1])
    if nove_napovedi == napovedi:
        napaka_pri_vnosu = "Niste spremenili nobenega rezultata."
        redirect("{}{}/{}".format(ROOT, trenutna_liga, trenuten_krog))
        return
    napovedi_dict = {}
    for nap in napovedi:
        napovedi_dict[nap[1]] = [nap[0], nap[2], nap[3]]
    
    nove_napovedi_dict = {}
    for nap in nove_napovedi:
        nove_napovedi_dict[nap[1]] = [nap[0], nap[2], nap[3]]
    
    delete = []
    for napoved in napovedi_dict.keys():
        if napoved not in nove_napovedi_dict.keys():
            to_append = [napovedi_dict[napoved][0], napoved]+napovedi_dict[napoved][1:]
            if to_append not in delete:
                delete.append(to_append)

    update = []
    new = []
    for nova_napoved in nove_napovedi_dict.keys():
        if nova_napoved in napovedi_dict:
            if napovedi_dict[nova_napoved] != nove_napovedi_dict[nova_napoved]:
                to_append = [nove_napovedi_dict[nova_napoved][0], nova_napoved]+nove_napovedi_dict[nova_napoved][1:]
                if to_append not in update:
                    update.append(to_append)
        else:
            to_append = [nove_napovedi_dict[nova_napoved][0], nova_napoved]+nove_napovedi_dict[nova_napoved][1:]
            if to_append not in new:
                new.append(to_append)
    for nap in update:
        cur.execute(
            """
            UPDATE napovedi
            SET rez_dom = %s, rez_gos = %s
            WHERE napovedi.uporabnik = %s AND napovedi.tekma = %s
            """,
            (nap[2], nap[3], nap[0], nap[1])
        )
    for nap in new:
        cur.execute(
            """
            INSERT INTO napovedi (uporabnik, tekma, rez_dom, rez_gos)
            VALUES (%s,%s,%s,%s)
            """,
            (nap[0], nap[1], nap[2], nap[3])
        )
    for nap in delete:
        cur.execute(
            """
            DELETE FROM napovedi
            WHERE napovedi.uporabnik = %s AND napovedi.tekma = %s
            """,
            (nap[0], nap[1])
        )
    napaka_pri_vnosu = False
    napovedi_shranjene = True
    redirect("{}{}/{}".format(ROOT, trenutna_liga, trenuten_krog))
    return


#################################
# PRIKAZ NAPOVEDI IN REZULTATOV #
#################################

@get('/:liga/:krog')
def liga(liga,krog):
    global trenutna_liga, trenuten_krog, napaka_pri_vnosu, napovedi_shranjene, napaka_up_ime
    posodobi_tocke()
    napaka_up_ime = False
    if int(trenuten_krog) != int(krog) or int(trenutna_liga) != int(liga):
        napaka_pri_vnosu = False
        napovedi_shranjene = False
        trenutna_liga = liga
        trenuten_krog = krog
    cur.execute(
        """
        SELECT tekme.stevilka, K1.ime_ekipe, K2.ime_ekipe, tekme.rezultat, tekme.datum, tekme.ura FROM tekme
        JOIN klubi AS K1 ON tekme.domaca_ekipa = K1.id 
        JOIN klubi AS K2 ON tekme.gostujoca_ekipa = K2.id
        WHERE tekme.liga = %s AND tekme.krog = %s
        ORDER BY datum
        """,
        (str(liga),str(krog))
    )
    tekme = cur.fetchall()

    cur.execute(
            """
            SELECT napovedi.tekma, napovedi.rez_dom, napovedi.rez_gos, napovedi.tocke FROM napovedi
            JOIN tekme ON tekme.stevilka = napovedi.tekma
            JOIN uporabniki ON uporabniki.id = napovedi.uporabnik
            WHERE tekme.liga = %s AND tekme.krog = %s and uporabniki.up_ime = %s
            ORDER BY datum
            """,
            (str(liga),str(krog), uporabnik)
        )
    napovedi = cur.fetchall()
    cur.execute(
        """
        SELECT uporabniki.up_ime, COALESCE(sum(napovedi.tocke),0) AS stevilo_tock FROM uporabniki
        LEFT JOIN napovedi ON napovedi.uporabnik = uporabniki.id
        LEFT JOIN tekme ON napovedi.tekma = tekme.stevilka
        WHERE tekme.liga = %s OR tekme.liga IS NULL
        GROUP BY uporabniki.up_ime
        ORDER BY stevilo_tock DESC, sum(gol_razlika) ASC
        """,
        (liga,)
    )
    uporabniki = cur.fetchall()
    datum = datetime.datetime.now().date()
    ura_now = datetime.datetime.now().time()
    return rtemplate(
        "predloge/rezultati.html",
        tekme=tekme,
        liga=liga,
        krog=krog,
        uporabniki=uporabniki,
        uporabnik=uporabnik,
        datum=datum,
        ura_now=ura_now,
        napovedi=napovedi,
        napaka_pri_vnosu=napaka_pri_vnosu,
        napovedi_shranjene=napovedi_shranjene,
        igralni_krog=igralni_krog
    )


###################
# PRIKLOP NA BAZO #
###################

conn = psycopg2.connect(database=auth_baza.db, host=auth_baza.host, user=auth_baza.user, password=auth_baza.password, port=DB_PORT)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


##########################
# GLOBALNE SPREMENLJIVKE #
##########################

napaka_up_ime = False
spremenjeno = False

uporabnik = None
uporabnik_id = None

trenutna_liga = 6
trenuten_krog = 1
# lahko je igralni krog za vsako ligo posebaj
igralni_krog = 1
napaka_pri_vnosu = False
napovedi_shranjene = False


####################
# POSODOBITEV TOCK #
####################

posodobi_tocke()


##################################################################


####################
# ZAGON APLIKACIJE #
####################

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)