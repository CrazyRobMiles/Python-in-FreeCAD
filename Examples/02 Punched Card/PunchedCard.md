# Punched Card
![Screenshot of FreeCAD showing a punched card](/Examples/02%20Punched%20Card/PunchedCard.png)
Create a punched card with random holes.
```python
import FreeCAD as App
import FreeCADGui as Gui
import Part
import random

doc = App.newDocument("Punched Card")

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

panel = Part.makeBox(width, depth, height)

def make_hole(x,y):
  global panel
  hole = Part.makeBox(hole_width,hole_depth,depth)
  hole_pos = App.Vector(x,y,0)
  hole.translate(hole_pos)
  panel = panel.cut(hole)

for col in range (0, cols):
  for row in range(0,rows):
    if random.random()<hole_chance:
      x = col*hole_x_spacing+hole_margin
      y = row*hole_y_spacing+hole_margin
      make_hole(x,y)

frame_obj = doc.addObject("Part::Feature", "Card")
frame_obj.Shape = panel

Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)