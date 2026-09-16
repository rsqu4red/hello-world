#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer die Klinkenmanschette

Sechs Teile: zwei Formhaelften, zwei gleiche Bohrungskerne, ein
Kammerkern, ein Schnurkern.

Die Regel
---------

Jedes Formteil verlaesst das Gussteil auf geraden Zuegen. Kein Kippen,
kein Verformen. Fuenf der sechs Teile brauchen dafuer einen einzigen
Zug, der Kammerkern zwei - erst hoch in die Bohrung, dann axial heraus.
Mehr als zwei sind nicht erlaubt, und krumme Wege gar nicht.

Die Regel ist teuer erkauft. Die Form hatte fuenf Vorfassungen, jede
scheiterte an einem Teil, das nur auf einem krummen Weg herauskam:

1. Bohrung, Kammer und Schnurkanal als Halbkerne in den Haelften.
   806 von 1042 Saeulen gesperrt.
2. Loser Kammerkern, "von Hand nach oben kippen". 23 Prozent Dehnung -
   und die Kennzahl mass nur die Mittelscheibe.
3. Dreiteiliger Kammerkern mit Zunge. Zwoelf Scheiben gesperrt.
4. Kammer als nach oben offener Trog. Der Kern kam hoch, aber unter dem
   Bauteil sassen Knauf Ø12 und ein Flach 7 mm, die durch die Ø5-
   Schnurbohrung gemusst haetten.
5. Knotenkanal durchgehend, gebildet von einem Kiel an den
   Bohrungskernen. Alles gerade - aber die Knotenkammer war weg.

Was daraus geworden ist
-----------------------

Zwei Aenderungen halten alles frei:

Der Kammerquerschnitt ist ein U - untere Haelfte rund, darueber
senkrechte Waende bis in die Bohrung. Ein runder Querschnitt ist an
seiner breitesten Stelle breiter als sein Durchbruch; der Kern sitzt
dann darin fest wie ein Teller in der Flasche. Das U ist an keiner
Stelle breiter als seine Oeffnung.

Der Schnurstift ist ein eigenes Teil. Frueher hing er am Kammerkern und
machte ihn zum Pilz im Flaschenhals. Jetzt zieht er nach unten, vom
Bauteil weg - dort darf er beliebig dick sein. Er ragt 2 mm ueber den
Kammerboden hinaus in ein Steckloch im Kammerkern, traegt ihn damit und
haelt ihn in x und z fest.

Uebrig bleibt ein nackter Trog, 11 mm breit, 21 mm lang. Gegen Verdrehen
legt er sich mit seinen Oberkanten an die Bohrungskerne - nachgerechnet
sperrt das ab dem ersten Viertelgrad.

Die sechs Teile und ihre Zuege
------------------------------

Haelften      -> +/- x   Sie formen nur die Aussenflaeche. Deren
                         Querschnitt ist die Vereinigung zweier Kreise
                         auf x = 0, zu dieser Ebene hin also monoton.
Bohrungskerne -> +/- z   Die Bohrung ist nicht monoton - Ø20/Ø18/Ø20.
                         Ein einteiliger Kern braeuchte 11 Prozent
                         Dehnung; zwei in der Mitte gestossene kommen
                         ohne Verformung heraus. Weil das Teil zu z = 14
                         symmetrisch ist, sind beide dasselbe Druckteil.
Kammerkern    -> +y, +z  7,5 mm hoch, dann axial heraus. Der Hub darf
                         zwischen 7,5 und 13,2 mm liegen.
Schnurkern    -> -y      Bildet nur die Schnurbohrung.

Die beiden Bohrungskerne stossen bei z = 14 stumpf aneinander und
zentrieren sich ueber zwei Zapfen im Kernmaterial. Eine Ueberblattung
quer durch die Bohrung haette ihre Passluft in der Formflaeche gehabt:
bei 0,15 mm stand am Gussteil eine Silikonmembran von 0,15 x 18 x 8 mm
quer durch die ganze Bohrung.

Reihenfolge beim Entformen
--------------------------

Haelften seitlich abziehen, beide Bohrungskerne axial herausziehen,
Schnurkern nach unten herausziehen, Kammerkern hochheben und axial
herausnehmen.

Giessen
-------

Gedruckt wird flach, Trennflaeche nach oben. Gegossen wird auf den
Fuessen stehend, Drueckerachse senkrecht, gefuellt von unten: der Lauf
fuehrt vom Trichter aussen am Teil vorbei nach unten, der Anschnitt
sitzt knapp ueber der unteren Stirnflaeche, die Entlueftung im
Rippenboden an der oberen. Fuellte man von oben, muesste die Luft aus
einem unten geschlossenen 2-mm-Ringspalt gegen das einlaufende Silikon.

Alle Kanaele liegen je zur Haelfte in beiden Formhaelften und sind
damit voll rund. Nur in einer waeren sie halbrund - und ein halbrunder
Kanal fuehrt bei gleichem Radius nur 18,9 Prozent des Stroms.

    python3 giessform_manschette.py
