#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer den Reif (Rev. A, Ø 72 x 14)

Dreiteilige Form zum Ausgiessen mit Silikon, gedacht fuer den FDM-Druck.
Die Kavitaet ist der Reif aus reif.py, Rev. A, unveraendert.

Warum drei Teile und nicht zwei.

Geteilt wird in der Reifebene, z = 7. Der Bandquerschnitt ist zu dieser
Ebene symmetrisch und dort am breitesten - jede andere Teilung schnitte
schraeg durch die Fasen. Nur hat der Reif einen Hohlraum, den die beiden
anderen Teile nicht hatten: die Knotenkammer liegt vollstaendig im Band,
mit 2,5 mm Material darueber und darunter. Ihr Kern haengt also ueber dem
Silikon und sperrt es ein. hinterschnitt() zaehlt das nach: 640 von 10345
Materialsaeulen sind gesperrt, bis zu 4,6 mm tief. Ein zweiteiliges
Werkzeug liesse sich nur oeffnen, indem man den Reif ueber den Kammerkern
zerrt.

Deshalb bilden Kammer und Schnurbohrung ein eigenes, loses Teil. Es wird
vor dem Schliessen eingelegt, mit dem 5-mm-Zapfen in einer Buchse im
Aussenblock und mit dem hinteren Ende in einem Schlitz im Mittelklotz.
Beide Sitze liegen in der Trennebene und oeffnen sich mit der Form; der
Kern bleibt im Gussteil stecken und wird danach radial nach innen
herausgezogen. Er ist ueber seine ganze Laenge prismatisch bzw. zylin-
drisch und nach innen hin nie schmaler, laesst sich also nur in diese
eine Richtung ziehen - nachgerechnet in kern_ziehbar().

Der Kern traegt auch die Verrundung, mit der die Kammer in die Oeffnung
muendet. Im Bauteil entsteht sie durch eine weiche Subtraktion; ein
Kern mit scharfer Kante wuerde sie verlieren. Er ist deshalb nicht als
Kammer modelliert, sondern als genau das Volumen, das dem Reifkoerper
fehlt: koerper minus Bauteil.

Gedruckt wird flach, Trennflaeche nach oben. Die Kavitaet ist dann eine
nach oben offene Rille, und die 40-Grad-Fasen des Reifs arbeiten dabei
fuer uns: der Querschnitt wird nach oben breiter, es entsteht nirgends
eine Decke. Die Trennflaeche ist zugleich die oberste Druckschicht und
damit so plan, wie der Drucker es kann.

Gegossen wird hochkant, der Reif steht wie ein Rad. Die Schnurbohrung
zeigt dabei waagerecht zur Seite; oben und unten hat die Kavitaet dann je
genau einen Punkt. Angegossen wird unten, entlueftet oben, gefuellt also
von unten nach oben. Das Silikon laeuft vom Trichter in einem Bogen
aussen um den Reif herum nach unten - der Bogen liegt als Rille in der
Trennflaeche der Haelfte A, damit sich der erstarrte Anguss seitlich mit
herausheben laesst.

    python3 giessform_reif.py
