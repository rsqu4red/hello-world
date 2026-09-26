#!/usr/bin/env python3
"""
Türzwerg – wie gross ist der Knoten wirklich?

Ich habe in der Auslegung durchgehend mit "Knoten Ø8" gerechnet und das
nie hergeleitet. Nachgerechnet kommt mehr heraus. Deshalb hier die
Rechnung offen, mit ihren Annahmen - damit man sieht, wo sie wackelt.

Der Weg ist ueber das Volumen, nicht ueber eine Faustformel
-------------------------------------------------------------

Ein fest gezogener Ueberhandknoten (Sackstich) windet sich rund
anderthalbmal um einen Kern, der selbst etwa so dick ist wie die Schnur.
Der Umfang einer Windung ist damit rund 2*pi*d, anderthalb Windungen
brauchen also knapp 10 Schnurdurchmesser Laenge. Dieses Stueck Schnur
steckt anschliessend in der Huelle des Knotens.

    Schnurvolumen im Knoten  =  L * pi * (d/2)^2
    Huellvolumen             =  Schnurvolumen / Packungsgrad
    Huelle als Zylinder      =  pi/4 * D^2 * H,  H = k * D

Daraus faellt D heraus. Drei Groessen sind dabei geschaetzt und
entscheiden das Ergebnis:

  L   Schnurlaenge im Knoten, 9 bis 12 Durchmesser
  phi Packungsgrad in der Huelle, 0,65 bis 0,80 - der Knoten hat Luecken
      und in der Mitte ein (fast geschlossenes) Loch
  k   Hoehe je Breite, 0,8 bis 1,0

Und eine vierte, die Paracord eigen ist: der Kernmantel ist innen hohl
und laesst sich zusammendruecken. Unter festem Zug verliert er
geschaetzt 20 Prozent seines Volumens. Das ist der groesste Hebel in der
ganzen Rechnung und zugleich der am schlechtesten belegte.

Das Ergebnis ist deshalb ein Bereich, keine Zahl - und eine
Schieblehre an einem echten Knoten ersetzt ihn in zwei Minuten.

    python3 knotenmass.py
"""

import math

D_SCHNUR = 4.0           # Paracord 550 Typ III, Nennmass


def knoten(d=D_SCHNUR, laengen=10.0, phi=0.72, k=0.85, stauchung=0.85):
    """Aussenmasse eines fest gezogenen Ueberhandknotens.

    laengen    Schnurlaenge im Knoten, in Durchmessern
    phi        Packungsgrad in der Huelle
    k          Hoehe je Breite
    stauchung  wieviel Volumen die Schnur unter Zug behaelt
    """
    v_schnur = laengen * d * math.pi * (d / 2.0) ** 2 * stauchung
    v_huelle = v_schnur / phi
    D = (v_huelle / (math.pi / 4.0 * k)) ** (1.0 / 3.0)
    return D, k * D, laengen * d


def spanne():
    """Der ganze plausible Bereich, nicht nur der Mittelwert."""
    werte = []
    for L in (9.0, 10.0, 12.0):
        for phi in (0.65, 0.72, 0.80):
            for k in (0.80, 0.85, 1.00):
                for st in (0.80, 0.85, 1.00):
                    werte.append(knoten(D_SCHNUR, L, phi, k, st))
    return (min(w[0] for w in werte), max(w[0] for w in werte),
            min(w[1] for w in werte), max(w[1] for w in werte))


# --------------------------------------------------- Kammer daraus ableiten --

LUFT_QUER = 1.0          # damit der Knoten hineingeht und nicht klemmt
LUFT_TIEF = 1.0          # damit er nicht in die Bohrung ragt


def kammer(D_knoten, H_knoten):
    return D_knoten + LUFT_QUER, H_knoten + LUFT_TIEF


if __name__ == "__main__":
    D, H, L = knoten()
    print("Ueberhandknoten (Sackstich) in Paracord 550, Ø4,0 mm")
    print(f"  Schnurlaenge im Knoten   {L:.0f} mm")
    print(f"  Knoten aussen            Ø{D:.1f} x {H:.1f} mm  (Mittelwert)")
    lo_d, hi_d, lo_h, hi_h = spanne()
    print(f"  plausibler Bereich       Ø{lo_d:.1f} bis {hi_d:.1f}, "
          f"Hoehe {lo_h:.1f} bis {hi_h:.1f} mm")
    print()

    dk, tk = kammer(D, H)
    print(f"Kammer daraus, mit {LUFT_QUER:.0f} mm Luft quer und "
          f"{LUFT_TIEF:.0f} mm in der Tiefe:")
    print(f"  Durchmesser              Ø{dk:.0f} mm")
    print(f"  Tiefe                    {tk:.0f} mm")
    print(f"  fuer den ganzen Bereich  Ø{hi_d+LUFT_QUER:.0f} x "
          f"{hi_h+LUFT_TIEF:.0f} mm")
    print()

    print("Was verschiedene Annahmen ausmachen:")
    print(f"  {'Fall':34s}{'Ø':>7}{'Hoehe':>8}")
    for name, kw in (("Mittelwert", {}),
                     ("Schnur nicht komprimierbar", dict(stauchung=1.0)),
                     ("locker gezogen (phi 0,65)", dict(phi=0.65)),
                     ("sehr fest (phi 0,80, st 0,80)",
                      dict(phi=0.80, stauchung=0.80)),
                     ("kurzer Knoten (L = 9 d)", dict(laengen=9.0)),
                     ("Achtknoten (L = 13 d)", dict(laengen=13.0))):
        a, b, _ = knoten(**kw)
        print(f"  {name:34s}{a:6.1f} {b:7.1f}")
    print()

    print("Zum Vergleich die Alternativen zum Knoten:")
    print(f"  {'Abschluss':34s}{'Ø':>7}{'Hoehe':>8}{'Kammer':>14}")
    for name, a, b in (("Sackstich", D, H),
                       ("doppelter Sackstich", *knoten(laengen=13.5)[:2]),
                       ("Ende verschmolzen und geplattet", 8.0, 2.5),
                       ("Ende verschmolzen, Tropfen", 6.5, 6.0)):
        print(f"  {name:34s}{a:6.1f} {b:7.1f}   "
              f"Ø{a+LUFT_QUER:.0f} x {b+LUFT_TIEF:.0f} mm")
    print()
    print("Die letzten beiden sind keine Rechnung, sondern Erfahrungswerte")
    print("fuer Nylon - Paracord wird am Ende ohnehin abgeschmolzen.")
    print()
    print("Schnurzuschnitt: der Knoten frisst rund "
          f"{L:.0f} mm, dazu {15:.0f} mm Schwanz, damit er nicht aufgeht.")
    print(f"  Fertiglaenge 220 mm  ->  zuschneiden auf rund "
          f"{220 + L + 15:.0f} mm")
