# Desk Tidy

![FreeCAD screenshot showing the desk tidy box](/Examples/06%20Desk%20Tidy/DeskTidy.png)

You can change the size of the box and the thickness of the box walls by adjusting the values in the program.

```Python
import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("Desk Tidy")

width = 100
depth = 50
height = 50
wall_thickness = 3

inner_width = width - (2*wall_thickness)
inner_depth = depth - (2*wall_thickness)
inner_height = height - wall_thickness

outer_box = Part.makeBox(width, depth, height)
inner_box = Part.makeBox(inner_width, inner_depth, inner_height)

move = App.Vector(wall_thickness,wall_thickness,wall_thickness)
inner_box.translate(move)

tidy = outer_box.cut(inner_box)

tidy_obj = doc.addObject("Part::Feature", "Desk Tidy")
tidy_obj.Shape = tidy

Gui.ActiveDocument.ActiveView.fitAll()
```
[Back](/README.md)