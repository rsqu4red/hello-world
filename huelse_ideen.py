#!/usr/bin/env python3
"""
Türzwerg – sechs Wege, die Schnur in einer Hülse zu halten

Warum der Knoten durchrutscht, und warum eine Hülse das nicht tut
------------------------------------------------------------------

Ein Knoten aus Paracord ist unter Zug kein starrer Koerper. Er laengt
sich und wird dabei schmaler - dasselbe Prinzip wie eine Fingerfalle.
Das Silikonloch muss sich also gar nicht um 100 Prozent weiten, der
Knoten kommt ihm entgegen. Deshalb hilft auch keine haertere Mischung:
die Bewegung kommt von der Schnur, nicht vom Loch.

Eine starre Huelse kann sich nicht laengen. Sie muesste das Loch
tatsaechlich um 150 Prozent aufweiten, und das tut sie nicht.

Was die Huelse aushalten muss
------------------------------

    25 kg Kind  x  2 dynamisch  x  2 Sicherheit  =  rund 1000 N

Paracord 550 reisst bei 2450 N, mit Knoten bei rund 1200. Ziel ist
also: die Verbindung haelt mehr als die Schnur - wenn etwas versagt,
dann das Seil und nicht die Verbindung.

Reine Klemmung reicht nicht, und das ist keine Meinung
-------------------------------------------------------

    F = mu * p * A,  mu = 0,3 fuer Nylon auf Kunststoff

    Klemmlaenge   Mantelflaeche   noetiger Radialdruck
       6 mm           75 mm2           43 MPa
      10 mm          126 mm2           26 MPa
      15 mm          188 mm2           17 MPa
      25 mm          314 mm2           10 MPa

Nylon beginnt bei etwa 10 MPa dauerhaft zu kriechen. Eine Huelse von
6 mm, die nur presst, muesste die Schnur mit 43 MPa zerquetschen - und
wuerde sich ueber Monate trotzdem loesen, weil das Material unter dem
Druck wegfliesst. Jede tragfaehige Loesung braucht deshalb Formschluss,
nicht nur Reibung.

Zwei Formschluesse sind besonders wirksam:

  Kapstan. Jede Umschlingung vervielfacht den Halt mit e^(mu*phi).
  Anderthalb Windungen um einen Poller: Verhaeltnis 17, der Schwanz
  muss nur noch 58 N halten statt 1000.

  Selbsthemmender Kegel. Unter Last zieht sich der Keil tiefer und
  presst staerker. Selbsthemmend bleibt er bis 17 Grad halbem
  Kegelwinkel; praktisch nimmt man 6 bis 8.

    python3 huelse_ideen.py
"""

import math

TINTE, LEISE, LINIE = "#17160F", "#6C675A", "#C9C4B6"
PAPIER, MOHN = "#FBFAF7", "#D2452B"
SCHNUR, KUNST, METALL = "#55886B", "#E0982F", "#9AA0A6"

MM = 9.0
D_SCHNUR = 4.0
DATEI = "tuerzwerg-huelse-ideen.svg"


def p(*w):
    return " ".join(f"{v:.1f}" for v in w)


def txt(x, y, s, g=10.5, f=LEISE, a="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{g}" fill="{f}" '
            f'text-anchor="{a}" font-family="Figtree, sans-serif">{s}</text>')


