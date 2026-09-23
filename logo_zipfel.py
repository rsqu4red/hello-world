#!/usr/bin/env python3
"""
Türzwerg – das Zipfel-Zeichen

Reif und Muetze als zwei Formen, die sich tangential beruehren, dazu die
Schnur in mehreren Fuehrungen.

Die Konstruktion
----------------

Von einer Spitze P ausserhalb des Reifs gibt es genau zwei Tangenten an
den Kreis. Ihre Beruehrpunkte liegen bei

    phi0 = atan2(Py, Px),   delta = acos(R / |P|)
    T = R * (cos(phi0 -+ delta), sin(phi0 -+ delta))

Setzen die Muetzenkanten dort an, geht die Gerade knickfrei in die
Rundung ueber - an keiner Stelle eine Ecke. Das war der Einwand an der
ersten Fassung: dort stand die Muetze ueber den Reif hinaus und
hinterliess unten zwei Absaetze.

Liegt P seitlich (34, -88) statt mittig, kippt die Muetze zum Zipfel,
ohne dass die Tangentenbedingung verlorengeht. Das ist der billigste Weg
zu einem unverwechselbaren Umriss: die Spitze rueckt zur Seite, sonst
aendert sich nichts - und es ist das, was eine Zipfelmuetze tut.

Die Schnur
----------

Gerade nach oben ist richtig und langweilig. Eine Schnur haengt nie
gerade: sie hat Durchhang, sie schwingt, sie legt sich in Schlaufen.
Die Fuehrungen hier sind Bezierkurven, die an der Muetzenspitze
tangential ansetzen - der Uebergang von Muetze zu Schnur ist damit so
knickfrei wie der von Muetze zu Reif. Strichstaerke Ø4 am Ø72-Reif, also
massstaeblich dieselbe Schnur, die durch das Bauteil laeuft.

Zwei Farben
-----------

Muetze und Reif sind getrennte Pfade, nicht eine Silhouette. Die Muetze
ist das Dreieck T_a - P - T_b, unten geschlossen durch den kurzen
Kreisbogen ueber den Scheitel; der Reif ist der volle Kreis mit der
Oeffnung als Aussparung. Sie ueberlappen nur auf diesem Bogen, und weil
er auf dem Kreis liegt, verlaeuft die Farbgrenze glatt.

Das weicht vom Markenkern ab, der "nie in zwei Farben" verlangt - auf
Wunsch und mit einem Preis: ein Farbwechsel im Shop faerbt nur noch die
Muetze um, nicht mehr das ganze Zeichen.

Der Reif kommt aus logo_kontur.json, also aus dem Bauteil - die Oeffnung
ist die wirkliche, kein Kreis.

    python3 logo_kontur.py && python3 logo_zipfel.py
"""

import json
import math

QUELLE = "logo_kontur.json"
DATEI = "tuerzwerg-zipfel.html"

R = 36.0                    # Reifradius aussen
D_SCHNUR = 4.0              # 5,6 Prozent der Reifbreite, wie am Bauteil
SPITZE = (34.0, -88.0)      # Zipfel
SPITZE_GERADE = (0.0, -96.1)

PAARE = [("Mohn auf Schiefer", "#D2452B", "#454A52"),
         ("Mohn auf Tinte", "#D2452B", "#17160F"),
         ("Sonne auf Schiefer", "#E0982F", "#454A52"),
         ("Salbei auf Tinte", "#55886B", "#17160F"),
         ("Himmel auf Schiefer", "#38689B", "#454A52")]

# Schnurfuehrungen ab der Muetzenspitze. Jede beginnt senkrecht nach oben,
# damit sie tangential aus der Spitze austritt.
SCHNUERE = [
    ("schwung", "Schwung", "-58 -176 116 220",
     "M34 -89C34 -112 12 -116 12 -138C12 -156 32 -160 32 -172",
     "Durchhang in eine Richtung, dann zurueck. So haengt eine Schnur wirklich."),
    ("schlaufe", "Schlaufe", "-58 -168 120 212",
     "M34 -89C34 -108 16 -112 16 -128C16 -146 46 -150 50 -132"
     "C53 -118 34 -114 27 -126",
     "Die Schnur legt sich in eine Schlaufe, wie sie ueber der Klinke haengt."),
    ("klinke", "Zur Klinke", "-76 -150 152 196",
     "M34 -89C34 -114 8 -128 -26 -128L-64 -128",
     "Der Bogen zeigt zur Tuer. Das Zeichen bekommt eine Richtung."),
    ("ringel", "Ringel", "-58 -164 116 208",
     "M34 -89C34 -110 22 -120 22 -134C22 -148 42 -150 44 -138"
     "C45 -130 36 -128 31 -134",
     "Eine Kringel am Ende - mehr Zwerg, weniger Technik."),
    ("welle", "Welle", "-58 -158 116 202",
     "M34 -89C34 -102 24 -106 24 -118C24 -130 40 -134 40 -146",
     "Nur angedeutet. Am ruhigsten, haelt am kleinsten."),
]


