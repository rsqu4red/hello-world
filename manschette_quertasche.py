#!/usr/bin/env python3
"""
Türzwerg – Klinkenmanschette mit Quertasche

Warum die vorige Idee nicht taugte
-----------------------------------

Der durchlaufende Kanal machte das Werkzeug einfach, nahm der Manschette
aber die beiden geschlossenen Ringe an den Stirnseiten - und die tragen
die Spannkraft. Nachgerechnet: der 11 mm breite Kanal durchtrennt in
einer Ø18-Bohrung 75 Grad des Rohrmantels. Geschlossen ist der Ring
heute nur auf 2 x 3,5 mm, also auf einem Viertel der Laenge. Faellt das
weg, federt die Manschette ueber die volle Laenge auf.

Der eigentliche Fehler steckt aber tiefer: die Knotenkammer teilt sich
den Platz mit der Bohrung. Daraus folgt beides - der durchbrochene
Mantel UND der zu knappe Knotenraum:

    Druecker Ø18  ->  7,5 mm     Druecker Ø20  ->  6,5 mm
    Druecker Ø23  ->  5,0 mm     gebraucht:       rund 9 mm

Fuer keinen einzigen Drueckerdurchmesser reicht es. Je dicker der
Druecker, desto weniger bleibt - weil er in denselben Raum hineinragt.

Die Aenderung
-------------

Die Tasche wandert unter den Rohrmantel und laeuft quer durch den Kiel,
von einer Seite zur anderen.

Drei Dinge fallen damit zusammen:

1. Der Rohrmantel bleibt ueber die volle Laenge ein geschlossener Ring.
   Die Manschette haelt besser als heute, nicht schlechter.

2. Der Knotenraum haengt nicht mehr vom Druecker ab. Er ist immer gleich
   gross, bei Ø18 wie bei Ø23.

3. Die Tasche geht quer durch - also genau in Richtung der Formtrennung.
   Jede Formhaelfte traegt einen Zapfen, beide treffen sich bei x = 0.
   Es braucht keinen eigenen Kern und keinen Schieber: das Werkzeug ist
   zwei Haelften plus ein glatter Zylinderkern fuer die Bohrung.

Die Schnur wird von der Seite eingefaedelt statt aus der Bohrung. Das
ist beim Montieren eher leichter - man sieht, was man tut.

Was es kostet
-------------

Bauhoehe. Die Tasche liegt jetzt unter dem Rohr statt daneben, das
Bauteil wird rund 3,5 mm hoeher. Und der Knoten ist von der Seite
sichtbar. Wer ihn verdecken will, setzt TASCHE_BLIND: dann bildet nur
eine Haelfte den Zapfen, die andere Seite bleibt geschlossen - immer
noch ein gerader Zug.

    python3 manschette_quertasche.py
"""

import math

from netz import (abweichung, offene_kanten, schreibe_stl, vernetzen, volumen,
                  weich_abziehen as _weich_abziehen,
                  weich_vereinen as _weich_vereinen)

import manschette as MA
from manschette import (D_INNEN, D_SCHNUR, EINLAUF, KANTE, LAENGE, R_AUSSEN,
                        R_INNEN, SCHNUR_SENK, VERRUNDUNG, WAND, WAND_ENDE,
                        _rundbox, _rundbox3, _ruecknahme)

# ---------------------------------------------------------------- Kiel ----

# Kielachse und -radius sind nicht frei waehlbar. Rohr- und Kielkreis
# muessen sich wirklich schneiden; haengt der Kiel nur am Bauch der
# weichen Vereinigung, wird der Hals duenn - und genau dort zieht die
# Schnur. Bei R = 6 und Achse 17 klaffen die Kreise um 0,36 mm, bei
# R = 7 und Achse 16 ueberlappen sie auf 9,7 mm Breite.
KIEL_ACHSE = 16.0       # Abstand der Kielachse von der Bohrungsachse
R_KIEL = 7.0            # Kielradius
KIEL_UNTEN = KIEL_ACHSE + R_KIEL
HOEHE = R_AUSSEN + KIEL_UNTEN

# ------------------------------------------------------------- Tasche -----

# Die Tasche liegt vollstaendig unter dem Rohrmantel: ihre Oberkante ist
# die Aussenflaeche des Rohres. Damit bleibt die Wand von r = 9 bis 12
# rundum stehen.
TASCHE_OBEN = -R_AUSSEN                 # -12,0
TASCHE_HOCH = 8.5                       # Knotenraum in der Hoehe
TASCHE_LANG = 12.0                      # in Richtung der Drueckerachse
TASCHE_ECK = 2.5
TASCHE_UNTEN = TASCHE_OBEN - TASCHE_HOCH
BODEN = KIEL_UNTEN - abs(TASCHE_UNTEN)  # Material unter der Tasche

