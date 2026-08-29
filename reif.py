#!/usr/bin/env python3
"""
Türzwerg – Der Reif

Ein Griff, der kein Drehkoerper ist. Alle Entwuerfe davor waren Varianten
derselben senkrechten Achse: Kuppe, Schaft, Bauch. Der Reif verlaesst diese
Achse und macht aus dem Griff eine Oeffnung.

Der Gedanke dahinter ist motorisch, nicht formal. Ein Zweijaehriger muss
eine Kugel treffen und umschliessen - beides braucht Zielgenauigkeit und
Handkraft. In einen Ring greift er nur hinein und haengt sich daran. Das
gelingt auch schief, mit zwei Fingern, mit der linken Hand, ohne hinzusehen.

Geometrisch ist der Reif eine Rohrform entlang eines Kreises. Aussen bleibt
der Kreis exakt rund; die Bandbreite waechst nach innen, wo Material
gebraucht wird - oben fuer Bohrung und Knotenkammer, unten fuer die
Zughand. Die Oeffnung wird dadurch von selbst zum Ei; die Funktion formt
die Innenkante, die Silhouette bleibt unberuehrt.

Gedruckt wird flach liegend. Die Stirnflaechen sind deshalb mit 40 Grad
angefast statt verrundet: eine Verrundung waere an der Unterseite ein
Ueberhang, der in der ersten Schicht ueber einen Millimeter auskragt.

Alle Masse in Millimetern. Anpassen und neu ausfuehren:
    python3 reif.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, weich_abziehen)

FASE_GRAD = 40.0        # Fasenwinkel aus der Senkrechten, fuer alle Varianten
KANTE = 1.0             # Verrundung aller Querschnittsecken
D_SCHNUR = 5.0

_CF = math.cos(math.radians(FASE_GRAD))
_SF = math.sin(math.radians(FASE_GRAD))

D_FINGER = 11.0         # Fingerdurchmesser eines Dreijaehrigen, Anhaltswert
RASTER = 0.45


class Reif:
    """Ein Reif. Alles andere folgt aus diesen sieben Massen."""

    def __init__(self, name, titel, datei, r_aussen, dicke,
                 b_oben, b_seite, b_unten, bohr_tiefe, b_kammer, notiz):
        self.name, self.titel, self.datei = name, titel, datei
        self.r_aussen, self.dicke = r_aussen, dicke
        self.b_oben, self.b_seite, self.b_unten = b_oben, b_seite, b_unten
        self.notiz = notiz

        # Bandbreite ueber dem Umfangswinkel als Kosinusreihe. Sie trifft die
        # drei Vorgaben exakt und ist ueberall knickfrei - es gibt keine
        # Stelle, an der die Verdickung "anfaengt".
        self.a0 = (b_oben + 2.0 * b_seite + b_unten) / 4.0
        self.a1 = (b_oben - b_unten) / 2.0
        self.a2 = (b_oben - 2.0 * b_seite + b_unten) / 4.0

        self.halb = dicke / 2.0
        self.fase_z = 3.0
        self.kammer_oben = r_aussen - bohr_tiefe
        self.kammer_unten = r_aussen - b_oben - 1.0   # bricht innen durch
        self.b_kammer = b_kammer
        self.a_kammer = 5.5
        self.fase_z_kammer = b_kammer - 1.0

    # ------------------------------------------------------------ Kontur ----

    def breite(self, cos_theta):
        """Bandbreite. cos_theta = 1 ist oben, -1 ist unten."""
        return (self.a0 + self.a1 * cos_theta
                + self.a2 * (2.0 * cos_theta * cos_theta - 1.0))

    def innenradius(self, cos_theta):
        return self.r_aussen - self.breite(cos_theta)

    def oeffnung(self, n=2000):
        """Groesste waagerechte Weite der Oeffnung und ihre Hoehe.

        Die schmalste Bandstelle liegt nicht genau seitlich, sondern etwas
        darunter; die breiteste Stelle der Oeffnung ist deshalb nicht der
        waagerechte Durchmesser. Gesucht ist die laengste waagerechte Sehne.
        """
        breit = hoehe_bei = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            r = self.innenradius(math.cos(th))
            x, y = r * math.sin(th), r * math.cos(th)
            # Die Kontur ist zur Senkrechten symmetrisch: die Sehne auf der
            # Hoehe y ist genau 2x breit.
            if 2.0 * x > breit:
                breit, hoehe_bei = 2.0 * x, y
        hoch = self.innenradius(1.0) + self.innenradius(-1.0)
        return breit, hoch, hoehe_bei

    def finger(self):
        """Wie viele Kinderfinger nebeneinander durch die Oeffnung passen."""
        breit, _, _ = self.oeffnung()
        return breit / D_FINGER

    # -------------------------------------------------------- Querschnitt ---

    def _g(self, a):
        return a * _CF + (self.halb - self.fase_z) * _SF

    def flaeche(self, cos_theta):
        """Querschnittsflaeche - fuer die Abschaetzung von Masse und Steifigkeit."""
        a = self.breite(cos_theta) / 2.0
        voll = 2.0 * a * self.dicke
        weg = self.fase_z * (self.fase_z / math.tan(math.radians(90 - FASE_GRAD)))
        return voll - 2.0 * weg

    def widerstand(self, cos_theta):
        """Widerstandsmoment gegen Biegung in der Reifebene."""
        b = self.breite(cos_theta)
        return self.dicke * b * b / 6.0

    # ------------------------------------------------------- Distanzfeld ----

    def feld(self, x, y, z):
        """Signierter Abstand. Negativ ist Material. z = 0 ist das Druckbett."""
        zz = z - self.halb
        rho = math.hypot(x, y)
        if rho < 1e-9:
            rho = 1e-9

        a = self.breite(y / rho) / 2.0
        u = rho - (self.r_aussen - a)     # Abstand von der Bandmittellinie

        # Geschrumpftes Achteck, danach wieder aufgedickt: das verrundet alle
        # Ecken mit genau KANTE, ohne dass die Fasen ihren Winkel aendern.
        koerper = _achteck(u, zz, a - KANTE, self.halb - KANTE,
                           self._g(a) - KANTE) - KANTE

        bohrung = max(math.hypot(x, zz) - D_SCHNUR / 2.0, self.kammer_oben - y)

        # Knotenkammer: liegender Kanal entlang y mit demselben angefasten
        # Querschnitt. Das ist nicht nur Formsprache - der Kanal liegt beim
        # Drucken waagerecht, seine Decke muss sich selbst tragen. Ein runder
        # Kanal haengt durch, eine 45-Grad-Raute laege genau auf den
        # Gitterdiagonalen und liesse das Netz aufreissen.
        gk = (self.a_kammer * _CF
              + (self.b_kammer - self.fase_z_kammer) * _SF) - KANTE
        quer = _achteck(x, zz, self.a_kammer - KANTE, self.b_kammer - KANTE,
                        gk) - KANTE
        kammer = max(quer, y - self.kammer_oben, self.kammer_unten - y)

        return weich_abziehen(max(koerper, -bohrung), kammer, 0.8)

    def grenzen(self):
        r = self.r_aussen + 2.0
        return ((-r, r), (-r, r), (-1.5, self.dicke + 1.5))


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
    Quadrant: bei einer konvexen, doppelt gespiegelten Form liegt der
    naechstgelegene Randpunkt immer im selben Quadranten wie der Punkt.
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


# ---------------------------------------------------------------- Varianten --

# Rev. A - der erste Wurf. Kompaktes Aussenmass, dafuer eine Oeffnung, durch
# die vier Kinderfinger nur ohne jedes Spiel passen.
REV_A = Reif("a", "Der Reif · Rev. A", "tuerzwerg-griff-reif-a.stl",
             r_aussen=36.0, dicke=14.0,
             b_oben=19.0, b_seite=12.0, b_unten=15.0,
             bohr_tiefe=8.0, b_kammer=4.5,
             notiz="Kompakt, aber die Oeffnung ist knapp.")

# Rev. B - Oeffnung auf gut 60 mm. Erreicht nicht durch ein groesseres
# Aussenmass, sondern durch ein schlankeres Band: der Reif wird gehakt, nicht
# umfasst, und die Biegespannung liegt selbst bei 80 N Zug bei 3,5 MPa gegen
# rund 50 MPa Streckgrenze. Der Faktor 14 ist Platz genug, um Material aus
# dem Band herauszunehmen und der Hand zu geben. Dass das Band dabei tiefer
# als breit wird, passt zum Griff: der Finger hakt ueber die schmale Kante
# und liegt dabei auf der ganzen Tiefe auf.
REV_B = Reif("b", "Der Reif · Rev. B", "tuerzwerg-griff-reif.stl",
             r_aussen=39.0, dicke=15.0,
             b_oben=16.0, b_seite=8.0, b_unten=11.0,
             bohr_tiefe=6.0, b_kammer=4.5,
             notiz="Oeffnung 61 mm, schlankeres Band, leichter als Rev. A.")

VARIANTEN = [REV_A, REV_B]


# ------------------------------------------------------------------ Lauf -----

def baue(r, still=False):
    tri = vernetzen(r.feld, r.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, r.datei, "Tuerzwerg %s - Masse in mm" % r.titel)

    anteil, grad, flaeche = ueberhang(tri)
    ab_max, ab_mit = abweichung(r.feld, tri)
    breit, hoch, _ = r.oeffnung()

    print(f"\n{r.titel}  ->  {r.datei}")
    print(f"  Abmessungen    {2*r.r_aussen:.0f} x {2*r.r_aussen:.0f} x "
          f"{r.dicke:.0f} mm")
    print(f"  Oeffnung       {breit:.1f} breit x {hoch:.1f} hoch  "
          f"({r.finger():.1f} Finger zu {D_FINGER:.0f} mm)")
    print(f"  Band           {r.b_oben:.0f} oben, {r.b_seite:.0f} seitlich, "
          f"{r.b_unten:.0f} unten, {r.dicke:.0f} tief")
    print(f"  Dreiecke       {len(tri)}")
    print(f"  Offene Kanten  {offene_kanten(tri)}")
    print(f"  Volumen        {vol/1000:.1f} cm^3   ({vol/1000*1.24:.0f} g PLA)")
    print(f"  Kammer         {2*r.a_kammer:.0f} x {2*r.b_kammer:.0f} mm, "
          f"{r.kammer_oben-r.kammer_unten:.0f} tief, "
          f"Wand {r.halb-r.b_kammer:.1f} mm")
    print(f"  Biegung        {0.18*80*r.r_aussen/r.widerstand(0.0):.1f} MPa "
          f"bei 80 N Zug  (PLA rund 50)")
    print(f"  Ueberhang      {anteil:.2f} % ueber 45 Grad")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"  Kleinball 44,5 {'besteht' if 2*r.r_aussen > 44.5 else 'faellt durch'}"
          f"   Zylinder 31,7 "
          f"{'besteht' if 2*r.r_aussen > 31.7 else 'faellt durch'}")
    return vol


if __name__ == "__main__":
    for r in VARIANTEN:
        baue(r)
    print("\nFingerklemme greift bei Oeffnungen von 5 bis 12 mm, Kopfklemme "
          "ab etwa 95 mm -\nbeide Reife liegen dazwischen.")
