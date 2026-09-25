#!/usr/bin/env python3
"""
Türzwerg – sechs Wege, die Schnur an der Manschette zu befestigen

Ein Blatt mit Prinzipskizzen, keine Konstruktion. Alle sechs sind
Querschnitte durch den Tuerdruecker, im selben Massstab, damit sie
vergleichbar sind.

Die Frage dahinter ist nicht "wie bekomme ich den Kern heraus", sondern
eine Ebene darueber: muss der Knoten ueberhaupt in der Manschette
sitzen? Vier der sechs Entwuerfe sagen nein - und haben das
Werkzeugproblem dann gar nicht erst.

    python3 manschette_ideen.py
"""

import math

TINTE = "#17160F"
LEISE = "#6C675A"
LINIE = "#C9C4B6"
DRUECKER = "#E6E2D8"
SILIKON = "#B9C8BE"
SCHNUR = "#55886B"
ZWEITES = "#E0982F"      # das zweite Teil, wo es eines gibt
MOHN = "#D2452B"
PAPIER = "#FBFAF7"

MM = 3.9                 # Pixel je Millimeter
R_DRUECKER = 10.0        # Radius des Drueckers
R_AUSSEN = 13.0          # Manschette aussen, auf dem Druecker gedehnt
D_SCHNUR = 4.0

DATEI = "tuerzwerg-manschette-ideen.svg"


def p(*werte):
    return " ".join(f"{v:.1f}" for v in werte)


# ----------------------------------------------------------- Bausteine ----

def druecker(cx, cy):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_DRUECKER*MM:.1f}" '
            f'fill="{DRUECKER}" stroke="{LINIE}" stroke-width="1"/>')


def manschette(cx, cy, luecke=None, strich=1.6, ri=None, ra=None):
    """Ringquerschnitt. luecke = (von, bis) in Grad, 0 = unten."""
    ra = (R_AUSSEN if ra is None else ra) * MM
    ri = (R_DRUECKER if ri is None else ri) * MM
    if luecke is None:
        return (f'<path d="M{p(cx-ra,cy)} a{p(ra,ra)} 0 1 0 {p(2*ra,0)} '
                f'a{p(ra,ra)} 0 1 0 {p(-2*ra,0)} Z '
                f'M{p(cx-ri,cy)} a{p(ri,ri)} 0 1 1 {p(2*ri,0)} '
                f'a{p(ri,ri)} 0 1 1 {p(-2*ri,0)} Z" fill="{SILIKON}" '
                f'fill-rule="evenodd" stroke="{TINTE}" stroke-width="{strich}"/>')
    a0, a1 = [math.radians(90 + g) for g in luecke]
    def pt(r, a):
        return (cx + r * math.cos(a), cy + r * math.sin(a))
    return (f'<path d="M{p(*pt(ri,a0))} A{p(ri,ri)} 0 1 0 {p(*pt(ri,a1))} '
            f'L{p(*pt(ra,a1))} A{p(ra,ra)} 0 1 1 {p(*pt(ra,a0))} Z" '
            f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="{strich}"/>')


def manschette_nut(cx, cy, tiefe=2.6):
    """Querschnitt in der Nutebene: der Ring ist dort einfach duenner.
    Die ungenutete Aussenkontur steht gestrichelt daneben, sonst laesst
    sich nicht erkennen, dass es eine Nut ist."""
    ra = (R_AUSSEN - tiefe) * MM
    s = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_AUSSEN*MM:.1f}" '
         f'fill="none" stroke="{LINIE}" stroke-width="1.2" '
         f'stroke-dasharray="5 4"/>']
    ri = R_DRUECKER * MM
    s.append(f'<path d="M{p(cx-ra,cy)} a{p(ra,ra)} 0 1 0 {p(2*ra,0)} '
             f'a{p(ra,ra)} 0 1 0 {p(-2*ra,0)} Z '
             f'M{p(cx-ri,cy)} a{p(ri,ri)} 0 1 1 {p(2*ri,0)} '
             f'a{p(ri,ri)} 0 1 1 {p(-2*ri,0)} Z" fill="{SILIKON}" '
             f'fill-rule="evenodd" stroke="{TINTE}" stroke-width="1.6"/>')
    return "".join(s), ra


def schnur_linie(punkte, breite=D_SCHNUR, farbe=SCHNUR):
    d = "M" + " L".join(p(x, y) for x, y in punkte)
    return (f'<path d="{d}" fill="none" stroke="{farbe}" '
            f'stroke-width="{breite*MM:.1f}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def knoten(cx, cy, d=8.0, farbe=SCHNUR):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{d/2*MM:.1f}" '
            f'fill="{farbe}" stroke="{PAPIER}" stroke-width="1.2"/>')


