#!/usr/bin/env python3
"""
Türzwerg – Griffvarianten
Alternativentwuerfe zur Griffbirne. Alle mit schmalerer Griffzone und einer
Gestalt, die nicht auf die Achse Schaft-plus-Kuppe hinauslaeuft.

Gemeinsam bleiben: durchgehende Schnurbohrung, verdeckte Knotenkammer,
Auslegung gegen Verschluckbarkeit, druckbar ohne Stuetzen.

    python3 griffe.py
"""

import math
import struct

D_SCHNUR = 5.0          # Bohrung oben
R_EINLAUF = 1.6         # Verrundung am Schnureinlauf
KRONE_R = D_SCHNUR / 2.0 + R_EINLAUF
KONUS_HOEHE = 3.5       # 45-Grad-Uebergang zur Knotenkammer

SEGMENTE = 96
STUFEN = 120


# --------------------------------------------------------------- Kurven ------

def _lin(t):
    return t


def _smooth(t):
    return t * t * (3.0 - 2.0 * t)


def _kuppe(t):
    """Waagerechte Tangente am Anfang, senkrechte am Ende."""
    return math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))


MODI = {"lin": _lin, "smooth": _smooth, "kuppe": _kuppe}


class Profil:
    """Aussenkontur als Folge von Stuetzpunkten (h, a, b) mit Uebergangsart.

    'cap' ist ein Sonderfall: abgeschnittene Viertelellipse fuer den Boden.
    Sie setzt mit senkrechter Tangente an und wird vor dem waagerechten
    Auslauf gekappt, damit die Standflaeche traegt und der Ueberhang flach
    genug zum Drucken bleibt.
    """

    def __init__(self, punkte, rillen=None):
        self.punkte = punkte
        # rillen = (h_von, h_bis, periode, tiefe) – gedrechselte Zierrillen.
        # Die Kerbe folgt einer Kosinuswelle, die an beiden Bandgrenzen auf
        # null steht; die Bandhoehe muss ein Vielfaches der Periode sein,
        # sonst entsteht dort ein Absatz. Weichere Kerben als eine V-Nut,
        # dafuer druckbar: die groesste Neigung ist tiefe * pi / periode.
        self.rillen = rillen

    def _kerbe(self, h):
        if not self.rillen:
            return 0.0
        h0, h1, periode, tiefe = self.rillen
        if not (h0 <= h <= h1):
            return 0.0
        return tiefe * 0.5 * (1.0 - math.cos(2.0 * math.pi * (h - h0) / periode))

    def __call__(self, h):
        a, b = self._roh(h)
        d = self._kerbe(h)
        return (a - d, b - d)

    def _roh(self, h):
        pkt = self.punkte
        for i in range(len(pkt) - 1):
            h0, a0, b0, _ = pkt[i]
            h1, a1, b1, modus = pkt[i + 1]
            if h <= h1 or i == len(pkt) - 2:
                t = 0.0 if h1 == h0 else min(max((h - h0) / (h1 - h0), 0.0), 1.0)
                if modus == "cap":
                    verh = a1 / a0
                    tmax = math.sqrt(max(0.0, 1.0 - verh * verh))
                    f = math.sqrt(max(0.0, 1.0 - (t * tmax) ** 2))
                    return (a0 * f, b0 * f)
                u = MODI[modus](t)
                return (a0 + (a1 - a0) * u, b0 + (b1 - b0) * u)
        return (pkt[-1][1], pkt[-1][2])

    @property
    def hoehe(self):
        return self.punkte[-1][0]

    @property
    def knicke(self):
        stellen = {p[0] for p in self.punkte}
        if self.rillen:
            h0, h1, periode, _ = self.rillen
            n = max(1, int(round((h1 - h0) / periode)) * 14)
            stellen |= {h0 + (h1 - h0) * i / n for i in range(n + 1)}
        return stellen


