#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer die Klinkenmanschette

Zweiteilige Steckform zum Ausgiessen mit Silikon, gedacht fuer den FDM-Druck.
Die Kavitaet ist die Manschette aus manschette.py, unveraendert.

Teilung durch die Symmetrieebene. Die Manschette ist kein Drehkoerper,
aber Rohr, Rippe, Kammer und Schnurbohrung liegen alle auf x = 0. Nur
diese Ebene geht hinterschnittfrei auf; nachgerechnet wird das unten in
hinterschnitt(): in jeder Haelfte darf das Material an jeder Stelle nur
ein einziges Intervall in x belegen.

Drei Kerne, keiner schwebt. Der Bohrungskern steht in den Stirnwaenden,
die Knotenkammer haengt ueber ihren Durchbruch am Bohrungskern, der
Schnurkanal bindet die Kammer zusaetzlich an den Aussenblock.

Gedruckt und gegossen wird hochkant, Drueckerachse senkrecht. Damit
stehen alle Kerne aufrecht auf der unteren Stirnwand und sind ueber die
volle Hoehe gestuetzt. Laege die Form flach, waere der Bohrungskern eine
28 mm lange Bruecke mit runder Unterseite.

Gefuellt wird von unten. Das ist der Grund, warum das Kanalsystem so
aussieht: das Silikon laeuft vom Trichter aussen am Bauteil vorbei nach
unten und tritt am tiefsten Punkt in die Kavitaet ein. Die Form fuellt
sich dadurch von unten nach oben, und die Luft wird vor dem Spiegel her
nach oben aus Steiger und Entlueftung geschoben. Fuellte man von oben,
muesste die Luft aus einem unten geschlossenen 2-mm-Ringspalt gegen das
einlaufende Silikon nach oben - der sichere Weg zu Lufteinschluessen in
der Rohrwand.

Alle Kanaele sind Rillen in der Trennflaeche der Haelfte A: nur so hebt
sich der erstarrte Anguss zusammen mit dem Teil seitlich heraus. Eine
Bohrung im Block waere ein Sackloch, aus dem der Angussstab nicht
herauskaeme, ohne ihn vorher blind abzuschneiden.

Haelfte B ist glatt - Block, Kavitaet, Zentrierung, sonst nichts.

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
Y_UNTEN, Y_OBEN = -29.0, 18.0
Z_UNTEN, Z_OBEN = -5.0, 33.0        # Stirnwaende von 5 mm

# Zentrierung: vier senkrechte Halbrundzapfen in den Stirnstreifen, wo
# die Trennflaeche ueber die volle Breite frei ist. Senkrecht, weil in
# dieser Drucklage jede Schicht vollstaendig auf der darunter liegt; ein
# liegender Zapfen haette eine frei tragende Unterseite. Diagonal
# verteilt - unten Rippe rechts, oben Rippe links -, damit die Haelften
# nur in einer Lage zusammenpassen.
Y_ZENTRIER = 6.0
ZENTRIER_R, ZENTRIER_NUT_R = 2.0, 2.2
NUT_UEBER = 0.3                     # Nut laeuft spaeter aus als die Rippe

# Kanalsystem, vollstaendig in Haelfte A
LAUF_Y = -23.5                      # senkrechter Lauf neben der Rippe
LAUF_R = 3.0
TRICHTER_AB, TRICHTER_BIS = 30.0, 31.5
TRICHTER_R = LAUF_R + (TRICHTER_BIS - TRICHTER_AB)      # 4,5
LAUF_UNTEN = -1.0

ANSCHNITT_R = 2.0                   # waagerecht vom Lauf in die Kavitaet
ANSCHNITT_Z = 1.5                   # knapp ueber der Bodenflaeche
ANSCHNITT_BIS = -17.0

STEIGER_R, STEIGER_Y = 1.5, -11.0   # ueber der Rippenstirn
ENTL_R, ENTL_Y = 0.75, 10.0         # ueber dem Rohrscheitel

