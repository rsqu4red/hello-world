#!/usr/bin/env python3
"""Zeichenblatt Zugring Mix: Vorder-, Seiten-, Draufsicht, Schnitte."""

import math

TAU = 2.0 * math.pi
INK, AKZ, SOFT, LIN = "#161A17", "#C7422A", "#5E665E", "#B9C1B7"
GRAU = "#9AA29A"


def zeichne(m, vergleiche, datei="tuerzwerg-zugring-mix-zeichnung.svg",
            titel="Zugring „Mix“", untertitel=None, eigen="Mix"):
    S = 1.85          # Hauptmassstab
    SQ = 3.4          # Schnitte
    W, H = 1420, 1120
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}"><rect width="{W}" height="{H}" '
           f'fill="#F2F4F1"/>']

    def txt(x, y, s, size=13, farbe=INK, w=600, anchor="start"):
        out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans '
                   f'Condensed,DejaVu Sans Condensed,sans-serif" '
                   f'font-size="{size}" font-weight="{w}" fill="{farbe}" '
                   f'text-anchor="{anchor}">{s}</text>')

    def linie(x1, y1, x2, y2, farbe=LIN, br=0.8, strich=None):
        dash = f' stroke-dasharray="{strich}"' if strich else ""
        out.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" '
                   f'stroke="{farbe}" stroke-width="{br}" fill="none"{dash}/>')

    def polar(f, ox, oy, farbe, br, strich=None, n=600):
        d = []
        for i in range(n + 1):
            th = TAU * i / n
            r = f(math.cos(th))
            d.append(("M" if i == 0 else "L")
                     + f"{ox + r*math.sin(th)*S:.2f} {oy - r*math.cos(th)*S:.2f}")
        dash = f' stroke-dasharray="{strich}"' if strich else ""
        out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{farbe}" '
                   f'stroke-width="{br}"{dash}/>')

    def schnitt(ox, oy, a, b, k, farbe=INK, br=2.0, s=SQ):
        k = min(k, a, b)
        out.append(f'<rect x="{ox-a*s:.1f}" y="{oy-b*s:.1f}" '
                   f'width="{2*a*s:.1f}" height="{2*b*s:.1f}" '
                   f'rx="{k*s:.1f}" fill="none" stroke="{farbe}" '
                   f'stroke-width="{br}"/>')

    br_a, ho_a = m.aussenmass()
    ob, oh = m.oeffnung()

    txt(56, 52, "Türzwerg · " + titel, 27, INK, 700)
    txt(56, 78, untertitel or "Silikon Shore A 60–70 · Maße in mm",
        13.5, SOFT, 400)

    # ---------------------------------------------------- 1 Vorderansicht --
    VX, VY = 240, 330
    txt(VX, VY - ho_a / 2 * S - 46, "1  Vorderansicht", 17, INK, 700, "middle")
    linie(VX, VY - ho_a / 2 * S - 26, VX, VY + ho_a / 2 * S + 26, LIN, 0.7, "6 5")
    linie(VX - br_a / 2 * S - 26, VY, VX + br_a / 2 * S + 26, VY, LIN, 0.7, "6 5")
    polar(m.aussen, VX, VY, INK, 2.4)
    polar(m.innen, VX, VY, INK, 2.4)
    # Bandmitte
    polar(lambda c: (m.aussen(c) + m.innen(c)) / 2.0, VX, VY, LIN, 0.9, "4 4")
    # Schnurbohrung und Kammer
    top = m.aussen(1.0)
    ka, ki = top - m.bohr_tiefe, m.innen(1.0) - 1.0
    out.append(f'<rect x="{VX - 2.5*S:.1f}" y="{VY - top*S:.1f}" '
               f'width="{5*S:.1f}" height="{(top-ka)*S:.1f}" fill="none" '
               f'stroke="{AKZ}" stroke-width="1.6"/>')
    out.append(f'<rect x="{VX - m.a_kammer*S:.1f}" y="{VY - ka*S:.1f}" '
               f'width="{2*m.a_kammer*S:.1f}" height="{(ka-ki)*S:.1f}" '
               f'rx="{3*S:.1f}" fill="none" stroke="{AKZ}" stroke-width="1.6"/>')
    linie(VX, VY - top * S, VX, VY - top * S - 34, AKZ, 2.2)

    for lbl, yv in (("A", 1.0), ("B", 0.0), ("C", -1.0)):
        r = (m.aussen(yv if lbl != "B" else 0.0))
        if lbl == "B":
            px, py = VX + m.aussen(0.0) * S + 16, VY
        else:
            px, py = VX + 20, VY - yv * r * S
        txt(px, py + 4, f"{lbl}–{lbl}", 12, AKZ, 700)

    txt(VX, VY + ho_a / 2 * S + 44,
        f"außen {br_a:.0f} × {ho_a:.0f}   ·   Öffnung {ob:.0f} × {oh:.0f}",
        14, INK, 600, "middle")
    txt(VX, VY + ho_a / 2 * S + 64,
        f"Band {m.b_oben:.0f} oben / {m.b_seite:.0f} seitlich / "
        f"{m.b_unten:.0f} unten", 12.5, SOFT, 500, "middle")

    # -------------------------------------------- 2 Seiten- 3 Draufsicht ---
    def projektionsbild(achse, ox, oy, titel, quer_txt):
        lo, hi, bins = m.projektion(achse)
        n = len(bins) - 1
        d = []
        for i in range(n + 1):
            v = lo + (hi - lo) * i / n
            d.append(("M" if i == 0 else "L")
                     + f"{ox + bins[i]*S:.2f} {oy - v*S:.2f}")
        for i in range(n, -1, -1):
            v = lo + (hi - lo) * i / n
            d.append(f"L{ox - bins[i]*S:.2f} {oy - v*S:.2f}")
        out.append(f'<path d="{"".join(d)}Z" fill="none" stroke="{INK}" '
                   f'stroke-width="2.2"/>')
        linie(ox, oy - hi * S - 22, ox, oy - lo * S + 22, LIN, 0.7, "6 5")
        txt(ox, oy - hi * S - 46, titel, 17, INK, 700, "middle")
        txt(ox, oy - lo * S + 44, quer_txt, 12.5, SOFT, 500, "middle")

    projektionsbild("y", 560, 330, "2  Seitenansicht",
                    f"{m.d_oben:.0f} mm oben → {m.d_unten:.1f} mm unten")
    projektionsbild("x", 760, 330, "3  Draufsicht",
                    f"Breite {br_a:.0f} mm")

    # --------------------------------------------------------- 4 Schnitte --
    txt(1010, 148, "4  Querschnitte des Bands", 17, INK, 700)
    txt(1010, 170, "im Maßstab 3,4 : 1 — dieselbe Reihenfolge wie die "
                   "Marken links", 12, SOFT, 400)
    for i, (lbl, c, wo) in enumerate((("A–A", 1.0, "oben, Knotenkammer"),
                                      ("B–B", 0.0, "seitlich"),
                                      ("C–C", -1.0, "unten, Zughand"))):
        sy = 250 + i * 138
        a = m.breite(c) / 2.0
        b = m.dicke(c) / 2.0
        k = m.eckfaktor(c) * min(a, b)
        schnitt(1120, sy, a, b, k, INK, 2.2)
        if c == 1.0:
            schnitt(1120, sy, m.a_kammer, m.b_kammer,
                    0.8 * min(m.a_kammer, m.b_kammer), AKZ, 1.6)
        txt(1010, sy - 26, lbl, 15, AKZ, 700)
        txt(1010, sy - 8, wo, 12, SOFT, 400)
        txt(1010, sy + 14, f"{2*a:.0f} × {2*b:.1f} mm", 13, INK, 600)
        txt(1010, sy + 32, f"Eckradius {k:.1f}", 12, SOFT, 400)

    # ----------------------------------------------------- 5 Ueberlagerung -
    UX, UY = 240, 810
    txt(UX, UY - 120, f"5  {eigen} gegen die Vorentwürfe", 17, INK, 700, "middle")
    palette = [AKZ, SOFT, GRAU, "#7C8A9A", "#A8845C"]
    farben = {n: palette[i % len(palette)]
              for i, (n, _) in enumerate(vergleiche)}
    for name, v in vergleiche:
        polar(v.aussen, UX, UY, farben.get(name, LIN), 1.6, "5 4")
        polar(v.innen, UX, UY, farben.get(name, LIN), 1.6, "5 4")
    polar(m.aussen, UX, UY, INK, 2.6)
    polar(m.innen, UX, UY, INK, 2.6)
    lx = UX + 120
    txt(lx, UY - 40, eigen, 12.5, INK, 700)
    for j, (name, _) in enumerate(vergleiche):
        txt(lx, UY - 20 + j * 19, name, 12.5, farben.get(name, LIN), 600)

    # --------------------------------------------------------- 6 Tabelle ---
    TX, TY = 560, 700
    txt(TX, TY, "6  Zahlen, alle bei Shore A 70", 17, INK, 700)
    spalten = [(eigen, m)] + list(vergleiche)
    schritt = min(140, int(760 / max(1, len(spalten))))
    SPX = [TX + 300 + i * schritt for i in range(len(spalten))]
    zeilen = [
        ("Außen", lambda k: "%.0f × %.0f" % k.aussenmass()),
        ("Öffnung", lambda k: "%.0f × %.0f" % k.oeffnung()),
        ("Band o / s / u", lambda k: "%.0f/%.0f/%.0f"
         % (k.b_oben, k.b_seite, k.b_unten)),
        ("Tiefe oben → unten", lambda k: "%.0f → %.1f" % (k.d_oben, k.d_unten)),
        ("Griff unten", lambda k: "%.0f × %.1f" % (k.b_unten, k.dicke(-1.0))),
        ("Griffumfang", lambda k: "%.0f mm" % k.griffumfang()),
        ("Aufweitung 17 N", lambda k: "%.1f mm" % k.aufweitung(17.0, 70)),
        ("Grenze (10 % auf)", lambda k: "%.0f N" % k.grenzkraft(70)),
    ]
    y = TY + 32
    for i, (name, _) in enumerate(spalten):
        txt(SPX[i], y, name, 12.5,
            INK if i == 0 else farben.get(name, SOFT), 700, "middle")
    for name, f in zeilen:
        y += 30
        txt(TX, y, name, 12.5, SOFT, 500)
        for i, (_, k) in enumerate(spalten):
            txt(SPX[i], y, f(k), 13.5, INK, 700 if i == 0 else 500, "middle")
        linie(TX, y + 8, W - 56, y + 8, LIN, 0.6)

    txt(56, H - 66, "Rot: Schnurbohrung Ø5 und Knotenkammer. "
                    "Gestrichelt in Ansicht 1: die Bandmitte, an der "
                    "gerechnet wird.", 12, SOFT, 400)
    txt(56, H - 46, "Die Seiten- und Draufsicht sind aus dem Körper "
                    "projiziert, nicht konstruiert – deshalb zeigen sie "
                    "die Dickenänderung so, wie sie wirklich verläuft.",
        12, SOFT, 400)
    txt(56, H - 26, "Vier Kinderfinger brauchen rund 44 mm Öffnung · "
                    "Fingerfalle unter 12 mm · Kopffalle ab 95 mm · "
                    "Kleinteilezylinder 31,7 mm.", 12, SOFT, 400)

    out.append("</svg>")
    open(datei, "w").write("\n".join(out))
    print(f"\ngeschrieben: {datei}")
