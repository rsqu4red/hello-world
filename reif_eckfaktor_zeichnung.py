#!/usr/bin/env python3
"""
Türzwerg – was eck_oben und eck_unten am Zugring bedeuten

Ein Blatt, das den Eckfaktor zeigt statt ihn zu beschreiben. Der Faktor ist
keine Laenge, sondern ein Anteil:

    k = eck * min(a, b)

a ist die halbe Bandbreite, b die halbe Banddicke. k = 0 gibt ein Rechteck,
k = min(a, b) - also eck = 1 - gibt ein Stadion, weil der Radius dann die
kuerzere Halbachse ganz ausfuellt. Dazwischen liegt alles andere.

Warum oben und unten verschieden: unten wird gezogen, dort soll gar keine
Kante mehr stehen. Oben sitzt die Knotenkammer, und je groesser der
Eckradius, desto duenner steht das Band an seiner Innenkante - genau dort,
wo die Kammer in die Oeffnung durchbricht.

    python3 reif_eckfaktor_zeichnung.py
"""

import math

from reif_mix import D_SCHNUR
from reif_eh import REV_A_PHI as M, REV_A_RUND, PHI

INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"
GRUND, FLAECHE, GRAU = "#F2F4F1", "#E9ECE7", "#9AA29A"
W, H = 1380, 980
DATEI = "tuerzwerg-zugring-eckfaktor.svg"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" '
       f'fill="{GRUND}"/>']


def txt(x, y, s, size=13, farbe=INK, w=600, anchor="start", mono=False):
    fam = ("IBM Plex Mono,ui-monospace,monospace" if mono else
           "IBM Plex Sans Condensed,DejaVu Sans Condensed,sans-serif")
    out.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def linie(x1, y1, x2, y2, farbe=LIN, br=0.9, strich=None):
    d = f' stroke-dasharray="{strich}"' if strich else ""
    out.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{farbe}" '
               f'stroke-width="{br}" fill="none"{d}/>')


def rundbox(ox, oy, a, b, k, s, farbe=INK, br=2.4, fuell="none"):
    """Querschnitt: a und b sind Halbmasse, k der Eckradius, s der Massstab."""
    k = min(k, a, b)
    out.append(f'<rect x="{ox-a*s:.2f}" y="{oy-b*s:.2f}" width="{2*a*s:.2f}" '
               f'height="{2*b*s:.2f}" rx="{k*s:.2f}" fill="{fuell}" '
               f'stroke="{farbe}" stroke-width="{br}"/>')


def masspfeil(x1, y1, x2, y2, beschriftung, farbe=AKZ, ab=10):
    linie(x1, y1, x2, y2, farbe, 1.3)
    for (px, py), vz in (((x1, y1), 1), ((x2, y2), -1)):
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1
        dx, dy = dx / n * vz, dy / n * vz
        out.append(f'<path d="M{px:.1f} {py:.1f}l{dx*ab-dy*ab*0.28:.1f} '
                   f'{dy*ab+dx*ab*0.28:.1f}M{px:.1f} {py:.1f}'
                   f'l{dx*ab+dy*ab*0.28:.1f} {dy*ab-dx*ab*0.28:.1f}" '
                   f'stroke="{farbe}" stroke-width="1.3" fill="none"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    senkrecht = abs(y2 - y1) > abs(x2 - x1)
    txt(mx + (13 if senkrecht else 0), my + (4 if senkrecht else -8),
        beschriftung, 12.5, farbe, 700, "start" if senkrecht else "middle")


# ------------------------------------------------------------------ Kopf ----

txt(56, 50, "Türzwerg · Zugring · der Eckfaktor", 27, INK, 700)
txt(56, 76, "eck ist keine Länge, sondern ein Anteil an der kürzeren "
            "Halbachse des Querschnitts", 14, SOFT, 400)

out.append(f'<rect x="56" y="98" width="{W-112}" height="52" fill="{FLAECHE}" '
           f'stroke="{LIN}" stroke-width="1"/>')
txt(76, 122, "k  =  eck · min(a, b)", 20, INK, 700, mono=True)
txt(290, 118, "a = halbe Bandbreite     b = halbe Banddicke     "
              "k = Eckradius", 13, SOFT, 500)
txt(290, 138, "eck = 0 → Rechteck        eck = 1 → Stadion, der Radius "
              "füllt die kürzere Halbachse ganz aus", 13, SOFT, 500)

# ------------------------------------------------- 1 Die beiden Schnitte ----

S = 9.0            # Massstab der grossen Schnitte
a_o, b_o = M.b_oben / 2.0, M.d_oben / 2.0
k_o = M.eck_oben * min(a_o, b_o)
a_u, b_u = M.b_unten / 2.0, M.d_unten / 2.0
k_u = M.eck_unten * min(a_u, b_u)

txt(56, 196, "1  Die zwei Stellen, an denen es zählt", 18, INK, 700)
txt(56, 218, "Maßstab 9 : 1 · innen liegt links, zur Öffnung hin",
    12.5, SOFT, 400)

# --- oben ---
OX, OY = 268, 340
txt(OX, 252, "A–A  oben, mit der Knotenkammer", 15, AKZ, 700, "middle")
rundbox(OX, OY, a_o, b_o, k_o, S, INK, 2.6, FLAECHE)
# Kammer und Schnurbohrung
rundbox(OX, OY, M.a_kammer, M.b_kammer, 0.8 * min(M.a_kammer, M.b_kammer),
        S, AKZ, 1.8)
out.append(f'<rect x="{OX-D_SCHNUR/2*S:.1f}" y="{OY-b_o*S:.1f}" '
           f'width="{D_SCHNUR*S:.1f}" height="{(b_o-M.b_kammer)*S:.1f}" '
           f'fill="none" stroke="{AKZ}" stroke-width="1.8"/>')
# Eckradius zeigen
cx, cy = OX - (a_o - k_o) * S, OY - (b_o - k_o) * S
out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{k_o*S:.1f}" fill="none" '
           f'stroke="{AKZ}" stroke-width="1.2" stroke-dasharray="5 4"/>')
