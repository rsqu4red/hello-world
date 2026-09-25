#!/usr/bin/env python3
"""
Türzwerg – den Zugring als STEP ausgeben

Warum nicht das STL umwandeln
-----------------------------

STL und STEP sind keine zwei Schreibweisen derselben Sache. Ein STL ist
ein Dreiecksnetz - hier 353 828 Facetten -, ein STEP ist ein B-Rep aus
exakten Flaechen. Wer ein Netz "nach STEP wandelt", bekommt ein STEP, in
dem jede Facette eine eigene ebene Flaeche ist: formal gueltig, aber
dreistellig Megabyte gross, in keinem CAD zu bearbeiten und beim
Verrunden oder Anbohren unbrauchbar. Die Kruemmung ist dann fuer immer
weg, denn im Netz war sie schon nicht mehr drin.

Dieses Skript geht deshalb nicht ueber das Netz, sondern an der
Netzerzeugung vorbei: es baut denselben Koerper noch einmal, aus
derselben parametrischen Definition in reif_mix.py, aus der auch das STL
entsteht - nur diesmal mit Kurven und Flaechen statt mit Dreiecken. Das
Ergebnis ist genauer als das STL, nicht ungenauer: 2 gegen 207 um
groesste Abweichung vom Sollkoerper.

Aufbau
------

Der Ring ist ein geschlossener Loft. An jeder Stelle des Umfangs ist der
Querschnitt ein Rundrechteck, dessen Breite, Tiefe und Eckradius als
Kosinusreihe ueber den Umfang laufen (Mix.breite, .dicke, .eckfaktor).
Die Querschnittsebene enthaelt die radiale Richtung und die Ringachse.
Abgezogen werden die Schnurbohrung mit ihrer Senkung und die
Knotenkammer.

Drei Dinge, an denen der naive Weg scheitert
--------------------------------------------

1. Der Querschnitt entartet. eck_unten ist 1,0, unten gilt also
   k = min(a, b) und die geraden Stuecke verschwinden - aus dem
   Rundrechteck wird ein Stadion. Ein Loft verlangt aber in jedem
   Schnitt dieselbe Topologie, und OCC nimmt keine Kante der Laenge
   null. Ausserdem wechselt ueber den Umfang, ob a oder b das
   Kleinstmass ist: seitlich ist das Band mit 11,74 mm schmaler als die
   14 mm Dicke. Deshalb wird jeder Querschnitt als eine geschlossene
   periodische B-Spline-Kurve ausgegeben, abgetastet nach Bogenlaenge.
   Entartete Stuecke bekommen dann einfach keine Punkte.

2. OCCs ThruSections gibt oberhalb von rund 24 Schnitten auf, im
   Schalenmodus schon bei neun. Mit nur 24 Schnitten woelbt sich die
   Flaeche zwischen ihnen um 70 um ueber die Solldicke - das Teil misst
   dann 14,14 statt 14,00 mm. Der Koerper wird deshalb aus Teilschalen
   von je acht Schnitten gebaut und zusammengenaeht; so sind beliebig
   viele Schnitte moeglich und die Woelbung faellt auf 10 um.

   Die Zahlen sind ein Handel zwischen Genauigkeit und Dateigroesse,
   denn jede Loft-Flaeche traegt ihr volles Kontrollpunktnetz mit:

       Schnitte x Punkte      Datei     groesste Abweichung
       192 x 96              20,2 MB          2,4 um
        96 x 64               7,0 MB          5,7 um     <- gewaehlt
        96 x 48               5,2 MB         10,7 um
        48 x 48               2,6 MB         53,1 um

   Gewaehlt ist die mittlere Zeile. 5,7 um sind gegenueber dem STL mit
   207 um immer noch ein Faktor 36, und 7 MB laesst sich verschicken.

3. Wegschneiden laesst sich die Woelbung nicht. Eine Scheibe bei z = +-7
   beruehrt die Flaeche tangential, und daran scheitert jede boolesche
   Operation in OCC - auch mit Fuzzy-Toleranz.

Ein Unterschied zum Netz, der benannt gehoert
---------------------------------------------

Im Distanzfeld wird die Kammer mit weich_abziehen(..., 0.8) abgezogen,
also mit einem weichen Minimum. Das ist kein Radius im CAD-Sinn, sondern
eine Mischfunktion: die Verrundung ist dort, wo beide Koerper sich
naehern, breiter als 0,8 mm und laeuft weiter aus. Im B-Rep wird daraus
eine echte Verrundung mit konstantem Radius 0,8 an denselben Kanten.

Fuer die Fertigung ist das die bessere Fassung - eine konstante
Verrundung laesst sich fraesen, messen und bemassen, ein weiches Minimum
nicht. Es ist aber nicht bis auf den Mikrometer dasselbe Teil, und das
soll hier stehen statt stillschweigend geglaettet zu werden.

    python3 step_reif.py
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

from reif_eh import REV_A_PHI
from reif_mix import D_SCHNUR, SCHNUR_SENK, WAND_KAMMER, _rundbox

SCHNITTE = 96           # Querschnitte ueber den Umfang
JE_SCHALE = 8           # Schnitte je Teilschale; darueber gibt OCC auf
PROFILPUNKTE = 64       # Stuetzpunkte je Querschnitt
KAMMER_SCHNITTE = 24
VERRUNDUNG = 0.8        # entspricht weich_abziehen(..., 0.8) im Feld
DATEI = "tuerzwerg-zugring-reva-phi.step"


# ------------------------------------------------------------- Werkzeug ---

def volumen(shape, eps=1e-6):
    """Volumen. Der Standardaufruf von VolumeProperties rechnet auf
    Spline-Flaechen grob - hier lag er um 13 mm^3 daneben und haette
    beinahe einen Geometriefehler vorgetaeuscht, der keiner war."""
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, p, eps, True)
    return p.Mass()


def soll_volumen(m, n=20000):
    """Koerpervolumen ohne Abzuege, analytisch.

    In radialen Ebenen ist dV = rho drho dz dtheta, also
    V = Integral A(theta) * rho_schwerpunkt(theta) dtheta. Der
    Querschnitt ist in u symmetrisch, sein Schwerpunkt liegt daher auf
    der Profilmitte. Das ist die unabhaengige Kontrolle fuer alles,
    was OCC ausrechnet.
    """
    s = 0.0
    for i in range(n):
        c = math.cos(2.0 * math.pi * (i + 0.5) / n)
        a, b = m.breite(c) / 2.0, m.dicke(c) / 2.0
        k = min(m.eckfaktor(c) * min(a, b), a, b)
        s += (4.0 * a * b - (4.0 - math.pi) * k * k) * (m.aussen(c) - a)
    return s * 2.0 * math.pi / n


def koerperfeld(m):
    """Das Distanzfeld ohne Bohrung und Kammer - fuer die Kontrolle des
    Rohkoerpers. Gegen das volle Feld gemessen laegen die Abzugsbereiche
    natuerlich weit vom Sollwert weg, ohne dass etwas falsch waere."""
    def f(x, y, z):
        rho = math.hypot(x, y) or 1e-9
        c = y / rho
        a, b = m.breite(c) / 2.0, m.dicke(c) / 2.0
        return _rundbox(rho - (m.aussen(c) - a), z, a, b,
                        m.eckfaktor(c) * min(a, b))
    return f


# ---------------------------------------------------------- Querschnitt ---

def rundrechteck_punkte(a, b, k, n=PROFILPUNKTE):
    """Umriss des Rundrechtecks als n Punkte, gleichmaessig nach
    Bogenlaenge. Entartete Stuecke bekommen keine Punkte, es entstehen
    also nie zwei gleiche Punkte hintereinander."""
    k = max(0.0, min(k, a, b))
    ax, bz = a - k, b - k
    stuecke = []

    def gerade(p, q):
        if math.dist(p, q) > 1e-12:
            stuecke.append(("L", math.dist(p, q), p, q))

    def bogen(mitte, w0):
        if k > 1e-12:
            stuecke.append(("A", k * math.pi / 2.0, mitte, w0))

    gerade((a, 0.0), (a, bz))
    bogen((ax, bz), 0.0)
    gerade((ax, b), (-ax, b))
    bogen((-ax, bz), math.pi / 2.0)
    gerade((-a, bz), (-a, -bz))
    bogen((-ax, -bz), math.pi)
    gerade((-ax, -b), (ax, -b))
    bogen((ax, -bz), 1.5 * math.pi)
    gerade((a, -bz), (a, 0.0))

    gesamt = sum(st[1] for st in stuecke)
    punkte = []
    for i in range(n):
        s = gesamt * i / n
        for art, laenge, p, q in stuecke:
            if s > laenge:
                s -= laenge
                continue
            if art == "L":
                t = s / laenge
                punkte.append((p[0] + (q[0] - p[0]) * t,
                               p[1] + (q[1] - p[1]) * t))
            else:
                w = q + (s / laenge) * (math.pi / 2.0)
                punkte.append((p[0] + k * math.cos(w), p[1] + k * math.sin(w)))
            break
    return punkte


def profil_draht(ebene, a, b, k, n=PROFILPUNKTE):
    """Der Querschnitt als geschlossene periodische B-Spline-Kurve."""
    pts = [ebene.toWorldCoords(cq.Vector(u, v, 0.0))
           for u, v in rundrechteck_punkte(a, b, k, n)]
    return cq.Wire.assembleEdges(
        [cq.Edge.makeSpline([cq.Vector(p) for p in pts], periodic=True)])


def ring_draht(m, i, n, pts=PROFILPUNKTE):
    """Der Querschnitt an der Umfangsstelle i von n.

    Die Profilebene wird von der radialen Richtung und der Ringachse
    aufgespannt; ihre Normale ist die Tangente. Der Ursprung liegt in
    der Querschnittsmitte, also auf aussen(c) - breite(c)/2, nicht auf
    einem festen Radius: die Mittellinie des Bandes ist keine Kreislinie.
    """
    th = 2.0 * math.pi * i / n
    s, c = math.sin(th), math.cos(th)
    a, b = m.breite(c) / 2.0, m.dicke(c) / 2.0
    mitte = m.aussen(c) - a
    ebene = cq.Plane(origin=(mitte * s, mitte * c, 0.0),
                     xDir=(s, c, 0.0), normal=(c, -s, 0.0))
    return profil_draht(ebene, a, b, m.eckfaktor(c) * min(a, b), pts)


# ---------------------------------------------------------------- Ring ----

def ring_koerper(m, n=SCHNITTE, je=JE_SCHALE, pts=PROFILPUNKTE):
    """Der Ringkoerper, aus Teilschalen zusammengenaeht (siehe Modulkopf)."""
    drahte = [ring_draht(m, i, n, pts) for i in range(n)]
    naht = BRepBuilderAPI_Sewing(1e-6)
    for g in range(n // je):
        ts = BRepOffsetAPI_ThruSections(False, False, 1e-6)
        for j in range(je + 1):
            ts.AddWire(drahte[(g * je + j) % n].wrapped)
        ts.Build()
        naht.Add(ts.Shape())
    naht.Perform()
    ex = TopExp_Explorer(naht.SewedShape(), TopAbs_SHELL)
    schalen = []
    while ex.More():
        schalen.append(TopoDS.Shell_s(ex.Current()))
        ex.Next()
    if len(schalen) != 1:
        raise RuntimeError(f"{len(schalen)} Schalen statt einer - nicht dicht")
    return cq.Solid(BRepBuilderAPI_MakeSolid(schalen[0]).Solid())


def schnurbohrung(m):
    """Ø4 von der Kammer nach aussen, mit abgeleiteter Senkung."""
    y_kammer = m.aussen(1.0) - m.bohr_tiefe
    y_aus = m.aussen(1.0)
    a_top, b_top = m.b_oben / 2.0, m.d_oben / 2.0
    k_top = m.eck_oben * min(a_top, b_top)
    tiefe = min(SCHNUR_SENK,
                max(0.0, ((b_top - k_top) - D_SCHNUR / 2.0) * 0.5))

    ueber, r = 1.0, D_SCHNUR / 2.0
    koerper = cq.Solid.makeCylinder(
        r, (y_aus + ueber) - (y_kammer - ueber),
        cq.Vector(0, y_kammer - ueber, 0), cq.Vector(0, 1, 0))
    if tiefe > 1e-6:
        koerper = koerper.fuse(cq.Solid.makeCone(
            r, r + tiefe + ueber, tiefe + ueber,
            cq.Vector(0, y_aus - tiefe, 0), cq.Vector(0, 1, 0)))
    return koerper, tiefe


def kammer_hoehe(m, y):
    """bk aus reif_mix.feld, als eigene Funktion - damit Loft und
    Kontrolle nachweislich dasselbe rechnen."""
    a_top, b_top = m.b_oben / 2.0, m.d_oben / 2.0
    k_top = m.eck_oben * min(a_top, b_top)
    u_top = y - (m.aussen(1.0) - a_top)
    hoch = m._profil_z(u_top, a_top, b_top, k_top) - WAND_KAMMER
    t = min(max((u_top + a_top) / max(k_top, 1e-6), 0.0), 1.0)
    t = t * t * (3.0 - 2.0 * t)
    return min(m.b_kammer, max(hoch, 0.0) * t + m.b_kammer * (1.0 - t))


def knotenkammer(m, n=KAMMER_SCHNITTE):
    """Rundrechteck in x/z, Hoehe folgt der Bandkontur, gerade Stirnwaende."""
    y0, y1 = m.innen(1.0) - 1.0, m.aussen(1.0) - m.bohr_tiefe
    drahte = []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        bk = kammer_hoehe(m, y)
        ebene = cq.Plane(origin=(0.0, y, 0.0), xDir=(1, 0, 0), normal=(0, 1, 0))
        drahte.append(profil_draht(ebene, m.a_kammer, bk,
                                   0.8 * min(m.a_kammer, bk)))
    return cq.Solid.makeLoft(drahte, ruled=False)


def _kennung(kante):
    """Kanten vor und nach dem Schnitt vergleichbar machen. hashCode gibt
    es in neueren OCP nicht mehr, und Identitaet haelt der Schnitt ohnehin
    nicht durch - Mitte und Laenge auf ein Tausendstel genuegen."""
    c = kante.Center()
    return (round(c.x, 3), round(c.y, 3), round(c.z, 3),
            round(kante.Length(), 3))


# ------------------------------------------------------------- Pruefung ---

def formtreue(shape, feld, toleranz=0.02, winkel=0.2):
    """Wie weit liegen die Flaechen des B-Rep vom Distanzfeld entfernt?

    Der Koerper wird vernetzt und an jedem Netzpunkt das Feld
    ausgewertet. Null hiesse: der Punkt liegt exakt auf der Sollflaeche.
    """
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopLoc import TopLoc_Location

    BRepMesh_IncrementalMesh(shape.wrapped, toleranz, False, winkel, True)
    werte = []
    ex = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
    while ex.More():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(TopoDS.Face_s(ex.Current()), loc)
        if tri is not None:
            tr = loc.Transformation()
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(tr)
                werte.append(abs(feld(p.X(), p.Y(), p.Z())))
        ex.Next()
    werte.sort()
    n = len(werte)
    return n, werte[-1], sum(werte) / n, werte[int(n * 0.999)]


# ---------------------------------------------------------------- Lauf ----

def baue(m=REV_A_PHI, datei=DATEI, verrunden=True):
    print("Ringkoerper ...", flush=True)
    koerper = ring_koerper(m)
    roh = koerper

    print("Schnurbohrung ...", flush=True)
    bohr, senk = schnurbohrung(m)
    koerper = koerper.cut(bohr)

    print("Knotenkammer ...", flush=True)
    vorher = set(_kennung(e) for e in koerper.Edges())
    koerper = koerper.cut(knotenkammer(m))

    verrundet = False
    if verrunden:
        neu = [e for e in koerper.Edges() if _kennung(e) not in vorher]
        print(f"Verrundung {VERRUNDUNG} mm an {len(neu)} Kanten ...", flush=True)
        try:
            koerper = koerper.fillet(VERRUNDUNG, neu)
            verrundet = True
        except Exception as e:                       # noqa: BLE001
            print(f"  fehlgeschlagen ({type(e).__name__}) - Kanten bleiben "
                  f"scharf.", flush=True)

    cq.exporters.export(cq.Workplane(obj=koerper), datei, exportType="STEP")
    return koerper, roh, senk, verrundet


if __name__ == "__main__":
    m = REV_A_PHI
    shape, roh, senk, verrundet = baue(m)

    br, ho = m.aussenmass()
    ob, oh = m.oeffnung()
    bb = shape.BoundingBox()
    v_roh, v_soll = volumen(roh), soll_volumen(m)
    n, a_max, a_mit, a_999 = formtreue(roh, koerperfeld(m))

    print(f"\ngeschrieben: {DATEI}")
    print(f"  Bauteil        Rev. A phi, {br:.1f} x {ho:.1f} x "
          f"{m.d_oben:.1f} mm")
    print(f"  Oeffnung       {ob:.1f} x {oh:.1f} mm")
    print(f"  Band o/s/u     {m.b_oben:.1f} / {m.b_seite:.2f} / "
          f"{m.b_unten:.1f} mm")
    print(f"  Eckfaktor      oben {m.eck_oben:.3f}, unten {m.eck_unten:.3f}")
    print(f"  Schnurbohrung  Ø{D_SCHNUR:.1f} mm, Senkung {senk:.3f} mm "
          f"unter 45 Grad")
    print(f"  Knotenkammer   {2*m.a_kammer:.1f} x "
          f"{2*kammer_hoehe(m, m.aussen(1.0)-m.bohr_tiefe):.1f} mm, "
          f"Mund {2*kammer_hoehe(m, m.innen(1.0)-1.0):.1f} mm")
    print(f"  Verrundung     {VERRUNDUNG:.1f} mm "
          f"{'gesetzt' if verrundet else 'NICHT gesetzt'}")
    print()
    print(f"  Huellquader    {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
    print(f"  Volumen        fertig {volumen(shape)/1000:.3f} cm^3, "
          f"Rohkoerper {v_roh/1000:.4f}")
    print(f"  Sollvolumen    {v_soll/1000:.4f} cm^3 (analytisch), "
          f"Abweichung {abs(v_roh-v_soll):.2f} mm^3")
    print(f"  Topologie      {len(shape.Faces())} Flaechen, "
          f"{len(shape.Edges())} Kanten, {len(shape.Solids())} Solid, "
          f"gueltig={shape.isValid()}")
    print(f"  Formtreue      {n} Netzpunkte auf dem Rohkoerper: hoechstens "
          f"{a_max*1000:.1f} um, im Mittel {a_mit*1000:.2f} um")
