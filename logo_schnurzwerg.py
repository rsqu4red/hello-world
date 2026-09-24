#!/usr/bin/env python3
"""
Türzwerg – der Schnurzwerg: das Zeichen aus der Skizze

Unten ein offener Reif, darüber ein flacher Bogen als Krempe, und darauf
eine Mütze aus Schlaufen, die sich zur Spitze schliessen. Gleichbleibende
Strichstaerke, runde Enden, kein Knick.

Der Punkt, an dem die erste Fassung scheiterte
----------------------------------------------

Mein erster Versuch hat die Schlaufen UM eine senkrechte Achse gewickelt -
eine Spirale. Das ergibt unweigerlich eine Sprungfeder: jede Windung
umschliesst die Achse, die Linie laeuft immer in dieselbe Drehrichtung
weiter, und das Auge liest Draht.

Die Skizze macht es umgekehrt. Die Schlaufen zeigen AUS der Achse heraus -
jede geht hinaus, kehrt um und kommt zurueck, wie die Schlaufen einer
Schleife. Das ist die Bewegung, die eine Schnur macht, wenn man sie
verknotet, und deshalb liest das Auge Knoten statt Feder.

    Spirale:  Mittelpunkt innen, Linie umrundet ihn  -> Feder
    Blatt:    Mittelpunkt auf der Achse, Linie geht  -> Knoten
              hinaus und kehrt zurueck

Die Blaetter faechern sich dabei zu: unten zeigen sie fast waagerecht nach
aussen, oben steht das letzte senkrecht. Das ergibt von selbst die
Dreiecksform der Muetze, ohne dass eine Kontur gezeichnet werden muesste.

Zwei Linien, nicht eine
-----------------------

In der Skizze ist der Reif eine eigene Linie mit zwei freien Enden, und
die Muetze schwebt darueber. Das ist besser als mein Einstrich-Versuch,
aus zwei Gruenden: die Silhouette schnuert sich nicht mehr zwischen Reif
und Muetze ein (der Einstrich brauchte dort eine Verbindung, und die las
als Schlinge), und die Wunschfassung "Reif und Muetze in verschiedenen
Farben" ist damit ueberhaupt erst moeglich.

Der Kurvenzug ist zentripetales Catmull-Rom (alpha = 1/2), in kubische
Bezier umgerechnet. Uniform parametrisiert schlaegt die Kurve dort aus,
wo die Stuetzpunkte ungleich dicht stehen - an den Blattspitzen stehen
sie eng, auf der Achse weit. Zentripetal ist nachweislich schlaufen- und
spitzenfrei.

Intern wird mit y nach oben gerechnet (wie am Bauteil); erst beim
Schreiben des Pfades wird auf die SVG-Konvention gespiegelt.

    python3 logo_schnurzwerg.py
"""

import math

R = 36.0                # Reif aussen, wie am Bauteil
STRICH = 5.2            # Schnurstaerke: Ø4 am Ø72-Reif, leicht betont
LUECKE = 24.0           # halber Oeffnungswinkel des Reifs oben, in Grad
LUFT = 10.0             # Abstand Reifscheitel zu den Krempenenden

FARBEN = [("Salbei", "#55886B"), ("Mohn", "#D2452B"), ("Himmel", "#38689B"),
          ("Sonne", "#E0982F"), ("Schiefer", "#454A52"), ("Tinte", "#17160F")]


# ------------------------------------------------------------ Kurvenzug ----

