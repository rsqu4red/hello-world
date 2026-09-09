#!/usr/bin/env python3
"""
Türzwerg – Giessform fuer den Griff (Kehle, Schaft 15, Kehle 13)

Zweiteilige Form zum Ausgiessen mit Silikon, gedacht fuer den FDM-Druck.

Die entscheidenden Entscheidungen:

Teilung durch die Achse. Der Griff ist ein Drehkoerper; eine Ebene durch
seine Achse schneidet ihn hinterschnittfrei in zwei Haelften. Jede andere
Teilung erzeugt Hinterschnitte am Bauch.

Eine Datei, zweimal gedruckt. Die Haelfte ist so gebaut, dass sie zu sich
selbst passt: Rippe rechts, Nut links, beide spiegelbildlich zur Achse.
Dreht man die zweite gedruckte Haelfte um 180 Grad um die Hochachse,
treffen Rippe auf Nut und Nut auf Rippe.

Kerne statt Einlegeteile. Die Schnurbohrung und die Knotenkammer sind
angeformt, nicht eingelegt. Das geht nur, weil beide an einem Ende offen
sind: die Kammer oeffnet zur Bodenflaeche, und der 5-mm-Kern waechst aus
ihr heraus. Beim Drucken steht der Kern damit auf dem Bett und ist bis
oben durchgehend gestuetzt - ein freistehender Kern quer ueber der Kavitaet
waere weder druck- noch tragbar.

Druckrichtung ist Bodenflaeche unten. Der Bauch ist damit die einzige
Stelle, an der die Kavitaet nach oben aufgeht, und zwar mit 18 Grad aus
der Senkrechten.

Gegossen wird in derselben Lage: Form auf den Deckel stellen, Bodenflaeche
oben. Der offene Ring um den Kammerkern ist die Einfuelloeffnung. Eine
Entlueftung braucht es nicht und darf es nicht geben: die Kavitaet steigt
von der Kuppe bis zur Bodenflaeche stetig an und hat genau eine Oeffnung,
naemlich die oben liegende. Luft weicht durch dieselbe Oeffnung nach oben
aus; ein Kanal an der Kuppe laege beim Giessen unten und wuerde nicht
entlueften, sondern auslaufen.

Die Bodenflaeche des Griffs ist keine Kappe, sondern eine ebene Kreis-
flaeche von 22 mm: die Viertelellipse des Bauchs ist dort abgeschnitten.
Sie faellt mit der Trennebene der Form zusammen, liegt beim Giessen oben
und wird nach dem Fuellen mit einer Klinge glatt abgezogen.

    python3 giessform.py
"""

import math

import griffe as G
from netz import (vernetzen, volumen, offene_kanten, ueberhang,
                  abweichung, schreibe_stl, quader, zapfen)

# ---------------------------------------------------------------- Bauteil ---

VARIANTE = "kehle"
PROFIL = G.VARIANTEN[VARIANTE]["profil"]
BOHR = G.VARIANTEN[VARIANTE]["bohr"]
HOEHE = PROFIL.hoehe                    # 90 mm

# z = 0 ist die Bodenflaeche des Griffs, z = HOEHE die Kuppe.
DECKEL = 6.0                            # Wand ueber der Kuppe
H_FORM = HOEHE + DECKEL

# ------------------------------------------------------------------ Form ----

X_HALB = 28.0           # halbe Formbreite
Y_TIEF = 23.0           # Tiefe der Haelfte hinter der Trennebene

RIPPE_X = 23.0          # Lage von Zentrierrippe und -nut
RIPPE_R = 3.0
NUT_R = 3.2             # 0,2 mm Luft, damit sich die Haelften fuegen lassen

# Beide Enden der Rippe laufen unter 45 Grad aus. Ohne das schwebte die
# Unterseite der Rippe frei ueber dem Druckbett. Die Nut ist unten offen -
# sie kann also nicht aufsetzen - und laeuft oben 0,2 mm spaeter aus als
# die Rippe, womit die Luft ueber die ganze Schraege gleich bleibt.
RIPPE_Z = (1.0, 89.0)   # Spitzen der beiden Auslaufkegel
NUT_Z = 89.2            # Spitze des oberen Kegels, unten durchgehend

RASTER = 0.65
DATEI = "tuerzwerg-giessform-griff.stl"


def teil(x, y, z):
    """Signierter Abstand zum Griff selbst, Bohrung bereits abgezogen."""
    r = math.hypot(x, y)
    h = HOEHE - z
    hc = min(max(h, 0.0), HOEHE)
    aussen = r - PROFIL(hc)[0]
    innen = BOHR(hc) - r
    return max(aussen, innen, z - HOEHE, -z)


