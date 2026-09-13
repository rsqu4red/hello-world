# -*- coding: utf-8 -*-
"""Vorentwurf Wochenendhaus Flurstück 7348, Grenzweg 12, 69245 Bammental
Erzeugt Planmappe (PDF, A3 quer) + PNG-Seiten, parametrisch für zwei Varianten."""
import math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 8

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

INK = "#1a1a1a"; GREY = "#8a8a8a"; LIGHT = "#d9d9d9"; WOOD = "#e8d9b8"; ROOF = "#5a5f66"
GLASS = "#cfe3ec"; DIM = "#b0004e"; GREEN = "#6f8f5a"; SAND = "#efe8d8"

PROJ = dict(
    vorhaben="Neubau eines Wochenendhauses",
    ort="Grenzweg 12 · 69245 Bammental · Flurstück 7348",
    bplan="B-Plan „Wochenendhausgebiet – 1. Änderung (Neufassung)“, Gemeinde Bammental, 11.09.2008",
    stand="VORENTWURF · Stand 09/2026 · zur Vorabstimmung mit der Gemeinde",
)

# ------------------------------------------------------------------ Varianten
VAR_A = dict(
    key="A", name="Variante A – Bebauung im Baufenster (Regelfall)",
    L=7.20, B=5.20, wall=0.30, h_wall=2.70, pitch=45.0, ov_eave=0.40, ov_gable=0.30,
    fok=0.30, roof_t=0.25, deck_depth=3.00,
    east_zone=2.60, bad_depth=1.80,
)
VAR_B = dict(
    key="B", name="Variante B – Überbauung 8,40 × 6,80 m (Antrag auf Befreiung)",
    L=8.40, B=6.80, wall=0.30, h_wall=2.60, pitch=38.0, ov_eave=0.40, ov_gable=0.30,
    fok=0.30, roof_t=0.25, deck_depth=3.00,
    east_zone=3.10, bad_depth=2.20,
)

def derived(v):
    d = dict(v)
    t = math.tan(math.radians(v["pitch"]))
    d["rise"] = v["B"] / 2 * t
    d["h_ridge"] = v["h_wall"] + d["rise"]                # OK Dachhaut First über FOK
    d["h_eave"] = v["h_wall"] - v["ov_eave"] * t           # Traufkante (UK Dachhaut) über FOK
    d["GR"] = v["L"] * v["B"]
    d["Li"] = v["L"] - 2 * v["wall"]; d["Bi"] = v["B"] - 2 * v["wall"]
    d["roof_L"] = v["L"] + 2 * v["ov_gable"]; d["roof_B"] = v["B"] + 2 * v["ov_eave"]
    d["roof_area_proj"] = d["roof_L"] * d["roof_B"]
    d["deck_area"] = v["L"] * v["deck_depth"]
    return d

# ------------------------------------------------------------------ Helfer
def page(pp, title, scale_txt, sheet_no, extra=None, short=None):
    fig = plt.figure(figsize=(16.54, 11.69))  # A3 quer
    fig.patch.set_facecolor("white")
    # Rahmen
    fig.add_artist(patches.Rectangle((0.02, 0.03), 0.96, 0.94, fill=False, lw=1.2, ec=INK, transform=fig.transFigure))
    # Schriftfeld
    x0, y0, w, h = 0.60, 0.03, 0.38, 0.115
    fig.add_artist(patches.Rectangle((x0, y0), w, h, fill=True, fc="white", lw=1.0, ec=INK, transform=fig.transFigure))
    fig.text(x0 + 0.01, y0 + h - 0.022, PROJ["vorhaben"], fontsize=11, weight="bold")
    fig.text(x0 + 0.01, y0 + h - 0.040, PROJ["ort"], fontsize=8.5)
    fig.text(x0 + 0.01, y0 + h - 0.055, PROJ["bplan"], fontsize=7, color=GREY)
    fig.text(x0 + 0.01, y0 + 0.030, short or title, fontsize=10, weight="bold")
    fig.text(x0 + 0.01, y0 + 0.012, PROJ["stand"], fontsize=7.5, color=GREY)
    fig.text(x0 + w - 0.01, y0 + 0.030, scale_txt, fontsize=9, ha="right")
    fig.text(x0 + w - 0.01, y0 + 0.012, f"Blatt {sheet_no}", fontsize=9, ha="right", weight="bold")
    fig.text(0.03, 0.955, title, fontsize=15, weight="bold")
    if extra:
        fig.text(0.03, 0.935, extra, fontsize=9, color=GREY)
    return fig

def finish(fig, pp, name):
    pp.savefig(fig)
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=110)
    plt.close(fig)

def dim_h(ax, x1, x2, y, txt=None, off=0.0, fs=7, col=DIM):
    ax.plot([x1, x2], [y, y], color=col, lw=0.6)
    for x in (x1, x2):
        ax.plot([x, x], [y - 0.12, y + 0.12], color=col, lw=0.6)
        ax.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color=col, lw=0.8)
    ax.text((x1 + x2) / 2, y + 0.06 + off, txt or f"{abs(x2-x1):.2f}".replace(".", ","), ha="center", va="bottom", fontsize=fs, color=col)

def dim_v(ax, y1, y2, x, txt=None, fs=7, col=DIM, side=1):
    ax.plot([x, x], [y1, y2], color=col, lw=0.6)
    for y in (y1, y2):
        ax.plot([x - 0.12, x + 0.12], [y, y], color=col, lw=0.6)
        ax.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color=col, lw=0.8)
    ax.text(x + 0.08 * side, (y1 + y2) / 2, txt or f"{abs(y2-y1):.2f}".replace(".", ","), ha="left" if side > 0 else "right",
            va="center", fontsize=fs, color=col, rotation=90)

def level(ax, x, y, txt, side=1):
    ax.plot([x, x + 0.25 * side], [y, y], color=INK, lw=0.6)
    ax.plot(x, y, marker=(3, 0, 180), ms=6, mfc="white", mec=INK, mew=0.6)
    ax.text(x + 0.3 * side, y + 0.03, txt, fontsize=7, ha="left" if side > 0 else "right", va="bottom")

def boards(ax, x1, x2, y1, y2, step=0.15, col=GREY, lw=0.25, horiz=True, clip=None):
    if horiz:
        y = y1
        while y < y2:
            ax.plot([x1, x2], [y, y], color=col, lw=lw, zorder=1.5)
            y += step
    else:
        x = x1
        while x < x2:
            ax.plot([x, x], [y1, y2], color=col, lw=lw, zorder=1.5)
            x += step

def fmt(x):
    return f"{x:.2f}".replace(".", ",")

def setup_ax(ax):
    ax.set_aspect("equal"); ax.axis("off")

def north(ax, x, y, s=1.0):
    ax.annotate("", xy=(x, y + s), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=INK))
    ax.text(x, y + s + 0.15 * s, "N", ha="center", fontsize=10, weight="bold")