def pfeil(x1, y1, x2, y2, f=MOHN):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{f}" stroke-width="1.8" marker-end="url(#sp)"/>')


def band(pts, b=D_SCHNUR, f=SCHNUR):
    d = "M" + " L".join(p(x, y) for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{f}" '
            f'stroke-width="{b*MM:.1f}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def huelse(cx, cy, da, h, di_unten, farbe=KUNST, kavi=None):
    """Laengsschnitt: zwei Wangen, unten die Austrittsbohrung."""
    ra, ri = da / 2 * MM, di_unten / 2 * MM
    H = h * MM
    s = []
    for vz in (-1, 1):
        s.append(f'<path d="M{p(cx+vz*ri, cy+H)} L{p(cx+vz*ra, cy+H)} '
                 f'L{p(cx+vz*ra, cy)} L{p(cx+vz*(kavi or ri), cy)} Z" '
                 f'fill="{farbe}" stroke="{TINTE}" stroke-width="1.4"/>')
    return "".join(s)


# ------------------------------------------------------------- Entwuerfe --

def e_knoten(cx, cy):
    """Knoten in einer starren, geteilten Huelse."""
    da, h, dk = 11.0, 10.0, 8.5
    ra, H = da / 2 * MM, h * MM
    s = [f'<path d="M{p(cx-ra, cy)} L{p(cx+ra, cy)} L{p(cx+ra, cy+H)} '
         f'L{p(cx+2.25*MM, cy+H)} L{p(cx+2.25*MM, cy+H-2*MM)} '
         f'A{p(dk/2*MM, dk/2*MM)} 0 0 0 {p(cx-2.25*MM, cy+H-2*MM)} '
         f'L{p(cx-2.25*MM, cy+H)} L{p(cx-ra, cy+H)} Z" '
         f'fill="{KUNST}" stroke="{TINTE}" stroke-width="1.4"/>']
    s.append(f'<circle cx="{cx:.1f}" cy="{cy+(h-4.8)*MM:.1f}" '
             f'r="{dk/2*MM:.1f}" fill="{SCHNUR}" stroke="{PAPIER}" '
             f'stroke-width="1.2"/>')
    s.append(band([(cx, cy + (h - 4.8) * MM), (cx, cy + (h + 5) * MM)]))
    s.append(f'<line x1="{cx:.1f}" y1="{cy-4:.1f}" x2="{cx:.1f}" '
             f'y2="{cy+H+4:.1f}" stroke="{MOHN}" stroke-width="1.3" '
             f'stroke-dasharray="5 4"/>')
    s.append(txt(cx, cy - 10, "geteilt, klipst um den Knoten", 10, MOHN))
    return "".join(s)


def e_press(cx, cy):
    """Metallhuelse, Seil doppelt gelegt und verpresst."""
    da, h = 10.0, 13.0
    H = h * MM
    s = [band([(cx - 2.2 * MM, cy + H + 4 * MM), (cx - 2.2 * MM, cy + 2 * MM),
               (cx, cy + 1.2 * MM), (cx + 2.2 * MM, cy + 2 * MM),
               (cx + 2.2 * MM, cy + (h - 2) * MM)], b=3.6)]
    s.append(huelse(cx, cy, da, h, 9.0))
    s.append(f'<rect x="{cx-da/2*MM:.1f}" y="{cy:.1f}" '
             f'width="{da*MM:.1f}" height="{H:.1f}" fill="none" '
             f'stroke="{TINTE}" stroke-width="1.4"/>')
    s.append(f'<rect x="{cx-da/2*MM:.1f}" y="{cy:.1f}" '
             f'width="{da*MM:.1f}" height="{H:.1f}" fill="{METALL}" '
             f'opacity="0.35"/>')
    for yy in (0.32, 0.62):
        s.append(pfeil(cx - da * MM, cy + H * yy, cx - da / 2 * MM - 3,
                       cy + H * yy))
        s.append(pfeil(cx + da * MM, cy + H * yy, cx + da / 2 * MM + 3,
                       cy + H * yy))
    s.append(txt(cx, cy - 10, "Seil umgeschlagen, dann verpresst", 10, MOHN))
    return "".join(s)


def e_keil(cx, cy):
    """Selbsthemmender Kegel mit geteiltem Keil."""
    da, h = 10.0, 9.0
    ra, H = da / 2 * MM, h * MM
    ro, ru = 3.6 * MM, 2.3 * MM
    s = []
    for vz in (-1, 1):
        s.append(f'<path d="M{p(cx+vz*ro, cy)} L{p(cx+vz*ra, cy)} '
                 f'L{p(cx+vz*ra, cy+H)} L{p(cx+vz*ru, cy+H)} Z" '
                 f'fill="{KUNST}" stroke="{TINTE}" stroke-width="1.4"/>')
    for vz in (-1, 1):
        s.append(f'<path d="M{p(cx+vz*2.1*MM, cy+1.2*MM)} '
                 f'L{p(cx+vz*3.3*MM, cy+1.2*MM)} '
                 f'L{p(cx+vz*2.15*MM, cy+H-0.6*MM)} '
                 f'L{p(cx+vz*2.1*MM, cy+H-0.6*MM)} Z" '
                 f'fill="{METALL}" stroke="{TINTE}" stroke-width="1.2"/>')
    s.append(band([(cx, cy - 1 * MM), (cx, cy + (h + 5) * MM)]))
    s.append(pfeil(cx + 6.5 * MM, cy + 2 * MM, cx + 4.0 * MM, cy + H - 1 * MM))
    s.append(txt(cx, cy - 10, "Zug zieht den Keil tiefer", 10, MOHN))
    return "".join(s)


def e_kapstan(cx, cy):
    """Anderthalb Windungen um einen Poller im Inneren."""
    da, h = 10.0, 11.0
    ra, H = da / 2 * MM, h * MM
    s = [f'<rect x="{cx-ra:.1f}" y="{cy:.1f}" width="{2*ra:.1f}" '
         f'height="{H:.1f}" rx="3" fill="{KUNST}" stroke="{TINTE}" '
         f'stroke-width="1.4"/>']
    px, py, pr = cx, cy + 4.2 * MM, 1.4 * MM
    s.append(band([(cx - 2.0 * MM, cy + H + 4 * MM),
                   (cx - 2.0 * MM, py + 1.4 * MM)], b=3.4))
    s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr + 2.0*MM:.1f}" '
             f'fill="none" stroke="{SCHNUR}" stroke-width="{3.4*MM:.1f}"/>')
    s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr:.1f}" '
             f'fill="{METALL}" stroke="{TINTE}" stroke-width="1.2"/>')
    s.append(band([(cx + 2.0 * MM, py + 1.4 * MM),
                   (cx + 2.0 * MM, cy + (h - 0.6) * MM)], b=3.0))
    s.append(txt(cx, cy - 10, "1,5 Windungen: Schwanz hält 58 N", 10, MOHN))
    return "".join(s)


