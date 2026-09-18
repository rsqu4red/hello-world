#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer den Zugring Rev. H

Drei Teile: zwei Formhaelften und ein loser Kammerkern.

Die Regel, wie bei der Manschette
---------------------------------

Jedes Formteil verlaesst das Gussteil in einer geraden Linie.

  Haelften      -> +/- z   Sie bilden die Aussenflaeche und die Oeffnung.
  Kammerkern    -> -y      Radial nach innen durch die Oeffnung heraus.

Warum die Teilung bei z = 0 aufgeht
-----------------------------------

Der Bandquerschnitt ist zur Ringebene symmetrisch und dort am
breitesten - die Eckradien nehmen nach beiden Seiten Material weg. Fuer
einen Zug in z ist damit sowohl die Aussenflaeche als auch die Oeffnung
hinterschnittfrei: aussen wird der Querschnitt zur Stirnflaeche hin
schmaler, innen wird die Oeffnung dorthin weiter.

Warum es trotzdem ein drittes Teil braucht
------------------------------------------

Die Knotenkammer liegt bei z = -3,6 bis +3,6 in einem Band, das von
z = -5,5 bis +5,5 reicht. Ueber ihr stehen 1,9 mm Silikon. Ein Vorsprung
aus einer Haelfte muesste die durchdringen, um die Kammer zu bilden -
das geht nicht. Die Kammer bekommt deshalb einen eigenen Kern, der
radial nach innen durch die Oeffnung gezogen wird.

Er ist ueber seine ganze Laenge prismatisch, und der Schnurstift am
aeusseren Ende ist mit Ø5 schmaler als die Kammer mit 14 x 7,2. Nach
innen wird er also nirgends breiter und laesst sich nur in diese eine
Richtung ziehen.

Gehalten wird er an beiden Enden: aussen steckt der Schnurstift in
einer Bohrung in der Stirnwand, innen sitzt ein Zapfen gleichen
Querschnitts in einem Schlitz im Oeffnungskern. Beide Sitze liegen in
der Trennebene und oeffnen sich mit der Form.

Giessen
-------

Gedruckt wird flach, Trennflaeche nach oben. Gegossen wird hochkant,
der Reif steht wie ein Rad. Gefuellt wird von unten: der Lauf fuehrt vom
Trichter oben links aussen am Reif vorbei nach unten, laeuft unter ihm
durch und tritt am tiefsten Punkt ein. Von dort steigt das Silikon auf
beiden Seiten gleich hoch und trifft sich oben - genau dort sitzen die
beiden Entlueftungen, links und rechts neben der Schnurbohrung.

Alle Kanaele liegen je zur Haelfte in beiden Formhaelften und sind
damit voll rund. Nur in einer waeren sie halbrund, und ein halbrunder
Kanal fuehrt bei gleichem Radius nur 18,9 Prozent des Stroms.

Der Lauf hat keine Ecken
------------------------

Die erste Fassung setzte den senkrechten Lauf, den waagerechten und den
Anschnitt stumpf aneinander - drei rechte Winkel. In einer solchen Ecke
steht das Silikon, statt zu fliessen: aussen reisst der Strom ab, innen
bleibt eine Totzone stehen, in der Luft haengt.

Jetzt sind die beiden Umlenkungen echte Viertelkreise vom
Kruemmungsradius 7 mm, also 1,75 mal dem Rohrradius. Sie stossen
tangential an die geraden Stuecke, der Querschnitt bleibt dabei ueberall
gleich. Der Trichter oben laeuft ueber eine Smoothstep-Kurve auf, hat
also weder am Anfang noch am Ende einen Knick, und der Anschnitt
verjuengt sich auf dieselbe Weise von 8 auf 6 mm. Wo Lauf und
Entlueftungen in die Kavitaet muenden, sitzt eine 1,5-mm-Verrundung.

Zentrierung
-----------

