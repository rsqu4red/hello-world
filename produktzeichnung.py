#!/usr/bin/env python3
"""
Türzwerg – Produktzeichnungen für den Shop

Zwei Blaetter, beide als SVG:

    tuerzwerg-produkt-teile.svg     Reif und Manschette, gleicher Massstab
    tuerzwerg-produkt-montiert.svg  beides am Druecker, mit Greifhoehe

Nichts daran ist nachgezeichnet. Der Reifumriss kommt aus REV_A_PHI, seine
Seitenansicht aus Mix.projektion(), der Manschettenquerschnitt aus dem
Distanzfeld in manschette.py - polar abgetastet, weil die Form vom
Mittelpunkt aus sternfoermig ist und jeder Strahl den Rand genau einmal
trifft. Aendert sich ein Bauteil, aendert sich die Zeichnung mit.

Die Farbe steht als CSS-Variable --produkt im <svg>. Der Shop kann sie je
Produktfarbe ueberschreiben, ohne die Datei zu tauschen - das ist die
Regel aus dem Markenkern: die Seite ist farblos, die Farbe kommt vom
Produkt.

    python3 produktzeichnung.py
"""

import math

import manschette as M
from netz import weich_vereinen
from reif_eh import REV_A_PHI as R

INK, LEISE, LINIE, GRUND = "#17160F", "#6C675A", "#D8DDD6", "#FBFAF7"
AKZ = "#D2452B"
SCHRIFT = ("IBM Plex Sans Condensed,Figtree,DejaVu Sans Condensed,sans-serif")
MONO = "IBM Plex Mono,ui-monospace,monospace"


# ------------------------------------------------------------- Geometrie ----

def reif_kontur(f, n=180):
    p = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        r = f(math.cos(th))
        p.append(("M" if i == 0 else "L")
                 + f"{r * math.sin(th):.2f} {-r * math.cos(th):.2f}")
    return "".join(p) + "Z"


def reif_seite():
    """Silhouette des Reifs von der Seite, aus der eigenen Projektion."""
    lo, hi, bins = R.projektion("y")
    n = len(bins) - 1
    vor = [f"{'M' if i == 0 else 'L'}{bins[i]:.2f} "
           f"{-(lo + (hi - lo) * i / n):.2f}" for i in range(n + 1)]
    zurueck = [f"L{-bins[i]:.2f} {-(lo + (hi - lo) * i / n):.2f}"
               for i in range(n, -1, -1)]
    return "".join(vor + zurueck) + "Z"


def _manschette_profil(x, y):
    return weich_vereinen(math.hypot(x, y) - M.R_AUSSEN,
                          math.hypot(x, y + M.KAMMER_ACHSE) - M.R_RIPPE,
                          M.VERRUNDUNG)


def manschette_quer(n=240):
    """Aussenkontur des Manschettenquerschnitts, polar abgetastet."""
    p = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        c, s = math.cos(th), math.sin(th)
        lo, hi = 0.0, 34.0
        for _ in range(48):
            m = (lo + hi) / 2.0
            if _manschette_profil(c * m, s * m) < 0.0:
                lo = m
            else:
                hi = m
        p.append(("M" if i == 0 else "L") + f"{c * lo:.2f} {s * lo:.2f}")
    return "".join(p) + "Z"


def manschette_seite(n=120):
    """Von der Seite: oben die Rampe, unten der durchlaufende Kiel."""
    oben, unten = [], []
    for i in range(n + 1):
        z = M.LAENGE * i / n
        y = M.R_AUSSEN - M._ruecknahme(z)
        oben.append(f"{'M' if i == 0 else 'L'}{z:.2f} {-y:.2f}")
        unten.append(f"L{M.LAENGE - z:.2f} {M.RIPPE_UNTEN:.2f}")
    return "".join(oben + unten) + "Z"


# ------------------------------------------------------------- Zeichnen -----

