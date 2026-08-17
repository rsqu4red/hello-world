#!/usr/bin/env python3
"""Zeichnet die Produktbilder der Website als flache Vektorgrafik.

Die Kontur kommt aus demselben Profil wie die STL-Dateien, damit die
Proportionen stimmen – gezeichnet wird sie aber flach und einfarbig, im
selben Stil wie Tuer, Klinke und Manschette. Einheit ist durchgaengig
Millimeter.
"""

import sys

sys.path.insert(0, "/home/user/hello-world")
import griffe as G

ZIEL = ("/tmp/claude-0/-home-user-hello-world/"
        "7a0c3b0c-ca36-5270-9b6c-6fe37f9c8344/scratchpad/")

SCHRITT = 0.5           # Abtastung der Kontur in mm


def silhouette(name, dx=0.0, dy=0.0):
    """Aussenkontur als geschlossener Pfad. Rueckgabe: (pfad, breite, hoehe).

    Das Teil ist ein Drehkoerper, die Vorderansicht also einfach die
    Halbbreite nach beiden Seiten gespiegelt.
    """
    profil = G.VARIANTEN[name]["profil"]
    hoehe = profil.hoehe
    stufen = sorted({round(i * SCHRITT, 3) for i in range(int(hoehe / SCHRITT) + 1)}
                    | {round(h, 3) for h in profil.knicke} | {hoehe})
    stufen = [h for h in stufen if 0.0 <= h <= hoehe]

    rechts = [(profil(h)[0], h) for h in stufen]
    links = [(-a, h) for a, h in reversed(rechts)]
    punkte = rechts + links

    d = "M " + " L ".join("%.2f %.2f" % (x + dx, y + dy) for x, y in punkte) + " Z"
    breite = max(a for a, _ in rechts) * 2
    return d, breite, hoehe


# ------------------------------------------------------------------ Szene ----

def hero():
    """Tuer, Klinke, Manschette, Schnur und Griff – flach und massstabsgetreu."""
    pfad, breite, hoehe = silhouette("drechsel", dx=132.0, dy=300.0)

    s = []
    s.append('<svg viewBox="0 0 300 430" role="img" aria-label="Der Tuerzwerg '
             'an einer Tuerklinke: Silikonmanschette auf dem Druecker, Schnur '
             'und Griff auf Kinderhoehe">')
    # Tuerblatt
    s.append('<rect x="150" y="-10" width="170" height="450" rx="6" fill="var(--flaeche-2)"/>')
    s.append('<rect x="168" y="18" width="132" height="180" rx="4" fill="none" '
             'stroke="var(--kante)" stroke-width="1.4"/>')
    # Rosette und Druecker
    s.append('<circle cx="252" cy="62" r="21" fill="var(--metall)"/>')
    s.append('<path d="M96 51 H246 a11 11 0 0 1 0 22 H96 a11 11 0 0 1 0-22 Z" '
             'fill="var(--metall)"/>')
    s.append('<path d="M96 51 a11 11 0 0 0 0 22 h9 V51 Z" fill="var(--metall-2)"/>')
    # Manschette auf dem Druecker
    s.append('<path d="M112 44 h56 l-5 36 h-46 Z" fill="var(--akzent)"/>')
    s.append('<path d="M126 80 h28 l-3 15 h-22 Z" fill="var(--akzent)"/>')
    # Schnur, 220 mm
    s.append('<path d="M140 92 C 136 150, 145 220, 140 300" stroke="var(--schnur)" '
             'stroke-width="6" stroke-linecap="round" fill="none"/>')
    # Griff
    s.append('<path d="%s" fill="var(--akzent)"/>' % pfad)
    s.append("</svg>")
    return "\n".join(s)


def einzelgriff(name="drechsel"):
    """Der Griff allein, freigestellt – Farbe kommt per CSS von aussen."""
    pfad, breite, hoehe = silhouette(name)
    rand = 3
    vb = "%.1f %.1f %.1f %.1f" % (-breite / 2 - rand, -rand,
                                  breite + 2 * rand, hoehe + 2 * rand)
    return ('<svg viewBox="%s" role="img" aria-label="Griff in der Seitenansicht">'
            '<path d="%s" fill="currentColor"/></svg>' % (vb, pfad))


if __name__ == "__main__":
    dateien = {
        "web-hero.svg": hero(),
        "web-griff.svg": einzelgriff(),
    }
    for name, inhalt in dateien.items():
        with open(ZIEL + name, "w") as f:
            f.write(inhalt)
        print("%-18s %6.1f KB" % (name, len(inhalt) / 1024))

    _, b, h = silhouette("drechsel")
    print("Griffkontur: %.1f x %.1f mm" % (b, h))
