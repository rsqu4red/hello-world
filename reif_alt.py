#!/usr/bin/env python3
"""
Türzwerg – Drei Zugringe in Silikon Shore A 50-60

Der bisherige Reif (reif.py, Rev. E) ist fuer Shore A 80 ausgelegt. Bei
A 50-60 ist das Material 2,6- bis 3,8-mal weicher:

    Shore A50   E = 2,46 MPa      A70   E = 5,52 MPa
    Shore A60   E = 3,61 MPa      A80   E = 9,35 MPa

Ein Ring biegt sich in seiner Ebene, sein Widerstand geht mit der dritten
Potenz der Bandbreite. Gleiche Steifigkeit wie bei A 80 verlangt deshalb
bei A 60 ein um 1,37-mal, bei A 50 ein um 1,56-mal breiteres Band - aus
11 mm werden 15 bzw. 17 mm. Alle drei Entwuerfe hier tragen deshalb ein
deutlich breiteres Band als Rev. E; sie sehen nicht nur anders aus, sie
muessen es auch sein.

Die drei Entwuerfe
-----------------

Kreis    Aussen ein exakter Kreis, das Band nach innen unterschiedlich
         breit. Keine Vorzugsrichtung, keine Erzaehlung - die stillste
         der drei Formen. Haengt in jeder Lage gleich.

Tropfen  Die Aussenkontur folgt der Last: oben schmal, wo die Schnur
         ansetzt, unten breit, wo die Hand zieht. Haengt immer richtig
         herum und zeigt dem Kind, wo es hingreifen soll.

Buegel   Hochkant gestrecktes Langloch als Superellipse. Zwei lange,
         fast gerade Flanken - die Hand greift ueberall, nicht nur unten.
         Schlankeste Silhouette an der Tuer.

Alle drei teilen denselben Querschnitt (ovales Band), dieselbe
Knotenkammer und dieselben Sicherheitsmasse. Sie unterscheiden sich nur
in der Kontur, damit sie vergleichbar bleiben.

Was fuer eine Kinderhand von 1 bis 3 gilt
-----------------------------------------

Greifen: Ein Zweijaehriger umschliesst einen Querschnitt von 12 bis
16 mm bequem. Darunter schneidet die Kante ein, darueber bekommt er die
Finger nicht mehr herum. Alle drei tragen unten 18 x 15 mm, Umfang
52 mm - das ist die Zugstelle, und sie liegt am oberen Rand des
Bequemen, weil die Steifigkeit es verlangt.

Hineingreifen: Vier Kinderfinger nebeneinander brauchen rund 44 mm.
Kreis und Tropfen bieten 48 bzw. 49 mm, der Buegel 42 mm in der Breite
bei 51 mm Hoehe - dort greift die Hand laengs statt quer.

Warum die Ringe kleiner sind als Rev. E: die Aufweitung geht mit der
dritten Potenz des Radius. Ø 80 statt Ø 86 bringt allein ein Fuenftel
mehr Steifigkeit, und das ist bei A 50-60 noetig. Ein Ring in dieser
Haerte und zugleich in Rev.-E-Groesse waere schlapp: er zoege sich bei
17 N um 8 mm auf statt um 3,4.

Klemmen: Finger klemmen in Oeffnungen von 5 bis 12 mm, Koepfe ab etwa
95 mm. Alle drei Oeffnungen liegen sicher dazwischen.

Verschlucken: Der Kleinteilezylinder misst 31,7 mm. Jeder Ring ist in
jeder Richtung groesser.

    python3 reif_alt.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, abweichung,
                  schreibe_stl, schreibe_3mf, weich_abziehen)

# ------------------------------------------------------------- Werkstoff ----

def e_modul(shore_a):
    """Zugmodul aus der Shore-A-Haerte nach Gent."""
    return 0.0981 * (56.0 + 7.62336 * shore_a) / \
           (0.137505 * (254.0 - 2.54 * shore_a))


D_SCHNUR = 5.0          # Schnurbohrung
D_FINGER = 11.0         # Fingerdurchmesser eines Dreijaehrigen, Anhaltswert
HAND_4F = 44.0          # vier Kinderfinger nebeneinander
ZYLINDER = 31.7         # Kleinteilezylinder
KOPF = 95.0             # ab hier wird eine Oeffnung zur Kopffalle

# 0,47 statt 0,50. Bei 0,50 landen auf der gerundeten Bandkante einzelne
# Gitterpunkte so genau auf der Isoflaeche, dass zwei Nachbartetraeder
# ihren Schnittpunkt unterschiedlich runden - das Netz meldet dann ein
# Dutzend offene Kanten, obwohl kein Loch da ist. Das Volumen ist bei
# 0,47, 0,50 und 0,53 auf zwei Stellen identisch (43,90 cm^3); nur bei
# 0,50 zaehlt die Pruefung Kanten. Ein anderes Raster loest es.
RASTER = 0.47


# ------------------------------------------------------------ Querschnitt ---

def _rundbox(u, z, a, b, k):
    """Abstand zum Rechteck 2a x 2b mit Eckradius k."""
    dx, dz = abs(u) - (a - k), abs(z) - (b - k)
    return (math.hypot(max(dx, 0.0), max(dz, 0.0))
            + min(max(dx, dz), 0.0) - k)


class Zugring:
    """Ein Ring als Band entlang einer Kontur r(theta).

    theta wird von oben gemessen: cos(theta) = 1 ist oben, -1 unten.
    Kontur und Bandbreite sind beide Funktionen davon, der Querschnitt
    ist ueberall dasselbe Oval.
    """

    def __init__(self, name, titel, datei, dicke,
                 b_oben, b_seite, b_unten, kontur, notiz,
                 bohr_tiefe=8.0, a_kammer=6.0, b_kammer=3.6):
        self.name, self.titel, self.datei = name, titel, datei
        self.dicke, self.halb = dicke, dicke / 2.0
        self.b_oben, self.b_seite, self.b_unten = b_oben, b_seite, b_unten
        self.kontur, self.notiz = kontur, notiz
        self.bohr_tiefe = bohr_tiefe
        self.a_kammer, self.b_kammer = a_kammer, b_kammer

        # Bandbreite als Kosinusreihe: trifft die drei Vorgaben exakt und
        # ist ueberall knickfrei.
        self.a0 = (b_oben + 2.0 * b_seite + b_unten) / 4.0
        self.a1 = (b_oben - b_unten) / 2.0
        self.a2 = (b_oben - 2.0 * b_seite + b_unten) / 4.0

    # ----------------------------------------------------------- Kontur ----

    def breite(self, c):
        return self.a0 + self.a1 * c + self.a2 * (2.0 * c * c - 1.0)

    def aussen(self, c):
        return self.kontur(c)

    def innen(self, c):
        return self.aussen(c) - self.breite(c)

    def oeffnung(self, n=2000):
        """Laengste waagerechte Sehne der Oeffnung und ihre Hoehe."""
        breit = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            r = self.innen(math.cos(th))
            if 2.0 * r * math.sin(th) > breit:
                breit = 2.0 * r * math.sin(th)
        return breit, self.innen(1.0) + self.innen(-1.0)

    def aussenmass(self, n=2000):
        breit = hoch = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            r = self.aussen(math.cos(th))
            breit = max(breit, 2.0 * r * math.sin(th))
        hoch = self.aussen(1.0) + self.aussen(-1.0)
        return breit, hoch

    def mittelradius(self, n=2000):
        s = sum(self.aussen(math.cos(math.pi * i / n)) - self.breite(
            math.cos(math.pi * i / n)) / 2.0 for i in range(n + 1))
        return s / (n + 1)

    # ------------------------------------------------------ Nachgiebigkeit --

    def aufweitung(self, kraft, shore_a, n=720):
        """Wie weit zieht sich der Ring unter 'kraft' auf?

        Modell: duenner Kreisring unter zwei gegenueberliegenden
        Einzelkraeften, delta = 0,149 * F * R^3 / (E * I). Weil das Band
        nicht ueberall gleich breit ist, wird 1/I ueber den Umfang
        gemittelt, gewichtet mit dem Quadrat des Biegemoments
        M(theta) ~ cos(theta)/2 - 1/pi. Bei konstantem Band ergibt das
        exakt die Lehrbuchformel.

        Das ist eine Abschaetzung: sie unterstellt einen duennen Ring
        (Band klein gegen Radius) und rechnet die Kontur als Kreis mit
        dem mittleren Radius. Fuer den Vergleich der drei Entwuerfe
        untereinander reicht sie, als Absolutwert ist sie optimistisch.
        """
        e = e_modul(shore_a)
        r = self.mittelradius()
        zaehler = nenner = 0.0
        for i in range(n):
            th = 2.0 * math.pi * i / n
            w = (math.cos(th) / 2.0 - 1.0 / math.pi) ** 2
            b = self.breite(math.cos(th))
            i_flaeche = self.dicke * b ** 3 / 12.0
            zaehler += w / i_flaeche
            nenner += w
        i_eff = nenner / zaehler
        return 0.149 * kraft * r ** 3 / (e * i_eff), i_eff

    def grenzkraft(self, shore_a, anteil=0.10):
        """Kraft, bei der sich der Ring um 'anteil' seiner Hoehe aufzieht.

        Darueber hinaus zu rechnen waere unredlich: das Modell ist linear
        und setzt kleine Verformungen voraus. Jenseits dieser Kraft
        ovalisiert der Ring stark, federt zwar zurueck - Silikon reisst
        erst bei mehreren hundert Prozent Dehnung -, aber die Hand kann
        herausrutschen und die zusammenlaufenden Flanken koennen Finger
        klemmen. Das ist die Zahl, die zaehlt.
        """
        _, hoch = self.aussenmass()
        je_newton, _ = self.aufweitung(1.0, shore_a)
        return anteil * hoch / je_newton

    def randdehnung(self, kraft, shore_a):
        """Groesste Randfaserdehnung im Band, in Prozent."""
        e = e_modul(shore_a)
        r = self.mittelradius()
        m = kraft * r * (0.5 - 1.0 / math.pi)     # Moment am Lastpunkt
        b = self.breite(-1.0)
        i_flaeche = self.dicke * b ** 3 / 12.0
        return 100.0 * abs(m) * (b / 2.0) / (e * i_flaeche)

    def griffumfang(self):
        """Umfang des Querschnitts an der Zugstelle unten."""
        a, b = self.b_unten / 2.0, self.halb
        return math.pi * (3.0 * (a + b)
                          - math.sqrt((3 * a + b) * (a + 3 * b)))

    # ------------------------------------------------------- Distanzfeld ----

    def feld(self, x, y, z):
        """Signierter Abstand. Negativ ist Material."""
        zz = z - self.halb
        rho = math.hypot(x, y)
        if rho < 1e-9:
            rho = 1e-9
        c = y / rho

        a = self.breite(c) / 2.0
        u = rho - (self.aussen(c) - a)          # Abstand zur Bandmitte

        # Ovaler Querschnitt. Fuer Silikon so rund wie moeglich: kleine
        # Radien sind die Stellen, an denen ein Riss anfaengt.
        k = min(a, self.halb) * 0.85
        koerper = _rundbox(u, zz, a, self.halb, k)

        # Schnurbohrung, radial von aussen oben nach innen.
        kammer_aussen = self.aussen(1.0) - self.bohr_tiefe
        bohrung = max(math.hypot(x, zz) - D_SCHNUR / 2.0, kammer_aussen - y)

        # Knotenkammer: radialer Kanal am Scheitel, nach innen offen.
        # Der Knoten wird von der Oeffnung her eingelegt.
        kammer_innen = self.innen(1.0) - 1.0
        kk = min(self.a_kammer, self.b_kammer) * 0.8
        quer = _rundbox(x, zz, self.a_kammer, self.b_kammer, kk)
        kammer = max(quer, y - kammer_aussen, kammer_innen - y)

        return weich_abziehen(max(koerper, -bohrung), kammer, 0.8)

    def grenzen(self):
        b, h = self.aussenmass()
        return ((-b / 2 - 2, b / 2 + 2),
                (-self.aussen(-1.0) - 2, self.aussen(1.0) + 2),
                (-1.5, self.dicke + 1.5))


# ---------------------------------------------------------------- Konturen --

def kreis(r):
    return lambda c: r


def tropfen(r_mitte, neigung):
    """Ei-Kontur: oben um 'neigung' kleiner, unten um ebenso groesser."""
    return lambda c: r_mitte - neigung * c


def superellipse(halb_breit, halb_hoch, n):
    """Langloch. n = 2 ist die Ellipse, groesseres n naehert das Rechteck."""
    def f(c):
        c = max(-1.0, min(1.0, c))
        s = math.sqrt(max(0.0, 1.0 - c * c))
        return ((abs(s) / halb_breit) ** n
                + (abs(c) / halb_hoch) ** n) ** (-1.0 / n)
    return f


# --------------------------------------------------------------- Entwuerfe --

KREIS = Zugring(
    "kreis", "Zugring · Kreis", "tuerzwerg-zugring-kreis.stl",
    dicke=15.0, b_oben=21.0, b_seite=16.0, b_unten=18.0,
    kontur=kreis(40.0),
    notiz="Aussen ein exakter Kreis. Keine Vorzugsrichtung, "
          "die stillste der drei Formen.")

TROPFEN = Zugring(
    "tropfen", "Zugring · Tropfen", "tuerzwerg-zugring-tropfen.stl",
    dicke=15.0, b_oben=21.0, b_seite=16.0, b_unten=18.0,
    kontur=tropfen(40.0, 4.5),
    notiz="Aussenkontur folgt der Last: oben schmal, unten breit. "
          "Haengt immer richtig herum.")

BUEGEL = Zugring(
    "buegel", "Zugring · Buegel", "tuerzwerg-zugring-buegel.stl",
    dicke=16.0, b_oben=21.0, b_seite=16.0, b_unten=18.0,
    kontur=superellipse(36.0, 45.0, 3.0),
    notiz="Hochkant gestrecktes Langloch. Lange gerade Flanken, "
          "die Hand greift ueberall.")

ENTWUERFE = [KREIS, TROPFEN, BUEGEL]


# ------------------------------------------------------------------- Lauf ---

def baue(r):
    tri = vernetzen(r.feld, r.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, r.datei, "Tuerzwerg %s - Masse in mm" % r.titel)

    breit_a, hoch_a = r.aussenmass()
    breit_o, hoch_o = r.oeffnung()
    ab_max, ab_mit = abweichung(r.feld, tri)

    print(f"\n{r.titel}  ->  {r.datei}")
    print(f"  {r.notiz}")
    print(f"  Aussen         {breit_a:.0f} x {hoch_a:.0f} x {r.dicke:.0f} mm")
    print(f"  Oeffnung       {breit_o:.0f} breit x {hoch_o:.0f} hoch "
          f"({breit_o/D_FINGER:.1f} Finger zu {D_FINGER:.0f} mm)")
    print(f"  Band           {r.b_oben:.0f} oben, {r.b_seite:.0f} seitlich, "
          f"{r.b_unten:.0f} unten")
    print(f"  Griff unten    {r.b_unten:.0f} x {r.dicke:.0f} mm, "
          f"Umfang {r.griffumfang():.0f} mm")
    print(f"  Volumen        {vol/1000:.1f} cm^3 "
          f"({vol/1000*1.15:.0f} g Silikon)")
    print(f"  Dreiecke       {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    for shore in (50, 60):
        d17, _ = r.aufweitung(17.0, shore)
        fg = r.grenzkraft(shore)
        eps = r.randdehnung(17.0, shore)
        print(f"  Shore A{shore}      {d17:.1f} mm auf bei 17 N, "
              f"Randdehnung {eps:.1f} % | ab {fg:.0f} N zieht er sich "
              f"um mehr als ein Zehntel auf")
    print(f"  Klemmen        Oeffnung {breit_o:.0f} mm: "
          f"{'ueber 12 mm' if breit_o > 12 else 'FINGERFALLE'}, "
          f"{'unter 95 mm' if hoch_o < KOPF else 'KOPFFALLE'}")
    print(f"  Kleinteile     {'besteht' if min(breit_a, hoch_a) > ZYLINDER else 'FAELLT DURCH'}"
          f" (Zylinder {ZYLINDER:.1f} mm)")
    return vol


if __name__ == "__main__":
    print("Zugmodul nach Gent:")
    for s in (50, 60, 80):
        print(f"  Shore A{s}   E = {e_modul(s):.2f} MPa")
    for r in ENTWUERFE:
        baue(r)