class Blatt:
    def __init__(self, w, h, titel):
        self.w, self.h = w, h
        self.o = [f'<svg xmlns="http://www.w3.org/2000/svg" '
                  f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                  f'style="--produkt:{AKZ}" role="img" aria-label="{titel}">'
                  f'<title>{titel}</title>'
                  f'<rect width="{w}" height="{h}" fill="{GRUND}"/>']

    def txt(self, x, y, s, gr=13, f=INK, w=600, an="start", mono=False):
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family='
                      f'"{MONO if mono else SCHRIFT}" font-size="{gr}" '
                      f'font-weight="{w}" fill="{f}" text-anchor="{an}">{s}</text>')

    def linie(self, x1, y1, x2, y2, f=LINIE, b=1.0, strich=None):
        d = f' stroke-dasharray="{strich}"' if strich else ""
        self.o.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" '
                      f'stroke="{f}" stroke-width="{b}" fill="none"{d}/>')

    def form(self, d, ox, oy, s, fuell="var(--produkt)", strich=None, b=1.4):
        self.o.append(f'<g transform="translate({ox} {oy}) scale({s})">'
                      f'<path d="{d}" fill="{fuell}" fill-rule="evenodd"'
                      + (f' stroke="{strich}" stroke-width="{b / s:.3f}"'
                         if strich else "") + '/></g>')

    def mass(self, x1, y1, x2, y2, text, f=LEISE):
        self.linie(x1, y1, x2, y2, f, 1.0)
        for (px, py), vz in (((x1, y1), 1), ((x2, y2), -1)):
            dx, dy = x2 - x1, y2 - y1
            n = math.hypot(dx, dy) or 1.0
            dx, dy = dx / n * 8 * vz, dy / n * 8 * vz
            self.o.append(f'<path d="M{px:.1f} {py:.1f}'
                          f'l{dx - dy * .3:.1f} {dy + dx * .3:.1f}'
                          f'M{px:.1f} {py:.1f}'
                          f'l{dx + dy * .3:.1f} {dy - dx * .3:.1f}" '
                          f'stroke="{f}" stroke-width="1" fill="none"/>')
        senk = abs(y2 - y1) > abs(x2 - x1)
        self.txt((x1 + x2) / 2 + (11 if senk else 0),
                 (y1 + y2) / 2 + (4 if senk else -9), text, 12.5, f, 600,
                 "start" if senk else "middle", mono=True)

    def schreibe(self, datei):
        self.o.append("</svg>")
        open(datei, "w", encoding="utf-8").write("\n".join(self.o))
        return datei


# ------------------------------------------------------------ Blatt eins ----

def teile(datei="tuerzwerg-produkt-teile.svg"):
    S = 4.2                                   # Pixel je Millimeter
    b = Blatt(1240, 720, "Türzwerg · Zugring und Manschette")
    b.txt(56, 62, "Türzwerg", 30, INK, 700)
    b.txt(56, 88, "Zugring und Klinkenmanschette · gleicher Maßstab · "
                  "Maße in Millimeter", 14, LEISE, 400)
    b.linie(56, 112, 1184, 112, LINIE, 1.4)

    # Reif, Vorderansicht
    rx, ry = 270, 330
    b.txt(rx, 156, "Zugring", 20, INK, 700, "middle")
    b.form(reif_kontur(R.aussen) + reif_kontur(R.innen), rx, ry, S)
    b.mass(rx - 36 * S, ry + 36 * S + 30, rx + 36 * S, ry + 36 * S + 30, "Ø72")
    ob, oh = R.oeffnung()
    b.mass(rx - ob / 2 * S, ry - 4, rx + ob / 2 * S, ry - 4, f"{ob:.1f}")
    b.txt(rx, ry + 36 * S + 62, "Öffnung 48,6 × 38,0", 13, LEISE, 500, "middle")

    # Reif, Seitenansicht
    sx = 520
    b.txt(sx, 156, "von der Seite", 15, LEISE, 600, "middle")
    b.form(reif_seite(), sx, ry, S)
    b.mass(sx - 7 * S, ry + 36 * S + 30, sx + 7 * S, ry + 36 * S + 30, "14")

    # Manschette, Querschnitt
    mx, my = 800, 318
    b.txt(mx, 156, "Klinkenmanschette", 20, INK, 700, "middle")
    b.form(manschette_quer(), mx, my, S)
    b.o.append(f'<circle cx="{mx}" cy="{my}" r="{M.R_INNEN * S:.1f}" '
               f'fill="{GRUND}"/>')
    b.o.append(f'<path d="M{mx - M.D_KAMMER / 2 * S:.1f} {my + 0:.1f}'
               f'h{M.D_KAMMER * S:.1f}v{(M.KAMMER_ACHSE + M.D_KAMMER / 2) * S - 0:.1f}'
               f'h{-M.D_KAMMER * S:.1f}Z" fill="{GRUND}" stroke="{AKZ}" '
               f'stroke-width="1.2" stroke-dasharray="4 3"/>')
    b.mass(mx - 12 * S, my + 19.5 * S + 30, mx + 12 * S, my + 19.5 * S + 30, "Ø24")
    b.mass(mx + 12 * S + 28, my - 12 * S, mx + 12 * S + 28, my + 19.5 * S, "31,5")
    b.txt(mx, my + 19.5 * S + 62, "Bohrung Ø18 · Knotenkammer 11 × 11",
          13, LEISE, 500, "middle")

    # Manschette, Seitenansicht
    lx, ly = 1010, my
    b.txt(lx + 14 * S / 2, 156, "von der Seite", 15, LEISE, 600, "middle")
    b.form(manschette_seite(), lx - M.LAENGE / 2 * S, ly, S)
    b.mass(lx - M.LAENGE / 2 * S, ly + 19.5 * S + 30,
           lx + M.LAENGE / 2 * S, ly + 19.5 * S + 30, "28")

    b.txt(56, 640, "Alle Umrisse sind aus der Bauteilgeometrie gerechnet, "
                   "nicht nachgezeichnet.", 12.5, LEISE, 400)
    b.txt(56, 662, "Die Produktfarbe steht als CSS-Variable --produkt im SVG "
                   "und lässt sich je Farbvariante überschreiben.",
          12.5, LEISE, 400)
    b.txt(56, 684, "Silikon Shore A 50–60 · Schnur Paracord 550 Type III, Ø4 mm",
          12.5, LEISE, 400)
    return b.schreibe(datei)


