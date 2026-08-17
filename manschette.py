#!/usr/bin/env python3
"""
Türzwerg – Klinkenmanschette
Erzeugt ein druckfertiges STL der Silikonmanschette, die auf den Tuerdruecker
geschoben wird und die Schnur aufnimmt.

Anders als der Griff ist die Manschette kein Drehkoerper: Rohr, Rippe,
Knotenkammer und Schnurbohrung muessen vereinigt und voneinander abgezogen
werden. Die Form wird deshalb als Distanzfeld beschrieben und mit Marching
Tetrahedra vernetzt. Das kostet Rechenzeit, liefert dafuer weiche Uebergaenge
zwischen Rohr und Rippe, die sich mit gestapelten Querschnitten nicht
erzeugen liessen.

Alle Masse in Millimetern. Anpassen und neu ausfuehren:
    python3 manschette.py
"""

import math
import struct

# ---------------------------------------------------------------- Parameter --

LAENGE = 32.0           # Laenge der Manschette entlang des Drueckers

# Innendurchmesser. Konisch, damit sich die Manschette beim Ziehen selbst
# verkeilt und einen Bereich von Drueckerstaerken abdeckt.
# DIN 18255 normt Tuerdruecker auf 20 mm, es gibt Ausfuehrungen mit 23 mm,
# und viele Druecker verjuengen sich zum Ende hin. Beide Werte liegen
# bewusst unter dem Drueckermass: Silikon soll sich aufspannen.
D_INNEN_VORN = 18.0     # am Drueckerende, hier wird aufgeschoben
D_INNEN_HINTEN = 20.5   # zur Rosette hin

WAND = 2.0              # Wandstaerke des Rohrs

# Rippe an der Unterseite: nimmt die Knotenkammer auf und laeuft ueber die
# volle Laenge durch. Das ist nicht nur Optik – ein durchlaufendes Profil
# hat beim Drucken keine nach unten weisende Flaeche und braucht dadurch
# keine Stuetzen.
KAMMER_ACHSE = 11.0     # Abstand der Kammerachse von der Rohrachse
D_KAMMER = 11.0         # Knotenkammer
KAMMER_LAENGE = 14.0    # gerader Teil der Kammer
RIPPE_WAND = 2.0        # Material um die Kammer herum

D_SCHNUR = 5.0          # Schnurbohrung nach aussen
VERRUNDUNG = 4.0        # weicher Uebergang Rohr zu Rippe

RASTER = 0.42           # Kantenlaenge der Gitterzelle
DATEI = "tuerzwerg-manschette.stl"


# ------------------------------------------------------------- Distanzfeld ---

def _innen_radius(z):
    t = min(max(z / LAENGE, 0.0), 1.0)
    return (D_INNEN_VORN + (D_INNEN_HINTEN - D_INNEN_VORN) * t) / 2.0


def _weich_vereinen(a, b, k):
    """Vereinigung mit weichem Uebergang statt scharfer Kante."""
    h = min(max(0.5 + 0.5 * (b - a) / k, 0.0), 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)


def feld(x, y, z):
    """Signierter Abstand. Negativ bedeutet Material."""
    r = math.hypot(x, y)

    # Rohr, aussen
    rohr = r - (_innen_radius(z) + WAND)

    # Rippe: liegender Zylinder entlang der Achse, unter dem Rohr
    rippe = math.hypot(x, y + KAMMER_ACHSE) - (D_KAMMER / 2.0 + RIPPE_WAND)

    koerper = _weich_vereinen(rohr, rippe, VERRUNDUNG)
    koerper = max(koerper, z - LAENGE, -z)          # Stirnflaechen

    # Durchgangsbohrung fuer den Druecker
    bohrung = r - _innen_radius(z)

    # Knotenkammer: Zylinder entlang der Achse, oben zur Bohrung hin offen.
    # Die Enden laufen als 45-Grad-Kegel aus statt als Kugelkappen – eine
    # Kappe waere beim Drucken eine nach unten weisende Decke, ein Kegel
    # traegt sich selbst.
    rk = math.hypot(x, y + KAMMER_ACHSE)
    z_a = LAENGE / 2.0 - KAMMER_LAENGE / 2.0 - D_KAMMER / 2.0
    z_b = LAENGE / 2.0 + KAMMER_LAENGE / 2.0 + D_KAMMER / 2.0
    kammer = max(rk - D_KAMMER / 2.0, rk - (z - z_a), rk - (z_b - z))

    # Schnurbohrung: von aussen unten in die Kammer
    schnur = math.hypot(x, z - LAENGE / 2.0) - D_SCHNUR / 2.0
    schnur = max(schnur, y + KAMMER_ACHSE)          # endet in der Kammer

    return max(koerper, -bohrung, -kammer, -schnur)


# ----------------------------------------------------- Marching Tetrahedra ---

