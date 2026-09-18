#!/usr/bin/env python3
"""
Türzwerg – Zugring Rev. H

Die Fassung, die aus dem Realtest folgt.

Zur Knotenkammer
----------------

Rev. G hatte das Band am Scheitel auf 14 mm verdickt, um eine 10,2 mm
hohe Kammer zu bekommen. Begruendung war eine Abschaetzung: ein Knoten
in 5-mm-Schnur misst als Kugel gerechnet 12 bis 18 mm und passt damit
nicht in die 7,2 mm, die ein 11-mm-Band mit 1,9 mm Wand uebrig laesst.

Der Realtest sagt etwas anderes: die Kammer von Rev. E - 12 x 7,2 x 17
mm - haelt den Knoten gut. Die Rechnung war zu pessimistisch, weil sie
den Knoten als Kugel behandelt. Er ist keine: in einer 17 mm langen
Kammer laengt er sich und flacht ab, und Silikon gibt zusaetzlich nach.

Rev. H nimmt deshalb die geprueften 7,2 mm Hoehe, behaelt aber die
groessere Breite von Rev. F: 14 x 7,2 x 16,5 statt 12 x 7,2 x 17. Zwei
Millimeter mehr in der Breite kosten nichts - die Breite liegt
tangential, dort ist Material im Ueberfluss -, und sie geben dem Knoten
Luft in der Richtung, in der er sie ohne Verdickung bekommen kann.

Das Band ist damit wieder ueberall 11,0 mm dick.

Goldene Proportionen
--------------------

Aus Rev. G bleibt, was nichts kostet. Zwei Verhaeltnisse lagen schon
vor jeder Absicht dicht an phi = 1,618 - sie waren aus Steifigkeit und
Handgroesse entstanden, unabhaengig voneinander:

    Aussen : Oeffnung      86 : 54 = 1,593   (-1,6 %)
    Griff Breite : Dicke   18 : 11 = 1,636   (+1,1 %)

Exakt gemacht sind das Aenderungen unter einem Millimeter:

    Aussen : Oeffnung      86 : 53,2   -> Band seitlich 16,4
    Griff                  17,8 : 11,0

Nicht auf phi gezwungen wurden Bandbreite oben zu unten und Aussen zu
Oeffnungshoehe; dort haette es 20 bis 30 Prozent Verschiebung gekostet.
phi ordnet hier den Masssatz, es begruendet ihn nicht.

Querschnitt
-----------

Eckradius unten voll - ein echtes Stadion, 17,8 x 11,0 rundum gewoelbt,
das ist die Zugstelle. Oben 0,72, weil die Kammer Hoehe braucht.
Uebergang als Kosinus. Keine Griffmulde: sie traegt nur auf zwei Kanten
statt auf der vollen Breite, weil der Ring umgriffen wird.

    python3 reif_revh.py
"""

from netz import vernetzen, volumen, offene_kanten, abweichung, schreibe_stl
from reif_mix import Mix, RASTER, D_FINGER, ZYLINDER, KOPF
import reif_mix_zeichnung as Z

PHI = (1.0 + 5.0 ** 0.5) / 2.0

R_AUSSEN = 43.0
OEFFNUNG = 2.0 * R_AUSSEN / PHI          # 53,2
B_SEITE = R_AUSSEN - OEFFNUNG / 2.0      # 16,4
D_BAND = 11.0                            # ueberall, auch am Scheitel
B_UNTEN = D_BAND * PHI                   # 17,8

REV_H = Mix(r0=R_AUSSEN, e=0.0, w=0.0,
            b_oben=23.0, b_seite=B_SEITE, b_unten=B_UNTEN,
            d_oben=D_BAND, d_unten=D_BAND,
            a_kammer=7.0, b_kammer=3.6)   # 14 x 7,2 - Hoehe wie Rev. E

