#!/usr/bin/env python3
"""
Türzwerg – Zugring Rev. G: groessere Knotenkammer, goldene Proportionen

Die Knotenkammer
----------------

Rev. F hatte 14 x 7,2 mm. Die 7,2 sind das, was von 11 mm Bandtiefe
uebrig bleibt, wenn oben und unten 1,9 mm Wand stehen. Ein Knoten in
3-mm-Schnur misst rund 7 mm und passt gerade; einer in 4-mm-Schnur misst
rund 9 mm und passt nicht.

Mehr Hoehe gibt es in einem 11 mm dicken Band nicht - ausser man nimmt
Wand weg, und die steht schon auf dem Rev.-E-Mass. Also wird das Band
dort dicker, wo die Kammer sitzt: 14 mm am Scheitel, 11 mm unten am
Griff. Das ist kein Widerspruch zur Vorgabe "11 mm dick" - gegriffen
wird unten, und dort bleiben es 11 mm.

Damit: Kammer 16,5 x 10,2 mm statt 14 x 7,2. Ein 4-mm-Knoten geht
hinein, ohne dass man ihn hineinzwingt.

Die Dickenaenderung ist dieselbe Kosinusfunktion, die frueher schon
einmal drin war und wieder herausflog. Der Unterschied: damals machte
sie das Band unten fuelliger, mit der vagen Begruendung "besser in der
Hand" - nachgerechnet kostete das 4 mm Griffumfang fuer 0,7 mm
Steifigkeit. Jetzt macht sie das Band oben dicker, aus einem messbaren
Grund, und laesst den Griff in Ruhe.

Goldener Schnitt
----------------

Nachgemessen, bevor etwas geaendert wurde, hatte Rev. F schon zwei
Verhaeltnisse dicht an phi = 1,618:

    Aussen : Oeffnung        86 : 54   = 1,593   -1,6 %
    Griff Breite : Dicke     18 : 11   = 1,636   +1,1 %

Das ist kein Zufall im mystischen Sinn, sondern einer im statistischen:
beide Masse entstanden aus Steifigkeit und Handgroesse, unabhaengig
voneinander, und landeten zufaellig nebeneinander. Genau deshalb kostet
es nichts, sie exakt zu machen - es sind Aenderungen von unter einem
Millimeter:

    Aussen : Oeffnung        86 : 53,2   = phi   (Band seitlich 16,4)
    Griff Breite : Dicke     17,8 : 11,0 = phi
    Kammer Breite : Hoehe    16,5 : 10,2 = phi

phi ist hier ein Ordnungsmittel, keine Mechanik. Es macht den Masssatz
zusammenhaengend statt zufaellig; messbar besser wird davon nichts. Was
nicht auf phi gezwungen wurde: Bandbreite oben zu unten, Aussen zu
Oeffnungshoehe. Dort haetten die Proportionen um 20 bis 30 Prozent
verschoben werden muessen, und das haette Funktion gekostet.

Fibonacci steckt schon drin: die Schnurbohrung misst 5 mm. Wer die
ganze Reihe will, nimmt Aussen 89 und Oeffnung 55 - benachbarte
Fibonacci-Zahlen stehen immer im Verhaeltnis phi. Das waere ein um
3 mm groesserer Ring; hier bleibt es bei 86.

    python3 reif_revg.py
"""

from netz import vernetzen, volumen, offene_kanten, abweichung, schreibe_stl
from reif_mix import Mix, RASTER, D_FINGER, ZYLINDER, KOPF, WAND_KAMMER
import reif_mix_zeichnung as Z

PHI = (1.0 + 5.0 ** 0.5) / 2.0

R_AUSSEN = 43.0                      # Ø 86 wie Rev. E und F
OEFFNUNG = 2.0 * R_AUSSEN / PHI      # 53,2 - goldenes Verhaeltnis
B_SEITE = R_AUSSEN - OEFFNUNG / 2.0  # 16,4
D_GRIFF = 11.0
B_UNTEN = D_GRIFF * PHI              # 17,8 - Griff im goldenen Verhaeltnis
D_KOPF = 14.0                        # damit die Kammer 10,2 mm hoch wird
H_KAMMER = D_KOPF - 2.0 * WAND_KAMMER
B_KAMMER = H_KAMMER * PHI            # 16,5 - Kammer im goldenen Verhaeltnis

REV_G = Mix(r0=R_AUSSEN, e=0.0, w=0.0,
            b_oben=23.0, b_seite=B_SEITE, b_unten=B_UNTEN,
            d_oben=D_KOPF, d_unten=D_GRIFF,
            a_kammer=B_KAMMER / 2.0, b_kammer=H_KAMMER / 2.0)

