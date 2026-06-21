import matplotlib
matplotlib.use("Agg")
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

doc = ezdxf.readfile("floorplan.dxf")
msp = doc.modelspace()
fig = plt.figure(figsize=(14, 12))
ax = fig.add_axes([0, 0, 1, 1])
ctx = RenderContext(doc)
Frontend(ctx, MatplotlibBackend(ax)).draw_layout(msp, finalize=True)
ax.set_facecolor("white")
fig.savefig("floorplan_preview.png", dpi=130, facecolor="white")
print("ok")
