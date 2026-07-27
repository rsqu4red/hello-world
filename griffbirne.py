#!/usr/bin/env python3
"""
Türzwerg – Griffbirne
Erzeugt ein druckfertiges STL-Modell der Griffbirne mit durchgehender
Schnurbohrung und aufgeweiteter Knotenkammer im unteren Bereich.

Alle Masse in Millimetern. Anpassen und neu ausfuehren:
    python3 griffbirne.py
"""

import math
import struct

# ---------------------------------------------------------------- Parameter --

HOEHE = 62.0            # Gesamthoehe der Birne

# Aussenkontur: Halbbreite (a) und Halbtiefe (b) ueber der Hoehe h
# h = 0 ist oben (Kopf), h = HOEHE ist unten (Boden)
A_KOPF, B_KOPF = 11.0, 9.0     # Kragen oben
A_GRIFF, B_GRIFF = 15.0, 11.0  # Griffzone (30 x 22 mm)
A_BAUCH, B_BAUCH = 26.0, 14.0  # groesste Stelle (52 x 28 mm)

H_KRAGEN_ENDE = 10.0    # Ende der Kragenaufweitung
H_GRIFF_ENDE = 36.0     # Ende der zylindrischen Griffzone
H_BAUCH = 46.0          # Hoehe der groessten Breite
DOM_HALBACHSE = 24.19    # bestimmt, wie stark der Boden abgeflacht wird
# -> ergibt am Boden 39 x 21 mm Standflaeche und eine Ueberhangneigung
#    von rund 43 Grad, damit der Druck ohne Stuetzen auskommt

# Innenbohrung
D_SCHNUR = 5.0          # Durchmesser oben, fuer die Schnur
D_KAMMER = 12.0         # Durchmesser unten, hier verschwindet der Knoten
H_KAMMER_OBEN = 40.0    # ab hier nach unten hat die Bohrung Kammermass
KONUS_HOEHE = 3.5       # 45-Grad-Uebergang, druckbar und selbstzentrierend

# Netzaufloesung
# 96 Segmente ergeben bei 26 mm Radius eine Abweichung von 0,014 mm –
# weit unter allem, was ein 0,4-mm-Duesendruck aufloesen kann.
SEGMENTE = 96           # Unterteilungen im Umfang
STUFEN = 130            # Unterteilungen ueber die Hoehe

DATEI = "tuerzwerg-griffbirne.stl"


# ----------------------------------------------------------------- Kontur ----

def smoothstep(t):
    """Weicher Uebergang mit waagerechter Tangente an beiden Enden."""
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def kontur(h):
    """Halbbreite und Halbtiefe der Aussenkontur auf Hoehe h."""
    if h <= H_KRAGEN_ENDE:
        t = smoothstep(h / H_KRAGEN_ENDE)
        return (A_KOPF + (A_GRIFF - A_KOPF) * t,
                B_KOPF + (B_GRIFF - B_KOPF) * t)

    if h <= H_GRIFF_ENDE:
        return (A_GRIFF, B_GRIFF)

    if h <= H_BAUCH:
        t = smoothstep((h - H_GRIFF_ENDE) / (H_BAUCH - H_GRIFF_ENDE))
        return (A_GRIFF + (A_BAUCH - A_GRIFF) * t,
                B_GRIFF + (B_BAUCH - B_GRIFF) * t)

    # Boden: Viertelellipse, unten flach abgeschnitten
    t = (h - H_BAUCH) / DOM_HALBACHSE
    f = math.sqrt(max(0.0, 1.0 - t * t))
    return (A_BAUCH * f, B_BAUCH * f)


def bohrung(h):
    """Radius der Innenbohrung auf Hoehe h."""
    r_oben = D_SCHNUR / 2.0
    r_unten = D_KAMMER / 2.0
    h_konus_start = H_KAMMER_OBEN - KONUS_HOEHE

    if h <= h_konus_start:
        return r_oben
    if h >= H_KAMMER_OBEN:
        return r_unten
    t = (h - h_konus_start) / KONUS_HOEHE
    return r_oben + (r_unten - r_oben) * t


# ------------------------------------------------------------------ Netz -----

def hoehenstufen():
    """Hoehenwerte, an denen ein Ring erzeugt wird – Knickstellen exakt getroffen."""
    fest = {0.0, H_KRAGEN_ENDE, H_GRIFF_ENDE, H_BAUCH, HOEHE,
            H_KAMMER_OBEN - KONUS_HOEHE, H_KAMMER_OBEN}
    werte = {i * HOEHE / STUFEN for i in range(STUFEN + 1)}
    werte |= fest
    return sorted(w for w in werte if 0.0 <= w <= HOEHE)


