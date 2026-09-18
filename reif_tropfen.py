#!/usr/bin/env python3
"""
Türzwerg – Zugring Tropfen, Breitenreihe

"Leicht breiter" laesst sich auf zwei Arten lesen, deshalb zeigt das
Blatt beide.

Geweitet wird ueber einen sin^2-Term:

    r(theta) = r0 - e*cos(theta) + w*sin(theta)^2

sin^2 ist oben und unten null und an den Flanken eins. Die Weitung wirkt
also genau dort, wo die Silhouette breiter werden soll, und laesst Scheitel
und Boden unberuehrt - die Hoehe bleibt bei allen 80 mm, nur die Breite
waechst.

Lesart A (Felder 2 bis 4): das Band bleibt, die Oeffnung waechst mit.
Der Ring wird breiter und luftiger, aber auch weicher - der mittlere
Radius waechst, und die Aufweitung geht mit seiner dritten Potenz.

Lesart B (Feld 5): die Oeffnung bleibt, das Band waechst an den Flanken.
Die Silhouette wird genauso breit, der Ring dabei aber steifer statt
weicher. Optisch sitzt das Material dann sichtbar an den Seiten.

    python3 reif_tropfen.py
"""

import math
from reif_uebersicht2 import Kontur, kosinusband

TAU = 2.0 * math.pi
R0, E = 40.0, 4.5
BAND = (21.0, 16.0, 18.0)


def tropfen(r0, e, w):
    """Tropfenkontur, an den Flanken um w geweitet."""
    def f(th):
        s = math.sin(th)
        return r0 - e * math.cos(th) + w * s * s
    return f


def band_von(aussen, bo, bs, bu):
    """Innenkontur: Aussenkontur minus Kosinusband."""
    a0 = (bo + 2 * bs + bu) / 4.0
    a1 = (bo - bu) / 2.0
    a2 = (bo - 2 * bs + bu) / 4.0
    def f(th):
        c = math.cos(th)
        return aussen(th) - (a0 + a1 * c + a2 * (2 * c * c - 1))
    return f


ENTWUERFE = []
for w, titel, notiz in [
        (0.0, "Tropfen  w = 0", "Wie gehabt. Der Vergleichspunkt."),
        (2.0, "w = 2", "Kaum zu sehen, aber die Rundung wirkt voller."),
        (4.0, "w = 4", "Deutlich breiter, bleibt trotzdem ein Tropfen."),
        (6.0, "w = 6", "Schon fast ein Querformat. Untere Grenze der Steife.")]:
    a = tropfen(R0, E, w)
    ENTWUERFE.append(Kontur(f"w{w:.0f}", titel, a, band_von(a, *BAND),
                            15.0, 60, notiz))

# Lesart B: Oeffnung bleibt die des Referenztropfens, Band waechst mit
a0 = tropfen(R0, E, 0.0)
innen_fest = band_von(a0, *BAND)
a4 = tropfen(R0, E, 4.0)
ENTWUERFE.append(Kontur("fest", "w = 4, Öffnung fest", a4, innen_fest,
                        15.0, 60,
                        "Gleiche Silhouette wie Feld 3, aber die Öffnung "
                        "bleibt. Das Band wächst an den Flanken – steifer "
                        "statt weicher."))

# ---------------------------------------------------------------- Blatt -----

S = 2.05
W, H = 1280, 640
INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=14, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def pfad(f, ox, oy, farbe, br, strich=None, n=540):
    d = []
    for i in range(n + 1):
        th = TAU * i / n
        r = f(th)
        d.append(("M" if i == 0 else "L")
                 + f"{ox + r*math.sin(th)*S:.2f} {oy - r*math.cos(th)*S:.2f}")
    dash = f' stroke-dasharray="{strich}"' if strich else ""
    out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{farbe}" '
               f'stroke-width="{br}"{dash}/>')


txt(52, 50, "Türzwerg · Zugring Tropfen · wie breit?", 26, INK, 700)
txt(52, 76, "Weitung nur an den Flanken, Höhe bleibt 80 mm · "
            "gleicher Maßstab · Shore A 60", 13, SOFT, 400)

X0, BREIT, OY = 178, 243, 280
for i, k in enumerate(ENTWUERFE):
    ox = X0 + i * BREIT
    if i > 0:
        pfad(ENTWUERFE[0].aussen, ox, OY, LIN, 1.0, "3 4")
    pfad(k.aussen, ox, OY, INK, 2.2)
    pfad(k.innen, ox, OY, INK, 2.2)

    top = k.aussen(0.0)
    out.append(f'<path d="M{ox} {OY - top*S:.1f}L{ox} {OY - top*S - 30:.1f}" '
               f'stroke="{AKZ}" stroke-width="2.2"/>')
    out.append(f'<circle cx="{ox}" cy="{OY - (k.innen(0.0)+4)*S:.1f}" r="6" '
               f'fill="none" stroke="{AKZ}" stroke-width="1.6"/>')

    ab, ah = k.aussenmass()
    ob, oh = k.oeffnung()
    bo, bs, bu = k.bandmasse()
    y = OY + ah / 2 * S + 40
    txt(ox, y, k.titel, 19, INK, 700, "middle")
    txt(ox, y + 24, f"{ab:.0f} × {ah:.0f} mm", 14, INK, 600, "middle")
    txt(ox, y + 43, f"Öffnung {ob:.0f} × {oh:.0f}", 12.5, SOFT, 500, "middle")
    txt(ox, y + 60, f"Band {bo:.0f}/{bs:.0f}/{bu:.0f}", 12.5, SOFT, 500, "middle")
    txt(ox, y + 80, f"{k.aufweitung(17.0):.1f} mm auf · {k.grenzkraft():.0f} N",
        13, INK, 600, "middle")
    worte, zeile, zeilen = k.notiz.split(), "", []
    for wort in worte:
        if len(zeile) + len(wort) > 30:
            zeilen.append(zeile); zeile = wort
        else:
            zeile = (zeile + " " + wort).strip()
    zeilen.append(zeile)
    for j, zl in enumerate(zeilen):
        txt(ox, y + 100 + j * 15, zl, 11.5, SOFT, 400, "middle")

txt(52, H - 42, "Gestrichelt: der Referenztropfen w = 0 zum Vergleich.", 12, SOFT, 400)
txt(52, H - 22, "Weiten kostet Steifigkeit, solange die Öffnung mitwächst – "
                "der mittlere Radius geht mit der dritten Potenz ein. "
                "Feld 5 zeigt, wie man das vermeidet.", 12, SOFT, 400)
out.append("</svg>")
open("tuerzwerg-zugring-tropfen-breite.svg", "w").write("\n".join(out))

print(f"{'Entwurf':<22}{'aussen':>11}{'Oeffnung':>12}{'Band':>13}"
      f"{'17 N':>8}{'Grenze':>9}")
for k in ENTWUERFE:
    ab, ah = k.aussenmass()
    ob, oh = k.oeffnung()
    bo, bs, bu = k.bandmasse()
    print(f"{k.titel:<22}{f'{ab:.0f} x {ah:.0f}':>11}{f'{ob:.0f} x {oh:.0f}':>12}"
          f"{f'{bo:.0f}/{bs:.0f}/{bu:.0f}':>13}{k.aufweitung(17.0):>7.1f} "
          f"{k.grenzkraft():>6.0f} N")
print("\ngeschrieben: tuerzwerg-zugring-tropfen-breite.svg")
