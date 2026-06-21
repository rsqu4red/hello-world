# Grundriss – 2-Zimmer-Wohnung (CAD)

A clean, orthogonal reconstruction of the scanned architect's drawing, ready to
edit in any CAD program.

## Files
- **`floorplan.dxf`** – the editable drawing (AutoCAD R2010 DXF). Open in
  AutoCAD, LibreCAD, QCAD, FreeCAD, BricsCAD, nanoCAD, etc.
- `floorplan.py` – the generator script (re-run to regenerate the DXF).
- `floorplan_preview.png` – a quick raster preview.
- `render.py` – renders the preview from the DXF.

## Layers
| Layer | Content |
|-------|---------|
| `A-WALL` | exterior + interior walls (solid-filled, face-to-face) |
| `A-DOOR` | door leaves + swing arcs |
| `A-GLAZ` | windows / glazed openings |
| `A-STAIR` | staircase (Treppe) |
| `A-FLOR-FIXT` | bath + kitchen fixtures (delete freely) |
| `A-AREA-IDEN` / `A-AREA` | room names / areas |
| `A-ANNO-DIMS` | dimensions |
| `A-ANNO` | north arrow, notes, title |

## Rooms
Schlafen (bedroom) · Wohnen (living) · Küche/Essen (kitchen/dining) ·
Bad (bath) · Abst. (storage) · Flur (hall) · Wintergarten (conservatory),
plus the communal Treppe (stairs) / Eingang.

## Units & accuracy
1 drawing unit = 1 metre. Dimensions are an **interpretation** of the
hand-drawn scan and are meant to be fine-tuned in CAD. Key dims taken from the
original: outer width ≈ 9.00 m, kitchen 4.28 m, right column 3.76 m,
Wohnen↔Schlafen opening 2.75 m, Wintergarten ≈ 4.90 m wide. To change
anything parametrically, edit the face-coordinate constants near the top of
`floorplan.py` and re-run `python3 floorplan.py`.