def _bogen(t0, t1, n=48):
    return "".join(
        f"L{R * math.cos(t0 + (t1 - t0) * i / n):.2f} "
        f"{R * math.sin(t0 + (t1 - t0) * i / n):.2f}" for i in range(1, n + 1))


def teile(px, py, innen):
    """Muetze und Reif als getrennte Pfade."""
    d = math.acos(R / math.hypot(px, py))
    f0 = math.atan2(py, px)
    ta, tb = f0 - d, f0 + d
    hut = (f"M{R * math.cos(ta):.2f} {R * math.sin(ta):.2f}"
           f"L{px:.2f} {py:.2f}"
           f"L{R * math.cos(tb):.2f} {R * math.sin(tb):.2f}{_bogen(tb, ta)}Z")
    kreis = "".join(("M" if i == 0 else "L")
                    + f"{R * math.cos(2 * math.pi * i / 96):.2f} "
                      f"{R * math.sin(2 * math.pi * i / 96):.2f}"
                    for i in range(96)) + "Z"
    return hut, kreis + innen, math.degrees(d)


def zeichen(hut, reif, viewbox, schnur=None):
    s = (f'<path d="{schnur}" fill="none" stroke="var(--a)" '
         f'stroke-width="{D_SCHNUR}" stroke-linecap="round"/>') if schnur else ""
    return (f'<svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{reif}" fill="var(--b)" fill-rule="evenodd"/>'
            f'<path d="{hut}" fill="var(--a)"/>{s}</svg>')


def siegel(hut, reif):
    return (f'<svg viewBox="-56 -56 112 112" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="-52" y="-52" width="104" height="104" rx="24" fill="var(--b)"/>'
            f'<g transform="translate(0 15.4) scale(0.629)">'
            f'<path d="{reif}" fill="#F2F4F1" fill-rule="evenodd"/>'
            f'<path d="{hut}" fill="var(--a)"/></g></svg>')


def baue():
    innen = json.load(open(QUELLE))["innen"]
    hut, reif, winkel = teile(*SPITZE, innen)
    hut_g, reif_g, _ = teile(*SPITZE_GERADE, innen)

    def masse(vb):
        _, _, w, h = (float(t) for t in vb.split())
        return w, h

    v = {"zipfel": (zeichen(hut, reif, "-44 -98 88 142"), 88, 142),
         "gerade": (zeichen(hut_g, reif_g, "-44 -106 88 150"), 88, 150),
         "siegel": (siegel(hut, reif), 112, 112)}
    for k, _, vb, d, _ in SCHNUERE:
        w, h = masse(vb)
        v[k] = (zeichen(hut, reif, vb, d), w, h)
    return v, winkel


# ------------------------------------------------------------------ Seite ----

def _stil(a, b):
    return f"--a:{a};--b:{b}"


def _karte(v, k, name, note, hoehe=250):
    svg, vw, vh = v[k]
    return (f'<figure class="karte"><div class="buehne" '
            f'style="{_stil("#D2452B", "#454A52")}">'
            f'<div style="width:{round(hoehe * vw / vh)}px;height:{hoehe}px">{svg}</div>'
            f'</div><figcaption><b>{name}</b><span>{note}</span></figcaption></figure>')


