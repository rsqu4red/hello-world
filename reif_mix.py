#!/usr/bin/env python3
"""
Türzwerg – Zugring "Mix": Tropfenkontur mit Rev.-E-Oeffnung

Was von welchem Entwurf kommt
-----------------------------

Von Rev. E auch die Knotenkammer: 14 x 7,2 mm statt der 12 x 6,4, die
eine fruehere Fassung hatte - Rev. E hat 12 x 7,2, der Mix ist also
sogar 2 mm breiter. Der Knoten muss hineinpassen, ohne dass man ihn
hineinzwingt.

Ihre Hoehe folgt dabei der Bandkontur. Am inneren Ende rundet der
Querschnitt ab und das Band wird duenner; mit fester Kammerhoehe blieben
dort nur 1,38 mm Wand stehen - weniger als bei Rev. E, und ausgerechnet
an der Stelle, an der der Knoten drueckt. Die Kammer wird deshalb
flacher, sobald ihr weniger als 1,9 mm bleiben.

Von Rev. E die Grosszuegigkeit: eine Oeffnung, durch die eine
Kinderhand wirklich hindurchgeht, nicht nur vier Fingerkuppen. Rev. E
hat 64 x 48 mm, der Tropfen nur 53 x 41.

Vom Tropfen die Kontur und das tragfaehige Band: oben schmal, wo die
Schnur ansetzt, unten breit, wo die Hand zieht, Flanken leicht geweitet.
Rev. E ist an den Flanken nur 11 mm breit, und daran scheitert er - bei
gleichem Werkstoff und gleicher Dicke ist er 3,5-mal weicher als der
Kreis.

Der Mix nimmt Rev. E's Aussenmass und faehrt darin ein Band von
23/16/18 mm statt 23/11/15. Ergebnis: Oeffnung 59 x 45, also fast
Rev.-E-Format, bei einem Drittel seiner Nachgiebigkeit.

Was in 3D dazukommt
-------------------

Die bisherigen Entwuerfe hatten ueberall denselben Querschnitt. Das ist
fuer den Vergleich richtig und fuer die Hand falsch: oben am Ring wird
Breite fuer die Knotenkammer gebraucht, unten Fuelle zum Anfassen.

Geaendert wird deshalb der Eckradius ueber den Umfang: oben 0,72 des
halben Kleinstmasses, unten voll. Unten ist der Querschnitt damit ein
echtes Stadion - rundum gewoelbt, keine Kante, die in die Handflaeche
schneidet. Oben bleibt er flacher, weil die Knotenkammer dort Platz
braucht. Der Uebergang laeuft als Kosinus, es gibt also keine Stelle,
an der die Aenderung anfaengt.

Die Dicke bleibt dagegen ueberall 11,0 mm. Eine fruehere Fassung lief
von 11,0 oben auf 13,5 unten, mit der Begruendung, das Band werde zur
Zughand hin fuelliger. Nachgerechnet traegt die Begruendung nicht:

    unten     Griffumfang   Aufweitung bei 17 N
    11,0 mm      46 mm            4,3 mm
    12,0 mm      48 mm            4,0 mm
    13,5 mm      50 mm            3,6 mm
    15,0 mm      52 mm            3,3 mm

Die 13,5 mm kosten 4 mm Griffumfang und bringen 0,7 mm Aufweitung. Ein
Einjaehriger hakt den Ring eher mit zwei Fingern ein, als ihn zu
umfassen; fuer ihn ist das schlanke Band das bessere. 4,3 mm sind
immer noch ein Drittel von Rev. E's 10,7 mm.

Keine Griffmulde. Eine Hohlkehle an der Innenkante klingt nach
Ergonomie, traegt aber nur auf zwei Kanten statt auf der vollen Breite -
der Ring wird umgriffen, nicht eingehaengt. Das stand schon in reif.py
und gilt weiter.

    python3 reif_mix.py
"""

import math

from netz import (vernetzen, volumen, offene_kanten, abweichung,
                  schreibe_stl, weich_abziehen)
from reif_alt import e_modul, D_FINGER, ZYLINDER, KOPF

TAU = 2.0 * math.pi

