#!/usr/bin/env python3
"""
Türzwerg – Klinkenmanschette
Erzeugt ein druckfertiges STL der Silikonmanschette, die auf den Tuerdruecker
geschoben wird und die Schnur aufnimmt.

Anders als der Griff ist die Manschette kein Drehkoerper: Rohr, Rippe,
Knotenkammer und Schnurbohrung muessen vereinigt und voneinander abgezogen
werden. Die Form wird deshalb als Distanzfeld beschrieben und mit Marching
Tetrahedra vernetzt. Das kostet Rechenzeit, liefert dafuer weiche Uebergaenge
zwischen Rohr und Rippe, die sich mit gestapelten Querschnitten nicht
erzeugen liessen.

Alle Masse in Millimetern. Anpassen und neu ausfuehren:
    python3 manschette.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl,
                  weich_vereinen as _weich_vereinen,
                  weich_abziehen as _weich_abziehen)

# ---------------------------------------------------------------- Parameter --

LAENGE = 28.0           # Laenge der Manschette entlang des Drueckers

# Innendurchmesser, durchgehend zylindrisch.
# DIN 18255 normt Tuerdruecker auf 20 mm, daneben gibt es 23 mm; die
# Barrierefreiheitsnormen fordern mindestens 19 mm. 18 mm sind also kein
# Passmass, sondern rund 11 Prozent Untermass - genau das soll eine
# Silikonmanschette haben, damit sie sich aufspannt.
D_INNEN = 18.0

# Wandstaerke. 2,0 mm sind beim Drucken genau fuenf Bahnen einer 0,4-mm-Duese.
# Krumme Vielfache sind bei TPU der haeufigste Grund fuer poroese Waende:
# der Slicer laesst dann zwischen den Bahnen eine Luecke, die er mit
# Lueckenfuellung zu schliessen versucht, was bei weichem Filament schlecht
# haelt.
WAND = 2.0
BAHN = 0.4              # angenommene Extrusionsbreite, nur zur Kontrolle

# Rippe an der Unterseite: nimmt die Knotenkammer auf und laeuft ueber die
# volle Laenge durch. Das ist nicht nur Optik - ein durchlaufendes Profil
# hat beim Drucken keine nach unten weisende Flaeche und braucht dadurch
# keine Stuetzen.
KAMMER_ACHSE = 11.0     # Abstand der Kammerachse von der Rohrachse
D_KAMMER = 11.0         # Knotenkammer
KAMMER_LAENGE = 10.0    # gerader Teil; mit den 45-Grad-Kegeln 21 mm gesamt,
                        # bleiben bei 28 mm Laenge 3,5 mm Wand an beiden Enden
RIPPE_WAND = 2.0        # Material um die Kammer herum

D_SCHNUR = 5.0          # Schnurbohrung nach aussen, rund
SCHNUR_SENK = 0.5       # 45-Grad-Senkung am aeusseren Ende, fuer die Schnur
VERRUNDUNG = 4.0        # weicher Uebergang Rohr zu Rippe

# Verrundung der Stirnkanten. Eine scharfe Kante laesst sich mit einem
# Gittervernetzer nicht sauber abbilden - sie faellt zwangslaeufig treppig
# aus, weil die Flaeche die Zellen schraeg durchlaeuft. Ein Radius von gut
# einer Zellbreite loest das, und an einer Silikonmanschette ist eine
# verrundete Kante ohnehin besser als eine scharfe Lippe.
KANTE = 1.2

# Anfasung der Bohrung an beiden Enden, damit sich die Manschette leichter
# auf den Druecker schieben laesst.
EINLAUF = 1.0

# Abgeleitet
R_INNEN = D_INNEN / 2.0
R_AUSSEN = R_INNEN + WAND
R_RIPPE = D_KAMMER / 2.0 + RIPPE_WAND
RIPPE_UNTEN = KAMMER_ACHSE + R_RIPPE           # tiefster Punkt der Rippe
HOEHE = R_AUSSEN + RIPPE_UNTEN                 # Gesamthoehe ueber alles

RASTER = 0.36           # Kantenlaenge der Gitterzelle
DATEI = "tuerzwerg-manschette.stl"


# ------------------------------------------------------------- Distanzfeld ---

def feld(x, y, z):
    """Signierter Abstand. Negativ bedeutet Material."""
    r = math.hypot(x, y)

    # Querschnitt: Rohr und Rippe, weich vereinigt. Haengt nicht von z ab.
    profil = _weich_vereinen(r - R_AUSSEN,
                             math.hypot(x, y + KAMMER_ACHSE) - R_RIPPE,
                             VERRUNDUNG)

    # Gerundete Extrusion: das Profil wird um KANTE geschrumpft, in z um
    # KANTE gekuerzt und der Koerper anschliessend wieder um KANTE
    # aufgedickt. Das ergibt an beiden Stirnkanten exakt einen Viertelkreis
    # statt einer scharfen Ecke.
    wq = profil + KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    koerper = (min(max(wq, wz), 0.0)
               + math.hypot(max(wq, 0.0), max(wz, 0.0)) - KANTE)

    # Durchgangsbohrung, an beiden Enden mit 45-Grad-Einlauf aufgeweitet
    rand = min(z, LAENGE - z)
    bohrung = r - (R_INNEN + max(0.0, EINLAUF - rand))

    # Knotenkanal: durchgehende Nut in der Rippe, oben zur Bohrung offen.
    #
    # Frueher war das eine geschlossene Tasche - runder Zylinder mit
    # 45-Grad-Kegelenden. Die liess sich drucken, aber nicht giessen: was
    # den Hohlraum bildet, sitzt danach darin fest. Jede Abhilfe an der
    # Form allein hat nur den naechsten Klemmpunkt freigelegt.
    #
    # Der Kanal ist deshalb in beide Richtungen offen:
    #
    # - nach oben: min(0, ...) macht aus dem Kreisquerschnitt ein U -
    #   untere Haelfte rund, darueber senkrechte Waende. Der Kanal ist
    #   damit an keiner Stelle breiter als seine Oeffnung.
    # - nach den Stirnseiten: kein Kegelende mehr, der Kanal laeuft durch.
    #   Der Querschnitt ist ueber die ganze Laenge gleich.
    #
    # Beides zusammen macht den Kanal zu einer geraden Nut. Gebildet wird
    # er dadurch nicht mehr von einem Losteil, sondern von einem Kiel an
    # den beiden Bohrungskernen, die ohnehin axial herausgezogen werden.
    # Es gibt kein gefangenes Formteil mehr.
    #
    # y als vierter Term deckelt den Kanal auf Hoehe der Bohrungsachse.
    # Ohne Deckel ist der Querschnitt nach oben unbegrenzt und saegt als
    # 11 mm breiter Schlitz quer durch die Rohrwand. y = 0 liegt sicher
    # in der Bohrung: bei |x| <= 5,5 ist deren Wand schon bei y = -7,1.
    #
    # Der Knoten verliert nichts: der Boden bleibt, wo er war, und
    # getragen wird der Knoten von diesem Boden rings um die
    # Schnurbohrung - die Schnur zieht nach unten. Geschlossen wird der
    # Kanal vom Tuerdruecker, der in der Bohrung darueber steckt.
    # Einfaedeln wird sogar leichter: der Knoten geht jetzt von der
    # Stirnseite hinein statt durch die Oeffnung gequetscht zu werden.
    rk = math.hypot(x, min(0.0, y + KAMMER_ACHSE))
    kammer = max(rk - D_KAMMER / 2.0, y)

    # Schnurbohrung. Scharf abgezogen und nach aussen leicht kegelig.
    #
    # Eine Verrundung am oberen Ende waere ein Wulst am Kiel, und der
    # zieht laengs - er wuerde den Kanalboden ueber die ganze Laenge
    # aufreissen. Nach unten dagegen darf sie sich oeffnen: dort zieht
    # der Schnurkern, und der geht nach unten vom Bauteil weg.
    senk = min(SCHNUR_SENK, max(0.0, -y - (RIPPE_UNTEN - SCHNUR_SENK)))
    schnur = math.hypot(x, z - LAENGE / 2.0) - (D_SCHNUR / 2.0 + senk)
    schnur = max(schnur, y + KAMMER_ACHSE)          # endet im Kanal

    # Bohrung scharf abziehen - sie ist eine Funktionsflaeche. Kammer und
    # Schnurkanal dagegen weich: Dort, wo die Kammer in die Bohrung
    # durchbricht, entstuende sonst eine scharfe Innenkante. Die ist am
    # Silikonteil eine Kerbe genau an der Stelle, an der der Knoten zieht -
    # und ein Gittervernetzer bildet sie ohnehin nur ungenau ab.
    d = max(koerper, -bohrung)
    d = _weich_abziehen(d, kammer, 0.8)
    d = max(d, -schnur)
    return d


def knotenfreiraum(d_druecker):
    """Radialer Platz, der dem Knoten unter einem Druecker bleibt.

    Die Bohrung wird vom Druecker aufgeweitet, seine Oberflaeche liegt also
    auf halbem Drueckerdurchmesser. Alles darunter bis zur Kammerunterseite
    steht dem Knoten zur Verfuegung.
    """
    return KAMMER_ACHSE + D_KAMMER / 2.0 - d_druecker / 2.0


if __name__ == "__main__":
    grenzen = ((-R_AUSSEN - 2, R_AUSSEN + 2),
               (-RIPPE_UNTEN - 2, R_AUSSEN + 2),
               (-1.5, LAENGE + 1.5))

    print("Vernetze ...")
    tri = vernetzen(feld, grenzen, RASTER)

    vol = volumen(tri)
    if vol < 0:                       # Wicklung global umdrehen
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol

    schreibe_stl(tri, DATEI, "Tuerzwerg Manschette - Masse in mm")
    anteil, grad, flaeche = ueberhang(tri)

    print(f"\nDatei          {DATEI}")
    print(f"Dreiecke       {len(tri)}")
    print(f"Offene Kanten  {offene_kanten(tri)}  (0 = geschlossenes Volumen)")
    print(f"Volumen        {vol/1000:.2f} cm^3   ({vol/1000*1.15:.1f} g Silikon)")
    print(f"Abmessungen    {2*R_AUSSEN:.1f} breit x {HOEHE:.1f} hoch x "
          f"{LAENGE:.0f} lang")
    print(f"Innen          {D_INNEN:.1f} mm durchgehend zylindrisch")
    print(f"Wand           {WAND:.1f} mm = {WAND/BAHN:.0f} Bahnen zu {BAHN} mm")
    print(f"Rippenwand     {RIPPE_WAND:.1f} mm = {RIPPE_WAND/BAHN:.0f} Bahnen")
    print(f"Knotenkanal    {D_KAMMER:.1f} mm breit, durchgehend, "
          f"Schnurbohrung {D_SCHNUR:.1f} mm")
    print(f"Oberflaeche    {flaeche/100:.1f} cm^2")
    print(f"Ueberhang      {anteil:.2f} % der Flaeche ueber 45 Grad")
    ab_max, ab_mit = abweichung(feld, tri)
    print(f"Formtreue      hoechstens {ab_max*1000:.0f} um von der Sollflaeche "
          f"entfernt, im Mittel {ab_mit*1000:.0f} um")
    print(f"Facettengroesse ca. {RASTER:.2f} mm")
    print()
    print("Platz fuer den Knoten unter dem Druecker:")
    for d in (18.0, 20.0, 23.0):
        f = knotenfreiraum(d)
        print(f"  Druecker {d:4.1f} mm  ->  {f:4.1f} mm")
    print("  Ein Knoten in 3-mm-Schnur braucht rund 7 mm, in 4-mm-Schnur rund 9.")