def e_umspritzt(cx, cy):
    """Huelse direkt an die Schnur gespritzt."""
    da, h = 10.0, 9.0
    ra, H = da / 2 * MM, h * MM
    s = [f'<rect x="{cx-ra:.1f}" y="{cy:.1f}" width="{2*ra:.1f}" '
         f'height="{H:.1f}" rx="3" fill="{KUNST}" stroke="{TINTE}" '
         f'stroke-width="1.4"/>']
    s.append(band([(cx, cy + 2.0 * MM), (cx, cy + (h + 5) * MM)]))
    for i in range(7):
        a = math.pi * (0.12 + 0.76 * i / 6)
        s.append(f'<line x1="{cx:.1f}" y1="{cy+2.0*MM:.1f}" '
                 f'x2="{cx - 3.3*MM*math.cos(a):.1f}" '
                 f'y2="{cy+2.0*MM - 1.6*MM*math.sin(a):.1f}" '
                 f'stroke="{SCHNUR}" stroke-width="2" stroke-linecap="round"/>')
    s.append(txt(cx, cy - 10, "Schmelze dringt ins Geflecht", 10, MOHN))
    return "".join(s)


def e_verguss(cx, cy):
    """Fasern aufgespleisst im Kegel, mit Harz vergossen."""
    da, h = 10.0, 10.0
    ra, H = da / 2 * MM, h * MM
    ro, ru = 3.9 * MM, 2.3 * MM
    s = []
    for vz in (-1, 1):
        s.append(f'<path d="M{p(cx+vz*ro, cy)} L{p(cx+vz*ra, cy)} '
                 f'L{p(cx+vz*ra, cy+H)} L{p(cx+vz*ru, cy+H)} Z" '
                 f'fill="{KUNST}" stroke="{TINTE}" stroke-width="1.4"/>')
    s.append(f'<path d="M{p(cx-ro, cy)} L{p(cx-ru, cy+H)} '
             f'L{p(cx+ru, cy+H)} L{p(cx+ro, cy)} Z" fill="{METALL}" '
             f'opacity="0.35"/>')
    for i in range(9):
        t = -1.0 + 2.0 * i / 8
        s.append(f'<line x1="{cx + t*1.7*MM:.1f}" y1="{cy+H:.1f}" '
                 f'x2="{cx + t*3.4*MM:.1f}" y2="{cy+0.6*MM:.1f}" '
                 f'stroke="{SCHNUR}" stroke-width="2.2" '
                 f'stroke-linecap="round"/>')
    s.append(band([(cx, cy + H), (cx, cy + (h + 5) * MM)]))
    s.append(txt(cx, cy - 10, "Fasern gespreizt, dann vergossen", 10, MOHN))
    return "".join(s)


