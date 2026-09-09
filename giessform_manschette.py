#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer die Klinkenmanschette

Zweiteilige Steckform zum Ausgiessen mit Silikon, gedacht fuer den FDM-Druck.

Warum die Form anders aussieht als die des Griffs:

Teilung durch die Symmetrieebene. Die Manschette ist kein Drehkoerper,
aber sie ist spiegelsymmetrisch zur Ebene x = 0 - Rohr, Rippe, Kammer und
Schnurbohrung liegen alle darauf. Genau diese Ebene ist die einzige, in
der die Form hinterschnittfrei aufgeht. Nachgerechnet wird das unten in
hinterschnitt(): fuer jede Hoehe und jede Querlage darf das Material in
einer Haelfte nur ein einziges Intervall in x belegen. Zwei Intervalle
hiessen Hinterschnitt, und die Haelfte liesse sich nicht abziehen.

Drei Kerne, alle angebunden. Die Durchgangsbohrung wird von zwei
Halbkernen gebildet, die in den Stirnwaenden der Form stehen; die
Knotenkammer haengt ueber den Schlitz, mit dem sie in die Bohrung
durchbricht, am Bohrungskern; der Schnurkanal verbindet die Kammer
zusaetzlich mit dem Aussenblock. Kein Kern schwebt.

Gedruckt und gegossen wird hochkant, Drueckerachse senkrecht. Damit
stehen alle drei Kerne aufrecht auf der unteren Stirnwand und sind ueber
die volle Hoehe gestuetzt. Laege die Form flach, waere der Bohrungskern
eine 28 mm lange Bruecke mit runder Unterseite - nicht druckbar ohne
Stuetzen mitten in der Kavitaet.

Zwei verschiedene Haelften, nicht zweimal dieselbe. Beim Griff genuegte
eine Datei, weil die zweite Haelfte nur gedreht werden musste. Hier sind
die Haelften Spiegelbilder, und ein gedrucktes Teil laesst sich nicht
spiegeln. Man koennte die Drehsymmetrie der Manschette (sie ist auch zu
z = 14 symmetrisch) ausnutzen - dann muesste der Anguss aber an beiden
Enden sitzen, und das untere Loch waere beim Giessen ein Leck. Also zwei
Haelften, beide in dieser einen Datei, nebeneinander auf dem Bett.

Anguss und Entlueftung liegen in der Trennebene, jede Haelfte traegt die
Haelfte davon. Angegossen wird auf die Stirnflaeche der Rippe - die
groesste ebene Flaeche des Teils und die am wenigsten sichtbare. Die
Entlueftung sitzt am hoechsten Punkt des Rohrquerschnitts; sie zeigt an,
wann die Form voll ist. Entlueften wuerde die Form auch ohne sie, weil
die Kavitaetsdecke auf ganzer Laenge an der Trennebene liegt.

    python3 giessform_manschette.py
