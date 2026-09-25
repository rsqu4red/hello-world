#!/usr/bin/env python3
"""
Türzwerg – Klinkenmanschette, spritzgussgerecht

Das Problem, das der Werkzeugbauer meldet
------------------------------------------

Die heutige Manschette hat die Knotenkammer als geschlossene Tasche: ein
Kanal von 21 mm Laenge mit 3,5 mm Stirnwand an beiden Enden, nach oben
in die Ø18-Bohrung offen. Fuer den Druck ist das gut, fuer ein
Spritzgusswerkzeug ist es der teuerste Fall, den es gibt.

Der Grund laesst sich nachrechnen (entformbarkeit() weiter unten): von
den Hohlraumpunkten im Bauteil sind 19,7 Prozent gegenueber einem axial
gezogenen Kern hinterschnitten. Anders gesagt - ein Kern, der die
Bohrung und die Kammer zugleich bildet, kommt nicht heraus, weil die
Stirnwaende im Weg stehen.

Damit bleiben nur zwei Kerne mit verschiedenen Zugrichtungen:

  1. der Bohrungskern, axial in z,
  2. der Kammerkern, der zuerst nach oben (+y) in die Bohrung ausweichen
     muss und erst dann axial heraus kann.

Der zweite steckt dabei in dem Raum, den der erste ausfuellt. Die beiden
muessen also nacheinander bewegt werden, in einem Bauteil von 28 mm
Laenge. Das ist ein Schieber mit Zwangsfuehrung im Kern - machbar, aber
es verdoppelt den Werkzeugpreis und kostet Zykluszeit, und bei LSR
bedeutet jede zusaetzliche Trennstelle zusaetzlichen Grat.

Die Aenderung
-------------

Die Stirnwaende entfallen. Der Kanal laeuft durch.

Damit bilden Bohrung und Kanal zusammen EINEN Hohlraum mit ueber die
ganze Laenge gleichem Querschnitt - einen Zylinder mit angehaengtem
Kiel. Der laesst sich in einem Zug axial herausziehen. Das Werkzeug ist
dann: zwei Haelften, die bei x = 0 trennen, und ein gerader Kern.

Die Schnurbohrung braucht dabei keinen eigenen Kern: ihre Achse liegt in
der Trennebene x = 0. Jede Haelfte traegt einen Halbzylinder von 2 mm
Radius, beide zusammen bilden das Ø4-Loch, und beim Oeffnen fahren sie
seitlich heraus.

Was das kostet
--------------

Der Knoten kann im Kanal laengs wandern. Er kann nicht herausfallen -
nach oben schliesst der Tuerdruecker den Kanal, nach unten haelt ihn die
Ø4-Bohrung -, aber er ist nicht mehr zwischen zwei Waenden gefangen.

Praktisch traegt das wenig: unter Zug zieht die Schnur den Knoten auf
die Bohrung, er zentriert sich also selbst. Wandern kann er nur im
lastfreien Zustand, und auch dann muesste die Manschette vom Druecker
ab, damit er herauskommt.

Wer den Anschlag behalten will, nimmt STIRNWAND > 0: dann bleibt EIN
Ende geschlossen und der Kern wird zur anderen Seite gezogen. Auch das
ist ein gerader Zug.

Zusaetzlich bekommt der Kanal eine Entformschraege (ZUG). Silikon
entformt zwar auch ohne, aber der Werkzeugbauer wird danach fragen.

    python3 manschette_spritzguss.py
"""

import math

from netz import (abweichung, offene_kanten, schreibe_stl, vernetzen, volumen,
                  weich_abziehen as _weich_abziehen,
                  weich_vereinen as _weich_vereinen)

import manschette as MA
from manschette import (D_INNEN, D_KAMMER, D_SCHNUR, ECK_KAMMER, EINLAUF,
                        KANTE, LAENGE, RIPPE_WAND, R_AUSSEN, R_INNEN,
                        SCHNUR_SENK, VERRUNDUNG, WAND, WAND_ENDE,
                        _rundbox, _ruecknahme)

