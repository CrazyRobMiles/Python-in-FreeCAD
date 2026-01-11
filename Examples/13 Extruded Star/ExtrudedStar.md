# Extruded Star

![Extruded star shape in FreeCAD](/Examples/13%20Extruded%20Star/ExtrudedStar.png)

You can change the number of points in the star by modifying the value of the **points** variable. 
```Python
import FreeCAD as App
import FreeCADGui as Gui
import Part
import math

points = 12          # points in the star
r_outer = 30
r_inner = 15
height = 120

vectors = []

doc = App.ActiveDocument or App.newDocument("Extruded Star")

half_step = (2 * math.pi / points) / 2
angle=0

for i in range(points):

    # Outer point (tip)
    vectors.append(App.Vector(
        r_outer * math.sin(angle),
        r_outer * math.cos(angle),
        0
    ))

    angle=angle+half_step

    # Inner point (valley)
    vectors.append(App.Vector(
        r_inner * math.sin(angle),
        r_inner * math.cos(angle),
        0
    ))

    angle=angle+half_step

# Close polygon
vectors.append(vectors[0])

wire = Part.makePolygon(vectors)

face = Part.Face(wire)

solid = face.extrude(App.Vector(0, 0, height))
obj = doc.addObject("Part::Feature", "Extruded Star")
obj.Shape = solid

doc.recompute()
Gui.ActiveDocument.ActiveView.fitAll()
```
[Back](/README.md)