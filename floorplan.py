#!/usr/bin/env python3
"""
Clean, CAD-editable floor plan of a 2-room apartment (2-Zimmer-Wohnung),
reconstructed from a scanned architect's drawing.

Output: floorplan.dxf  (AutoCAD R2010 DXF, fully editable in any CAD tool:
        AutoCAD, LibreCAD, QCAD, FreeCAD, BricsCAD, nanoCAD, ...)

Everything is organised on named layers so you can toggle / edit cleanly:
    A-WALL        exterior + interior walls (double line, face-to-face)
    A-DOOR        door leaves + swing arcs
    A-GLAZ        windows (Fenster) / glazed openings
    A-STAIR       staircase (Treppe)
    A-FLOR-FIXT   sanitary + kitchen fixtures (easily deletable)
    A-AREA-IDEN   room names
    A-AREA        room areas
    A-ANNO-DIMS   dimensions
    A-ANNO        misc annotation (north arrow, sill notes)

Units: metres (1 drawing unit = 1 m).  All dimensions are an interpretation
of the original scan and are meant to be fine-tuned in CAD.
"""

import math
import ezdxf
from ezdxf.enums import TextEntityAlignment

doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
msp = doc.modelspace()

# ----------------------------------------------------------------------------
# Layers
# ----------------------------------------------------------------------------
LAYERS = {
    "A-WALL":        {"color": 7,  "lineweight": 50},   # white/black, 0.50 mm
    "A-DOOR":        {"color": 3,  "lineweight": 18},    # green
    "A-GLAZ":        {"color": 4,  "lineweight": 18},    # cyan
    "A-STAIR":       {"color": 8,  "lineweight": 13},    # gray
    "A-FLOR-FIXT":   {"color": 8,  "lineweight": 13},    # gray
    "A-AREA-IDEN":   {"color": 2,  "lineweight": 25},    # yellow text
    "A-AREA":        {"color": 30, "lineweight": 13},    # orange text
    "A-ANNO-DIMS":   {"color": 1,  "lineweight": 13},    # red
    "A-ANNO":        {"color": 6,  "lineweight": 13},    # magenta
}
for name, attrs in LAYERS.items():
    lay = doc.layers.add(name, color=attrs["color"])
    lay.lineweight = attrs["lineweight"]

# A text style
if "ROOM" not in doc.styles:
    doc.styles.add("ROOM", font="arial.ttf")

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def rect(x0, y0, x1, y1, layer="A-WALL", fill=False):
    """Closed rectangle (face-to-face wall block) as a LWPOLYLINE.
    fill=True adds a solid hatch (used for walls)."""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    if fill:
        h = msp.add_hatch(color=251, dxfattribs={"layer": layer})  # light gray solid
        h.paths.add_polyline_path(pts, is_closed=True)
        h.set_solid_fill(color=251)

def hwall(x0, x1, yf0, yf1, openings=None, layer="A-WALL"):
    """Horizontal wall between faces yf0..yf1, spanning x0..x1.
    openings = list of (xa, xb) gaps (doors/windows)."""
    openings = sorted(openings or [])
    f = (layer == "A-WALL")
    x = x0
    for xa, xb in openings:
        if xa > x:
            rect(x, yf0, xa, yf1, layer, fill=f)
        x = max(x, xb)
    if x < x1:
        rect(x, yf0, x1, yf1, layer, fill=f)

def vwall(y0, y1, xf0, xf1, openings=None, layer="A-WALL"):
    """Vertical wall between faces xf0..xf1, spanning y0..y1.
    openings = list of (ya, yb) gaps."""
    openings = sorted(openings or [])
    f = (layer == "A-WALL")
    y = y0
    for ya, yb in openings:
        if ya > y:
            rect(xf0, y, xf1, ya, layer, fill=f)
        y = max(y, yb)
    if y < y1:
        rect(xf0, y, xf1, y1, layer, fill=f)

