#!/usr/bin/env python3
"""
Türzwerg – das durchgehende Rundloch: was daran aufgeht und was nicht

Der Vorschlag: statt der eckigen Knotenkammer ein rundes Loch von rund
10 mm, und dieses Loch nach oben durch die Rohrwand bis in die Bohrung
verlaengern. Dann bildet es ein einfacher Stab.

Der erste Teil stimmt, und zwar deutlicher als gedacht. Eine Tasche mit
Boden ist eine Sackbohrung - der Kern muss irgendwie wieder heraus. Ein
Loch, das durchgeht, wird von einem geraden Stift gebildet, und der ist
das billigste, robusteste und am besten polierbare Formelement, das es
gibt. Legt man die Trennebene zusaetzlich waagerecht, braucht der Stift
nicht einmal eine Mechanik: er steht fest in der unteren Haelfte, und
das Teil wird beim Auswerfen einfach von ihm abgezogen.

Der Haken steckt in der Stufe.

Der Knoten haelt nur, wenn das Loch sich nach unten verengt - er muss
sich an einer Schulter abstuetzen, denn die Schnur zieht nach unten. Der
Stift dagegen kommt nur nach unten heraus, wenn sich das Loch nach unten
erweitert. Das sind dieselbe Flaeche und entgegengesetzte Vorzeichen:

    Ød unten   Knoten muss weiten   Loch muss beim Entformen aufgehen
      4 mm            100 %                        150 %
      5 mm             60 %                        100 %
      6 mm             33 %                         67 %

Ohne Stufe faellt der Knoten durch: ein Sackstich in 4-mm-Schnur misst
rund 8 mm, das Loch 10.

Drei Aufloesungen stehen auf dem Blatt. Die dritte ist die, die zur
Zweiteil-Idee passt - dort wandert die Schulter in das zweite Teil, und
die Manschette selbst bleibt ein Rohr mit einem geraden Loch.

    python3 manschette_stabloch.py
"""

import math

from manschette_ideen import (DRUECKER, LEISE, LINIE, MM, MOHN, PAPIER,
                              R_AUSSEN, R_DRUECKER, SCHNUR, SILIKON, TINTE,
                              ZWEITES, beschriftung, druecker, knoten,
                              manschette, p, pfeil, schnur_linie)

R_RIPPE = 8.5
RIPPE_ACHSE = 11.0
RIPPE_UNTEN = RIPPE_ACHSE + R_RIPPE      # 19,5
D_LOCH = 10.0
D_KNOTEN = 8.0

DATEI = "tuerzwerg-manschette-stabloch.svg"


def rippe(cx, cy):
    return (f'<circle cx="{cx:.1f}" cy="{cy+RIPPE_ACHSE*MM:.1f}" '
            f'r="{R_RIPPE*MM:.1f}" fill="{SILIKON}" stroke="{TINTE}" '
            f'stroke-width="1.6"/>')


def loch(cx, cy, d_oben=D_LOCH, d_unten=None, y_oben=None):
    """Das Loch als ausgesparte Flaeche. y_oben = wo es oben endet."""
    yo = cy + (R_DRUECKER if y_oben is None else y_oben) * MM
    yu = cy + RIPPE_UNTEN * MM
    ro = d_oben / 2 * MM
    if d_unten is None:
        return (f'<rect x="{cx-ro:.1f}" y="{yo:.1f}" width="{2*ro:.1f}" '
                f'height="{yu-yo:.1f}" fill="{PAPIER}" stroke="{TINTE}" '
                f'stroke-width="1.3"/>')
    ru = d_unten / 2 * MM
    ys = cy + 16.5 * MM
    return (f'<path d="M{p(cx-ro,yo)} L{p(cx-ro,ys)} L{p(cx-ru,ys)} '
            f'L{p(cx-ru,yu)} L{p(cx+ru,yu)} L{p(cx+ru,ys)} '
            f'L{p(cx+ro,ys)} L{p(cx+ro,yo)} Z" fill="{PAPIER}" '
            f'stroke="{TINTE}" stroke-width="1.3"/>')


def stift(cx, cy, d, von, bis, farbe=ZWEITES):
    r = d / 2 * MM
    return (f'<rect x="{cx-r:.1f}" y="{cy+von*MM:.1f}" width="{2*r:.1f}" '
            f'height="{(bis-von)*MM:.1f}" rx="1.5" fill="{farbe}" '
            f'opacity="0.45" stroke="{TINTE}" stroke-width="1.1"/>')


# ------------------------------------------------------------- Entwuerfe --

