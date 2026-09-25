#!/usr/bin/env python3
"""
Türzwerg – Klinkenmanschette mit durchgehendem Rundloch

Der Vorschlag
-------------

Die Knotenkammer wird ein rundes Loch von Ø10, und dieses Loch laeuft
nach OBEN durch die Decke der Manschette hindurch - also durch die obere
Rohrwand, durch die Bohrung, durch die untere Rohrwand bis in den Kiel.
Nur die letzten 3,5 mm zum Kielboden hin sind Ø4, damit der Knoten sich
abstuetzt und die Schnur durchpasst.

Warum das den Knoten UND den Stift zusammenbringt
--------------------------------------------------

Vorher stand hier ein Widerspruch: der Knoten haelt nur bei Verengung
nach unten, ein nach unten gezogener Stift braucht Erweiterung nach
unten. Beides an derselben Flaeche, entgegengesetztes Vorzeichen.

Das Loch durch die Decke loest ihn, weil der Stift dann gar nicht nach
unten muss. Er wird nach OBEN herausgezogen, und in dieser Richtung
erweitert sich das Loch ueberall: Ø4 an der Spitze, darueber Ø10 bis
hinaus. Kein Hinterschnitt, kein Abstreifen, keine Dehnung.

Liegt die Trennebene waagerecht, steckt der Stift fest in der oberen
Formhaelfte und faehrt beim Oeffnen von selbst heraus - ohne Mechanik.
Er durchquert dabei den Bohrungskern, der dafuer eine Ø10-Querbohrung
bekommt; die Reihenfolge ist dann Oeffnen, Kern ziehen, Auswerfen.

Was es kostet
-------------

Ein sichtbares Loch oben auf der Manschette. Und der tragende Ring ist
dort unterbrochen, wo das Loch durchgeht - nicht mehr nur unten, sondern
auch oben. Ueber die 10 mm Lochbreite ist der Rohrmantel damit in zwei
Boegen geteilt. Wie viel das ausmacht, steht unten gemessen.

Der Knotenraum aendert sich dagegen nicht von selbst: er haengt weiter
am Drueckerdurchmesser, weil der Knoten unter dem Druecker sitzt. Mit
TIEFER wird der Kiel nach unten verlaengert, dann stimmt auch das.

    python3 manschette_rundloch.py
"""

import math

from netz import (abweichung, offene_kanten, schreibe_stl, vernetzen, volumen,
                  weich_abziehen as _weich_abziehen,
                  weich_vereinen as _weich_vereinen)

import manschette as MA
from manschette import (D_INNEN, D_SCHNUR, EINLAUF, KANTE, LAENGE, RIPPE_WAND,
                        R_AUSSEN, R_INNEN, SCHNUR_SENK, VERRUNDUNG, WAND,
                        WAND_ENDE, _ruecknahme)

D_LOCH = 10.0            # Knotenloch, rund
SCHNUR_HALS = 3.5        # Laenge des Ø4-Halses am Kielboden
# Kiel nach unten verlaengern. 0 waere die Fassung genau wie
# vorgeschlagen - dann bleiben unter einem Ø20-Druecker aber nur 5,5 mm
# fuer den Knoten, also noch weniger als die 6,5 von heute. Der Grund ist
# nicht das Rundloch, sondern dass der Knoten weiterhin unter dem
# Druecker sitzt. 3,5 mm tiefer bringt die 9,0 mm, die ein Sackstich in
# 4-mm-Schnur braucht, und kostet 3,5 mm Bauhoehe. Am Mantel aendert es
# nichts - der bleibt bei 62 Prozent.
TIEFER = 3.5

KIEL_ACHSE = MA.KAMMER_ACHSE + TIEFER
R_KIEL = D_LOCH / 2.0 + RIPPE_WAND
KIEL_UNTEN = KIEL_ACHSE + R_KIEL
Y_STUFE = -(KIEL_UNTEN - SCHNUR_HALS)     # wo Ø10 auf Ø4 springt

RASTER = 0.29
DATEI = "tuerzwerg-manschette-rundloch.stl"


def knotenfreiraum(d_druecker=20.0):
    """Vom Drueckermantel bis zur Stufe."""
    return abs(Y_STUFE) - d_druecker / 2.0


# --------------------------------------------------------------- Feld -----

def aussenfeld(x, y, z):
    profil = _weich_vereinen(
        math.hypot(x, y) - (R_AUSSEN - _ruecknahme(z)),
        math.hypot(x, y + KIEL_ACHSE) - R_KIEL, VERRUNDUNG)
    wq = profil + KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    return (min(max(wq, wz), 0.0)
            + math.hypot(max(wq, 0.0), max(wz, 0.0)) - KANTE)


def loch_gross(x, y, z):
    """Ø10, von der Stufe nach oben durch die Decke hinaus."""
    return max(math.hypot(x, z - LAENGE / 2.0) - D_LOCH / 2.0, Y_STUFE - y)


def loch_klein(x, y, z):
    """Ø4 von der Stufe nach unten, mit Senkung am Austritt."""
    senk = min(SCHNUR_SENK, max(0.0, -y - (KIEL_UNTEN - SCHNUR_SENK)))
    return max(math.hypot(x, z - LAENGE / 2.0) - (D_SCHNUR / 2.0 + senk),
               y - Y_STUFE)


def feld(x, y, z):
    r = math.hypot(x, y)
    bohrung = r - (R_INNEN + max(0.0, EINLAUF - min(z, LAENGE - z)))
    d = max(aussenfeld(x, y, z), -bohrung)
    d = _weich_abziehen(d, loch_gross(x, y, z), 0.8)
    return max(d, -loch_klein(x, y, z))