# Blindtasche: Tiefe von der offenen Seite her. 0 = quer durch.
TASCHE_BLIND = 0.0

RASTER = 0.29
DATEI = "tuerzwerg-manschette-quertasche.stl"


def knotenfreiraum(d_druecker=20.0):
    """Unabhaengig vom Druecker - das ist der Punkt."""
    return TASCHE_HOCH


# --------------------------------------------------------------- Feld -----

def profil(x, y, z):
    """Rohr und Kiel, weich vereinigt - wie bisher."""
    return _weich_vereinen(
        math.hypot(x, y) - (R_AUSSEN - _ruecknahme(z)),
        math.hypot(x, y + KIEL_ACHSE) - R_KIEL, VERRUNDUNG)


def aussenfeld(x, y, z):
    wq = profil(x, y, z) + KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    return (min(max(wq, wz), 0.0)
            + math.hypot(max(wq, 0.0), max(wz, 0.0)) - KANTE)


def tasche(x, y, z):
    """Gerundete Box, quer durch den Kiel. In x unbegrenzt (oder bis
    TASCHE_BLIND, dann bleibt eine Seite stehen)."""
    mitte = (TASCHE_OBEN + TASCHE_UNTEN) / 2.0
    q = _rundbox(y - mitte, z - LAENGE / 2.0,
                 TASCHE_HOCH / 2.0, TASCHE_LANG / 2.0, TASCHE_ECK)
    if TASCHE_BLIND > 0.0:
        # von +x her gebohrt, bei x = R_KIEL - TASCHE_BLIND endet sie
        q = max(q, (R_KIEL - TASCHE_BLIND) - x)
    return q


def feld(x, y, z):
    d = max(aussenfeld(x, y, z),
            -(math.hypot(x, y) - (R_INNEN + max(0.0,
              EINLAUF - min(z, LAENGE - z)))))
    d = _weich_abziehen(d, tasche(x, y, z), 0.8)

    senk = min(SCHNUR_SENK, max(0.0, -y - (KIEL_UNTEN - SCHNUR_SENK)))
    schnur = math.hypot(x, z - LAENGE / 2.0) - (D_SCHNUR / 2.0 + senk)
    schnur = max(schnur, y - TASCHE_UNTEN)      # endet in der Tasche
    return max(d, -schnur)


def grenzen():
    return ((-R_AUSSEN - 2, R_AUSSEN + 2),
            (-KIEL_UNTEN - 2, R_AUSSEN + 2),
            (-1.5, LAENGE + 1.5))


# --------------------------------------------------------- Entformbarkeit --

def _r(lo, hi, s):
    return [lo + s * (i + 0.5) for i in range(int(round((hi - lo) / s)))]


def haelften_hinterschnitt(f, schritt=0.35):
    """Kommt die Formhaelfte bei x > 0 frei?

    Die Bedingung ist nicht "ein Materialstueck je Schnittlinie" - das
    waere zu streng. Ein Hohlraum, der an der Trennebene liegt, ist kein
    Hinterschnitt: die Haelfte fuellt ihn mit einem Zapfen und zieht ihn
    beim Oeffnen heraus. Genau so entstehen die Ø4-Schnurbohrung und die
    Quertasche.

    Hinterschnitten ist die Haelfte erst, wenn nach aussen hin Material,
    dann Luft, dann wieder Material kommt - dann liegt hinter dem Hohlraum
    noch Wand, und der Zapfen kaeme nicht heraus. Gezaehlt wird deshalb
    nur bei x > 0 und nur, ob mehr als EIN Materialstueck vorliegt.
    """
    xs = _r(0.0, 14.0, schritt)
    schlecht = ges = 0
    for y in _r(-KIEL_UNTEN - 1, R_AUSSEN + 1, schritt):
        for z in _r(0.0, LAENGE, schritt):
            reihe = [f(x, y, z) < 0.0 for x in xs]
            if not any(reihe):
                continue
            ges += 1
            stuecke = sum(1 for i in range(len(reihe))
                          if reihe[i] and (i == 0 or not reihe[i - 1]))
            if stuecke > 1:
                schlecht += 1
    return schlecht, ges


def kern_hinterschnitt(f, schritt=0.35):
    """Der Bohrungskern ist ein glatter Zylinder. Hinterschnitten ist er
    nur dort, wo der Hohlraum in ihn hineinragt - also nirgends, wenn die
    Tasche unter dem Rohrmantel bleibt."""
    bl = ges = 0
    zs = list(reversed(_r(0.0, LAENGE, schritt)))
    for x in _r(-11, 11, schritt):
        for y in _r(-KIEL_UNTEN - 1, R_AUSSEN + 1, schritt):
            if math.hypot(x, y) > R_INNEN:
                continue
            gesehen = False
            for z in zs:
                if f(x, y, z) < 0.0:
                    gesehen = True
                else:
                    ges += 1
                    if gesehen:
                        bl += 1
    return bl, ges