def a_vorschlag(cx, cy):
    """Ø10 durchgehend - der Stift geht, der Knoten faellt durch."""
    s = [druecker(cx, cy), rippe(cx, cy), manschette(cx, cy)]
    s.append(stift(cx, cy, D_LOCH, R_DRUECKER, RIPPE_UNTEN + 9))
    s.append(loch(cx, cy).replace(f'fill="{PAPIER}"', 'fill="none"'))
    s.append(pfeil(cx, cy + (RIPPE_UNTEN + 5) * MM,
                   cx, cy + (RIPPE_UNTEN + 12) * MM))
    s.append(beschriftung(cx + 7 * MM, cy + (RIPPE_UNTEN + 10) * MM,
                          "Stift gerade heraus", 10, ZWEITES, "start"))
    s.append(knoten(cx, cy + (RIPPE_UNTEN + 7) * MM, D_KNOTEN))
    s.append(beschriftung(cx - 7 * MM, cy + (RIPPE_UNTEN + 8) * MM,
                          "Ø8 fällt durch Ø10", 10, MOHN, "end"))
    return "".join(s)


def b_stufe(cx, cy):
    """Ø10 oben, Ø4 unten - der Knoten haelt, der Stift klemmt."""
    s = [druecker(cx, cy), rippe(cx, cy), manschette(cx, cy)]
    s.append(loch(cx, cy, D_LOCH, 4.0))
    s.append(knoten(cx, cy + 13 * MM, D_KNOTEN))
    s.append(schnur_linie([(cx, cy + 13 * MM), (cx, cy + 30 * MM)]))
    s.append(stift(cx, cy, D_LOCH, R_DRUECKER, 16.5))
    s.append(stift(cx, cy, 4.0, 16.5, RIPPE_UNTEN + 8))
    s.append(pfeil(cx + 9 * MM, cy + 19 * MM, cx + 3 * MM, cy + 17 * MM))
    s.append(beschriftung(cx + 10 * MM, cy + 20 * MM,
                          "Schulter muss durch Ø4", 10, MOHN, "start"))
    s.append(beschriftung(cx + 10 * MM, cy + 24 * MM,
                          "150 % Dehnung", 10, MOHN, "start"))
    return "".join(s)


def c_zweiteilig(cx, cy):
    """Ø10 durchgehend, die Schulter steckt im zweiten Teil."""
    s = [druecker(cx, cy), rippe(cx, cy), manschette(cx, cy),
         loch(cx, cy)]
    # Stopfen: Bund liegt in der Bohrung, Schaft im Loch, Ø4 fuer die Schnur
    bo, bu = R_DRUECKER - 1.2, RIPPE_UNTEN - 3.0
    s.append(f'<path d="M{p(cx-7*MM, cy+bo*MM)} L{p(cx+7*MM, cy+bo*MM)} '
             f'L{p(cx+7*MM, cy+(bo+1.4)*MM)} L{p(cx+4.7*MM, cy+(bo+1.4)*MM)} '
             f'L{p(cx+4.7*MM, cy+bu*MM)} L{p(cx-4.7*MM, cy+bu*MM)} '
             f'L{p(cx-4.7*MM, cy+(bo+1.4)*MM)} L{p(cx-7*MM, cy+(bo+1.4)*MM)} Z" '
             f'fill="{ZWEITES}" stroke="{TINTE}" stroke-width="1.3"/>')
    s.append(knoten(cx, cy + (bo + 3.4) * MM, 6.0))
    s.append(schnur_linie([(cx, cy + (bo + 3.4) * MM), (cx, cy + 30 * MM)]))
    s.append(pfeil(cx - 12 * MM, cy + (bo - 5) * MM, cx - 7.5 * MM,
                   cy + bo * MM))
    s.append(beschriftung(cx - 13 * MM, cy + (bo - 6) * MM,
                          "Bund trägt", 10, ZWEITES, "end"))
    return "".join(s)