VERGLEICH = [
    ("Rev. G", Mix(r0=43.0, e=0.0, w=0.0, b_oben=23.0, b_seite=16.4,
                   b_unten=17.8, d_oben=14.0, d_unten=11.0,
                   a_kammer=8.25, b_kammer=5.1)),
    ("Rev. F", Mix(r0=43.0, e=0.0, w=0.0,
                   b_oben=23.0, b_seite=16.0, b_unten=18.0)),
    ("Rev. E", Mix(r0=43.0, e=0.0, w=0.0,
                   b_oben=23.0, b_seite=11.0, b_unten=15.0,
                   eck_oben=0.85, eck_unten=0.85, a_kammer=6.0)),
    ("Kreis", Mix(r0=40.0, e=0.0, w=0.0,
                  b_oben=21.0, b_seite=16.0, b_unten=18.0,
                  eck_oben=0.85, eck_unten=0.85)),
]

if __name__ == "__main__":
    print("Vernetze Rev. H ...")
    tri = vernetzen(REV_H.feld, REV_H.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, "tuerzwerg-zugring-revh.stl",
                 "Tuerzwerg Zugring Rev. H - Masse in mm")
    ab_max, ab_mit = abweichung(REV_H.feld, tri)

    br, ho = REV_H.aussenmass()
    ob, oh = REV_H.oeffnung()
    print(f"\nZugring Rev. H  ->  tuerzwerg-zugring-revh.stl")
    print(f"  Aussen         {br:.0f} x {ho:.0f} x {D_BAND:.0f} mm, "
          f"Dicke ueberall gleich")
    print(f"  Oeffnung       {ob:.1f} x {oh:.1f} mm ({ob/D_FINGER:.1f} Finger)"
          f"   86 : {ob:.1f} = {86/ob:.3f}")
    print(f"  Band           23 / {B_SEITE:.1f} / {B_UNTEN:.1f} mm")
    print(f"  Griff unten    {B_UNTEN:.1f} x {D_BAND:.1f} = "
          f"{B_UNTEN/D_BAND:.3f}, Umfang {REV_H.griffumfang():.0f} mm")
    print(f"  Kammer         {2*REV_H.a_kammer:.0f} x {2*REV_H.b_kammer:.1f} mm "
          f"(Rev. E: 12 x 7,2 - im Realtest bewaehrt)")
    print(f"  Volumen        {vol/1000:.1f} cm^3 ({vol/1000*1.15:.0f} g)")
    print(f"  Dreiecke       {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    for s in (60, 70):
        print(f"  Shore A{s}      {REV_H.aufweitung(17.0, s):.1f} mm bei 17 N, "
              f"Grenze {REV_H.grenzkraft(s):.0f} N")
    print(f"  Kleinteile     {'besteht' if min(br, ho) > ZYLINDER else 'FAELLT DURCH'}"
          f", Klemmen {'ok' if 12 < ob < KOPF else 'PRUEFEN'}")

    print("\nVergleich bei Shore A 70:")
    print(f"  {'Entwurf':<10}{'aussen':>11}{'Oeffnung':>11}{'Dicke':>12}"
          f"{'Kammer':>12}{'17 N':>8}{'Grenze':>9}")
    for name, m in [("Rev. H", REV_H)] + VERGLEICH:
        b1, h1 = m.aussenmass()
        o1, o2 = m.oeffnung()
        d = (f"{m.d_oben:.0f}" if m.d_oben == m.d_unten
             else f"{m.d_oben:.0f}/{m.d_unten:.0f}")
        print(f"  {name:<10}{f'{b1:.0f} x {h1:.0f}':>11}"
              f"{f'{o1:.0f} x {o2:.0f}':>11}{d:>12}"
              f"{f'{2*m.a_kammer:.0f} x {2*m.b_kammer:.1f}':>12}"
              f"{m.aufweitung(17.0, 70):>7.1f} {m.grenzkraft(70):>7.0f} N")

    Z.zeichne(REV_H, VERGLEICH,
              datei="tuerzwerg-zugring-revh-zeichnung.svg",
              titel="Zugring Rev. H",
              untertitel="Band überall 11 mm · Kammer 14 × 7,2 wie im "
                         "Realtest bewährt · goldene Proportionen · "
                         "Shore A 60–70 · Maße in mm",
              eigen="Rev. H")
