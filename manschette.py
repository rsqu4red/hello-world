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
import sys

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

# Wandstaerke in der Mitte. 2,0 mm sind beim Drucken genau fuenf Bahnen einer
# 0,4-mm-Duese. Krumme Vielfache sind bei TPU der haeufigste Grund fuer
# poroese Waende: der Slicer laesst dann zwischen den Bahnen eine Luecke, die
# er mit Lueckenfuellung zu schliessen versucht, was bei weichem Filament
# schlecht haelt. Fuer die gegossene Silikonfassung gilt das Bahnenargument
# nicht mehr - dort zaehlt nur, dass die Form sich fuellt.
WAND = 2.0
BAHN = 0.4              # angenommene Extrusionsbreite, nur zur Kontrolle

# Abflachung zu den Stirnseiten hin.
#
# Ueber ABFLACHUNG laeuft die ganze Aussenkontur - Rohr und Rippe - von WAND
# auf WAND_ENDE zurueck. Der Uebergang vom blanken Druecker auf die Manschette
# ist damit kein Absatz von zwei Millimetern mehr, sondern eine Rampe.
#
# Zurueckgenommen wird die Aussenflaeche, nicht die Bohrung: die Ø18 bleibt
# ueber die volle Laenge zylindrisch, sie ist die Funktionsflaeche am Druecker.
# Die Rampe laeuft als Smoothstep, hat an beiden Enden also Steigung null und
# hinterlaesst weder am Mundstueck noch dort, wo sie in die volle Wand
# einlaeuft, eine Kante.
WAND_ENDE = 1.2
ABFLACHUNG = 6.0

# Rippe an der Unterseite: nimmt die Knotenkammer auf und laeuft ueber die
# volle Laenge durch. Das ist nicht nur Optik - ein durchlaufendes Profil
# hat beim Drucken keine nach unten weisende Flaeche und braucht dadurch
# keine Stuetzen.
KAMMER_ACHSE = 11.0     # Abstand der Kammerachse von der Rohrachse
D_KAMMER = 11.0         # Knotenkammer
KAMMER_LAENGE = 10.0    # gerader Teil; mit den 45-Grad-Kegeln 21 mm gesamt,
                        # bleiben bei 28 mm Laenge 3,5 mm Wand an beiden Enden

# Material um die Kammer herum. Haengt an WAND: wird die Manschette staerker,
# waechst die Rippe mit, sonst sitzt eine duenne Kammer in einem dicken Rohr.
RIPPE_WAND = WAND

D_SCHNUR = 5.0          # Schnurbohrung nach aussen, rund
SCHNUR_SENK = 0.5       # 45-Grad-Senkung am aeusseren Ende, fuer die Schnur
VERRUNDUNG = 4.0        # weicher Uebergang Rohr zu Rippe

# Verrundung der Stirnkanten. Eine scharfe Kante laesst sich mit einem
# Gittervernetzer nicht sauber abbilden - sie faellt zwangslaeufig treppig
# aus, weil die Flaeche die Zellen schraeg durchlaeuft. Ein Radius von gut
# einer Zellbreite loest das, und an einer Silikonmanschette ist eine
# verrundete Kante ohnehin besser als eine scharfe Lippe.
#
# Kleiner als frueher (1,2): die Stirnwand ist durch die Abflachung nur noch
# 1,2 mm dick, und ein Radius von 1,2 haette sie ganz weggerundet.
KANTE = 0.9

# Anfasung der Bohrung an beiden Enden, damit sich die Manschette leichter
# auf den Druecker schieben laesst. Ebenfalls kleiner als frueher (1,0) -
# die abgeflachte Aussenkontur uebernimmt jetzt den groesseren Teil der
# Einfuehrhilfe, und was von der Stirnwand uebrig bleibt, soll nicht von
# beiden Seiten gleichzeitig abgetragen werden.
EINLAUF = 0.5

# Wandstaerke laesst sich beim Aufruf ueberschreiben, um Varianten zu
# vergleichen:   python3 manschette.py 2.5
if len(sys.argv) > 1:
    WAND = float(sys.argv[1])
    RIPPE_WAND = WAND

# Abgeleitet
R_INNEN = D_INNEN / 2.0
R_AUSSEN = R_INNEN + WAND
R_RIPPE = D_KAMMER / 2.0 + RIPPE_WAND
RIPPE_UNTEN = KAMMER_ACHSE + R_RIPPE           # tiefster Punkt der Rippe
HOEHE = R_AUSSEN + RIPPE_UNTEN                 # Gesamthoehe ueber alles

RASTER = 0.36           # Kantenlaenge der Gitterzelle
DATEI = ("tuerzwerg-manschette.stl" if abs(WAND - 2.0) < 1e-9
         else f"tuerzwerg-manschette-wand{WAND:.1f}".replace(".", "") + ".stl")


# ------------------------------------------------------------- Distanzfeld ---

def _ruecknahme(z):
    """Wieviel die Aussenkontur an dieser Stelle zurueckgenommen wird.

    Null in der Mitte, WAND - WAND_ENDE an beiden Stirnseiten. Dazwischen
    ein Smoothstep, damit an keinem Ende der Rampe eine Kante steht.
    """
    s = min(z, LAENGE - z)
    if s >= ABFLACHUNG:
        return 0.0
    t = min(max(s, 0.0), ABFLACHUNG) / ABFLACHUNG
    return (WAND - WAND_ENDE) * (1.0 - t * t * (3.0 - 2.0 * t))


