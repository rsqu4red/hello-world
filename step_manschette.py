#!/usr/bin/env python3
"""
Türzwerg – die Klinkenmanschette als STEP ausgeben

Wie beim Reif wird nicht das Netz gewandelt, sondern der Koerper aus
derselben parametrischen Definition neu gebaut - hier aus manschette.py.
Ein aus 496 136 Dreiecken erzeugtes STEP waere formal gueltig und
praktisch unbrauchbar.

Der Unterschied zum Reif: hier geht der CAD-Weg nicht
------------------------------------------------------

Beim Reif liess sich der Querschnitt als Rundrechteck hinschreiben. Die
Manschette dagegen entsteht aus einer WEICHEN VEREINIGUNG von Rohr und
Rippe mit VERRUNDUNG = 4,0. Das ist kein Radius im CAD-Sinn, sondern
eine Mischfunktion, und sie traegt an der Kehle messbar mehr auf, als
eine echte Verrundung es taete:

    Winkel   weiche Vereinigung   scharf   Differenz
     130 Grad       12,564        12,000     +0,564
     140 Grad       13,848        13,144     +0,704

0,7 mm an einem Teil mit 3 mm Wand - wer das durch einen 4-mm-Radius
ersetzt, baut ein anderes Teil. Die Aussenkontur wird deshalb je Hoehe
aus dem Feld abgetastet (Bisektion entlang Strahlen vom Mittelpunkt; der
Querschnitt ist darum sternfoermig) und die Schnitte werden gelauft.

Was dagegen analytisch gebaut wird
-----------------------------------

Alles, was im Feld ohnehin exakt ist: die Ø18-Bohrung samt ihren
45-Grad-Einlaeufen, die Knotenkammer als gerundeter Quader mit
aufgesetztem Prisma, die Ø4-Schnurbohrung mit ihrer Senkung. Die werden
als Zylinder, Kegel und verrundete Quader gebaut und abgezogen - im
STEP stehen sie dann als echte Zylinder- und Kegelflaechen.

Zwei Eigenheiten der Aussenkontur
----------------------------------

Die Stirnkanten sind eine "gerundete Extrusion": das Profil wird um
KANTE geschrumpft, in z gekuerzt und der Koerper wieder aufgedickt. Die
Kontur an der Hoehe z ist daher nicht das Profil selbst, sondern das um
KANTE - sqrt(KANTE^2 - wz^2) nach innen versetzte. Direkt an der
Stirnflaeche ist das Feld ueber der ganzen Endflaeche null und eine
Bisektion liefe ins Leere; abgetastet wird deshalb gegen diesen
Zielwert statt gegen null.

Und die Abflachung zu den Enden hin (WAND auf WAND_ENDE ueber 7 mm)
betrifft nur das Rohr, nicht die Rippe - beides steckt im Profil und
kommt durch die Abtastung von selbst mit.

Bekannte Abweichung
-------------------

Die Knotenkammer wird im Feld mit weich_abziehen(..., 0.8) abgezogen.
Daraus wird hier eine echte Verrundung mit konstantem Radius 0,8 an
denselben Kanten - fertigbar und bemassbar, aber nicht auf den
Mikrometer dasselbe. Wo das zu Buche schlaegt, misst das Skript nach
und schreibt es hin, statt es zu verschweigen.

    python3 step_manschette.py
"""

import math

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
from OCP.BRepGProp import BRepGProp
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

import manschette as MA
from netz import weich_vereinen

JE_SCHALE = 8           # Schnitte je Teilschale; darueber gibt OCC auf
KONTURPUNKTE = 96       # Stuetzpunkte je Querschnitt
VERRUNDUNG_KAMMER = 0.8     # entspricht weich_abziehen(..., 0.8) im Feld
DATEI = "tuerzwerg-manschette.step"


# ------------------------------------------------------------- Werkzeug ---

def volumen(shape, eps=1e-6):
    """Volumen. Der Standardaufruf rechnet auf Spline-Flaechen zu grob."""
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, p, eps, True)
    return p.Mass()


def profil(x, y, z):
    """Der Querschnitt: Rohr und Rippe, weich vereinigt. Nur das Rohr
    wird zu den Enden hin abgeflacht, die Rippe behaelt ihre Wand."""
    return weich_vereinen(
        math.hypot(x, y) - (MA.R_AUSSEN - MA._ruecknahme(z)),
        math.hypot(x, y + MA.KAMMER_ACHSE) - MA.R_RIPPE, MA.VERRUNDUNG)


