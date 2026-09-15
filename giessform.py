#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer den Griff (Kehle, Schaft 15, Kehle 13)

Vier Teile: zwei gleiche Formhaelften und zwei lose Kerne.

Warum die erste Fassung nicht aufging.

Sie hatte Bohrung und Knotenkammer als Halbkerne in den Haelften selbst.
Das laesst sich giessen, aber nicht mehr oeffnen: der Kern sitzt genau
zwischen dem Silikon und der Trennebene. Wer die Haelfte abzieht, zieht
den Kern quer durch die Bohrungswand. entformbar() rechnet es nach - in
der alten Fassung kamen 724 von 2486 Materialsaeulen nicht zur Trenn-
ebene, bis zu 6 mm versperrt.

Der Denkfehler steckte in der Pruefung, nicht im Entwurf: gepruef wurde,
ob das Material je Stelle ein einziges Intervall bildet. Das ist nicht
dasselbe wie die Frage, ob es die Trennebene erreicht. Ein Rohr erfuellt
das erste und verletzt das zweite.

Jetzt formen die Haelften nur die Aussenflaeche. Der Griff ist ein
Drehkoerper; von jedem Punkt seiner Aussenhaelfte nimmt der Radius zur
Trennebene hin ab, also liegt nie Formmaterial im Weg. Die Haelften
gehen auf, ohne dass irgendetwas verformt werden muss.

Warum zwei Kerne und nicht einer.

Die Bohrung ist nicht monoton: 8,2 mm Trichter an der Kuppe, 5 mm
Schaft, 12 mm Knotenkammer am Boden. Ein einteiliger Kern kaeme in
keiner Richtung heraus - nach unten sperrt der Trichter, nach oben die
Kammer. Geteilt wird deshalb an der engsten Stelle, am Uebergang vom
Schaft zum Trichter bei h = 1,6 mm. Jede Haelfte ist in ihrer eigenen
Zugrichtung monoton:

    Kern unten   Kammer 12 -> Kegel -> Schaft 5, wird nach oben
                 durch die Bodenflaeche herausgezogen
    Kern oben    Trichter 8,2 -> 5, wird nach unten durch den
                 Deckel herausgezogen

Beide sind im Block gefuehrt, der untere in einer 12,1er Bohrung im
Kopfstueck, der obere in einer 8,3er im Deckel. Ihre Knaeufe sitzen
aussen auf und legen damit zugleich die Tiefe fest.

Gedruckt wird flach liegend, Trennflaeche nach oben. Das geht erst,
seit die Kerne draussen sind - ein angeformter Bohrungskern waere in
dieser Lage eine 90 mm lange schwebende Bruecke gewesen. Jetzt hat die
Haelfte ueberhaupt keine ueberhaengende Flaeche mehr: die Kavitaet
wird nach oben hin nur breiter, und Rillen und Nuten oeffnen sich alle
zur Oberseite.

Gegossen wird auf den Fuessen stehend, Kuppe unten, Bodenflaeche oben.
Angegossen und entlueftet wird durch zwei gleiche Kanaele am Rand der
Bodenflaeche - gleich deshalb, weil die Haelfte sonst nicht mehr zu
sich selbst passte.

    python3 giessform.py