def baue_netz():
    stufen = hoehenstufen()
    winkel = [2.0 * math.pi * j / SEGMENTE for j in range(SEGMENTE)]
    cos = [math.cos(w) for w in winkel]
    sin = [math.sin(w) for w in winkel]

    aussen, innen = [], []
    for h in stufen:
        a, b = kontur(h)
        r = bohrung(h)
        z = HOEHE - h  # Boden liegt auf z = 0, Kopf oben
        aussen.append([(a * cos[j], b * sin[j], z) for j in range(SEGMENTE)])
        innen.append([(r * cos[j], r * sin[j], z) for j in range(SEGMENTE)])

    dreiecke = []
    n = SEGMENTE
    letzte = len(stufen) - 1

    # Mantelflaechen
    for i in range(letzte):
        for j in range(n):
            k = (j + 1) % n
            ao, bo = aussen[i][j], aussen[i][k]
            co, do = aussen[i + 1][k], aussen[i + 1][j]
            dreiecke.append((ao, do, bo))     # Normale nach aussen
            dreiecke.append((bo, do, co))

            ai, bi = innen[i][j], innen[i][k]
            ci, di = innen[i + 1][k], innen[i + 1][j]
            dreiecke.append((ai, bi, di))     # Normale in die Bohrung
            dreiecke.append((bi, ci, di))

    # Ringflaeche oben (Kopf, Normale +z)
    for j in range(n):
        k = (j + 1) % n
        dreiecke.append((aussen[0][j], aussen[0][k], innen[0][k]))
        dreiecke.append((aussen[0][j], innen[0][k], innen[0][j]))

    # Ringflaeche unten (Standflaeche, Normale -z)
    for j in range(n):
        k = (j + 1) % n
        dreiecke.append((aussen[letzte][j], innen[letzte][k], aussen[letzte][k]))
        dreiecke.append((aussen[letzte][j], innen[letzte][j], innen[letzte][k]))

    return dreiecke


# ------------------------------------------------------------------ STL ------

def normale(p, q, r):
    ux, uy, uz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
    vx, vy, vz = r[0] - p[0], r[1] - p[1], r[2] - p[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    laenge = math.sqrt(nx * nx + ny * ny + nz * nz)
    if laenge == 0.0:
        return (0.0, 0.0, 0.0)
    return (nx / laenge, ny / laenge, nz / laenge)


def schreibe_stl(dreiecke, pfad):
    with open(pfad, "wb") as f:
        f.write(b"Tuerzwerg Griffbirne Rev.A - Masse in mm".ljust(80, b" "))
        f.write(struct.pack("<I", len(dreiecke)))
        for p, q, r in dreiecke:
            f.write(struct.pack("<3f", *normale(p, q, r)))
            f.write(struct.pack("<3f", *p))
            f.write(struct.pack("<3f", *q))
            f.write(struct.pack("<3f", *r))
            f.write(struct.pack("<H", 0))


# ------------------------------------------------------------------ Pruefung --

def pruefe(dreiecke):
    """Zaehlt Kanten und Ecken – jede Kante muss genau zweimal vorkommen."""
    kanten = {}
    ecken = set()
    for tri in dreiecke:
        for v in tri:
            ecken.add((round(v[0], 5), round(v[1], 5), round(v[2], 5)))
        for i in range(3):
            a = tuple(round(c, 5) for c in tri[i])
            b = tuple(round(c, 5) for c in tri[(i + 1) % 3])
            kanten[frozenset((a, b))] = kanten.get(frozenset((a, b)), 0) + 1
    offen = sum(1 for v in kanten.values() if v != 2)
    return len(ecken), len(kanten), offen


def volumen(dreiecke):
    """Signiertes Volumen in mm^3 ueber das Divergenztheorem."""
    v = 0.0
    for p, q, r in dreiecke:
        v += (p[0] * (q[1] * r[2] - q[2] * r[1])
              - p[1] * (q[0] * r[2] - q[2] * r[0])
              + p[2] * (q[0] * r[1] - q[1] * r[0]))
    return abs(v) / 6.0


if __name__ == "__main__":
    netz = baue_netz()
    schreibe_stl(netz, DATEI)

    ecken, kanten, offen = pruefe(netz)
    vol = volumen(netz)

    a_boden, b_boden = kontur(HOEHE)
    print(f"Datei          {DATEI}")
    print(f"Dreiecke       {len(netz)}")
    print(f"Ecken/Kanten   {ecken} / {kanten}")
    print(f"Offene Kanten  {offen}  (0 = geschlossenes Volumen)")
    print(f"Volumen        {vol/1000:.1f} cm^3")
    print(f"Masse Silikon  {vol/1000*1.15:.0f} g   (Dichte 1,15 g/cm^3)")
    print(f"Masse PLA      {vol/1000*1.24:.0f} g   (voll gefuellt)")
    print(f"Abmessungen    {2*A_BAUCH:.0f} x {2*B_BAUCH:.0f} x {HOEHE:.0f} mm")
    print(f"Standflaeche   {2*a_boden:.1f} x {2*b_boden:.1f} mm")
    print(f"Bohrung        oben {D_SCHNUR:.1f} mm, Kammer {D_KAMMER:.1f} mm "
          f"x {HOEHE-H_KAMMER_OBEN:.0f} mm tief")