Drei Halbrundzapfen Ø6 statt zwei, und keiner mehr am Kanal: der linke
sass mit 3 mm Abstand neben dem senkrechten Lauf. Die Form ist dafuer
links um 10 mm breiter geworden, der Zapfen steht jetzt aussen daneben
mit 5,4 mm Wand nach beiden Seiten. Die drei liegen so, dass die um 180
Grad verdrehte Lage nicht passt - falsch herum kann man sie nicht
zusammenlegen.

    python3 giessform_revh.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, ueberhang, abweichung,
                  schreibe_stl, schreibe_3mf, quader, weich_vereinen)
from reif_revh import REV_H as R
from reif_mix import _rundbox, D_SCHNUR

TAU = 2.0 * math.pi

# ---------------------------------------------------------------- Bauteil ---

R_AUSSEN = R.aussen(1.0)                    # 43
HALB = R.d_oben / 2.0                       # 5,5
A_K, B_K = R.a_kammer, R.b_kammer           # 7,0 und 3,6
KAMMER_A = R_AUSSEN - R.bohr_tiefe          # 35,5 aeusseres Kammerende
KAMMER_I = R.innen(1.0) - 1.0               # 19,0 Durchbruch in die Oeffnung
STIFT_R = D_SCHNUR / 2.0                    # 2,5

# ------------------------------------------------------------------ Form ----

X_LINKS, X_RECHTS = -72.0, 50.0
Y_UNTEN, Y_OBEN = -63.0, 50.0
Z_TIEF = 14.0
TURM_X, TURM_Y = -34.0, 72.0

LUFT = 0.05
SITZ_AUSSEN = R_AUSSEN + 4.0                # Stiftsitz in der Stirnwand
SITZ_INNEN = KAMMER_I - 3.0                 # Zapfensitz im Oeffnungskern

# Kanaele, alle in der Trennebene z = 0
LAUF_R = 4.0                                # Rohrradius, ueberall gleich
LAUF_X = -51.0                              # Achse des senkrechten Laufs
LAUF_UNTEN = -54.0                          # Achse des waagerechten Laufs
BOGEN_R = 7.0                               # Kruemmungsradius der Umlenkungen
TRICHTER_AB, TRICHTER_BIS = 62.0, 72.0
TRICHTER_WEIT = 7.0                         # Zuwachs bis zur Muendung
ANSCHNITT_R = 3.0
VERRUNDUNG = 1.5                            # Uebergang Kanal -> Kavitaet
ENTL_R = 1.0
ENTL_WINKEL = 8.0                           # Grad neben der Schnurbohrung

ZENTRIER_R, ZENTRIER_NUT_R = 3.0, 3.1
# Drei Zapfen, unsymmetrisch: um 180 Grad verdreht passt keine Lage.
# Der linke sitzt aussen neben dem senkrechten Lauf, nicht mehr an ihm.
ZENTRIER = [(-63.5, 30.0), (42.0, -48.0), (42.0, 36.0)]

RASTER = 0.6
DATEI_A = "tuerzwerg-giessform-revh-haelfte-a.stl"
DATEI_B = "tuerzwerg-giessform-revh-haelfte-b.stl"
DATEI_K = "tuerzwerg-giessform-revh-kern.stl"
DATEI_3MF = "tuerzwerg-giessform-revh.3mf"

# Tangentenpunkte der beiden Umlenkungen
_TANG_Y = LAUF_UNTEN + BOGEN_R              # -47: Ende senkrecht, Beginn Anschnitt
_TANG_XL = LAUF_X + BOGEN_R                 # -44: Beginn waagerecht
_TANG_XR = -BOGEN_R                         # -7:  Ende waagerecht
ANSCHNITT_BIS = -R_AUSSEN + 2.0             # -41: 2 mm im Bauteil


# ------------------------------------------------------------- Kammerkern ---

def _koerper(x, y, z):
    """Der Reifkoerper ohne Kammer und ohne Schnurbohrung."""
    rho = math.hypot(x, y)
    if rho < 1e-9:
        rho = 1e-9
    c = y / rho
    a = R.breite(c) / 2.0
    b = R.dicke(c) / 2.0
    u = rho - (R.aussen(c) - a)
    return _rundbox(u, z, a, b, R.eckfaktor(c) * min(a, b))


