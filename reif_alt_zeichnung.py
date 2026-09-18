#!/usr/bin/env python3
"""Vergleichsblatt der drei Zugringe: Silhouetten, Masse, Steifigkeit."""

import math
import reif_alt as RA

S = 2.3                                    # mm -> px
W, H = 1180, 760
INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=15, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def kontur(rfun, ox, oy, farbe, breite, n=720):
    d = []
    for i in range(n + 1):
        th = 2.0 * math.pi * i / n
        r = rfun(math.cos(th))
        x, y = ox + r * math.sin(th) * S, oy - r * math.cos(th) * S
        d.append(("M" if i == 0 else "L") + f"{x:.2f} {y:.2f}")
    out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{farbe}" '
               f'stroke-width="{breite}"/>')


txt(60, 56, "Türzwerg · Zugring · drei Entwürfe", 26, INK, 700)
txt(60, 82, "Silikon Shore A 50–60 · Maße in mm · 1:1 nicht maßstäblich "
            "gedruckt, Verhältnisse stimmen", 13, SOFT, 400)

spalten = [(230, RA.KREIS), (590, RA.TROPFEN), (950, RA.BUEGEL)]
oy = 300

for ox, r in spalten:
    kontur(r.aussen, ox, oy, INK, 2.0)
    kontur(r.innen, ox, oy, INK, 2.0)
    # Bandmitte gestrichelt
    d = []
    n = 360
    for i in range(n + 1):
        th = 2.0 * math.pi * i / n
        rr = r.aussen(math.cos(th)) - r.breite(math.cos(th)) / 2.0
        x, y = ox + rr * math.sin(th) * S, oy - rr * math.cos(th) * S
        d.append(("M" if i == 0 else "L") + f"{x:.2f} {y:.2f}")
    out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{LIN}" '
               f'stroke-width="1.0" stroke-dasharray="4 4"/>')

    # Schnur und Knoten andeuten
    top = r.aussen(1.0)
    out.append(f'<path d="M{ox} {oy - top*S:.1f}L{ox} {oy - top*S - 46:.1f}" '
               f'stroke="{AKZ}" stroke-width="2.4" fill="none"/>')
    innen_oben = r.innen(1.0)
    out.append(f'<circle cx="{ox}" cy="{oy - (innen_oben + 4)*S:.1f}" r="7" '
               f'fill="none" stroke="{AKZ}" stroke-width="1.8"/>')

    ab, ah = r.aussenmass()
    ob, oh = r.oeffnung()
    txt(ox, oy + ah / 2 * S + 44, r.titel.split("·")[1].strip(), 21, INK, 700, "middle")
    txt(ox, oy + ah / 2 * S + 66, f"{ab:.0f} × {ah:.0f} × {r.dicke:.0f}",
        14, SOFT, 500, "middle")

zeilen = [
    ("Öffnung", lambda r: "%.0f × %.0f" % r.oeffnung()),
    ("Band oben / seitlich / unten", lambda r: "%.0f / %.0f / %.0f"
     % (r.b_oben, r.b_seite, r.b_unten)),
    ("Griff unten, Umfang", lambda r: "%.0f × %.0f mm, %.0f"
     % (r.b_unten, r.dicke, r.griffumfang())),
    ("Silikon", lambda r: "%.0f g" % (0.0,)),
    ("Aufweitung bei 17 N · A 50", lambda r: "%.1f mm" % r.aufweitung(17.0, 50)[0]),
    ("Aufweitung bei 17 N · A 60", lambda r: "%.1f mm" % r.aufweitung(17.0, 60)[0]),
    ("ab hier über 10 % auf · A 60", lambda r: "%.0f N" % r.grenzkraft(60)),
]

y = 520
txt(60, y - 26, "Zahlen", 17, INK, 700)
for name, f in zeilen:
    if name == "Silikon":
        continue
    txt(60, y, name, 13, SOFT, 500)
    for ox, r in spalten:
        txt(ox, y, f(r), 14, INK, 600, "middle")
    out.append(f'<path d="M60 {y+7}L{W-60} {y+7}" stroke="{LIN}" '
               f'stroke-width="0.6"/>')
    y += 27

txt(60, H - 42, "Rot: Schnur und Knotenkammer. Gestrichelt: Bandmitte, "
                "an der gerechnet wird.", 12, SOFT, 400)
txt(60, H - 24, "Die Aufweitung geht mit der dritten Potenz des Radius und "
                "der dritten Potenz der Bandbreite – deshalb sind alle drei "
                "kleiner und breiter als der A-80-Reif.", 12, SOFT, 400)

out.append("</svg>")
open("tuerzwerg-zugring-vergleich.svg", "w").write("\n".join(out))
print("geschrieben")