class Bohrung:
    def __init__(self, d_kammer, h_kammer, hoehe, kopf):
        self.r_kammer = d_kammer / 2.0
        self.h_kammer = h_kammer
        self.hoehe = hoehe
        self.kopf = kopf          # "kuppe" oder "flach"

    def __call__(self, h):
        r_oben = D_SCHNUR / 2.0
        if h <= R_EINLAUF:
            return KRONE_R - math.sqrt(
                max(0.0, R_EINLAUF ** 2 - (R_EINLAUF - h) ** 2))
        start = self.h_kammer - KONUS_HOEHE
        if h <= start:
            return r_oben
        if h >= self.h_kammer:
            return self.r_kammer
        t = (h - start) / KONUS_HOEHE
        return r_oben + (self.r_kammer - r_oben) * t


# ----------------------------------------------------------- Querschnitt -----

def superellipse(a, b, n, j, seg):
    """Punkt auf einer Superellipse. n = 2 ergibt die Ellipse,
    groessere Werte einen zunehmend rechteckigen Querschnitt."""
    w = 2.0 * math.pi * j / seg
    c, s = math.cos(w), math.sin(w)
    p = 2.0 / n
    return (a * math.copysign(abs(c) ** p, c),
            b * math.copysign(abs(s) ** p, s))


# ------------------------------------------------------------------ Netz -----

def hoehenstufen(profil, bohr):
    hoehe = profil.hoehe
    fest = set(profil.knicke) | {0.0, hoehe, R_EINLAUF,
                                 bohr.h_kammer, bohr.h_kammer - KONUS_HOEHE}
    werte = {i * hoehe / STUFEN for i in range(STUFEN + 1)} | fest
    werte |= {R_EINLAUF * (i / 28.0) ** 2 for i in range(29)}
    kuppe_bis = min((p[0] for p in profil.punkte if p[0] > 0), default=hoehe)
    werte |= {kuppe_bis * (i / 40.0) ** 2 for i in range(41)}
    return sorted(w for w in werte if 0.0 <= w <= hoehe)


def baue_netz(profil, bohr, n_quer):
    stufen = hoehenstufen(profil, bohr)
    hoehe = profil.hoehe
    # Bei gekuppeltem Kopf treffen sich Aussenflaeche und Einlauftrichter auf
    # dem Scheitelring. Der Trichter ist kreisrund, also muss es der
    # Querschnitt dort auch sein – der Exponent wird ueber die Kuppe
    # eingeblendet, sonst klafft am Scheitel eine Naht.
    h_blend = min((p[0] for p in profil.punkte if p[0] > 0), default=1.0)

    def exponent(h):
        if bohr.kopf != "kuppe":
            return n_quer
        return 2.0 + (n_quer - 2.0) * min(1.0, h / h_blend)

    aussen, innen = [], []
    for h in stufen:
        a, b = profil(h)
        r = bohr(h)
        z = hoehe - h
        aussen.append([superellipse(a, b, exponent(h), j, SEGMENTE) + (z,)
                       for j in range(SEGMENTE)])
        innen.append([superellipse(r, r, 2.0, j, SEGMENTE) + (z,)
                      for j in range(SEGMENTE)])

    tri = []
    n, letzte = SEGMENTE, len(stufen) - 1
    for i in range(letzte):
        for j in range(n):
            k = (j + 1) % n
            ao, bo, co, do = aussen[i][j], aussen[i][k], aussen[i + 1][k], aussen[i + 1][j]
            tri.append((ao, do, bo))
            tri.append((bo, do, co))
            ai, bi, ci, di = innen[i][j], innen[i][k], innen[i + 1][k], innen[i + 1][j]
            tri.append((ai, bi, di))
            tri.append((bi, ci, di))

    if bohr.kopf == "flach":
        for j in range(n):
            k = (j + 1) % n
            tri.append((aussen[0][j], aussen[0][k], innen[0][k]))
            tri.append((aussen[0][j], innen[0][k], innen[0][j]))

    for j in range(n):
        k = (j + 1) % n
        tri.append((aussen[letzte][j], innen[letzte][k], aussen[letzte][k]))
        tri.append((aussen[letzte][j], innen[letzte][j], innen[letzte][k]))
    return tri