def _bez(p0, p1, p2, p3):
    """Ein Catmull-Rom-Segment p1..p2 als kubische Bezier, zentripetal
    parametrisiert (alpha = 1/2, also t = Wurzel der Sehnenlaenge)."""
    t1 = max(math.dist(p0, p1) ** 0.5, 1e-6)
    t2 = max(math.dist(p1, p2) ** 0.5, 1e-6)
    t3 = max(math.dist(p2, p3) ** 0.5, 1e-6)
    b1, b2 = [], []
    for k in (0, 1):
        b1.append((t1 * t1 * p2[k] - t2 * t2 * p0[k]
                   + (2 * t1 * t1 + 3 * t1 * t2 + t2 * t2) * p1[k])
                  / (3 * t1 * (t1 + t2)))
        b2.append((t3 * t3 * p1[k] - t2 * t2 * p3[k]
                   + (2 * t3 * t3 + 3 * t3 * t2 + t2 * t2) * p2[k])
                  / (3 * t3 * (t3 + t2)))
    return tuple(b1), tuple(b2)


def _spiegel(a, b):
    """Gedachter Punkt vor dem Anfang: b an a gespiegelt. Ein doppelter
    Endpunkt ginge nicht - die Sehnenlaenge waere dort null."""
    return (2 * a[0] - b[0], 2 * a[1] - b[1])


def kurve(p):
    """Offener Kurvenzug durch alle Punkte, als SVG-Pfad. Die Punkte
    kommen mit y nach oben herein und werden hier gespiegelt."""
    p = [(x, -y) for x, y in p]
    q = [_spiegel(p[0], p[1])] + p + [_spiegel(p[-1], p[-2])]
    d = [f"M{p[0][0]:.2f} {p[0][1]:.2f}"]
    for i in range(1, len(q) - 2):
        c1, c2 = _bez(q[i - 1], q[i], q[i + 1], q[i + 2])
        d.append(f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} "
                 f"{q[i + 1][0]:.2f} {q[i + 1][1]:.2f}")
    return "".join(d)


# ----------------------------------------------------------------- Reif ----

def reif(offen=True, n=80):
    """Der Reif: ein Kreisbogen mit Luecke oben, beide Enden frei. Sie
    zeigen nach oben, der Muetze entgegen."""
    g = math.radians(LUECKE)
    a0 = math.pi / 2.0 - g
    bogen = 2.0 * math.pi - 2.0 * g if offen else 2.0 * math.pi + 1.1 * g
    return [(R * math.cos(a0 - bogen * i / n), R * math.sin(a0 - bogen * i / n))
            for i in range(n + 1)]


# ---------------------------------------------------------------- Muetze ---

def krempe(breit=42.0, bauch=10.0, ueber=1.04, n=34):
    """Der flache Bogen ueber dem Reif, von rechts nach links gezeichnet.

    Eine Parabel, ueber ihre Nullstellen hinaus verlaengert - dadurch
    biegen sich die beiden Enden nach unten, so wie in der Skizze, und
    zeigen auf die offenen Enden des Reifs.

    Die Krempe ist breiter als der Reif. Das ist der eigentliche Grund,
    warum das Zeichen nicht als Schlinge liest: die breiteste Stelle des
    Umrisses liegt unten an der Muetze, nicht in der Mitte.
    """
    fuss = R + LUFT
    p = []
    for i in range(n + 1):
        x = breit * ueber * (1.0 - 2.0 * i / n)
        p.append((x, fuss + bauch * (1.0 - (x / breit) ** 2)))
    return p


# Eine Schlaufe, in Vielfachen von Laenge und Breite. Zwei Dinge daran
# sind entscheidend und waren in der ersten Fassung falsch:
#
# Erstens laeuft sie aussen NICHT spitz zu. Drei Punkte um das aeussere
# Ende (0.86 / 1.00 / 0.86) ergeben eine runde Kehre. Ein einzelner
# Punkt an der Spitze ergibt eine Blattform - und fuenf davon lesen als
# Pflanze, nicht als Knoten.
#
# Zweitens liegen Ein- und Ausgang auf verschiedenen Seiten der Achse
# (-0.30 / +0.30). Dadurch kreuzt sich die Schnur am Fuss jeder Schlaufe.
# Diese Kreuzung ist das, was ein Auge als "verknotet" liest; ohne sie
# sind es nur aneinandergereihte Oesen.
SCHLAUFE = ((0.00, -0.30), (0.40, 0.54), (0.86, 0.50),
            (1.00, 0.00), (0.86, -0.50), (0.40, -0.54), (0.00, 0.30))