"""

import math

import reif as R
from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, schreibe_3mf,
                  quader, zapfen)

# ---------------------------------------------------------------- Bauteil ---

REIF = R.VARIANTEN[0]                   # Rev. A
R_AUSSEN = REIF.r_aussen                # 36
HALB = REIF.halb                        # 7 - halbe Dicke, zugleich Trennebene
DICKE = REIF.dicke                      # 14

# ------------------------------------------------------------------ Form ----

XY_HALB = 46.0                          # halbe Blockbreite
Z_UNTEN = -5.0                          # Boden unter dem Reif
Z_TRENN = HALB

# Loser Kern
TAB_Y0 = 10.0                           # hinteres Ende im Mittelklotz
TAB_BIS = 17.0                          # bis hierhin steckt der Kern im Klotz
PIN_Y1 = 41.0                           # Zapfenspitze in der Buchse
LUFT = 0.15                             # Sitzluft fuer Schlitz und Buchse

# Zentrierung: senkrechte Zapfen, in dieser Drucklage die einfachste Form
# ueberhaupt - jede Schicht liegt vollstaendig auf der darunter.
ZAPFEN_XY = 38.0
ZAPFEN_R, ZAPFEN_NUT_R = 3.0, 3.2
ZAPFEN_SPITZE = 12.0                    # Kegelspitze, volle Hoehe bis z = 9
NUT_BODEN = 1.5

# Kanalsystem, vollstaendig in Haelfte A. Giesslage: +x ist oben.
R_LAUF = 41.0                           # 2,5 mm Wand zur Kavitaet
LAUF_R = 2.5
# Der Bogen laeuft ueber die y < 0 Seite. Ueber y > 0 waere er durch
# die Buchse des losen Kerns gegangen - beide liegen dort bei x = 0.
LAUF_AB_GRAD = 20.0                     # Bogenanfang, gemessen von +x nach -y
TR_X0 = 38.5                            # Trichter beginnt am Bogenende
TR_AB = 43.0                            # ab hier oeffnet er sich mit 45 Grad
TR_R = LAUF_R + (XY_HALB - TR_AB)       # 6,0
ANSCHNITT_R = 2.0
ANSCHNITT_X = (-XY_HALB + 3.0, -34.0)   # vom Bogenende in die Kavitaet
ENTL_R = 1.0
ENTL_X0 = 34.0

SPALT = 8.0
RASTER = 0.6
DATEI_A = "tuerzwerg-giessform-reif-a.stl"      # mit Kanalsystem
DATEI_B = "tuerzwerg-giessform-reif-b.stl"      # glatt
DATEI_K = "tuerzwerg-giessform-reif-kern.stl"   # loser Kern
DATEI_3MF = "tuerzwerg-giessform-reif.3mf"      # alles in einer Datei

_S20 = math.sin(math.radians(LAUF_AB_GRAD))
_C20 = math.cos(math.radians(LAUF_AB_GRAD))
_Y_TR = -R_LAUF * _S20                  # -14,02, Bogen liegt bei y < 0
_SCHRAEG = 0.7071067811865476


# ------------------------------------------------------------- Distanzfeld ---

def koerper(x, y, z):
    """Der Reifkoerper ohne Kammer und ohne Schnurbohrung.

    Das ist der Raum, den Silikon und Kern zusammen ausfuellen.
    """
    zz = z - HALB
    rho = math.hypot(x, y)
    if rho < 1e-9:
        rho = 1e-9
    a = REIF.breite(y / rho) / 2.0
    u = rho - (R_AUSSEN - a)
    K = REIF.kante
    return R._achteck(u, zz, a - K, HALB - K, REIF._g(a) - K) - K


def _quer(x, zz):
    """Querschnitt der Knotenkammer, wie in reif.py."""
    gk = (REIF.a_kammer * R._CF
          + (REIF.b_kammer - REIF.fase_z_kammer) * R._SF) - R.KANTE
    return R._achteck(x, zz, REIF.a_kammer - R.KANTE,
                      REIF.b_kammer - R.KANTE, gk) - R.KANTE


def kern(x, y, z):
    """Der lose Kern.

    Sein formender Teil ist nicht die Kammer, sondern das, was dem
    Reifkoerper zum Bauteil fehlt - damit ist die weiche Verrundung an
    der Kammermuendung mit im Kern und geht nicht verloren.
    """
    zz = z - HALB
    formend = max(koerper(x, y, z), -REIF.feld(x, y, z))
    fuehrung = max(_quer(x, zz), TAB_Y0 - y, y - TAB_BIS)
    stift = max(math.hypot(x, zz) - R.D_SCHNUR / 2.0, R_AUSSEN - y, y - PIN_Y1)
    return min(formend, fuehrung, stift)


def sitz(x, y, z):
    """Schlitz im Mittelklotz und Buchse im Aussenblock, mit Sitzluft.

    Beide sind aus den Grundformen aufgebaut und nicht aus kern(). Das
    ist kein Umweg, sondern noetig: kern() liefert abseits von Kammer und
    Bohrung den Betrag von koerper(), also einen kleinen positiven Wert
    dicht an der Kavitaetswand. Um LUFT verkleinert wuerde daraus ein
    negativer Saum rings um die ganze Kavitaet - die Form waere ueberall
    0,15 mm zu weit.
    """
    zz = z - HALB
    schlitz = max(_quer(x, zz) - LUFT, TAB_Y0 - 1.0 - y, y - TAB_BIS)
    buchse = max(math.hypot(x, zz) - R.D_SCHNUR / 2.0 - LUFT,
                 R_AUSSEN - y, y - PIN_Y1 - 1.0)
    return min(schlitz, buchse)


def kanal(x, y, z):
    """Trichter, Bogen, Anschnitt und Entlueftung - Rillen in z <= Z_TRENN."""
    rho = math.hypot(x, y)
    bogen = max(math.hypot(rho - R_LAUF, z - Z_TRENN) - LAUF_R,
                y, x * _S20 + y * _C20, z - Z_TRENN)

    rad = math.hypot(y - _Y_TR, z - Z_TRENN)
    ueber = x - TR_AB
    d = rad - LAUF_R if ueber <= 0.0 else (rad - LAUF_R - ueber) * _SCHRAEG
    trichter = max(d, TR_X0 - x, z - Z_TRENN)

    rad2 = math.hypot(y, z - Z_TRENN)
    anschnitt = max(rad2 - ANSCHNITT_R, ANSCHNITT_X[0] - x,
                    x - ANSCHNITT_X[1], z - Z_TRENN)

    entl = max(rad2 - ENTL_R, ENTL_X0 - x, z - Z_TRENN)
    return min(bogen, trichter, anschnitt, entl)


def haelfte(x, y, z, mit_kanaelen):
    """Signierter Abstand einer Formhaelfte. Negativ ist Material.

    Material liegt bei z <= Z_TRENN, die Zentrierzapfen stehen darueber
    hinaus. Beide Haelften sind gleich gebaut; nur Haelfte A traegt das
    Kanalsystem.
    """
    d = quader(x, y, z, -XY_HALB, XY_HALB, -XY_HALB, XY_HALB,
               Z_UNTEN, Z_TRENN)

    # Zentriernuten
    for nx, ny in ((-ZAPFEN_XY, ZAPFEN_XY), (ZAPFEN_XY, -ZAPFEN_XY)):
        nut = max(math.hypot(x - nx, y - ny) - ZAPFEN_NUT_R, NUT_BODEN - z)
        d = max(d, -nut)

    # Kavitaet: die untere Haelfte des Reifkoerpers. Kammer und Bohrung
    # gehoeren nicht dazu - die fuellt der lose Kern.
    d = max(d, -max(koerper(x, y, z), z - Z_TRENN))

    # Sitze fuer den Kern
    d = max(d, -max(sitz(x, y, z), z - Z_TRENN))

    if mit_kanaelen:
        d = max(d, -kanal(x, y, z))

    # Zentrierzapfen
    for px, py in ((ZAPFEN_XY, ZAPFEN_XY), (-ZAPFEN_XY, -ZAPFEN_XY)):
        zap = max(zapfen(math.hypot(x - px, y - py), z, ZAPFEN_R,
                         None, ZAPFEN_SPITZE), Z_UNTEN - z)
        d = min(d, zap)
    return d


def feld_a(x, y, z):
    return haelfte(x, y, z, True)


def feld_b(x, y, z):
    return haelfte(x, y, z, False)


def grenzen_halb():
    return ((-XY_HALB - 1.5, XY_HALB + 1.5),
            (-XY_HALB - 1.5, XY_HALB + 1.5),
            (Z_UNTEN - 1.5, ZAPFEN_SPITZE + 1.5))


def grenzen_kern():
    return ((-REIF.a_kammer - 3.0, REIF.a_kammer + 3.0),
            (TAB_Y0 - 1.5, PIN_Y1 + 1.5),
            (HALB - REIF.b_kammer - 3.0, HALB + REIF.b_kammer + 3.0))


# -------------------------------------------------------------- Kennzahlen --

def hinterschnitt(schritt=0.5, fein=0.1):
    """Sperrt ueber Kavitaetsmaterial irgendwo wieder Formmaterial?

    Geprueft wird die Kavitaet der Haelften, also der Reifkoerper mit
    Kammer und Bohrung als Teil des Hohlraums. Jede Materialsaeule muss
    von ihrem tiefsten Punkt durchgehend bis zur Trennebene reichen.
    """
    schlimm = gepr = 0
    tiefe, wo = 0.0, None
    y = -R_AUSSEN
    while y <= R_AUSSEN:
        x = -R_AUSSEN
        while x <= R_AUSSEN:
            drin, z = [], fein / 2.0
            while z <= Z_TRENN:
                drin.append(koerper(x, y, z) < 0.0)
                z += fein
            if any(drin):
                gepr += 1
                erst = drin.index(True)
                luecken = sum(1 for i in range(erst, len(drin)) if not drin[i])
                if luecken:
                    schlimm += 1
                    if luecken * fein > tiefe:
                        tiefe, wo = luecken * fein, (x, y)
            x += schritt
        y += schritt
    return schlimm, gepr, tiefe, wo


def kern_ziehbar(schritt=0.3):
    """Laesst sich der Kern nach innen (-y) aus dem Gussteil ziehen?

    Der Kern wird gedanklich nach -y verschoben; ueberstrichen wird an
    jeder Stelle (x, z) alles unterhalb seines groessten y. Sperren
    wuerde nur Bauteilmaterial in diesem ueberstrichenen Bereich - nicht
    etwa eine Luecke im Kern selbst, denn hinter der Muendung haelt ihn
    nichts mehr.
    """
    schlimm = gepr = 0
    x = -REIF.a_kammer - 2.5
    while x <= REIF.a_kammer + 2.5:
        z = HALB - REIF.b_kammer - 2.5
        while z <= HALB + REIF.b_kammer + 2.5:
            y, y_max = R_AUSSEN + 4.0, None
            while y >= TAB_Y0:
                if kern(x, y, z) < 0.0 and y_max is None:
                    y_max = y
                y -= schritt
            if y_max is not None:
                gepr += 1
                y = y_max
                while y >= TAB_Y0:
                    if REIF.feld(x, y, z) < 0.0 and kern(x, y, z) > 0.0:
                        schlimm += 1
                        break
                    y -= schritt
            z += schritt
        x += schritt
    return schlimm, gepr


def kavitaet_volumen(schritt=0.4):
    """Bauteilvolumen und Kernvolumen."""
    vt = vk = 0.0
    zelle = schritt ** 3
    x = -R_AUSSEN
    while x <= R_AUSSEN:
        y = -R_AUSSEN
        while y <= R_AUSSEN:
            z = 0.0
            while z <= DICKE:
                if REIF.feld(x, y, z) < 0.0:
                    vt += zelle
                elif koerper(x, y, z) < 0.0:
                    vk += zelle
                z += schritt
            y += schritt
        x += schritt
    return vt, vk


def engste_wand(schritt=0.6):
    """Duennste Formwand zwischen Kavitaet und Bogen, Zentriernut oder
    Aussenflaeche. Die Trennebene zaehlt nicht - dort steht die
    Gegenhaelfte. Anschnitt, Entlueftung und Kernsitze sind gewollte
    Durchbrueche und bleiben aussen vor.
    """
    def wandfeld(x, y, z):
        d = quader(x, y, z, -XY_HALB, XY_HALB, -XY_HALB, XY_HALB,
                   Z_UNTEN, 1e4)
        rho = math.hypot(x, y)
        bogen = max(math.hypot(rho - R_LAUF, z - Z_TRENN) - LAUF_R,
                    y, x * _S20 + y * _C20, z - Z_TRENN)
        d = max(d, -bogen)
        for nx, ny in ((-ZAPFEN_XY, ZAPFEN_XY), (ZAPFEN_XY, -ZAPFEN_XY)):
            nut = max(math.hypot(x - nx, y - ny) - ZAPFEN_NUT_R, NUT_BODEN - z)
            d = max(d, -nut)
        return d

    best = (1e9, None)
    x = -R_AUSSEN - 1.0
    while x <= R_AUSSEN + 1.0:
        y = -R_AUSSEN - 1.0
        while y <= R_AUSSEN + 1.0:
            z = -0.5
            while z <= Z_TRENN:
                if abs(koerper(x, y, z)) < 0.25:
                    w = -wandfeld(x, y, z)
                    if 0.0 < w < best[0]:
                        best = (w, (x, y, z))
                z += schritt
            y += schritt
        x += schritt
    return best


def kanal_gegen_sitz(schritt=0.3):
    """Schneidet das Kanalsystem irgendwo in einen Kernsitz?

    Ein Treffer hiesse, dass Silikon am Zapfen entlanglaeuft und der
    Kern seine Fuehrung verliert.
    """
    treffer = 0
    x = -XY_HALB
    while x <= XY_HALB:
        y = -XY_HALB
        while y <= XY_HALB:
            z = Z_TRENN - LAUF_R - 1.0
            while z <= Z_TRENN:
                if sitz(x, y, z) < 0.0 and kanal(x, y, z) < 0.0:
                    treffer += 1
                z += schritt
            y += schritt
        x += schritt
    return treffer


def fuellweg(schritt=0.6):
    """Flutet die geschlossene Form vom Trichter aus.

    Gitter auf allen Achsen um einen halben Schritt versetzt, damit kein
    Punkt genau auf die Trennebene faellt - dort laesen beide Haelften
    ihren Rand und die Flut kaeme nicht hinueber.
    """
    def frei(x, y, z):
        # Haelfte B liegt gewendet: um die y-Achse gedreht.
        if min(feld_a(x, y, z), feld_b(-x, y, DICKE - z)) <= 0.05:
            return False
        return kern(x, y, z) > 0.05

    def auf(v):
        return (round(v / schritt - 0.5) + 0.5) * schritt

    def idx(p):
        return tuple(round(c / schritt - 0.5) for c in p)

    start = tuple(auf(c) for c in (XY_HALB - 1.0, _Y_TR, Z_TRENN - 0.5))
    gesehen, stapel = {idx(start)}, [start]
    while stapel:
        p = stapel.pop()
        for d in ((schritt, 0, 0), (-schritt, 0, 0), (0, schritt, 0),
                  (0, -schritt, 0), (0, 0, schritt), (0, 0, -schritt)):
            q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if not (-XY_HALB < q[0] < XY_HALB and -XY_HALB < q[1] < XY_HALB
                    and Z_UNTEN < q[2] < DICKE - Z_UNTEN):
                continue
            k = idx(q)
            if k in gesehen or not frei(*q):
                continue
            gesehen.add(k)
            stapel.append(q)

    ges = err = 0
    x = auf(-R_AUSSEN)
    while x <= R_AUSSEN:
        y = auf(-R_AUSSEN)
        while y <= R_AUSSEN:
            z = auf(0.0)
            while z <= DICKE:
                if REIF.feld(x, y, z) < -0.5:
                    ges += 1
                    if idx((x, y, z)) in gesehen:
                        err += 1
                z += schritt
            y += schritt
        x += schritt
    entl = idx(tuple(auf(c) for c in
                     (XY_HALB - 1.0, 0.0, Z_TRENN))) in gesehen
    return err, ges, entl


if __name__ == "__main__":
    print("Vernetze Haelfte A ...")
    tri_a = vernetzen(feld_a, grenzen_halb(), RASTER)
    print("Vernetze Haelfte B ...")
    tri_b = vernetzen(feld_b, grenzen_halb(), RASTER)
    print("Vernetze Kern ...")
    tri_k = vernetzen(kern, grenzen_kern(), RASTER * 0.5)

    def richte(tri):
        v = volumen(tri)
        if v < 0:
            return [(a, c, b) for a, b, c in tri], -v
        return tri, v

    tri_a, vol_a = richte(tri_a)
    tri_b, vol_b = richte(tri_b)
    tri_k, vol_k = richte(tri_k)

    ab_max, ab_mit = abweichung(feld_a, tri_a)

    def schiebe(tri, dx, dy=0.0, dz=0.0):
        return [tuple((p[0] + dx, p[1] + dy, p[2] + dz) for p in t)
                for t in tri]

    # Kern aufrichten: Laengsachse y wird zur Druckachse z
    kern_druck = [tuple((p[0], p[2] - HALB, p[1] - TAB_Y0) for p in t)
                  for t in tri_k]
    kern_druck = [(a, c, b) for a, b, c in kern_druck]      # Spiegelung heilen

    # Drei getrennte Dateien: zusammen waeren es 55 MB, mehr als sich
    # bequem verschicken laesst. Jedes Teil wird einzeln gedruckt.
    a_druck = schiebe(tri_a, 0.0, 0.0, -Z_UNTEN)
    b_druck = schiebe(tri_b, 0.0, 0.0, -Z_UNTEN)
    schreibe_stl(a_druck, DATEI_A,
                 "Tuerzwerg Giessform Reif A mit Kanaelen - mm")
    schreibe_stl(b_druck, DATEI_B, "Tuerzwerg Giessform Reif B glatt - mm")
    schreibe_stl(kern_druck, DATEI_K, "Tuerzwerg Giessform Reif Kern - mm")
    # Alles in einer Datei, schon auf dem Bett verteilt. 3MF statt STL:
    # als STL waeren dieselben Daten 55 MB.
    schreibe_3mf(
        [("Haelfte A mit Kanalsystem", a_druck, (50.0, 50.0, 0.0)),
         ("Haelfte B glatt", b_druck, (150.0, 50.0, 0.0)),
         ("Loser Kern", kern_druck, (100.0, 105.0, 0.0))],
        DATEI_3MF, "Tuerzwerg Giessform Reif Rev. A",
        "Alle drei Teile flach drucken, wie sie liegen. PLA, 0,2 mm "
        "Schicht, mindestens 4 Perimeter, 30 Prozent Infill, keine "
        "Stuetzen. Die nach oben zeigende Flaeche der beiden Haelften "
        "ist die Trennflaeche - Bauteilkuehler an, damit sie plan wird.")

    tri = a_druck + b_druck + kern_druck
    kanten = (offene_kanten(a_druck), offene_kanten(b_druck),
              offene_kanten(kern_druck))

    anteil, grad, flaeche = ueberhang(tri)
    vt, vkav = kavitaet_volumen()
    schlimm, gepr, tiefe, wo = hinterschnitt()
    kz_s, kz_n = kern_ziehbar()
    err, ges, entl = fuellweg()
    wand, wo = engste_wand()
    kollision = kanal_gegen_sitz()

    print(f"\nDateien         {DATEI_A}")
    print(f"                {DATEI_B}")
    print(f"                {DATEI_K}")
    print(f"                {DATEI_3MF}  <- alles in einer Datei")
    print(f"Eine Haelfte    {2*XY_HALB:.0f} x {2*XY_HALB:.0f} x "
          f"{Z_TRENN-Z_UNTEN:.0f} mm, Zapfen {ZAPFEN_SPITZE-Z_TRENN:.0f} mm hoch")
    print(f"Zusammengesetzt {2*XY_HALB:.0f} x {2*XY_HALB:.0f} x "
          f"{2*(Z_TRENN-Z_UNTEN):.0f} mm")
    print(f"Kern            {PIN_Y1-TAB_Y0:.0f} mm lang, {vol_k/1000:.2f} cm^3")
    print(f"Dreiecke        {len(tri)}")
    print(f"Offene Kanten   A {kanten[0]}, B {kanten[1]}, Kern {kanten[2]}  "
          f"(je 0 = geschlossenes Volumen)")
    print(f"Formvolumen     {vol_a/1000:.0f} + {vol_b/1000:.0f} cm^3 brutto")
    print(f"Bauteil         {vt/1000:.2f} cm^3 ({vt/1000*1.15:.0f} g Silikon)")
    print(f"Hinterschnitt   {schlimm} von {gepr} Saeulen"
          + (f", tiefste {tiefe:.1f} mm bei x={wo[0]:.0f} y={wo[1]:.0f}"
             if wo else "  (0 = Haelften lassen sich abheben)"))
    print(f"Kern ziehbar    {kz_s} von {kz_n} Stellen sperren "
          f"(0 = laesst sich nach innen ziehen)")
    print(f"Fuellweg        {100.0*err/ges:.1f} % der Kavitaet vom Einguss "
          f"erreichbar, Entlueftung {'an' if entl else 'AB'}")
    print(f"Duennste Wand   {wand:.1f} mm"
          + (f" bei x={wo[0]:.0f} y={wo[1]:.0f} z={wo[2]:.1f}" if wo else ""))
    print(f"Kanal/Kernsitz  {kollision} Ueberschneidungen (0 = getrennt)")
    print(f"Zentrierung     2 Zapfen {2*ZAPFEN_R:.0f} mm gegen Nut "
          f"{2*ZAPFEN_NUT_R:.1f} mm, {ZAPFEN_NUT_R-ZAPFEN_R:.1f} mm Luft")
    print(f"Anguss          {2*ANSCHNITT_R:.0f} mm unten, Bogen "
          f"{2*LAUF_R:.0f} mm auf r = {R_LAUF:.0f}, Trichter {2*TR_R:.0f} mm")
    print(f"Entlueftung     {2*ENTL_R:.1f} mm oben")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm (Kern {RASTER*0.5:.2f} mm)")
