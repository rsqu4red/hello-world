#!/usr/bin/env python3
"""
Türzwerg – Der Reif als Schaumteil

Der Reif soll aussen weich sein, ohne beim Ziehen nachzugeben. Vollmaterial
kann das nicht: ein Elastomer, das steif genug waere, muesste so dick sein,
dass es zu schwer wird. Schaum kann es, weil er seine Steifigkeit aus dem
Querschnitt holt statt aus dem Modul - und Querschnitt kostet bei 200 bis
350 g/l fast kein Gewicht.

Ein Schaumteil ist ausserdem ein anderes Bauteil als ein gedrucktes. Es
wird aus der Platte gestanzt, nicht aufgebaut. Damit entfallen die
40-Grad-Fasen (die gab es nur wegen der Ueberhaenge beim Drucken) und die
Knotenkammer (in Schaum zieht sich der Knoten durch). Statt der Kammer
bekommt der Reif einen Schlitz fuer ein Gurtband.

Ausgegeben wird deshalb kein STL, sondern die Schnittkontur 1:1 als SVG -
das ist, was ein Stanzformbauer oder ein Laser braucht.

    python3 schaum.py
"""

import math

# ---------------------------------------------------------------- Parameter --

R_AUSSEN = 44.0         # Aussenradius, exakt rund
DICKE = 12.0            # Plattenstaerke

B_OBEN, B_SEITE, B_UNTEN = 24.0, 13.0, 17.0

# Schlitz fuer das Gurtband. Rundes Seil schneidet in Schaum ein - 17 N auf
# einen 3-mm-Strang sind rund 470 kPa, mehr als die Druckfestigkeit von
# EVA 350. Ein 15 mm breites Gurtband verteilt dieselbe Kraft auf
# 160 kPa. Das Band wird im Ankerstich durch den Schlitz gelegt.
SCHLITZ_BREITE = 15.0
SCHLITZ_R1, SCHLITZ_R2 = 34.0, 37.0     # radiale Lage
SCHLITZ_RUND = 1.5                      # Eckenradius, gegen Einreissen

F_BETRIEB = 17.0

# E-Modul und Dichte. Beide streuen mit Rezeptur und Aufschaeumgrad
# erheblich; die Groessenordnung nicht.
SCHAEUME = [
    ("EVA-Schaum 150 g/l",  4.0, 0.15),
    ("EVA-Schaum 200 g/l",  8.0, 0.20),
    ("EVA-Schaum 350 g/l", 25.0, 0.35),
    ("PU-Integralschaum",  30.0, 0.45),
]

A0 = (B_OBEN + 2.0 * B_SEITE + B_UNTEN) / 4.0
A1 = (B_OBEN - B_UNTEN) / 2.0
A2 = (B_OBEN - 2.0 * B_SEITE + B_UNTEN) / 4.0


def breite(ct):
    return A0 + A1 * ct + A2 * (2.0 * ct * ct - 1.0)


def innenradius(ct):
    return R_AUSSEN - breite(ct)


def oeffnung(n=2000):
    breit = hy = 0.0
    for i in range(n + 1):
        th = math.pi * i / n
        r = innenradius(math.cos(th))
        if 2.0 * r * math.sin(th) > breit:
            breit, hy = 2.0 * r * math.sin(th), r * math.cos(th)
    return breit, innenradius(1.0) + innenradius(-1.0), hy


def aufweitung(e_modul, kraft=F_BETRIEB):
    traegheit = DICKE * A0 ** 3 / 12.0
    return 0.149 * kraft * (R_AUSSEN - A0 / 2.0) ** 3 / (e_modul * traegheit)


def masse(dichte):
    flaeche = A0 * DICKE
    return flaeche * 2.0 * math.pi * (R_AUSSEN - A0 / 2.0) * dichte / 1000.0


# -------------------------------------------------------------- Schnittbild --

def _bogen(r, von, bis, n):
    return [(r * math.sin(von + (bis - von) * i / n),
             -r * math.cos(von + (bis - von) * i / n)) for i in range(n + 1)]


def kontur(n=720):
    aus = [(R_AUSSEN * math.sin(2 * math.pi * i / n),
            -R_AUSSEN * math.cos(2 * math.pi * i / n)) for i in range(n)]
    inn = [(innenradius(math.cos(2 * math.pi * i / n)) * math.sin(2 * math.pi * i / n),
            -innenradius(math.cos(2 * math.pi * i / n)) * math.cos(2 * math.pi * i / n))
           for i in range(n - 1, -1, -1)]
    return aus, inn