out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="{AKZ}"/>')
linie(cx, cy, cx - k_o * S * 0.707, cy - k_o * S * 0.707, AKZ, 1.6)
txt(cx - k_o * S * 0.5 - 8, cy - k_o * S * 0.5 - 8,
    f"k = {k_o:.2f}", 13, AKZ, 700, "end")
# die flache Innenflaeche
linie(OX - a_o * S, OY - (b_o - k_o) * S, OX - a_o * S, OY + (b_o - k_o) * S,
      AKZ, 4.0)
masspfeil(OX - a_o * S - 34, OY - (b_o - k_o) * S,
          OX - a_o * S - 34, OY + (b_o - k_o) * S,
          f"{2*(b_o-k_o):.2f}")
txt(OX - a_o * S - 40, OY + (b_o - k_o) * S + 26,
    "flache Innenfläche", 12, AKZ, 600, "middle")
txt(OX - a_o * S - 40, OY + (b_o - k_o) * S + 42,
    "hier bricht die Kammer durch", 11, SOFT, 400, "middle")
masspfeil(OX - a_o * S, OY + b_o * S + 30, OX + a_o * S, OY + b_o * S + 30,
          f"{M.b_oben:.1f}")
masspfeil(OX + a_o * S + 30, OY - b_o * S, OX + a_o * S + 30, OY + b_o * S,
          f"{M.d_oben:.1f}")
txt(OX, OY + b_o * S + 76, f"eck_oben = 1/φ = {M.eck_oben:.3f}",
    14, INK, 700, "middle")

# --- unten ---
UX, UY = 800, 340
txt(UX, 252, "C–C  unten, die Zugstelle", 15, AKZ, 700, "middle")
rundbox(UX, UY, a_u, b_u, k_u, S, INK, 2.6, FLAECHE)
cx2, cy2 = UX - (a_u - k_u) * S, UY - (b_u - k_u) * S
out.append(f'<circle cx="{cx2:.1f}" cy="{cy2:.1f}" r="{k_u*S:.1f}" fill="none" '
           f'stroke="{AKZ}" stroke-width="1.2" stroke-dasharray="5 4"/>')
out.append(f'<circle cx="{cx2:.1f}" cy="{cy2:.1f}" r="2.6" fill="{AKZ}"/>')
linie(cx2, cy2, cx2 - k_u * S * 0.707, cy2 - k_u * S * 0.707, AKZ, 1.6)
txt(cx2 - k_u * S * 0.5 - 8, cy2 - k_u * S * 0.5 - 8,
    f"k = {k_u:.2f}", 13, AKZ, 700, "end")
masspfeil(UX - a_u * S, UY + b_u * S + 30, UX + a_u * S, UY + b_u * S + 30,
          f"{M.b_unten:.1f}")
masspfeil(UX + a_u * S + 30, UY - b_u * S, UX + a_u * S + 30, UY + b_u * S,
          f"{M.d_unten:.1f}")
txt(UX, UY + b_u * S + 76, f"eck_unten = 1,000   ·   Stadion",
    14, INK, 700, "middle")
txt(UX, UY + b_u * S + 96, "kein gerades Stück mehr in der Höhe",
    12, SOFT, 400, "middle")