def ziel(z):
    """Wogegen bei der Hoehe z abgetastet wird.

    In der Mitte null - die Kontur ist das Profil. In den aeussersten
    KANTE Millimetern liegt die Kontur um KANTE - sqrt(KANTE^2 - wz^2)
    weiter innen; das ist der Viertelkreis der gerundeten Extrusion.
    """
    wz = abs(z - MA.LAENGE / 2.0) - (MA.LAENGE / 2.0 - MA.KANTE)
    if wz <= 0.0:
        return 0.0
    wz = min(wz, MA.KANTE)
    return math.sqrt(max(MA.KANTE ** 2 - wz * wz, 0.0)) - MA.KANTE


def koerperfeld(x, y, z):
    """Der Rohkoerper ohne Bohrung, Kammer und Schnurloch - fuer die
    Kontrolle der Aussenflaeche."""
    wq = profil(x, y, z) + MA.KANTE
    wz = abs(z - MA.LAENGE / 2.0) - (MA.LAENGE / 2.0 - MA.KANTE)
    return (min(max(wq, wz), 0.0)
            + math.hypot(max(wq, 0.0), max(wz, 0.0)) - MA.KANTE)


# ---------------------------------------------------------- Querschnitt ---

def kontur_punkte(z, n=KONTURPUNKTE, rmax=26.0):
    """Die Aussenkontur bei der Hoehe z, als n Punkte.

    Bisektion entlang Strahlen vom Mittelpunkt. Das geht nur, weil der
    Querschnitt sternfoermig um den Ursprung ist: der Ursprung liegt im
    Rohr, und die Rippe schliesst ohne Hinterschnitt daran an. Bei einer
    Kontur mit Hinterschnitt wuerde dieselbe Bisektion stillschweigend
    den falschen Rand finden.
    """
    t = ziel(z)
    pts = []
    for i in range(n):
        w = 2.0 * math.pi * i / n
        dx, dy = math.cos(w), math.sin(w)
        lo, hi = 0.0, rmax
        if profil(dx * hi, dy * hi, z) - t < 0.0:
            raise RuntimeError(f"Kontur reicht ueber {rmax} mm hinaus")
        for _ in range(64):
            mi = 0.5 * (lo + hi)
            if profil(dx * mi, dy * mi, z) - t < 0.0:
                lo = mi
            else:
                hi = mi
        pts.append((dx * lo, dy * lo))
    return pts


def kontur_draht(z, n=KONTURPUNKTE):
    """Die Aussenkontur als geschlossene periodische B-Spline-Kurve."""
    pts = [cq.Vector(x, y, z) for x, y in kontur_punkte(z, n)]
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def hoehen():
    """Die Hoehen, in denen abgetastet wird - bewusst ungleich verteilt.

    An den Stirnkanten laeuft die Kontur als Viertelkreis aus und steht
    bei z = 0 senkrecht auf der Endflaeche; gleichmaessig verteilte
    Schnitte wuerden das verschleifen. Dort wird deshalb nach dem Winkel
    des Viertelkreises abgetastet, nicht nach z. Ueber der Rampe
    (Abflachung) mittel dicht, in der Mitte duenn - dort ist der
    Querschnitt konstant.
    """
    z = []
    for i in range(9):                       # Stirnverrundung, nach Winkel
        a = math.pi / 2.0 * i / 8
        z.append(MA.KANTE * (1.0 - math.cos(a)))
    for i in range(1, 17):                   # Rampe
        z.append(MA.KANTE + (MA.ABFLACHUNG - MA.KANTE) * i / 16)
    for i in range(1, 9):                    # Mitte
        z.append(MA.ABFLACHUNG
                 + (MA.LAENGE / 2.0 - MA.ABFLACHUNG) * i / 8)
    z += [MA.LAENGE - v for v in reversed(z[:-1])]
    return z


# --------------------------------------------------------------- Aufbau ---