def feld(x, y, z):
    """Signierter Abstand. Negativ bedeutet Material."""
    r = math.hypot(x, y)

    # Querschnitt: Rohr und Rippe, weich vereinigt. Zu den Stirnseiten hin
    # wird das ganze Profil zurueckgenommen - ein positiver Summand auf ein
    # Distanzfeld schrumpft den Koerper genau um diesen Betrag, und zwar
    # senkrecht zur Flaeche, also an Rohr und Rippe gleich viel.
    profil = _weich_vereinen(r - R_AUSSEN,
                             math.hypot(x, y + KAMMER_ACHSE) - R_RIPPE,
                             VERRUNDUNG) + _ruecknahme(z)

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

    # Knotenkammer: Tasche in der Rippe, nach oben zur Bohrung offen.
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
    # - an den Stirnseiten geschlossen: 45-Grad-Kegel, 3,5 mm Wand. Der
    #   Knoten bleibt damit in der Kammer, statt im Kanal wandern zu
    #   koennen.
    #
    # Die Kegelenden verbieten es, die Kammer von einem Kiel an den
    # Bohrungskernen bilden zu lassen: ein axial gezogener Kiel verlangt,
    # dass die Kammer an der Stirnflaeche am tiefsten ist und nach innen
    # nur enger wird - eine Tasche ist genau umgekehrt. Die Kammer bekommt
    # deshalb einen eigenen Kern. Weil der Querschnitt aber ein U mit
    # senkrechten Waenden ist, haengt der an nichts fest: er geht gerade
    # nach oben in die Bohrung und dort axial heraus.
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
    # Eingefaedelt wird von oben, bevor der Druecker eingeschoben wird.
    rk = math.hypot(x, min(0.0, y + KAMMER_ACHSE))
    z_a = LAENGE / 2.0 - KAMMER_LAENGE / 2.0 - D_KAMMER / 2.0
    z_b = LAENGE / 2.0 + KAMMER_LAENGE / 2.0 + D_KAMMER / 2.0
    kammer = max(rk - D_KAMMER / 2.0, rk - (z - z_a), rk - (z_b - z), y)

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


def wand_bei(z, grad=0.0, rmax=30.0, schritt=0.004):
    """Wanddicke, radial gemessen, an dieser Stelle.

    Laeuft von der Bohrungsachse nach aussen und misst die Strecke, auf der
    das Feld negativ ist. Das ist die wirkliche Wand am fertigen Koerper,
    nicht die Differenz zweier Konstanten - Kantenverrundung, Einlauf und
    Abflachung sind darin enthalten. Genau daran ist die bisherige Fassung
    duenn: in der Mitte hat sie ihre 2,0 mm, am Mundstueck nicht.

    grad = 0 zeigt nach oben, also auf die dem Kiel gegenueberliegende Seite.
    """
    w = math.radians(grad)
    dx, dy = math.sin(w), math.cos(w)
    ein = None
    r = 0.0
    while r <= rmax:
        if feld(dx * r, dy * r, z) < 0.0:
            if ein is None:
                ein = r
        elif ein is not None:
            return r - ein
        r += schritt
    return 0.0 if ein is None else rmax - ein


def abmessungen(tri):
    """Umschliessender Quader des vernetzten Koerpers."""
    lo = [min(p[i] for d in tri for p in d) for i in range(3)]
    hi = [max(p[i] for d in tri for p in d) for i in range(3)]
    return [hi[i] - lo[i] for i in range(3)], lo, hi


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
    (bb, lo, hi) = abmessungen(tri)
    print()
    print("Masse ueber alles, am vernetzten Koerper gemessen")
    print(f"  Breite (x)   {bb[0]:6.2f} mm    Rohr aussen Ø{2*R_AUSSEN:.1f}")
    print(f"  Hoehe  (y)   {bb[1]:6.2f} mm    Rohrscheitel {R_AUSSEN:.1f} "
          f"ueber Achse, Kiel {RIPPE_UNTEN:.1f} darunter")
    print(f"  Tiefe  (z)   {bb[2]:6.2f} mm    Laenge entlang des Drueckers")
    print(f"  Bohrung      {D_INNEN:6.2f} mm    durchgehend zylindrisch")
    print()
    print("Wandstaerke, radial nachgemessen (0 Grad = oben, dem Kiel gegenueber)")
    for z, was in ((LAENGE / 2.0, "Mitte"),
                   (ABFLACHUNG, "Ende der Rampe"),
                   (ABFLACHUNG / 2.0, "Mitte der Rampe"),
                   (1.0, "1 mm vom Rand"),
                   (0.3, "0,3 mm vom Rand")):
        print(f"  z = {z:5.1f}  {was:<17}{wand_bei(z):5.2f} mm")
    print(f"  Soll: {WAND:.1f} in der Mitte, {WAND_ENDE:.1f} an der Stirnseite, "
          f"Rampe {ABFLACHUNG:.0f} mm")
    print(f"  Duese 0,4: Mitte {WAND/BAHN:.0f} Bahnen, "
          f"Kiel {RIPPE_WAND/BAHN:.0f} Bahnen")
    print(f"Knotenkammer   {D_KAMMER:.1f} x {KAMMER_LAENGE:.0f} mm, "
          f"Stirnwand {(LAENGE - KAMMER_LAENGE)/2 - D_KAMMER/2:.1f} mm, "
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