SPALT = 8.0                         # Abstand der Haelften auf dem Druckbett
RASTER = 0.5
DATEI = "tuerzwerg-giessform-manschette.stl"

_SCHRAEG = 0.7071067811865476


# ------------------------------------------------------------- Distanzfeld ---

def kanal(x, y, z):
    """Anguss, Lauf, Anschnitt, Steiger, Entlueftung - alles Rillen in
    der Trennflaeche (x <= 0)."""
    rad = math.hypot(x, y - LAUF_Y)
    if z <= TRICHTER_AB:
        d = rad - LAUF_R
    elif z <= TRICHTER_BIS:
        d = (rad - LAUF_R - (z - TRICHTER_AB)) * _SCHRAEG
    else:
        d = rad - TRICHTER_R
    lauf = max(d, x, LAUF_UNTEN - z)

    anschnitt = max(math.hypot(x, z - ANSCHNITT_Z) - ANSCHNITT_R,
                    x, LAUF_Y - y, y - ANSCHNITT_BIS)

    steiger = max(math.hypot(x, y - STEIGER_Y) - STEIGER_R, x, LAENGE - z)
    entl = max(math.hypot(x, y - ENTL_Y) - ENTL_R, x, LAENGE - z)

    return min(lauf, anschnitt, steiger, entl)


def _zentrierpaar(rollen):
    """(Rippen, Nuten) je als (y, unten?) - Haelfte A hat rollen=True."""
    rippen = [(Y_ZENTRIER, True), (-Y_ZENTRIER, False)]
    nuten = [(-Y_ZENTRIER, True), (Y_ZENTRIER, False)]
    return (rippen, nuten) if rollen else (nuten, rippen)


def _zapfen_feld(x, y, z, y0, unten, r, ueber=0.0):
    """Senkrechter Halbzapfen im unteren oder oberen Stirnstreifen.

    Das offene Ende wird am Block abgeschnitten. Ohne diese Begrenzung
    liefe der Zapfen ins Unendliche weiter und das Netz endete offen an
    der Gitterkante.
    """
    rad = math.hypot(x, y - y0)
    if unten:
        return max(zapfen(rad, z, r, None, 0.0 + ueber), Z_UNTEN - z)
    return max(zapfen(rad, z, r, LAENGE - ueber, None), z - Z_OBEN)


def haelfte(x, y, z, rollen):
    """Signierter Abstand einer Formhaelfte. Negativ ist Material.

    Material liegt bei x <= 0, die Zentrierrippen stehen nach x > 0 vor.
    """
    d = quader(x, y, z, -X_HALB, 0.0, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)

    rippen, nuten = _zentrierpaar(rollen)

    # Zentriernuten zuerst: sie sind Loecher im Block
    for y0, unten in nuten:
        nut = max(_zapfen_feld(x, y, z, y0, unten, ZENTRIER_NUT_R, NUT_UEBER), x)
        d = max(d, -nut)

    # Kavitaet: die Haelfte der Manschette, die auf dieser Seite liegt
    d = max(d, -max(M.feld(x, y, z), x))

    # Kanalsystem nur in Haelfte A
    if rollen:
        d = max(d, -kanal(x, y, z))

    # Zentrierrippen stehen in die Gegenhaelfte hinein
    for y0, unten in rippen:
        rippe = max(_zapfen_feld(x, y, z, y0, unten, ZENTRIER_R), -x)
        d = min(d, rippe)
    return d


def feld_a(x, y, z):
    return haelfte(x, y, z, True)


def feld_b(x, y, z):
    """Gegenhaelfte: gespiegelt und mit vertauschten Rollen."""
    return haelfte(-x, y, z, False)


def grenzen(gespiegelt):
    x = (-ZENTRIER_R - 1.5, X_HALB + 1.5) if gespiegelt else \
        (-X_HALB - 1.5, ZENTRIER_R + 1.5)
    return (x, (Y_UNTEN - 1.5, Y_OBEN + 1.5), (Z_UNTEN - 1.5, Z_OBEN + 1.5))


# -------------------------------------------------------------- Kennzahlen --