# Schnurbohrung, gleich dem Schnurdurchmesser. 4 mm, nicht 5: Paracord 550
# Type III misst rund 4 mm. Gleich gross und nicht groesser, wie bei der
# Manschette - Silikon dehnt sich beim Einfaedeln, und was bleibt, ist eine
# Bohrung ohne Spiel. Ein Sackstich in 4-mm-Schnur misst rund 8 mm: durch
# eine 5er Bohrung muesste er sie um 60 Prozent weiten, durch eine 4er um
# 100.
D_SCHNUR = 4.0
WAND_KAMMER = 1.9       # Mindestwand ueber der Knotenkammer, wie Rev. E
RASTER = 0.47


def _rundbox(u, z, a, b, k):
    k = min(k, a, b)
    dx, dz = abs(u) - (a - k), abs(z) - (b - k)
    return (math.hypot(max(dx, 0.0), max(dz, 0.0))
            + min(max(dx, dz), 0.0) - k)


def _reihe(oben, seite, unten):
    """Kosinusreihe, die die drei Vorgaben exakt trifft."""
    a0 = (oben + 2.0 * seite + unten) / 4.0
    a1 = (oben - unten) / 2.0
    a2 = (oben - 2.0 * seite + unten) / 4.0
    return lambda c: a0 + a1 * c + a2 * (2.0 * c * c - 1.0)


