#!/usr/bin/env python3
"""
Türzwerg – Zugring: Tropfen w = 2, Kreis und Rev. E im direkten Vergleich

Drei Silhouetten nebeneinander, darunter der Griffquerschnitt im selben
Massstab, und alle drei noch einmal uebereinandergelegt. Die Ueberlagerung
ist zum Beurteilen das Ehrlichste - nebeneinander taeuscht die Groesse.

Alle drei in Shore A 70 und 11 mm Dicke. Damit ist als Unterschied nur
noch die Kontur uebrig - Bandbreite, Radius, Verlauf. Zum Einordnen
steht Rev. E zusaetzlich an seinem Auslegungspunkt A 80 in der Tabelle.

    python3 reif_dreier.py
"""

import math
from reif_uebersicht2 import Kontur, kreis, kosinusband

TAU = 2.0 * math.pi


def tropfen(r0, e, w):
    def f(th):
        s = math.sin(th)
        return r0 - e * math.cos(th) + w * s * s
    return f


def band_von(aussen, bo, bs, bu):
    a0 = (bo + 2 * bs + bu) / 4.0
    a1 = (bo - bu) / 2.0
    a2 = (bo - 2 * bs + bu) / 4.0
    def f(th):
        c = math.cos(th)
        return aussen(th) - (a0 + a1 * c + a2 * (2 * c * c - 1))
    return f


def pappus(k, n=720):
    """Volumen nach Guldin: Querschnittsflaeche mal Schwerpunktweg."""
    v = 0.0
    for i in range(n):
        th = TAU * i / n
        b, t = k.breite(th), k.dicke
        r_m = (k.aussen(th) + k.innen(th)) / 2.0
        ecke = min(b / 2.0, t / 2.0) * 0.85
        flaeche = b * t - (4.0 - math.pi) * ecke * ecke
        v += flaeche * r_m * (TAU / n)
    return v


A_TROPFEN = tropfen(40.0, 4.5, 2.0)
A_KREIS = kreis(40.0)
A_REVE = kreis(43.0)

# Alle drei in Shore A 70 und 11 mm Dicke - damit bleibt als Unterschied
# nur noch die Kontur, und die Zahlen sind unmittelbar vergleichbar.
DICKE, SHORE = 11.0, 70

TROPFEN = Kontur("tropfen", "Tropfen w = 2", A_TROPFEN,
                 band_von(A_TROPFEN, 21, 16, 18), DICKE, SHORE,
                 "Oben schmal, unten breit, Flanken leicht geweitet.")
KREIS = Kontur("kreis", "Kreis", A_KREIS,
               band_von(A_KREIS, 21, 16, 18), DICKE, SHORE,
               "Außen exakter Kreis, Band nach innen unterschiedlich.")
REV_E = Kontur("reve", "Rev. E", A_REVE,
               band_von(A_REVE, 23, 11, 15), DICKE, SHORE,
               "Der bestehende. Form ist gebaut.")
# Zum Einordnen: Rev. E an seinem Auslegungspunkt.
REV_E80 = Kontur("reve80", "Rev. E in A 80", A_REVE,
                 band_von(A_REVE, 23, 11, 15), DICKE, 80, "")

DREI = [TROPFEN, KREIS, REV_E]

# ---------------------------------------------------------------- Blatt -----

S = 1.95
W, H = 1240, 940
INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"
GRAU = "#9AA29A"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=14, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def pfad(f, ox, oy, farbe, br, strich=None, n=600):
    d = []
    for i in range(n + 1):
        th = TAU * i / n
        r = f(th)
        d.append(("M" if i == 0 else "L")
                 + f"{ox + r*math.sin(th)*S:.2f} {oy - r*math.cos(th)*S:.2f}")
    dash = f' stroke-dasharray="{strich}"' if strich else ""
    out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{farbe}" '
               f'stroke-width="{br}"{dash}/>')


txt(52, 50, "Türzwerg · Zugring · Tropfen w = 2, Kreis, Rev. E", 26, INK, 700)
txt(52, 76, "Alle in Shore A 70 · alle 11 mm dick · gleicher Maßstab — "
            "der einzige Unterschied ist die Kontur", 13, SOFT, 400)

FARBEN = {"tropfen": AKZ, "kreis": INK, "reve": GRAU}
X = [230, 620, 1010]
OY = 285