ENTWUERFE = [
    (e_knoten, "Knoten in der Hülse", "Ø11 × 10 mm, zweiteilig",
     ["Formschluss: der Knoten selbst",
      "Schulterpressung 18–24 MPa, für PA kein Problem",
      "knoten, zuklipsen — das Loch hält den Klips zu",
      "sicherste Variante, aber die größte"]),
    (e_press, "Presshülse, Seil doppelt", "Alu oder Kupfer, Ø10 × 13 mm",
     ["Formschluss: die Umkehrschlaufe",
      "Standardteil, Standardzange, nichts zu entwickeln",
      "Nylon kriecht, die Umkehrschlaufe hält trotzdem",
      "Metall am Kinderprodukt: Kanten, Nickel prüfen"]),
    (e_keil, "Klemmkegel", "selbsthemmend, Ø10 × 9 mm",
     ["Formschluss: Keil im Kegel, unter Last stärker",
      "selbsthemmend bis 17°, praktisch 6 bis 8°",
      "zwei Teile, beide einfach zu spritzen",
      "muss vorgespannt werden, greift sonst spät"]),
    (e_kapstan, "Kapstan-Hülse", "Umschlingung, Ø10 × 11 mm",
     ["Formschluss: Reibung über Umschlingung, e^(µφ)",
      "1,5 Windungen → Faktor 17 → Schwanz nur 58 N",
      "schont die Fasern, nichts wird gequetscht",
      "Einfädeln fummelig, eher Handmontage"]),
    (e_umspritzt, "Umspritzt", "Hülse direkt an die Schnur, Ø10 × 9 mm",
     ["Formschluss: Schmelze im Geflecht",
      "Normalfall bei Kabelenden, hält mehr als die Schnur",
      "ein Arbeitsgang, kein Zusatzteil, keine Montage",
      "Schnur wird Baugruppe: Werkzeug mit Einlage"]),
    (e_verguss, "Vergussanker", "Fasern gespreizt, Ø10 × 10 mm",
     ["Formschluss: jede einzelne Faser im Harz",
      "stärkste Variante, Prinzip der Seilendvergüsse",
      "Kegel unten eng: Zug verkeilt zusätzlich",
      "Aushärtezeit nötig, 2K oder Schmelzkleber"]),
]


def blatt(datei=DATEI):
    bw, bh, rand, kopf = 380, 445, 30, 126
    w, h = rand * 2 + 3 * bw, kopf + 2 * bh + rand
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="Figtree, sans-serif">',
         f'<defs><marker id="sp" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         f'<path d="M0 0 L10 5 L0 10 z" fill="{MOHN}"/></marker></defs>',
         f'<rect width="100%" height="100%" fill="{PAPIER}"/>',
         f'<text x="{rand}" y="46" font-size="27" font-weight="700" '
         f'fill="{TINTE}">Sechs Hülsen statt des Knotens</text>',
         f'<text x="{rand}" y="73" font-size="13.5" fill="{LEISE}">'
         f'Längsschnitte, gleicher Maßstab. Grün ist die Schnur, Orange die '
         f'Hülse, Grau ein Metallteil.</text>',
         f'<text x="{rand}" y="94" font-size="13.5" fill="{LEISE}">'
         f'Auslegung auf <tspan font-weight="600">1000 N</tspan> — 25 kg × 2 '
         f'dynamisch × 2 Sicherheit. Reine Klemmung auf 6 mm bräuchte 43 MPa '
         f'und scheidet damit aus: alle sechs arbeiten mit Formschluss.</text>']
    for i, (f, name, unter, punkte) in enumerate(ENTWUERFE):
        x0, y0 = rand + (i % 3) * bw, kopf + (i // 3) * bh
        s.append(f'<rect x="{x0+6}" y="{y0}" width="{bw-12}" height="{bh-16}" '
                 f'rx="5" fill="#fff" stroke="{LINIE}"/>')
        s.append(f'<text x="{x0+24}" y="{y0+32}" font-size="16.5" '
                 f'font-weight="700" fill="{TINTE}">{name}</text>')
        s.append(f'<text x="{x0+24}" y="{y0+51}" font-size="11.5" '
                 f'fill="{LEISE}">{unter}</text>')
        s.append(f'<g>{f(x0 + bw/2, y0 + 108)}</g>')
        for j, t in enumerate(punkte):
            farbe = TINTE if j == 0 else LEISE
            gew = "600" if j == 0 else "400"
            s.append(f'<text x="{x0+24}" y="{y0+bh-104+j*21}" font-size="11.5" '
                     f'font-weight="{gew}" fill="{farbe}">{t}</text>')
    s.append('</svg>')
    open(datei, "w", encoding="utf-8").write("\n".join(s))
    return datei


if __name__ == "__main__":
    print("geschrieben:", blatt())
    for _, name, unter, punkte in ENTWUERFE:
        print(f"  {name:24s}{unter}")
        print(f"      {punkte[0]}")