# Wuerfelecken, danach die sechs Tetraeder ueber die Raumdiagonale 0–6.
# Diese Zerlegung passt nahtlos an die Nachbarzellen an.
_ECKEN = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
          (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
_TETS = [(0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6),
         (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)]


def _rechtshaendig(ps):
    """Spatprodukt der drei Kanten. Positiv heisst rechtshaendig."""
    u = [ps[1][n] - ps[0][n] for n in range(3)]
    v = [ps[2][n] - ps[0][n] for n in range(3)]
    w = [ps[3][n] - ps[0][n] for n in range(3)]
    return (u[0] * (v[1] * w[2] - v[2] * w[1])
            - u[1] * (v[0] * w[2] - v[2] * w[0])
            + u[2] * (v[0] * w[1] - v[1] * w[0]))


def _schnitt(pa, da, pb, db, ia, ib):
    """Punkt auf der Kante. Die Reihenfolge wird ueber den Gitterindex
    festgelegt, damit benachbarte Tetraeder bitgenau denselben Punkt
    berechnen – sonst reisst das Netz an jeder Kante auf."""
    if ib < ia:
        pa, da, pb, db = pb, db, pa, da
    t = 0.5 if da == db else da / (da - db)
    return (pa[0] + (pb[0] - pa[0]) * t,
            pa[1] + (pb[1] - pa[1]) * t,
            pa[2] + (pb[2] - pa[2]) * t)


def vernetzen(grenzen, raster):
    (x0, x1), (y0, y1), (z0, z1) = grenzen
    nx = int((x1 - x0) / raster) + 2
    ny = int((y1 - y0) / raster) + 2
    nz = int((z1 - z0) / raster) + 2

    print(f"  Gitter {nx} x {ny} x {nz} = {nx*ny*nz//1000} Tausend Punkte")
    def wert(x, y, z):
        d = feld(x, y, z)
        return -1e-9 if d == 0.0 else d

    werte = [[[wert(x0 + i * raster, y0 + j * raster, z0 + k * raster)
               for k in range(nz)] for j in range(ny)] for i in range(nx)]

    def punkt(i, j, k):
        return (x0 + i * raster, y0 + j * raster, z0 + k * raster)

    def index(i, j, k):
        return (i * ny + j) * nz + k

    tri = []
    for i in range(nx - 1):
        wi = werte[i]
        wi1 = werte[i + 1]
        for j in range(ny - 1):
            for k in range(nz - 1):
                # Zelle ueberspringen, wenn alle acht Ecken gleiches Vorzeichen
                acht = (wi[j][k], wi1[j][k], wi1[j + 1][k], wi[j + 1][k],
                        wi[j][k + 1], wi1[j][k + 1], wi1[j + 1][k + 1], wi[j + 1][k + 1])
                if min(acht) >= 0.0 or max(acht) < 0.0:
                    continue
                ecke = [(i + dx, j + dy, k + dz) for dx, dy, dz in _ECKEN]
                for tet in _TETS:
                    ds = [acht[c] for c in tet]
                    n_minus = sum(1 for v in ds if v < 0.0)
                    if n_minus == 0 or n_minus == 4:
                        continue

                    # Ecken umsortieren: erst die im Material, dann die
                    # ausserhalb. Das Umsortieren kann die Haendigkeit des
                    # Tetraeders kippen – dann zeigen die Dreiecke nach innen.
                    # Deshalb wird sie geprueft und notfalls durch Tausch
                    # zweier Ecken derselben Gruppe wiederhergestellt.
                    ord_ = sorted(range(4), key=lambda n: ds[n] >= 0.0)
                    ps = [punkt(*ecke[tet[n]]) for n in ord_]
                    if _rechtshaendig(ps) < 0.0:
                        if n_minus <= 2:
                            ord_[2], ord_[3] = ord_[3], ord_[2]
                        else:
                            ord_[0], ord_[1] = ord_[1], ord_[0]
                        ps = [punkt(*ecke[tet[n]]) for n in ord_]

                    dd = [ds[n] for n in ord_]
                    gi = [index(*ecke[tet[n]]) for n in ord_]

                    def kante(a, b):
                        return _schnitt(ps[a], dd[a], ps[b], dd[b], gi[a], gi[b])

                    if n_minus == 1:
                        tri.append((kante(0, 1), kante(0, 2), kante(0, 3)))
                    elif n_minus == 3:
                        tri.append((kante(3, 0), kante(3, 1), kante(3, 2)))
                    else:
                        p02, p03 = kante(0, 2), kante(0, 3)
                        p12, p13 = kante(1, 2), kante(1, 3)
                        tri.append((p02, p03, p13))
                        tri.append((p02, p13, p12))
    return tri


# -------------------------------------------------------------- Pruefungen ---

def volumen(tri):
    v = 0.0
    for p, q, r in tri:
        v += (p[0] * (q[1] * r[2] - q[2] * r[1])
              - p[1] * (q[0] * r[2] - q[2] * r[0])
              + p[2] * (q[0] * r[1] - q[1] * r[0]))
    return v / 6.0


def offene_kanten(tri):
    """Jede Kante muss genau zwei Dreiecke haben.

    Gerundet wird auf sechs Stellen. Vier waren zu grob: Wo die Flaeche fast
    genau durch einen Gitterpunkt laeuft, entstehen Eckpunkte, die nur
    Bruchteile eines Mikrometers auseinanderliegen. Beim Runden fielen sie
    zusammen und meldeten Kanten als undicht, die es nicht waren.
    """
    kanten = {}
    for t in tri:
        for n in range(3):
            a = tuple(round(c, 6) for c in t[n])
            b = tuple(round(c, 6) for c in t[(n + 1) % 3])
            s = frozenset((a, b))
            kanten[s] = kanten.get(s, 0) + 1
    return sum(1 for c in kanten.values() if c != 2)


def ueberhang(tri):
    """Flaechenanteil, der beim Drucken ueber 45 Grad ueberhaengt.

    Gedruckt wird mit der Rohrachse senkrecht, aufgebaut also entlang z.
    Eine senkrechte Wand hat 0 Grad, eine waagerechte Decke 90 Grad. Die
    Standflaeche bei z = 0 liegt auf dem Druckbett und bleibt aussen vor.
    """
    schlimm = gesamt = 0.0
    grad_max = 0.0
    for p, q, r in tri:
        if max(p[2], q[2], r[2]) < 0.3:      # liegt auf dem Druckbett
            continue
        u = [q[n] - p[n] for n in range(3)]
        v = [r[n] - p[n] for n in range(3)]
        nx = u[1] * v[2] - u[2] * v[1]
        ny = u[2] * v[0] - u[0] * v[2]
        nz = u[0] * v[1] - u[1] * v[0]
        flaeche = math.sqrt(nx * nx + ny * ny + nz * nz) / 2.0
        if flaeche == 0.0:
            continue
        gesamt += flaeche
        sinus = -nz / (2.0 * flaeche)
        if sinus > 0.0:
            grad = math.degrees(math.asin(min(1.0, sinus)))
            grad_max = max(grad_max, grad)
            if grad > 45.0:
                schlimm += flaeche
    return schlimm / gesamt * 100.0, grad_max, gesamt


def _normale(p, q, r):
    u = [q[n] - p[n] for n in range(3)]
    v = [r[n] - p[n] for n in range(3)]
    nx = u[1] * v[2] - u[2] * v[1]
    ny = u[2] * v[0] - u[0] * v[2]
    nz = u[0] * v[1] - u[1] * v[0]
    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (0.0, 0.0, 0.0) if ln == 0 else (nx / ln, ny / ln, nz / ln)


def schreibe_stl(tri, pfad, titel):
    with open(pfad, "wb") as f:
        f.write(titel.encode("ascii", "replace")[:79].ljust(80, b" "))
        f.write(struct.pack("<I", len(tri)))
        for p, q, r in tri:
            f.write(struct.pack("<3f", *_normale(p, q, r)))
            for v in (p, q, r):
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))