HTML = r"""<title>Zipfel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@400;600&display=swap">
<style>
:root{--papier:#FBFAF7;--grund:#F2F4F1;--linie:#E2DFD5;--leise:#6C675A;--tinte:#17160F;
--akz:#D2452B;--a:#D2452B;--b:#454A52}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--papier:#1B1F1C;--grund:#131614;--linie:#333C35;--leise:#9AA69A;--tinte:#E8EBE7;--akz:#E4674C}}
:root[data-theme="dark"]{--papier:#1B1F1C;--grund:#131614;--linie:#333C35;
--leise:#9AA69A;--tinte:#E8EBE7;--akz:#E4674C}
*{box-sizing:border-box}
body{margin:0;background:var(--grund);color:var(--tinte);
font-family:Figtree,-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.6}
.blatt{max-width:1100px;margin:0 auto;padding-inline:20px;padding-block:0 80px}
h1,h2{font-family:"Bricolage Grotesque",Figtree,sans-serif;font-weight:800;
letter-spacing:-.03em;margin:0}
h1{font-size:clamp(36px,7vw,58px);line-height:1}
h2{font-size:22px;margin-top:60px}
.eyebrow{font-family:ui-monospace,monospace;font-size:11.5px;letter-spacing:.16em;
text-transform:uppercase;color:var(--akz);margin:56px 0 14px}
.lead{margin:16px 0 0;color:var(--leise);max-width:62ch;font-size:16.5px}
.sub{margin:8px 0 20px;color:var(--leise);font-size:14px;max-width:64ch}
.reihe{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:16px;
margin-top:26px}
.karte{margin:0;background:var(--papier);border:1px solid var(--linie);border-radius:4px;
overflow:hidden}
.buehne{height:300px;display:flex;align-items:center;justify-content:center;padding:20px}
figcaption{padding:0 18px 20px;text-align:center;display:flex;flex-direction:column;gap:5px}
figcaption b{font-family:"Bricolage Grotesque",Figtree,sans-serif;font-weight:800;
font-size:18px;letter-spacing:-.02em}
figcaption span{font-size:12.5px;color:var(--leise);line-height:1.5}
.paare{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
.paar{display:flex;flex-direction:column;align-items:center;gap:9px}
.pfeld{width:100%;aspect-ratio:1;background:var(--papier);border:1px solid var(--linie);
border-radius:4px;display:flex;align-items:center;justify-content:center}
.paar span{font-size:12px;color:var(--leise)}
.mireihe{display:flex;align-items:flex-end;gap:18px;padding:12px 0;
border-bottom:1px solid var(--linie);flex-wrap:wrap}
.mireihe b{width:100px;font-size:13px;font-weight:600}
.mini{display:flex;flex-direction:column;align-items:center;gap:5px}
.mibox{height:52px;display:flex;align-items:flex-end}
.mini span{font-family:ui-monospace,monospace;font-size:9.5px;color:var(--leise)}
.regel{border-left:3px solid var(--akz);padding-left:18px;margin-top:26px;max-width:64ch}
.regel p{margin:0;font-size:14px;color:var(--leise)}
</style>

<div class="blatt">
<p class="eyebrow">Türzwerg · Zeichen</p>
<h1>Zipfel</h1>
<p class="lead">Reif und Mütze, zwei Farben, tangential verbunden. Die Mützenkanten
treffen den Reif ohne Knick — deshalb gibt es an keiner Stelle eine Ecke, und die
Silhouette bleibt eine.</p>

<h2>Die Schnur, fünf Führungen</h2>
<p class="sub">Eine Schnur hängt nie gerade. Alle setzen senkrecht an der Spitze an,
laufen also knickfrei aus der Mütze heraus.</p>
<div class="reihe">
__SCHNUERE__
</div>

<h2>Ohne Schnur</h2>
<p class="sub">Für Favicon, Prägung und alles, was klein wird.</p>
<div class="reihe">
__PUR__
</div>

<h2>Farbpaare</h2>
<p class="sub">Die Mütze trägt die Produktfarbe, der Reif bleibt ruhig.</p>
<div class="paare">__PAARE__</div>

<h2>Kleinstgrößen</h2>
<p class="sub">16, 24, 32 und 48 Pixel.</p>
<div>__KLEIN__</div>

<div class="regel"><p><b>Eine Abweichung, bewusst:</b> der Markenkern sagt
„nie in zwei Farben". Hier sind es zwei. Das gibt dem Zeichen die Trennung
zwischen Mütze und Reif, die es vorher nicht hatte — kostet aber die Regel,
dass ein Farbwechsel im Shop das ganze Zeichen umfärbt. Dann färbt nur noch
die Mütze mit.</p></div>
</div>"""


def schreibe(v, datei):
    schnuere = "".join(_karte(v, k, name, note)
                       for k, name, _, _, note in SCHNUERE)
    pur = (_karte(v, "zipfel", "Zipfel pur",
                  "Die Spitze sitzt seitlich. Das Merkmal, das auch bei 16 px bleibt.")
           + _karte(v, "gerade", "Gerade",
                    "Symmetrisch, zum Vergleich. Ruhiger, aber beliebiger.")
           + _karte(v, "siegel", "Siegel",
                    "Für App-Icon und Aufkleber. Reif ausgespart, Mütze farbig."))
    svg, vw, vh = v["zipfel"]
    paare = "".join(
        f'<div class="paar"><div class="pfeld" style="{_stil(a, b)}">'
        f'<div style="width:{round(118 * vw / vh)}px;height:118px">{svg}</div>'
        f'</div><span>{name}</span></div>' for name, a, b in PAARE)

    klein = ""
    for k, name in ([("zipfel", "Zipfel pur"), ("siegel", "Siegel")]
                    + [(k, n) for k, n, _, _, _ in SCHNUERE]):
        s, w, h = v[k]
        reihe = "".join(
            f'<div class="mini"><div class="mibox" '
            f'style="{_stil("#D2452B", "#454A52")}">'
            f'<div style="width:{round(px * w / h)}px;height:{px}px">{s}</div>'
            f'</div><span>{px}</span></div>' for px in (16, 24, 32, 48))
        klein += f'<div class="mireihe"><b>{name}</b>{reihe}</div>'

    open(datei, "w", encoding="utf-8").write(
        HTML.replace("__SCHNUERE__", schnuere)
            .replace("__PUR__", pur)
            .replace("__PAARE__", paare)
            .replace("__KLEIN__", klein))


if __name__ == "__main__":
    v, winkel = baue()
    schreibe(v, DATEI)
    print(f"geschrieben: {DATEI}")
    print(f"  Zipfelspitze  ({SPITZE[0]:.0f}, {SPITZE[1]:.0f})")
    print(f"  Tangenten     {winkel:.1f} Grad beidseits, knickfrei")
    print(f"  Schnur        Ø{D_SCHNUR:.0f} = "
          f"{D_SCHNUR / (2 * R) * 100:.1f} Prozent der Reifbreite")
    print(f"  Fuehrungen    {', '.join(n for _, n, _, _, _ in SCHNUERE)}")
    print(f"  Fassungen     {len(v)} insgesamt")
