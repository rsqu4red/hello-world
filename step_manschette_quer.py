#!/usr/bin/env python3
"""
Türzwerg – die Manschette mit Quertasche als STEP

Gleiche Bauweise wie step_manschette.py: die Aussenhaut wird aus dem
Feld abgetastet, weil die weiche Vereinigung von Rohr und Kiel kein
CAD-Radius ist. Bohrung, Quertasche und Schnurloch sind analytisch.

Die Quertasche ist hier ein Quader mit vier verrundeten Laengskanten,
quer durch den Kiel. Im STEP stehen dafuer ebene Flaechen und
Zylinderflaechen - also genau das, was ein Werkzeugbauer als Zapfen
nachbaut.

    python3 step_manschette_quer.py
"""

import math

import cadquery as cq

import manschette_quertasche as Q
from manschette import D_SCHNUR, EINLAUF, KANTE, LAENGE, R_INNEN
from step_manschette import _kennung, _schale, netzpunkte, volumen

DATEI = "tuerzwerg-manschette-quertasche.step"


def ziel(z):
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    if wz <= 0.0:
        return 0.0
    wz = min(wz, KANTE)
    return math.sqrt(max(KANTE ** 2 - wz * wz, 0.0)) - KANTE


def kontur_draht(z, n=128, roh_n=720, rmax=34.0, schritt=0.1):
    """Die Aussenkontur bei der Hoehe z.

    Gesucht wird die AEUSSERSTE Nullstelle, nicht irgendeine: von
    aussen nach innen tasten, bis das Feld negativ wird, und erst dann
    halbieren. Eine Halbierung ueber das ganze Intervall setzt voraus,
    dass es genau einen Vorzeichenwechsel gibt - das gilt nur, solange
    der Querschnitt streng sternfoermig ist. Bei schlankem Kiel ist er
    das nicht mehr zuverlaessig, und die Halbierung landet dann still
    auf der falschen Flanke.
    """
    t = ziel(z)
    pts = []
    for i in range(roh_n):
        w = 2.0 * math.pi * i / roh_n
        dx, dy = math.cos(w), math.sin(w)
        hi = rmax
        while hi > schritt and Q.profil(dx * hi, dy * hi, z) - t >= 0.0:
            hi -= schritt
        # hi ist der erste Schritt INNERHALB - die Grenze liegt also
        # zwischen hi und hi + schritt, nicht davor. Das eine Feld
        # daneben kostete konstant bis zu einen Tastschritt, und zwar
        # unabhaengig von der Punktzahl: kein Verfeinern half.
        lo = hi
        hi = lo + schritt
        for _ in range(60):
            mi = 0.5 * (lo + hi)
            if Q.profil(dx * mi, dy * mi, z) - t < 0.0:
                lo = mi
            else:
                hi = mi
        pts.append((dx * lo, dy * lo))
    return cq.Wire.assembleEdges(
        [cq.Edge.makeSpline([cq.Vector(x, y, z) for x, y in
                             _nach_bogenlaenge(pts, n)], periodic=True)])