def _schale(drahte, je=JE_SCHALE):
    """Offener Loft aus zusammengenaehten Teilschalen plus zwei ebenen
    Deckeln. OCCs ThruSections gibt im Schalenmodus oberhalb von neun
    Schnitten auf - deshalb stueckweise."""
    naht = BRepBuilderAPI_Sewing(1e-6)
    i = 0
    while i < len(drahte) - 1:
        j = min(i + je, len(drahte) - 1)
        ts = BRepOffsetAPI_ThruSections(False, False, 1e-6)
        for k in range(i, j + 1):
            ts.AddWire(drahte[k].wrapped)
        ts.Build()
        naht.Add(ts.Shape())
        i = j
    for d in (drahte[0], drahte[-1]):
        naht.Add(cq.Face.makeFromWires(d).wrapped)
    naht.Perform()
    ex = TopExp_Explorer(naht.SewedShape(), TopAbs_SHELL)
    schalen = []
    while ex.More():
        schalen.append(TopoDS.Shell_s(ex.Current()))
        ex.Next()
    if len(schalen) != 1:
        raise RuntimeError(f"{len(schalen)} Schalen statt einer - nicht dicht")
    return cq.Solid(BRepBuilderAPI_MakeSolid(schalen[0]).Solid())


def rohkoerper(n=KONTURPUNKTE):
    return _schale([kontur_draht(z, n) for z in hoehen()])


def bohrung():
    """Ø18 durchgehend, an beiden Enden 45 Grad auf EINLAUF aufgeweitet."""
    ue = 1.0
    k = cq.Solid.makeCylinder(MA.R_INNEN, MA.LAENGE + 2 * ue,
                              cq.Vector(0, 0, -ue), cq.Vector(0, 0, 1))
    for z0, richtung in ((MA.EINLAUF, -1.0), (MA.LAENGE - MA.EINLAUF, 1.0)):
        # Kegel von R_INNEN bei z0 auf R_INNEN + EINLAUF an der Stirnflaeche,
        # und darueber hinaus, damit sauber geschnitten wird.
        spitze = cq.Vector(0, 0, z0)
        k = k.fuse(cq.Solid.makeCone(
            MA.R_INNEN, MA.R_INNEN + MA.EINLAUF + ue, MA.EINLAUF + ue,
            spitze, cq.Vector(0, 0, richtung)))
    return k


def _rundrechteck_prisma(a, b, k, y0, y1):
    """Prisma in y-Richtung, Querschnitt Rundrechteck 2a x 2b in x/z."""
    kasten = cq.Solid.makeBox(2 * a, y1 - y0, 2 * b,
                              cq.Vector(-a, y0, MA.LAENGE / 2.0 - b))
    senkrecht = [e for e in kasten.Edges()
                 if abs(e.tangentAt(0.5).z) < 1e-6
                 and abs(e.tangentAt(0.5).x) < 1e-6]
    return kasten.fillet(k, senkrecht)


def knotenkammer():
    """Gerundeter Quader unten, darueber ein Prisma bis zur Bohrungsachse.

    Das bildet yk = min(0, y + KAMMER_ACHSE) aus dem Feld nach: unterhalb
    der Kammerachse ein allseits mit ECK_KAMMER verrundeter Quader,
    darueber senkrechte Waende bis y = 0. Der Kanal ist damit an keiner
    Stelle breiter als seine Oeffnung - das ist die Bedingung dafuer,
    dass sich der Kern nach oben aus der Form ziehen laesst.
    """
    a = MA.D_KAMMER / 2.0
    unten = cq.Solid.makeBox(
        2 * a, 2 * a, MA.KAMMER_LAENGE,
        cq.Vector(-a, -MA.KAMMER_ACHSE - a, MA.LAENGE / 2.0 - MA.KAMMER_HALB))
    unten = unten.fillet(MA.ECK_KAMMER, unten.Edges())
    oben = _rundrechteck_prisma(a, MA.KAMMER_HALB, MA.ECK_KAMMER,
                                -MA.KAMMER_ACHSE, 0.0)
    return unten.fuse(oben)


def schnurbohrung():
    """Ø4 vom Kammerboden nach aussen, mit 45-Grad-Senkung am Austritt."""
    ue = 1.0
    r = MA.D_SCHNUR / 2.0
    y_aus = -MA.RIPPE_UNTEN
    k = cq.Solid.makeCylinder(
        r, (-MA.KAMMER_ACHSE + ue) - (y_aus - ue),
        cq.Vector(0, y_aus - ue, MA.LAENGE / 2.0), cq.Vector(0, 1, 0))
    if MA.SCHNUR_SENK > 1e-6:
        k = k.fuse(cq.Solid.makeCone(
            r, r + MA.SCHNUR_SENK + ue, MA.SCHNUR_SENK + ue,
            cq.Vector(0, y_aus + MA.SCHNUR_SENK, MA.LAENGE / 2.0),
            cq.Vector(0, -1, 0)))
    return k