# Stirnwand am geschlossenen Ende. 0 = Kanal beidseits offen, Kern kann
# nach beiden Seiten gezogen werden. Ein Wert > 0 laesst ein Ende stehen;
# der Kern wird dann zur offenen Seite gezogen.
STIRNWAND = 0.0

# Entformschraege des Kanals, gesamt ueber die Laenge, je Seite. Der Kanal
# ist an der Ziehseite (z = 0) am weitesten. Der Kern wird also zu z = 0
# gezogen - andersherum sind die Schraege und der Kern gegeneinander, und
# aus 0,03 Prozent Resthinterschnitt werden 0,80.
ZUG = 0.25

# Abstand der Kanalachse von der Bohrungsachse.
#
# 11,0 ist der heutige Wert. Damit bleiben unter einem Ø20-Druecker nur
# 6,5 mm fuer den Knoten, und ein Sackstich in 4-mm-Schnur braucht rund 9.
# Das war schon vor dieser Aenderung offen; wenn ohnehin umkonstruiert
# wird, gehoert es mit erledigt. 13,5 bringt die 9,0 mm, kostet 2,5 mm
# Bauhoehe und laesst die Wand unter dem Kanal unveraendert bei 3,0 mm.
KANAL_ACHSE = 13.5

R_RIPPE = D_KAMMER / 2.0 + RIPPE_WAND
RIPPE_UNTEN = KANAL_ACHSE + R_RIPPE
HOEHE = R_AUSSEN + RIPPE_UNTEN


def knotenfreiraum(d_druecker=20.0):
    """Radialer Platz unter dem Druecker, der dem Knoten bleibt."""
    return KANAL_ACHSE + D_KAMMER / 2.0 - d_druecker / 2.0

RASTER = 0.29
DATEI = "tuerzwerg-manschette-spritzguss.stl"


# ------------------------------------------------------------- Kanalfeld ---

def _weich_max(a, b, k):
    """Verrundeter Schnitt. Smooth-min mit umgedrehten Vorzeichen."""
    return -_weich_vereinen(-a, -b, k)


def kanal(x, y, z):
    """Der Knotenkanal: derselbe Querschnitt wie die heutige Kammer, aber
    durchlaufend und mit Entformschraege.

    yk = min(0, y + KANAL_ACHSE) macht daraus wie bisher ein U - unten
    rund, darueber senkrechte Waende bis zur Bohrungsachse. Der Kanal ist
    damit an keiner Stelle breiter als seine Oeffnung, und genau das
    erlaubt es, ihn zusammen mit der Bohrung von einem Kern bilden zu
    lassen.
    """
    yk = min(0.0, y + KANAL_ACHSE)
    a = D_KAMMER / 2.0 - ZUG * (z / LAENGE)
    q = _rundbox(x, yk, a, D_KAMMER / 2.0, ECK_KAMMER)
    if STIRNWAND > 0.0:
        q = _weich_max(q, z - (LAENGE - STIRNWAND), ECK_KAMMER)
    return max(q, y)


def feld(x, y, z):
    """Wie manschette.feld, nur mit durchlaufendem Kanal."""
    r = math.hypot(x, y)

    profil = _weich_vereinen(r - (R_AUSSEN - _ruecknahme(z)),
                             math.hypot(x, y + KANAL_ACHSE) - R_RIPPE,
                             VERRUNDUNG)
    wq = profil + KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    koerper = (min(max(wq, wz), 0.0)
               + math.hypot(max(wq, 0.0), max(wz, 0.0)) - KANTE)

    rand = min(z, LAENGE - z)
    bohrung = r - (R_INNEN + max(0.0, EINLAUF - rand))

    senk = min(SCHNUR_SENK, max(0.0, -y - (RIPPE_UNTEN - SCHNUR_SENK)))
    schnur = math.hypot(x, z - LAENGE / 2.0) - (D_SCHNUR / 2.0 + senk)
    schnur = max(schnur, y + KANAL_ACHSE)

    d = max(koerper, -bohrung)
    d = _weich_abziehen(d, kanal(x, y, z), 0.8)
    return max(d, -schnur)