# ----------------------------------------------------------- Blatt zwei ----

def montiert(datei="tuerzwerg-produkt-montiert.svg"):
    S = 2.0
    b = Blatt(900, 1120, "Türzwerg · montiert")
    b.txt(56, 62, "So sitzt es", 30, INK, 700)
    b.txt(56, 88, "Manschette auf dem Drücker, Schnur nach unten, Reif in "
                  "Greifhöhe", 14, LEISE, 400)
    b.linie(56, 112, 844, 112, LINIE, 1.4)

    kx, ky = 300, 250                        # Drueckerachse
    # Tuer und Druecker, Masse aus der Marktuebersicht
    b.o.append(f'<path d="M110 150V1020" stroke="{LINIE}" stroke-width="3" '
               f'fill="none"/>')
    b.txt(118, 172, "Türblatt", 12, LEISE, 400)
    b.o.append(f'<circle cx="{kx - 60}" cy="{ky}" r="26" fill="none" '
               f'stroke="{LEISE}" stroke-width="3"/>')
    b.o.append(f'<path d="M{kx - 60} {ky}h150c18 0 24 8 21 18" fill="none" '
               f'stroke="{LEISE}" stroke-width="17" stroke-linecap="round"/>')
    b.txt(kx + 130, ky - 34, "Drücker Ø20", 12, LEISE, 400)

    # Manschette quer auf dem Druecker
    b.form(manschette_quer(), kx + 46, ky, S * 1.0)
    b.o.append(f'<circle cx="{kx + 46}" cy="{ky}" r="{M.R_INNEN * S:.1f}" '
               f'fill="{LEISE}"/>')
    b.txt(kx + 46, ky - 34, "Manschette", 12.5, INK, 600, "middle")

    # Schnur
    sx = kx + 46
    b.o.append(f'<path d="M{sx} {ky + 19.5 * S}C{sx} {ky + 300} '
               f'{sx - 26} {ky + 360} {sx - 26} {ky + 470}" fill="none" '
               f'stroke="var(--produkt)" stroke-width="{4 * S}" '
               f'stroke-linecap="round"/>')
    b.txt(sx + 18, ky + 330, "Paracord Ø4", 12.5, LEISE, 500)

    # Reif
    rx, ry = sx - 26, ky + 470 + 36 * S
    b.form(reif_kontur(R.aussen) + reif_kontur(R.innen), rx, ry, S)
    b.txt(rx + 36 * S + 16, ry, "Zugring Ø72", 12.5, INK, 600)

    # Hoehen
    b.linie(110, ky, 700, ky, LINIE, 1.0, "6 5")
    b.txt(706, ky + 4, "Klinke, rund 105 cm", 12.5, LEISE, 500)
    b.linie(110, ry, 700, ry, LINIE, 1.0, "6 5")
    b.txt(706, ry + 4, "Reif, rund 75 cm", 12.5, LEISE, 500)
    b.mass(670, ky, 670, ry, "≈ 30 cm")

    b.txt(56, 1046, "Die Schnurlänge bestimmt, wie tief der Reif hängt — "
                    "sie wird beim Knüpfen auf das Kind eingestellt.",
          12.5, LEISE, 400)
    b.txt(56, 1068, "Drückerhöhe nach DIN 18040 rund 105 cm. Ein Zweijähriger "
                    "greift bequem bei 70 bis 80 cm.", 12.5, LEISE, 400)
    return b.schreibe(datei)


if __name__ == "__main__":
    for d in (teile(), montiert()):
        print("geschrieben:", d)
    print(f"  Reif          Ø72 × 14, Öffnung "
          f"{R.oeffnung()[0]:.1f} × {R.oeffnung()[1]:.1f}")
    print(f"  Manschette    Ø24 × 28, Höhe {M.HOEHE:.1f}, Bohrung "
          f"Ø{M.D_INNEN:.0f}")
