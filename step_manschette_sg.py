#!/usr/bin/env python3
"""
Türzwerg – die spritzgussgerechte Manschette als STEP

Baut dieselbe Geometrie wie manschette_spritzguss.py, nur als B-Rep:
Aussenhaut aus dem Feld abgetastet (die weiche Vereinigung Rohr/Rippe
laesst sich nicht als CAD-Radius schreiben, siehe step_manschette.py),
Bohrung, Kanal und Schnurloch analytisch.

Der Kanal ist hier ein Loft aus genau zwei Querschnitten. Das ist nicht
Sparsamkeit, sondern exakt: die Entformschraege ist linear, die
Eckradien bleiben gleich, und ein geradliniger Loft zwischen zwei
Rundrechtecken gleichen Radius ergibt an jeder Zwischenstelle wieder ein
Rundrechteck.

    python3 step_manschette_sg.py
"""

import math

import cadquery as cq

import manschette_spritzguss as SP
from manschette import D_INNEN, D_SCHNUR, ECK_KAMMER, EINLAUF, LAENGE, R_INNEN
from step_manschette import _kennung, _schale, netzpunkte, volumen

KONTURPUNKTE = 96
DATEI = "tuerzwerg-manschette-spritzguss.step"


def ziel(z):
    from manschette import KANTE
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    if wz <= 0.0:
        return 0.0
    wz = min(wz, KANTE)
    return math.sqrt(max(KANTE ** 2 - wz * wz, 0.0)) - KANTE


def kontur_draht(z, n=KONTURPUNKTE, rmax=30.0):
    t = ziel(z)
    pts = []
    for i in range(n):
        w = 2.0 * math.pi * i / n
        dx, dy = math.cos(w), math.sin(w)
        lo, hi = 0.0, rmax
        for _ in range(64):
            mi = 0.5 * (lo + hi)
            if SP.profil(dx * mi, dy * mi, z) - t < 0.0:
                lo = mi
            else:
                hi = mi
        pts.append(cq.Vector(dx * lo, dy * lo, z))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def kanal_draht(z, ueber=0.0):
    """Der Kanalquerschnitt: unten mit ECK_KAMMER verrundet, oben offen
    bis zur Bohrungsachse."""
    a = SP.kanal_halbbreite(z) + ueber
    yu, yo = -(SP.KANAL_ACHSE + SP.D_KAMMER / 2.0), 2.0
    k = ECK_KAMMER
    e = cq.Plane(origin=(0, 0, z), xDir=(1, 0, 0), normal=(0, 0, 1))
    m = math.sqrt(0.5)
    w = (cq.Workplane(e).moveTo(a, yo).lineTo(a, yu + k)
         .threePointArc((a - k + k * m, yu + k - k * m), (a - k, yu))
         .lineTo(-(a - k), yu)
         .threePointArc((-(a - k) - k * m, yu + k - k * m), (-a, yu + k))
         .lineTo(-a, yo).close())
    return w.wire().val()


def kanal():
    ue = 1.0
    return cq.Solid.makeLoft([kanal_draht(-ue), kanal_draht(LAENGE + ue)],
                             ruled=True)


def bohrung():
    ue = 1.0
    k = cq.Solid.makeCylinder(R_INNEN, LAENGE + 2 * ue,
                              cq.Vector(0, 0, -ue), cq.Vector(0, 0, 1))
    for z0, ri in ((EINLAUF, -1.0), (LAENGE - EINLAUF, 1.0)):
        k = k.fuse(cq.Solid.makeCone(
            R_INNEN, R_INNEN + EINLAUF + ue, EINLAUF + ue,
            cq.Vector(0, 0, z0), cq.Vector(0, 0, ri)))
    return k


