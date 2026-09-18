#!/usr/bin/env python3
"""
Türzwerg – Zugring Rev. F: Rev. E, enger gefasst und gerundet

Rev. E hat die grosszuegigste Oeffnung aller Entwuerfe - 64 x 48 mm -
und ist zugleich der weichste. Beides hat dieselbe Ursache: das Band ist
an den Flanken nur 11 mm breit. Bei Shore A 70 und 11 mm Dicke zieht er
sich unter 17 N um 10,7 mm auf; seine Grenzkraft liegt bei 14 N,
unterhalb dessen, was das Oeffnen einer Tuer verlangt.

Rev. F behaelt Rev. E's Silhouette - ein exakter Kreis Ø 86 - und nimmt
von der Oeffnung zurueck, was das Band braucht:

    Band          Oeffnung      bei A 70    Grenze
    23/11/15      64 x 48       10,7 mm      14 N     <- Rev. E
    23/13/15      60 x 48        8,2 mm      18 N
    23/14/16      58 x 47        6,3 mm      23 N
    23/15/17      56 x 46        5,0 mm      29 N
    23/16/18      54 x 45        4,0 mm      37 N     <- Rev. F
    23/17/19      52 x 44        3,2 mm      46 N

10 mm weniger Oeffnung bringen den Faktor 2,7 an Steifigkeit. Damit
liegt Rev. F in derselben Klasse wie die uebrigen Kandidaten und hat
von ihnen die groesste Oeffnung: 54 mm gegen 53 beim Tropfen und 48
beim Kreis.

Gerundet fuer die Hand
----------------------

Rev. E hatte 40-Grad-Fasen an den Stirnflaechen. Die gab es nur, weil
er flach gedruckt wurde - im Giesswerkzeug bringen sie nichts und in
der Hand sind sie eine Kante.

Rev. F rundet stattdessen ueber den Umfang gestaffelt:

  unten   Eckradius voll - der Querschnitt ist ein echtes Stadion,
          18 x 11 mm rundum gewoelbt. Das ist die Zugstelle.
  oben    Eckradius 0,72 des halben Kleinstmasses. Flacher, weil die
          Knotenkammer dort Hoehe braucht.

Der Uebergang laeuft als Kosinus; es gibt keine Stelle, an der die
Rundung anfaengt. Keine Griffmulde an der Innenkante - sie traegt nur
auf zwei Kanten statt auf der vollen Breite, weil der Ring umgriffen
und nicht eingehaengt wird.

    python3 reif_revf.py
"""

from netz import vernetzen, volumen, offene_kanten, abweichung, schreibe_stl
from reif_mix import Mix, RASTER, D_FINGER, ZYLINDER, KOPF
import reif_mix_zeichnung as Z

REV_F = Mix(r0=43.0, e=0.0, w=0.0, b_oben=23.0, b_seite=16.0, b_unten=18.0)

VERGLEICH = [
    ("Rev. E", Mix(r0=43.0, e=0.0, w=0.0,
                   b_oben=23.0, b_seite=11.0, b_unten=15.0,
                   eck_oben=0.85, eck_unten=0.85)),
    ("Mix", Mix()),
    ("Tropfen w = 2", Mix(r0=40.0, e=4.5, w=2.0,
                          b_oben=21.0, b_seite=16.0, b_unten=18.0,
                          eck_oben=0.85, eck_unten=0.85)),
    ("Kreis", Mix(r0=40.0, e=0.0, w=0.0,
                  b_oben=21.0, b_seite=16.0, b_unten=18.0,
                  eck_oben=0.85, eck_unten=0.85)),
]

if __name__ == "__main__":
    print("Vernetze Rev. F ...")
    tri = vernetzen(REV_F.feld, REV_F.grenzen(), RASTER)
    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol
    schreibe_stl(tri, "tuerzwerg-zugring-revf.stl",
                 "Tuerzwerg Zugring Rev. F - Masse in mm")
    ab_max, ab_mit = abweichung(REV_F.feld, tri)

    br, ho = REV_F.aussenmass()
    ob, oh = REV_F.oeffnung()
    print(f"\nZugring Rev. F  ->  tuerzwerg-zugring-revf.stl")
    print(f"  Aussen         {br:.0f} x {ho:.0f} x {REV_F.d_oben:.0f} mm")
    print(f"  Oeffnung       {ob:.0f} x {oh:.0f} mm "
          f"({ob/D_FINGER:.1f} Finger zu {D_FINGER:.0f} mm)")
    print(f"  Band           {REV_F.b_oben:.0f} / {REV_F.b_seite:.0f} / "
          f"{REV_F.b_unten:.0f} mm")
    print(f"  Griff unten    {REV_F.b_unten:.0f} x {REV_F.dicke(-1.0):.0f} mm, "
          f"Umfang {REV_F.griffumfang():.0f} mm, Eckradius voll")
    print(f"  Volumen        {vol/1000:.1f} cm^3 ({vol/1000*1.15:.0f} g)")
    print(f"  Dreiecke       {len(tri)}, offene Kanten {offene_kanten(tri)}")
    print(f"  Formtreue      hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    for s in (60, 70):
        print(f"  Shore A{s}      {REV_F.aufweitung(17.0, s):.1f} mm bei 17 N, "
              f"Grenze {REV_F.grenzkraft(s):.0f} N")
    print(f"  Kleinteile     {'besteht' if min(br, ho) > ZYLINDER else 'FAELLT DURCH'}"
          f", Klemmen {'ok' if 12 < ob < KOPF else 'PRUEFEN'}")

    print("\nVergleich bei Shore A 70:")
    print(f"  {'Entwurf':<16}{'aussen':>11}{'Oeffnung':>11}{'Band':>13}"
          f"{'17 N':>8}{'Grenze':>9}{'Griff':>8}")
    for name, m in [("Rev. F", REV_F)] + VERGLEICH:
        b1, h1 = m.aussenmass()
        o1, o2 = m.oeffnung()
        print(f"  {name:<16}{f'{b1:.0f} x {h1:.0f}':>11}"
              f"{f'{o1:.0f} x {o2:.0f}':>11}"
              f"{f'{m.b_oben:.0f}/{m.b_seite:.0f}/{m.b_unten:.0f}':>13}"
              f"{m.aufweitung(17.0, 70):>7.1f} {m.grenzkraft(70):>7.0f} N"
              f"{m.griffumfang():>6.0f} mm")

    Z.zeichne(REV_F, VERGLEICH,
              datei="tuerzwerg-zugring-revf-zeichnung.svg",
              titel="Zugring Rev. F",
              untertitel="Rev. E mit engerer Öffnung, breiterem Band und "
                         "gerundetem Querschnitt · Shore A 60–70 · Maße in mm",
              eigen="Rev. F")