def blaetter(anzahl=5, y0=None, y1=112.0, laenge=47.0, schlank=0.42,
             faecher=78.0, neigung=6.0, breite=0.52, zipfel=1.45,
             steig=1.30):
    """Die Schlaufen der Muetze, als Blaetter aus einer steigenden Achse.

    anzahl   Zahl der Schlaufen
    y0, y1   Achse von unten nach oben
    laenge   Laenge des untersten Blattes
    schlank  wie stark die Blaetter nach oben kuerzer werden
    faecher  Winkel des untersten Blattes gegen die Senkrechte, in Grad;
             nach oben laeuft er auf null zu, das letzte steht senkrecht
    neigung  seitlicher Versatz der Achse nach oben - der Zipfel faellt
    breite   Schlaufenbreite je Laenge
    steig    Exponent der Achse. Ueber 1 steigt sie unten langsam an, so
             dass die beiden untersten Schlaufen fast auf einer Hoehe
             liegen - linear gerechnet sitzt die rechte sichtbar hoeher
             als die linke und die Muetze wirkt verrutscht.
    zipfel   Laengenzuschlag fuer das oberste Blatt; es ist die Spitze
             der Muetze und braucht mehr Gewicht als die Reihe hergibt
    """
    if y0 is None:
        y0 = R + LUFT + 16.0
    p = []
    for i in range(anzahl):
        t = i / (anzahl - 1.0)
        bx, by = neigung * t * t, y0 + (y1 - y0) * t ** steig
        a = math.radians(90.0 + faecher * (1.0 - t) * (1 if i % 2 == 0 else -1))
        lang = laenge * (1.0 - schlank * t) * (zipfel if i == anzahl - 1 else 1.0)
        weit = lang * breite * (1.0 - 0.30 * t)
        ux, uy = math.cos(a), math.sin(a)
        for lf, wf in SCHLAUFE:
            p.append((bx + lf * lang * ux - wf * weit * uy,
                      by + lf * lang * uy + wf * weit * ux))
    p.append((p[-1][0] * 0.3 + neigung * 0.7, y1 - laenge * 0.10))
    return p


def muetze(bommel=0.0, **kw):
    """Krempe und Blaetter als ein Strich. Optional endet der Zipfel in
    einem geschlossenen Bommel."""
    k = {a: kw.pop(a) for a in ("breit", "bauch") if a in kw}
    p = krempe(**k) + blaetter(**kw)
    if bommel > 0.0:
        mx, my = p[-1]
        cx, cy = mx, my + bommel
        p += [(cx + bommel * math.cos(math.pi * (-0.5 + 2.1 * i / 13)),
               cy + bommel * math.sin(math.pi * (-0.5 + 2.1 * i / 13)))
              for i in range(1, 14)]
    return p


# --------------------------------------------------------------- Zeichen ---

def zeichen(offen=True, **kw):
    """Reif und Muetze als zwei Striche in einem SVG. Zwei Pfade, damit
    die Fassung 'Reif und Muetze verschieden gefaerbt' moeglich bleibt -
    ohne zweite Farbe erben beide currentColor."""
    pr, pm = reif(offen), muetze(**kw)
    alle = pr + pm
    rand = STRICH * 0.75
    xs = [q[0] for q in alle]
    ys = [-q[1] for q in alle]
    vb = (min(xs) - rand, min(ys) - rand,
          max(xs) - min(xs) + 2 * rand, max(ys) - min(ys) + 2 * rand)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}" '
           f'fill="none" stroke="currentColor" stroke-width="{STRICH}" '
           f'stroke-linecap="round" stroke-linejoin="round" '
           f'style="display:block;width:100%;height:100%">'
           f'<path class="reif" d="{kurve(pr)}"/>'
           f'<path class="hut" d="{kurve(pm)}"/></svg>')
    return svg, vb[2], vb[3]