def kern(x, y, z):
    """Kammer, Schnurbohrung und beide Sitze. Zieht nach -y.

    Gebaut als scharfe Huellform - Kammerprisma, Schnurstift, Zapfen -,
    von der das Bauteil abgezogen wird. Damit traegt der Kern die weichen
    Verrundungen mit, mit denen die Kammer in Oeffnung und Schnurbohrung
    laeuft, und ueberlappt das Silikon an keiner Stelle.

    Zwei Sackgassen davor: ein Kern aus scharfen Kanten steht an genau
    diesen Verrundungen an. Ein Kern aus "Reifkoerper minus Bauteil"
    traegt sie zwar, hat aber bei y = 20 eine Luecke - dort endet der
    Reifkoerper an der Bandinnenkante, und der Zapfen fing erst bei 19 an.
    """
    quer = _rundbox(x, z, A_K, B_K, 0.8 * min(A_K, B_K))
    kammer = max(quer, y - KAMMER_A, SITZ_INNEN - y)
    stift = max(math.hypot(x, z) - STIFT_R, KAMMER_A - y, y - SITZ_AUSSEN)
    return max(min(kammer, stift), -R.feld(x, y, z))


def kernsitz(x, y, z):
    """Die beiden Sitze mit Passluft - Aussparungen in den Haelften."""
    quer = _rundbox(x, z, A_K + LUFT, B_K + LUFT,
                    0.8 * min(A_K, B_K))
    innen = max(quer, y - KAMMER_I, SITZ_INNEN - LUFT - y)
    stift = max(math.hypot(x, z) - (STIFT_R + LUFT),
                R_AUSSEN - y, y - (SITZ_AUSSEN + LUFT))
    return min(innen, stift)


# ---------------------------------------------------------------- Kanaele ---

def _weich(t):
    """Smoothstep: laeuft an beiden Enden mit Steigung null an.

    Damit bekommt eine Aufweitung weder am Anfang noch am Ende einen
    Knick - anders als eine Gerade, die zweimal eine Kante hinterlaesst.
    """
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def _bogen(x, y, z, cx, cy, sx, sy, rb, r):
    """Viertelkreisbogen als Rohr vom Radius r.

    Die Achse ist ein Kreisviertel vom Radius rb um (cx, cy) in der
    Ebene z = 0; sx und sy waehlen den Quadranten. Der naechste
    Achsenpunkt ergibt sich, indem die Richtung (x - cx, y - cy) auf
    diesen Quadranten geklemmt und auf rb normiert wird - fuer einen
    Kreisbogen ist das der exakte Abstand, nicht genaehert.
    """
    dx = max((x - cx) * sx, 0.0)
    dy = max((y - cy) * sy, 0.0)
    n = math.hypot(dx, dy)
    if n < 1e-12:
        dx, dy, n = 1.0, 0.0, 1.0
    ax = cx + rb * dx / n * sx
    ay = cy + rb * dy / n * sy
    return math.hypot(math.hypot(x - ax, y - ay), z) - r


