#!/usr/bin/env python3
"""
Türzwerg – die Ringkontur als Logopfad

Der Markenkern verlangt vom Zeichen: "Der Ring ist keine gezeichnete
Kreisform, sondern die echte Produktkontur - oben und unten breiter,
seitlich schmal. Damit ist die Marke nicht nachzeichenbar, ohne das
Produkt zu kennen."

Dieses Skript loest das Versprechen ein. Es tastet Aussen- und
Innenkontur von Rev. A phi ab - dieselben Funktionen, aus denen auch
das STL entsteht - und schreibt sie als SVG-Pfade. Aendert sich das
Bauteil, aendert sich das Logo mit; ein Zwischenschritt ueber ein
Zeichenprogramm, in dem die Kontur wieder zum Kreis wuerde, entfaellt.

Der Unterschied ist nicht kosmetisch: die Innenkontur schwankt um 44
Prozent ueber den Umfang, weil oben die Knotenkammer Platz braucht und
seitlich das Band schmal bleibt. Genau diese Unregelmaessigkeit ist die
Signatur.

Beide Pfade laufen im Uhrzeigersinn und werden mit fill-rule="evenodd"
uebereinandergelegt - der innere stanzt die Oeffnung aus.

    python3 logo_kontur.py
"""

import json
import math

from reif_eh import REV_A_PHI as R
from reif_mix import D_SCHNUR

DATEI = "logo_kontur.json"
PUNKTE = 120            # bei Logogroesse nicht von der Kurve zu unterscheiden
STELLEN = 1


def pfad(radius, n=PUNKTE):
    """Kontur als geschlossener SVG-Pfad. theta = 0 ist oben, y zeigt
    nach unten - das ist die SVG-Konvention, nicht die des Bauteils."""
    teile = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        r = radius(math.cos(th))
        x, y = r * math.sin(th), -r * math.cos(th)
        teile.append(("M" if i == 0 else "L")
                     + f"{x:.{STELLEN}f} {y:.{STELLEN}f}")
    return "".join(teile) + "Z"


def spanne(radius, n=720):
    werte = [radius(math.cos(2.0 * math.pi * i / n)) for i in range(n)]
    return min(werte), max(werte)


def svg_reif(datei="tuerzwerg-reif-zeichen.svg", farbe="#454A52", rand=2.0):
    """Der Reif allein, ohne Muetze und ohne Schnur.

    fill="currentColor" mit einem color-Attribut am <svg>: eingebettet
    erbt das Zeichen die Textfarbe, als eigenstaendige Datei zeigt es die
    angegebene. Die Oeffnung ist mit fill-rule evenodd ausgestanzt.
    """
    a = R.aussen(1.0) + rand
    inhalt = (f'<svg xmlns="http://www.w3.org/2000/svg" '
              f'viewBox="{-a:.0f} {-a:.0f} {2 * a:.0f} {2 * a:.0f}" '
              f'width="{2 * a:.0f}" height="{2 * a:.0f}" color="{farbe}" '
              f'role="img" aria-label="Türzwerg Reif">'
              f'<title>Türzwerg · Reif</title>'
              f'<path d="{pfad(R.aussen)}{pfad(R.innen)}" '
              f'fill="currentColor" fill-rule="evenodd"/></svg>\n')
    open(datei, "w", encoding="utf-8").write(inhalt)
    return datei


if __name__ == "__main__":
    i_min, i_max = spanne(R.innen)
    daten = {
        "quelle": "reif_eh.REV_A_PHI",
        "aussen": pfad(R.aussen),
        "innen": pfad(R.innen),
        "aussenmass": R.aussenmass(),
        "oeffnung": R.oeffnung(),
        "band": [R.b_oben, R.b_seite, R.b_unten],
        "dicke": R.d_oben,
        "d_schnur": D_SCHNUR,
        "innen_min": i_min,
        "innen_max": i_max,
    }
    json.dump(daten, open(DATEI, "w"), ensure_ascii=False)

    print(f"geschrieben: {DATEI}")
    print(f"  Aussenmass   {daten['aussenmass'][0]:.1f} x "
          f"{daten['aussenmass'][1]:.1f} mm")
    print(f"  Oeffnung     {daten['oeffnung'][0]:.1f} x "
          f"{daten['oeffnung'][1]:.1f} mm")
    print(f"  Band o/s/u   {R.b_oben:.1f} / {R.b_seite:.2f} / {R.b_unten:.1f}")
    print(f"  Schnur       Ø{D_SCHNUR:.0f}")
    print(f"  Innenkontur  {i_min:.1f} bis {i_max:.1f} mm  "
          f"= {(i_max / i_min - 1) * 100:.0f} % Unterschied")
    print(f"  Pfade        {len(daten['aussen'])} und "
          f"{len(daten['innen'])} Zeichen bei {PUNKTE} Punkten")
    print(f"geschrieben: {svg_reif()}  (Reif allein, ohne Muetze und Schnur)")
