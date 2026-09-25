#!/usr/bin/env python3
"""
Türzwerg – die Manschette mit Rundloch als STEP

Gleiche Bauweise wie die anderen: die Aussenhaut wird aus dem Feld
abgetastet, weil die weiche Vereinigung von Rohr und Kiel kein
CAD-Radius ist; alles uebrige analytisch.

Hier ist "alles uebrige" fast das ganze Teil - Bohrung, Ø10-Loch und
Ø4-Hals sind drei Zylinder und ein Kegel. Genau das ist der Punkt des
Entwurfs: was im STEP als schlichte Zylinderflaeche steht, ist im
Werkzeug ein gerader Stift.

    python3 step_manschette_rundloch.py
"""

import math

import cadquery as cq

import manschette_rundloch as RL
from manschette import D_SCHNUR, EINLAUF, KANTE, LAENGE, R_INNEN
from step_manschette import _kennung, _schale, netzpunkte, volumen
from step_manschette_quer import _nach_bogenlaenge, hoehen

DATEI = "tuerzwerg-manschette-rundloch.step"


def ziel(z):
    wz = abs(z - LAENGE / 2.0) - (LAENGE / 2.0 - KANTE)
    if wz <= 0.0:
        return 0.0
    wz = min(wz, KANTE)
    return math.sqrt(max(KANTE ** 2 - wz * wz, 0.0)) - KANTE


def kontur_draht(z, n=128, roh_n=720, rmax=34.0, schritt=0.1):
    """Aussenkontur bei der Hoehe z: aeusserste Nullstelle suchen, dann
    nach Bogenlaenge gleichmaessig verteilen."""
    t = ziel(z)
    roh = []
    for i in range(roh_n):
        w = 2.0 * math.pi * i / roh_n
        dx, dy = math.cos(w), math.sin(w)
        hi = rmax
        while hi > schritt and RL.profil(dx * hi, dy * hi, z) - t >= 0.0:
            hi -= schritt
        lo = hi
        hi = lo + schritt
        for _ in range(60):
            mi = 0.5 * (lo + hi)
            if RL.profil(dx * mi, dy * mi, z) - t < 0.0:
                lo = mi
            else:
                hi = mi
        roh.append((dx * lo, dy * lo))
    return cq.Wire.assembleEdges(
        [cq.Edge.makeSpline([cq.Vector(x, y, z)
                             for x, y in _nach_bogenlaenge(roh, n)],
                            periodic=True)])


def bohrung():
    ue = 1.0
    k = cq.Solid.makeCylinder(R_INNEN, LAENGE + 2 * ue,
                              cq.Vector(0, 0, -ue), cq.Vector(0, 0, 1))
    for z0, ri in ((EINLAUF, -1.0), (LAENGE - EINLAUF, 1.0)):
        k = k.fuse(cq.Solid.makeCone(
            R_INNEN, R_INNEN + EINLAUF + ue, EINLAUF + ue,
            cq.Vector(0, 0, z0), cq.Vector(0, 0, ri)))
    return k


def loch_gross():
    """Ø10, von der Stufe senkrecht nach oben durch die Decke hinaus."""
    ue = 2.0
    hoehe = (RL.R_AUSSEN + ue) - RL.Y_STUFE
    return cq.Solid.makeCylinder(
        RL.D_LOCH / 2.0, hoehe, cq.Vector(0, RL.Y_STUFE, LAENGE / 2.0),
        cq.Vector(0, 1, 0))


def loch_klein():
    """Ø4 von der Stufe nach unten, mit 45-Grad-Senkung am Austritt."""
    ue, r = 1.0, D_SCHNUR / 2.0
    y_aus = -RL.KIEL_UNTEN
    k = cq.Solid.makeCylinder(
        r, (RL.Y_STUFE + ue) - (y_aus - ue),
        cq.Vector(0, y_aus - ue, LAENGE / 2.0), cq.Vector(0, 1, 0))
    if RL.SCHNUR_SENK > 1e-6:
        k = k.fuse(cq.Solid.makeCone(
            r, r + RL.SCHNUR_SENK + ue, RL.SCHNUR_SENK + ue,
            cq.Vector(0, y_aus + RL.SCHNUR_SENK, LAENGE / 2.0),
            cq.Vector(0, -1, 0)))
    return k


def baue(datei=DATEI):
    print("Aussenhaut ...", flush=True)
    koerper = _schale([kontur_draht(z) for z in hoehen()])
    roh = koerper
    print("Bohrung ...", flush=True)
    koerper = koerper.cut(bohrung())
    print("Ø10-Loch ...", flush=True)
    vorher = set(_kennung(e) for e in koerper.Edges())
    koerper = koerper.cut(loch_gross())
    neu = [e for e in koerper.Edges() if _kennung(e) not in vorher]
    ver = False
    for menge, was in ((neu, f"alle {len(neu)}"),
                       ([e for e in neu if e.Length() > 8.0], "nur die langen")):
        if not menge:
            continue
        try:
            koerper = koerper.fillet(0.8, menge)
            print(f"Verrundung 0.8 mm: {was} Kanten", flush=True)
            ver = True
            break
        except Exception as e:                        # noqa: BLE001
            print(f"  {was}: {type(e).__name__}", flush=True)
    print("Ø4-Hals ...", flush=True)
    koerper = koerper.cut(loch_klein())
    cq.exporters.export(cq.Workplane(obj=koerper), datei, exportType="STEP")
    return koerper, roh, ver


if __name__ == "__main__":
    shape, roh, ver = baue()
    bb = shape.BoundingBox()
    w = sorted(abs(RL.aussenfeld(*p)) for p in netzpunkte(roh, 0.02, 0.2))
    print(f"\ngeschrieben: {DATEI}")
    print(f"  Huellquader    {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
    print(f"  Volumen        {volumen(shape)/1000:.3f} cm^3")
    print(f"  Topologie      {len(shape.Faces())} Flaechen, "
          f"{len(shape.Edges())} Kanten, {len(shape.Solids())} Solid, "
          f"gueltig={shape.isValid()}")
    print(f"  Aussenhaut     hoechstens {w[-1]*1000:.1f} um vom Feld, "
          f"im Mittel {sum(w)/len(w)*1000:.2f} um")
    print(f"  Verrundung     {'gesetzt' if ver else 'NICHT gesetzt'}")
    print(f"  Loch           Ø{RL.D_LOCH:.0f} von oben durch, Stufe bei "
          f"y = {RL.Y_STUFE:.1f}, Hals Ø{D_SCHNUR:.0f} auf "
          f"{RL.SCHNUR_HALS:.1f} mm")
    print(f"  Knotenraum     {RL.knotenfreiraum(20.0):.1f} mm unter Ø20")