"""

import math

import griffe as G
from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, schreibe_3mf, quader, zapfen)

# ---------------------------------------------------------------- Bauteil ---

VARIANTE = "kehle"
PROFIL = G.VARIANTEN[VARIANTE]["profil"]
BOHR = G.VARIANTEN[VARIANTE]["bohr"]
HOEHE = PROFIL.hoehe                    # 90 mm

# z = 0 ist die Bodenflaeche des Griffs, z = HOEHE die Kuppe.
KOPF = 8.0                              # Block ueber der Bodenflaeche
DECKEL = 6.0                            # Block unter der Kuppe
Z_OBEN = HOEHE + DECKEL                 # 96
Z_KOPF = -KOPF                          # -8

# Teilung der beiden Kerne: die engste Stelle der Bohrung.
H_TRICHTER = G.R_EINLAUF                # 1,6 mm unter der Kuppe
Z_FUGE = HOEHE - H_TRICHTER             # 88,4

# ------------------------------------------------------------------ Form ----

X_HALB = 28.0
Y_TIEF = 23.0

RIPPE_X = 23.0
RIPPE_R = 3.0
NUT_R = 3.2                             # 0,2 mm Luft
RIPPE_Z = (-7.0, 95.0)                  # Spitzen der Auslaufkegel
NUT_Z = 95.2

# Anguss und Entlueftung. Beide gleich gross und spiegelbildlich zur
# Achse - sonst passte die um 180 Grad gedrehte Haelfte nicht mehr zu
# sich selbst. Gegossen wird durch den einen, beobachtet am anderen.
KANAL_X = 11.0
KANAL_R = 2.5
TRICHTER_AB = -5.0                      # ab hier oeffnet sich der Kanal

# Fuehrungen fuer die Kerne
FUEHR_U_R = 6.05                        # 12,1 fuer den 12er Schaft
FUEHR_O_R = 4.15                        # 8,3 fuer den 8,2er Schaft

# Knaeufe: sie sitzen aussen auf dem Block auf und legen damit zugleich
# die Eintauchtiefe der Kerne fest.
KNAUF_R = 9.0                           # runder Knauf des oberen Kerns
KNAUF_U_Z = (Z_KOPF - 6.0, Z_KOPF)      # -14 .. -8, oben auf dem Kopfstueck
KNAUF_O_Z = Z_OBEN + 4.0                # 100, unter dem Deckel

# Der untere Kern bekommt keinen runden Knauf, sondern einen schmalen
# Steg quer zu den beiden Kanaelen. Ein Ø18-Knauf haette ein Drittel
# jeder Eingussoeffnung verdeckt - die Trichter reichen bis x = 5,6
# heran. Zwei Stifte legen die Lage des Stegs fest, sonst koennte man
# ihn quer aufsetzen und beide Oeffnungen zudecken.
STEG_X = 6.5                            # halbe Breite, laesst die Trichter frei
STEG_Y = 19.0                           # halbe Laenge, greift ausserhalb
STIFT_Y = 16.0
STIFT_R = 1.5
STIFT_TIEF = 3.0

# Fuesse, damit der Knauf des oberen Kerns beim Giessen frei liegt.
FUSS_X = (20.0, 28.0)
FUSS_Y = (-23.0, -15.0)
FUSS_Z = 6.0

RASTER = 0.6
DATEI_H = "tuerzwerg-giessform-griff-haelfte.stl"
DATEI_U = "tuerzwerg-giessform-griff-kern-unten.stl"
DATEI_O = "tuerzwerg-giessform-griff-kern-oben.stl"
DATEI_3MF = "tuerzwerg-giessform-griff.3mf"


# ------------------------------------------------------------- Distanzfeld ---

def aussen(z):
    """Aussenradius des Griffs auf der Hoehe z."""
    h = min(max(HOEHE - z, 0.0), HOEHE)
    return PROFIL(h)[0]


def innen(z):
    """Bohrungsradius auf der Hoehe z."""
    h = min(max(HOEHE - z, 0.0), HOEHE)
    return BOHR(h)


def kavitaet(x, y, z):
    """Der Griff als Vollkoerper, ohne Bohrung und Kammer.

    Die fuellen die beiden losen Kerne aus; zusammen ergeben Silikon und
    Kerne genau diesen Raum.
    """
    return max(math.hypot(x, y) - aussen(z), z - HOEHE, -z)


def kern_unten(x, y, z):
    """Kammer, Kegel, Schaft und Knauf. Wird nach oben herausgezogen."""
    r = math.hypot(x, y)
    rr = innen(0.0) if z <= 0.0 else innen(z)   # 6,0 in der Fuehrung
    schaft = max(r - rr, Z_KOPF - z, z - Z_FUGE)
    steg = quader(x, y, z, -STEG_X, STEG_X, -STEG_Y, STEG_Y,
                  KNAUF_U_Z[0], Z_KOPF)
    aus = min(schaft, steg)
    for vz in (1.0, -1.0):
        stift = max(math.hypot(x, y - vz * STIFT_Y) - STIFT_R,
                    Z_KOPF - z, z - (Z_KOPF + STIFT_TIEF))
        aus = min(aus, stift)
    return aus


def kern_oben(x, y, z):
    """Trichter, Schaft und Knauf. Wird nach unten herausgezogen."""
    r = math.hypot(x, y)
    trichter = max(r - innen(z), Z_FUGE - z, z - HOEHE)
    schaft = max(r - innen(HOEHE), HOEHE - z, z - Z_OBEN)
    knauf = max(r - KNAUF_R, Z_OBEN - z, z - KNAUF_O_Z)
    return min(trichter, schaft, knauf)


def kanal(x, y, z):
    """Zwei gleiche Rillen in der Trennflaeche, am Rand der Bodenflaeche."""
    aus = 1e9
    for vz in (1.0, -1.0):
        rad = math.hypot(x - vz * KANAL_X, y)
        if z >= TRICHTER_AB:
            d = rad - KANAL_R
        else:
            d = (rad - KANAL_R - (TRICHTER_AB - z)) * 0.70710678
        # 1 mm in die Kavitaet hinein, damit der Kanal sie wirklich
        # schneidet und nicht nur beruehrt.
        aus = min(aus, max(d, Z_KOPF - z, z - 1.0, y))
    return aus


def fuehrung(x, y, z):
    """Bohrungen fuer die beiden Kernschaefte."""
    r = math.hypot(x, y)
    unten = max(r - FUEHR_U_R, Z_KOPF - z, z - 0.0)
    oben = max(r - FUEHR_O_R, HOEHE - z, z - Z_OBEN)
    return min(unten, oben)


def haelfte(x, y, z):
    """Signierter Abstand einer Formhaelfte. Negativ ist Material.

    Material liegt bei y <= 0, die Zentrierrippe steht nach y > 0 vor.
    Beide Haelften sind dasselbe Teil; die zweite wird um 180 Grad um
    die Hochachse gedreht aufgesetzt.
    """
    d = quader(x, y, z, -X_HALB, X_HALB, -Y_TIEF, 0.0, Z_KOPF, Z_OBEN)

    # Fuesse
    for x0, x1 in ((FUSS_X[0], FUSS_X[1]), (-FUSS_X[1], -FUSS_X[0])):
        fuss = quader(x, y, z, x0, x1, FUSS_Y[0], FUSS_Y[1],
                      Z_OBEN, Z_OBEN + FUSS_Z)
        d = min(d, fuss)

    # Kavitaet, Kernfuehrungen und Kanaele
    d = max(d, -max(kavitaet(x, y, z), y))
    d = max(d, -max(fuehrung(x, y, z), y))
    d = max(d, -kanal(x, y, z))

    # Loch fuer den Lagestift des unteren Kerns. Nur eines je Haelfte;
    # die gedrehte Gegenhaelfte liefert das zweite.
    loch = max(math.hypot(x, y + STIFT_Y) - (STIFT_R + 0.2),
               Z_KOPF - z, z - (Z_KOPF + STIFT_TIEF + 0.5))
    d = max(d, -loch)

    # Zentriernut, in die eigene Haelfte geschnitten
    nut = max(zapfen(math.hypot(x + RIPPE_X, y), z, NUT_R, None, NUT_Z), y)
    d = max(d, -nut)

    # Zentrierrippe, steht in die Gegenhaelfte hinein
    rippe = max(zapfen(math.hypot(x - RIPPE_X, y), z, RIPPE_R,
                       RIPPE_Z[0], RIPPE_Z[1]), -y)
    return min(d, rippe)


def grenzen_haelfte():
    return ((-X_HALB - 1.5, X_HALB + 1.5),
            (-Y_TIEF - 1.5, RIPPE_R + 1.5),
            (Z_KOPF - 1.5, Z_OBEN + FUSS_Z + 1.5))


def grenzen_kern_u():
    # Steg und Lagestifte reichen weiter als der Schaft - die Grenzen
    # muessen sie einschliessen, sonst endet das Netz an der Gitterkante
    # offen.
    return ((-STEG_X - 1.5, STEG_X + 1.5),
            (-STEG_Y - 1.5, STEG_Y + 1.5),
            (KNAUF_U_Z[0] - 1.5, Z_FUGE + 1.5))


def grenzen_kern_o():
    return ((-KNAUF_R - 1.5, KNAUF_R + 1.5),
            (-KNAUF_R - 1.5, KNAUF_R + 1.5),
            (Z_FUGE - 1.5, KNAUF_O_Z + 1.5))


# -------------------------------------------------------------- Kennzahlen --

def entformbar(schritt=0.15):
    """Erreicht jeder Kavitaetspunkt die Trennebene?

    Das ist die Bedingung dafuer, dass sich die Haelfte abziehen laesst,
    und sie ist schaerfer als die Frage nach einem einzigen Intervall:
    ein Rohr belegt ein einziges Intervall und kommt trotzdem nicht frei.
    Geprueft wird die fertige Kavitaet einschliesslich der Kernschaefte,
    denn die gehoeren beim Oeffnen nicht mehr zur Haelfte.
    """
    schlimm = gepr = 0
    tiefe, wo = 0.0, None
    z = Z_KOPF + 0.5
    while z < Z_OBEN:
        x = -X_HALB
        while x <= X_HALB:
            y, erst = -Y_TIEF, None
            while y <= 0.0:
                if min(max(kavitaet(x, y, z), y),
                       max(fuehrung(x, y, z), y)) < 0.0 and erst is None:
                    erst = y
                y += schritt
            if erst is not None:
                gepr += 1
                y, sperre = erst, 0.0
                while y <= 0.0:
                    frei = min(max(kavitaet(x, y, z), y),
                               max(fuehrung(x, y, z), y)) < 0.0
                    if not frei:
                        sperre += schritt
                    y += schritt
                if sperre > 0.0:
                    schlimm += 1
                    if sperre > tiefe:
                        tiefe, wo = sperre, (x, z)
            x += 0.5
        z += 1.5
    return schlimm, gepr, tiefe, wo


def kern_ziehbar(schritt=0.2):
    """Sind beide Kerne in ihrer Zugrichtung monoton?

    Der untere geht nach oben heraus, sein Radius darf zur Bodenflaeche
    hin also nie kleiner werden; der obere geht nach unten und darf zur
    Kuppe hin nie kleiner werden.
    """
    fehler_u = fehler_o = 0
    z, vor = 0.0, 0.0
    while z <= Z_FUGE:                  # unterer Kern, Blick von z = 0 aufwaerts
        r = innen(z)
        if z > 0.0 and r > vor + 1e-9:
            fehler_u += 1
        vor = r
        z += schritt
    z, vor = HOEHE, 0.0
    while z >= Z_FUGE:                  # oberer Kern, Blick von der Kuppe abwaerts
        r = innen(z)
        if z < HOEHE and r > vor + 1e-9:
            fehler_o += 1
        vor = r
        z -= schritt
    return fehler_u, fehler_o


def kavitaet_volumen(n=4000):
    """Silikon je Guss: Aussenkoerper minus beide Kerne."""
    v = 0.0
    for i in range(n):
        h = HOEHE * (i + 0.5) / n
        v += math.pi * (PROFIL(h)[0] ** 2 - BOHR(h) ** 2) * HOEHE / n
    return v


def engste_wand():
    """Duennste Formwand zwischen Kavitaet und Aussenkante oder Kanal."""
    best = (1e9, None)
    for i in range(901):
        z = Z_KOPF + (Z_OBEN - Z_KOPF) * i / 900.0
        if not (0.0 <= z <= HOEHE):
            continue
        r = aussen(z)
        # Der Kanal bleibt aussen vor: er reicht nur bis z = 1 und
        # muendet dort absichtlich in den Rand der Bodenflaeche.
        for wand, wo in ((X_HALB - r, "seitlich"), (Y_TIEF - r, "hinten")):
            if 0.0 < wand < best[0]:
                best = (wand, (wo, z))
    return best


if __name__ == "__main__":
    print("Vernetze Haelfte ...")
    tri_h = vernetzen(haelfte, grenzen_haelfte(), RASTER)
    print("Vernetze Kern unten ...")
    tri_u = vernetzen(kern_unten, grenzen_kern_u(), RASTER * 0.5)
    print("Vernetze Kern oben ...")
    tri_o = vernetzen(kern_oben, grenzen_kern_o(), RASTER * 0.5)

    def richte(tri):
        v = volumen(tri)
        if v < 0:
            return [(a, c, b) for a, b, c in tri], -v
        return tri, v

    tri_h, vol_h = richte(tri_h)
    tri_u, vol_u = richte(tri_u)
    tri_o, vol_o = richte(tri_o)

    ab_max, ab_mit = abweichung(haelfte, tri_h)

    # Drucklage. Die Haelfte legt sich flach, Trennflaeche nach oben:
    # Drehung um die x-Achse, (x, y, z) -> (x, -z, y). Das ist eine echte
    # Drehung, die Wicklung bleibt richtig.
    def flach(tri):
        return [tuple((p[0], 102.0 - p[2], p[1] + Y_TIEF) for p in t)
                for t in tri]

    def stehend(tri, dz):
        return [tuple((p[0], p[1], p[2] + dz) for p in t) for t in tri]

    def kopf_unten(tri, z0):
        # 180 Grad um die x-Achse, damit der Knauf auf dem Bett liegt
        return [tuple((p[0], -p[1], z0 - p[2]) for p in t) for t in tri]

    h_druck = flach(tri_h)
    u_druck = stehend(tri_u, -KNAUF_U_Z[0])
    o_druck = kopf_unten(tri_o, KNAUF_O_Z)

    schreibe_stl(h_druck, DATEI_H, "Tuerzwerg Giessform Griff Haelfte - mm")
    schreibe_stl(u_druck, DATEI_U, "Tuerzwerg Giessform Griff Kern unten - mm")
    schreibe_stl(o_druck, DATEI_O, "Tuerzwerg Giessform Griff Kern oben - mm")

    schreibe_3mf(
        [("Formhaelfte 1", h_druck, (40.0, 60.0, 0.0)),
         ("Formhaelfte 2", h_druck, (105.0, 60.0, 0.0)),
         ("Kern unten", u_druck, (160.0, 60.0, 0.0)),
         ("Kern oben", o_druck, (185.0, 60.0, 0.0))],
        DATEI_3MF, "Tuerzwerg Giessform Griff Kehle",
        "Zwei gleiche Haelften flach mit der Trennflaeche nach oben, "
        "beide Kerne stehend. PLA, 0,2 mm Schicht, mindestens 4 "
        "Perimeter, 30 Prozent Infill, keine Stuetzen. Den langen Kern "
        "langsam drucken.")

    anteil, grad, flaeche = ueberhang(h_druck)
    kav = kavitaet_volumen()
    wand, wo = engste_wand()
    s, n, t, sw = entformbar()
    fu, fo = kern_ziehbar()

    print(f"\nDateien         {DATEI_3MF}  <- alles in einer Datei")
    print(f"                {DATEI_H}, {DATEI_U}, {DATEI_O}")
    print(f"Eine Haelfte    {2*X_HALB:.0f} x {Y_TIEF:.0f} x "
          f"{Z_OBEN + FUSS_Z - Z_KOPF:.0f} mm")
    print(f"Zusammengesetzt {2*X_HALB:.0f} x {2*Y_TIEF:.0f} x "
          f"{Z_OBEN + FUSS_Z - Z_KOPF:.0f} mm")
    print(f"Kern unten      {Z_FUGE - KNAUF_U_Z[0]:.0f} mm lang, "
          f"{vol_u/1000:.1f} cm^3")
    print(f"Kern oben       {KNAUF_O_Z - Z_FUGE:.0f} mm lang, "
          f"{vol_o/1000:.1f} cm^3")
    print(f"Dreiecke        {len(h_druck)} + {len(u_druck)} + {len(o_druck)}")
    print(f"Offene Kanten   Haelfte {offene_kanten(h_druck)}, "
          f"Kern unten {offene_kanten(u_druck)}, "
          f"Kern oben {offene_kanten(o_druck)}")
    print(f"Formvolumen     {vol_h/1000:.0f} cm^3 je Haelfte")
    print(f"Kavitaet        {kav/1000:.1f} cm^3 Silikon je Guss "
          f"({kav/1000*1.15:.0f} g)")
    print(f"Entformbar      {s} von {n} Saeulen gesperrt"
          + (f", bis {t:.1f} mm bei x={sw[0]:.0f} z={sw[1]:.0f}" if sw
             else "  (0 = Haelfte laesst sich abziehen)"))
    print(f"Kerne monoton   unten {fu} Verstoesse, oben {fo} "
          f"(je 0 = laesst sich ziehen)")
    print(f"Duennste Wand   {wand:.1f} mm {wo[0]}, bei z = {wo[1]:.0f}")
    print(f"Zentrierung     Rippe {2*RIPPE_R:.0f} gegen Nut {2*NUT_R:.1f} mm, "
          f"{NUT_R-RIPPE_R:.1f} mm Luft")
    weit = 0.0
    while kanal(KANAL_X + weit, -0.01, Z_KOPF + 0.1) < 0.0:
        weit += 0.01
    print(f"Kanaele         2 x {2*KANAL_R:.0f} mm am Rand der Bodenflaeche, "
          f"Muendung {2*weit:.1f} mm")
    print(f"Einguss frei    von x = {KANAL_X - weit:.1f} bis "
          f"{KANAL_X + weit:.1f}, Steg reicht bis {STEG_X:.1f}")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm (Kerne {RASTER*0.5:.2f} mm)")
