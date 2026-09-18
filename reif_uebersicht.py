#!/usr/bin/env python3
"""
Türzwerg – Uebersichtsblatt Zugringe

Nur Kontur und Kennzahlen, kein Netz. Das Blatt dient dem groben
Vergleich; gerechnet wird zweidimensional, also in Sekunden statt in
Minuten.

Verglichen werden sieben Ringe:

  Rev. E    der bestehende, fuer den die Form schon existiert (A 80)
  Kreis     der Entwurf aus der letzten Runde
  + fuenf Abwandlungen davon, alle mit exakt kreisfoermiger Aussenkontur

    python3 reif_uebersicht.py
"""

import math
from reif_alt import Zugring, kreis, e_modul, D_FINGER, ZYLINDER, KOPF

# ------------------------------------------------------------- Entwuerfe ----
# (Schluessel, Titel, Radius, Band oben/seitlich/unten, Dicke, Haerte, Notiz)

ENTWUERFE = [
    ("rev_e", "Rev. E", 43.0, 23.0, 11.0, 15.0, 11.0, 80,
     "Der bestehende. Form ist gebaut."),
    ("kreis", "Kreis", 40.0, 21.0, 16.0, 18.0, 15.0, 60,
     "Aus der letzten Runde."),
    ("gleich", "Gleichband", 40.0, 18.0, 18.0, 18.0, 15.0, 60,
     "Band ueberall gleich breit: zwei Kreise, sonst nichts."),
    ("leicht", "Leicht", 40.0, 20.0, 13.0, 15.0, 15.0, 60,
     "Schmaleres Band, groessere Oeffnung. Wirkt luftiger."),
    ("kompakt", "Kompakt", 36.0, 19.0, 15.0, 17.0, 16.0, 60,
     "Kleiner und steifer. Passt in kleinere Haende."),
    ("gross", "Gross", 45.0, 23.0, 18.0, 20.0, 15.0, 60,
     "Mehr Platz fuer die ganze Hand, dafuer breiteres Band."),
    ("rund", "Rundprofil", 40.0, 19.0, 14.0, 16.0, 19.0, 60,
     "Dickeres, rundes Band - fasst sich an wie ein Seil."),
]


def ring(r_a, bo, bs, bu, d):
    return Zugring("x", "x", "x.stl", dicke=d, b_oben=bo, b_seite=bs,
                   b_unten=bu, kontur=kreis(r_a), notiz="")


# ------------------------------------------------------------------- SVG ----

S = 1.75
W, H = 1240, 980
INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"
GRAU = "#8A928A"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>']


def txt(x, y, s, size=14, farbe=INK, w=600, anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')


def kontur(f, ox, oy, farbe, br, strich=None, n=540):
    d = []
    for i in range(n + 1):
        th = 2.0 * math.pi * i / n
        r = f(math.cos(th))
        d.append(("M" if i == 0 else "L")
                 + f"{ox + r*math.sin(th)*S:.2f} {oy - r*math.cos(th)*S:.2f}")
    dash = f' stroke-dasharray="{strich}"' if strich else ""
    out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{farbe}" '
               f'stroke-width="{br}"{dash}/>')


txt(56, 54, "Türzwerg · Zugring · sieben Konturen im Vergleich", 26, INK, 700)
txt(56, 80, "Alle Außenkonturen exakt kreisförmig · gleicher Maßstab · "
            "Aufweitung bei 17 N (Tür öffnen)", 13, SOFT, 400)

# Vergleichskreis Rev. E als blasse Referenz in jedem Feld
ref = ring(43.0, 23.0, 11.0, 15.0, 11.0)

SPALTEN = 4
BREIT, HOCH = 292, 300
X0, Y0 = 200, 250