"""

import math

import manschette as M
from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, quader, zapfen)

# ---------------------------------------------------------------- Bauteil ---

LAENGE = M.LAENGE                   # 28 mm, Drueckerachse = z
Y_OBEN_TEIL = M.R_AUSSEN            # 11
Y_UNTEN_TEIL = -M.RIPPE_UNTEN       # -18,5

# ------------------------------------------------------------------ Form ----

X_HALB = 16.0                       # Tiefe einer Haelfte hinter der Trennebene
Y_UNTEN, Y_OBEN = -25.5, 18.0
Z_UNTEN, Z_OBEN = -5.0, 33.0        # Stirnwaende von 5 mm

# Zentrierung: senkrechte Halbrundleisten statt runder Zapfen. Eine
# senkrechte Leiste hat beim Drucken in dieser Lage ueberhaupt keine
# ueberhaengende Flaeche - jede Schicht liegt vollstaendig auf der
# darunter. Ein liegender Zapfen haette eine frei tragende Unterseite.
Y_LEISTE = (14.5, -22.0)            # oben und unten neben dem Teil
LEISTE_R, LEISTE_NUT_R = 2.0, 2.2   # 0,2 mm Luft
LEISTE_Z = (0.0, LAENGE)            # Spitzen der 45-Grad-Auslaeufe
NUT_Z = (-2.0, LAENGE + 2.0)        # Nut laenger, damit sie nicht aufsetzt

# Die Leisten sitzen diagonal: oben Leiste, unten Nut. Die Gegenhaelfte
# hat es umgekehrt. Damit passen die Haelften nur in einer Lage zusammen.

ANGUSS_R = 2.5
ANGUSS_Y = -M.KAMMER_ACHSE          # -11, Mitte der Rippenstirnflaeche
TRICHTER_AB = 29.5                  # ab hier oeffnet sich der Anguss mit 45 Grad
ENTL_R, ENTL_Y = 0.6, 10.0          # Entlueftung im Rohrquerschnitt

SPALT = 8.0                         # Abstand der Haelften auf dem Druckbett
RASTER = 0.5
DATEI = "tuerzwerg-giessform-manschette.stl"


# ------------------------------------------------------------- Distanzfeld ---

def anguss(x, y, z):
    """Angusskanal mit Trichter, halb in jeder Haelfte."""
    rad = math.hypot(x, y - ANGUSS_Y)
    ueber = z - TRICHTER_AB
    d = rad - ANGUSS_R if ueber <= 0.0 else (rad - ANGUSS_R - ueber) * 0.70710678
    return max(d, LAENGE - z, x)


def entlueftung(x, y, z):
    return max(math.hypot(x, y - ENTL_Y) - ENTL_R, LAENGE - z, x)


def traeger(x, y, z, y_nut):
    """Formmaterial ohne die Kavitaet - Block minus Zentriernut."""
    d = quader(x, y, z, -X_HALB, 0.0, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)
    nut = max(zapfen(math.hypot(x, y - y_nut), z, LEISTE_NUT_R, *NUT_Z), x)
    return max(d, -nut)


def haelfte(x, y, z, leiste_oben):
    """Signierter Abstand einer Formhaelfte. Negativ ist Material.

    Material liegt bei x <= 0, die Zentrierleiste steht nach x > 0 vor.
    """
    y_leiste, y_nut = Y_LEISTE if leiste_oben else (Y_LEISTE[1], Y_LEISTE[0])

    d = traeger(x, y, z, y_nut)

    # Kavitaet: die Haelfte der Manschette, die auf dieser Seite liegt
    d = max(d, -max(M.feld(x, y, z), x))

    # Anguss und Entlueftung
    d = max(d, -anguss(x, y, z))
    d = max(d, -entlueftung(x, y, z))

    # Zentrierleiste, steht in die Gegenhaelfte hinein
    leiste = max(zapfen(math.hypot(x, y - y_leiste), z, LEISTE_R, *LEISTE_Z), -x)
    return min(d, leiste)


def feld_a(x, y, z):
    return haelfte(x, y, z, True)


def feld_b(x, y, z):
    """Gegenhaelfte: gespiegelt und mit vertauschten Rollen."""
    return haelfte(-x, y, z, False)


def grenzen(gespiegelt):
    x = (-LEISTE_R - 1.5, X_HALB + 1.5) if gespiegelt else \
        (-X_HALB - 1.5, LEISTE_R + 1.5)
    return (x, (Y_UNTEN - 1.5, Y_OBEN + 1.5), (Z_UNTEN - 1.5, Z_OBEN + 1.5))


# -------------------------------------------------------------- Kennzahlen --

def hinterschnitt(schritt=0.25):
    """Belegt das Material je Haelfte ueberall nur ein Intervall in x?

    Das ist die Bedingung dafuer, dass sich die Haelfte in x abziehen
    laesst. Gezaehlt werden Stellen mit mehr als einem Materialstueck.
    """
    schlimm = 0
    n = 0
    y = Y_UNTEN_TEIL - 1.0
    while y <= Y_OBEN_TEIL + 1.0:
        z = 0.5
        while z <= LAENGE - 0.5:
            stuecke, drin = 0, False
            x = -M.R_AUSSEN - 1.0
            while x <= 0.0:
                jetzt = M.feld(x, y, z) < 0.0
                if jetzt and not drin:
                    stuecke += 1
                drin = jetzt
                x += schritt
            n += 1
            if stuecke > 1:
                schlimm += 1
            z += 1.0
        y += 0.5
    return schlimm, n


def kavitaet_volumen(schritt=0.3):
    """Rauminhalt der Manschette - so viel Silikon je Guss."""
    v = 0.0
    zelle = schritt ** 3
    x = -M.R_AUSSEN
    while x <= M.R_AUSSEN:
        y = Y_UNTEN_TEIL
        while y <= Y_OBEN_TEIL:
            z = 0.0
            while z <= LAENGE:
                if M.feld(x, y, z) < 0.0:
                    v += zelle
                z += schritt
            y += schritt
        x += schritt
    return v


def engste_wand(schritt=0.5):
    """Duennste Formwand zwischen Kavitaet und Aussenflaeche oder Nut.

    Die Trennebene zaehlt nicht als Wand - dort steht die Gegenhaelfte.
    Sie wird darum bei der Messung ins Unendliche geschoben.
    """
    def wandfeld(x, y, z):
        d = quader(x, y, z, -X_HALB, 1e4, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)
        nut = max(zapfen(math.hypot(x, y - Y_LEISTE[1]), z,
                         LEISTE_NUT_R, *NUT_Z), x)
        return max(d, -nut)

    best = (1e9, None)
    x = -M.R_AUSSEN - 0.5
    while x <= 0.0:
        y = Y_UNTEN_TEIL - 0.5
        while y <= Y_OBEN_TEIL + 0.5:
            z = -0.5
            while z <= LAENGE + 0.5:
                if abs(M.feld(x, y, z)) < 0.2:          # auf der Teilflaeche
                    w = -wandfeld(x, y, z)
                    if 0.0 < w < best[0]:
                        best = (w, (x, y, z))
                z += schritt
            y += schritt
        x += schritt
    return best


if __name__ == "__main__":
    print("Vernetze Haelfte A ...")
    tri_a = vernetzen(feld_a, grenzen(False), RASTER)
    print("Vernetze Haelfte B ...")
    tri_b = vernetzen(feld_b, grenzen(True), RASTER)

    vol_a, vol_b = volumen(tri_a), volumen(tri_b)
    if vol_a < 0:
        tri_a = [(a, c, b) for a, b, c in tri_a]
        vol_a = -vol_a
    if vol_b < 0:
        tri_b = [(a, c, b) for a, b, c in tri_b]
        vol_b = -vol_b

    ab_max, ab_mit = abweichung(feld_a, tri_a)

    # Beides auf das Druckbett stellen: z = 0 unten, Haelften nebeneinander
    def rueck(tri, dx):
        return [tuple((p[0] + dx, p[1], p[2] - Z_UNTEN) for p in t) for t in tri]

    tri = rueck(tri_a, 0.0) + rueck(tri_b, SPALT)
    schreibe_stl(tri, DATEI, "Tuerzwerg Giessform Manschette - Masse in mm")

    anteil, grad, flaeche = ueberhang(tri)
    kav = kavitaet_volumen()
    wand, wo = engste_wand()
    schlimm, gepr = hinterschnitt()

    print(f"\nDatei           {DATEI} (beide Haelften)")
    print(f"Eine Haelfte    {X_HALB:.0f} x {Y_OBEN-Y_UNTEN:.1f} x "
          f"{Z_OBEN-Z_UNTEN:.0f} mm")
    print(f"Zusammengesetzt {2*X_HALB:.0f} x {Y_OBEN-Y_UNTEN:.1f} x "
          f"{Z_OBEN-Z_UNTEN:.0f} mm")
    print(f"Dreiecke        {len(tri)}")
    print(f"Offene Kanten   {offene_kanten(tri)}  (0 = zwei geschlossene Koerper)")
    print(f"Formvolumen     {vol_a/1000:.0f} + {vol_b/1000:.0f} cm^3 "
          f"({(vol_a+vol_b)/1000*1.24:.0f} g PLA voll gefuellt)")
    print(f"Kavitaet        {kav/1000:.2f} cm^3 Silikon je Guss "
          f"({kav/1000*1.15:.1f} g)")
    print(f"Hinterschnitt   {schlimm} von {gepr} Stellen "
          f"(0 = Haelfte laesst sich abziehen)")
    print(f"Duennste Wand   {wand:.1f} mm"
          + (f" bei x={wo[0]:.1f} y={wo[1]:.1f} z={wo[2]:.1f}" if wo else ""))
    print(f"Zentrierung     Leiste {2*LEISTE_R:.0f} mm gegen Nut "
          f"{2*LEISTE_NUT_R:.1f} mm, {LEISTE_NUT_R-LEISTE_R:.1f} mm Luft")
    print(f"Anguss          {2*ANGUSS_R:.0f} mm auf die Rippenstirn, "
          f"Trichter {2*(ANGUSS_R+Z_OBEN-TRICHTER_AB):.0f} mm")
    print(f"Entlueftung     {2*ENTL_R:.1f} mm am Rohrscheitel")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm")