def kanal(x, y, z):
    """Lauf, Anschnitt und die beiden Entlueftungen, alle bei z = 0.

    Fuenf Stuecke, die tangential ineinander laufen: senkrechter Lauf mit
    Trichter, Bogen, waagerechter Lauf, Bogen, Anschnitt. Weil die Boegen
    an den Tangentenpunkten dieselbe Richtung und denselben Querschnitt
    haben wie die Geraden, gibt min() hier keine Kante.
    """
    # senkrechter Lauf, oben weich zum Trichter aufgeweitet
    rad = math.hypot(x - LAUF_X, z)
    r_lauf = LAUF_R + TRICHTER_WEIT * _weich(
        (y - TRICHTER_AB) / (TRICHTER_BIS - TRICHTER_AB))
    senkrecht = max(rad - r_lauf, _TANG_Y - y)

    # Umlenkung nach unten links
    bogen_l = _bogen(x, y, z, _TANG_XL, _TANG_Y, -1.0, -1.0, BOGEN_R, LAUF_R)

    # waagerechter Lauf unter dem Reif
    waagerecht = max(math.hypot(y - LAUF_UNTEN, z) - LAUF_R,
                     _TANG_XL - x, x - _TANG_XR)

    # Umlenkung nach oben rechts
    bogen_r = _bogen(x, y, z, _TANG_XR, _TANG_Y, 1.0, -1.0, BOGEN_R, LAUF_R)

    # Anschnitt: senkrecht in den tiefsten Punkt, dabei weich verjuengt
    r_an = LAUF_R + (ANSCHNITT_R - LAUF_R) * _weich(
        (y - _TANG_Y) / (ANSCHNITT_BIS - _TANG_Y))
    anschnitt = max(math.hypot(x, z) - r_an, _TANG_Y - y, y - ANSCHNITT_BIS)

    d = min(senkrecht, bogen_l, waagerecht, bogen_r, anschnitt)

    # zwei Entlueftungen, radial nach aussen neben der Schnurbohrung
    for vz in (1.0, -1.0):
        w = math.radians(ENTL_WINKEL) * vz
        sx, sy = math.sin(w), math.cos(w)
        laengs = x * sx + y * sy                  # Abstand laengs der Achse
        quer = math.hypot(x - laengs * sx, z)     # Abstand zur Achse
        entl = max(quer - ENTL_R, (R_AUSSEN - 2.0) - laengs)
        d = min(d, entl)
    return d


# -------------------------------------------------------------- Haelften ----

def _zentrier(x, y, z, r, oben, nut):
    """Halbrundzapfen bzw. -nut auf der Trennebene."""
    # Der Zapfen steht aus der Trennflaeche heraus, also nach z < 0;
    # die Nut geht in den Block hinein. Eine fruehere Fassung legte beide
    # nach z = 0 bis 4 - der Zapfen lag damit im Block und tat nichts,
    # die Form hatte gar keine Zentrierung.
    best = 1e9
    for i, (zx, zy) in enumerate(ZENTRIER):
        if (i == 0) != oben:
            continue
        rad = math.hypot(x - zx, y - zy) - r
        if nut:
            best = min(best, max(rad, z - 4.5, -z))
        else:
            best = min(best, max(rad, z, -4.0 - z))
    return best


def haelfte(x, y, z, gespiegelt):
    if gespiegelt:
        x = x                      # Spiegelung geschieht ueber z
    d = quader(x, y, z, X_LINKS, X_RECHTS, Y_UNTEN, Y_OBEN, 0.0, Z_TIEF)
    turm = quader(x, y, z, X_LINKS, TURM_X, Y_OBEN, TURM_Y, 0.0, Z_TIEF)
    d = min(d, turm)

    # Kavitaet und Kanal zusammen abziehen, mit weichem Uebergang: wo
    # Anschnitt und Entlueftungen in die Kavitaet muenden, steht so eine
    # Verrundung statt einer Kerbe. Nur z >= 0, die andere Haelfte spiegelt.
    hohl = weich_vereinen(R.feld(x, y, z), kanal(x, y, z), VERRUNDUNG)
    d = max(d, -max(hohl, -z))
    d = max(d, -max(kern(x, y, z), -z))
    d = max(d, -max(kernsitz(x, y, z), -z))

    # Zentrierung: Zapfen der einen, Nut der anderen Haelfte
    nut = _zentrier(x, y, z, ZENTRIER_NUT_R, not gespiegelt, True)
    d = max(d, -nut)
    zapfen = _zentrier(x, y, z, ZENTRIER_R, gespiegelt, False)
    return min(d, zapfen)


def feld_a(x, y, z):
    return haelfte(x, y, z, False)