VERGLEICH = [
    ("Rev. F", Mix(r0=43.0, e=0.0, w=0.0,
                   b_oben=23.0, b_seite=16.0, b_unten=18.0)),
    ("Rev. E", Mix(r0=43.0, e=0.0, w=0.0,
                   b_oben=23.0, b_seite=11.0, b_unten=15.0,
                   eck_oben=0.85, eck_unten=0.85)),
    ("Tropfen w = 2", Mix(r0=40.0, e=4.5, w=2.0,
                          b_oben=21.0, b_seite=16.0, b_unten=18.0,
                          eck_oben=0.85, eck_unten=0.85)),
    ("Kreis", Mix(r0=40.0, e=0.0, w=0.0,
                  b_oben=21.0, b_seite=16.0, b_unten=18.0,
                  eck_oben=0.85, eck_unten=0.85)),
]

if __name__ == "__main__":
    print(f"phi = {PHI:.4f}")
    print(f"Oeffnung {OEFFNUNG:.1f}  Band seitlich {B_SEITE:.1f}  "
          f"Griff {B_UNTEN:.1f} x {D_GRIFF:.1f}  "
          f"Kammer {B_KAMMER:.1f} x {H_KAMMER:.1f}")

    print("\nVernetze Rev. G ...")
    tri = vernetzen(REV_G.feld, REV_G.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, "tuerzwerg-zugring-revg.stl",
                 "Tuerzwerg Zugring Rev. G - Masse in mm")
    ab_max, ab_mit = abweichung(REV_G.feld, tri)

    br, ho = REV_G.aussenmass()
    ob, oh = REV_G.oeffnung()
    print(f"\nZugring Rev. G  ->  tuerzwerg-zugring-revg.stl")
    print(f"  Aussen         {br:.0f} x {ho:.0f} mm, "
          f"{D_KOPF:.0f} mm am Scheitel / {D_GRIFF:.0f} mm am Griff")
    print(f"  Oeffnung       {ob:.1f} x {oh:.1f} mm "
          f"({ob/D_FINGER:.1f} Finger)   86 : {ob:.1f} = {86/ob:.3f}")
    print(f"  Band           23 / {B_SEITE:.1f} / {B_UNTEN:.1f} mm")
    print(f"  Griff unten    {B_UNTEN:.1f} x {D_GRIFF:.1f} mm "
          f"= {B_UNTEN/D_GRIFF:.3f}, Umfang {REV_G.griffumfang():.0f} mm")
    print(f"  Kammer         {B_KAMMER:.1f} x {H_KAMMER:.1f} mm "
          f"= {B_KAMMER/H_KAMMER:.3f}  (Rev. F: 14,0 x 7,2)")
    print(f"  Volumen        {vol/1000:.1f} cm^3 ({vol/1000*1.15:.0f} g)")
    print(f"  Dreiecke       {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    for s in (60, 70):
        print(f"  Shore A{s}      {REV_G.aufweitung(17.0, s):.1f} mm bei 17 N, "
              f"Grenze {REV_G.grenzkraft(s):.0f} N")
    print(f"  Kleinteile     {'besteht' if min(br, ho) > ZYLINDER else 'FAELLT DURCH'}"
          f", Klemmen {'ok' if 12 < ob < KOPF else 'PRUEFEN'}")

    print("\nVergleich bei Shore A 70:")
    print(f"  {'Entwurf':<16}{'aussen':>11}{'Oeffnung':>11}{'Kammer':>13}"
          f"{'17 N':>8}{'Grenze':>9}")
    for name, m in [("Rev. G", REV_G)] + VERGLEICH:
        b1, h1 = m.aussenmass()
        o1, o2 = m.oeffnung()
        print(f"  {name:<16}{f'{b1:.0f} x {h1:.0f}':>11}"
              f"{f'{o1:.0f} x {o2:.0f}':>11}"
              f"{f'{2*m.a_kammer:.1f} x {2*m.b_kammer:.1f}':>13}"
              f"{m.aufweitung(17.0, 70):>7.1f} {m.grenzkraft(70):>7.0f} N")

    Z.zeichne(REV_G, VERGLEICH,
              datei="tuerzwerg-zugring-revg-zeichnung.svg",
              titel="Zugring Rev. G",
              untertitel="Größere Knotenkammer, Kopf 14 mm / Griff 11 mm, "
                         "goldene Proportionen · Shore A 60–70 · Maße in mm",
              eigen="Rev. G")
