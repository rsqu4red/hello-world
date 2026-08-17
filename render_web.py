#!/usr/bin/env python3
"""Rendert Produktbilder fuer die Website – aus demselben Modell wie die STL.

Einheit ist durchgaengig Millimeter, damit sich der Griff massstabsgetreu
in eine Szene mit Tuer, Klinke und Schnur setzen laesst.
"""

import math
import sys

sys.path.insert(0, "/home/user/hello-world")
import griffe as G

ZIEL = ("/tmp/claude-0/-home-user-hello-world/"
        "7a0c3b0c-ca36-5270-9b6c-6fe37f9c8344/scratchpad/")

YAW = math.radians(30)
ELEV = math.radians(11)
LICHT = (-0.40, 0.74, 0.54)


def rot(p):
    x, y, z = p
    x1 = x * math.cos(YAW) - y * math.sin(YAW)
    y1 = x * math.sin(YAW) + y * math.cos(YAW)
    return (x1,
            y1 * math.cos(ELEV) + z * math.sin(ELEV),
            -y1 * math.sin(ELEV) + z * math.cos(ELEV))


def misch(farbe, f, weiss=0.0):
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(c * f + 255 * weiss))) for c in farbe)


def polygone(name, farbe, seg=44, dunkel=0.34):
    """Sichtbare Vierecke des Griffs, als (tiefe, punkte, farbe)."""
    v = G.VARIANTEN[name]
    profil, bohr, n_quer = v["profil"], v["bohr"], v["n_quer"]
    hoehe = profil.hoehe
    h_blend = min((p[0] for p in profil.punkte if p[0] > 0), default=1.0)

    def expo(h):
        if bohr.kopf != "kuppe":
            return n_quer
        return 2.0 + (n_quer - 2.0) * min(1.0, h / h_blend)

    alle = G.hoehenstufen(profil, bohr)
    hs = [h for i, h in enumerate(alle) if i % 2 == 0 or h < 3.0]
    aus, inn = [], []
    for h in hs:
        a, b = profil(h)
        r = bohr(h)
        z = hoehe - h
        aus.append([G.superellipse(a, b, expo(h), j, seg) + (z,) for j in range(seg)])
        inn.append([G.superellipse(r, r, 2.0, j, seg) + (z,) for j in range(seg)])

    roh = []
    for i in range(len(hs) - 1):
        for j in range(seg):
            k = (j + 1) % seg
            roh.append((aus[i][j], aus[i][k], aus[i + 1][k], aus[i + 1][j], 1.0))
            if hs[i] < hoehe * 0.30:
                roh.append((inn[i][k], inn[i][j], inn[i + 1][j], inn[i + 1][k], dunkel))

    fertig = []
    for q in roh:
        ecken, ton = q[:4], q[4]
        e1 = [ecken[1][i] - ecken[0][i] for i in range(3)]
        e2 = [ecken[2][i] - ecken[0][i] for i in range(3)]
        n = (e1[1] * e2[2] - e1[2] * e2[1],
             e1[2] * e2[0] - e1[0] * e2[2],
             e1[0] * e2[1] - e1[1] * e2[0])
        ln = math.sqrt(sum(c * c for c in n)) or 1.0
        nv = rot(tuple(c / ln for c in n))
        if nv[1] <= 0.01:
            continue
        d = max(0.0, sum(nv[i] * LICHT[i] for i in range(3)))
        f = (0.34 + 0.66 * (d ** 0.8)) * ton
        pq = [rot(p) for p in ecken]
        fertig.append((sum(p[1] for p in pq) / 4.0,
                       [(p[0], -p[2]) for p in pq],
                       misch(farbe, f)))
    fertig.sort(key=lambda t: t[0])
    return fertig


def als_svg(polys, dx, dy, skala=1.0):
    aus = []
    for _, punkte, col in polys:
        p = " ".join("%.2f,%.2f" % (x * skala + dx, y * skala + dy) for x, y in punkte)
        aus.append('<polygon points="%s" fill="%s"/>' % (p, col))
    return "\n".join(aus)