def feld(x, y, z):
    """Signierter Abstand der Formhaelfte. Negativ ist Material."""
    d = quader(x, y, z, -X_HALB, X_HALB, -Y_TIEF, 0.0, 0.0, H_FORM)

    # Kavitaet: die Haelfte des Griffs, die auf dieser Seite liegt
    d = max(d, -max(teil(x, y, z), y))

    # Zentrierrippe, steht in die Gegenhaelfte hinein
    rippe = max(zapfen(math.hypot(x - RIPPE_X, y), z, RIPPE_R,
                        RIPPE_Z[0], RIPPE_Z[1]), -y)
    d = min(d, rippe)

    # Zentriernut, in die eigene Haelfte geschnitten
    nut = max(zapfen(math.hypot(x + RIPPE_X, y), z, NUT_R, None, NUT_Z), y)
    d = max(d, -nut)
    return d


def grenzen():
    return ((-X_HALB - 1.5, X_HALB + 1.5),
            (-Y_TIEF - 1.5, RIPPE_R + 1.5),
            (-1.5, H_FORM + 1.5))


# -------------------------------------------------------------- Kennzahlen --

def kavitaet_volumen(n=4000):
    """Rauminhalt des Griffs - so viel Silikon wird gebraucht."""
    v = 0.0
    for i in range(n):
        h = HOEHE * (i + 0.5) / n
        v += math.pi * (PROFIL(h)[0] ** 2 - BOHR(h) ** 2) * HOEHE / n
    return v


def engste_wand():
    """Duennste Formwand zwischen Kavitaet und Aussenkante."""
    best = None
    for i in range(901):
        h = HOEHE * i / 900.0
        for wand, wo in ((X_HALB - PROFIL(h)[0], "seitlich"),
                         (Y_TIEF - PROFIL(h)[0], "hinten")):
            if best is None or wand < best[0]:
                best = (wand, wo, HOEHE - h)
    return best


if __name__ == "__main__":
    print("Vernetze ...")
    tri = vernetzen(feld, grenzen(), RASTER)

    vol = volumen(tri)
    if vol < 0:
        tri = [(a, c, b) for a, b, c in tri]
        vol = -vol

    schreibe_stl(tri, DATEI, "Tuerzwerg Giessform Griff - Masse in mm")
    anteil, grad, flaeche = ueberhang(tri)
    ab_max, ab_mit = abweichung(feld, tri)
    kav = kavitaet_volumen()
    wand, wo, wh = engste_wand()

    print(f"\nDatei           {DATEI}")
    print(f"Eine Haelfte    {2*X_HALB:.0f} x {Y_TIEF:.0f} x {H_FORM:.0f} mm")
    print(f"Zusammengesetzt {2*X_HALB:.0f} x {2*Y_TIEF:.0f} x {H_FORM:.0f} mm")
    print(f"Dreiecke        {len(tri)}")
    print(f"Offene Kanten   {offene_kanten(tri)}  (0 = geschlossenes Volumen)")
    print(f"Formvolumen     {vol/1000:.0f} cm^3 je Haelfte "
          f"({vol/1000*1.24:.0f} g PLA voll gefuellt)")
    print(f"Kavitaet        {kav/1000:.1f} cm^3 Silikon je Guss "
          f"({kav/1000*1.15:.0f} g)")
    print(f"Duennste Wand   {wand:.1f} mm {wo}, bei h = {wh:.0f} mm")
    print(f"Zentrierung     Rippe {2*RIPPE_R:.0f} mm gegen Nut {2*NUT_R:.1f} mm, "
          f"{NUT_R-RIPPE_R:.1f} mm Luft")
    print(f"Trennflaeche    {2*X_HALB*H_FORM/100.0:.0f} cm^2 plan, "
          f"abzueglich des halben Griffquerschnitts")
    print(f"Ueberhang       {anteil:.2f} % der Flaeche ueber 45 Grad, "
          f"hoechstens {grad:.0f} Grad")
    print(f"Formtreue       hoechstens {ab_max*1000:.0f} um, "
          f"im Mittel {ab_mit*1000:.0f} um")
    print(f"Facette         {RASTER:.2f} mm")

    print("\nKontur der Kavitaet, Soll gegen Rechnung:")
    for h, soll in ((0.0, 8.2), (20.0, 15.0), (36.0, 15.0),
                    (48.0, 13.0), (68.0, 36.0), (90.0, 22.0)):
        print(f"  h = {h:4.0f}   {2*PROFIL(h)[0]:6.2f} mm   (Soll {soll:.1f})")