def beschriftung(x, y, text, groesse=11.5, farbe=LEISE, anker="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{groesse}" '
            f'fill="{farbe}" text-anchor="{anker}" '
            f'font-family="Figtree, sans-serif">{text}</text>')


def pfeil(x1, y1, x2, y2, farbe=MOHN):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{farbe}" stroke-width="1.8" marker-end="url(#spitze)"/>')


def seitenansicht(cx, cy, nut_tief=0.0, band=False, knebel=False):
    """Laengsschnitt: Druecker waagerecht, Manschette darueber.

    Eine umlaufende Nut ist im Querschnitt nur ein duennerer Ring und
    damit nicht als Nut zu erkennen. Von der Seite dagegen sieht man sie
    sofort - deshalb hier diese Ansicht.
    """
    L, Ra, Rd = 28.0, R_AUSSEN, R_DRUECKER
    s = [f'<rect x="{cx-(L/2+9)*MM:.1f}" y="{cy-Rd*MM:.1f}" '
         f'width="{(L+18)*MM:.1f}" height="{2*Rd*MM:.1f}" '
         f'fill="{DRUECKER}" stroke="{LINIE}" stroke-width="1"/>']
    nb = 6.0
    if nut_tief > 0.0:
        teile = [(-L/2, -nb/2, Ra), (-nb/2, nb/2, Ra-nut_tief), (nb/2, L/2, Ra)]
    else:
        teile = [(-L/2, L/2, Ra)]
    for x0, x1, r in teile:
        for vz in (-1, 1):
            y = cy + vz * Rd * MM
            hoehe = (r - Rd) * MM
            s.append(f'<rect x="{cx+x0*MM:.1f}" '
                     f'y="{y if vz>0 else y-hoehe:.1f}" '
                     f'width="{(x1-x0)*MM:.1f}" height="{hoehe:.1f}" '
                     f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.4"/>')
    if nut_tief > 0.0:
        rs = (Ra - nut_tief + D_SCHNUR / 2) * MM
        for vz in (-1, 1):
            s.append(f'<circle cx="{cx:.1f}" cy="{cy+vz*rs:.1f}" '
                     f'r="{D_SCHNUR/2*MM:.1f}" fill="{SCHNUR}"/>')
        if band:
            for vz in (-1, 1):
                s.append(f'<rect x="{cx-(nb/2+0.4)*MM:.1f}" '
                         f'y="{cy+vz*rs - (1.2 if vz>0 else -1.2+2.4)*MM:.1f}" '
                         f'width="{(nb+0.8)*MM:.1f}" height="{2.4*MM:.1f}" '
                         f'fill="{ZWEITES}" stroke="{TINTE}" '
                         f'stroke-width="1"/>')
        s.append(schnur_linie([(cx, cy + rs), (cx, cy + 26 * MM)]))
    if knebel:
        s.append(f'<rect x="{cx-6*MM:.1f}" y="{cy+Rd*MM+1.2*MM:.1f}" '
                 f'width="{12*MM:.1f}" height="{5*MM:.1f}" rx="{1.4*MM:.1f}" '
                 f'fill="{ZWEITES}" stroke="{TINTE}" stroke-width="1.2"/>')
        s.append(f'<path d="M{p(cx-9*MM, cy+Rd*MM+0.6*MM)} '
                 f'L{p(cx+14*MM, cy+Rd*MM+0.6*MM)}" stroke="{LEISE}" '
                 f'stroke-width="1.2" stroke-dasharray="4 3" fill="none"/>')
        s.append(pfeil(cx + 17 * MM, cy + Rd * MM + 3.5 * MM,
                       cx + 10 * MM, cy + Rd * MM + 3.5 * MM))
        s.append(schnur_linie([(cx, cy + Rd * MM + 4 * MM),
                               (cx, cy + 26 * MM)]))
    return "".join(s)


# ------------------------------------------------------------- Entwuerfe --

def e_heute(cx, cy):
    """Kammer an der Bohrung - der heutige Stand."""
    s = [druecker(cx, cy), manschette(cx, cy, luecke=(-33, 33))]
    # Kiel mit Kammer
    kb, ko, ku = 5.5 * MM, cy + 9 * MM, cy + 19.5 * MM
    s.append(f'<path d="M{p(cx-kb-3*MM, ko)} L{p(cx-kb-3*MM, ku)} '
             f'A{p(3*MM,3*MM)} 0 0 0 {p(cx-kb+0*MM, ku+3*MM)} '
             f'L{p(cx+kb, ku+3*MM)} A{p(3*MM,3*MM)} 0 0 0 '
             f'{p(cx+kb+3*MM, ku)} L{p(cx+kb+3*MM, ko)} Z" '
             f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.6"/>')
    s.append(f'<rect x="{cx-kb:.1f}" y="{cy-2*MM:.1f}" '
             f'width="{2*kb:.1f}" height="{18*MM:.1f}" rx="{2.5*MM:.1f}" '
             f'fill="{PAPIER}" stroke="{TINTE}" stroke-width="1.2"/>')
    s.append(knoten(cx, cy + 11 * MM))
    s.append(schnur_linie([(cx, cy + 11 * MM), (cx, cy + 30 * MM)]))
    s.append(pfeil(cx + 9.5 * MM, cy - 6 * MM, cx + 9.5 * MM, cy - 1 * MM))
    s.append(beschriftung(cx + 11 * MM, cy - 8 * MM,
                          "Ring hier offen", 10, MOHN, "start"))
    return "".join(s)


def e_quertasche(cx, cy):
    """Tasche unter dem Rohr, quer durch - die gerechnete Fassung."""
    s = [druecker(cx, cy), manschette(cx, cy)]
    kb, ko, ku = 7 * MM, cy + 9 * MM, cy + 23 * MM
    s.append(f'<path d="M{p(cx-kb, ko)} L{p(cx-kb, ku-3*MM)} '
             f'A{p(kb,kb)} 0 0 0 {p(cx+kb, ku-3*MM)} L{p(cx+kb, ko)} Z" '
             f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.6"/>')
    s.append(f'<rect x="{cx-6*MM:.1f}" y="{cy+12*MM:.1f}" '
             f'width="{12*MM:.1f}" height="{8.5*MM:.1f}" rx="{2.5*MM:.1f}" '
             f'fill="{PAPIER}" stroke="{TINTE}" stroke-width="1.2" '
             f'stroke-dasharray="4 3"/>')
    s.append(knoten(cx, cy + 16 * MM))
    s.append(schnur_linie([(cx, cy + 16 * MM), (cx, cy + 32 * MM)]))
    return "".join(s)


def e_umschlingung(cx, cy):
    """Schnur legt sich in eine umlaufende Nut - Zug zieht sie zu."""
    r = [seitenansicht(cx, cy, nut_tief=2.6)]
    for vz in (-1, 1):
        r.append(pfeil(cx - 15 * MM, cy + vz * 22 * MM,
                       cx - 3 * MM, cy + vz * 15 * MM))
    r.append(beschriftung(cx, cy - 26 * MM,
                          "Zug zieht die Manschette zu", 10, MOHN))
    return "".join(r)


def e_drueckerschlaufe(cx, cy):
    """Schnur schlingt sich um den Druecker, die Manschette deckt sie ab."""
    s = [druecker(cx, cy)]
    rl = (R_DRUECKER + D_SCHNUR / 2) * MM
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rl:.1f}" '
             f'fill="none" stroke="{SCHNUR}" '
             f'stroke-width="{D_SCHNUR*MM:.1f}"/>')
    s.append(manschette(cx, cy, luecke=(-11, 11),
                        ri=R_DRUECKER + D_SCHNUR,
                        ra=R_AUSSEN + D_SCHNUR))
    s.append(schnur_linie([(cx, cy + rl), (cx, cy + 32 * MM)]))
    s.append(beschriftung(cx, cy - (R_AUSSEN + 11) * MM,
                          "Manschette nur Abdeckung", 10, LEISE))
    return "".join(s)


def e_quersteg(cx, cy):
    """Quersteg im Kiel, Schnur mit Ankerstich."""
    s = [druecker(cx, cy), manschette(cx, cy)]
    kb, ko, ku = 7 * MM, cy + 9 * MM, cy + 22 * MM
    s.append(f'<path d="M{p(cx-kb, ko)} L{p(cx-kb, ku-3.5*MM)} '
             f'A{p(kb,kb)} 0 0 0 {p(cx+kb, ku-3.5*MM)} L{p(cx+kb, ko)} Z" '
             f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.6"/>')
    # Fenster, darunter bleibt der Steg stehen
    s.append(f'<rect x="{cx-5*MM:.1f}" y="{cy+11*MM:.1f}" '
             f'width="{10*MM:.1f}" height="{5.5*MM:.1f}" rx="{1.8*MM:.1f}" '
             f'fill="{PAPIER}" stroke="{TINTE}" stroke-width="1.2"/>')
    s.append(beschriftung(cx + 8.5 * MM, cy + 20 * MM, "Steg", 10,
                          LEISE, "start"))
    s.append(f'<line x1="{cx+7.5*MM:.1f}" y1="{cy+19*MM:.1f}" '
             f'x2="{cx+3*MM:.1f}" y2="{cy+18*MM:.1f}" stroke="{LEISE}" '
             f'stroke-width="1"/>')
    # Ankerstich: Schnur laeuft durch das Fenster, um den Steg herum
    s.append(schnur_linie([(cx - 2.6 * MM, cy + 12 * MM),
                           (cx - 2.6 * MM, cy + 19.5 * MM),
                           (cx + 2.6 * MM, cy + 19.5 * MM),
                           (cx + 2.6 * MM, cy + 12 * MM)], breite=3.0))
    s.append(schnur_linie([(cx, cy + 11.5 * MM), (cx, cy + 32 * MM)]))
    return "".join(s)


def e_einteilig(cx, cy):
    """Manschette, Band und Reif in einem Schuss - keine Schnur."""
    s = [druecker(cx, cy), manschette(cx, cy)]
    b = 6.0 * MM
    s.append(f'<path d="M{p(cx-b/2, cy+10*MM)} L{p(cx-b/2, cy+36*MM)} '
             f'L{p(cx+b/2, cy+36*MM)} L{p(cx+b/2, cy+10*MM)} Z" '
             f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.6"/>')
    s.append(f'<ellipse cx="{cx:.1f}" cy="{cy+42*MM:.1f}" '
             f'rx="{9*MM:.1f}" ry="{6.5*MM:.1f}" fill="none" '
             f'stroke="{SILIKON}" stroke-width="{4.0*MM:.1f}"/>')
    s.append(f'<ellipse cx="{cx:.1f}" cy="{cy+42*MM:.1f}" '
             f'rx="{9*MM:.1f}" ry="{6.5*MM:.1f}" fill="none" '
             f'stroke="{TINTE}" stroke-width="1.4"/>')
    s.append(beschriftung(cx + 6 * MM, cy + 22 * MM, "alles ein Teil", 10,
                          MOHN, "start"))
    return "".join(s)


def e_knebel(cx, cy):
    """Zweiteilig: Knebel an der Schnur, laengs in eine Nut geschoben."""
    return (seitenansicht(cx, cy, knebel=True)
            + beschriftung(cx, cy + 26 * MM,
                           "wird von der Seite eingeschoben", 10, ZWEITES))


def e_halbschalen(cx, cy):
    """Zweiteilig: zwei gleiche Halbschalen, der Knoten liegt dazwischen."""
    s = [druecker(cx, cy)]
    ra, ri = R_AUSSEN * MM, R_DRUECKER * MM
    for vz in (-1, 1):
        s.append(f'<path d="M{p(cx+vz*2, cy-ri)} A{p(ri,ri)} 0 0 {1 if vz>0 else 0} '
                 f'{p(cx+vz*2, cy+ri)} L{p(cx+vz*2, cy+ra)} '
                 f'A{p(ra,ra)} 0 0 {0 if vz>0 else 1} {p(cx+vz*2, cy-ra)} Z" '
                 f'fill="{SILIKON}" stroke="{TINTE}" stroke-width="1.6"/>')
    s.append(f'<rect x="{cx-4.5*MM:.1f}" y="{cy+ri:.1f}" '
             f'width="{9*MM:.1f}" height="{9*MM:.1f}" rx="{2*MM:.1f}" '
             f'fill="{PAPIER}" stroke="{TINTE}" stroke-width="1.2"/>')
    s.append(knoten(cx, cy + ri + 4.5 * MM, 7.5))
    s.append(schnur_linie([(cx, cy + ri + 4.5 * MM), (cx, cy + 30 * MM)]))
    s.append(beschriftung(cx, cy - (R_AUSSEN + 8) * MM,
                          "Trennung in der Mitte", 10, MOHN))
    return "".join(s)


def e_ueberwurf(cx, cy):
    """Zweiteilig: Manschette mit Nut, Schnur darin, Band darueber."""
    return (seitenansicht(cx, cy, nut_tief=3.2, band=True)
            + beschriftung(cx, cy - 26 * MM,
                           "Band hält die Schnur in der Nut", 10, ZWEITES))


# ---------------------------------------------------------------- Blatt ---

ENTWUERFE = [
    (e_heute, "Heute", "Kammer an der Bohrung",
     ["Werkzeug: Kern + Schieber", "Ring nur auf 12 % zu",
      "Knotenraum 5–7,5 mm"], False),
    (e_quertasche, "Quertasche", "Tasche unter dem Rohr, quer durch",
     ["Werkzeug: 2 Hälften + Kern", "Ring auf 87 % zu",
      "Knotenraum 8,5 mm, +3,5 mm hoch"], True),
    (e_umschlingung, "Umschlingung", "Schnur liegt in einer umlaufenden Nut",
     ["Werkzeug: 2 Hälften + Kern", "Ring bleibt ganz zu",
      "Zug erhöht die Klemmkraft"], True),
    (e_drueckerschlaufe, "Drückerschlaufe",
     "Schnur schlingt um den Drücker selbst",
     ["Werkzeug: 2 Hälften + Kern", "Manschette ohne jedes Merkmal",
      "Schlaufe kann axial wandern"], True),
    (e_quersteg, "Quersteg", "Ankerstich um einen Steg im Kiel",
     ["Werkzeug: 2 Hälften + Kern", "kein Knoten nötig",
      "Steg biegt sich unter Last"], True),
    (e_einteilig, "Einteilig", "Manschette, Band und Reif in einem Schuss",
     ["Werkzeug: groß, aber einfach", "keine Montage, keine Schnur",
      "Band dehnt sich ~15 mm"], True),
    (e_knebel, "Knebel  ·  2 Teile", "Knebel an der Schnur, längs eingeschoben",
     ["Werkzeug: 2 × trivial", "Knoten verschwindet ganz",
      "T-Nut läuft zum Ende offen"], True),
    (e_halbschalen, "Halbschalen  ·  2 Teile",
     "Zwei gleiche Schalen klemmen den Knoten",
     ["Werkzeug: EIN Nest, kein Kern", "beide Teile identisch",
      "muss zuverlässig zusammenhalten"], True),
    (e_ueberwurf, "Überwurfband  ·  2 Teile",
     "Band presst die Schnur in eine Nut",
     ["Werkzeug: 2 × trivial", "Manschette ohne jedes Merkmal",
      "Band ist ein Verschleißteil"], True),
]


def blatt(datei=DATEI):
    sp, ze = 3, 3
    bw, bh = 385, 445
    rand = 30
    kopf = 112
    w = rand * 2 + sp * bw
    h = kopf + ze * bh + rand
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="Figtree, sans-serif">',
         f'<defs><marker id="spitze" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         f'<path d="M0 0 L10 5 L0 10 z" fill="{MOHN}"/></marker></defs>',
         f'<rect width="100%" height="100%" fill="{PAPIER}"/>',
         f'<text x="{rand}" y="46" font-size="27" font-weight="700" '
         f'fill="{TINTE}">Neun Wege, die Schnur zu befestigen</text>',
         f'<text x="{rand}" y="70" font-size="13.5" fill="{LEISE}">'
         f'Alles im selben Maßstab. Grün ist die Schnur, Orange das zweite '
         f'Teil. Sechs Querschnitte, drei Seitenansichten — je nachdem, '
         f'was die Idee zeigt.</text>',
         f'<text x="{rand}" y="89" font-size="13.5" fill="{LEISE}">'
         f'Die Frage ist nicht, wie der Kern herauskommt — sondern ob der '
         f'Knoten überhaupt in die Manschette muss.</text>']
    for i, (f, name, unter, punkte, gut) in enumerate(ENTWUERFE):
        x0 = rand + (i % sp) * bw
        y0 = kopf + (i // sp) * bh
        s.append(f'<rect x="{x0+6}" y="{y0}" width="{bw-12}" height="{bh-16}" '
                 f'rx="5" fill="#fff" stroke="{LINIE}"/>')
        s.append(f'<text x="{x0+24}" y="{y0+30}" font-size="16.5" '
                 f'font-weight="700" fill="{TINTE}">{name}</text>')
        s.append(f'<text x="{x0+24}" y="{y0+50}" font-size="11.5" '
                 f'fill="{LEISE}">{unter}</text>')
        s.append(f'<g>{f(x0 + bw/2, y0 + 168)}</g>')
        for j, t in enumerate(punkte):
            farbe = TINTE if j == 0 else LEISE
            s.append(f'<text x="{x0+24}" y="{y0+bh-84+j*19}" font-size="11.5" '
                     f'fill="{farbe}">{t}</text>')
        if not gut:
            s.append(f'<text x="{x0+bw-24}" y="{y0+30}" font-size="11.5" '
                     f'fill="{MOHN}" text-anchor="end">heutiger Stand</text>')
    s.append('</svg>')
    open(datei, "w", encoding="utf-8").write("\n".join(s))
    return datei


if __name__ == "__main__":
    print("geschrieben:", blatt())
    for f, name, unter, punkte, _ in ENTWUERFE:
        print(f"  {name:18s} {unter}")
        for t in punkte:
            print(f"      {t}")