txt(1090, 262, "Warum verschieden", 15, INK, 700)
for i, z in enumerate([
        "Unten wird gezogen. Dort soll",
        "keine Kante mehr stehen, an der",
        "der Finger abknickt — also eck = 1.",
        "",
        "Oben sitzt die Knotenkammer. Je",
        "größer der Eckradius, desto dünner",
        "steht das Band an seiner Innen-",
        "kante — und genau dort bricht die",
        "Kammer in die Öffnung durch.",
        "Deshalb oben kleiner."]):
    txt(1090, 288 + i * 19, z, 12.5, SOFT, 400)

# ----------------------------------------------- 2 Reihe der Eckfaktoren ----

txt(56, 560, "2  Derselbe obere Querschnitt bei verschiedenen Eckfaktoren",
    18, INK, 700)
txt(56, 582, f"19,0 × 14,0 mm · Maßstab 5 : 1 · rot die flache Innenfläche, "
             f"die der Knotenkammer bleibt", 12.5, SOFT, 400)

S2 = 5.0
REIHE = [(0.143, "0,143", "Rev. A, wie er war\n1 mm Kante"),
         (1.0 / PHI, "0,618", "Rev. A φ\n1/φ — jetzt"),
         (0.72, "0,720", "Rev. A rund, Rev. H\nvorher"),
         (1.0, "1,000", "Stadion\nwie unten")]
for i, (eck, lab, note) in enumerate(REIHE):
    x = 190 + i * 300
    y = 690
    k = eck * min(a_o, b_o)
    rundbox(x, y, a_o, b_o, k, S2, INK, 2.4, FLAECHE)
    linie(x - a_o * S2, y - (b_o - k) * S2, x - a_o * S2, y + (b_o - k) * S2,
          AKZ, 4.5)
    txt(x, y + b_o * S2 + 32, f"eck = {lab}", 15, INK, 700, "middle")
    txt(x, y + b_o * S2 + 52, f"k = {k:.2f} mm", 13, AKZ, 600, "middle")
    txt(x, y + b_o * S2 + 72, f"flach innen {2*(b_o-k):.2f} mm",
        12.5, SOFT, 500, "middle")
    for j, z in enumerate(note.split("\n")):
        txt(x, y + b_o * S2 + 94 + j * 16, z, 11.5, GRAU, 400, "middle")

# ------------------------------------------------------------- Fusszeile ----

linie(56, H - 92, W - 56, H - 92, LIN, 0.8)
txt(56, H - 66, f"Rev. A φ: oben {M.b_oben:.1f} × {M.d_oben:.1f} mit "
                f"k = {k_o:.2f} · unten {M.b_unten:.1f} × {M.d_unten:.1f} mit "
                f"k = {k_u:.2f} · beide Radien stehen zueinander im "
                f"Verhältnis {k_u/k_o:.4f} = φ.", 12.5, SOFT, 400)
txt(56, H - 46, f"Die Schnurbohrung ist jetzt Ø{D_SCHNUR:.0f} statt Ø5 — "
                f"gleich dem Durchmesser von Paracord 550 Type III. Die "
                f"Knotenkammer bleibt {2*M.a_kammer:.0f} × {2*M.b_kammer:.1f}.",
    12.5, SOFT, 400)
txt(56, H - 26, "eck ist ein Anteil, keine Länge: ändert sich die Banddicke, "
                "ändert sich der Radius mit. Deshalb steht in der Tabelle "
                "immer beides — der Faktor und der Radius in Millimetern.",
    12.5, SOFT, 400)

out.append("</svg>")
open(DATEI, "w", encoding="utf-8").write("\n".join(out))

print(f"Rev. A phi")
print(f"  oben    {M.b_oben:.1f} x {M.d_oben:.1f}   a = {a_o:.2f}  b = {b_o:.2f}"
      f"   eck = {M.eck_oben:.4f}   k = {k_o:.3f}")
print(f"  unten   {M.b_unten:.1f} x {M.d_unten:.1f}   a = {a_u:.2f}  b = {b_u:.2f}"
      f"   eck = {M.eck_unten:.4f}   k = {k_u:.3f}")
print(f"  k unten : k oben = {k_u/k_o:.4f}   phi = {PHI:.4f}")
print(f"  flache Innenflaeche oben {2*(b_o-k_o):.2f} mm "
      f"(bei eck 0,72 waeren es {2*(b_o-0.72*min(a_o,b_o)):.2f})")
print(f"  Schnurbohrung Ø{D_SCHNUR:.1f}")
print(f"\ngeschrieben: {DATEI}")
