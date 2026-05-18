# Spaghetti Maker
![FreeCAD showing a yellow curved pipe winding through three dimensions](/Examples/27%20Spaghetti%20maker/SpaghettiMaker.png)

This program extends the pipe path idea into three dimensions. It generates a set of random waypoints in 3D space, fits a smooth BSpline curve through them, and sweeps a circular cross-section along it using `makePipeShell` — producing a shape that looks like a piece of spaghetti.

## How it works

A BSpline curve is interpolated through the random waypoints, giving a smooth path that passes through every point. The circular profile is aligned perpendicular to the path at the start point. `makePipeShell` then sweeps the profile along the full length of the curve.

Changing `RANDOM_SEED` produces a completely different shape while keeping all other settings the same.

## Control Values

* **NUM_POINTS** — number of random waypoints the path passes through
* **SPREAD_MM** — XY spread of the waypoints in mm
* **HEIGHT_MM** — Z spread of the waypoints in mm
* **PIPE_RADIUS** — radius of the circular pipe cross-section in mm
* **RANDOM_SEED** — change this integer for a different shape

```python
import random
import FreeCAD as App
import FreeCADGui as Gui
import Part

if App.ActiveDocument:
    doc = App.ActiveDocument
else:
    doc = App.newDocument("SpaghettiMaker")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

# ── Configuration ─────────────────────────────────────────────────────────────

NUM_POINTS  = 15     # number of random waypoints the path passes through
SPREAD_MM   = 100.0  # XY spread of the path
HEIGHT_MM   = 40.0   # Z spread of the path
PIPE_RADIUS = 1.5    # radius of the pipe cross-section
RANDOM_SEED = 42     # change for a different shape

# ── Generate random waypoints ─────────────────────────────────────────────────

random.seed(RANDOM_SEED)
points = [
    App.Vector(
        random.uniform(0, SPREAD_MM),
        random.uniform(0, SPREAD_MM),
        random.uniform(0, HEIGHT_MM),
    )
    for _ in range(NUM_POINTS)
]

# ── Build a smooth BSpline through all waypoints ──────────────────────────────

curve = Part.BSplineCurve()
curve.interpolate(points)
path_wire = Part.Wire(curve.toShape())

# ── Build the circular profile at the start of the path ───────────────────────
# Orient the profile circle perpendicular to the path by pointing its normal
# along the approximate tangent at the start (direction to the second waypoint).

d = points[1] - points[0]
start_dir = App.Vector(d.x, d.y, d.z)
start_dir.normalize()

profile_circle = Part.makeCircle(PIPE_RADIUS, points[0], start_dir)
profile_wire   = Part.Wire(profile_circle)

# ── Sweep the profile along the path ─────────────────────────────────────────

pipe = path_wire.makePipeShell([profile_wire], True, False)

# ── Display ───────────────────────────────────────────────────────────────────

pipe_obj = doc.addObject("Part::Feature", "Spaghetti")
pipe_obj.Shape = pipe
try:
    pipe_obj.ViewObject.ShapeColor = (0.95, 0.85, 0.55)
except Exception:
    pass

doc.recompute()
Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)