for i, (key, titel, r_a, bo, bs, bu, d, shore, notiz) in enumerate(ENTWUERFE):
    r = ring(r_a, bo, bs, bu, d)
    ox = X0 + (i % SPALTEN) * BREIT
    oy = Y0 + (i // SPALTEN) * HOCH

    # blasse Referenzkontur Rev. E
    if key != "rev_e":
        kontur(ref.aussen, ox, oy, LIN, 1.0, "3 4")

    kontur(r.aussen, ox, oy, INK, 2.2)
    kontur(r.innen, ox, oy, INK, 2.2)

    # Schnur
    top = r.aussen(1.0)
    out.append(f'<path d="M{ox} {oy - top*S:.1f}L{ox} {oy - top*S - 34:.1f}" '
               f'stroke="{AKZ}" stroke-width="2.2"/>')
    out.append(f'<circle cx="{ox}" cy="{oy - (r.innen(1.0)+4)*S:.1f}" r="5.5" '
               f'fill="none" stroke="{AKZ}" stroke-width="1.6"/>')

    ab, ah = r.aussenmass()
    ob, oh = r.oeffnung()
    dehn, _ = r.aufweitung(17.0, shore)
    grenz = r.grenzkraft(shore)

    y = oy + ah / 2 * S + 34
    marke = "  ← Form vorhanden" if key == "rev_e" else ""
    txt(ox, y, titel + marke, 19, AKZ if key == "rev_e" else INK, 700, "middle")
    txt(ox, y + 20, notiz, 11.5, SOFT, 400, "middle")
    txt(ox, y + 42, f"Ø{ab:.0f} × {d:.0f}   Öffnung Ø{ob:.0f}",
        13, INK, 600, "middle")
    txt(ox, y + 60, f"Band {bo:.0f} / {bs:.0f} / {bu:.0f}   "
                    f"Griff {bu:.0f}×{d:.0f}", 12, SOFT, 500, "middle")
    txt(ox, y + 80, f"A{shore}: {dehn:.1f} mm auf · Grenze {grenz:.0f} N",
        12.5, INK, 600, "middle")

txt(56, H - 96, "Gestrichelt in jedem Feld: die Außenkontur von Rev. E "
                "zum Größenvergleich.", 12, SOFT, 400)
txt(56, H - 76, "„Grenze“ = Kraft, ab der sich der Ring um mehr als ein "
                "Zehntel seiner Höhe aufzieht. Darüber rutscht die Hand "
                "leicht heraus.", 12, SOFT, 400)
txt(56, H - 56, "Rev. E ist in Shore A 80 gerechnet, alle anderen in A 60 – "
                "deshalb ist sein schmales 11-mm-Band dort zulässig und "
                "hier nicht.", 12, SOFT, 400)
txt(56, H - 36, "Vier Kinderfinger brauchen rund 44 mm Öffnung. "
                "Fingerfalle unter 12 mm, Kopffalle ab 95 mm, "
                "Kleinteilezylinder 31,7 mm.", 12, SOFT, 400)

out.append("</svg>")
open("tuerzwerg-zugring-uebersicht.svg", "w").write("\n".join(out))

# ------------------------------------------------------------- Konsole ------

print(f"{'Entwurf':<12}{'aussen':>8}{'Oeffn':>8}{'Band':>14}"
      f"{'Griff':>9}{'Shore':>7}{'17 N':>9}{'Grenze':>9}{'Finger':>8}")
for key, titel, r_a, bo, bs, bu, d, shore, notiz in ENTWUERFE:
    r = ring(r_a, bo, bs, bu, d)
    ab, ah = r.aussenmass()
    ob, oh = r.oeffnung()
    dehn, _ = r.aufweitung(17.0, shore)
    print(f"{titel:<12}{ab:>7.0f} {ob:>7.0f} "
          f"{f'{bo:.0f}/{bs:.0f}/{bu:.0f}':>14}{f'{bu:.0f}x{d:.0f}':>9}"
          f"{shore:>7}{dehn:>8.1f} {r.grenzkraft(shore):>7.0f} N"
          f"{ob/D_FINGER:>7.1f}")
print("\ngeschrieben: tuerzwerg-zugring-uebersicht.svg")