def grenzen(polys):
    xs = [x for _, pts, _ in polys for x, _ in pts]
    ys = [y for _, pts, _ in polys for _, y in pts]
    return min(xs), max(xs), min(ys), max(ys)


# ------------------------------------------------------------------ Szene ----

def hero():
    """Tuer, Klinke, Manschette, Schnur und Griff – massstabsgetreu in mm."""
    rot_ = (222, 74, 43)
    polys = polygone("drechsel", rot_, seg=48)
    x0, x1, y0, y1 = grenzen(polys)
    mitte_x, oben = 132.0, 300.0          # Kopf des Griffs auf dieser Hoehe
    griff = als_svg(polys, mitte_x - (x0 + x1) / 2, oben - y0)

    s = []
    s.append('<svg viewBox="0 0 300 430" role="img" aria-label="Der Tuerzwerg '
             'an einer Tuerklinke: Silikonmanschette auf dem Drucker, Schnur '
             'und gedrechselter Griff auf Kinderhoehe">')
    s.append('<defs><linearGradient id="tuer" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="var(--flaeche)"/>'
             '<stop offset="1" stop-color="var(--flaeche-2)"/></linearGradient></defs>')
    # Tuerblatt
    s.append('<rect x="150" y="-10" width="170" height="450" rx="6" fill="url(#tuer)"/>')
    s.append('<rect x="168" y="18" width="132" height="180" rx="4" fill="none" '
             'stroke="var(--kante)" stroke-width="1.4"/>')
    # Rosette und Druecker
    s.append('<circle cx="252" cy="62" r="21" fill="var(--metall)"/>')
    s.append('<circle cx="252" cy="62" r="21" fill="none" stroke="var(--metall-2)" stroke-width="1"/>')
    s.append('<path d="M96 51 H246 a11 11 0 0 1 0 22 H96 a11 11 0 0 1 0-22 Z" fill="var(--metall)"/>')
    s.append('<path d="M96 51 a11 11 0 0 0 0 22 h9 V51 Z" fill="var(--metall-2)"/>')
    # Manschette auf dem Druecker
    s.append('<path d="M112 44 h56 l-5 36 h-46 Z" fill="#DE4A2B"/>')
    s.append('<path d="M126 80 h28 l-3 15 h-22 Z" fill="#DE4A2B"/>')
    s.append('<circle cx="140" cy="88" r="3.4" fill="var(--flaeche)" opacity="0.85"/>')
    # Schnur, 220 mm
    s.append('<path d="M140 95 C 136 150, 145 220, 140 300" stroke="#EFE0C4" '
             'stroke-width="7" stroke-linecap="round" fill="none"/>')
    s.append('<path d="M140 95 C 136 150, 145 220, 140 300" stroke="#00000018" '
             'stroke-width="7" stroke-linecap="round" fill="none"/>')
    s.append(griff)
    s.append("</svg>")
    return "\n".join(s)


def einzelgriff(name, farbe, seg=40):
    polys = polygone(name, farbe, seg=seg)
    x0, x1, y0, y1 = grenzen(polys)
    rand = 4
    vb = "%.1f %.1f %.1f %.1f" % (x0 - rand, y0 - rand,
                                  x1 - x0 + 2 * rand, y1 - y0 + 2 * rand)
    return ('<svg viewBox="%s" role="img" aria-label="Griff">\n%s\n</svg>'
            % (vb, als_svg(polys, 0, 0)))


if __name__ == "__main__":
    dateien = {
        "web-hero.svg": hero(),
        "web-griff-rot.svg": einzelgriff("drechsel", (222, 74, 43)),
        "web-griff-gruen.svg": einzelgriff("drechsel", (62, 124, 89)),
        "web-griff-petrol.svg": einzelgriff("drechsel", (47, 110, 126)),
        "web-griff-honig.svg": einzelgriff("drechsel", (217, 161, 63)),
    }
    for name, inhalt in dateien.items():
        with open(ZIEL + name, "w") as f:
            f.write(inhalt)
        print("%-22s %5d KB" % (name, len(inhalt) // 1024))