def door(hinge, radius, start_deg, sweep_deg, layer="A-DOOR"):
    """Door leaf + 90deg swing arc. hinge=(x,y), leaf shown open."""
    hx, hy = hinge
    end = start_deg + sweep_deg
    msp.add_arc(center=(hx, hy), radius=radius,
                start_angle=min(start_deg, end), end_angle=max(start_deg, end),
                dxfattribs={"layer": layer})
    ex = hx + radius * math.cos(math.radians(end))
    ey = hy + radius * math.sin(math.radians(end))
    msp.add_line((hx, hy), (ex, ey), dxfattribs={"layer": layer})

def window(x0, y0, x1, y1, n=3, layer="A-GLAZ"):
    """Window symbol filling the opening rectangle (the wall gap).
    Draws jambs at the ends and n glazing lines across the thickness."""
    horizontal = abs(x1 - x0) >= abs(y1 - y0)
    # jambs (close the wall ends)
    msp.add_line((x0, y0), (x0, y1) if horizontal else (x1, y0),
                 dxfattribs={"layer": layer})
    msp.add_line((x1, y1) if horizontal else (x0, y1), (x1, y1),
                 dxfattribs={"layer": layer})
    if horizontal:
        msp.add_line((x0, y0), (x1, y0), dxfattribs={"layer": layer})  # outer jamb
        msp.add_line((x0, y1), (x1, y1), dxfattribs={"layer": layer})
        for i in range(1, n + 1):
            y = y0 + (y1 - y0) * i / (n + 1)
            msp.add_line((x0, y), (x1, y), dxfattribs={"layer": layer})
    else:
        msp.add_line((x0, y0), (x0, y1), dxfattribs={"layer": layer})
        msp.add_line((x1, y0), (x1, y1), dxfattribs={"layer": layer})
        for i in range(1, n + 1):
            x = x0 + (x1 - x0) * i / (n + 1)
            msp.add_line((x, y0), (x, y1), dxfattribs={"layer": layer})