if __name__ == "__main__":
    r_aussen = D_INNEN_HINTEN / 2.0 + WAND
    r_rippe = D_KAMMER / 2.0 + RIPPE_WAND
    grenzen = ((-r_aussen - 2, r_aussen + 2),
               (-KAMMER_ACHSE - r_rippe - 2, r_aussen + 2),
               (-1.5, LAENGE + 1.5))

    print("Vernetze ...")
    tri = vernetzen(grenzen, RASTER)

    vol = volumen(tri)
    if vol < 0:                       # Wicklung global umdrehen
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol

    schreibe_stl(tri, DATEI, "Tuerzwerg Manschette - Masse in mm")

    hoehe = KAMMER_ACHSE + r_rippe + r_aussen
    print(f"\nDatei          {DATEI}")
    print(f"Dreiecke       {len(tri)}")
    print(f"Offene Kanten  {offene_kanten(tri)}  (0 = geschlossenes Volumen)")
    print(f"Volumen        {vol/1000:.2f} cm^3   ({vol/1000*1.15:.1f} g Silikon)")
    print(f"Abmessungen    {2*r_aussen:.1f} x {hoehe:.1f} x {LAENGE:.0f} mm")
    print(f"Innen          {D_INNEN_VORN:.1f} mm vorn, {D_INNEN_HINTEN:.1f} mm hinten")
    print(f"Wand           {WAND:.1f} mm")
    print(f"Kammer         {D_KAMMER:.1f} x {KAMMER_LAENGE:.0f} mm, "
          f"Schnurbohrung {D_SCHNUR:.1f} mm")
    anteil, grad, flaeche = ueberhang(tri)
    print(f"Oberflaeche    {flaeche/100:.1f} cm^2")
    print(f"Ueberhang      {anteil:.2f} % der Flaeche ueber 45 Grad "
          f"(steilste Stelle {grad:.0f} Grad)")