def _kennung(kante):
    c = kante.Center()
    return (round(c.x, 3), round(c.y, 3), round(c.z, 3),
            round(kante.Length(), 3))


# ------------------------------------------------------------- Pruefung ---

def netzpunkte(shape, toleranz=0.02, winkel=0.2):
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopLoc import TopLoc_Location

    BRepMesh_IncrementalMesh(shape.wrapped, toleranz, False, winkel, True)
    pts = []
    ex = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
    while ex.More():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(TopoDS.Face_s(ex.Current()), loc)
        if tri is not None:
            tr = loc.Transformation()
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(tr)
                pts.append((p.X(), p.Y(), p.Z()))
        ex.Next()
    return pts


def formtreue(shape, feld, **kw):
    w = sorted(abs(feld(*p)) for p in netzpunkte(shape, **kw))
    return len(w), w[-1], sum(w) / len(w), w[int(len(w) * 0.999)]


# ---------------------------------------------------------------- Lauf ----

def baue(datei=DATEI, verrunden=True):
    print("Rohkoerper ...", flush=True)
    koerper = rohkoerper()
    roh = koerper

    print("Bohrung Ø18 ...", flush=True)
    koerper = koerper.cut(bohrung())

    print("Knotenkammer ...", flush=True)
    vorher = set(_kennung(e) for e in koerper.Edges())
    koerper = koerper.cut(knotenkammer())

    verrundet = False
    if verrunden:
        neu = [e for e in koerper.Edges() if _kennung(e) not in vorher]
        print(f"Verrundung {VERRUNDUNG_KAMMER} mm an {len(neu)} Kanten ...",
              flush=True)
        try:
            koerper = koerper.fillet(VERRUNDUNG_KAMMER, neu)
            verrundet = True
        except Exception as e:                       # noqa: BLE001
            print(f"  fehlgeschlagen ({type(e).__name__}) - Kanten bleiben "
                  f"scharf.", flush=True)

    print("Schnurbohrung Ø4 ...", flush=True)
    koerper = koerper.cut(schnurbohrung())

    cq.exporters.export(cq.Workplane(obj=koerper), datei, exportType="STEP")
    return koerper, roh, verrundet


if __name__ == "__main__":
    shape, roh, verrundet = baue()
    bb = shape.BoundingBox()
    n, a_max, a_mit, a_999 = formtreue(roh, koerperfeld)

    print(f"\ngeschrieben: {DATEI}")
    print(f"  Bauteil        Klinkenmanschette, Wand {MA.WAND:.1f} mm")
    print(f"  Bohrung        Ø{MA.D_INNEN:.1f} mm durchgehend, "
          f"Einlauf {MA.EINLAUF:.1f} mm unter 45 Grad")
    print(f"  Wand Mitte     {MA.WAND:.1f} mm, Stirnseite "
          f"{MA.WAND_ENDE:.1f} mm, Rampe {MA.ABFLACHUNG:.0f} mm")
    print(f"  Knotenkammer   {MA.D_KAMMER:.1f} x {MA.KAMMER_LAENGE:.0f} mm, "
          f"Eckradius {MA.ECK_KAMMER:.1f}, Stirnwand "
          f"{(MA.LAENGE - MA.KAMMER_LAENGE)/2:.1f} mm")
    print(f"  Schnurbohrung  Ø{MA.D_SCHNUR:.1f} mm, Senkung "
          f"{MA.SCHNUR_SENK:.1f} mm unter 45 Grad")
    print(f"  Kammerkanten   {VERRUNDUNG_KAMMER:.1f} mm "
          f"{'verrundet' if verrundet else 'NICHT verrundet'}")
    print()
    print(f"  Huellquader    {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
    print(f"  Volumen        {volumen(shape)/1000:.3f} cm^3   "
          f"(Rohkoerper {volumen(roh)/1000:.3f})")
    print(f"  Topologie      {len(shape.Faces())} Flaechen, "
          f"{len(shape.Edges())} Kanten, {len(shape.Solids())} Solid, "
          f"gueltig={shape.isValid()}")
    print(f"  Aussenflaeche  {n} Netzpunkte gegen das Feld: hoechstens "
          f"{a_max*1000:.1f} um, im Mittel {a_mit*1000:.2f} um")
