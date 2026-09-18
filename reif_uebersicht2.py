#!/usr/bin/env python3
"""
Türzwerg – Zugring, zweite Uebersicht: Varianten der Oeffnung

Die erste Uebersicht hat an den Massen gedreht - Durchmesser, Bandbreite,
Dicke. Dieses Blatt laesst den Aussenkreis fest und veraendert, was
innen passiert. Das ist der groessere Hebel fuer das Aussehen, und bei
zweien davon auch fuer die Funktion.

Wieder nur Kontur und Kennzahl, kein Netz.

    python3 reif_uebersicht2.py
"""

import math
from reif_alt import e_modul, D_FINGER, ZYLINDER, KOPF

TAU = 2.0 * math.pi


class Kontur:
    """Ein Ring, beschrieben durch Aussen- und Innenkontur ueber theta.

    theta = 0 ist oben. Beide Konturen sind Radien vom Mittelpunkt aus.
    """

    def __init__(self, name, titel, aussen, innen, dicke, shore, notiz,
                 steg=None, oese=None, steif=1.0):
        self.name, self.titel, self.notiz = name, titel, notiz
        self.aussen, self.innen = aussen, innen
        self.dicke, self.shore = dicke, shore
        self.steg, self.oese = steg, oese
        self.steif = steif          # Faktor fuer Verstrebungen

    def breite(self, th):
        return self.aussen(th) - self.innen(th)

    def mittelradius(self, n=720):
        return sum((self.aussen(TAU * i / n) + self.innen(TAU * i / n)) / 2.0
                   for i in range(n)) / n

    def oeffnung(self, n=1440):
        breit = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            breit = max(breit, 2.0 * self.innen(th) * math.sin(th))
        return breit, self.innen(0.0) + self.innen(math.pi)

    def aussenmass(self, n=1440):
        breit = 0.0
        for i in range(n + 1):
            th = math.pi * i / n
            breit = max(breit, 2.0 * self.aussen(th) * math.sin(th))
        return breit, self.aussen(0.0) + self.aussen(math.pi)

    def aufweitung(self, kraft, n=720):
        e = e_modul(self.shore)
        r = self.mittelradius()
        za = ne = 0.0
        for i in range(n):
            th = TAU * i / n
            w = (math.cos(th) / 2.0 - 1.0 / math.pi) ** 2
            b = self.breite(th)
            za += w / (self.dicke * b ** 3 / 12.0)
            ne += w
        return 0.149 * kraft * r ** 3 / (e * (ne / za)) / self.steif

    def grenzkraft(self, anteil=0.10):
        return anteil * self.aussenmass()[1] / self.aufweitung(1.0)

    def bandmasse(self):
        """Band oben / seitlich / unten."""
        return (self.breite(0.0), self.breite(math.pi / 2), self.breite(math.pi))


# ------------------------------------------------------------- Konturen -----

def kreis(r):
    return lambda th: r


def kosinusband(r_a, bo, bs, bu):
    a0 = (bo + 2 * bs + bu) / 4.0
    a1 = (bo - bu) / 2.0
    a2 = (bo - 2 * bs + bu) / 4.0
    def f(th):
        c = math.cos(th)
        return r_a - (a0 + a1 * c + a2 * (2 * c * c - 1))
    return f


def exzenter(ri, e):
    """Innenkreis vom Radius ri, um e nach unten versetzt."""
    def f(th):
        c = math.cos(th)
        return -e * c + math.sqrt(max(0.0, ri * ri - e * e * (1 - c * c)))
    return f


def flachboden(ri, h):
    """Innenkreis ri, unten von der Geraden y = -h gekappt."""
    def f(th):
        c = math.cos(th)
        return min(ri, -h / c) if c < -1e-9 else ri
    return f


# ------------------------------------------------------------- Entwuerfe ----

R = 40.0

ENTWUERFE = [
    Kontur("kreis", "Kreis", kreis(R), kosinusband(R, 21, 16, 18), 15.0, 60,
           "Aus der letzten Runde. Der Vergleichspunkt."),
    Kontur("gleich", "Gleichband", kreis(R), kreis(R - 18), 15.0, 60,
           "Band überall 18 mm. Zwei konzentrische Kreise."),
    Kontur("exzenter", "Exzenter", kreis(R), exzenter(22.0, 3.0), 15.0, 60,
           "Öffnung ein echter Kreis, 3 mm nach unten versetzt. "
           "Zwei reine Kreise, nur nicht konzentrisch."),
    Kontur("flach", "Flachboden", kreis(R), flachboden(23.0, 22.0), 15.0, 60,
           "Runde Öffnung, unten gerade gekappt. Die Finger liegen "
           "auf einer Geraden statt in einer Rundung."),
    Kontur("steg", "Steg", kreis(R), kreis(R - 17), 15.0, 60,
           "Querstange durch die Öffnung. Das Kind greift eine Stange "
           "statt in ein Loch – deutlich mehr Zugkraft.",
           steg=(11.0, 0.0), steif=3.2),
    Kontur("oese", "Öse", kreis(R), kreis(R - 17), 15.0, 60,
           "Knoten sitzt in einem Lappen oben. Das Band braucht deshalb "
           "keine dicke Stelle mehr und läuft ganz gleichmäßig.",
           oese=(9.0, 13.0)),
    Kontur("gross", "Gleichband groß", kreis(45.0), kreis(45.0 - 18), 15.0, 60,
           "Wie Gleichband, aber Ø90. Ganze Hand geht durch."),
    Kontur("duenn", "Flachring", kreis(R), kreis(R - 18), 10.0, 60,
           "Gleichband, nur 10 mm statt 15 mm tief. Liegt flach "
           "an der Tür an."),
]

