#!/usr/bin/env python3
"""
Türzwerg – Der Reif

Ein Griff, der kein Drehkoerper ist. Alle bisherigen Entwuerfe waren
Varianten derselben senkrechten Achse: Kuppe, Schaft, Bauch. Der Reif
verlaesst diese Achse und macht aus dem Griff eine Oeffnung.

Der Gedanke dahinter ist nicht formal, sondern motorisch. Ein Zweijaehriger
muss eine Kugel treffen und umschliessen - beides braucht Zielgenauigkeit
und Handkraft. In einen Ring greift er nur hinein und haengt sich daran.
Das gelingt auch schief, mit zwei Fingern, mit der linken Hand, ohne
hinzusehen.

Geometrisch ist der Reif eine Rohrform entlang eines Kreises. Aussen bleibt
der Kreis exakt rund; die Wandstaerke waechst dort, wo die Schnur ansetzt,
und dort, wo die Hand zieht. Die Oeffnung innen wird dadurch von selbst zum
Ei - die Funktion formt die Innenkante, die Aussenkante bleibt unberuehrt.

Gedruckt wird flach liegend. Die Stirnflaechen sind deshalb mit 40 Grad
angefast statt verrundet: eine Verrundung waere an der Unterseite ein
Ueberhang, der in der ersten Schicht ueber einen Millimeter auskragt.

Alle Masse in Millimetern. Anpassen und neu ausfuehren:
    python3 reif.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, weich_abziehen)

# ---------------------------------------------------------------- Parameter --

R_AUSSEN = 36.0         # Aussenradius, ueber den ganzen Umfang konstant
DICKE = 14.0            # Staerke quer zur Reifebene = Bauhoehe beim Drucken

# Radiale Breite ueber dem Umfangswinkel, gemessen von oben (Schnurseite).
#   oben  19 mm  - Platz fuer Bohrung und Knotenkammer
#   seitlich 12 mm - die schlanke Stelle
#   unten 15 mm  - hier zieht die Hand, hier verteilt mehr Material den Druck
# Als Kosinusreihe angesetzt, damit der Verlauf ueberall knickfrei ist.
B_OBEN, B_SEITE, B_UNTEN = 19.0, 12.0, 15.0
A0 = (B_OBEN + 2.0 * B_SEITE + B_UNTEN) / 4.0
A1 = (B_OBEN - B_UNTEN) / 2.0
A2 = (B_OBEN - 2.0 * B_SEITE + B_UNTEN) / 4.0

# Querschnitt: senkrechte Wand, dann 40-Grad-Fase zur Stirnflaeche.
FASE_Z = 3.0            # Hoehe der Fase je Seite
FASE_GRAD = 40.0        # aus der Senkrechten
KANTE = 1.0             # Verrundung aller Querschnittsecken

# Schnuranschluss oben: Bohrung von aussen, Knotenkammer dahinter.
D_SCHNUR = 5.0
BOHR_TIEFE = 8.0                        # radiale Laenge der Bohrung
KAMMER_OBEN = R_AUSSEN - BOHR_TIEFE     # y, ab hier nach innen die Kammer
KAMMER_UNTEN = R_AUSSEN - B_OBEN - 1.0  # bricht in die Reifoeffnung durch

# Die Kammer bekommt denselben angefasten Querschnitt wie der Reif selbst.
# Das ist nicht nur Formsprache: der Kanal liegt beim Drucken waagerecht,
# seine Decke muss sich also selbst tragen. Ein runder Kanal haengt oben
# durch, eine 45-Grad-Raute laege genau auf den Gitterdiagonalen und liesse
# das Netz aufreissen - die 40-Grad-Fase loest beides.
A_KAMMER = 6.0          # halbe Breite in Umfangsrichtung
B_KAMMER = 4.5          # halbe Hoehe; laesst 2,5 mm Wand zur Stirnflaeche
FASE_Z_KAMMER = 3.5

RASTER = 0.45
DATEI = "tuerzwerg-griff-reif.stl"

# Abgeleitet
_CF = math.cos(math.radians(FASE_GRAD))
_SF = math.sin(math.radians(FASE_GRAD))
_HALB = DICKE / 2.0


def breite(cos_theta):
    """Radiale Breite des Reifs. cos_theta = 1 ist oben, -1 ist unten."""
    return A0 + A1 * cos_theta + A2 * (2.0 * cos_theta * cos_theta - 1.0)


def innenradius(cos_theta):
    return R_AUSSEN - breite(cos_theta)


# ------------------------------------------------------------- Querschnitt ---

def _strecke(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    t = ((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz)
    t = min(max(t, 0.0), 1.0)
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def _achteck(u, z, a, b, g):
    """Signierter Abstand zum konvexen Achteck mit den Halbmassen a und b
    und der Fasenebene u*cos + z*sin = g.

    Das Achteck ist zu beiden Achsen symmetrisch, deshalb genuegt der erste
    Quadrant: der naechstgelegene Randpunkt liegt bei einer konvexen,
    doppelt gespiegelten Form immer im selben Quadranten wie der Punkt.
    """
    U, Z = abs(u), abs(z)
    p1 = (0.0, b)
    p2 = ((g - b * _SF) / _CF, b)
    p3 = (a, (g - a * _CF) / _SF)
    p4 = (a, 0.0)
    rand = min(_strecke(U, Z, *p1, *p2),
               _strecke(U, Z, *p2, *p3),
               _strecke(U, Z, *p3, *p4))
    drin = U <= a and Z <= b and U * _CF + Z * _SF <= g
    return -rand if drin else rand


# ------------------------------------------------------------- Distanzfeld ---

def feld(x, y, z):
    """Signierter Abstand. Negativ bedeutet Material.

    z = 0 ist das Druckbett, die Reifebene liegt bei z = DICKE/2.
    """
    zz = z - _HALB
    rho = math.hypot(x, y)
    if rho < 1e-9:
        rho = 1e-9

    a = breite(y / rho) / 2.0
    u = rho - (R_AUSSEN - a)        # Abstand von der Mittellinie des Rohrs

    # Geschrumpftes Achteck, anschliessend wieder aufgedickt: das verrundet
    # alle Ecken mit genau KANTE, ohne dass die Fasen ihren Winkel aendern.
    g = (a * _CF + (_HALB - FASE_Z) * _SF) - KANTE
    koerper = _achteck(u, zz, a - KANTE, _HALB - KANTE, g) - KANTE

    # Schnurbohrung: Zylinder entlang y, rund, von aussen bis zur Kammer.
    bohrung = max(math.hypot(x, zz) - D_SCHNUR / 2.0, KAMMER_OBEN - y)

    # Knotenkammer: liegender Kanal entlang y, angefasster Querschnitt.
    gk = (A_KAMMER * _CF + (B_KAMMER - FASE_Z_KAMMER) * _SF) - KANTE
    quer = _achteck(x, zz, A_KAMMER - KANTE, B_KAMMER - KANTE, gk) - KANTE
    kammer = max(quer, y - KAMMER_OBEN, KAMMER_UNTEN - y)

    d = max(koerper, -bohrung)
    return weich_abziehen(d, kammer, 0.8)


# -------------------------------------------------------------- Kennzahlen ---

def umfang(cos_theta, n=720):
    """Umfang des Querschnitts - das Mass, das die Kinderhand umgreift."""
    a = breite(cos_theta) / 2.0
    g = a * _CF + (_HALB - FASE_Z) * _SF
    ecken = [(0.0, _HALB), ((g - _HALB * _SF) / _CF, _HALB),
             (a, (g - a * _CF) / _SF), (a, 0.0)]
    lang = sum(math.dist(ecken[i], ecken[i + 1]) for i in range(3))
    # Die Verrundung kuerzt jede Ecke und ersetzt sie durch einen Bogen.
    # Fuer die Groessenordnung genuegt der Polygonzug.
    return 4.0 * lang


def engste_oeffnung():
    """Kleinste Kreisoeffnung, durch die das Teil passt.

    Der Reif ist flach: die kleinste Silhouette sieht man von der Kante her,
    sie misst Aussendurchmesser mal Dicke. Massgeblich ist die groessere der
    beiden Zahlen - kleiner wird die Oeffnung nicht, durch die er passt.
    """
    return 2.0 * R_AUSSEN


if __name__ == "__main__":
    grenzen = ((-R_AUSSEN - 2, R_AUSSEN + 2),
               (-R_AUSSEN - 2, R_AUSSEN + 2),
               (-1.5, DICKE + 1.5))

    print("Vernetze ...")
    tri = vernetzen(feld, grenzen, RASTER)

    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol

    schreibe_stl(tri, DATEI, "Tuerzwerg Der Reif - Masse in mm")
    anteil, grad, flaeche = ueberhang(tri)
    ab_max, ab_mit = abweichung(feld, tri)

    oeff_h = 2.0 * innenradius(0.0)
    oeff_v = innenradius(1.0) + innenradius(-1.0)

    print(f"\nDatei          {DATEI}")
    print(f"Dreiecke       {len(tri)}")
    print(f"Offene Kanten  {offene_kanten(tri)}  (0 = geschlossenes Volumen)")
    print(f"Volumen        {vol/1000:.1f} cm^3   ({vol/1000*1.24:.0f} g PLA, "
          f"{vol/1000*1.15:.0f} g Silikon)")
    print(f"Abmessungen    {2*R_AUSSEN:.0f} x {2*R_AUSSEN:.0f} x {DICKE:.0f} mm")
    print(f"Oeffnung       {oeff_h:.1f} breit x {oeff_v:.1f} hoch")
    print(f"Querschnitt    {breite(-1.0):.0f} x {DICKE:.0f} mm unten, "
          f"{breite(0.0):.0f} x {DICKE:.0f} seitlich, "
          f"{breite(1.0):.0f} x {DICKE:.0f} oben")
    print(f"Griffumfang    {umfang(-1.0):.0f} mm unten, "
          f"{umfang(0.0):.0f} mm seitlich")
    print(f"Kammer         {2*A_KAMMER:.0f} x {2*B_KAMMER:.0f} mm Querschnitt, "
          f"{KAMMER_OBEN-KAMMER_UNTEN:.0f} mm tief, Wand {_HALB-B_KAMMER:.1f} mm")
    print(f"Oberflaeche    {flaeche/100:.1f} cm^2")
    print(f"Ueberhang      {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.1f} Grad")
    print(f"Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facettengroesse ca. {RASTER:.2f} mm")

    e = engste_oeffnung()
    print(f"\nKleinteilepruefung")
    print(f"  Engste Oeffnung {e:.1f} mm")
    print(f"  Kleinball 44,5 mm      {'besteht' if e > 44.5 else 'faellt durch'}")
    print(f"  Zylinder 31,7 x 57,1   "
          f"{'besteht' if 2*R_AUSSEN > 31.7 else 'faellt durch'}")
    print(f"  Reifoeffnung {oeff_v:.0f}-{oeff_h:.0f} mm: zu gross fuer eine "
          f"Fingerklemme (5-12 mm),")
    print(f"  zu klein fuer eine Kopfklemme (ab etwa 95 mm).")
