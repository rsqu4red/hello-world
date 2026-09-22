#!/usr/bin/env python3
"""
Türzwerg – Zugring: Rev. H auf Ø72 und Rev. E mit den Kanten von Rev. H

Zwei Ringe, ein Codepfad
------------------------

Beide werden hier aus derselben Mix-Klasse gebaut, mit demselben Vernetzer
und derselben Messung. Nur so ist der Vergleich einer: Rev. E steckte
urspruenglich in reif.py und damit in einer anderen Klasse mit eigener
Fasenlogik. Was unten "Rev. E" heisst, ist dessen Kontur - Ø86, Band
23/11/15, Kammer 12 x 7,2 - im Mix-Rahmen nachgebaut, nicht die
reif.py-Fassung Zeile fuer Zeile.

Zur Groesse
-----------

Die erste Giessform war fuer Rev. A, Ø72 x 14 - nicht fuer Rev. E. Rev. E
und Rev. H haben beide Ø86 x 11; sie unterscheiden sich nicht im Umriss,
sondern in der Verteilung: Rev. H hat seitlich 16,4 mm Band, Rev. E 11.
Deutlich groesser ist Rev. H nur gegenueber Rev. A.

Rev. H wird deshalb auf Ø72 gebracht, das Aussenmass der ersten Form.
Skaliert wird nur in der Ringebene - Radius, Bandbreiten, Bohrtiefe -,
waehrend Dicke und Knotenkammer bleiben, wie sie sind: 11 mm und 14 x 7,2.
Die 11 mm sind die im Realtest bewaehrte Banddicke, und eine mitskalierte
Kammer haette den Knoten verloren.

Ein Widerspruch, der stehen bleibt
----------------------------------

Im Kommentar zu Rev. E in reif.py steht "Aufweitung bei 17 N: 3,9 mm"
(Silikon A 80). Dieses Modell rechnet 6,3 mm. Nachpruefbar ist keine der
beiden Zahlen aus reif.py, denn die Datei enthaelt ueberhaupt keine
Aufweitungsrechnung - nur widerstand(), ein Widerstandsmoment. Die 3,9
stammen also aus einer Nebenrechnung, die nicht mit im Quelltext liegt.

Was hier steht, kommt durchgehend aus einem Modell: Ring unter
Diametrallast, Biegesteifigkeit ueber den Umfang compliance-gewichtet,
E-Modul nach Gent aus der Shore-Haerte. Dasselbe Modell liefert fuer
Rev. H die 3,91 mm, mit denen seit Wochen gearbeitet wird. Die Zahlen
sind untereinander vergleichbar; ob sie absolut stimmen, sagt erst ein
Zugversuch am gegossenen Teil.

Was das Schrumpfen mit der Steife macht
---------------------------------------

Nichts, und das ist kein Zufall. Die Aufweitung geht mit

    delta = 0,149 * F * R^3 / (E * I),   I = t * b^3 / 12

Skaliert man R und b mit demselben Faktor und laesst t stehen, kuerzt sich
der Faktor heraus: R^3 waechst wie b^3. Der kleine Ring zieht sich also
genauso an wie der grosse. Die Zahlen unten bestaetigen das.

    python3 reif_eh.py
"""

import math

from netz import vernetzen, volumen, offene_kanten, abweichung, schreibe_stl
from reif_mix import Mix, RASTER, D_FINGER, ZYLINDER, KOPF
from reif_revh import REV_H
import reif_mix_zeichnung as Z

ZIEL_AUSSEN = 72.0                       # Aussenmass der ersten Giessform
F = ZIEL_AUSSEN / REV_H.aussenmass()[0]  # 72 / 86 = 0,8372

# Rev. H, in der Ringebene auf Ø72 geschrumpft. Dicke und Kammer bleiben.
REV_H72 = Mix(r0=REV_H.r0 * F, e=0.0, w=0.0,
              b_oben=REV_H.b_oben * F,
              b_seite=REV_H.b_seite * F,
              b_unten=REV_H.b_unten * F,
              d_oben=REV_H.d_oben, d_unten=REV_H.d_unten,
              eck_oben=REV_H.eck_oben, eck_unten=REV_H.eck_unten,
              bohr_tiefe=REV_H.bohr_tiefe * F,
              a_kammer=REV_H.a_kammer, b_kammer=REV_H.b_kammer)