# --------------------------------------------------------------- Zeichnung --

S = 1.62
W, H = 1280, 1010
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


txt(52, 52, "Türzwerg · Zugring · was mit der Öffnung passiert", 26, INK, 700)
txt(52, 78, "Außenkontur bei allen ein exakter Kreis · gleicher Maßstab · "
            "Shore A 60 · Aufweitung bei 17 N", 13, SOFT, 400)

SP, BREIT, HOCH = 4, 306, 330
X0, Y0 = 208, 250

for i, k in enumerate(ENTWUERFE):
    ox = X0 + (i % SP) * BREIT
    oy = Y0 + (i // SP) * HOCH

    pfad(k.aussen, ox, oy, INK, 2.2)
    pfad(k.innen, ox, oy, INK, 2.2)

    if k.steg:
        hb, ym = k.steg
        ri = k.innen(math.pi / 2)
        out.append(f'<rect x="{ox - ri*S:.1f}" y="{oy - hb/2*S:.1f}" '
                   f'width="{2*ri*S:.1f}" height="{hb*S:.1f}" rx="{hb/2*S:.1f}" '
                   f'fill="none" stroke="{INK}" stroke-width="2.2"/>')

    if k.oese:
        ob, oh = k.oese
        top = k.aussen(0.0)
        out.append(f'<rect x="{ox - ob/2*S:.1f}" y="{oy - (top+oh-4)*S:.1f}" '
                   f'width="{ob*S:.1f}" height="{(oh+6)*S:.1f}" '
                   f'rx="{ob/2*S:.1f}" fill="none" stroke="{INK}" '
                   f'stroke-width="2.2"/>')
        out.append(f'<circle cx="{ox}" cy="{oy - (top+oh-6)*S:.1f}" r="{2.5*S:.1f}" '
                   f'fill="none" stroke="{AKZ}" stroke-width="1.6"/>')

    top = k.aussen(0.0) + (k.oese[1] if k.oese else 0.0)
    out.append(f'<path d="M{ox} {oy - top*S - 4:.1f}'
               f'L{ox} {oy - top*S - 32:.1f}" stroke="{AKZ}" stroke-width="2.2"/>')
    if not k.oese:
        out.append(f'<circle cx="{ox}" cy="{oy - (k.innen(0.0)+4)*S:.1f}" '
                   f'r="5.5" fill="none" stroke="{AKZ}" stroke-width="1.6"/>')

    ab, ah = k.aussenmass()
    ob_, oh_ = k.oeffnung()
    bo, bs, bu = k.bandmasse()
    d17 = k.aufweitung(17.0)

    y = oy + ah / 2 * S + 40
    txt(ox, y, k.titel, 19, INK, 700, "middle")
    txt(ox, y + 42, f"Ø{ab:.0f} × {k.dicke:.0f}   Öffnung {ob_:.0f} × {oh_:.0f}",
        13, INK, 600, "middle")
    txt(ox, y + 60, f"Band {bo:.0f} / {bs:.0f} / {bu:.0f}", 12, SOFT, 500, "middle")
    stern = "*" if k.steif != 1.0 else ""
    txt(ox, y + 80, f"{d17:.1f} mm auf{stern} · Grenze {k.grenzkraft():.0f} N{stern}",
        12.5, INK, 600, "middle")
    # Notiz umbrechen
    worte, zeile, zeilen = k.notiz.split(), "", []
    for wort in worte:
        if len(zeile) + len(wort) > 34:
            zeilen.append(zeile); zeile = wort
        else:
            zeile = (zeile + " " + wort).strip()
    zeilen.append(zeile)
    for j, zl in enumerate(zeilen):
        txt(ox, y + 100 + j * 15, zl, 11.5, SOFT, 400, "middle")

txt(52, H - 66, "* Der Steg verstrebt den Ring. Die Ringformel gilt dafür "
                "nicht mehr; der Faktor 3,2 ist geschätzt, nicht gerechnet – "
                "er wäre nachzurechnen, wenn die Variante weiterkommt.",
    12, SOFT, 400)
txt(52, H - 46, "„Grenze“ = Kraft, ab der sich der Ring um mehr als ein "
                "Zehntel seiner Höhe aufzieht.", 12, SOFT, 400)
txt(52, H - 26, "Vier Kinderfinger brauchen rund 44 mm Öffnung · "
                "Fingerfalle unter 12 mm · Kopffalle ab 95 mm · "
                "Kleinteilezylinder 31,7 mm.", 12, SOFT, 400)

out.append("</svg>")
open("tuerzwerg-zugring-uebersicht2.svg", "w").write("\n".join(out))

print(f"{'Entwurf':<17}{'aussen':>8}{'Oeffnung':>12}{'Band o/s/u':>14}"
      f"{'17 N':>8}{'Grenze':>9}")
for k in ENTWUERFE:
    ab, ah = k.aussenmass()
    ob_, oh_ = k.oeffnung()
    bo, bs, bu = k.bandmasse()
    print(f"{k.titel:<17}{ab:>7.0f} {f'{ob_:.0f} x {oh_:.0f}':>11} "
          f"{f'{bo:.0f}/{bs:.0f}/{bu:.0f}':>13}{k.aufweitung(17.0):>7.1f} "
          f"{k.grenzkraft():>6.0f} N")
print("\ngeschrieben: tuerzwerg-zugring-uebersicht2.svg")
