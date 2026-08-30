#!/usr/bin/env python3
"""
Türzwerg – Greifbarkeit und Werkstoffwahl fuer den Reif

Zwei Fragen, die ueber die Geometrie allein nicht zu beantworten sind:
kann eine Kinderhand das untere Band umgreifen, und was passiert, wenn der
Reif statt aus PLA aus einem weichen Werkstoff besteht.

Die zweite Frage entscheidet ueber die Bauform. Ein Reif traegt seine Last
ueber Biegung im Band - anders als ein massiver Griff, der nur auf Zug
belastet wird. Biegung geht linear mit dem Elastizitaetsmodul, und
zwischen Silikon und PLA liegen drei Zehnerpotenzen.

    python3 werkstoff.py
"""

import math

import reif as R

# ---------------------------------------------------------------- Annahmen --

# Betaetigungskraft. Ein Tuerdruecker braucht rund 1,5 Nm, um die Falle
# zurueckzuziehen; die Schnur greift etwa 90 mm von der Drueckerachse an.
DREHMOMENT = 1.5        # Nm
HEBEL_DRUECKER = 0.090  # m
F_BETRIEB = DREHMOMENT / HEBEL_DRUECKER
F_MISSBRAUCH = 80.0     # N - Kind haengt sich mit vollem Gewicht hinein

# Elastizitaetsmoduln in MPa. Fuer Elastomere aus der Shore-Haerte
# abgeleitet; die Werte streuen je nach Rezeptur, die Groessenordnung nicht.
WERKSTOFFE = [
    ("Silikon Shore A 40",   1.5, "weich, LSR fuer Kinderartikel"),
    ("Silikon Shore A 60",   3.3, "das haerteste uebliche Silikon"),
    ("TPU Shore A 85",      12.0, "weicher Druck-TPU"),
    ("TPU Shore A 95",      30.0, "gaengiger Druck-TPU"),
    ("TPU Shore D 55",      75.0, "harter TPU, fast schon Kunststoff"),
    ("Polypropylen",      1400.0, "Spritzguss, zaeh"),
    ("PETG",              2100.0, "Druck, zaeher als PLA"),
    ("PLA",               3500.0, "Druck, sproede"),
]

# Kinderhand, Anhaltswerte aus der Kinderanthropometrie. Solche Tabellen
# streuen deutlich; die Zahlen taugen zum Auslegen, nicht zum Nachweis.
HAND = [
    ("18 Monate", 90.0, 44.0, 10.0, 25.0),
    ("2 Jahre",   97.0, 48.0, 11.0, 35.0),
    ("3 Jahre",  105.0, 53.0, 12.0, 50.0),
]   # Name, Handlaenge, Handbreite, Fingerdicke, Griffkraft [N]

# Fuer Erwachsene liegt der guenstigste Griffdurchmesser bei 30 bis 45 mm
# bei rund 185 mm Handlaenge. Linear auf die Kinderhand skaliert ergibt das
# den Zielbereich unten.
ERW_HANDLAENGE = 185.0
ERW_GRIFF = (30.0, 45.0)


# ------------------------------------------------------------- Querschnitt --

def _sdf(reif, a, u, z):
    return R._achteck(u, z, a - R.KANTE, reif.halb - R.KANTE,
                      reif._g(a) - R.KANTE) - R.KANTE


def umfang(reif, cos_theta, n=1440):
    """Umfang des Bandquerschnitts - das Mass, das die Hand umschliesst."""
    a = reif.breite(cos_theta) / 2.0
    pkt = []
    for i in range(n):
        w = 2.0 * math.pi * i / n
        cw, sw = math.cos(w), math.sin(w)
        lo, hi = 0.0, a + reif.halb + 4.0
        for _ in range(44):
            m = 0.5 * (lo + hi)
            if _sdf(reif, a, m * cw, m * sw) < 0.0:
                lo = m
            else:
                hi = m
        r = 0.5 * (lo + hi)
        pkt.append((r * cw, r * sw))
    return sum(math.dist(pkt[i], pkt[(i + 1) % n]) for i in range(n))


# ----------------------------------------------------------- Ringsteifigkeit --