# ------------------------------------------------------------------ Lageplan
def sheet_lageplan(pp, v, no):
    d = derived(v)
    fig = page(pp, "Lageplan (schematisch)", "M 1:250 (schematisch)", no,
               "Grundstücksgrenzen näherungsweise aus dem B-Plan abgegriffen – für den Bauantrag durch amtlichen Lageplan (Vermesser) zu ersetzen. Nord = oben.")
    ax = fig.add_axes([0.04, 0.16, 0.55, 0.76]); setup_ax(ax)
    # Koordinaten: x nach Osten, y nach Norden, Ursprung = SW-Ecke Gebäude
    L, B = v["L"], v["B"]
    gx, gy = -20.0, -18.0   # Grundstückspolygon (schematisch, ca. 24 x 36 m)
    parcel = np.array([[-19.5, -14.0], [11.6, -21.0], [11.2, 26.0], [-19.0, 23.0]])
    ax.add_patch(patches.Polygon(parcel, closed=True, fc=SAND, ec=INK, lw=1.2, zorder=0))
    ax.text(-8, 4, "Flurstück 7348\n(Grenzen schematisch)", fontsize=10, style="italic", ha="center")
    # Grenzweg (nördlich)
    road = np.array([[-22, 23.4], [14, 27.6], [14, 31.2], [-22, 27.0]])
    ax.add_patch(patches.Polygon(road, closed=True, fc="#f4f1a9", ec=GREEN, lw=1.0, zorder=0))
    ax.text(-8, 26.6, "Grenzweg", fontsize=10, rotation=6.5, color=INK)
    # Wald / Geltungsbereichsgrenze Ost
    ax.add_patch(patches.Rectangle((11.2, -23), 7, 50, fc="#cfe0c3", ec="none", zorder=0))
    for yy in np.arange(-21, 26, 3.0):
        ax.plot(13.6, yy, marker="^", color=GREEN, ms=7, mec="none")
    ax.text(16.2, 0, "Wald (außerhalb Geltungsbereich B-Plan)", rotation=90, fontsize=8, ha="center", va="center", color=GREEN)
    ax.plot([11.4, 11.2], [-21, 26], color=INK, lw=2.5, ls=(0, (4, 2)), zorder=2)
    # Nachbarn
    ax.text(-19.2, -1, "7349", fontsize=9, color=GREY, rotation=90)
    ax.text(-6, -19.0, "7354", fontsize=9, color=GREY)
    # Waldabstand 30 m (Hinweis-Linie)
    ax.plot([-19.5, 11.2], [7.0, 7.0], color=GREY, lw=0.6, ls="--")
    ax.text(-18.8, 7.3, "Waldabstandslinie 30 m (§ 4 Abs. 3 LBO) – nachrichtlich, Lage prüfen", fontsize=6.5, color=GREY)
    # Baufenster
    bf = patches.Rectangle((0, 0), 7.20, 5.20, fc="none", ec="#00a3d9", lw=2.0, ls="-.", zorder=3)
    ax.add_patch(bf)
    ax.text(7.3, 5.35, "Baufenster (Baugrenze)\n7,20 × 5,20 m = 37,44 m²", fontsize=7, color="#0077a3", ha="right", va="bottom")
    # Gebäude
    ox, oy = (0, 0) if v["key"] == "A" else (-(v["L"] - 7.20) / 2, -(v["B"] - 5.20) / 2)
    ax.add_patch(patches.Rectangle((ox - v["ov_gable"], oy - v["ov_eave"]), d["roof_L"], d["roof_B"], fc="none", ec=GREY, lw=0.6, ls=":", zorder=3))
    ax.add_patch(patches.Rectangle((ox, oy), L, B, fc="#f2b6a0", ec=INK, lw=1.4, zorder=4, hatch="//"))
    ax.plot([ox, ox + L], [oy + B / 2, oy + B / 2], color=INK, lw=1.0, ls="-.", zorder=5)
    ax.text(ox - 0.6, oy + B / 2, f"Wochenendhaus {v['key']}\n{fmt(L)} × {fmt(B)} m · GR {fmt(d['GR'])} m²\nFirst {fmt(d['h_ridge'])} m ü. FOK · I", ha="right", va="center", fontsize=7, zorder=6, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    # Terrasse
    ax.add_patch(patches.Rectangle((ox, oy - v["deck_depth"]), L, v["deck_depth"], fc=WOOD, ec=INK, lw=0.8, zorder=3))
    boards(ax, ox, ox + L, oy - v["deck_depth"], oy, step=0.3, horiz=True)
    ax.text(ox + L / 2, oy - v["deck_depth"] / 2, f"Holzterrasse {fmt(L)} × {fmt(v['deck_depth'])} m\n{fmt(d['deck_area'])} m² (§ 5.1: ≤ 6,0 m Tiefe)", ha="center", va="center", fontsize=7, zorder=5, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    # Stellplatz + Zufahrt
    sp = patches.Rectangle((-16.5, 17.5), 5.0, 2.5, fc="#e6e6e6", ec=INK, lw=0.8, hatch="..", zorder=3)
    ax.add_patch(sp)
    ax.text(-14.0, 15.6, "1 Stellplatz 5,0 × 2,5 m\nSchotterrasen (wasserdurchlässig, § 7.2)", ha="center", va="top", fontsize=6.5, zorder=5)
    ax.add_patch(patches.Polygon([[-16.5, 20.0], [-11.5, 20.0], [-11.0, 24.7], [-17.0, 24.0]], fc="#e6e6e6", ec=GREY, lw=0.6, zorder=2))
    ax.text(-14.0, 22.0, "Zufahrt", fontsize=6.5, ha="center")
    # Weg zum Haus
    ax.plot([-11.5, ox + 3.7, ox + 3.7], [18.5, 9.0, B + 0.6], color=GREY, lw=3, alpha=0.5, solid_capstyle="round", zorder=2)
    ax.text(-8.5, 14.6, "Fußweg (Kies/Holzbohlen)", fontsize=6.5, rotation=-32, color=GREY)
    # Zisterne
    ax.add_patch(patches.Circle((ox + L + 2.0, oy + B + 1.5), 1.0, fc="#dbe9f2", ec="#3a6d8c", lw=0.8, ls="--", zorder=3))
    ax.text(ox + L + 2.0, oy + B + 3.0, "Zisterne\n≥ 3 m³ (Hinweis B-Plan)", ha="center", fontsize=6.5, color="#3a6d8c")
    # Bestandsbäume erhalten (symbolisch)
    for (tx, ty) in [(-17, 3), (-13, -8), (-4, -14), (-9, 2)]:
        ax.add_patch(patches.Circle((tx, ty), 2.2, fc="none", ec=GREEN, lw=0.8, ls=":"))
        ax.plot(tx, ty, "+", color=GREEN)
    ax.text(-13, -12.6, "Bestandsbäume/-gehölze außerhalb\nBaufenster bleiben erhalten (§ 9)", fontsize=6.5, color=GREEN, ha="center")
    # Abstände
    dim_h(ax, ox + L, 11.2, oy + B / 2, txt=f"≈ {fmt(11.2-(ox+L))} m", fs=6.5)
    dim_v(ax, oy + B, 25.0, ox - 1.5, txt="≈ 20 m zum Grenzweg", fs=6.5, side=-1)
    north(ax, -3, 32.0, 2.5)
    ax.set_xlim(-24, 19); ax.set_ylim(-24, 36)

    # Legende rechts
    lx = fig.add_axes([0.62, 0.20, 0.34, 0.70]); lx.axis("off")
    txt = [
        ("Legende", None),
        ("Baugrenze (Baufenster) gem. B-Plan", "#00a3d9"),
        ("Wochenendhaus (Neubau), Hauptgebäude", "#f2b6a0"),
        ("Dachüberstand (Traufe 0,40 m / Ortgang 0,30 m)", GREY),
        ("Holzterrasse, aufgeständert, unüberdacht", WOOD),
        ("Stellplatz / Zufahrt, wasserdurchlässig", "#e6e6e6"),
        ("Grenze Geltungsbereich B-Plan / Waldrand", INK),
        ("", None),
        ("Flächenbilanz (Variante " + v["key"] + ")", None),
        (f"Grundfläche Hauptgebäude GR  {fmt(d['GR'])} m²  (max. 65 m²)", None),
        (f"Terrasse  {fmt(d['deck_area'])} m²  ·  Stellplatz+Zufahrt ca. 25 m²", None),
        (f"Summe versiegelt/Nebenanlagen ca. {fmt(d['GR']+d['deck_area']+25)} m²", None),
        (f"GRZ bei 900 m² Grundstück: {(d['GR']+d['deck_area']+25)/900:.2f}".replace(".", ",") + "  (zul. 0,15 inkl. Nebenanlagen)", None),
        ("", None),
        ("Hinweise", None),
        ("• Grundstücksfläche lt. Kataster eintragen (Mindestgröße 900 m²).", None),
        ("• Ausrichtung Baufenster / Grenzen vor Ort einmessen lassen.", None),
        ("• Waldabstand: Befreiung/Ausnahme nach § 4 Abs. 3 LBO BW i. V. m.", None),
        ("  Forstbehörde – Baufenster liegt lt. B-Plan bereits im 30-m-Streifen.", None),
    ]
    y = 0.98
    for t, c in txt:
        if c:
            lx.add_patch(patches.Rectangle((0.0, y - 0.012), 0.05, 0.03, fc=c if c not in (GREY, INK, "#00a3d9") else "white", ec=c, lw=1.2, transform=lx.transAxes, ls="-." if c == "#00a3d9" else "-"))
            lx.text(0.07, y, t, fontsize=8.5, va="center", transform=lx.transAxes)
        else:
            lx.text(0.0, y, t, fontsize=9.5 if t and not t.startswith(("•", " ", "G", "T", "S")) or t.startswith(("Legende", "Fl", "Hin")) else 8.5,
                    weight="bold" if t.startswith(("Legende", "Flächen", "Hinweise")) else "normal", va="center", transform=lx.transAxes)
        y -= 0.045
    finish(fig, pp, f"{no:02d}_Lageplan_{v['key']}")

# ------------------------------------------------------------------ Grundriss
def sheet_grundriss(pp, v, no):
    d = derived(v)
    L, B, w = v["L"], v["B"], v["wall"]
    fig = page(pp, f"Grundriss Erdgeschoss – {v['name']}", "M 1:50", no, short=f"Grundriss EG – Variante {v['key']}",
               extra="Holzrahmenbau, Außenwand 30 cm (inkl. Lärchenschalung), Innenwände 10 cm. Maße in m. Süden = unten (Terrassenseite).")
    ax = fig.add_axes([0.03, 0.14, 0.62, 0.80]); setup_ax(ax)
    # Wände
    ax.add_patch(patches.Rectangle((0, 0), L, B, fc=INK, ec=INK, lw=0.8, zorder=2))
    ax.add_patch(patches.Rectangle((w, w), d["Li"], d["Bi"], fc="white", ec="none", zorder=3))
    ez = v["east_zone"]; bd = v["bad_depth"]
    xp = L - w - ez          # Trennwand-Position (Westkante)
    # Innenwände
    ax.add_patch(patches.Rectangle((xp - 0.10, w), 0.10, d["Bi"], fc=INK, zorder=4))
    ax.add_patch(patches.Rectangle((xp, B - w - bd - 0.10), ez, 0.10, fc=INK, zorder=4))
    # Türen innen (Öffnungen weiß)
    def door(x, y, wd, vert=True):
        if vert:
            ax.add_patch(patches.Rectangle((x, y), 0.10, wd, fc="white", ec="none", zorder=5))
            ax.add_patch(patches.Arc((x + 0.10, y), 2 * wd, 2 * wd, theta1=0, theta2=90, lw=0.5, color=INK, zorder=6))
            ax.plot([x + 0.10, x + 0.10 + wd], [y, y], lw=0.8, color=INK, zorder=6)
        else:
            ax.add_patch(patches.Rectangle((x, y), wd, 0.10, fc="white", ec="none", zorder=5))
            ax.add_patch(patches.Arc((x, y + 0.10), 2 * wd, 2 * wd, theta1=0, theta2=90, lw=0.5, color=INK, zorder=6))
            ax.plot([x, x], [y + 0.10, y + 0.10 + wd], lw=0.8, color=INK, zorder=6)
    door(xp - 0.10, w + 0.30, 0.80)                       # Schlafen
    door(xp - 0.10, B - w - bd + 0.30, 0.70)              # Bad
    # Fenster / Türen außen (Glas)
    def win(x, y, wd, ht, horiz=True, label=None):
        if horiz:
            ax.add_patch(patches.Rectangle((x, y), wd, ht, fc=GLASS, ec=INK, lw=0.6, zorder=5))
            ax.plot([x, x + wd], [y + ht / 2, y + ht / 2], color=INK, lw=0.5, zorder=6)
        else:
            ax.add_patch(patches.Rectangle((x, y), ht, wd, fc=GLASS, ec=INK, lw=0.6, zorder=5))
            ax.plot([x + ht / 2, x + ht / 2], [y, y + wd], color=INK, lw=0.5, zorder=6)
    # Süd: Hebeschiebetür + Fenster Schlafen
    hst_x1, hst_w = w + 0.30, (xp - 0.10) - (w + 0.30) - 0.20
    win(hst_x1, 0, hst_w, w, label="HST")
    ax.text(hst_x1 + hst_w / 2, -0.35, f"Hebe-Schiebetür {fmt(hst_w)} × 2,30 m (Terrasse)", ha="center", fontsize=6.5)
    sf_x1 = xp + 0.40; sf_w = ez - 0.80
    win(sf_x1, 0, sf_w, w)
    ax.text(sf_x1 + sf_w / 2, -0.35, f"Fenster {fmt(sf_w)} × 1,40", ha="center", fontsize=6.5)
    # Schiebeladen (Holz) vor Schlafzimmerfenster / Sonnenschutz – gestrichelt
    ax.add_patch(patches.Rectangle((xp - 0.2, -0.16), ez + 0.4, 0.08, fc=WOOD, ec=INK, lw=0.5, ls="--", zorder=6))
    ax.text(L + 0.15, -0.12, "Schiebeladen\n(Lärche, vertikal)", fontsize=6, va="center")
    # Nord: Haustür + Küchenfenster + Badfenster
    door_x = xp - 0.10 - 1.00
    ax.add_patch(patches.Rectangle((door_x, B - w), 0.95, w, fc="white", ec="none", zorder=5))
    ax.plot([door_x, door_x + 0.95], [B - w, B - w], color=INK, lw=0.8, zorder=6)
    ax.add_patch(patches.Arc((door_x, B - w), 1.9, 1.9, theta1=270, theta2=360, lw=0.5, color=INK, zorder=6))
    ax.text(door_x + 0.47, B + 0.32, "Haustür 0,95", ha="center", fontsize=6.5)
    kw_x1, kw_w = w + 0.60, min(2.20, xp - w - 2.4)
    win(kw_x1, B - w, kw_w, w)
    ax.text(kw_x1 + kw_w / 2, B + 0.32, f"Fenster Küche {fmt(kw_w)} × 1,10 (BRH 1,20)", ha="center", fontsize=6.5)
    bw_x1 = xp + ez / 2 - 0.40
    win(bw_x1, B - w, 0.80, w)
    ax.text(bw_x1 + 0.40, B + 0.32, "Fenster Bad 0,80 × 0,80", ha="center", fontsize=6.5)
    # Ost: Fenster Schlafen; West: Giebelfenster Wohnen
    win(L - w, w + 0.80, 1.20, w, horiz=False)
    ax.text(L + 0.38, w + 1.40, "Fenster 1,20 × 1,40", rotation=90, ha="center", va="center", fontsize=6.5)
    win(0, w + 1.60, 0.90, w, horiz=False)
    ax.text(-0.38, w + 2.05, "Fenster 0,90 × 2,30", rotation=90, ha="center", va="center", fontsize=6.5)
    # Möblierung
    # Küche
    ax.add_patch(patches.Rectangle((w, B - w - 0.60), xp - 0.10 - w - 1.1, 0.60, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    ax.text(w + 0.1, B - w - 0.30, "Küchenzeile", fontsize=6.5, va="center", color=GREY)
    # Esstisch
    ax.add_patch(patches.Rectangle((w + 1.6, w + 1.3), 1.6, 0.8, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    # Sofa
    ax.add_patch(patches.Rectangle((w + 0.1, w + 0.35), 0.9, 2.0, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    # Kaminofen
    ax.add_patch(patches.Circle((xp - 0.6, B - w - 1.0), 0.25, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    ax.text(xp - 0.6, B - w - 1.45, "Ofen\n(opt.)", fontsize=5.5, ha="center", color=GREY)
    # Bett
    ax.add_patch(patches.Rectangle((L - w - 2.05, w + 0.3), 1.6, 2.0, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    # Bad: Dusche, WC, WT
    by0 = B - w - bd
    ax.add_patch(patches.Rectangle((L - w - 0.95, B - w - 0.95), 0.9, 0.9, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    ax.plot([L - w - 0.95, L - w - 0.05], [B - w - 0.95, B - w - 0.05], color=GREY, lw=0.4, zorder=5)
    ax.add_patch(patches.Ellipse((xp + 0.5, B - w - 0.40), 0.4, 0.6, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    ax.add_patch(patches.Rectangle((xp + 0.1, by0 + 0.15), 0.45, 0.6, fc="#f4f4f4", ec=GREY, lw=0.6, zorder=4))
    ax.text(xp + 0.35, by0 + 0.45, "T", fontsize=6, ha="center", va="center", color=GREY)
    # Raumbeschriftung
    A_w = (xp - 0.10 - w) * d["Bi"]; A_s = ez * (by0 - 0.10 - w); A_b = ez * bd
    ax.text((w + xp - 0.10) / 2, w + d["Bi"] * 0.55, f"WOHNEN · ESSEN · KOCHEN\n{fmt(A_w)} m²", ha="center", va="center", fontsize=9, weight="bold", zorder=7)
    ax.text(xp + ez / 2, (w + by0 - 0.1) / 2 + 0.55, f"SCHLAFEN\n{fmt(A_s)} m²", ha="center", va="center", fontsize=8, weight="bold", zorder=7)
    ax.text(xp + ez / 2 + 0.05, by0 + bd / 2 + 0.05, f"BAD / TECHNIK\n{fmt(A_b)} m²", ha="center", va="center", fontsize=7, weight="bold", zorder=7)
    # Terrasse
    ax.add_patch(patches.Rectangle((0, -v["deck_depth"]), L, v["deck_depth"], fc=WOOD, ec=INK, lw=0.6, zorder=1))
    boards(ax, 0, L, -v["deck_depth"], 0, step=0.145, horiz=True)
    ax.text(L / 2, -v["deck_depth"] + 0.5, f"TERRASSE (Lärche, aufgeständert) {fmt(L)} × {fmt(v['deck_depth'])} m = {fmt(d['deck_area'])} m²", ha="center", fontsize=8, weight="bold", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
    # Dachüberstand
    ax.add_patch(patches.Rectangle((-v["ov_gable"], -v["ov_eave"]), d["roof_L"], d["roof_B"], fc="none", ec=GREY, lw=0.6, ls=":", zorder=1))
    ax.plot([-v["ov_gable"], L + v["ov_gable"]], [B / 2, B / 2], color=GREY, lw=0.6, ls="-.", zorder=1)
    ax.text(L + v["ov_gable"] + 0.1, B / 2, "First", fontsize=6.5, color=GREY, va="center")
    # Schnittlinie
    sx = xp + ez / 2 + 0.75
    ax.plot([sx, sx], [-v["deck_depth"] - 0.6, B + 1.0], color=INK, lw=1.2, ls=(0, (6, 3)), zorder=8)
    ax.text(sx + 0.1, B + 0.85, "A", fontsize=9, weight="bold"); ax.text(sx + 0.1, -v["deck_depth"] - 0.55, "A", fontsize=9, weight="bold")
    # Bemaßung
    dim_h(ax, 0, L, B + 1.35, txt=f"{fmt(L)} (Außenmaß = Baufenster)" if v["key"] == "A" else f"{fmt(L)} (Außenmaß)")
    dim_h(ax, -v["ov_gable"], L + v["ov_gable"], B + 1.85, txt=f"{fmt(d['roof_L'])} (Dach)")
    dim_v(ax, 0, B, L + 1.2, txt=f"{fmt(B)} (Außenmaß)")
    dim_v(ax, -v["ov_eave"], B + v["ov_eave"], L + 1.7, txt=f"{fmt(d['roof_B'])} (Dach)")
    dim_v(ax, -v["deck_depth"], 0, L + 1.2, txt=f"{fmt(v['deck_depth'])} Terrasse")
    dim_h(ax, w, xp - 0.10, -v["deck_depth"] - 1.1, txt=fmt(xp - 0.10 - w))
    dim_h(ax, xp, L - w, -v["deck_depth"] - 1.1, txt=fmt(ez))
    dim_v(ax, w, by0 - 0.10, -1.1, txt=fmt(by0 - 0.10 - w), side=-1)
    dim_v(ax, by0, B - w, -1.1, txt=fmt(bd), side=-1)
    north(ax, -1.6, B + 0.9, 1.0)
    ax.set_xlim(-2.4, L + 2.6); ax.set_ylim(-v["deck_depth"] - 1.7, B + 2.6)

    # Raumprogramm rechts
    tx = fig.add_axes([0.67, 0.18, 0.30, 0.72]); tx.axis("off")
    rows = [("Raumprogramm", ""),
            ("Wohnen / Essen / Kochen", f"{fmt(A_w)} m²"),
            ("Schlafen", f"{fmt(A_s)} m²"),
            ("Bad / WC / Technik", f"{fmt(A_b)} m²"),
            ("Wohnfläche EG netto", f"{fmt(A_w+A_s+A_b)} m²"),
            ("Schlafempore (optional, kein Vollgeschoss)", f"≈ {fmt(ez*d['Bi'])} m²"),
            ("Terrasse (unüberdacht)", f"{fmt(d['deck_area'])} m²"),
            ("", ""),
            ("Kennwerte", ""),
            ("Grundfläche GR (Außenmaß)", f"{fmt(d['GR'])} m²"),
            ("Baufenster lt. B-Plan", "37,44 m²"),
            ("GR max. lt. Nutzungsschablone", "65,00 m²"),
            ("Vollgeschosse", "I"),
            ("Bauweise", "offen (o)"),
            ("Traufhöhe (Schnittpunkt Wand/Dach) ü. FOK", f"{fmt(v['h_wall'])} m"),
            ("Firsthöhe ü. FOK EG (max. 5,50)", f"{fmt(d['h_ridge'])} m"),
            ("Dachneigung / Dachform", f"{v['pitch']:.0f}° Satteldach"),
            ("Dachüberstand Traufe (max. 0,80)", f"{fmt(v['ov_eave'])} m"),
            ("Dachüberstand Ortgang (0,20–0,60)", f"{fmt(v['ov_gable'])} m"),
            ("FOK EG über Gelände (bergs. ≤0,20 / tals. ≤0,80)", "≈ 0,20–0,30 m"),
            ("", ""),
            ("Konstruktion", ""),
            ("Holzrahmenbau, vorgefertigt, diffusionsoffen", ""),
            ("Fassade: Lärche sägerau, horizontal, unbehandelt", ""),
            ("Dach: Stehfalz, beschichtetes Blech (kein Cu/Zn/Pb blank)", ""),
            ("Gründung: Punkt-/Schraubfundamente (minimaler Eingriff)", ""),
            ]
    y = 0.98
    for a, b in rows:
        bold = a in ("Raumprogramm", "Kennwerte", "Konstruktion", "Wohnfläche EG netto")
        tx.text(0, y, a, fontsize=8.5, weight="bold" if bold else "normal", transform=tx.transAxes, va="center")
        tx.text(1.0, y, b, fontsize=8.5, ha="right", transform=tx.transAxes, va="center", weight="bold" if bold else "normal")
        if a and b and not bold:
            tx.plot([0, 1], [y - 0.014, y - 0.014], color=LIGHT, lw=0.5, transform=tx.transAxes)
        y -= 0.036
    finish(fig, pp, f"{no:02d}_Grundriss_{v['key']}")
    return dict(A_w=A_w, A_s=A_s, A_b=A_b)

# ------------------------------------------------------------------ Ansichten
def draw_eave_elev(ax, v, side):
    """side='S' (Terrasse) oder 'N' (Eingang). Blick auf Traufseite."""
    d = derived(v); L, B, w = v["L"], v["B"], v["wall"]
    fok = v["fok"]; t = math.tan(math.radians(v["pitch"]))
    og = v["ov_gable"]
    # Gelände + Terrasse
    ax.add_patch(patches.Rectangle((-3, -fok - 1.2), L + 6, 1.2, fc="#efece4", ec="none", zorder=0))
    ax.plot([-3, L + 3], [-fok, -fok], color=INK, lw=1.2, zorder=1)
    if side == "S":
        ax.add_patch(patches.Rectangle((0, -0.05), L, 0.05 + 0.20, fc=WOOD, ec=INK, lw=0.6, zorder=2))
        ax.add_patch(patches.Rectangle((0, -0.08), L, 0.06, fc=WOOD, ec=INK, lw=0.6, zorder=2))
        for x in np.arange(0.4, L, 1.8):
            ax.plot([x, x], [-fok, -0.08], color=INK, lw=1.0, zorder=1)
    else:
        for x in np.arange(0.5, L, 1.9):
            ax.plot([x, x], [-fok, -0.05], color=INK, lw=1.0, zorder=1)
    # Wand
    ax.add_patch(patches.Rectangle((0, -0.05), L, v["h_wall"] + 0.05, fc=WOOD, ec=INK, lw=0.8, zorder=2))
    boards(ax, 0, L, 0.0, v["h_wall"], step=0.15)
    # Dach (Ansicht der geneigten Fläche): von Traufkante bis First
    ax.add_patch(patches.Rectangle((-og, d["h_eave"]), d["roof_L"], d["h_ridge"] - d["h_eave"], fc=ROOF, ec=INK, lw=0.8, zorder=3))
    boards(ax, -og, L + og, d["h_eave"], d["h_ridge"], step=0.53, horiz=False, col="#8e949c", lw=0.5)
    ax.add_patch(patches.Rectangle((-og, d["h_eave"] - 0.06), d["roof_L"], 0.18, fc="#3f434a", ec=INK, lw=0.6, zorder=4))  # Traufblende / Rinne
    ax.plot([-og, L + og], [d["h_ridge"], d["h_ridge"]], color=INK, lw=1.2, zorder=4)
    # Fallrohr
    ax.plot([L + og - 0.15, L + og - 0.15], [d["h_eave"] - 0.06, -fok], color="#3f434a", lw=1.5, zorder=4)
    ez = v["east_zone"]; xp = L - w - ez
    def win(x, y, wd, ht, glass=True, mullions=1):
        ax.add_patch(patches.Rectangle((x, y), wd, ht, fc=GLASS if glass else "white", ec=INK, lw=0.7, zorder=5))
        for i in range(1, mullions + 1):
            ax.plot([x + wd * i / (mullions + 1)] * 2, [y, y + ht], color=INK, lw=0.5, zorder=6)
        ax.add_patch(patches.Rectangle((x - 0.04, y - 0.04), wd + 0.08, ht + 0.08, fc="none", ec=INK, lw=0.5, zorder=6))
    if side == "S":
        hst_x1, hst_w = w + 0.30, (xp - 0.10) - (w + 0.30) - 0.20
        win(hst_x1, 0.0, hst_w, 2.30, mullions=1)
        sf_x1 = xp + 0.40; sf_w = ez - 0.80
        win(sf_x1, 0.90, sf_w, 1.40, mullions=0)
        # Schiebeladen (geparkt vor Schlafzimmerfenster) – vertikale Lärche
        ax.add_patch(patches.Rectangle((xp - 0.10, 0.10), ez + 0.05, 2.25, fc="#dfcfa8", ec=INK, lw=0.8, zorder=7))
        boards(ax, xp - 0.10, xp + ez - 0.05, 0.10, 2.35, step=0.10, horiz=False, col="#9c8a63", lw=0.5)
        ax.plot([w + 0.3, L - w - 0.3], [2.42, 2.42], color="#3f434a", lw=1.2, zorder=7)   # Schiene
        ax.annotate("", xy=(xp - 1.4, 1.2), xytext=(xp - 0.2, 1.2), arrowprops=dict(arrowstyle="<->", lw=0.8, color=DIM), zorder=8)
        ax.text(xp - 0.8, 1.32, "Schiebeladen", fontsize=6, color=DIM, ha="center", zorder=8)
        ax.text(L + og + 0.35, d["h_eave"] - 0.3, "Rinne + Fallrohr\n(Zisterne)", fontsize=6, color=GREY, va="top")
    else:
        # Nordansicht: gespiegelt (Blick von Norden: Westen rechts)
        def m(x, wd): return L - x - wd
        door_x = xp - 0.10 - 1.00
        win(m(door_x, 0.95), 0.0, 0.95, 2.20, glass=False, mullions=0)
        ax.add_patch(patches.Rectangle((m(door_x, 0.95) + 0.1, 0.9), 0.75, 0.7, fc=GLASS, ec=INK, lw=0.5, zorder=6))
        kw_x1, kw_w = w + 0.60, min(2.20, xp - w - 2.4)
        win(m(kw_x1, kw_w), 1.20, kw_w, 1.10, mullions=1)
        bw_x1 = xp + ez / 2 - 0.40
        win(m(bw_x1, 0.80), 1.50, 0.80, 0.80, mullions=0)
        # Außenleuchte
        ax.add_patch(patches.Rectangle((m(door_x, 0.95) - 0.35, 2.35), 0.2, 0.12, fc="#3f434a", ec="none", zorder=6))
    # Höhenkoten
    level(ax, L + og + 1.6, d["h_ridge"], f"OK First +{fmt(d['h_ridge'])}")
    level(ax, L + og + 1.6, v["h_wall"], f"Traufe (Wand/Dach) +{fmt(v['h_wall'])}")
    level(ax, L + og + 1.6, 0.0, "FOK EG ±0,00")
    level(ax, L + og + 1.6, -fok, f"Gelände ≈ −{fmt(fok)}")
    dim_v(ax, 0, d["h_ridge"], -og - 1.0, txt=f"{fmt(d['h_ridge'])} (max. 5,50)", side=-1)
    dim_h(ax, 0, L, -fok - 0.9, txt=fmt(L))
    dim_h(ax, -og, L + og, -fok - 1.5, txt=f"{fmt(d['roof_L'])} inkl. Ortgang 2 × {fmt(og)}")
    ax.set_xlim(-og - 2.2, L + og + 4.5); ax.set_ylim(-fok - 2.0, d["h_ridge"] + 0.8)

def draw_gable_elev(ax, v, side):
    """side='O' (Blick von Osten: Süden rechts) oder 'W' (Blick von Westen: Süden links)."""
    d = derived(v); L, B, w = v["L"], v["B"], v["wall"]
    fok = v["fok"]; t = math.tan(math.radians(v["pitch"])); oe = v["ov_eave"]
    # x in Ansicht: Süden links bei 'W', Süden rechts bei 'O'
    def X(yplan): return yplan if side == "W" else B - yplan
    ax.add_patch(patches.Rectangle((-4, -fok - 1.2), B + 8, 1.2, fc="#efece4", ec="none", zorder=0))
    ax.plot([-4, B + 4], [-fok, -fok], color=INK, lw=1.2, zorder=1)
    # Terrasse (seitlich sichtbar)
    dx0 = -v["deck_depth"] if side == "W" else B
    ax.add_patch(patches.Rectangle((dx0, -0.08), v["deck_depth"], 0.23, fc=WOOD, ec=INK, lw=0.6, zorder=2))
    for x in np.arange(dx0 + 0.3, dx0 + v["deck_depth"], 1.3):
        ax.plot([x, x], [-fok, -0.08], color=INK, lw=1.0, zorder=1)
    # Wand + Giebel
    poly = [(0, -0.05), (B, -0.05), (B, v["h_wall"]), (B / 2, d["h_ridge"] - v["roof_t"] / math.cos(math.radians(v["pitch"]))), (0, v["h_wall"])]
    ax.add_patch(patches.Polygon(poly, closed=True, fc=WOOD, ec=INK, lw=0.8, zorder=2))
    boards(ax, 0, B, 0.0, d["h_ridge"], step=0.15)
    ax.add_patch(patches.Polygon([(-1, -0.05), (-1, d["h_ridge"] + 1), (B + 1, d["h_ridge"] + 1), (B + 1, -0.05)], closed=True, fc="none", zorder=2))
    # Dachpolygon (Ortgang-Ansicht): Dachhaut Dicke roof_t
    rt = v["roof_t"] / math.cos(math.radians(v["pitch"]))
    roof = [(-oe, d["h_eave"]), (B / 2, d["h_ridge"]), (B + oe, d["h_eave"]), (B + oe, d["h_eave"] - rt), (B / 2, d["h_ridge"] - rt), (-oe, d["h_eave"] - rt)]
    ax.add_patch(patches.Polygon(roof, closed=True, fc="#3f434a", ec=INK, lw=0.8, zorder=4))
    # Fenster
    ez = v["east_zone"]; xp = L - w - ez
    def win(xc, y, wd, ht):
        ax.add_patch(patches.Rectangle((xc - wd / 2, y), wd, ht, fc=GLASS, ec=INK, lw=0.7, zorder=5))
        ax.add_patch(patches.Rectangle((xc - wd / 2 - 0.04, y - 0.04), wd + 0.08, ht + 0.08, fc="none", ec=INK, lw=0.5, zorder=6))
    if side == "O":
        win(X(w + 0.80 + 0.60), 0.90, 1.20, 1.40)
        ax.text(X(w + 1.4), 2.45, "Schlafen", fontsize=6, ha="center", color=GREY)
    else:
        win(X(w + 1.60 + 0.45), 0.0, 0.90, 2.30)
        ax.text(X(w + 2.05), 2.45, "Wohnen", fontsize=6, ha="center", color=GREY)
        # Empore-Giebelfenster (klein, optional)
        win(B / 2, v["h_wall"] + 0.45, 0.80, 0.80)
        ax.text(B / 2, v["h_wall"] + 1.35, "Giebelfenster\nEmpore (opt.)", fontsize=6, ha="center", color=GREY)
    # Koten + Maße
    level(ax, B + oe + 1.6, d["h_ridge"], f"OK First +{fmt(d['h_ridge'])}")
    level(ax, B + oe + 1.6, d["h_eave"], f"UK Traufkante +{fmt(d['h_eave'])}")
    level(ax, B + oe + 1.6, 0.0, "FOK EG ±0,00")
    level(ax, B + oe + 1.6, -fok, f"Gelände ≈ −{fmt(fok)}")
    dim_h(ax, 0, B, -fok - 0.9, txt=fmt(B))
    dim_h(ax, -oe, B + oe, -fok - 1.5, txt=f"{fmt(d['roof_B'])} inkl. Traufe 2 × {fmt(oe)}")
    dim_v(ax, 0, v["h_wall"], -oe - 1.0, txt=fmt(v["h_wall"]), side=-1)
    dim_v(ax, v["h_wall"], d["h_ridge"], -oe - 1.0, txt=fmt(d["rise"]), side=-1)
    # Neigungswinkel
    ax.add_patch(patches.Arc((-oe, d["h_eave"]), 1.6, 1.6, theta1=0, theta2=v["pitch"], lw=0.6, color=DIM, zorder=6))
    ax.plot([-oe, -oe + 1.0], [d["h_eave"], d["h_eave"]], color=DIM, lw=0.5, zorder=6)
    ax.text(-oe + 0.9, d["h_eave"] + 0.25, f"{v['pitch']:.0f}°", fontsize=7, color=DIM)
    ax.set_xlim(-oe - 2.4 - (v["deck_depth"] if side == "W" else 0), B + oe + 4.6 + (v["deck_depth"] if side == "O" else 0))
    ax.set_ylim(-fok - 2.0, d["h_ridge"] + 1.2)

def sheet_ansichten(pp, v, no):
    fig = page(pp, f"Ansichten – {v['name']}", "M 1:100", no, short=f"Ansichten – Variante {v['key']}",
               extra="Fassade Lärche horizontal (vergraut), Dach Stehfalz anthrazit (beschichtet), Fenster Holz-Alu. Höhen in m bezogen auf FOK EG = ±0,00.")
    for i, (side, ttl) in enumerate([("S", "Ansicht Süd (Terrasse / Gartenseite)"), ("N", "Ansicht Nord (Eingang / Grenzweg)"),
                                     ("O", "Ansicht Ost (Giebel, Waldseite)"), ("W", "Ansicht West (Giebel)")]):
        col, row = i % 2, i // 2
        ax = fig.add_axes([0.03 + col * 0.485, 0.53 - row * 0.385, 0.46, 0.38]); setup_ax(ax)
        ax.set_title(ttl, fontsize=10, weight="bold", loc="left")
        (draw_eave_elev if side in "SN" else draw_gable_elev)(ax, v, side)
    finish(fig, pp, f"{no:02d}_Ansichten_{v['key']}")

# ------------------------------------------------------------------ Schnitt
def sheet_schnitt(pp, v, no):
    d = derived(v); L, B, w = v["L"], v["B"], v["wall"]
    fok = v["fok"]; oe = v["ov_eave"]; th = math.radians(v["pitch"]); t = math.tan(th); yE = 2.33
    fig = page(pp, f"Schnitt A–A – {v['name']}", "M 1:50", no, short=f"Schnitt A–A – Variante {v['key']}",
               extra="Schnitt durch Schlaf-/Badzone mit optionaler Schlafempore (kein Vollgeschoss: lichte Höhe ≥ 2,30 m auf deutlich < 3/4 der Grundfläche).")
    ax = fig.add_axes([0.03, 0.14, 0.62, 0.80]); setup_ax(ax)
    # Gelände, Fundamente
    ax.add_patch(patches.Rectangle((-4.5, -fok - 1.6), B + 9, 1.6, fc="#efece4", ec="none", hatch="...", zorder=0))
    ax.plot([-4.5, B + 4.5], [-fok, -fok], color=INK, lw=1.2, zorder=1)
    for x in (0.4, B / 2, B - 0.4):
        ax.add_patch(patches.Rectangle((x - 0.15, -fok - 1.0), 0.30, 1.0 - 0.0, fc="#c9c9c9", ec=INK, lw=0.6, zorder=1))
        ax.plot([x, x], [-fok, -0.05], color=INK, lw=1.4, zorder=1)
    ax.text(B / 2, -fok - 1.95, "Punkt-/Schraubfundamente, frostfrei; Bodenplatte entfällt (Holzbalkendecke, hinterlüftet)", fontsize=6.5, ha="center", color=GREY)
    # Terrasse (Süd = links)
    ax.add_patch(patches.Rectangle((-v["deck_depth"], -0.08), v["deck_depth"], 0.23, fc=WOOD, ec=INK, lw=0.6, zorder=2))
    for x in np.arange(-v["deck_depth"] + 0.3, 0, 1.3):
        ax.plot([x, x], [-fok, -0.08], color=INK, lw=1.0, zorder=1)
    ax.text(-v["deck_depth"] / 2, 0.35, "Terrasse", fontsize=7, ha="center", color=GREY)
    # Bodenaufbau
    ax.add_patch(patches.Rectangle((0, -0.35), B, 0.35, fc="#d8d0c0", ec=INK, lw=0.6, hatch="//", zorder=2))
    # Außenwände (Schnitt)
    for x in (0, B - w):
        ax.add_patch(patches.Rectangle((x, -0.35), w, v["h_wall"] + 0.35 + 0.05, fc="#d8d0c0", ec=INK, lw=0.8, hatch="//", zorder=3))
    # Innenwand Schlafen/Bad
    bd = v["bad_depth"]; y_iw = B - w - bd - 0.10   # Plan-y -> Schnitt-x (Süd links): x = y_plan
    ax.add_patch(patches.Rectangle((y_iw, 0), 0.10, yE, fc="#d8d0c0", ec=INK, lw=0.6, hatch="//", zorder=3))
    # Dach (Sparren + Dachhaut) beidseitig
    rt = v["roof_t"] / math.cos(th)
    for sgn, x0 in ((1, -oe), (-1, B + oe)):
        xs = [x0, B / 2]; ys = [d["h_eave"], d["h_ridge"]]
        ax.add_patch(patches.Polygon([(x0, d["h_eave"]), (B / 2, d["h_ridge"]), (B / 2, d["h_ridge"] - rt), (x0, d["h_eave"] - rt)], closed=True, fc="#d8d0c0", ec=INK, lw=0.8, hatch="//", zorder=4))
        # Dachhaut
        ax.plot(xs, ys, color="#3f434a", lw=2.2, zorder=5)
    # Kehlbalken/ Empore
    ax.add_patch(patches.Rectangle((y_iw - 0.0, yE), B - w - y_iw, 0.22, fc="#d8d0c0", ec=INK, lw=0.6, hatch="//", ls="--", zorder=3))
    ax.plot([y_iw - 0.7, y_iw - 0.7, y_iw], [0, yE, yE], color=GREY, lw=0.6, ls=":", zorder=3)
    ax.text(y_iw - 0.75, 1.2, "Leiter-\ntreppe", fontsize=6, ha="right", color=GREY)
    # Bereich ≥ 2,30 m lichte Höhe auf Empore (Vollgeschoss-Nachweis)
    h_clear = 2.30 + yE + 0.22
    half = (d["h_ridge"] - rt - h_clear) / t if d["h_ridge"] - rt > h_clear else 0
    if half > 0:
        ax.plot([B / 2 - half, B / 2 + half], [h_clear, h_clear], color=DIM, lw=0.8, ls="--", zorder=6)
        ax.annotate("SCHLAFEMPORE (optional) · OK +" + fmt(yE + 0.22) + "\nlichte Höhe am First ≈ " + fmt(d["h_ridge"] - rt - yE - 0.22) + " m\n" + f"Breite mit ≥ 2,30 m lichter Höhe: nur {fmt(2*half)} m\n→ kein Vollgeschoss (§ 2 Abs. 6 LBO BW)",
                    xy=(B / 2 + 0.3, yE + 0.6), xytext=(B + oe + 1.4, v["h_wall"] + 1.5), fontsize=7, color=DIM, va="center",
                    arrowprops=dict(arrowstyle="->", lw=0.6, color=DIM), zorder=9)
    # Raumbeschriftung
    ax.text((w + y_iw) / 2, 1.2, "SCHLAFEN", fontsize=8, weight="bold", ha="center")
    ax.text(y_iw + 1.2, 1.2, "BAD", fontsize=8, weight="bold", ha="center")
    # Fenster Süd (Schlafen) / Nord (Bad) im Schnitt
    ax.add_patch(patches.Rectangle((-0.02, 0.90), w + 0.04, 1.40, fc=GLASS, ec=INK, lw=0.6, zorder=5))
    ax.add_patch(patches.Rectangle((B - w - 0.02, 1.50), w + 0.04, 0.80, fc=GLASS, ec=INK, lw=0.6, zorder=5))
    # Koten
    xk = B + oe + 1.4
    level(ax, xk, d["h_ridge"], f"OK First +{fmt(d['h_ridge'])} (≤ 5,50)")
    level(ax, xk, v["h_wall"], f"Traufe +{fmt(v['h_wall'])}")
    level(ax, xk, d["h_eave"], f"UK Traufkante +{fmt(d['h_eave'])}")
    level(ax, xk, 0.0, "FOK EG ±0,00")
    level(ax, xk, -fok, f"OK Gelände ≈ −{fmt(fok)} (FOK ≤ 0,20/0,80 ü. Gelände, § 2.2)")
    dim_v(ax, -fok, 0, -oe - 1.6, txt=fmt(fok), side=-1)
    dim_v(ax, 0, v["h_wall"], -oe - 1.6, txt=fmt(v["h_wall"]), side=-1)
    dim_v(ax, v["h_wall"], d["h_ridge"], -oe - 1.6, txt=fmt(d["rise"]), side=-1)
    dim_v(ax, 0, yE, y_iw + 0.4, txt=f"{fmt(yE)} lichte Raumhöhe (≥ 2,30)", side=1)
    dim_h(ax, 0, B, -fok - 0.9, txt=fmt(B))
    dim_h(ax, -oe, B + oe, -fok - 1.45, txt=f"{fmt(d['roof_B'])} Dach")
    ax.add_patch(patches.Arc((-oe, d["h_eave"]), 1.8, 1.8, theta1=0, theta2=v["pitch"], lw=0.6, color=DIM, zorder=6))
    ax.plot([-oe, -oe + 1.1], [d["h_eave"], d["h_eave"]], color=DIM, lw=0.5, zorder=6)
    ax.text(-oe + 1.0, d["h_eave"] + 0.3, f"DN {v['pitch']:.0f}°", fontsize=7, color=DIM)
    ax.text(-v["deck_depth"] - 0.3, -fok - 0.5, "SÜD", fontsize=8, weight="bold"); ax.text(B + 2.5, -fok - 0.5, "NORD", fontsize=8, weight="bold")
    ax.set_xlim(-v["deck_depth"] - 2.6, B + oe + 6.5); ax.set_ylim(-fok - 2.4, d["h_ridge"] + 1.3)

    # Aufbauten rechts
    tx = fig.add_axes([0.67, 0.18, 0.30, 0.72]); tx.axis("off")
    rows = [
        ("Dachaufbau (von außen)", True),
        ("Stehfalzdeckung, beschichtetes Stahl-/Aluminiumblech, anthrazit", False),
        ("Trennlage, Holzschalung 24 mm, Hinterlüftung 40 mm", False),
        ("Unterdeckbahn diffusionsoffen", False),
        ("Sparren 80/240 mit Holzfaser-/Zellulosedämmung 240 mm", False),
        ("Dampfbremse, Lattung, Innenbekleidung Fichte/Tanne weiß lasiert", False),
        ("optional: extensive Dachbegrünung statt Blech (Hinweis B-Plan)", False),
        ("", False),
        ("Außenwand (von außen) ≈ 30 cm", True),
        ("Lärche sägerau 24 mm, horizontal, offene Fuge, unbehandelt (vergraut)", False),
        ("Konterlattung 30 mm, Fassadenbahn", False),
        ("Holzrahmen 60/200 mit Holzfaserdämmung 200 mm", False),
        ("OSB/Dampfbremse, Installationsebene 40 mm, Bekleidung", False),
        ("", False),
        ("Boden", True),
        ("Dielen Eiche/Douglasie 25 mm, Holzbalkendecke 240 mm gedämmt", False),
        ("Hinterlüfteter Kriechraum, Punkt-/Schraubfundamente", False),
        ("", False),
        ("Haustechnik (Vorschlag)", True),
        ("Kaminofen + Infrarot-/Elektro-Direktheizung (Wochenendnutzung)", False),
        ("Trinkwasser/Abwasser: Anschluss lt. Gemeinde (Trennsystem, Hinweis B-Plan)", False),
        ("Regenwasser → Zisterne ≥ 3 m³ (Gartenbewässerung)", False),
        ("PV-Module dachintegriert Südseite optional (Blende in Dachfarbe)", False),
    ]
    y = 0.98
    for a, bold in rows:
        tx.text(0, y, a, fontsize=8.2, weight="bold" if bold else "normal", transform=tx.transAxes, va="center")
        y -= 0.037
    finish(fig, pp, f"{no:02d}_Schnitt_{v['key']}")

# ------------------------------------------------------------------ Isometrie
def sheet_isometrie(pp, v, no):
    d = derived(v); L, B, w = v["L"], v["B"], v["wall"]
    fig = page(pp, f"Schema-Isometrie – {v['name']}", "o. M.", no, short=f"Isometrie – Variante {v['key']}",
               extra="Blick von Südwesten. Nur Volumenstudie – Materialwirkung siehe Referenzbilder / Visualisierungen.")
    ax = fig.add_axes([0.03, 0.10, 0.94, 0.84]); setup_ax(ax)
    ca, sa = math.cos(math.radians(30)), math.sin(math.radians(30))
    def P(x, y, z):  # x Ost, y Nord, z Höhe
        return (x * ca - y * ca * 0.0 + y * 0.0 + (x - y) * 0.0 + x * 0 + (x * ca + y * ca * -1) * 0 + x * ca - y * -ca - x * ca, 0)  # placeholder
    def P(x, y, z):
        X = (x + y) * ca
        Y = (y - x) * sa + z
        return (X, Y)
    def poly(pts, fc, ec=INK, lw=0.8, z=1, alpha=1.0, hatch=None):
        ax.add_patch(patches.Polygon([P(*p) for p in pts], closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, hatch=hatch))
    fok = v["fok"]; oe, og = v["ov_eave"], v["ov_gable"]; hw, hr, he = v["h_wall"], d["h_ridge"], d["h_eave"]
    # Boden
    poly([(-8, -8, -fok), (L + 8, -8, -fok), (L + 8, B + 8, -fok), (-8, B + 8, -fok)], "#e8ead9", ec="none", z=0)
    # Baufenster
    ax.add_patch(patches.Polygon([P(0, 0, -fok), P(7.2, 0, -fok), P(7.2, 5.2, -fok), P(0, 5.2, -fok)], closed=True, fc="none", ec="#00a3d9", lw=1.5, ls="-.", zorder=0.5))
    ax.text(*P(7.4, -0.4, -fok), "Baufenster 7,20 × 5,20", fontsize=7, color="#0077a3")
    ox = 0 if v["key"] == "A" else -(L - 7.2) / 2; oy = 0 if v["key"] == "A" else -(B - 5.2) / 2
    # Terrasse
    poly([(ox, oy - v["deck_depth"], 0), (ox + L, oy - v["deck_depth"], 0), (ox + L, oy, 0), (ox, oy, 0)], WOOD, z=1)
    poly([(ox, oy - v["deck_depth"], 0), (ox + L, oy - v["deck_depth"], 0), (ox + L, oy - v["deck_depth"], -0.25), (ox, oy - v["deck_depth"], -0.25)], "#cbb98f", z=1)
    poly([(ox + L, oy - v["deck_depth"], 0), (ox + L, oy, 0), (ox + L, oy, -0.25), (ox + L, oy - v["deck_depth"], -0.25)], "#b8a67c", z=1)
    for i in range(1, 20):
        yy = oy - v["deck_depth"] + i * 0.145
        if yy >= oy: break
        ax.plot(*zip(P(ox, yy, 0), P(ox + L, yy, 0)), color="#b8a67c", lw=0.3, zorder=1.1)
    # Wände
    poly([(ox, oy, 0), (ox + L, oy, 0), (ox + L, oy, hw), (ox, oy, hw)], WOOD, z=2)                       # Süd
    poly([(ox + L, oy, 0), (ox + L, oy + B, 0), (ox + L, oy + B / 2, 0), (ox + L, oy + B, hw), (ox + L, oy + B / 2, hr - v["roof_t"]), (ox + L, oy, hw)], "#d9c8a0", z=2)  # Ost-Giebel
    poly([(ox + L, oy, 0), (ox + L, oy + B, 0), (ox + L, oy + B, hw), (ox + L, oy + B / 2, hr - 0.02), (ox + L, oy, hw)], "#d9c8a0", z=2)
    # Fassadenlinien
    for k in range(1, int(hw / 0.15)):
        z = k * 0.15
        ax.plot(*zip(P(ox, oy, z), P(ox + L, oy, z)), color="#b8a67c", lw=0.3, zorder=2.1)
        ax.plot(*zip(P(ox + L, oy, z), P(ox + L, oy + B, z)), color="#a89468", lw=0.3, zorder=2.1)
    # Fenster Süd
    ez = v["east_zone"]; xp = L - w - ez
    hst_x1, hst_w = w + 0.30, (xp - 0.10) - (w + 0.30) - 0.20
    poly([(ox + hst_x1, oy, 0), (ox + hst_x1 + hst_w, oy, 0), (ox + hst_x1 + hst_w, oy, 2.30), (ox + hst_x1, oy, 2.30)], GLASS, z=2.2)
    ax.plot(*zip(P(ox + hst_x1 + hst_w / 2, oy, 0), P(ox + hst_x1 + hst_w / 2, oy, 2.30)), color=INK, lw=0.5, zorder=2.3)
    poly([(ox + xp - 0.1, oy - 0.05, 0.1), (ox + xp + ez - 0.05, oy - 0.05, 0.1), (ox + xp + ez - 0.05, oy - 0.05, 2.35), (ox + xp - 0.1, oy - 0.05, 2.35)], "#dfcfa8", z=2.4)
    for k in range(1, int(ez / 0.1)):
        xx = ox + xp - 0.1 + k * 0.1
        ax.plot(*zip(P(xx, oy - 0.05, 0.1), P(xx, oy - 0.05, 2.35)), color="#9c8a63", lw=0.3, zorder=2.5)
    # Fenster Ost
    poly([(ox + L, oy + w + 0.8, 0.9), (ox + L, oy + w + 2.0, 0.9), (ox + L, oy + w + 2.0, 2.3), (ox + L, oy + w + 0.8, 2.3)], GLASS, z=2.2)
    # Dach: Südfläche + Nordfläche (Nord kaum sichtbar) + Stirn
    poly([(ox - og, oy - oe, he), (ox + L + og, oy - oe, he), (ox + L + og, oy + B / 2, hr), (ox - og, oy + B / 2, hr)], ROOF, z=3)
    poly([(ox - og, oy + B / 2, hr), (ox + L + og, oy + B / 2, hr), (ox + L + og, oy + B + oe, he), (ox - og, oy + B + oe, he)], "#474b52", z=2.9)
    # Stehfalz-Linien
    for k in range(1, int(d["roof_L"] / 0.53)):
        xx = ox - og + k * 0.53
        ax.plot(*zip(P(xx, oy - oe, he), P(xx, oy + B / 2, hr)), color="#8e949c", lw=0.4, zorder=3.1)
    # Traufblende
    poly([(ox - og, oy - oe, he), (ox + L + og, oy - oe, he), (ox + L + og, oy - oe, he - 0.18), (ox - og, oy - oe, he - 0.18)], "#3f434a", z=3.2)
    # Ortgang Ost (Dachstirn als Dreieck-Streifen)
    rt = v["roof_t"]
    poly([(ox + L + og, oy - oe, he), (ox + L + og, oy + B / 2, hr), (ox + L + og, oy + B + oe, he), (ox + L + og, oy + B + oe, he - rt), (ox + L + og, oy + B / 2, hr - rt), (ox + L + og, oy - oe, he - rt)], "#3f434a", z=3.3)
    # Beschriftung
    ax.text(*P(ox + L / 2, oy - v["deck_depth"] - 1.2, -fok), "Terrasse Süd", fontsize=8, ha="center")
    ax.text(*P(ox + L + 1.0, oy + B + 0.8, hr + 0.4), f"First +{fmt(hr)} m ü. FOK · DN {v['pitch']:.0f}°", fontsize=8)
    ax.text(*P(ox - 1.5, oy - 1.0, hw + 0.3), f"{fmt(L)} × {fmt(B)} m · GR {fmt(d['GR'])} m²", fontsize=8, ha="right")
    ax.text(*P(ox + L + 1.5, oy + B / 2 + 1.5, -fok), "Wald / Ost", fontsize=8, color=GREEN)
    ax.text(*P(ox + L / 2, oy + B + 4, -fok), "Grenzweg / Nord", fontsize=8, color=GREY, ha="center")
    ax.set_xlim(-9, L + B + 9); ax.set_ylim(-8, hr + 7)
    finish(fig, pp, f"{no:02d}_Isometrie_{v['key']}")

# ------------------------------------------------------------------ Nachweis
def sheet_nachweis(pp, vA, vB, no):
    dA, dB = derived(vA), derived(vB)
    fig = page(pp, "Nachweis der planungsrechtlichen Festsetzungen (B-Plan „Wochenendhausgebiet – 1. Änderung“)", "–", no, short="Nachweis Festsetzungen A / B",
               extra="Prüfung beider Varianten gegen die textlichen Festsetzungen, die Nutzungsschablone und die örtlichen Bauvorschriften (Dachüberstand).")
    ax = fig.add_axes([0.03, 0.16, 0.94, 0.77]); ax.axis("off")
    cols = ["Nr.", "Festsetzung / Vorschrift", "Anforderung", f"Variante A ({fmt(vA['L'])}×{fmt(vA['B'])})", f"Variante B ({fmt(vB['L'])}×{fmt(vB['B'])})"]
    ok, bef = "✔ eingehalten", "✘ Befreiung § 31 (2) BauGB erforderlich"
    rows = [
        ("1.1", "Art der Nutzung: SO Wochenendhaus", "nur Wochenendhäuser", "Wochenendhaus, 1 Wohneinheit ✔", "Wochenendhaus, 1 Wohneinheit ✔"),
        ("NS", "Grundfläche GR max.", "65 m²", f"{fmt(dA['GR'])} m² {ok}", f"{fmt(dB['GR'])} m² {ok}"),
        ("NS", "Zahl der Vollgeschosse", "I (max.)", "I – Empore kein Vollgeschoss ✔", "I – Empore kein Vollgeschoss ✔"),
        ("NS", "Bauweise", "offen (o)", "Einzelhaus ✔", "Einzelhaus ✔"),
        ("§ 9(1)2", "Überbaubare Grundstücksfläche (Baugrenze)", "Baufenster 7,20 × 5,20 m", "Außenkante = Baugrenze ✔ (Dachüberstand als untergeordnetes Bauteil, § 23 (3) BauNVO)", bef + " – Überschreitung 0,60 m je Seite (Traufe) / 0,80 m je Seite (Ortgang), begründet s. Bericht"),
        ("2.1", "GRZ inkl. Nebenanlagen (Terrasse, Stellplatz, Zufahrt)", "≤ 0,15", f"≈ {(dA['GR']+dA['deck_area']+25)/900:.2f} bei 900 m² ✔".replace(".", ","), f"≈ {(dB['GR']+dB['deck_area']+25)/900:.2f} bei 900 m² ✔".replace(".", ",")),
        ("2.2", "FOK EG über urspr. Gelände", "bergseits ≤ 0,20 m, talseits ≤ 0,80 m", "≈ 0,20–0,30 m (Geländeaufmaß erforderlich) ✔", "≈ 0,20–0,30 m ✔"),
        ("2.3", "Firsthöhe ab FOK EG", "≤ 5,50 m", f"{fmt(dA['h_ridge'])} m ✔", f"{fmt(dB['h_ridge'])} m ✔"),
        ("3", "Abstand zu seitl. Grenzen (nur in Flächen [1])", "≥ 5,0 m", "Baufenster 7348 nicht mit [1] gekennzeichnet; LBO-Abstand ≥ 2,5 m ✔ (ca. 4 m Ost)", "≈ 3,4 m Ost ✔ (LBO)"),
        ("4", "Mindestgröße Baugrundstück", "900 m²", "Fläche lt. Kataster nachweisen", "Fläche lt. Kataster nachweisen"),
        ("5.1", "Terrasse", "gesamte Gebäudebreite, Tiefe ≤ 6,0 m", f"{fmt(vA['L'])} × {fmt(vA['deck_depth'])} m ✔", f"{fmt(vB['L'])} × {fmt(vB['deck_depth'])} m ✔"),
        ("5.2", "Garagen/Carports/überdachte Sitzplätze", "nur im Baufenster", "keine (offener Stellplatz) ✔", "keine ✔"),
        ("7.1", "Dachflächen", "kein unbeschichtetes Cu/Zn/Pb", "Stehfalz beschichtet (Stahl/Alu) ✔ – alternativ Gründach", "wie A ✔"),
        ("7.2", "Stellplätze, Fußwege", "wasserdurchlässig", "Schotterrasen / Kiesweg ✔", "wie A ✔"),
        ("9", "Baumbestand außerhalb Baufenster", "erhalten", "Erhalt; Neubau auf Wiese ✔", "wie A ✔"),
        ("öBV § 3", "Dachüberstand Traufe / Ortgang", "≤ 0,80 m / 0,20–0,60 m", f"{fmt(vA['ov_eave'])} m / {fmt(vA['ov_gable'])} m ✔", f"{fmt(vB['ov_eave'])} m / {fmt(vB['ov_gable'])} m ✔"),
        ("Hinw.", "Dachbegrünung / Zisterne", "empfohlen; ≥ 0,02 m³/m² Dach", f"Zisterne ≥ {math.ceil(dA['roof_area_proj']*0.02*10)/10:.1f} m³ → 3 m³ vorgesehen ✔".replace(".", ","), f"≥ {math.ceil(dB['roof_area_proj']*0.02*10)/10:.1f} m³ → 3 m³ ✔".replace(".", ",")),
        ("Hinw.", "Artenschutz", "Brutstätten/Orchideen prüfen", "Bauen auf Wiese, keine Fällung; Vorprüfung Fachbüro", "wie A"),
        ("LBO § 4(3)", "Waldabstand 30 m", "Ausnahme durch Baurechtsbehörde im Benehmen mit Forst", "Baufenster liegt lt. B-Plan im Streifen → Ausnahme beantragen", "wie A"),
    ]
    widths = [0.06, 0.24, 0.18, 0.26, 0.26]
    x = np.cumsum([0] + widths[:-1])
    y = 1.0
    hdr_h = 0.045
    for j, c in enumerate(cols):
        ax.add_patch(patches.Rectangle((x[j], y - hdr_h), widths[j], hdr_h, fc="#e9e9e9", ec=INK, lw=0.5, transform=ax.transAxes))
        ax.text(x[j] + 0.005, y - hdr_h / 2, c, fontsize=8.5, weight="bold", va="center", transform=ax.transAxes)
    y -= hdr_h
    import textwrap
    for r in rows:
        wrapped = [textwrap.wrap(str(cell), [10, 44, 34, 50, 50][j]) for j, cell in enumerate(r)]
        nlines = max(len(wv) for wv in wrapped)
        rh = 0.013 * nlines + 0.016
        for j in range(5):
            ax.add_patch(patches.Rectangle((x[j], y - rh), widths[j], rh, fc="white", ec=LIGHT, lw=0.5, transform=ax.transAxes))
            col = INK
            txt = "\n".join(wrapped[j])
            if j >= 3 and "✘" in txt: col = DIM
            elif j >= 3 and "✔" in txt: col = "#2a6f2a"
            ax.text(x[j] + 0.005, y - rh / 2, txt, fontsize=7.6, va="center", transform=ax.transAxes, color=col, linespacing=1.15)
        y -= rh
    ax.text(0, y - 0.02, "NS = Nutzungsschablone · öBV = örtliche Bauvorschriften zum B-Plan · Grundstücksfläche und Geländehöhen sind vor Einreichung durch Vermessung zu belegen.",
            fontsize=7.5, color=GREY, transform=ax.transAxes)
    finish(fig, pp, f"{no:02d}_Nachweis_Festsetzungen")

# ------------------------------------------------------------------ Deckblatt / Konzept
def sheet_deckblatt(pp, no):
    fig = page(pp, "Vorentwurf Wochenendhaus – Flurstück 7348", "–", no)
    ax = fig.add_axes([0.03, 0.16, 0.94, 0.76]); ax.axis("off")
    txt = [
        ("Bauvorhaben", "Neubau eines Wochenendhauses in Holzbauweise mit Terrasse und einem offenen Stellplatz"),
        ("Grundstück", "Grenzweg 12, 69245 Bammental · Gemarkung Bammental · Flurstück 7348"),
        ("Planungsrecht", "Bebauungsplan „Wochenendhausgebiet – 1. Änderung (Neufassung)“ der Gemeinde Bammental, rechtskräftig 19.09.2008 (Plan Nr. BP 0806, Büro Piske) · SO Wochenendhaus · GRmax 65 m² · I · o"),
        ("Ziel dieser Unterlage", "Vorabstimmung mit der Gemeinde Bammental (Bauamt / Gemeinderat) und der unteren Baurechtsbehörde (Rhein-Neckar-Kreis) vor Einreichung eines Bauantrags. Die Unterlage ist ein Vorentwurf, kein Bauantrag."),
        ("Entwurfsidee", "Ein einfacher, ruhiger Holzkörper mit steilem Satteldach – die Archetyp-Form der Wochenendhäuser im Gebiet, zeitgemäß interpretiert: unbehandelte Lärchenschalung, die silbergrau vergraut und im Waldrand zurücktritt; anthrazitfarbenes Stehfalzdach; eine große Verglasung zur Wiese nach Süden, geschützt durch einen hölzernen Schiebeladen; eine niedrige Holzterrasse, die das Haus in die Wiese legt. Das Gebäude steht auf Punktfundamenten – der Boden bleibt weitgehend unversiegelt, der Baumbestand außerhalb des Baufensters bleibt erhalten."),
        ("Varianten", "A – Bebauung exakt im Baufenster 7,20 × 5,20 m (37,44 m²), regelkonform, ohne Befreiung.\nB – Wunschvariante 8,40 × 6,80 m (57,12 m²) innerhalb der zulässigen GR von 65 m², jedoch mit Überschreitung der Baugrenze → Antrag auf Befreiung nach § 31 Abs. 2 BauGB (Begründung im Erläuterungsbericht)."),
        ("Inhalt", "Blatt 1 Deckblatt · Blatt 2 Lageplan · Blatt 3–6 Variante A (Grundriss, Ansichten, Schnitt, Isometrie) · Blatt 7–10 Variante B · Blatt 11 Nachweis Festsetzungen · Blatt 12 Gestaltung & Material"),
        ("Bauherr / Verfasser", "Bauherr: Fam. Schneider · Vorentwurf erstellt zur Abstimmung; Werkplanung, Statik, Wärmeschutz und amtlicher Lageplan folgen im Bauantrag durch bauvorlageberechtigte Entwurfsverfasser."),
    ]
    y = 0.98
    import textwrap
    for a, b in txt:
        ax.text(0, y, a, fontsize=11, weight="bold", va="top", transform=ax.transAxes)
        lines = []
        for para in b.split("\n"):
            lines += textwrap.wrap(para, 120)
        ax.text(0.20, y, "\n".join(lines), fontsize=10, va="top", transform=ax.transAxes, linespacing=1.35)
        y -= 0.035 * len(lines) + 0.045
    finish(fig, pp, f"{no:02d}_Deckblatt")

def sheet_gestaltung(pp, no):
    fig = page(pp, "Gestaltung, Material, Einfügung in die Umgebung", "–", no)
    ax = fig.add_axes([0.03, 0.16, 0.94, 0.76]); ax.axis("off")
    blocks = [
        ("Einfügung (§ 34 BauGB-Gedanke / Ortsbild)", [
            "Satteldach wie die bestehenden Wochenendhäuser im Gebiet; First parallel zur langen Gebäudeseite (Ost–West).",
            "Kleinmaßstäblicher, eingeschossiger Baukörper unter 5,50 m Firsthöhe; keine Dachaufbauten, keine Gauben, keine Dachterrasse.",
            "Farbigkeit aus der Umgebung: silbergrau vergrautes Holz + dunkles Dach = Farbtöne von Baumrinde, Schatten und Waldboden. Keine weißen Putzflächen, keine glänzenden Oberflächen.",
            "Geschlossene, ruhige Nordfassade zum Grenzweg mit nur Haustür und zwei kleinen Fenstern; die große Verglasung öffnet sich allein nach Süden zur eigenen Wiese.",
            "Bauen auf der bestehenden Wiese, keine Fällungen; Terrasse und Wege aufgeständert bzw. wasserdurchlässig.",
        ]),
        ("Material & Farben", [
            "Fassade: Lärche (europ.), sägerau, horizontale Schalung mit offener Fuge ca. 15 cm, unbehandelt → vergraut in 2–3 Jahren gleichmäßig (Referenz: Cabin-Bilder).",
            "Dach: Doppelstehfalz aus beschichtetem Stahl- oder Aluminiumblech (z. B. Prefa, Farbton anthrazit-grau matt, ca. RAL 7016/7022). Unbeschichtetes Zink/Kupfer/Blei ist gem. 7.1 unzulässig und daher nicht vorgesehen. Alternative: extensives Gründach.",
            "Fenster: Holz-Alu, außen anthrazit, innen Fichte natur; Hebe-Schiebetür 3-fach verglast, Süd.",
            "Schiebeladen: Lärche vertikal auf oberer Laufschiene – Sonnen-, Einbruch- und Sturmschutz bei Abwesenheit (Wochenendnutzung).",
            "Terrasse: Lärche/Douglasie, aufgeständert auf Stelzlagern/Schraubfundamenten, ca. 3 m tief, ohne Überdachung.",
            "Außenanlagen: Kiesweg, Schotterrasen-Stellplatz, Zisterne 3 m³, Wildwiese belassen, ggf. Obstbaumpflanzung.",
        ]),
        ("Nachhaltigkeit / Technik", [
            "Vorgefertigter Holzrahmenbau (kurze Bauzeit, geringe Belastung des Waldrands), Holzfaserdämmung, diffusionsoffen.",
            "Punkt-/Schraubfundamente statt Bodenplatte – minimaler Bodeneingriff, rückbaubar.",
            "Regenwasserrückhalt (Zisterne) gem. Hinweis im B-Plan; optionale PV-Module dachintegriert, matt, in Dachfarbe.",
            "Beheizung Wochenendnutzung: Kaminofen + elektrische Direktheizung; keine Öl-/Gastanks.",
        ]),
        ("Für das Gespräch mit der Gemeinde – offene Punkte", [
            "1. Bestätigung, dass Dachüberstände nach örtlicher Bauvorschrift (Traufe ≤ 0,80 m, Ortgang 0,20–0,60 m) über die Baugrenze hinausragen dürfen (untergeordnete Bauteile).",
            "2. Haltung der Gemeinde zu Variante B (Befreiung Baugrenze bei Einhaltung GRmax 65 m²); gemeindliches Einvernehmen § 36 BauGB.",
            "3. Waldabstand § 4 Abs. 3 LBO: Ausnahme im Benehmen mit dem Forstamt – Baufenster liegt planerisch bereits im 30-m-Streifen.",
            "4. Erschließung: Trinkwasser, Abwasser (Trennsystem), Strom; Lage des Hausanschlusses am Grenzweg.",
            "5. Artenschutz-Vorprüfung (Vogelbrut, Orchidee Listera ovata) – Zeitfenster für Bauarbeiten.",
        ]),
    ]
    import textwrap
    y = 0.99
    for title, items in blocks:
        ax.text(0, y, title, fontsize=11, weight="bold", va="top", transform=ax.transAxes); y -= 0.04
        for it in items:
            lines = textwrap.wrap(it, 150)
            ax.text(0.01, y, "• " + "\n   ".join(lines), fontsize=9.2, va="top", transform=ax.transAxes, linespacing=1.3)
            y -= 0.027 * len(lines) + 0.008
        y -= 0.02
    finish(fig, pp, f"{no:02d}_Gestaltung")

# ------------------------------------------------------------------ main
if __name__ == "__main__":
    pdf_path = os.path.join(OUT, "01_Vorentwurf_Plaene_Fl7348_Bammental.pdf")
    with PdfPages(pdf_path) as pp:
        sheet_deckblatt(pp, 1)
        sheet_lageplan(pp, VAR_A, 2)
        sheet_grundriss(pp, VAR_A, 3)
        sheet_ansichten(pp, VAR_A, 4)
        sheet_schnitt(pp, VAR_A, 5)
        sheet_isometrie(pp, VAR_A, 6)
        sheet_grundriss(pp, VAR_B, 7)
        sheet_ansichten(pp, VAR_B, 8)
        sheet_schnitt(pp, VAR_B, 9)
        sheet_isometrie(pp, VAR_B, 10)
        sheet_nachweis(pp, VAR_A, VAR_B, 11)
        sheet_gestaltung(pp, 12)
    for v in (VAR_A, VAR_B):
        d = derived(v)
        print(v["key"], {k: round(d[k], 2) for k in ("GR", "h_ridge", "h_eave", "rise", "roof_area_proj", "deck_area", "Li", "Bi")})
    print("OK", pdf_path)