def hinterschnitt(schritt=0.25):
    """Belegt das Material je Haelfte ueberall nur ein Intervall in x?

    Das ist die Bedingung dafuer, dass sich die Haelfte abziehen laesst.
    """
    schlimm = n = 0
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
    """Rauminhalt der Manschette - so viel Silikon steckt im Teil."""
    v, zelle = 0.0, schritt ** 3
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


def kanal_volumen(schritt=0.3):
    """Silikon, das im Kanalsystem stehen bleibt - Verlust je Guss."""
    v, zelle = 0.0, schritt ** 3
    x = -LAUF_R - 1.0
    while x <= 0.0:
        y = Y_UNTEN
        while y <= Y_OBEN:
            z = LAUF_UNTEN
            while z <= Z_OBEN:
                if kanal(x, y, z) < 0.0 and M.feld(x, y, z) > 0.0:
                    v += zelle
                z += schritt
            y += schritt
        x += schritt
    return v


def fuellweg(schritt=0.5):
    """Flutet die Form vom Trichter aus - erreicht das Silikon alles?

    Gezaehlt wird, wie viel der Kavitaet vom Einguss aus zusammenhaengend
    erreichbar ist und ob Steiger und Entlueftung angeschlossen sind.
    Das ist die eigentliche Giessbarkeitspruefung.
    """
    # 0,05 mm statt eines groesseren Wertes: an der verrundeten Stirn-
    # kante ist die Kavitaet stellenweise nur Zehntelmillimeter von der
    # Formwand entfernt, und eine zu grobe Schwelle mauerte dort zu.
    def frei(x, y, z):
        return min(feld_a(x, y, z), feld_b(x, y, z)) > 0.05

    # Das Gitter liegt auf allen drei Achsen um einen halben Schritt
    # versetzt. Sonst faellt ein Punkt genau auf die Trennebene x = 0
    # oder auf z = 28, wo Kavitaet und Steiger aneinanderstossen - dort
    # lesen beide Seiten ihren Rand, und die Flut kaeme nie hinueber.
    def auf(v):
        return (round(v / schritt - 0.5) + 0.5) * schritt

    def gitter(p):
        return tuple(auf(c) for c in p)

    def idx(p):
        return tuple(round(c / schritt - 0.5) for c in p)

    start = gitter((-0.5 * schritt, LAUF_Y, Z_OBEN - 0.6))
    gesehen = {idx(start)}
    stapel = [start]
    kav = kav_erreicht = 0
    while stapel:
        p = stapel.pop()
        for dx, dy, dz in ((schritt, 0, 0), (-schritt, 0, 0), (0, schritt, 0),
                           (0, -schritt, 0), (0, 0, schritt), (0, 0, -schritt)):
            q = (p[0] + dx, p[1] + dy, p[2] + dz)
            if not (-X_HALB < q[0] < X_HALB and Y_UNTEN < q[1] < Y_OBEN
                    and Z_UNTEN < q[2] < Z_OBEN):
                continue
            k = idx(q)
            if k in gesehen or not frei(*q):
                continue
            gesehen.add(k)
            stapel.append(q)

    # wie viel der Kavitaet ist erreicht? Dieselbe versetzte Lage.
    x = auf(-M.R_AUSSEN)
    while x <= M.R_AUSSEN:
        y = auf(Y_UNTEN_TEIL)
        while y <= Y_OBEN_TEIL:
            z = auf(0.0)
            while z <= LAENGE:
                if M.feld(x, y, z) < -0.4:
                    kav += 1
                    if idx((x, y, z)) in gesehen:
                        kav_erreicht += 1
                z += schritt
            y += schritt
        x += schritt

    st = idx(gitter((-0.5 * schritt, STEIGER_Y, Z_OBEN - 0.6))) in gesehen
    en = idx(gitter((-0.5 * schritt, ENTL_Y, Z_OBEN - 0.6))) in gesehen
    return kav_erreicht, kav, st, en


