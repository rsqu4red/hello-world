#!/usr/bin/env python3
"""Schnittzeichnung der Reif-Giessform als SVG, 1:1 in mm skaliert."""

import math
import giessform_reif as F

S = 4.0                                  # mm -> px
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


def pfad(segs, tr, farbe, w=1.1):
    d = []
    for a, b in segs:
        ax, ay = tr(*a)
        bx, by = tr(*b)
        d.append(f"M{ax:.2f} {ay:.2f}L{bx:.2f} {by:.2f}")
    return (f'<path d="{"".join(d)}" fill="none" stroke="{farbe}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


W, H = 1240, 1080
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=15, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def b_mont(x, y, z):
    return F.feld_b(-x, y, F.DICKE - z)


# --- 1  Trennflaeche Haelfte A, Giesslage: +x ist oben --------------------
ox, oy = 80, 130
tr1 = lambda y, x: (ox + (y + 47) * S, oy + (47 - x) * S)
txt(ox, oy - 62, "1  Trennfläche Hälfte A", 19, INK, 700)
txt(ox, oy - 40, "Blick auf die Ebene z = 7. Gießlage: oben ist oben.", 13, SOFT, 400)
out.append(pfad(kontur(lambda y, x: F.feld_a(x, y, F.Z_TRENN - 0.02),
                       -47, 47, -47, 47, 300), tr1, INK, 1.2))
out.append(pfad(kontur(lambda y, x: F.REIF.feld(x, y, F.Z_TRENN - 0.02),
                       -47, 47, -47, 47, 300), tr1, AKZ, 1.5))
out.append(pfad(kontur(lambda y, x: F.kern(x, y, F.Z_TRENN - 0.02),
                       -47, 47, -47, 47, 300), tr1, KERN, 1.5))


def marke(y, x, s, anchor="start", dx=8):
    px, py = tr1(y, x)
    txt(px + dx, py + 4, s, 12, SOFT, 500, anchor)
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{AKZ}"/>')


marke(F._Y_TR, 44.5, "Trichter Ø11")
marke(-41, 0, "Bogen Ø5", "end", -8)
marke(0, -38, "Anschnitt Ø4 – unten")
marke(0, 40, "Entlüftung Ø2 – oben")
marke(30, 0, "loser Kern")
marke(38, 38, "Zentrierzapfen")
marke(-38, 38, "Zentriernut", "end", -8)

# --- 2  Schnitt x = 0 -----------------------------------------------------
ox2, oy2 = 800, 190
tr2 = lambda y, z: (ox2 + (y + 47) * S, oy2 + (19 - z) * S)
txt(ox2, oy2 - 62, "2  Schnitt x = 0", 19, INK, 700)
txt(ox2, oy2 - 40, "Der lose Kern in seinen beiden Sitzen.", 13, SOFT, 400)
for ff in (lambda y, z: F.feld_a(0.0, y, z), lambda y, z: b_mont(0.0, y, z)):
    out.append(pfad(kontur(ff, -47, 47, -6, 20, 300), tr2, INK, 1.2))
out.append(pfad(kontur(lambda y, z: F.REIF.feld(0.0, y, z), -47, 47, -6, 20, 300),
                tr2, AKZ, 1.5))
out.append(pfad(kontur(lambda y, z: F.kern(0.0, y, z), -47, 47, -6, 20, 300),
                tr2, KERN, 1.5))

# --- 3  Schnitt y = 0 -----------------------------------------------------
ox3, oy3 = 800, 560
tr3 = lambda x, z: (ox3 + (x + 47) * S, oy3 + (19 - z) * S)
txt(ox3, oy3 - 62, "3  Schnitt y = 0", 19, INK, 700)
txt(ox3, oy3 - 40, "Anschnitt links unten, Entlüftung rechts oben.", 13, SOFT, 400)
for ff in (lambda x, z: F.feld_a(x, 0.0, z), lambda x, z: b_mont(x, 0.0, z)):
    out.append(pfad(kontur(ff, -47, 47, -6, 20, 300), tr3, INK, 1.2))
out.append(pfad(kontur(lambda x, z: F.REIF.feld(x, 0.0, z), -47, 47, -6, 20, 300),
                tr3, AKZ, 1.5))

txt(80, H - 100, "rot = Silikonteil (Reif Rev. A)", 13, AKZ, 600)
txt(80, H - 78, "blau = loser Kern für Knotenkammer und Schnurbohrung", 13, KERN, 600)
txt(80, H - 56, "schwarz = Formkörper", 13, INK, 600)
txt(80, H - 26, "Türzwerg · Gießform Reif Rev. A · Maße in mm · "
                "gegossen wird hochkant, gefüllt von unten", 12, SOFT, 400)
out.append("</svg>")
open("tuerzwerg-giessform-reif.svg", "w").write("\n".join(out))
print("geschrieben")