def feld_b(x, y, z):
    """Gegenhaelfte: an der Trennebene gespiegelt, Rollen getauscht."""
    return haelfte(x, y, -z, True)


def grenzen_halb(gespiegelt=False):
    z = (-Z_TIEF - 2, 6.0) if gespiegelt else (-6.0, Z_TIEF + 2)
    return ((X_LINKS - 2, X_RECHTS + 2), (Y_UNTEN - 2, TURM_Y + 2), z)


def grenzen_kern():
    return ((-A_K - 2, A_K + 2), (SITZ_INNEN - 2, SITZ_AUSSEN + 2),
            (-B_K - 2, B_K + 2))


# ------------------------------------------------------------ Kennzahlen ----

def kern_frei(schritt=0.4, dmax=45.0):
    """Kommt der Kammerkern heraus?

    Nicht in einem Zug: er wird radial nach innen geschoben, bis er ganz
    in der Oeffnung steht, und dann seitlich herausgenommen. Geprueft
    wird, bei welchem Schub das erste Mal jeder Kernpunkt in der Oeffnung
    liegt, und ob er auf dem Weg dorthin Silikon durchquert.
    """
    (x0, x1), (y0, y1), (z0, z1) = grenzen_kern()
    punkte = []
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            z = z0
            while z <= z1:
                if kern(x, y, z) < 0.0:
                    punkte.append((x, y, z))
                z += schritt
            y += schritt
        x += schritt

    def drin(d):
        for px, py, pz in punkte:
            rho = math.hypot(px, py - d)
            if rho < 1e-9:
                continue
            if rho >= R.innen((py - d) / rho):
                return False
        return True

    passt = [d for d in (i * schritt for i in range(int(dmax / schritt)))
             if drin(d)]
    if not passt:
        return None, None, len(punkte), len(punkte), 0.0

    schub = passt[0]
    gesperrt, tief = 0, 0.0
    for px, py, pz in punkte:
        d, traf = schritt, False
        while d <= schub:
            v = R.feld(px, py - d, pz)
            if v < 0.0:
                traf = True
                tief = max(tief, -v)
            d += schritt
        if traf:
            gesperrt += 1
    return schub, passt[-1], len(punkte), gesperrt, tief


def zieh_test(feld, grenzen, richtung, weg, schritt=0.6):
    """Kommt dieses Formteil geradeaus heraus?"""
    (x0, x1), (y0, y1), (z0, z1) = grenzen
    dx, dy, dz = richtung
    gesperrt = gesamt = 0
    tief = 0.0
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            z = z0
            while z <= z1:
                if feld(x, y, z) < 0.0:
                    gesamt += 1
                    d, traf = schritt, False
                    while d <= weg:
                        v = R.feld(x + dx * d, y + dy * d, z + dz * d)
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


def drucklage(tri):
    """Die Haelfte so hinlegen, wie sie gedruckt wird.

    ueberhang() nimmt an, dass entlang +z aufgebaut wird und z = 0 auf
    dem Bett liegt. Die Haelfte wird aber mit der Trennflaeche nach oben
    gedruckt, das Bett ist also die Rueckseite bei z = Z_TIEF. Ohne
    diese Spiegelung misst die Pruefung die Form auf dem Kopf stehend -
    genau umgekehrt. Das Spiegeln dreht den Umlaufsinn um, deshalb
    werden zwei Ecken getauscht.
    """
    return [((a[0], a[1], Z_TIEF - a[2]),
             (c[0], c[1], Z_TIEF - c[2]),
             (b[0], b[1], Z_TIEF - b[2])) for a, b, c in tri]


def kavitaet_volumen(schritt=0.6):
    v = 0.0
    x = -R_AUSSEN - 1
    while x <= R_AUSSEN + 1:
        y = -R_AUSSEN - 1
        while y <= R_AUSSEN + 1:
            z = -HALB - 1
            while z <= HALB + 1:
                if R.feld(x, y, z) < 0.0:
                    v += schritt ** 3
                z += schritt
            y += schritt
        x += schritt
    return v


