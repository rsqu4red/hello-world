#!/usr/bin/env python3
"""Wo das Silikon eingefuellt wird - zwei Schnitte als SVG, 1:1 in mm."""

import math
import giessform as F

S = 5.2
INK, AKZ, SOFT, KERN = "#161A17", "#C7422A", "#5E665E", "#38689B"


def kontur(f, x0, x1, y0, y1, n):
    segs = []
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    v = [[f(x0 + i * dx, y0 + j * dy) for j in range(n + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(n):
            p = [(x0 + i * dx, y0 + j * dy, v[i][j]),
                 (x0 + (i + 1) * dx, y0 + j * dy, v[i + 1][j]),
                 (x0 + (i + 1) * dx, y0 + (j + 1) * dy, v[i + 1][j + 1]),
                 (x0 + i * dx, y0 + (j + 1) * dy, v[i][j + 1])]
            kr = []
            for k in range(4):
                a, b = p[k], p[(k + 1) % 4]
                if (a[2] < 0) != (b[2] < 0):
                    t = a[2] / (a[2] - b[2])
                    kr.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            if len(kr) == 2:
                segs.append((kr[0], kr[1]))
            elif len(kr) == 4:
                segs.append((kr[0], kr[1]))
                segs.append((kr[2], kr[3]))
    return segs


def pfad(segs, tr, farbe, w=1.2):
    d = []
    for a, b in segs:
        ax, ay = tr(*a)
        bx, by = tr(*b)
        d.append(f"M{ax:.2f} {ay:.2f}L{bx:.2f} {by:.2f}")
    return (f'<path d="{"".join(d)}" fill="none" stroke="{farbe}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


W, H = 1180, 860
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=15, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def pfeil(x, y, laenge=34):
    out.append(f'<path d="M{x} {y - laenge}L{x} {y}M{x - 6} {y - 9}L{x} {y}'
               f'L{x + 6} {y - 9}" fill="none" stroke="{AKZ}" '
               f'stroke-width="2.4" stroke-linecap="round"/>')


def form(x, y, z):
    return min(F.haelfte(x, y, z), F.haelfte(-x, -y, z))


# --- 1  Draufsicht auf die Eingussseite -----------------------------------
ox, oy = 90, 150
tr1 = lambda x, y: (ox + (x + 30) * S, oy + (26 - y) * S)
txt(ox, oy - 74, "1  Draufsicht auf die Eingussseite", 19, INK, 700)
txt(ox, oy - 52, "Die Form steht auf den Füßen, Kuppe unten. Das hier ist oben.",
    13, SOFT, 400)
out.append(pfad(kontur(lambda x, y: form(x, y, F.Z_KOPF + 0.5),
                       -30, 30, -26, 26, 260), tr1, INK))
out.append(pfad(kontur(lambda x, y: F.kern_unten(x, y, F.Z_KOPF + 0.5),
                       -30, 30, -26, 26, 260), tr1, KERN, 1.5))
for vz in (1, -1):
    px, py = tr1(vz * F.KANAL_X, 0.0)
    pfeil(px, py - 16)
    txt(px, py + 5, "Ø10,8", 12, AKZ, 700, "middle")
txt(tr1(11, 0)[0], tr1(11, 0)[1] - 58, "hier eingießen", 13, AKZ, 700, "middle")
txt(tr1(-11, 0)[0], tr1(-11, 0)[1] - 58, "hier steigt es hoch", 13, AKZ, 700,
    "middle")
txt(tr1(0, -24)[0], tr1(0, -24)[1] + 22, "Schaft des unteren Kerns, "
    "darüber der Steg mit zwei Lagestiften", 12, KERN, 500, "middle")

# --- 2  Laengsschnitt -----------------------------------------------------
ox2, oy2 = 700, 90
tr2 = lambda x, z: (ox2 + (x + 30) * S, oy2 + (z + 16) * S)
txt(ox2, oy2 - 14, "2  Längsschnitt durch die Trennebene", 19, INK, 700)
txt(ox2, oy2 + 8, "Der Weg des Silikons: Trichter, Kanal, Kavität.", 13, SOFT, 400)
out.append(pfad(kontur(lambda x, z: F.haelfte(x, -0.3, z),
                       -30, 30, -16, 104, 300), tr2, INK))
out.append(pfad(kontur(lambda x, z: min(F.kern_unten(x, -0.3, z),
                                        F.kern_oben(x, -0.3, z)),
                       -30, 30, -16, 104, 300), tr2, KERN, 1.5))
pfeil(tr2(11, F.Z_KOPF)[0], tr2(11, F.Z_KOPF)[1] - 4, 30)
txt(tr2(11, F.Z_KOPF)[0], tr2(11, F.Z_KOPF)[1] - 40, "eingießen", 12, AKZ, 700,
    "middle")
txt(tr2(-11, F.Z_KOPF)[0], tr2(-11, F.Z_KOPF)[1] - 40, "beobachten", 12, AKZ,
    700, "middle")
for zz, s in ((0.0, "Bodenfläche des Griffs"), (F.HOEHE, "Kuppe"),
              (F.Z_FUGE, "Fuge der beiden Kerne")):
    px, py = tr2(30, zz)
    out.append(f'<path d="M{px - 2} {py}L{px + 14} {py}" stroke="{SOFT}" '
               f'stroke-width="0.9" stroke-dasharray="4 3"/>')
    txt(px + 18, py + 4, s, 11, SOFT, 500)

txt(90, H - 62, "rot = Einguss und Entlüftung", 13, AKZ, 600)
txt(90, H - 40, "blau = die beiden losen Kerne", 13, KERN, 600)
txt(90, H - 18, "schwarz = Formkörper · Türzwerg Gießform Griff · Maße in mm",
    12, SOFT, 400)
out.append("</svg>")
open("tuerzwerg-giessform-griff.svg", "w").write("\n".join(out))
print("geschrieben")