VARIANTEN = [
    ("fuenf", "Fünf Schlaufen", dict(),
     "Ihre Skizze. Fünf Blätter, die sich nach oben zufächern — unten "
     "fast waagerecht, oben senkrecht als Zipfel."),
    ("vier", "Vier Schlaufen",
     dict(anzahl=4, y1=104.0, faecher=74.0, zipfel=1.5),
     "Eine Schlaufe weniger, jede deutlicher. Die ruhigste der Reihe und "
     "die, die am kleinsten noch liest."),
    ("sechs", "Sechs Schlaufen",
     dict(anzahl=6, y1=120.0, laenge=54.0, schlank=0.52, zipfel=1.35),
     "Dichter verknotet. Braucht Platz, trägt dafür große Formate und "
     "wirkt handgeknüpft statt konstruiert."),
    ("spitz", "Spitzer Zipfel",
     dict(y1=108.0, zipfel=2.0, breite=0.32, schlank=0.55, neigung=14.0),
     "Der Knoten bleibt gedrungen, die Spitze wird lang und schmal. Am "
     "deutlichsten Zwerg, am wenigsten Blume."),
    ("bommel", "Mit Bommel",
     dict(anzahl=4, y1=100.0, faecher=74.0, zipfel=1.25, bommel=9.5),
     "Der Zipfel endet in einem geschlossenen Bommel. Der Punkt gibt dem "
     "Zeichen oben ein Gewicht und einen Abschluss."),
]


# ----------------------------------------------------------------- Blatt ---

def _kasten(svg, w, h, px):
    return f'<div style="width:{round(px * w / h)}px;height:{px}px">{svg}</div>'


def blatt(datei="tuerzwerg-schnurzwerg.html"):
    v = {k: zeichen(**kw) for k, _, kw, _ in VARIANTEN}
    karten = "".join(
        f'<figure class="karte"><div class="buehne">'
        f'{_kasten(*v[k], 330)}</div><figcaption><b>{name}</b>'
        f'<span>{note}</span></figcaption></figure>'
        for k, name, _, note in VARIANTEN)
    s, w, h = v["fuenf"]
    farben = "".join(
        f'<div class="paar"><div class="pfeld" style="color:{hx}">'
        f'{_kasten(s, w, h, 120)}</div><span>{nm}</span></div>'
        for nm, hx in FARBEN)
    klein = "".join(
        f'<div class="mireihe"><b>{name}</b>'
        + "".join(f'<div class="mini"><div class="mibox">'
                  f'{_kasten(*v[k], px)}</div><span>{px}</span></div>'
                  for px in (16, 24, 32, 48)) + '</div>'
        for k, name, _, _ in VARIANTEN)
    zu = zeichen(offen=False)
    zwei = ('<div class="zf" style="--reif:#55886B;--hut:#D2452B">'
            + _kasten(s, w, h, 230) + '</div>'
            '<div class="zf" style="--reif:#454A52;--hut:#E0982F">'
            + _kasten(s, w, h, 230) + '</div>'
            '<div class="zf" style="--reif:#38689B;--hut:#38689B">'
            + _kasten(s, w, h, 230) + '</div>')
    open(datei, "w", encoding="utf-8").write(
        HTML.replace("__KARTEN__", karten).replace("__FARBEN__", farben)
            .replace("__KLEIN__", klein).replace("__ZWEI__", zwei)
            .replace("__OFFEN__", _kasten(s, w, h, 250))
            .replace("__ZU__", _kasten(*zu, 250)))
    return datei


