# Pipe Path
![FreeCAD showing a blue hollow pipe following a rounded rectangle path](/Examples/26%20Pipe%20path/PipePath.png)

This program introduces `makePipeShell`, a FreeCAD function that creates a solid by sweeping a cross-section profile along a path wire. Here it sweeps a circular cross-section around a rounded rectangle, producing a hollow pipe.

## How it works

The path is built from four straight edges joined by four quarter-circle arcs — one at each corner. The circular profile is placed at the start of the path, oriented perpendicular to it. `makePipeShell` then moves the profile along the entire path, generating a smooth continuous solid.

## Control Values

* **WIDTH** — overall width of the rectangle in mm
* **HEIGHT** — overall height of the rectangle in mm
* **CORNER_RADIUS** — radius of each rounded corner in mm
* **PIPE_RADIUS** — radius of the circular pipe cross-section in mm

```python
import math
import FreeCAD as App
import FreeCADGui as Gui
import Part

if App.ActiveDocument:
    doc = App.ActiveDocument
else:
    doc = App.newDocument("PipePath")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

# ── Configuration ─────────────────────────────────────────────────────────────

WIDTH         = 100.0   # overall width
HEIGHT        =  60.0   # overall height
CORNER_RADIUS =  10.0   # radius of each rounded corner
PIPE_RADIUS   =   3.0   # radius of the pipe cross-section

# ── Build the rounded-rectangle path wire ─────────────────────────────────────
# 4 straight edges connected by 4 quarter-circle arcs.
# Arc midpoints sit at 45° on each corner circle (centre ± r/√2 in each axis).

r   = CORNER_RADIUS
mid = r / math.sqrt(2.0)

# Points where straight edges meet arc tangent points
bot_l  = App.Vector(r,         0,      0)
bot_r  = App.Vector(WIDTH - r, 0,      0)
rgt_b  = App.Vector(WIDTH,     r,      0)
rgt_t  = App.Vector(WIDTH,     HEIGHT - r, 0)
top_r  = App.Vector(WIDTH - r, HEIGHT, 0)
top_l  = App.Vector(r,         HEIGHT, 0)
lft_t  = App.Vector(0,         HEIGHT - r, 0)
lft_b  = App.Vector(0,         r,      0)

# 45° midpoints on each arc
mid_br = App.Vector(WIDTH - r + mid, r          - mid, 0)   # bottom-right
mid_tr = App.Vector(WIDTH - r + mid, HEIGHT - r + mid, 0)   # top-right
mid_tl = App.Vector(r         - mid, HEIGHT - r + mid, 0)   # top-left
mid_bl = App.Vector(r         - mid, r          - mid, 0)   # bottom-left

e1 = Part.makeLine(bot_l, bot_r)
e2 = Part.Arc(bot_r, mid_br, rgt_b).toShape()
e3 = Part.makeLine(rgt_b, rgt_t)
e4 = Part.Arc(rgt_t, mid_tr, top_r).toShape()
e5 = Part.makeLine(top_r, top_l)
e6 = Part.Arc(top_l, mid_tl, lft_t).toShape()
e7 = Part.makeLine(lft_t, lft_b)
e8 = Part.Arc(lft_b, mid_bl, bot_l).toShape()

path_wire = Part.Wire([e1, e2, e3, e4, e5, e6, e7, e8])

# ── Build the circular profile at the start of the path ───────────────────────
# The path starts along +X at bot_l, so the profile sits in the YZ plane there.

profile_circle = Part.makeCircle(PIPE_RADIUS, bot_l, App.Vector(1, 0, 0))
profile_wire   = Part.Wire(profile_circle)

# ── Sweep the profile along the path ─────────────────────────────────────────
# frenet=False (Corrected Frenet) keeps world-Z stable so the cross-section
# does not twist as it travels around the corners.

pipe = path_wire.makePipeShell([profile_wire], True, False)

# ── Display ───────────────────────────────────────────────────────────────────

pipe_obj = doc.addObject("Part::Feature", "PipePath")
pipe_obj.Shape = pipe
try:
    pipe_obj.ViewObject.ShapeColor = (0.20, 0.55, 0.85)
except Exception:
    pass

doc.recompute()
Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)