if __name__ == "__main__":
    print("Vernetze Haelfte A ...")
    tri_a = vernetzen(feld_a, grenzen_halb(), RASTER)
    print("Vernetze Haelfte B ...")
    tri_b = vernetzen(feld_b, grenzen_halb(True), RASTER)
    print("Vernetze Kammerkern ...")
    tri_k = vernetzen(kern, grenzen_kern(), RASTER * 0.5)

    def richte(t):
        v = volumen(t)
        return ([(a, c, b) for a, b, c in t], -v) if v < 0 else (t, v)

    tri_a, vol_a = richte(tri_a)
    tri_b, vol_b = richte(tri_b)
    tri_k, vol_k = richte(tri_k)

    schreibe_stl(tri_a, DATEI_A, "Tuerzwerg Giessform Rev. H Haelfte A - mm")
    schreibe_stl(tri_b, DATEI_B, "Tuerzwerg Giessform Rev. H Haelfte B - mm")
    schreibe_stl(tri_k, DATEI_K, "Tuerzwerg Giessform Rev. H Kammerkern - mm")

    schreibe_3mf([("Haelfte A", tri_a, (0.0, 0.0, 0.0)),
                  ("Haelfte B", tri_b, (130.0, 0.0, 0.0)),
                  ("Kammerkern", tri_k, (60.0, 90.0, 0.0))],
                 DATEI_3MF, "Tuerzwerg Giessform Zugring Rev. H",
                 "Beide Haelften flach, Trennflaeche nach oben. PLA, "
                 "0,2 mm Schicht, 4 Perimeter, 30 Prozent Infill.")

    za_s, za_g, za_t = zieh_test(feld_a, grenzen_halb(), (0.0, 0.0, 1.0), 20.0)
    schub, schub_max, zk_g, zk_s, zk_t = kern_frei()
    kav = kavitaet_volumen()
    tri_druck = drucklage(tri_a)
    anteil, grad, flaeche = ueberhang(tri_druck, RASTER)
    anteil_saum = ueberhang(tri_druck)[0]
    anteil_falsch = ueberhang(tri_a, RASTER)[0]
    ab_max, ab_mit = abweichung(feld_a, tri_a)

    print(f"\nDateien         {DATEI_3MF}")
    print(f"Eine Haelfte    {X_RECHTS-X_LINKS:.0f} x {TURM_Y-Y_UNTEN:.0f} x "
          f"{Z_TIEF:.0f} mm")
    print(f"Kammerkern      {2*A_K:.0f} x {2*B_K:.1f} mm Querschnitt, "
          f"{SITZ_AUSSEN-SITZ_INNEN:.0f} mm lang")
    print(f"Dreiecke        {len(tri_a)} + {len(tri_b)} + {len(tri_k)}")
    print(f"Offene Kanten   A {offene_kanten(tri_a)}, B {offene_kanten(tri_b)}, "
          f"Kern {offene_kanten(tri_k)}")
    print(f"Bauteil         {kav/1000:.2f} cm^3 ({kav/1000*1.15:.0f} g Silikon)")
    print(f"Geradeaus heraus (0 gesperrt = kein Hinterschnitt):")
    print(f"  Haelfte -> +z   {za_s} von {za_g} Punkten gesperrt"
          + (f", bis {za_t:.2f} mm tief" if za_s else ""))
    if schub is None:
        print("  Kern -> -y      passt NIE ganz in die Oeffnung")
    else:
        print(f"  Kern -> -y      {zk_s} von {zk_g} Punkten gesperrt"
              + (f", bis {zk_t:.2f} mm tief" if zk_s else "")
              + f"; Schub {schub:.1f} bis {schub_max:.1f} mm, dann steht er "
                f"ganz in der Oeffnung")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"                mit dem alten 0,3-mm-Saum {anteil_saum:.2f} % - "
          f"die Differenz ist die Netzkante am Druckbett")
    print(f"                kopfueber gedruckt waeren es "
          f"{anteil_falsch:.2f} %")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