def schnurbohrung():
    ue, r = 1.0, D_SCHNUR / 2.0
    y_aus = -SP.RIPPE_UNTEN
    k = cq.Solid.makeCylinder(
        r, (-SP.KANAL_ACHSE + ue) - (y_aus - ue),
        cq.Vector(0, y_aus - ue, LAENGE / 2.0), cq.Vector(0, 1, 0))
    if SP.SCHNUR_SENK > 1e-6:
        k = k.fuse(cq.Solid.makeCone(
            r, r + SP.SCHNUR_SENK + ue, SP.SCHNUR_SENK + ue,
            cq.Vector(0, y_aus + SP.SCHNUR_SENK, LAENGE / 2.0),
            cq.Vector(0, -1, 0)))
    return k


def baue(datei=DATEI):
    print("Aussenhaut ...", flush=True)
    koerper = _schale([kontur_draht(z) for z in SP_hoehen()])
    roh = koerper
    print("Bohrung ...", flush=True)
    koerper = koerper.cut(bohrung())
    print("Kanal ...", flush=True)
    vorher = set(_kennung(e) for e in koerper.Edges())
    koerper = koerper.cut(kanal())
    # Verrundet werden die durchlaufenden Kanten, an denen der Kanal in
    # die Bohrung bricht - dort traegt der Knoten, und dort faengt bei
    # Silikon ein Riss an. Die kurzen Kanten an den Stirnflaechen bleiben
    # scharf: OCC bringt alle 28 nicht in einem Zug, und an der
    # Stirnflaeche faehrt der Kern ohnehin heraus, eine Kante dort ist
    # weder Kerbe noch Hindernis.
    neu = [e for e in koerper.Edges() if _kennung(e) not in vorher]
    lang = [e for e in neu if e.Length() > 10.0]
    print(f"Verrundung 0.8 mm an {len(lang)} von {len(neu)} Kanten ...",
          flush=True)
    try:
        koerper = koerper.fillet(0.8, lang)
        ver = True
    except Exception as e:                            # noqa: BLE001
        print(f"  fehlgeschlagen ({type(e).__name__})"); ver = False
    print("Schnurloch ...", flush=True)
    koerper = koerper.cut(schnurbohrung())
    cq.exporters.export(cq.Workplane(obj=koerper), datei, exportType="STEP")
    return koerper, roh, ver


def SP_hoehen():
    from manschette import ABFLACHUNG, KANTE
    z = [KANTE * (1.0 - math.cos(math.pi / 2.0 * i / 8)) for i in range(9)]
    z += [KANTE + (ABFLACHUNG - KANTE) * i / 16 for i in range(1, 17)]
    z += [ABFLACHUNG + (LAENGE / 2.0 - ABFLACHUNG) * i / 8 for i in range(1, 9)]
    return z + [LAENGE - v for v in reversed(z[:-1])]


if __name__ == "__main__":
    shape, roh, ver = baue()
    bb = shape.BoundingBox()
    w = sorted(abs(SP.aussenfeld(*p)) for p in netzpunkte(roh, 0.02, 0.2))
    print(f"\ngeschrieben: {DATEI}")
    print(f"  Huellquader    {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
    print(f"  Volumen        {volumen(shape)/1000:.3f} cm^3")
    print(f"  Topologie      {len(shape.Faces())} Flaechen, "
          f"{len(shape.Edges())} Kanten, {len(shape.Solids())} Solid, "
          f"gueltig={shape.isValid()}")
    print(f"  Aussenflaeche  hoechstens {w[-1]*1000:.1f} um vom Feld, "
          f"im Mittel {sum(w)/len(w)*1000:.2f} um")
    print(f"  Kanal          {2*SP.kanal_halbbreite(0):.2f} mm bei z=0, "
          f"{2*SP.kanal_halbbreite(LAENGE):.2f} mm bei z={LAENGE:.0f}, "
          f"Kern zieht zu z=0")
    print(f"  Knotenfreiraum {SP.knotenfreiraum(20.0):.1f} mm unter Ø20 "
          f"(heute 6,5)")
    print(f"  Verrundung     {'gesetzt' if ver else 'NICHT gesetzt'}")