"""

import math

import manschette as M
from netz import (vernetzen, volumen, offene_kanten, ueberhang, abweichung,
                  schreibe_stl, schreibe_3mf, quader, zapfen, weich_vereinen)

# ---------------------------------------------------------------- Bauteil ---

LAENGE = M.LAENGE                       # 28
R_AUSSEN = M.R_AUSSEN                   # 11
R_INNEN = M.R_INNEN                     # 9
EINLAUF = M.EINLAUF                     # 1,0
RIPPE_UNTEN = M.RIPPE_UNTEN             # 18,5
Z_FUGE = LAENGE / 2.0                   # 14, Stoss der beiden Bohrungskerne

# ------------------------------------------------------------------ Form ----

X_HALB = 16.0
Y_UNTEN, Y_OBEN = -26.0, 25.0
Z_UNTEN, Z_OBEN = -6.0, 34.0

# Ueber dem Block steht nur ueber dem Lauf ein Turm, der die Giesssaeule
# traegt. Den ganzen Block hochzuziehen waere bequemer gewesen, haette
# aber die obere Stirnwand auf 16 mm gebracht - und damit die beiden
# Bohrungskerne verschieden lang gemacht. So bleiben beide Stirnwaende
# 6 mm und beide Kerne dasselbe Druckteil.
Z_TURM = 44.0

# Bohrungskern: Schaft Ø20 in der Stirnwand, dann der Einlauf auf Ø18.
SCHAFT_R = R_INNEN + EINLAUF            # 10
FUEHR_B_R = SCHAFT_R + 0.05
KNAUF_B_R = 12.0                        # bleibt unter dem Turmfuss
KNAUF_B = 4.0

# Steckverbindung der beiden Bohrungskerne. Jeder ist nur 6 mm in seiner
# Stirnwand gefuehrt, bei 24 mm Laenge - ihre Spitzen koennten an der
# Fuge um bis zu 0,5 mm gegeneinander stehen. Ineinandergesteckt halten
# sie sich gegenseitig.
#
# Entscheidend ist, wo die Passluft liegt. Eine Ueberblattung quer durch
# die Bohrung braucht Luft in der Fuge selbst - und die Fuge ist hier
# Formflaeche. Bei 0,15 mm Luft stand am Gussteil eine Silikonhaut von
# 0,15 x 18 x 8 mm quer durch die ganze Bohrung, dazu zwei 0,1 mm dicke
# Halbmonde ueber je einen halben Bohrungsquerschnitt. Das ist kein Grat
# mehr, das ist eine Membran.
#
# Deshalb stossen die Kerne jetzt auf ganzer Flaeche stumpf bei Z_FUGE
# aneinander, und die Zentrierung sitzt in zwei Zapfen, die im Kern
# selbst stecken. Die Passluft liegt damit vollstaendig im Kernmaterial;
# die Kavitaet sieht nur noch die ebene Stossfuge.
#
# Die Anordnung passt zu sich selbst: ein Zapfen bei x = +FUGE_X, eine
# Buchse bei x = -FUGE_X. Der zweite Kern ist derselbe, um 180 Grad um
# die y-Achse gedreht (x -> -x, z -> LAENGE - z) - dabei tauschen die
# beiden Seiten, und Zapfen trifft Buchse.
FUGE_X = 5.0                            # Achsabstand, bleibt in der Bohrung
FUGE_ZAPFEN_R = 1.5
FUGE_BUCHSE_R = 1.6                     # 0,1 mm Luft, im Kern verborgen
FUGE_L = 4.0

# Schnurkern. Er bildet nur noch die Schnurbohrung und zieht nach unten,
# vom Bauteil weg - deshalb darf er unten so dick sein, wie er will.
STIFT_R = M.D_SCHNUR / 2.0              # 2,5
FUEHR_S_R = STIFT_R + 0.05
KNAUF_S_R = 7.0
KNAUF_S = 4.0

# Der Schnurstift ragt 2 mm ueber den Kammerboden hinaus in ein
# Steckloch im Kammerkern. Damit traegt er ihn und haelt ihn in x und z
# fest; gegen Verdrehen legt sich der Kammerkern mit seinen beiden
# Oberkanten an die Bohrungskerne.
SOCKEL_OBEN = -14.5
SOCKEL_LUFT = 0.05

# Zentrierung: senkrechte Halbrundzapfen in den Stirnstreifen.
# Die Stirnstreifen sind nur z < 0 bzw. z > 28 breit. Rippe und Nut
# muessen deshalb vor der Stirnflaeche des Teils enden - eine Nut, die
# 0,3 mm hineinragt, schneidet eine Kerbe in den Rand des Gussteils.
# Beide sitzen unter der Rippe - im oberen Streifen liegt der Lauf, und
# in der Stirnflaeche selbst haetten sie eine Kerbe ins Gussteil
# geschnitten. Einer je Stirnseite, 28 mm auseinander; gegen Verdrehen
# um diese Linie legen sich die beiden ebenen Trennflaechen.
Y_ZENTRIER = -22.0
ZENTRIER_R, ZENTRIER_NUT_R = 2.0, 2.2
RIPPE_SPITZE = 0.5                      # Rippe endet 0,5 mm vor dem Teil
NUT_SPITZE = 0.1                        # Nut 0,4 mm laenger, setzt nicht auf

# Kanalsystem, je zur Haelfte in beiden Formhaelften.
#
# Die Masse sind nachgerechnet, nicht geschaetzt. Mit Ø5-Lauf und
# Ø4-Anschnitt lag die Fuellzeit bei 20 Pa*s Silikon bei 44 Minuten -
# mehr als die Topfzeit. Zwei Ursachen: die Kanaele machten zusammen 82
# Prozent des Stroemungswiderstands, und der Trichter endete 4 mm ueber
# der Teiloberkante, sodass am Schluss fast keine Druckhoehe mehr
# uebrig war. Jetzt Ø8 und Ø6, und ueber dem Lauf steht ein Turm, der
# den Trichter auf z = 42 hebt - am Ende bleiben damit 14 mm Saeule
# statt 4. Fuellzeit bei 20 Pa*s: 10 Minuten statt 44.
LAUF_Y = 18.5
LAUF_R = 4.0
TRICHTER_AB, TRICHTER_BIS = 40.0, 42.0
TURM_Y = 13.5                           # 1,5 mm Luft zum Kernknauf
LAUF_UNTEN = -1.0
ANSCHNITT_R = 3.0
ANSCHNITT_Z = 3.5
ANSCHNITT_BIS = 9.5                     # bis hierhin greift er ins Teil
# Die Entlueftung sass bei y = -15,5 und damit im Knotenkanal - seit der
# durchlaeuft, steckt dort der Kiel und verstopft sie. Sie liegt jetzt im
# Rippenboden zwischen Kanalboden (-16,5) und Aussenflaeche (-18,5).
ENTL_R, ENTL_Y = 1.0, -17.5

FUSS_X = (-15.0, -9.0)
FUSS_Y = ((-26.0, -20.0), (19.0, 25.0))
FUSS_Z = 6.0

SPALT = 8.0
RASTER = 0.5
DATEI_H = "tuerzwerg-giessform-manschette-haelfte-a.stl"
DATEI_H2 = "tuerzwerg-giessform-manschette-haelfte-b.stl"
DATEI_B = "tuerzwerg-giessform-manschette-kern-bohrung.stl"
DATEI_KM = "tuerzwerg-giessform-manschette-kern-kammer.stl"
DATEI_K = "tuerzwerg-giessform-manschette-kern-schnur.stl"
DATEI_3MF = "tuerzwerg-giessform-manschette.3mf"

_SCHRAEG = 0.7071067811865476


# ------------------------------------------------------------- Distanzfeld ---

def koerper(x, y, z):
    """Aussenkoerper der Manschette, ohne Bohrung, Kammer und Schnurkanal.

    Das ist der Raum, den Silikon und die drei Kerne zusammen ausfuellen.
    """
    r = math.hypot(x, y)
    profil = weich_vereinen(r - R_AUSSEN,
                            math.hypot(x, y + M.KAMMER_ACHSE) - M.R_RIPPE,
                            M.VERRUNDUNG)
    K = M.KANTE
    wq = profil + K
    wz = abs(z - Z_FUGE) - (Z_FUGE - K)
    return (min(max(wq, wz), 0.0)
            + math.hypot(max(wq, 0.0), max(wz, 0.0)) - K)


def bohrung(x, y, z):
    """Durchgangsbohrung mit den beiden 45-Grad-Einlaeufen."""
    rand = min(z, LAENGE - z)
    return math.hypot(x, y) - (R_INNEN + max(0.0, EINLAUF - rand))








def kern_bohrung(x, y, z):
    """Der untere Bohrungskern. Der obere ist dasselbe Teil, gewendet.

    Schaft, Einlauf, bis zur Fuge in der Mitte - und ein Knauf ausserhalb
    der Stirnwand zum Herausziehen.
    """
    r = math.hypot(x, y)
    rr = SCHAFT_R if z <= 0.0 else R_INNEN + max(0.0, EINLAUF - z)
    schaft = max(r - rr, Z_UNTEN - z, z - Z_FUGE)
    knauf = max(r - KNAUF_B_R, Z_UNTEN - KNAUF_B - z, z - Z_UNTEN)

    # Zapfen ueber die Stossfuge hinaus, Buchse darunter hinein.
    zapfen = max(math.hypot(x - FUGE_X, y) - FUGE_ZAPFEN_R,
                 Z_FUGE - z, z - (Z_FUGE + FUGE_L))
    buchse = max(math.hypot(x + FUGE_X, y) - FUGE_BUCHSE_R,
                 Z_FUGE - FUGE_L - z, z - Z_FUGE)
    return max(min(schaft, knauf, zapfen), -buchse)


def _kammer_roh(x, y, z):
    """Der formende Teil der Knotenkammer, ohne Stift und Knauf.

    Nicht die Kammer selbst, sondern das, was dem Aussenkoerper zum
    Bauteil fehlt, ohne die Bohrung - so sind die weichen Uebergaenge am
    Durchbruch mit im Kern.
    """
    return max(koerper(x, y, z), -M.feld(x, y, z), -bohrung(x, y, z))


def kern_kammer(x, y, z):
    """Der Kammerkern: fuellt die Knotenkammer, sonst nichts.

    Kein Stift, kein Knauf, kein Flach - alles, was frueher unter dem
    Bauteil an ihm hing und ihn dort festhielt, ist jetzt der eigene
    Schnurkern. Uebrig bleibt ein nackter Trog, 11 mm breit, 21 mm lang.

    Er wird nicht aus dem Sollprofil gebaut, sondern aus Aussenkoerper
    minus Bauteil. So traegt er die weiche Verrundung mit, mit der die
    Kammer in die Bohrung durchbricht - und genau dort zieht der Knoten.

    Entnommen wird er in zwei geraden Zuegen: gerade nach oben in die
    Bohrung, dann axial heraus. Moeglich ist das nur, weil sein
    Querschnitt ein U mit senkrechten Waenden ist - die Kammer ist an
    keiner Stelle breiter als ihre Oeffnung.
    """
    kammer = max(koerper(x, y, z), -M.feld(x, y, z), -bohrung(x, y, z))
    # Schnurbohrung und Steckloch in einem: der Stift selbst, mit
    # Passluft. Seine Senkung muss mit abgezogen werden - sonst bleibt
    # von ihr ein Kragen am Kammerkern stehen, unten an der
    # Rippenaussenflaeche, und der haelt ihn beim Ausheben fest.
    senk = min(M.SCHNUR_SENK, max(0.0, -y - (RIPPE_UNTEN - M.SCHNUR_SENK)))
    loch = max(math.hypot(x, z - Z_FUGE) - (STIFT_R + senk + SOCKEL_LUFT),
               y - SOCKEL_OBEN)
    return max(kammer, -loch)


def kern_schnur(x, y, z):
    """Der Schnurkern: ein kegeliger Stift mit Knauf, zieht nach unten.

    Er reicht 2 mm ueber den Kammerboden hinaus in ein Steckloch im
    Kammerkern und traegt ihn damit. Nach unten wird er weiter, nicht
    enger; er kommt deshalb in gerader Linie heraus, und der Knauf stoert
    dabei nicht, weil er sich vom Bauteil weg bewegt.
    """
    rs = math.hypot(x, z - Z_FUGE)
    # Die Senkung ist 0,5 mm lang, nicht unbegrenzt: ohne Deckel waechst
    # der Kegel nach unten weiter und der Stift waere am Knauf Ø21.
    senk = min(M.SCHNUR_SENK, max(0.0, -y - (RIPPE_UNTEN - M.SCHNUR_SENK)))
    stift = max(rs - (STIFT_R + senk), Y_UNTEN - y, y - SOCKEL_OBEN)
    knauf = max(rs - KNAUF_S_R, Y_UNTEN - KNAUF_S - y, y - Y_UNTEN)
    return min(stift, knauf)


def fuehrung(x, y, z):
    """Fuehrungen fuer die drei Kerne in den Stirnwaenden und der Rippe."""
    r = math.hypot(x, y)
    unten = max(r - FUEHR_B_R, Z_UNTEN - z, z - 0.0)
    oben = max(r - FUEHR_B_R, LAENGE - z, z - Z_OBEN)
    # Durchgehende Fuehrung fuer den Schnurkern bis zur Aussenflaeche.
    # Sie muss seiner Senkung folgen: unter dem Bauteil ist der Kern Ø6,
    # in einer Ø5,1-Bohrung sass er fest.
    senk = min(M.SCHNUR_SENK, max(0.0, -y - (RIPPE_UNTEN - M.SCHNUR_SENK)))
    stift = max(math.hypot(x, z - Z_FUGE) - (FUEHR_S_R + senk),
                Y_UNTEN - 1.0 - y, y + RIPPE_UNTEN - 0.5)
    return min(unten, oben, stift)


def kanal(x, y, z):
    """Trichter, Lauf, Anschnitt und Entlueftung - Rillen in x <= 0."""
    rad = math.hypot(x, y - LAUF_Y)
    if z <= TRICHTER_AB:
        d = rad - LAUF_R
    elif z <= TRICHTER_BIS:
        d = (rad - LAUF_R - (z - TRICHTER_AB)) * _SCHRAEG
    else:
        d = rad - (LAUF_R + (TRICHTER_BIS - TRICHTER_AB))
    lauf = max(d, x, LAUF_UNTEN - z)

    anschnitt = max(math.hypot(x, z - ANSCHNITT_Z) - ANSCHNITT_R,
                    x, ANSCHNITT_BIS - y, y - LAUF_Y)

    entl = max(math.hypot(x, y - ENTL_Y) - ENTL_R, x, LAENGE - z)
    return min(lauf, anschnitt, entl)


def _zentrierpaar(rollen):
    """(Rippen, Nuten) je als (y, unten?). Haelfte A hat rollen=True."""
    rippen = [(Y_ZENTRIER, True)]
    nuten = [(Y_ZENTRIER, False)]
    return (rippen, nuten) if rollen else (nuten, rippen)


def _zapfen_feld(x, y, z, y0, unten, r, spitze):
    rad = math.hypot(x, y - y0)
    if unten:
        return max(zapfen(rad, z, r, None, -spitze), Z_UNTEN - z)
    return max(zapfen(rad, z, r, LAENGE + spitze, None), z - Z_OBEN)


def haelfte(x, y, z, mit_kanaelen):
    """Signierter Abstand einer Formhaelfte. Negativ ist Material."""
    d = quader(x, y, z, -X_HALB, 0.0, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)

    turm = quader(x, y, z, -X_HALB, 0.0, TURM_Y, Y_OBEN, Z_OBEN, Z_TURM)
    d = min(d, turm)

    for y0, y1 in FUSS_Y:
        fuss = quader(x, y, z, FUSS_X[0], FUSS_X[1], y0, y1,
                      Z_UNTEN - FUSS_Z, Z_UNTEN)
        d = min(d, fuss)

    rippen, nuten = _zentrierpaar(mit_kanaelen)
    for y0, unten in nuten:
        nut = max(_zapfen_feld(x, y, z, y0, unten, ZENTRIER_NUT_R,
                               NUT_SPITZE), x)
        d = max(d, -nut)

    # Kavitaet: die Haelfte des Aussenkoerpers auf dieser Seite
    d = max(d, -max(koerper(x, y, z), x))
    d = max(d, -max(fuehrung(x, y, z), x))

    # Das Kanalsystem liegt in BEIDEN Haelften, je zur Haelfte. Nur in
    # einer waere es halbrund, und ein halbrunder Kanal fuehrt bei
    # gleichem Radius nur 18,9 Prozent des Stroms eines runden - der
    # Widerstand ist 5,28-mal so hoch. Die Fuellzeit stiege damit von
    # zehn auf rund dreissig Minuten.
    d = max(d, -kanal(x, y, z))

    for y0, unten in rippen:
        rippe = max(_zapfen_feld(x, y, z, y0, unten, ZENTRIER_R,
                                 RIPPE_SPITZE), -x)
        d = min(d, rippe)
    return d


def feld_a(x, y, z):
    return haelfte(x, y, z, True)


def feld_b(x, y, z):
    """Gegenhaelfte: gespiegelt, mit vertauschten Zentrierrollen."""
    return haelfte(-x, y, z, False)


def grenzen_halb(gespiegelt):
    x = (-ZENTRIER_R - 1.5, X_HALB + 1.5) if gespiegelt else \
        (-X_HALB - 1.5, ZENTRIER_R + 1.5)
    return (x, (Y_UNTEN - 1.5, Y_OBEN + 1.5),
            (Z_UNTEN - FUSS_Z - 1.5, Z_TURM + 1.5))


def grenzen_kern_b():
    # Bis ueber den Zapfen hinaus, nicht bis Z_FUGE - sonst schneidet das
    # Gitter den Zapfen ab und das Netz endet dort offen.
    return ((-KNAUF_B_R - 1.5, KNAUF_B_R + 1.5),
            (-KNAUF_B_R - 1.5, KNAUF_B_R + 1.5),
            (Z_UNTEN - KNAUF_B - 1.5, Z_FUGE + FUGE_L + 1.5))


def grenzen_kern_k():
    return ((-M.D_KAMMER / 2.0 - 1.5, M.D_KAMMER / 2.0 + 1.5),
            (-RIPPE_UNTEN - 1.5, -M.R_INNEN + 2.5),
            (-1.5, LAENGE + 1.5))


def grenzen_kern_s():
    return ((-KNAUF_S_R - 1.5, KNAUF_S_R + 1.5),
            (Y_UNTEN - KNAUF_S - 1.5, -M.KAMMER_ACHSE),
            (Z_FUGE - KNAUF_S_R - 1.5, Z_FUGE + KNAUF_S_R + 1.5))


# -------------------------------------------------------------- Kennzahlen --

def entformbar(schritt=0.15):
    """Erreicht jeder Kavitaetspunkt die Trennebene x = 0?

    Das ist die Bedingung dafuer, dass sich die Haelfte abziehen laesst -
    und sie ist schaerfer als die Frage nach einem einzigen Intervall.
    """
    schlimm = gepr = 0
    tiefe, wo = 0.0, None
    z = Z_UNTEN + 0.5
    while z < Z_OBEN:
        y = Y_UNTEN
        while y <= Y_OBEN:
            x, erst = -X_HALB, None
            while x <= 0.0:
                if min(max(koerper(x, y, z), x),
                       max(fuehrung(x, y, z), x)) < 0.0 and erst is None:
                    erst = x
                x += schritt
            if erst is not None:
                gepr += 1
                x, sperre = erst, 0.0
                while x <= 0.0:
                    frei = min(max(koerper(x, y, z), x),
                               max(fuehrung(x, y, z), x)) < 0.0
                    if not frei:
                        sperre += schritt
                    x += schritt
                if sperre > 0.0:
                    schlimm += 1
                    if sperre > tiefe:
                        tiefe, wo = sperre, (y, z)
            y += 0.5
        z += 1.0
    return schlimm, gepr, tiefe, wo


def kern_bohr_ziehbar(schritt=0.05):
    """Ist der Bohrungskern in seiner Zugrichtung monoton?

    Er geht nach unten heraus, sein Radius darf zur Stirnflaeche hin also
    nie kleiner werden.
    """
    fehler = 0
    z, vor = Z_FUGE, 0.0
    while z >= 0.0:
        r = R_INNEN + max(0.0, EINLAUF - min(z, LAENGE - z))
        if z < Z_FUGE and r < vor - 1e-9:
            fehler += 1
        vor = r
        z -= schritt
    return fehler


def hub_test(kernfeld, grenzen, schritt=0.25, dmax=15.0):
    """Der Kammerkern kommt in zwei geraden Zuegen heraus.

    Erst gerade nach oben, bis er ganz im Bohrungszylinder steht - was
    darin steht, laesst sich danach axial herausschieben. Geprueft wird,
    in welchem Hubbereich das gilt und ob er auf dem Weg Silikon
    durchquert.
    """
    (x0, x1), (y0, y1), (z0, z1) = grenzen
    punkte = []
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            z = z0
            while z <= z1:
                if kernfeld(x, y, z) < 0.0:
                    punkte.append((x, y, z))
                z += schritt
            y += schritt
        x += schritt

    passt = []
    d = 0.0
    while d <= dmax:
        if all(math.hypot(px, py + d) <= R_INNEN for px, py, _ in punkte):
            passt.append(d)
        d += schritt
    if not passt:
        return None, None, len(punkte), len(punkte), 0.0

    hub = passt[0]
    gesperrt, tief = 0, 0.0
    for px, py, pz in punkte:
        d, traf = schritt, False
        while d <= hub:
            v = M.feld(px, py + d, pz)
            if v < 0.0:
                traf = True
                tief = max(tief, -v)
            d += schritt
        if traf:
            gesperrt += 1
    return hub, passt[-1], len(punkte), gesperrt, tief


def zieh_test(kernfeld, grenzen, richtung, weg, schritt=0.25):
    """Kommt dieses Formteil in gerader Linie heraus?

    Die einzige Pruefung, die hier noch zaehlt. Fuer jeden Punkt des
    Teils wird der Weg in 'richtung' abgetastet; liegt darauf Silikon,
    ist der Punkt gesperrt. Kein Kippen, kein Faedeln, keine Dehnung -
    gerade heraus oder gar nicht.

    Alle frueheren Fehlschlaege waren Teile, die nur auf krummen Wegen
    herauskamen. Jeder krumme Weg hat sich als Irrtum erwiesen.
    """
    (x0, x1), (y0, y1), (z0, z1) = grenzen
    dx, dy, dz = richtung
    gesperrt, gesamt, tief = 0, 0, 0.0
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            z = z0
            while z <= z1:
                if kernfeld(x, y, z) < 0.0:
                    gesamt += 1
                    d, traf = schritt, False
                    while d <= weg:
                        v = M.feld(x + dx * d, y + dy * d, z + dz * d)
                        if v < 0.0:
                            traf = True
                            tief = max(tief, -v)
                        d += schritt
                    if traf:
                        gesperrt += 1
                z += schritt
            y += schritt
        x += schritt
    return gesperrt, gesamt, tief


def kavitaet_volumen(schritt=0.3):
    v, zelle = 0.0, schritt ** 3
    x = -R_AUSSEN
    while x <= R_AUSSEN:
        y = -RIPPE_UNTEN
        while y <= R_AUSSEN:
            z = 0.0
            while z <= LAENGE:
                if M.feld(x, y, z) < 0.0:
                    v += zelle
                z += schritt
            y += schritt
        x += schritt
    return v


def fuellweg(schritt=0.5):
    """Flutet die geschlossene Form vom Trichter aus."""
    def frei(x, y, z):
        if min(feld_a(x, y, z), feld_b(x, y, z)) <= 0.05:
            return False
        return (kern_bohrung(x, y, z) > 0.05
                and kern_bohrung(-x, y, LAENGE - z) > 0.05
                and kern_kammer(x, y, z) > 0.05
                and kern_schnur(x, y, z) > 0.05)

    def auf(v):
        return (round(v / schritt - 0.5) + 0.5) * schritt

    def idx(p):
        return tuple(round(c / schritt - 0.5) for c in p)

    start = tuple(auf(c) for c in (-0.5 * schritt, LAUF_Y, Z_TURM - 0.8))
    gesehen, stapel = {idx(start)}, [start]
    while stapel:
        p = stapel.pop()
        for d in ((schritt, 0, 0), (-schritt, 0, 0), (0, schritt, 0),
                  (0, -schritt, 0), (0, 0, schritt), (0, 0, -schritt)):
            q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if not (-X_HALB < q[0] < X_HALB and Y_UNTEN < q[1] < Y_OBEN
                    and Z_UNTEN < q[2] < Z_TURM):
                continue
            k = idx(q)
            if k in gesehen or not frei(*q):
                continue
            gesehen.add(k)
            stapel.append(q)

    ges = err = 0
    x = auf(-R_AUSSEN)
    while x <= R_AUSSEN:
        y = auf(-RIPPE_UNTEN)
        while y <= R_AUSSEN:
            z = auf(0.0)
            while z <= LAENGE:
                if M.feld(x, y, z) < -0.4:
                    ges += 1
                    if idx((x, y, z)) in gesehen:
                        err += 1
                z += schritt
            y += schritt
        x += schritt
    entl = idx(tuple(auf(c) for c in
                     (-0.5 * schritt, ENTL_Y, Z_OBEN - 0.8))) in gesehen
    return err, ges, entl


def engste_wand(schritt=0.4):
    """Duennste Formwand zwischen Kavitaet und Lauf, Nut oder Aussenflaeche."""
    def wandfeld(x, y, z):
        d = quader(x, y, z, -X_HALB, 1e4, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)
        lauf = max(math.hypot(x, y - LAUF_Y) - LAUF_R, x, LAUF_UNTEN - z)
        d = max(d, -lauf)
        for y0, unten in _zentrierpaar(True)[1]:
            nut = max(_zapfen_feld(x, y, z, y0, unten,
                                   ZENTRIER_NUT_R, NUT_SPITZE), x)
            d = max(d, -nut)
        return d

    best = (1e9, None)
    x = -R_AUSSEN - 1.0
    while x <= 0.0:
        y = -RIPPE_UNTEN - 1.0
        while y <= R_AUSSEN + 1.0:
            z = -0.5
            while z <= LAENGE + 0.5:
                if abs(koerper(x, y, z)) < 0.2:
                    w = -wandfeld(x, y, z)
                    if 0.0 < w < best[0]:
                        best = (w, (x, y, z))
                z += schritt
            y += schritt
        x += schritt
    return best


if __name__ == "__main__":
    print("Vernetze Haelfte A ...")
    tri_a = vernetzen(feld_a, grenzen_halb(False), RASTER)
    print("Vernetze Haelfte B ...")
    tri_b = vernetzen(feld_b, grenzen_halb(True), RASTER)
    print("Vernetze Bohrungskern ...")
    tri_bk = vernetzen(kern_bohrung, grenzen_kern_b(), RASTER * 0.6)
    print("Vernetze Kammerkern ...")
    tri_km = vernetzen(kern_kammer, grenzen_kern_k(), RASTER * 0.6)
    print("Vernetze Schnurkern ...")
    tri_kk = vernetzen(kern_schnur, grenzen_kern_s(), RASTER * 0.6)

    def richte(tri):
        v = volumen(tri)
        if v < 0:
            return [(a, c, b) for a, b, c in tri], -v
        return tri, v

    tri_a, vol_a = richte(tri_a)
    tri_b, vol_b = richte(tri_b)
    tri_bk, vol_bk = richte(tri_bk)
    tri_km, vol_km = richte(tri_km)
    tri_kk, vol_kk = richte(tri_kk)

    ab_max, ab_mit = abweichung(feld_a, tri_a)

    # Drucklage. Die Haelften legen sich flach, Trennflaeche nach oben:
    # Drehung um die y-Achse, (x, y, z) -> (z, y, -x). Echte Drehung,
    # die Wicklung bleibt richtig.
    # Beide Haelften legen sich flach mit der Trennflaeche nach OBEN.
    # Haelfte A wird dazu um -90 Grad um die y-Achse gedreht, Haelfte B um
    # +90 Grad; beides sind echte Drehungen, die Wicklung bleibt richtig.
    def flach_a(tri):
        return [tuple((Z_TURM - p[2], p[1] - Y_UNTEN, p[0] + X_HALB)
                      for p in t) for t in tri]

    def flach_b(tri):
        return [tuple((p[2] - Z_UNTEN + FUSS_Z, p[1] - Y_UNTEN,
                       X_HALB - p[0]) for p in t) for t in tri]

    a_druck = flach_a(tri_a)
    b_druck = flach_b(tri_b)
    # Bohrungskern steht auf dem Knauf
    bk_druck = [tuple((p[0], p[1], p[2] - (Z_UNTEN - KNAUF_B)) for p in t)
                for t in tri_bk]
    # Kammerkern steht auf dem Knauf. Drehung um 90 Grad um die x-Achse:
    # (x, y, z) -> (x, -z, y). Das ist eine echte Drehung, die Wicklung
    # bleibt richtig - eine Korrektur wuerde sie umkehren.
    kk_druck = [tuple((p[0], Z_FUGE - p[2], p[1] - (Y_UNTEN - KNAUF_S))
                      for p in t) for t in tri_kk]
    # Kammerkern liegt auf dem Ruecken - seine runde Unterseite wird
    # dadurch zur Kuppel und braucht keine Stuetze. Drehung um 180 Grad
    # um die z-Achse: (x, y, z) -> (-x, -y, z), eine echte Drehung.
    km_druck = [tuple((-p[0], -(p[1] + M.KAMMER_ACHSE) + M.D_KAMMER / 2.0,
                       p[2]) for p in t) for t in tri_km]

    schreibe_stl(a_druck, DATEI_H, "Tuerzwerg Manschette Haelfte A - mm")
    schreibe_stl(b_druck, DATEI_H2, "Tuerzwerg Manschette Haelfte B - mm")
    schreibe_stl(bk_druck, DATEI_B, "Tuerzwerg Manschette Bohrungskern - mm")
    schreibe_stl(km_druck, DATEI_KM, "Tuerzwerg Manschette Kammerkern - mm")
    schreibe_stl(kk_druck, DATEI_K, "Tuerzwerg Manschette Schnurkern - mm")

    schreibe_3mf(
        [("Haelfte A", a_druck, (35.0, 35.0, 0.0)),
         ("Haelfte B", b_druck, (35.0, 92.0, 0.0)),
         ("Bohrungskern 1", bk_druck, (95.0, 40.0, 0.0)),
         ("Bohrungskern 2", bk_druck, (125.0, 40.0, 0.0)),
         ("Kammerkern", km_druck, (105.0, 78.0, 0.0)),
         ("Schnurkern", kk_druck, (142.0, 80.0, 0.0))],
        DATEI_3MF, "Tuerzwerg Giessform Manschette",
        "Beide Haelften flach mit der Trennflaeche nach oben, alle drei "
        "Kerne stehend auf ihren Knaeufen. PLA, 0,2 mm Schicht, "
        "mindestens 4 Perimeter, 30 Prozent Infill, keine Stuetzen.")

    anteil, grad, flaeche = ueberhang(a_druck)
    kav = kavitaet_volumen()
    s, n, t, sw = entformbar()
    fb = kern_bohr_ziehbar()
    zb_s, zb_g, zb_t = zieh_test(kern_bohrung, grenzen_kern_b(),
                                 (0.0, 0.0, -1.0), LAENGE + 2.0)
    zs_s, zs_g, zs_t = zieh_test(kern_schnur, grenzen_kern_s(),
                                 (0.0, -1.0, 0.0), 12.0)
    hub, hub_max, hg, hs, ht = hub_test(kern_kammer, grenzen_kern_k())
    err, ges, entl = fuellweg()
    wand, wo = engste_wand()

    print(f"\nDateien         {DATEI_3MF}  <- alles in einer Datei")
    print(f"Eine Haelfte    {Z_OBEN-Z_UNTEN+FUSS_Z:.0f} x {Y_OBEN-Y_UNTEN:.0f}"
          f" x {X_HALB:.0f} mm")
    print(f"Bohrungskern    2 x gleich, {Z_FUGE-Z_UNTEN+KNAUF_B:.0f} mm lang, "
          f"{vol_bk/1000:.1f} cm^3")
    print(f"Kammerkern      1 x, {vol_km/1000:.1f} cm^3")
    print(f"Schnurkern      1 x, {vol_kk/1000:.1f} cm^3")
    print(f"Dreiecke        {len(a_druck)} + {len(b_druck)} + "
          f"{len(bk_druck)} + {len(km_druck)} + {len(kk_druck)}")
    print(f"Offene Kanten   A {offene_kanten(a_druck)}, B {offene_kanten(b_druck)}, "
          f"Bohrkern {offene_kanten(bk_druck)}, Kammerkern "
          f"{offene_kanten(km_druck)}, Schnurkern {offene_kanten(kk_druck)}")
    print(f"Bauteil         {kav/1000:.2f} cm^3 ({kav/1000*1.15:.1f} g Silikon)")
    print(f"Entformbar      {s} von {n} Saeulen gesperrt"
          + (f", bis {t:.1f} mm bei y={sw[0]:.0f} z={sw[1]:.0f}" if sw
             else "  (0 = Haelfte laesst sich abziehen)"))

    print(f"Geradeaus heraus (0 gesperrt = kein Hinterschnitt):")
    print(f"  Haelfte  -> x  {s} von {n} Saeulen gesperrt")
    print(f"  Bohrkern -> z  {zb_s} von {zb_g} Punkten gesperrt"
          + (f", bis {zb_t:.2f} mm tief" if zb_s else ""))
    print(f"  Schnurkern -> y {zs_s} von {zs_g} Punkten gesperrt"
          + (f", bis {zs_t:.2f} mm tief" if zs_s else ""))
    if hub is None:
        print("Kammerkern      passt NIE ganz in die Bohrung")
    else:
        print(f"Kammerkern      erst {hub:.1f} mm hoch, dann axial heraus "
              f"(Hub {hub:.1f} bis {hub_max:.1f} mm moeglich)")
        print(f"  dabei         {hs} von {hg} Punkten mit Silikonkontakt"
              + (f", bis {ht:.2f} mm tief" if hs else ""))
    print(f"Fuellweg        {100.0*err/ges:.1f} % der Kavitaet erreichbar, "
          f"Entlueftung {'an' if entl else 'AB'}")
    print(f"Duennste Wand   {wand:.1f} mm"
          + (f" bei x={wo[0]:.0f} y={wo[1]:.0f} z={wo[2]:.0f}" if wo else ""))
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm (Kerne {RASTER*0.6:.2f} mm)")