def engste_wand(schritt=0.5):
    """Duennste Formwand zwischen Kavitaet und Aussenflaeche, Zentriernut
    oder Anlauf. Die Trennebene zaehlt nicht - dort steht die Gegenhaelfte.
    """
    def wandfeld(x, y, z):
        d = quader(x, y, z, -X_HALB, 1e4, Y_UNTEN, Y_OBEN, Z_UNTEN, Z_OBEN)
        for y0, unten in _zentrierpaar(True)[1]:
            nut = max(_zapfen_feld(x, y, z, y0, unten,
                                   ZENTRIER_NUT_R, NUT_UEBER), x)
            d = max(d, -nut)
        rad = math.hypot(x, y - LAUF_Y)          # nur der Lauf, nicht der
        lauf = max(rad - LAUF_R, x, LAUF_UNTEN - z)   # Anschnitt
        return max(d, -lauf)

    best = (1e9, None)
    x = -M.R_AUSSEN - 0.5
    while x <= 0.0:
        y = Y_UNTEN_TEIL - 0.5
        while y <= Y_OBEN_TEIL + 0.5:
            z = -0.5
            while z <= LAENGE + 0.5:
                if abs(M.feld(x, y, z)) < 0.2:
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

    def rueck(tri, dx):
        return [tuple((p[0] + dx, p[1], p[2] - Z_UNTEN) for p in t) for t in tri]

    tri = rueck(tri_a, 0.0) + rueck(tri_b, SPALT)
    schreibe_stl(tri, DATEI, "Tuerzwerg Giessform Manschette - Masse in mm")

    anteil, grad, flaeche = ueberhang(tri)
    kav = kavitaet_volumen()
    kan = kanal_volumen()
    wand, wo = engste_wand()
    schlimm, gepr = hinterschnitt()
    err, ges, steiger_an, entl_an = fuellweg()

    print(f"\nDatei           {DATEI} (beide Haelften nebeneinander)")
    print(f"Eine Haelfte    {X_HALB:.0f} x {Y_OBEN-Y_UNTEN:.0f} x "
          f"{Z_OBEN-Z_UNTEN:.0f} mm")
    print(f"Zusammengesetzt {2*X_HALB:.0f} x {Y_OBEN-Y_UNTEN:.0f} x "
          f"{Z_OBEN-Z_UNTEN:.0f} mm")
    print(f"Dreiecke        {len(tri)}")
    print(f"Offene Kanten   {offene_kanten(tri)}  (0 = zwei geschlossene Koerper)")
    print(f"Formvolumen     {vol_a/1000:.0f} + {vol_b/1000:.0f} cm^3 "
          f"({(vol_a+vol_b)/1000*1.24:.0f} g PLA voll gefuellt)")
    print(f"Bauteil         {kav/1000:.2f} cm^3 ({kav/1000*1.15:.1f} g Silikon)")
    print(f"Kanalverlust    {kan/1000:.2f} cm^3, "
          f"anzuruehren rund {(kav+kan)/1000*1.15*1.15:.0f} g")
    print(f"Hinterschnitt   {schlimm} von {gepr} Stellen "
          f"(0 = Haelfte laesst sich abziehen)")
    print(f"Fuellweg        {100.0*err/ges:.1f} % der Kavitaet vom Einguss "
          f"erreichbar, Steiger {'an' if steiger_an else 'AB'}, "
          f"Entlueftung {'an' if entl_an else 'AB'}")
    print(f"Duennste Wand   {wand:.1f} mm"
          + (f" bei x={wo[0]:.1f} y={wo[1]:.1f} z={wo[2]:.1f}" if wo else ""))
    print(f"Zentrierung     4 Zapfen {2*ZENTRIER_R:.0f} mm gegen Nut "
          f"{2*ZENTRIER_NUT_R:.1f} mm, {ZENTRIER_NUT_R-ZENTRIER_R:.1f} mm Luft")
    print(f"Anschnitt       {2*ANSCHNITT_R:.0f} mm bei z = {ANSCHNITT_Z:.1f} mm, "
          f"Lauf {2*LAUF_R:.0f} mm, Trichter {2*TRICHTER_R:.0f} mm")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm")