for ox, k in zip(X, DREI):
    f = FARBEN[k.name]
    pfad(k.aussen, ox, OY, f, 2.4)
    pfad(k.innen, ox, OY, f, 2.4)
    top = k.aussen(0.0)
    out.append(f'<path d="M{ox} {OY - top*S:.1f}L{ox} {OY - top*S - 30:.1f}" '
               f'stroke="{AKZ}" stroke-width="2.2"/>')
    out.append(f'<circle cx="{ox}" cy="{OY - (k.innen(0.0)+4)*S:.1f}" r="6" '
               f'fill="none" stroke="{AKZ}" stroke-width="1.5"/>')

    ab, ah = k.aussenmass()
    y = OY + ah / 2 * S + 36
    txt(ox, y, k.titel, 20, f, 700, "middle")

    # Griffquerschnitt unten, im selben Massstab
    bu = k.breite(math.pi)
    t = k.dicke
    ecke = min(bu, t) / 2.0 * 0.85
    qx, qy = ox, y + 44
    out.append(f'<rect x="{qx - bu/2*S:.1f}" y="{qy - t/2*S:.1f}" '
               f'width="{bu*S:.1f}" height="{t*S:.1f}" rx="{ecke*S:.1f}" '
               f'fill="none" stroke="{f}" stroke-width="2.0"/>')
    txt(ox, qy + t / 2 * S + 20, f"Griff {bu:.0f} × {t:.0f} mm",
        13, INK, 600, "middle")
    txt(ox, qy + t / 2 * S + 38, f"Umfang {math.pi*(3*(bu/2+t/2) - math.sqrt((3*bu/2+t/2)*(bu/2+3*t/2))):.0f} mm",
        12, SOFT, 400, "middle")

# ------------------------------------------------------------ Ueberlagerung -

UX, UY = 230, 700
txt(UX, UY - 118, "Übereinandergelegt", 18, INK, 700, "middle")
for k in DREI:
    f = FARBEN[k.name]
    pfad(k.aussen, UX, UY, f, 2.2, "5 4" if k.name == "reve" else None)
    pfad(k.innen, UX, UY, f, 2.2, "5 4" if k.name == "reve" else None)

# --------------------------------------------------------------- Tabelle ----

TX, TY = 470, 610
zeilen = [
    ("", "Tropfen w = 2", "Kreis", "Rev. E"),
    ("Außen", None, None, None),
    ("Öffnung", None, None, None),
    ("Band oben / seitl. / unten", None, None, None),
    ("Griff unten", None, None, None),
    ("Silikon (geschätzt)", None, None, None),
    ("Shore", None, None, None),
    ("Aufweitung bei 17 N", None, None, None),
    ("Grenze (10 % auf)", None, None, None),
]


def werte(k):
    ab, ah = k.aussenmass()
    ob, oh = k.oeffnung()
    bo, bs, bu = k.bandmasse()
    return [f"{ab:.0f} × {ah:.0f} × {k.dicke:.0f}",
            f"{ob:.0f} × {oh:.0f}",
            f"{bo:.0f} / {bs:.0f} / {bu:.0f}",
            f"{bu:.0f} × {k.dicke:.0f}",
            f"{pappus(k)/1000*1.15:.0f} g",
            f"A {k.shore}",
            f"{k.aufweitung(17.0):.1f} mm",
            f"{k.grenzkraft():.0f} N"]


spalten = [werte(k) for k in DREI]
SPX = [TX + 250, TX + 400, TX + 550]

txt(TX, TY, "Zahlen", 18, INK, 700)
y = TY + 30
for i, k in enumerate(DREI):
    txt(SPX[i], y, k.titel, 13, FARBEN[k.name], 700, "middle")
y += 8
for j, name in enumerate([z[0] for z in zeilen[1:]]):
    y += 30
    txt(TX, y, name, 13, SOFT, 500)
    for i in range(3):
        txt(SPX[i], y, spalten[i][j], 14, INK, 600, "middle")
    out.append(f'<path d="M{TX} {y+8}L{W-52} {y+8}" stroke="{LIN}" '
               f'stroke-width="0.6"/>')

y += 34
txt(TX, y, "Rev. E an seinem Auslegungspunkt A 80", 13, AKZ, 600)
txt(SPX[2], y, f"{REV_E80.aufweitung(17.0):.1f} mm · "
               f"{REV_E80.grenzkraft():.0f} N", 14, AKZ, 700, "middle")

txt(52, H - 44, "Rev. E gestrichelt in der Überlagerung. Er ist der größte "
                "und zugleich der weichste – Band seitlich nur 11 mm, "
                "Radius 43 mm, beides geht mit der dritten Potenz ein.",
    12, SOFT, 400)
txt(52, H - 24, "Die Griffquerschnitte sind im selben Maßstab wie die "
                "Silhouetten gezeichnet. Bei gleicher Tiefe unterscheiden "
                "sie sich nur noch in der Breite: 18 gegen 15 mm.",
    12, SOFT, 400)

out.append("</svg>")
open("tuerzwerg-zugring-dreier.svg", "w").write("\n".join(out))

kopf = ["Entwurf", "aussen", "Oeffnung", "Band", "Griff", "g", "Shore",
        "17 N", "Grenze"]
print(f"{kopf[0]:<16}{kopf[1]:>14}{kopf[2]:>10}{kopf[3]:>13}{kopf[4]:>9}"
      f"{kopf[5]:>6}{kopf[6]:>7}{kopf[7]:>8}{kopf[8]:>9}")
for k in DREI + [REV_E80]:
    v = werte(k)
    print(f"{k.titel:<16}{v[0]:>14}{v[1]:>10}{v[2]:>13}{v[3]:>9}"
          f"{v[4]:>6}{v[5]:>7}{v[6]:>8}{v[7]:>9}")
print("\ngeschrieben: tuerzwerg-zugring-dreier.svg")