# ------------------------------------------------------------------ STL ------

def _normale(p, q, r):
    u = [q[i] - p[i] for i in range(3)]
    v = [r[i] - p[i] for i in range(3)]
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


# -------------------------------------------------------------- Pruefung -----

def offene_kanten(tri):
    kanten = {}
    for t in tri:
        for i in range(3):
            a = tuple(round(c, 4) for c in t[i])
            b = tuple(round(c, 4) for c in t[(i + 1) % 3])
            key = frozenset((a, b))
            kanten[key] = kanten.get(key, 0) + 1
    return sum(1 for v in kanten.values() if v != 2)


def volumen(tri):
    v = 0.0
    for p, q, r in tri:
        v += (p[0] * (q[1] * r[2] - q[2] * r[1])
              - p[1] * (q[0] * r[2] - q[2] * r[0])
              + p[2] * (q[0] * r[1] - q[1] * r[0]))
    return abs(v) / 6.0


def max_ueberhang(profil):
    """Groesster Ueberhangwinkel der Aussenflaeche, gemessen von der Senkrechten.
    Gedruckt wird mit der Standflaeche unten, aufgebaut wird also entgegen h."""
    hoehe, d, best = profil.hoehe, 0.03, (0.0, 0.0)
    h = R_EINLAUF + d
    while h < hoehe - d:
        w = math.degrees(math.atan2(profil(h - d)[0] - profil(h + d)[0], 2 * d))
        if w > best[0]:
            best = (w, h)
        h += 0.05
    return best


def duennste_wand(profil, bohr):
    hoehe, best = profil.hoehe, None
    for i in range(3001):
        h = R_EINLAUF + (hoehe - R_EINLAUF) * i / 3000
        a, b = profil(h)
        r = bohr(h)
        for wert in (a - r, b - r):
            if best is None or wert < best[0]:
                best = (wert, h)
    return best


def griffumfang(a, b):
    """Ramanujan-Naeherung fuer den Ellipsenumfang."""
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


# ---------------------------------------------------------------- Varianten --

VARIANTEN = {}


def variante(name, titel, datei, profil, bohr, n_quer, griff, notiz):
    VARIANTEN[name] = dict(titel=titel, datei=datei, profil=profil,
                           bohr=bohr, n_quer=n_quer, griff=griff, notiz=notiz)


# 1 – Der Steg: liegender Griffsteg, quer zur Zugrichtung
variante(
    "steg", "Der Steg", "tuerzwerg-griff-steg.stl",
    Profil([
        (0.0,  38.0,  8.5,  "lin"),
        (4.0,  43.0, 10.5,  "kuppe"),
        (15.0, 43.0, 10.5,  "lin"),
        (25.0, 40.0,  9.77, "cap"),
    ]),
    Bohrung(d_kammer=10.0, h_kammer=10.0, hoehe=25.0, kopf="flach"),
    n_quer=4.5, griff=(21.0, 25.0),
    notiz="Querliegender Steg, 86 mm lang. Wird wie eine Turnstange gegriffen.")

# 2 – Die Hantel: Taille zwischen zwei Verdickungen.
# Die Taille ist die einzige Stellschraube, die sich beim Greifen bemerkbar
# macht, deshalb steht sie als Parameter. Der Uebergang von der oberen
# Verdickung zur Taille laeuft ueber 13 mm – schmalere Taillen wuerden bei
# kuerzerem Uebergang die 45-Grad-Grenze reissen und Stuetzen noetig machen.
def hantel(breite, tiefe, empfehlung=False):
    a, b = breite / 2.0, tiefe / 2.0
    variante(
        "hantel%02d" % round(breite),
        "Die Hantel · Taille %.0f mm" % breite,
        "tuerzwerg-griff-hantel-%02d.stl" % round(breite),
        Profil([
            (0.0,  KRONE_R, KRONE_R, "lin"),
            (9.0,  16.0,  9.0,  "kuppe"),
            (22.0, a,     b,    "smooth"),
            (44.0, a,     b,    "lin"),
            (54.0, 26.0, 13.0,  "smooth"),
            (64.0, 22.0, 11.0,  "cap"),
        ]),
        Bohrung(d_kammer=12.0, h_kammer=50.0, hoehe=64.0, kopf="kuppe"),
        n_quer=2.0, griff=(breite, tiefe),
        notiz=("Taille als Griff, Verdickung oben, Bauch unten."
               + (" Vorgeschlagene Mitte." if empfehlung else "")))