def profil(x, y, z):
    """Der Querschnitt: Rohr und Rippe, weich vereinigt."""
    return _weich_vereinen(math.hypot(x, y) - (R_AUSSEN - _ruecknahme(z)),
                           math.hypot(x, y + KANAL_ACHSE) - R_RIPPE,
                           VERRUNDUNG)


def kanal_halbbreite(z):
    return D_KAMMER / 2.0 - ZUG * (z / LAENGE)


def aussenfeld(x, y, z):
    """Nur die Aussenkontur, ohne Bohrung, Kanal und Schnurloch. Das ist
    die Flaeche, die die beiden Formhaelften bilden."""
    profil = _weich_vereinen(math.hypot(x, y) - (R_AUSSEN - _ruecknahme(z)),
                             math.hypot(x, y + KANAL_ACHSE) - R_RIPPE,
                             VERRUNDUNG)
    wq = profil + KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    return (min(max(wq, wz), 0.0)
            + math.hypot(max(wq, 0.0), max(wz, 0.0)) - KANTE)


# --------------------------------------------------------- Entformbarkeit --

def _raster(lo, hi, schritt):
    n = int(round((hi - lo) / schritt))
    return [lo + schritt * (i + 0.5) for i in range(n)]


def kern_hinterschnitt(f, aussen, richtung=-1, schritt=0.4):
    """Anteil der Hohlraumpunkte, die einem axial gezogenen Kern im Weg
    liegen.

    Ein Punkt ist hinterschnitten, wenn zwischen ihm und dem Ende, zu dem
    der Kern gezogen wird, noch Material steht. Null heisst: Bohrung und
    Kanal lassen sich von einem einzigen geraden Kern bilden.
    """
    hohl = blockiert = 0
    zs = _raster(0.0, LAENGE, schritt)
    if richtung > 0:
        zs = list(reversed(zs))
    for x in _raster(-11.0, 11.0, schritt):
        for y in _raster(-21.0, 13.0, schritt):
            gesehen = False
            for z in zs:
                if f(x, y, z) < 0.0:
                    gesehen = True
                elif aussen(x, y, z) < 0.0:
                    hohl += 1
                    if gesehen:
                        blockiert += 1
    return blockiert, hohl


def haelften_hinterschnitt(aussen, schritt=0.4):
    """Anteil der Schnittlinien, auf denen die Aussenkontur in x mehr als
    ein Materialstueck hat. Null heisst: zwei Haelften, die bei x = 0
    trennen, kommen von der Aussenflaeche ohne Schieber frei."""
    xs = _raster(-13.5, 13.5, schritt)
    schlecht = ges = 0
    for y in _raster(-21.0, 13.0, schritt):
        for z in _raster(0.0, LAENGE, schritt):
            reihe = [aussen(x, y, z) < 0.0 for x in xs]
            if not any(reihe):
                continue
            ges += 1
            if sum(1 for i in range(1, len(reihe))
                   if reihe[i] != reihe[i - 1]) > 2:
                schlecht += 1
    return schlecht, ges


def MA_grenzen():
    return ((-R_AUSSEN - 2, R_AUSSEN + 2),
            (-MA.RIPPE_UNTEN - 2, R_AUSSEN + 2),
            (-1.5, LAENGE + 1.5))


def grenzen():
    return ((-R_AUSSEN - 2, R_AUSSEN + 2),
            (-RIPPE_UNTEN - 2, R_AUSSEN + 2),
            (-1.5, LAENGE + 1.5))


# ---------------------------------------------------------------- Lauf ----

def bericht():
    """Die Zahlen, auf die es beim Werkzeug ankommt."""
    z = {}
    z["kern_heute"] = kern_hinterschnitt(MA.feld, aussenfeld)
    z["kern_neu"] = kern_hinterschnitt(feld, aussenfeld)
    z["haelften"] = haelften_hinterschnitt(aussenfeld)
    return z