class Mix:
    def __init__(self, r0=43.0, e=4.5, w=2.0,
                 b_oben=23.0, b_seite=16.0, b_unten=18.0,
                 d_oben=11.0, d_unten=11.0,
                 eck_oben=0.72, eck_unten=1.0,
                 bohr_tiefe=7.5, a_kammer=7.0, b_kammer=3.6):
        self.r0, self.e, self.w = r0, e, w
        self._breite = _reihe(b_oben, b_seite, b_unten)
        self.b_oben, self.b_seite, self.b_unten = b_oben, b_seite, b_unten
        self.d_oben, self.d_unten = d_oben, d_unten
        self.eck_oben, self.eck_unten = eck_oben, eck_unten
        self.bohr_tiefe = bohr_tiefe
        self.a_kammer, self.b_kammer = a_kammer, b_kammer

    # ------------------------------------------------------------ Kontur ---

    def aussen(self, c):
        """Tropfen: oben schmal, unten breit, Flanken um w geweitet."""
        return self.r0 - self.e * c + self.w * (1.0 - c * c)

    def breite(self, c):
        return self._breite(c)

    def innen(self, c):
        return self.aussen(c) - self.breite(c)

    def dicke(self, c):
        return (self.d_oben + self.d_unten) / 2.0 \
             + (self.d_oben - self.d_unten) / 2.0 * c

    def eckfaktor(self, c):
        return (self.eck_oben + self.eck_unten) / 2.0 \
             + (self.eck_oben - self.eck_unten) / 2.0 * c

    # ------------------------------------------------------------ Masse ----

    def aussenmass(self, n=1440):
        breit = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            breit = max(breit, 2.0 * self.aussen(math.cos(th)) * math.sin(th))
        return breit, self.aussen(1.0) + self.aussen(-1.0)

    def oeffnung(self, n=1440):
        breit = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            breit = max(breit, 2.0 * self.innen(math.cos(th)) * math.sin(th))
        return breit, self.innen(1.0) + self.innen(-1.0)

    def mittelradius(self, n=1440):
        return sum((self.aussen(math.cos(math.pi * i / n))
                    + self.innen(math.cos(math.pi * i / n))) / 2.0
                   for i in range(n + 1)) / (n + 1)

    def aufweitung(self, kraft, shore_a, n=720):
        em = e_modul(shore_a)
        r = self.mittelradius()
        za = ne = 0.0
        for i in range(n):
            th = TAU * i / n
            c = math.cos(th)
            gew = (c / 2.0 - 1.0 / math.pi) ** 2
            za += gew / (self.dicke(c) * self.breite(c) ** 3 / 12.0)
            ne += gew
        return 0.149 * kraft * r ** 3 / (em * (ne / za))

    def grenzkraft(self, shore_a, anteil=0.10):
        return anteil * self.aussenmass()[1] / self.aufweitung(1.0, shore_a)

    def griffumfang(self):
        a, b = self.b_unten / 2.0, self.dicke(-1.0) / 2.0
        return math.pi * (3.0 * (a + b)
                          - math.sqrt((3 * a + b) * (a + 3 * b)))

    # -------------------------------------------------------- Distanzfeld --

    def feld(self, x, y, z):
        """Mittelebene bei z = 0 - der Ring wird in dieser Ebene geteilt."""
        rho = math.hypot(x, y)
        if rho < 1e-9:
            rho = 1e-9
        c = y / rho

        a = self.breite(c) / 2.0
        b = self.dicke(c) / 2.0
        u = rho - (self.aussen(c) - a)
        koerper = _rundbox(u, z, a, b, self.eckfaktor(c) * min(a, b))

        kammer_aussen = self.aussen(1.0) - self.bohr_tiefe
        bohrung = max(math.hypot(x, z) - D_SCHNUR / 2.0, kammer_aussen - y)

        # Die Kammerhoehe folgt der Bandkontur, aber nur ueber dem
        # eingeschlossenen Teil - zum Mund hin laeuft sie wieder auf.
        #
        # Die erste Fassung nahm sie ueberall zurueck, sobald ihr weniger
        # als WAND_KAMMER blieb, mit 0,8 als unterer Schranke. Am inneren
        # Ende rundet der Querschnitt aber aus, die Bandhoehe geht gegen
        # null, und damit wurde der Mund ueberall genau 1,6 mm hoch. Ein
        # Knoten in 4-mm-Schnur misst rund 8 - er kommt da nicht hinein.
        #
        # Der Denkfehler steckte in der Begruendung "genau dort drueckt
        # der Knoten". Das stimmt nicht: die Schnur zieht nach aussen, der
        # Knoten drueckt gegen die Schulter um die Schnurbohrung am
        # AEUSSEREN Ende. Am Mund traegt die Wand darueber nichts, und es
        # gibt dort auch keine mehr - das Band endet ja.
        #
        # Deshalb wirkt die Ruecknahme jetzt gewichtet: tief im Band voll,
        # am Mund gar nicht. Die Uebergangslaenge ist der Eckradius des
        # Bandes selbst, also genau die Strecke, ueber die es ausrundet.
        # Das ist wieder das Verhalten des real erprobten Rev. E aus
        # reif.py, dessen Kammer ueber die ganze Laenge denselben
        # Querschnitt hat.
        a_top = self.b_oben / 2.0
        b_top = self.d_oben / 2.0
        k_top = self.eck_oben * min(a_top, b_top)
        u_top = y - (self.aussen(1.0) - a_top)
        hoch = self._profil_z(u_top, a_top, b_top, k_top) - WAND_KAMMER
        t = min(max((u_top + a_top) / max(k_top, 1e-6), 0.0), 1.0)
        t = t * t * (3.0 - 2.0 * t)          # weich, ohne Knick am Mund
        bk = min(self.b_kammer,
                 max(hoch, 0.0) * t + self.b_kammer * (1.0 - t))

        kammer_innen = self.innen(1.0) - 1.0
        quer = _rundbox(x, z, self.a_kammer, bk,
                        0.8 * min(self.a_kammer, bk))
        kammer = max(quer, y - kammer_aussen, kammer_innen - y)

        return weich_abziehen(max(koerper, -bohrung), kammer, 0.8)

    def grenzen(self):
        br, ho = self.aussenmass()
        d = max(self.d_oben, self.d_unten) / 2.0
        return ((-br / 2 - 2, br / 2 + 2),
                (-self.aussen(-1.0) - 2, self.aussen(1.0) + 2),
                (-d - 2, d + 2))

    # ------------------------------------------------------- Projektionen --

    def _profil_z(self, u, a, b, k):
        """Halbe Bauhoehe des Querschnitts an der radialen Stelle u."""
        k = min(k, a, b)
        if abs(u) <= a - k:
            return b
        d = abs(u) - (a - k)
        return (b - k) + math.sqrt(max(0.0, k * k - d * d)) if d <= k else 0.0

    def projektion(self, achse, n_th=360, n_u=60, n_bin=240):
        """Silhouette in der Seiten- (achse='y') oder Draufsicht ('x').

        Fuer jede Quermass-Klasse die groesste Bauhoehe - die Projektion
        eines Rings ist geschlossen, das Loch verschwindet darin.
        """
        br, ho = self.aussenmass()
        lo, hi = (-self.aussen(-1.0), self.aussen(1.0)) if achse == "y" \
            else (-br / 2.0, br / 2.0)
        bins = [0.0] * (n_bin + 1)
        for i in range(n_th + 1):
            th = math.pi * i / n_th
            c, s = math.cos(th), math.sin(th)
            a = self.breite(c) / 2.0
            b = self.dicke(c) / 2.0
            k = self.eckfaktor(c) * min(a, b)
            mitte = self.aussen(c) - a
            for j in range(n_u + 1):
                u = -a + 2.0 * a * j / n_u
                rho = mitte + u
                v = rho * c if achse == "y" else rho * s
                idx = int(round((v - lo) / (hi - lo) * n_bin))
                if 0 <= idx <= n_bin:
                    bins[idx] = max(bins[idx], self._profil_z(u, a, b, k))
        return lo, hi, bins