def schlitz():
    """Langloch mit verrundeten Ecken, als Pfad mit Boegen."""
    hb = SCHLITZ_BREITE / 2.0 - SCHLITZ_RUND
    r1, r2 = SCHLITZ_R1 + SCHLITZ_RUND, SCHLITZ_R2 - SCHLITZ_RUND
    k = SCHLITZ_RUND
    d = "M %.2f %.2f " % (-hb, -r1)
    d += "L %.2f %.2f " % (hb, -r1)
    d += "A %.2f %.2f 0 0 1 %.2f %.2f " % (k, k, hb + k, -r1 - k)
    d += "L %.2f %.2f " % (hb + k, -r2 + k)
    d += "A %.2f %.2f 0 0 1 %.2f %.2f " % (k, k, hb, -r2)
    d += "L %.2f %.2f " % (-hb, -r2)
    d += "A %.2f %.2f 0 0 1 %.2f %.2f " % (k, k, -hb - k, -r2 + k)
    d += "L %.2f %.2f " % (-hb - k, -r1 - k)
    d += "A %.2f %.2f 0 0 1 %.2f %.2f Z" % (k, k, -hb, -r1)
    return d


def schnittbild(datei):
    """Schnittkontur 1:1 in Millimetern - fuer Stanzform oder Laser."""
    aus, inn = kontur()
    rand = 4.0
    seite = 2.0 * (R_AUSSEN + rand)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" '
         'height="%.1fmm" viewBox="%.1f %.1f %.1f %.1f">'
         % (seite, seite, -R_AUSSEN - rand, -R_AUSSEN - rand, seite, seite)]
    s.append('<title>Tuerzwerg Reif Schaum - Schnittkontur 1:1 in mm</title>')
    stil = 'fill="none" stroke="#000000" stroke-width="0.25"'
    s.append('<path d="M %s Z" %s/>'
             % (" L ".join("%.3f %.3f" % p for p in aus), stil))
    s.append('<path d="M %s Z" %s/>'
             % (" L ".join("%.3f %.3f" % p for p in inn), stil))
    s.append('<path d="%s" %s/>' % (schlitz(), stil))
    s.append("</svg>")
    open(datei, "w").write("\n".join(s))
    return len("\n".join(s))


if __name__ == "__main__":
    br, ho, _ = oeffnung()
    print("Der Reif als Schaumteil")
    print("  Aussen         %.0f mm, Platte %.0f mm" % (2 * R_AUSSEN, DICKE))
    print("  Band           %.0f oben, %.0f seitlich, %.0f unten"
          % (B_OBEN, B_SEITE, B_UNTEN))
    print("  Oeffnung       %.1f breit x %.1f hoch" % (br, ho))
    print("  Schlitz        %.0f x %.0f mm bei r = %.0f..%.0f, "
          "Steg nach aussen %.0f mm"
          % (SCHLITZ_BREITE, SCHLITZ_R2 - SCHLITZ_R1, SCHLITZ_R1, SCHLITZ_R2,
             R_AUSSEN - SCHLITZ_R2))
    print("\n  Werkstoff              E     Aufweitung   Masse")
    for name, e, rho in SCHAEUME:
        print("  %-20s %4.0f MPa   %5.2f mm    %4.1f g"
              % (name, e, aufweitung(e), masse(rho)))

    print("\n  Pressung des Zugmittels am Schlitz bei %.0f N:" % F_BETRIEB)
    steg = R_AUSSEN - SCHLITZ_R2
    for nam, br_z in (("Seil 3 mm", 3.0), ("Gurtband 10 mm", 10.0),
                      ("Gurtband 15 mm", 15.0)):
        print("    %-16s %5.0f kPa" % (nam, F_BETRIEB / (br_z * steg) * 1000))
    print("    EVA 350 g/l haelt rund 300 bis 600 kPa.")

    n = schnittbild("tuerzwerg-reif-schaum.svg")
    print("\n  Schnittkontur   tuerzwerg-reif-schaum.svg  (%.1f KB, 1:1 in mm)"
          % (n / 1024))