# Rev. A - der Ring der ersten Giessform, Ø72 x 14. Mit den Kanten von
# Rev. H: unten voll ausgerundet, oben 0,72.
#
# Rev. A ist mit 14 mm das dickste Band der ganzen Reihe. Bei eck_unten = 1
# wird der Griffquerschnitt damit 15 x 14 mit 7 mm Radius - ein Rundstab mit
# einem Millimeter Gerade darin. Genau das ist "geschmeidig fuer die Hand":
# es gibt keine Kante mehr, an der der Finger abknickt.
REV_A_RUND = Mix(r0=36.0, e=0.0, w=0.0,
                 b_oben=19.0, b_seite=12.0, b_unten=15.0,
                 d_oben=14.0, d_unten=14.0,
                 eck_oben=REV_H.eck_oben, eck_unten=REV_H.eck_unten,
                 bohr_tiefe=8.0, a_kammer=5.5, b_kammer=4.5)

# Rev. A, wie er war: umlaufend 1,0 mm Kantenradius. Als Eckfaktor
# ausgedrueckt sind das 1,0 / 7,0 = 0,143.
#
# Naeherung, und zwar an einer Stelle: die 40-Grad-Druckfasen von Rev. A
# bildet die Mix-Klasse nicht ab. Fuer den Vergleich der Kantenverrundung
# spielt das keine Rolle, fuer ein Volumen auf zwei Stellen schon.
REV_A = Mix(r0=36.0, e=0.0, w=0.0,
            b_oben=19.0, b_seite=12.0, b_unten=15.0,
            d_oben=14.0, d_unten=14.0,
            eck_oben=1.0 / 7.0, eck_unten=1.0 / 7.0,
            bohr_tiefe=8.0, a_kammer=5.5, b_kammer=4.5)

# Rev. E, wie er war: Eckfaktor 0,85 rundum.
REV_E = Mix(r0=43.0, e=0.0, w=0.0,
            b_oben=23.0, b_seite=11.0, b_unten=15.0,
            d_oben=11.0, d_unten=11.0,
            eck_oben=0.85, eck_unten=0.85,
            bohr_tiefe=7.0, a_kammer=6.0, b_kammer=3.6)

# Rev. E mit den Kanten von Rev. H: unten voll ausgerundet - ein echtes
# Stadion, weil dort gezogen wird -, oben 0,72, weil die Kammer Hoehe
# braucht. Sonst unveraendert.
REV_E_RUND = Mix(r0=43.0, e=0.0, w=0.0,
                 b_oben=23.0, b_seite=11.0, b_unten=15.0,
                 d_oben=11.0, d_unten=11.0,
                 eck_oben=REV_H.eck_oben, eck_unten=REV_H.eck_unten,
                 bohr_tiefe=7.0, a_kammer=6.0, b_kammer=3.6)

DATEI_AR = "tuerzwerg-zugring-reva-rund.stl"
DATEI_H72 = "tuerzwerg-zugring-revh72.stl"
DATEI_ER = "tuerzwerg-zugring-reve-rund.stl"


def eckradius(m, c):
    """Wirklicher Eckradius des Querschnitts an dieser Stelle."""
    a, b = m.breite(c) / 2.0, m.dicke(c) / 2.0
    return m.eckfaktor(c) * min(a, b)


def umfang_quer(m, c=-1.0):
    """Wirklicher Umfang des Querschnitts - der Weg, den die Finger gehen.

    Mix.griffumfang() rechnet die Ramanujan-Naeherung fuer eine Ellipse und
    sieht den Eckradius nicht: fuer Rev. A mit 1 mm Kante und fuer Rev. A mit
    7 mm Kante liefert sie denselben Wert. Der Querschnitt ist aber ein
    Rechteck mit verrundeten Ecken, und dessen Umfang ist exakt

        4a + 4b - 8k + 2*pi*k

    mit den Halbmassen a, b und dem Eckradius k. Bei k = min(a, b) faellt das
    auf das Stadion zusammen, bei k = 0 auf das Rechteck.
    """
    a, b = m.breite(c) / 2.0, m.dicke(c) / 2.0
    k = m.eckfaktor(c) * min(a, b)
    return 4.0 * a + 4.0 * b - 8.0 * k + 2.0 * math.pi * k


def kammerlaenge(m):
    """Radiale Laenge der Knotenkammer, vom aeusseren Ende bis zum
    Durchbruch in die Oeffnung."""
    return (m.aussen(1.0) - m.bohr_tiefe) - (m.innen(1.0) - 1.0)