def aufweitung(reif, e_modul, kraft):
    """Wie weit zieht sich der Reif unter der Last in die Laenge?

    Ein Kreisring, oben gehalten und unten gezogen, ist der klassische Fall
    des diametral belasteten Rings. Die Aufweitung in Lastrichtung betraegt
    (pi/4 - 2/pi) * F * R^3 / (E * I). Als Flaechenmoment wird die mittlere
    Bandbreite eingesetzt - die tatsaechliche Breite schwankt ueber den
    Umfang, und zwar gegenlaeufig zum Biegemoment: oben und unten, wo das
    Moment am groessten ist, ist auch das Band am breitesten.
    """
    b = reif.a0                       # mittlere Bandbreite
    traegheit = reif.dicke * b ** 3 / 12.0
    r_mitte = reif.r_aussen - b / 2.0
    return 0.149 * kraft * r_mitte ** 3 / (e_modul * traegheit)


def flaechenpressung(reif, kraft, fingerdicke, finger=4):
    """Druck auf die Fingerglieder. Die Auflage ist so breit wie das Band
    tief ist, mal der Zahl der Finger mal ihrer Dicke - konservativ nur die
    halbe Umschlingung gerechnet."""
    auflage = finger * fingerdicke * reif.dicke * 0.5
    return kraft / auflage * 1000.0   # kPa


if __name__ == "__main__":
    reif = R.REV_D
    print("Der Reif, Rev. D - %0.f x %0.f x %0.f mm, Band %0.f/%0.f/%0.f\n"
          % (2 * reif.r_aussen, 2 * reif.r_aussen, reif.dicke,
             reif.b_oben, reif.b_seite, reif.b_unten))

    print("Kraefte")
    print("  Betaetigung   %4.1f N   (%.1f Nm Drueckermoment, %.0f mm Hebel)"
          % (F_BETRIEB, DREHMOMENT, HEBEL_DRUECKER * 1000))
    print("  Missbrauch    %4.1f N   (Kind haengt sich hinein)\n"
          % F_MISSBRAUCH)

    print("Frage 1 - kann die Hand das untere Band umgreifen?\n")
    u_unten = umfang(reif, -1.0)
    d_gleich = u_unten / math.pi
    print("  Bandquerschnitt unten   %.0f x %.0f mm" % (reif.b_unten, reif.dicke))
    print("  Umfang                  %.0f mm" % u_unten)
    print("  entspricht einem Rundstab von %.0f mm Durchmesser\n" % d_gleich)
    print("  Alter        Handlaenge  Zielgriff   Umschliessung   Pressung"
          "   Kraft")
    for name, hl, hb, fd, kraft in HAND:
        ziel = (ERW_GRIFF[0] * hl / ERW_HANDLAENGE,
                ERW_GRIFF[1] * hl / ERW_HANDLAENGE)
        # Wie weit reicht die Hand um den Querschnitt? Als Mass die halbe
        # Handlaenge gegen den halben Umfang.
        reicht = hl * 0.5 / (u_unten * 0.5)
        p = flaechenpressung(reif, F_BETRIEB, fd)
        print("  %-11s %5.0f mm   %2.0f-%2.0f mm    %4.1f-fach       "
              "%3.0f kPa   %2.0f von %.0f N"
              % (name, hl, ziel[0], ziel[1], reicht, p, F_BETRIEB, kraft))

    print("\nFrage 2 - was macht ein weicher Werkstoff mit dem Reif?\n")
    print("  Werkstoff              E-Modul   Aufweitung bei %2.0f N   bei %0.f N"
          % (F_BETRIEB, F_MISSBRAUCH))
    for name, e, _ in WERKSTOFFE:
        a1 = aufweitung(reif, e, F_BETRIEB)
        a2 = aufweitung(reif, e, F_MISSBRAUCH)
        urteil = ("unbrauchbar" if a1 > 10 else
                  "grenzwertig" if a1 > 3 else "brauchbar")
        print("  %-20s %6.0f MPa   %8.1f mm   %11.1f mm   %s"
              % (name, e, a1, a2, urteil))

    print("\n  Welche Bandbreite braeuchte Silikon Shore A 60 fuer 3 mm?")
    e = 3.3
    r_mitte = reif.r_aussen - reif.a0 / 2.0
    noetig = 0.149 * F_BETRIEB * r_mitte ** 3 / (e * 3.0)
    b3 = 12.0 * noetig / reif.dicke
    b_noetig = b3 ** (1 / 3.0)
    oeff = 2.0 * (reif.r_aussen - b_noetig)
    print("  Flaechenmoment %.0f mm^4 statt %.0f - Band %.0f mm statt %.0f."
          % (noetig, reif.dicke * reif.a0 ** 3 / 12.0, b_noetig, reif.a0))
    print("  Bei 86 mm Aussendurchmesser schrumpft die Oeffnung damit auf "
          "rund %.0f mm" % oeff)
    print("  und liegt unter der von Rev. A. Genau die Oeffnung war der Zweck.")