hantel(22.0, 15.0)
hantel(20.0, 14.0, empfehlung=True)
hantel(18.0, 13.0)

# 2b – Der Drechsel: Springseilgriff, auf den Kopf gestellt.
# Vorlage ist ein gedrechselter Holzgriff. Umgedreht kommt das schlanke
# Schaftende nach oben, wo die Schnur einlaeuft, der lange Schaft wird zum
# Griff, und die Olive sitzt unten als Rutschstopp – ergonomisch genau
# richtig herum, weil die Hand beim Ziehen nach unten wegrutscht.
variante(
    "drechsel", "Der Drechsel", "tuerzwerg-griff-drechsel.stl",
    Profil([
        (0.0,   KRONE_R, KRONE_R, "lin"),
        (7.0,    9.0,  9.0, "kuppe"),    # gerundetes Schaftende oben
        (44.0,  10.0, 10.0, "lin"),      # Schaft, leicht konisch: Griff
        (56.0,  10.0, 10.0, "lin"),      # Rillenband
        (64.0,   8.0,  8.0, "smooth"),   # Hals
        (82.0,  18.0, 18.0, "smooth"),   # Olive, groesste Stelle
        (104.0, 11.0, 11.0, "cap"),      # Olive laeuft auf die Standflaeche
    ], rillen=(44.0, 56.0, 4.0, 1.1)),
    Bohrung(d_kammer=12.0, h_kammer=86.0, hoehe=104.0, kopf="kuppe"),
    n_quer=2.0, griff=(20.0, 20.0),
    notiz="Gedrechselter Griff nach Vorlage, umgedreht. Schaft als Griff, "
          "Olive unten.")

# 2c – Der Drechsel kompakt: dieselbe Sprache, aber die Olive gross genug,
# dass das Teil auch die Kleinballprobe aus eigener Groesse besteht.
variante(
    "drechsel_kompakt", "Der Drechsel · kompakt",
    "tuerzwerg-griff-drechsel-kompakt.stl",
    Profil([
        (0.0,  KRONE_R, KRONE_R, "lin"),
        (6.0,   9.0,  9.0, "kuppe"),
        (38.0, 10.0, 10.0, "lin"),
        (50.0, 10.0, 10.0, "lin"),
        (57.0,  8.5,  8.5, "smooth"),
        (70.0, 24.0, 24.0, "smooth"),
        (92.0, 17.0, 17.0, "cap"),
    ], rillen=(38.0, 50.0, 4.0, 1.1)),
    Bohrung(d_kammer=12.0, h_kammer=74.0, hoehe=92.0, kopf="kuppe"),
    n_quer=2.0, griff=(20.0, 20.0),
    notiz="Wie der Drechsel, aber mit 48 mm Olive und kuerzerem Schaft.")

# 3 – Der Taler: flache Scheibe
variante(
    "taler", "Der Taler", "tuerzwerg-griff-taler.stl",
    Profil([
        (0.0,  KRONE_R, KRONE_R, "lin"),
        (14.0, 22.0, 10.0, "kuppe"),
        (26.0, 28.0, 11.0, "smooth"),
        (38.0, 28.0, 11.0, "lin"),
        (52.0, 24.0, 10.5, "smooth"),
    ]),
    Bohrung(d_kammer=12.0, h_kammer=34.0, hoehe=52.0, kopf="kuppe"),
    n_quer=2.6, griff=(56.0, 22.0),
    notiz="Flache Scheibe, 56 mm breit und nur 22 mm dick. Wird am Rand gefasst.")