if __name__ == "__main__":
    print("Entformbarkeit: heutige Fassung gegen durchlaufenden Kanal")
    print(f"  {'':38s}{'heute':>10}{'neu':>10}")
    a1, g1 = kern_hinterschnitt(MA.feld, aussenfeld)
    a2, g2 = kern_hinterschnitt(feld, aussenfeld)
    print(f"  {'ein Kern axial, hinterschnitten':38s}"
          f"{f'{100*a1/g1:.1f} %':>10}{f'{100*a2/g2:.2f} %':>10}")
    b1, h1 = haelften_hinterschnitt(MA.aussenfeld if hasattr(MA, 'aussenfeld')
                                    else aussenfeld)
    print(f"  {'Formhaelften +-x, hinterschnitten':38s}"
          f"{f'{100*b1/h1:.1f} %':>10}{f'{100*b1/h1:.1f} %':>10}")
    print(f"  {'Kerne mit eigener Bewegung':38s}{'2':>10}{'1':>10}")
    print(f"  {'Schieber im Kern':38s}{'ja':>10}{'nein':>10}")
    print()
    print(f"  Der Kern wird zu z = 0 gezogen, zur weiten Seite der")
    print(f"  Entformschraege. Andersherum blieben 0,80 Prozent stehen.")
    print()
    print(f"  Knotenfreiraum unter Ø20-Druecker: {knotenfreiraum(20.0):.1f} mm "
          f"(heute {MA.knotenfreiraum(20.0):.1f} mm, gebraucht rund 9)")
    for d in (18.0, 20.0, 23.0):
        print(f"    Druecker {d:4.1f} -> {knotenfreiraum(d):4.1f} mm")
    print()

    print("Vernetze ...")
    tri = vernetzen(feld, grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, DATEI, "Tuerzwerg Manschette spritzgussgerecht - mm")
    ab_max, ab_mit = abweichung(feld, tri)

    tri_alt = vernetzen(MA.feld, MA_grenzen(), RASTER)
    vol_alt = abs(volumen(tri_alt))
    lo = [min(p[i] for d in tri for p in d) for i in range(3)]
    hi = [max(p[i] for d in tri for p in d) for i in range(3)]

    print(f"\nDatei          {DATEI}")
    print(f"  Dreiecke     {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Masse        {hi[0]-lo[0]:.2f} x {hi[1]-lo[1]:.2f} x "
          f"{hi[2]-lo[2]:.2f} mm  (heute 24,00 x 31,50 x 28,00)")
    print(f"  Volumen      {vol/1000:.3f} cm^3  (heute {vol_alt/1000:.3f}, "
          f"{100*(vol-vol_alt)/vol_alt:+.1f} %)")
    print(f"  Silikon      {vol/1000*1.15:.1f} g je Teil "
          f"(heute {vol_alt/1000*1.15:.1f} g)")
    print(f"  Formtreue    hoechstens {ab_max*1000:.0f} um, im Mittel "
          f"{ab_mit*1000:.0f} um")
    print()
    print(f"  Kanal        {D_KAMMER:.1f} mm breit, durchlaufend, Achse "
          f"{KANAL_ACHSE:.1f} mm unter der Bohrung")
    print(f"  Schraege     {math.degrees(math.atan(ZUG/LAENGE)):.1f} Grad, "
          f"Kern zieht zu z = 0")
    print(f"  Wand         {WAND:.1f} mm Mitte, {WAND_ENDE:.1f} mm Stirnseite, "
          f"{RIPPE_WAND:.1f} mm unter dem Kanal")
    print()
    print("Werkzeug:  zwei Haelften (Trennebene x = 0) + ein gerader Kern")
    print("           (Zylinder Ø18 mit Kiel, gezogen zu z = 0).")
    print("           Das Schnurloch liegt in der Trennebene und braucht")
    print("           keinen eigenen Kern - je eine Halbschale je Haelfte.")