def _nach_bogenlaenge(roh, n):
    """Gleichmaessig nach Bogenlaenge umverteilen.

    Gleiche Winkelschritte vom Mittelpunkt aus verteilen die Punkte
    schlecht, sobald das Bauteil deutlich hoeher als breit ist: auf dem
    Kiel, der 35 mm tief haengt, landen dann kaum welche, und am Hals
    zwischen Rohr und Kiel schneidet die Kurve die Ecke ab. Nach
    Bogenlaenge verteilt sitzen sie dort, wo die Kontur etwas tut.
    """
    m = len(roh)
    s = [0.0]
    for i in range(m):
        a, b = roh[i], roh[(i + 1) % m]
        s.append(s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    ges = s[-1]
    aus = []
    j = 0
    for i in range(n):
        ziel_s = ges * i / n
        while s[j + 1] < ziel_s:
            j += 1
        t = (ziel_s - s[j]) / max(s[j + 1] - s[j], 1e-12)
        a, b = roh[j], roh[(j + 1) % m]
        aus.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return aus


def hoehen():
    from manschette import ABFLACHUNG
    z = [KANTE * (1.0 - math.cos(math.pi / 2.0 * i / 8)) for i in range(9)]
    z += [KANTE + (ABFLACHUNG - KANTE) * i / 16 for i in range(1, 17)]
    z += [ABFLACHUNG + (LAENGE / 2.0 - ABFLACHUNG) * i / 8 for i in range(1, 9)]
    return z + [LAENGE - v for v in reversed(z[:-1])]


def bohrung():
    ue = 1.0
    k = cq.Solid.makeCylinder(R_INNEN, LAENGE + 2 * ue,
                              cq.Vector(0, 0, -ue), cq.Vector(0, 0, 1))
    for z0, ri in ((EINLAUF, -1.0), (LAENGE - EINLAUF, 1.0)):
        k = k.fuse(cq.Solid.makeCone(
            R_INNEN, R_INNEN + EINLAUF + ue, EINLAUF + ue,
            cq.Vector(0, 0, z0), cq.Vector(0, 0, ri)))
    return k


def quertasche():
    """Quader quer durch den Kiel, vier Laengskanten verrundet."""
    ue = 2.0
    b = Q.R_KIEL + ue
    kasten = cq.Solid.makeBox(
        2 * b, Q.TASCHE_HOCH, Q.TASCHE_LANG,
        cq.Vector(-b, Q.TASCHE_UNTEN, LAENGE / 2.0 - Q.TASCHE_LANG / 2.0))
    laengs = [e for e in kasten.Edges()
              if abs(abs(e.tangentAt(0.5).x) - 1.0) < 1e-6]
    return kasten.fillet(Q.TASCHE_ECK, laengs)


def schnurbohrung():
    ue, r = 1.0, D_SCHNUR / 2.0
    y_aus = -Q.KIEL_UNTEN
    k = cq.Solid.makeCylinder(
        r, (Q.TASCHE_UNTEN + ue) - (y_aus - ue),
        cq.Vector(0, y_aus - ue, LAENGE / 2.0), cq.Vector(0, 1, 0))
    if Q.SCHNUR_SENK > 1e-6:
        k = k.fuse(cq.Solid.makeCone(
            r, r + Q.SCHNUR_SENK + ue, Q.SCHNUR_SENK + ue,
            cq.Vector(0, y_aus + Q.SCHNUR_SENK, LAENGE / 2.0),
            cq.Vector(0, -1, 0)))
    return k


def baue(datei=DATEI):
    print("Aussenhaut ...", flush=True)
    koerper = _schale([kontur_draht(z) for z in hoehen()])
    roh = koerper
    print("Bohrung ...", flush=True)
    koerper = koerper.cut(bohrung())
    print("Quertasche ...", flush=True)
    vorher = set(_kennung(e) for e in koerper.Edges())
    koerper = koerper.cut(quertasche())
    neu = [e for e in koerper.Edges() if _kennung(e) not in vorher]
    print(f"Verrundung 0.8 mm an {len(neu)} Kanten ...", flush=True)
    try:
        koerper = koerper.fillet(0.8, neu)
        ver = True
    except Exception:                                 # noqa: BLE001
        try:
            lang = [e for e in neu if e.Length() > 6.0]
            koerper = koerper.fillet(0.8, lang)
            ver = True
            print(f"  nur die {len(lang)} langen Kanten")
        except Exception as e:                        # noqa: BLE001
            print(f"  fehlgeschlagen ({type(e).__name__})"); ver = False
    print("Schnurloch ...", flush=True)
    koerper = koerper.cut(schnurbohrung())
    cq.exporters.export(cq.Workplane(obj=koerper), datei, exportType="STEP")
    return koerper, roh, ver


if __name__ == "__main__":
    shape, roh, ver = baue()
    bb = shape.BoundingBox()
    w = sorted(abs(Q.aussenfeld(*p)) for p in netzpunkte(roh, 0.02, 0.2))
    print(f"\ngeschrieben: {DATEI}")
    print(f"  Huellquader    {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
    print(f"  Volumen        {volumen(shape)/1000:.3f} cm^3")
    print(f"  Topologie      {len(shape.Faces())} Flaechen, "
          f"{len(shape.Edges())} Kanten, {len(shape.Solids())} Solid, "
          f"gueltig={shape.isValid()}")
    print(f"  Aussenhaut     hoechstens {w[-1]*1000:.1f} um vom Feld, "
          f"im Mittel {sum(w)/len(w)*1000:.2f} um")
    print(f"  Verrundung     {'gesetzt' if ver else 'NICHT gesetzt'}")
    print(f"  Quertasche     {Q.TASCHE_LANG:.0f} x {Q.TASCHE_HOCH:.1f} mm, "
          f"Eckradius {Q.TASCHE_ECK:.1f}, quer durch")
    print(f"  Knotenraum     {Q.knotenfreiraum():.1f} mm, unabhaengig vom "
          f"Druecker")