def d_trennebene(cx, cy):
    """Waagerechte Trennebene - der Stift braucht keine Mechanik."""
    s = [druecker(cx, cy), rippe(cx, cy), manschette(cx, cy)]
    s.append(stift(cx, cy, D_LOCH, R_DRUECKER, RIPPE_UNTEN + 14))
    s.append(loch(cx, cy).replace(f'fill="{PAPIER}"', 'fill="none"'))
    s.append(f'<line x1="{cx-26*MM:.1f}" y1="{cy:.1f}" '
             f'x2="{cx+26*MM:.1f}" y2="{cy:.1f}" stroke="{MOHN}" '
             f'stroke-width="1.6" stroke-dasharray="8 5"/>')
    s.append(beschriftung(cx + 26 * MM, cy - 3 * MM, "Trennebene", 10,
                          MOHN, "end"))
    s.append(f'<line x1="{cx-20*MM:.1f}" y1="{cy+(RIPPE_UNTEN+12)*MM:.1f}" '
             f'x2="{cx+20*MM:.1f}" y2="{cy+(RIPPE_UNTEN+12)*MM:.1f}" '
             f'stroke="{LEISE}" stroke-width="1.4"/>')
    s.append(beschriftung(cx, cy + (RIPPE_UNTEN + 17) * MM,
                          "Stift steht fest in der unteren Hälfte", 10, LEISE))
    return "".join(s)


ENTWUERFE = [
    (a_vorschlag, "So wie vorgeschlagen", "Ø10 durchgehend bis in die Bohrung",
     ["Werkzeug: ein gerader Stift", "kein Schieber, kein Hinterschnitt",
      "aber: der Knoten hält nicht"], MOHN),
    (b_stufe, "Mit Stufe Ø4", "damit der Knoten sich abstützen kann",
     ["Knoten hält sicher", "Stift nach unten: 150 % Dehnung",
      "Stift nach oben: zwei Bewegungen"], MOHN),
    (c_zweiteilig, "Zwei Teile", "die Schulter steckt im Stopfen",
     ["Manschette: Rohr mit geradem Loch", "Stopfen trägt Ø4 und Bund",
      "Bund baut ~1 mm in die Bohrung"], ZWEITES),
    (d_trennebene, "Der eigentliche Gewinn", "Trennebene waagerecht legen",
     ["Stift ohne jede Mechanik", "Teil wird von ihm abgezogen",
      "gilt für alle drei oben"], LEISE),
]


def blatt(datei=DATEI):
    bw, bh, rand, kopf = 400, 470, 30, 118
    w, h = rand * 2 + 2 * bw, kopf + 2 * bh + rand
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="Figtree, sans-serif">',
         f'<defs><marker id="spitze" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         f'<path d="M0 0 L10 5 L0 10 z" fill="{MOHN}"/></marker></defs>',
         f'<rect width="100%" height="100%" fill="{PAPIER}"/>',
         f'<text x="{rand}" y="46" font-size="27" font-weight="700" '
         f'fill="{TINTE}">Das durchgehende Rundloch</text>',
         f'<text x="{rand}" y="72" font-size="13.5" fill="{LEISE}">'
         f'Querschnitt durch den Türdrücker. Orange ist das Werkzeug '
         f'beziehungsweise das zweite Teil.</text>',
         f'<text x="{rand}" y="93" font-size="13.5" fill="{LEISE}">'
         f'Der Knoten hält nur bei Verengung nach unten, der Stift kommt nur '
         f'bei Erweiterung nach unten heraus.</text>']
    for i, (f, name, unter, punkte, farbe) in enumerate(ENTWUERFE):
        x0, y0 = rand + (i % 2) * bw, kopf + (i // 2) * bh
        s.append(f'<rect x="{x0+6}" y="{y0}" width="{bw-12}" height="{bh-16}" '
                 f'rx="5" fill="#fff" stroke="{LINIE}"/>')
        s.append(f'<text x="{x0+26}" y="{y0+32}" font-size="17" '
                 f'font-weight="700" fill="{TINTE}">{name}</text>')
        s.append(f'<text x="{x0+26}" y="{y0+52}" font-size="11.5" '
                 f'fill="{LEISE}">{unter}</text>')
        s.append(f'<g>{f(x0 + bw/2, y0 + 160)}</g>')
        for j, t in enumerate(punkte):
            s.append(f'<text x="{x0+26}" y="{y0+bh-84+j*19}" font-size="11.5" '
                     f'fill="{farbe if j == len(punkte)-1 else TINTE if j==0 else LEISE}">'
                     f'{t}</text>')
    s.append('</svg>')
    open(datei, "w", encoding="utf-8").write("\n".join(s))
    return datei


if __name__ == "__main__":
    print("geschrieben:", blatt())
    print()
    print("Knoten Ø8 gegen das Loch:")
    print(f"  {'Ød unten':>9}{'Knoten weitet':>16}{'Entformen weitet':>19}")
    for d in (4.0, 5.0, 6.0, 7.0):
        print(f"  {d:8.0f} {(D_KNOTEN-d)/d*100:14.0f} % "
              f"{(D_LOCH-d)/d*100:16.0f} %")