def room_label(cx, cy, name, area=None, h=0.26):
    msp.add_text(name, height=h, dxfattribs={"layer": "A-AREA-IDEN", "style": "ROOM"}
                 ).set_placement((cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)
    if area is not None:
        msp.add_text(f"{area:.1f} m²", height=h * 0.7,
                     dxfattribs={"layer": "A-AREA", "style": "ROOM"}
                     ).set_placement((cx, cy - h * 1.7),
                                     align=TextEntityAlignment.MIDDLE_CENTER)

def note(cx, cy, txt, h=0.16, layer="A-ANNO", align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(txt, height=h, dxfattribs={"layer": layer, "style": "ROOM"}
                 ).set_placement((cx, cy), align=align)

# ----------------------------------------------------------------------------
# Geometry constants (metres) -- wall FACE coordinates
# ----------------------------------------------------------------------------
OUT = 0.36   # exterior wall thickness
IN  = 0.24   # interior wall thickness

# Main body outer envelope
BX0, BX1 = 0.00, 9.00
BY0, BY1 = 0.00, 7.66

# Interior clear box
IX0, IX1 = BX0 + OUT, BX1 - OUT     # 0.36 .. 8.64
IY0, IY1 = BY0 + OUT, BY1 - OUT     # 0.36 .. 7.30

# Central vertical partition (left column | right column)
CV0, CV1 = 4.64, 4.88               # faces

# Right column horizontal partition (Wohnen | Schlafen)
RH0, RH1 = 3.66, 3.90

# Left column horizontal partition (Kueche | upper zone)
LH0, LH1 = 3.90, 4.14

# Upper-left vertical partition (Flur | Bad/Abst)
UV0, UV1 = 2.20, 2.44

# Bad | Abst horizontal partition
BA0, BA1 = 5.20, 5.40

# ----------------------------------------------------------------------------
# EXTERIOR WALLS (with openings)
# ----------------------------------------------------------------------------
# Left exterior wall  (apartment entrance door into Flur)
vwall(BY0, BY1, BX0, IX0, openings=[(5.60, 6.60)])
# Right exterior wall (windows F8 Wohnen, F9 Schlafen)
vwall(BY0, BY1, IX1, BX1, openings=[(1.00, 2.60), (4.80, 6.40)])
# Top exterior wall   (F10 Bad, window Schlafen)
hwall(BX0, BX1, IY1, BY1, openings=[(3.00, 3.80), (5.40, 7.60)])
# Bottom exterior wall (big glazed opening to Wintergarten)
hwall(BX0, BX1, BY0, IY0, openings=[(2.40, 6.30)])

# ----------------------------------------------------------------------------
# INTERIOR WALLS
# ----------------------------------------------------------------------------
# Central vertical partition: Kueche<->Wohnen cased opening (y1.20..2.70)
vwall(IY0, IY1, CV0, CV1, openings=[(1.20, 2.70)])
# Right column horizontal partition: Wohnen<->Schlafen 2.75 cased opening
hwall(CV1, IX1, RH0, RH1, openings=[(5.00, 7.75)])
# Left column horizontal partition: Flur<->Kueche door (x0.80..1.80)
hwall(IX0, CV0, LH0, LH1, openings=[(0.80, 1.80)])
# Upper-left vertical partition: Flur<->Bad door + Flur<->Abst door
vwall(LH1, IY1, UV0, UV1, openings=[(4.40, 5.00), (6.10, 6.90)])
# Bad | Abst partition
hwall(UV1, IX1, BA0, BA1)

# ----------------------------------------------------------------------------
# DOORS
# ----------------------------------------------------------------------------
door((IX0, 6.60), 1.00, -90, 90)             # entrance -> Flur (swing in)
door((1.80, LH1), 1.00, 90, 90)              # Flur -> Kueche
door((UV1, 6.90), 0.80, 180, 90)             # Flur -> Bad
door((UV1, 5.00), 0.60, 180, -90)            # Flur -> Abst

# ----------------------------------------------------------------------------
# WINDOWS / glazing
# ----------------------------------------------------------------------------
window(IX1, 1.00, BX1, 2.60)                 # F8 Wohnen (east)
window(IX1, 4.80, BX1, 6.40)                 # F9 Schlafen (east)
window(3.00, IY1, 3.80, BY1, n=2)            # F10 Bad (north)
window(5.40, IY1, 7.60, BY1)                 # Schlafen (north)

# ----------------------------------------------------------------------------
# WINTERGARTEN (glazed projection to the south)
# ----------------------------------------------------------------------------
WG_X0, WG_X1 = 1.80, 6.70
WG_Y0, WG_Y1 = -1.70, BY0
WGT = 0.12                                   # thin glazed frame
# frame outline (face to face)
rect(WG_X0, WG_Y0, WG_X1, WG_Y0 + WGT, fill=True)            # south frame bottom
rect(WG_X0, WG_Y0, WG_X0 + WGT, WG_Y1, fill=True)            # west frame
rect(WG_X1 - WGT, WG_Y0, WG_X1, WG_Y1, fill=True)            # east frame
# glazing (Fenster F5/F6/F7) on the three open sides
window(WG_X0 + WGT, WG_Y0, WG_X1 - WGT, WG_Y0 + WGT, n=5)    # south run
window(WG_X0, WG_Y0 + WGT, WG_X0 + WGT, WG_Y1 - 0.2, n=4)   # west
window(WG_X1 - WGT, WG_Y0 + WGT, WG_X1, WG_Y1 - 0.2, n=4)   # east
note((WG_X0 + WG_X1) / 2, WG_Y0 - 0.28,
     "VK-Verkleidung aus Trespaplatten", h=0.13, layer="A-ANNO")

# ----------------------------------------------------------------------------
# STAIRCASE (Treppe) -- communal, to the left of the apartment
# ----------------------------------------------------------------------------
SX0, SX1 = -3.00, BX0          # outer x of stairwell (shares apartment wall)
SY0, SY1 = 1.64, BY1
# stairwell walls
vwall(SY0, SY1, SX0, SX0 + OUT)                         # left wall
hwall(SX0, SX1, SY1 - OUT, SY1)                         # top wall
hwall(SX0, SX1, SY0, SY0 + OUT, openings=[(-2.20, -1.20)])  # bottom wall + Eingang
# stair run (straight, 16 risers), inside the shaft
ST_X0, ST_X1 = SX0 + OUT + 0.10, -0.30                  # tread width extents
ST_Y0, ST_Y1 = SY0 + OUT + 0.10, SY1 - OUT - 0.10
n_treads = 16
for i in range(n_treads + 1):
    y = ST_Y0 + (ST_Y1 - ST_Y0) * i / n_treads
    msp.add_line((ST_X0, y), (ST_X1, y), dxfattribs={"layer": "A-STAIR"})
# stringers
msp.add_line((ST_X0, ST_Y0), (ST_X0, ST_Y1), dxfattribs={"layer": "A-STAIR"})
msp.add_line((ST_X1, ST_Y0), (ST_X1, ST_Y1), dxfattribs={"layer": "A-STAIR"})
# direction arrow (up)
ax = (ST_X0 + ST_X1) / 2
msp.add_line((ax, ST_Y0 + 0.2), (ax, ST_Y1 - 0.2), dxfattribs={"layer": "A-STAIR"})
msp.add_line((ax, ST_Y1 - 0.2), (ax - 0.12, ST_Y1 - 0.45), dxfattribs={"layer": "A-STAIR"})
msp.add_line((ax, ST_Y1 - 0.2), (ax + 0.12, ST_Y1 - 0.45), dxfattribs={"layer": "A-STAIR"})
note((SX0 + SX1) / 2, SY0 + 0.55, "TREPPE", h=0.22, layer="A-AREA-IDEN")
note((SX0 + SX1) / 2, SY0 + 0.30, "16 Stg. 18,75/27", h=0.13, layer="A-ANNO")
note(-1.70, SY0 - 0.28, "EINGANG", h=0.16, layer="A-ANNO")

# ----------------------------------------------------------------------------
# FIXTURES (bath + kitchen) -- on deletable layer
# ----------------------------------------------------------------------------
FX = "A-FLOR-FIXT"
# --- Bad (bathroom): bathtub, washbasin, WC ---
# bathtub along right wall
rect(IX1 - 0.75, 6.40, IX1 - 0.05, 7.10, layer=FX)
msp.add_ellipse((IX1 - 0.40, 6.75), major_axis=(0.28, 0), ratio=0.45,
                dxfattribs={"layer": FX})
# washbasin
msp.add_ellipse((3.00, 5.65), major_axis=(0.26, 0), ratio=0.7,
                dxfattribs={"layer": FX})
# WC
msp.add_ellipse((3.85, 5.62), major_axis=(0.18, 0), ratio=0.8,
                dxfattribs={"layer": FX})
rect(3.70, 5.40, 4.00, 5.58, layer=FX)
# --- Kueche (kitchen): counter run along left + bottom ---
rect(IX0, 2.60, IX0 + 0.60, IY0 + 0.0, layer=FX)            # left counter (won't matter exact)
rect(IX0, 0.36, IX0 + 0.60, 2.60, layer=FX)                 # left counter
# stove + sink hint on counter
msp.add_circle((IX0 + 0.30, 1.10), 0.12, dxfattribs={"layer": FX})
msp.add_circle((IX0 + 0.30, 1.55), 0.12, dxfattribs={"layer": FX})
rect(IX0 + 0.10, 2.05, IX0 + 0.50, 2.45, layer=FX)          # sink

# ----------------------------------------------------------------------------
# ROOM LABELS + AREAS
# ----------------------------------------------------------------------------
room_label((IX0 + CV0) / 2, 2.10, "KÜCHE / ESSEN", area=4.28 * 3.54)
room_label((CV1 + IX1) / 2, 1.95, "WOHNEN", area=3.76 * 3.30)
room_label((CV1 + IX1) / 2, 5.55, "SCHLAFEN", area=3.76 * 3.40)
room_label((IX0 + UV0) / 2, 5.70, "FLUR", area=1.84 * 3.16, h=0.20)
room_label((UV1 + IX1) / 2, 6.35, "BAD", area=2.20 * 1.90, h=0.20)
room_label((UV1 + IX1) / 2, 4.65, "ABST.", area=2.20 * 1.06, h=0.16)
room_label((WG_X0 + WG_X1) / 2, -0.85, "WINTERGARTEN", h=0.20)

# ----------------------------------------------------------------------------
# DIMENSIONS (linear), DIMSCALE tuned for metres
# ----------------------------------------------------------------------------
doc.header["$DIMSCALE"] = 1.0
dimstyle = doc.dimstyles.get("Standard")
dimstyle.dxf.dimtxt = 0.18
dimstyle.dxf.dimasz = 0.12
dimstyle.dxf.dimexe = 0.08
dimstyle.dxf.dimexo = 0.08
dimstyle.dxf.dimdec = 2
dimstyle.dxf.dimlunit = 2
dimstyle.dxf.dimlfac = 1.0      # show metres (e.g. 9.00), not centimetres
dimstyle.dxf.dimrnd = 0.0
dimstyle.dxf.dimgap = 0.06

DIM_OVR = {"dimlfac": 1.0, "dimdec": 2, "dimlunit": 2, "dimtxt": 0.18,
           "dimasz": 0.12, "dimexe": 0.08, "dimexo": 0.10, "dimgap": 0.06,
           "dimtad": 1, "dimclrt": 1}

def hdim(x0, x1, y, off):
    d = msp.add_linear_dim(base=(x0, y + off), p1=(x0, y), p2=(x1, y),
                           override=DIM_OVR, dxfattribs={"layer": "A-ANNO-DIMS"})
    d.render()

def vdim(y0, y1, x, off):
    d = msp.add_linear_dim(base=(x + off, y0), p1=(x, y0), p2=(x, y1),
                           angle=90, override=DIM_OVR,
                           dxfattribs={"layer": "A-ANNO-DIMS"})
    d.render()

# overall + key room dims
hdim(BX0, BX1, BY1, 1.20)                     # overall width main body
hdim(IX0, CV0, BY1, 0.55)                     # kitchen width 4.28
hdim(CV1, IX1, BY1, 0.55)                     # right col 3.76
vdim(BY0, BY1, BX1, 1.20)                     # overall height
vdim(IY0, RH0, BX1, 0.55)                     # wohnen 3.30
vdim(RH1, IY1, BX1, 0.55)                     # schlafen 3.40
hdim(WG_X0, WG_X1, WG_Y0, -0.95)              # wintergarten width

# ----------------------------------------------------------------------------
# NORTH ARROW (top-right, original notes "NO" = north-east)
# ----------------------------------------------------------------------------
nx, ny = BX1 + 1.4, BY1 - 0.6
msp.add_line((nx, ny - 0.5), (nx, ny + 0.5), dxfattribs={"layer": "A-ANNO"})
msp.add_line((nx, ny + 0.5), (nx - 0.13, ny + 0.22), dxfattribs={"layer": "A-ANNO"})
msp.add_line((nx, ny + 0.5), (nx + 0.13, ny + 0.22), dxfattribs={"layer": "A-ANNO"})
note(nx, ny + 0.72, "N", h=0.22, layer="A-ANNO")

# ----------------------------------------------------------------------------
# TITLE
# ----------------------------------------------------------------------------
note(BX0, WG_Y0 - 1.45, "GRUNDRISS - 2-ZIMMER-WOHNUNG  (M 1:50)",
     h=0.30, layer="A-AREA-IDEN", align=TextEntityAlignment.LEFT)

doc.saveas("floorplan.dxf")
print("Wrote floorplan.dxf")