def grenzen():
    return ((-R_AUSSEN - 2, R_AUSSEN + 2),
            (-KIEL_UNTEN - 2, R_AUSSEN + 2),
            (-1.5, LAENGE + 1.5))


# --------------------------------------------------------- Entformbarkeit --

def _r(lo, hi, s):
    return [lo + s * (i + 0.5) for i in range(int(round((hi - lo) / s)))]


def stift_hinterschnitt(f, aussen, schritt=0.3):
    """Kommt der Stift nach oben heraus?

    Geprueft wird nur das, was der Stift bildet: die Saeule ueber der
    Bohrungsachse. Ein Punkt ist hinterschnitten, wenn zwischen ihm und
    dem Austritt oben noch Material steht.
    """
    bl = ges = 0
    ys = list(reversed(_r(-KIEL_UNTEN - 1, R_AUSSEN + 1, schritt)))
    for x in _r(-D_LOCH / 2, D_LOCH / 2, schritt):
        for z in _r(LAENGE / 2 - D_LOCH / 2, LAENGE / 2 + D_LOCH / 2, schritt):
            if math.hypot(x, z - LAENGE / 2.0) > D_LOCH / 2.0:
                continue
            gesehen = False
            for y in ys:
                if f(x, y, z) < 0.0:
                    gesehen = True
                elif aussen(x, y, z) < 0.0:
                    ges += 1
                    if gesehen:
                        bl += 1
    return bl, ges


def mantel_geschlossen(f, schritt=0.3):
    """Auf wie viel der Laenge ist der Rohrmantel ein geschlossener Ring?

    Gemessen wird dicht an der Bohrung, nicht auf halber Wand. Auf halber
    Wand (r = 10,5) liegt der Messkreis an den Stirnseiten ausserhalb des
    Bauteils, weil die Wand dort auf 1,2 mm abgeflacht ist - das zaehlt
    dann faelschlich als offen und drueckt alle Fassungen gleichmaessig.
    """
    rm = R_INNEN + 0.3
    zu = ges = 0
    for z in _r(0.0, LAENGE, schritt):
        ges += 1
        if all(f(rm * math.sin(math.radians(i)), rm * math.cos(math.radians(i)),
                 z) < 0.0 for i in range(360)):
            zu += 1
    return zu, ges


# ---------------------------------------------------------------- Lauf ----

if __name__ == "__main__":
    import manschette_quertasche as QT

    print("Rundloch durch die Decke, gegen die anderen Fassungen")
    print(f"  {'':34s}{'heute':>10}{'Rundloch':>11}{'Quertasche':>13}")
    a1, g1 = stift_hinterschnitt(MA.feld, aussenfeld)
    a2, g2 = stift_hinterschnitt(feld, aussenfeld)
    print(f"  {'Stift nach oben, hinterschnitten':34s}"
          f"{f'{100*a1/g1:.1f} %':>10}{f'{100*a2/g2:.2f} %':>11}{'—':>13}")
    m1, t1 = mantel_geschlossen(MA.feld)
    m2, t2 = mantel_geschlossen(feld)
    m3, t3 = mantel_geschlossen(QT.feld)
    print(f"  {'Rohrmantel geschlossen':34s}"
          f"{f'{100*m1/t1:.0f} %':>10}{f'{100*m2/t2:.0f} %':>11}"
          f"{f'{100*m3/t3:.0f} %':>13}")
    print(f"  {'Kerne mit eigener Bewegung':34s}{'2':>10}{'1 + Stift':>11}"
          f"{'1':>13}")
    print()
    print("  Knotenraum unter dem Druecker:")
    for d in (18.0, 20.0, 23.0):
        print(f"    Ø{d:4.1f}{MA.knotenfreiraum(d):>12.1f} mm"
              f"{knotenfreiraum(d):>10.1f} mm{QT.knotenfreiraum(d):>12.1f} mm")
    print()

    print("Vernetze ...")
    tri = vernetzen(feld, grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, DATEI, "Tuerzwerg Manschette Rundloch - mm")
    ab_max, ab_mit = abweichung(feld, tri)
    lo = [min(q[i] for d in tri for q in d) for i in range(3)]
    hi = [max(q[i] for d in tri for q in d) for i in range(3)]

    print(f"\nDatei          {DATEI}")
    print(f"  Dreiecke     {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Masse        {hi[0]-lo[0]:.2f} x {hi[1]-lo[1]:.2f} x "
          f"{hi[2]-lo[2]:.2f} mm   (heute 24,00 x 31,50 x 28,00)")
    print(f"  Volumen      {vol/1000:.3f} cm^3  ({vol/1000*1.15:.1f} g)")
    print(f"  Formtreue    hoechstens {ab_max*1000:.0f} um, im Mittel "
          f"{ab_mit*1000:.0f} um")
    print()
    print(f"  Loch         Ø{D_LOCH:.0f} von oben durch, Hals Ø{D_SCHNUR:.0f} "
          f"auf {SCHNUR_HALS:.1f} mm")
    print(f"  Stufe        bei y = {Y_STUFE:.1f}, Kielboden bei "
          f"{-KIEL_UNTEN:.1f}")
    print(f"  Wand         {WAND:.1f} mm Mitte, {WAND_ENDE:.1f} mm Stirnseite, "
          f"{RIPPE_WAND:.1f} mm neben dem Loch")
    print()
    print("Werkzeug:  zwei Haelften (Trennebene waagerecht) + Bohrungskern")
    print("           + ein gerader Ø10-Stift, der in der oberen Haelfte")
    print("           steckt und beim Oeffnen von selbst herausfaehrt.")
    print("           Der Kern braucht dafuer eine Ø10-Querbohrung.")