def baue(m, datei, name):
    print(f"Vernetze {name} ...")
    tri = vernetzen(m.feld, m.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, datei, f"Tuerzwerg Zugring {name} - Masse in mm")
    ab_max, ab_mit = abweichung(m.feld, tri)
    return tri, vol, offene_kanten(tri), ab_max, ab_mit


if __name__ == "__main__":
    print(f"Massstab fuer Rev. H:  {ZIEL_AUSSEN:.0f} / "
          f"{REV_H.aussenmass()[0]:.0f} = {F:.4f}\n")

    gebaut = {}
    for m, datei, name in ((REV_A_RUND, DATEI_AR, "Rev. A gerundet"),
                           (REV_H72, DATEI_H72, "Rev. H auf 72"),
                           (REV_E_RUND, DATEI_ER, "Rev. E gerundet")):
        gebaut[name] = baue(m, datei, name) + (datei,)

    alle = [("Rev. A rund", REV_A_RUND), ("Rev. A alt", REV_A),
            ("Rev. H 72", REV_H72), ("Rev. E rund", REV_E_RUND),
            ("Rev. H", REV_H)]

    print("\nVergleich, alle bei Shore A 70")
    kopf = [""] + [n for n, _ in alle]
    print(f"  {kopf[0]:<22}" + "".join(f"{k:>17}" for k in kopf[1:]))

    def zeile(name, f):
        print(f"  {name:<22}" + "".join(f"{f(m):>17}" for _, m in alle))

    zeile("Aussen", lambda m: "%.0f x %.0f" % m.aussenmass())
    zeile("Dicke", lambda m: "%.1f" % m.d_oben)
    zeile("Oeffnung", lambda m: "%.1f x %.1f" % m.oeffnung())
    zeile("Band o / s / u", lambda m: "%.1f/%.1f/%.1f"
          % (m.b_oben, m.b_seite, m.b_unten))
    zeile("Griff unten", lambda m: "%.1f x %.1f" % (m.b_unten, m.dicke(-1.0)))
    zeile("Eckradius unten", lambda m: "%.2f" % eckradius(m, -1.0))
    zeile("Eckradius oben", lambda m: "%.2f" % eckradius(m, 1.0))
    zeile("Griffumfang echt", lambda m: "%.1f" % umfang_quer(m))
    zeile("  (Ellipsennaeherung)", lambda m: "%.1f" % m.griffumfang())
    zeile("Kammer", lambda m: "%.0f x %.1f" % (2 * m.a_kammer, 2 * m.b_kammer))
    zeile("Kammerlaenge", lambda m: "%.1f" % kammerlaenge(m))
    for s in (60, 70, 80):
        zeile(f"Aufweitung 17 N, A{s}",
              lambda m, s=s: "%.2f mm" % m.aufweitung(17.0, s))
    zeile("Grenze 10 %, A70", lambda m: "%.0f N" % m.grenzkraft(70))

    print("\nGebaute Teile")
    for name, (tri, vol, ok_, ab_max, ab_mit, datei) in gebaut.items():
        print(f"  {name:<18}{datei}")
        print(f"  {'':<18}{len(tri)} Dreiecke, offene Kanten {ok_}, "
              f"{vol/1000:.2f} cm^3 ({vol/1000*1.15:.0f} g)")
        print(f"  {'':<18}Formtreue hoechstens {ab_max*1000:.0f} um, "
              f"im Mittel {ab_mit*1000:.0f} um")

    print("\nSicherheit und Handmass")
    for name, m in alle:
        br, ho = m.aussenmass()
        ob, oh = m.oeffnung()
        print(f"  {name:<14}Oeffnung {ob:.1f} mm = {ob/D_FINGER:.1f} Finger, "
              f"Kleinteilezylinder {'besteht' if min(br, ho) > ZYLINDER else 'FAELLT DURCH'}"
              f", Kopffalle {'ok' if ob < KOPF else 'PRUEFEN'}")

    Z.zeichne(REV_A_RUND,
              [("Rev. A alt", REV_A), ("Rev. H 72", REV_H72),
               ("Rev. E rund", REV_E_RUND), ("Rev. H", REV_H)],
              datei="tuerzwerg-zugring-eh-vergleich.svg",
              titel="Zugring · Rev. A gerundet wie Rev. H",
              untertitel="Rev. A mit den Eckfaktoren von Rev. H · unten ein "
                         "volles Stadion 15 x 14 · daneben Rev. H auf Ø72 "
                         "und Rev. E · Shore A 70 · Masse in mm",
              eigen="Rev. A rund")