def mantel_geschlossen(f, schritt=0.3):
    """Auf wie viel der Laenge ist der Rohrmantel ein geschlossener Ring?

    Gemessen wird auf r = (R_INNEN + R_AUSSEN)/2 rundum: ist das Material
    dort ueber alle 360 Grad durchgehend, traegt der Ring Spannkraft.
    """
    rm = (R_INNEN + R_AUSSEN) / 2.0
    zu = ges = 0
    for z in _r(0.0, LAENGE, schritt):
        ges += 1
        voll = True
        for i in range(360):
            w = math.radians(i)
            if f(rm * math.sin(w), rm * math.cos(w), z) >= 0.0:
                voll = False
                break
        if voll:
            zu += 1
    return zu, ges


# ---------------------------------------------------------------- Lauf ----

if __name__ == "__main__":
    print("Entformbarkeit und Halt, heute gegen Quertasche")
    print(f"  {'':40s}{'heute':>10}{'neu':>10}")
    b1, g1 = haelften_hinterschnitt(MA.feld)
    b2, g2 = haelften_hinterschnitt(feld)
    print(f"  {'Formhaelften +-x, hinterschnitten':40s}"
          f"{f'{100*b1/g1:.1f} %':>10}{f'{100*b2/g2:.1f} %':>10}")
    k1, h1 = kern_hinterschnitt(MA.feld)
    k2, h2 = kern_hinterschnitt(feld)
    print(f"  {'Bohrungskern, hinterschnitten':40s}"
          f"{f'{100*k1/h1:.1f} %':>10}{f'{100*k2/h2:.1f} %':>10}")
    print(f"  {'Kerne / Schieber ausser dem Zylinder':40s}{'1 + 1':>10}{'0':>10}")
    m1, t1 = mantel_geschlossen(MA.feld)
    m2, t2 = mantel_geschlossen(feld)
    print(f"  {'Rohrmantel geschlossen (Laengenanteil)':40s}"
          f"{f'{100*m1/t1:.0f} %':>10}{f'{100*m2/t2:.0f} %':>10}")
    print()
    print("  Knotenraum, nach Drueckerdurchmesser:")
    for d in (18.0, 20.0, 23.0):
        print(f"    Ø{d:4.1f}{MA.knotenfreiraum(d):>16.1f} mm"
              f"{knotenfreiraum(d):>9.1f} mm")
    print()

    print("Vernetze ...")
    tri = vernetzen(feld, grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, DATEI, "Tuerzwerg Manschette Quertasche - mm")
    ab_max, ab_mit = abweichung(feld, tri)
    lo = [min(p[i] for d in tri for p in d) for i in range(3)]
    hi = [max(p[i] for d in tri for p in d) for i in range(3)]

    print(f"\nDatei          {DATEI}")
    print(f"  Dreiecke     {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Masse        {hi[0]-lo[0]:.2f} x {hi[1]-lo[1]:.2f} x "
          f"{hi[2]-lo[2]:.2f} mm   (heute 24,00 x 31,50 x 28,00)")
    print(f"  Volumen      {vol/1000:.3f} cm^3  ({vol/1000*1.15:.1f} g Silikon)")
    print(f"  Formtreue    hoechstens {ab_max*1000:.0f} um, im Mittel "
          f"{ab_mit*1000:.0f} um")
    print()
    print(f"  Tasche       {TASCHE_LANG:.0f} x {TASCHE_HOCH:.1f} mm, quer durch, "
          f"Eckradius {TASCHE_ECK:.1f}")
    print(f"  Boden        {BODEN:.1f} mm unter der Tasche, "
          f"Schnurloch Ø{D_SCHNUR:.1f}")
    print(f"  Kiel         Ø{2*R_KIEL:.0f}, Achse {KIEL_ACHSE:.1f} mm unter "
          f"der Bohrung")
    print(f"  Rohr         Ø{D_INNEN:.0f} innen, Wand {WAND:.1f} / "
          f"{WAND_ENDE:.1f} mm, Ring durchgehend geschlossen")
    print()
    print("Werkzeug:  zwei Haelften (Trennebene x = 0) + ein glatter")
    print("           Zylinderkern Ø18. Die Quertasche bilden die Haelften")
    print("           selbst, das Schnurloch liegt in der Trennebene.")