MIX = Mix()

# Vergleichsringe, alle A 70 und 11 mm, wie zuletzt abgestimmt
VERGLEICH = [
    ("Tropfen w = 2", 40.0, 4.5, 2.0, 21.0, 16.0, 18.0, 11.0),
    ("Kreis", 40.0, 0.0, 0.0, 21.0, 16.0, 18.0, 11.0),
    ("Rev. E", 43.0, 0.0, 0.0, 23.0, 11.0, 15.0, 11.0),
]


def als_mix(r0, e, w, bo, bs, bu, d):
    return Mix(r0=r0, e=e, w=w, b_oben=bo, b_seite=bs, b_unten=bu,
               d_oben=d, d_unten=d, eck_oben=0.85, eck_unten=0.85)


if __name__ == "__main__":
    import reif_mix_zeichnung as Z

    print("Vernetze Mix ...")
    tri = vernetzen(MIX.feld, MIX.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, "tuerzwerg-zugring-mix.stl",
                 "Tuerzwerg Zugring Mix - Masse in mm")
    ab_max, ab_mit = abweichung(MIX.feld, tri)

    br, ho = MIX.aussenmass()
    ob, oh = MIX.oeffnung()
    print(f"\nZugring Mix  ->  tuerzwerg-zugring-mix.stl")
    print(f"  Aussen         {br:.0f} x {ho:.0f} mm, "
          f"{MIX.d_oben:.0f} mm oben / {MIX.d_unten:.1f} mm unten tief")
    print(f"  Oeffnung       {ob:.0f} x {oh:.0f} mm "
          f"({ob/D_FINGER:.1f} Finger zu {D_FINGER:.0f} mm)")
    print(f"  Band           {MIX.b_oben:.0f} / {MIX.b_seite:.0f} / "
          f"{MIX.b_unten:.0f} mm")
    print(f"  Griff unten    {MIX.b_unten:.0f} x {MIX.dicke(-1.0):.1f} mm, "
          f"Umfang {MIX.griffumfang():.0f} mm")
    print(f"  Volumen        {vol/1000:.1f} cm^3 ({vol/1000*1.15:.0f} g)")
    print(f"  Dreiecke       {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    for s in (60, 70):
        print(f"  Shore A{s}      {MIX.aufweitung(17.0, s):.1f} mm bei 17 N, "
              f"Grenze {MIX.grenzkraft(s):.0f} N")
    print(f"  Kleinteile     {'besteht' if min(br, ho) > ZYLINDER else 'FAELLT DURCH'}"
          f", Klemmen {'ok' if 12 < ob < KOPF else 'PRUEFEN'}")

    print("\nVergleich bei Shore A 70:")
    print(f"  {'Entwurf':<16}{'aussen':>11}{'Oeffnung':>11}{'Band':>13}"
          f"{'17 N':>8}{'Grenze':>9}")
    reihen = [("Mix", MIX)] + [(n, als_mix(*p)) for n, *p in
                               [(v[0],) + tuple(v[1:]) for v in VERGLEICH]]
    for name, m in reihen:
        b1, h1 = m.aussenmass()
        o1, o2 = m.oeffnung()
        print(f"  {name:<16}{f'{b1:.0f} x {h1:.0f}':>11}"
              f"{f'{o1:.0f} x {o2:.0f}':>11}"
              f"{f'{m.b_oben:.0f}/{m.b_seite:.0f}/{m.b_unten:.0f}':>13}"
              f"{m.aufweitung(17.0, 70):>7.1f} {m.grenzkraft(70):>7.0f} N")

    Z.zeichne(MIX, reihen[1:])