# 4 – Das Blatt: flaches Paddel mit Taille
variante(
    "blatt", "Das Blatt", "tuerzwerg-griff-blatt.stl",
    Profil([
        (0.0,  KRONE_R, KRONE_R, "lin"),
        (11.0, 12.0,  9.0,  "kuppe"),
        (34.0, 12.0,  8.5,  "lin"),
        (50.0, 25.0, 11.0,  "smooth"),
        (64.0, 20.5,  9.0,  "cap"),
    ]),
    Bohrung(d_kammer=11.0, h_kammer=50.0, hoehe=64.0, kopf="kuppe"),
    n_quer=2.3, griff=(24.0, 17.0),
    notiz="Flaches Paddel mit deutlicher Taille, 50 mm breit, 22 mm dick.")


def kennzahlen(v):
    """Masse und das Mass, auf das es bei den Pruefkoerpern ankommt.

    'engste_oeffnung' ist der kleinste Lochdurchmesser, durch den das Teil
    ueberhaupt hindurchkaeme – Minimum ueber die drei Hauptrichtungen. Fuer
    den Durchgang laengs der Achse zaehlt der Umkreis des groessten
    Querschnitts, nicht dessen Diagonale: ein runder Querschnitt braucht nur
    seinen Durchmesser, ein rechteckiger seine Diagonale.
    """
    profil, n = v["profil"], v["n_quer"]
    hoehe = profil.hoehe
    proben = [profil(hoehe * i / 600) for i in range(601)]
    breite = max(p[0] for p in proben) * 2
    tiefe = max(p[1] for p in proben) * 2

    umkreis = 0.0
    for j in range(180):
        x, y = superellipse(breite / 2, tiefe / 2, n, j, 720)
        umkreis = max(umkreis, 2.0 * math.hypot(x, y))

    engste = min(umkreis,                                  # laengs der Achse
                 math.hypot(tiefe, hoehe),                 # quer, schmale Seite
                 math.hypot(breite, hoehe))                # quer, breite Seite
    return dict(breite=breite, tiefe=tiefe, hoehe=hoehe, engste=engste)


if __name__ == "__main__":
    for name, v in VARIANTEN.items():
        tri = baue_netz(v["profil"], v["bohr"], v["n_quer"])
        schreibe_stl(tri, v["datei"], f"Tuerzwerg {v['titel']} - Masse in mm")
        k = kennzahlen(v)
        vol = volumen(tri)
        wand, _ = duennste_wand(v["profil"], v["bohr"])
        ueber, ueber_h = max_ueberhang(v["profil"])
        umfang = griffumfang(v["griff"][0] / 2, v["griff"][1] / 2)
        print(f"\n{v['titel']}  ->  {v['datei']}")
        print(f"  Abmessungen   {k['breite']:.0f} x {k['tiefe']:.0f} x "
              f"{k['hoehe']:.0f} mm")
        print(f"  Dreiecke      {len(tri)}")
        print(f"  Offene Kanten {offene_kanten(tri)}")
        print(f"  Volumen       {vol/1000:.1f} cm^3   ({vol/1000*1.15:.0f} g Silikon)")
        print(f"  Griffzone     {v['griff'][0]:.0f} x {v['griff'][1]:.0f} mm, "
              f"Umfang {umfang:.0f} mm")
        print(f"  Duennste Wand {wand:.2f} mm")
        print(f"  Max Ueberhang {ueber:.1f} Grad bei h = {ueber_h:.1f} mm")
        eng = k["engste"]
        print(f"  Engste Oeffnung    {eng:.1f} mm  "
              f"-> Kleinball 44,5: {'besteht' if eng > 44.5 else 'faellt durch'}"
              f" | Zylinder 31,7 x 57,1: "
              f"{'besteht' if (eng > 31.7 or k['hoehe'] > 57.1) else 'PRUEFEN'}")