HTML = r"""<title>Schnurzwerg</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@400;600&display=swap">
<style>
:root{--papier:#FBFAF7;--grund:#F2F4F1;--linie:#E2DFD5;--leise:#6C675A;
--tinte:#17160F;--akz:#55886B}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--papier:#1B1F1C;--grund:#131614;--linie:#333C35;--leise:#9AA69A;
--tinte:#E8EBE7;--akz:#7FB183}}
:root[data-theme="dark"]{--papier:#1B1F1C;--grund:#131614;--linie:#333C35;
--leise:#9AA69A;--tinte:#E8EBE7;--akz:#7FB183}
*{box-sizing:border-box}
body{margin:0;background:var(--grund);color:var(--tinte);
font-family:Figtree,-apple-system,"Segoe UI",sans-serif;font-size:16px;
line-height:1.6}
.blatt{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:0 80px}
h1,h2{font-family:"Bricolage Grotesque",Figtree,sans-serif;font-weight:800;
letter-spacing:-.03em;margin:0}
h1{font-size:clamp(36px,7vw,58px);line-height:1}
h2{font-size:22px;margin-top:64px}
.eyebrow{font-family:ui-monospace,monospace;font-size:11.5px;letter-spacing:.16em;
text-transform:uppercase;color:var(--akz);margin:56px 0 14px}
.lead{margin:16px 0 0;color:var(--leise);max-width:64ch;font-size:16.5px}
.sub{margin:8px 0 20px;color:var(--leise);font-size:14px;max-width:68ch}
.reihe{display:grid;grid-template-columns:repeat(auto-fit,minmax(186px,1fr));
gap:16px;margin-top:26px}
.karte{margin:0;background:var(--papier);border:1px solid var(--linie);
border-radius:4px;overflow:hidden}
.buehne{height:356px;display:flex;align-items:center;justify-content:center;
padding:22px;color:var(--akz)}
figcaption{padding:0 16px 22px;text-align:center;display:flex;
flex-direction:column;gap:6px}
figcaption b{font-family:"Bricolage Grotesque",Figtree,sans-serif;
font-weight:800;font-size:17px;letter-spacing:-.02em}
figcaption span{font-size:12.5px;color:var(--leise);line-height:1.5}
.paare{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));
gap:14px}
.paar{display:flex;flex-direction:column;align-items:center;gap:9px}
.pfeld{width:100%;aspect-ratio:1;background:var(--papier);
border:1px solid var(--linie);border-radius:4px;display:flex;
align-items:center;justify-content:center}
.paar span{font-size:12px;color:var(--leise)}
.zwei{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
gap:16px;margin-top:24px}
.zwei>div{background:var(--papier);border:1px solid var(--linie);
border-radius:4px;padding:26px;display:flex;flex-direction:column;
align-items:center;gap:14px;color:var(--akz)}
.zwei p{margin:0;font-size:12.5px;color:var(--leise);text-align:center;
max-width:32ch}
.zf .reif{stroke:var(--reif)}
.zf .hut{stroke:var(--hut)}
.mireihe{display:flex;align-items:flex-end;gap:18px;padding:12px 0;
border-bottom:1px solid var(--linie);flex-wrap:wrap;color:var(--tinte)}
.mireihe b{width:140px;font-size:13px;font-weight:600}
.mini{display:flex;flex-direction:column;align-items:center;gap:5px}
.mibox{height:52px;display:flex;align-items:flex-end}
.mini span{font-family:ui-monospace,monospace;font-size:9.5px;color:var(--leise)}
.regel{border-left:3px solid var(--akz);padding-left:18px;margin-top:30px;
max-width:68ch}
.regel p{margin:0;font-size:14px;color:var(--leise)}
.regel p+p{margin-top:12px}
code{font-family:ui-monospace,monospace;font-size:.9em;background:var(--grund);
padding:1px 5px;border-radius:3px}
</style>

<div class="blatt">
<p class="eyebrow">Türzwerg · Zeichen</p>
<h1>Schnurzwerg</h1>
<p class="lead">Ein offener Reif, ein flacher Bogen als Krempe, darauf eine
Mütze aus Schlaufen, die sich zur Spitze zufächern. Gleichbleibende Stärke,
runde Enden, kein Knick.</p>

<h2>Fünf Fassungen</h2>
<p class="sub">Die Schlaufen zeigen <b>aus</b> der Achse heraus, nicht um sie
herum — jede geht hinaus, kehrt um und kommt zurück, wie die Schlaufen einer
Schleife. Das ist der Unterschied zwischen Knoten und Sprungfeder: eine
Spirale umrundet ihre Achse und liest als Draht. Weil die Blätter sich nach
oben zufächern, entsteht die Dreiecksform der Mütze von selbst — es ist keine
Kontur gezeichnet.</p>
<div class="reihe">
__KARTEN__
</div>

<h2>Reif offen oder geschlossen</h2>
<p class="sub">Offen zeigen die beiden Enden nach oben, der Krempe entgegen —
das ist der Reif als Produkt, mit der Durchführung für die Schnur. Geschlossen
ist ruhiger und hält kleine Größen besser.</p>
<div class="zwei">
<div>__OFFEN__<p>Offen. Zeigt das Bauteil, wirkt leichter.</p></div>
<div>__ZU__<p>Geschlossen. Ruhiger, robuster im Kleinen.</p></div>
</div>

<h2>Zweifarbig</h2>
<p class="sub">Weil Reif und Mütze zwei getrennte Linien sind, geht auch die
Fassung, die Sie sich gewünscht hatten: Reif in der einen, Mütze in der
anderen Produktfarbe. Rechts steht zum Vergleich die einfarbige.</p>
<div class="zwei">__ZWEI__</div>

<h2>In den Produktfarben</h2>
<p class="sub">Einfarbig bleibt der Normalfall — so steht es im Markenkern.</p>
<div class="paare">__FARBEN__</div>

<h2>Kleinstgrößen</h2>
<p class="sub">16, 24, 32 und 48 Pixel — und hier die unangenehme Wahrheit:
ein Knoten hat nach unten eine Grenze. Ab 48 px sitzt jede Fassung. Bei 32 px
trägt „Vier Schlaufen“ am saubersten, die dichteren verlieren die Windungen.
Bei 24 px bleibt nur die Silhouette, bei 16 px Matsch. Das ist kein Mangel
dieser Zeichnung, sondern der Preis des Motivs.</p>
<div>__KLEIN__</div>

<div class="regel"><p><b>Konsequenz für die Anwendung:</b> zwei Größenstufen.
Ab Etikettgröße das ganze Zeichen; für Favicon, Prägung und Nähetikett der
<b>Reif allein</b> — die echte Produktkontur, die <code>logo_kontur.py</code>
ohnehin schon ausgibt. Der Reif ist bei 16 px eindeutig, und weil er aus
demselben Bauteil stammt, ist es dieselbe Marke und kein zweites Logo.</p>
<p><b>Was diese Fassung gegenüber der letzten löst:</b> die Schlaufen laufen
nicht mehr um eine Achse, sondern aus ihr heraus — damit ist die Sprungfeder
weg. Die Krempe liegt breiter auf als der Reif, damit schnürt sich die
Silhouette nicht mehr ein und das Zeichen liest nicht mehr als Schlinge. Und
weil Reif und Mütze getrennte Linien sind, ist die zweifarbige Fassung
möglich.</p></div>
</div>"""


if __name__ == "__main__":
    d = blatt()
    print(f"geschrieben: {d}")
    for k, name, kw, _ in VARIANTEN:
        s, w, h = zeichen(**kw)
        print(f"  {name:<18}{w:5.0f} x {h:5.0f} mm   1:{h / w:.2f}   "
              f"{len(s):5d} Zeichen")
    print(f"  Strich {STRICH} bei Reif Ø{2 * R:.0f} "
          f"= {STRICH / (2 * R) * 100:.1f} Prozent")
