# Velcro(tm) Cards

![FreeCAD screenshot showing two cards, one with holes in and the other with corresponding bumps](/Examples/04%20Velcro%20Cards/VelcroCards.png)

These cards stick together, like Velcro. The bumps on one card match exactly the holes on the other. 

```python
import FreeCAD as App
import FreeCADGui as Gui
import Part
import random

doc = App.ActiveDocument or App.newDocument("Lumpy Card")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

width = 100
depth = 50
height = 5

rows = 10
cols = 20

hole_margin = 1.0
hole_x_spacing = width/cols
hole_y_spacing = depth/rows
hole_width = hole_x_spacing-(2*hole_margin)
hole_depth = hole_y_spacing-(2*hole_margin)
hole_chance = 0.4

pin_margin = 0.1
pin_height = 1.5
pin_width = hole_width-2*pin_margin
pin_depth = hole_depth-2*pin_margin

top_panel = Part.makeBox(width, depth, height)
bottom_panel = Part.makeBox(width, depth, height)

for row in range(0,rows):
	for col in range (0, cols):
		if random.random()<hole_chance:
			top_hole_pos = App.Vector(col*hole_x_spacing+hole_margin,row*hole_y_spacing+hole_margin,0)
			top_hole = Part.makeBox(hole_width,hole_depth,height,top_hole_pos)
			top_panel = top_panel.cut(top_hole)

			bottom_hole_pos = App.Vector(width-(col*hole_x_spacing+hole_margin+pin_margin)-pin_width,row*hole_y_spacing+hole_margin+pin_margin,height)
			bottom_pin = Part.makeBox(pin_width,pin_depth,pin_height,bottom_hole_pos)
			bottom_panel = bottom_panel.fuse(bottom_pin)

top_frame_obj = doc.addObject("Part::Feature", "Top")
top_frame_obj.Shape = top_panel

bottom_panel.translate(App.Vector(width+10,0,0))

bottom_frame_obj = doc.addObject("Part::Feature", "Bottom")
bottom_frame_obj.Shape = bottom_panel

Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)