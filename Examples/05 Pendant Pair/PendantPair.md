# Pendant Pair

![A FreeCAD screenshot showing a pair of matching pendants with holds and pillars](/Examples/05%20Pendant%20Pair/PendantPair.png)

The program makes a pair of pendants which fit together, with exactly matching pillars and holes. The program uses Python random number generation which will make each pair of pendants unique and complementary. The holes are slightly larger than the pillars to allow for tolerances in the print process. 

```python
import FreeCAD as App
import FreeCADGui as Gui
import Part

import random

doc = App.ActiveDocument or App.newDocument("Pendant Pair")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

pin_width = 5
pin_depth = 5
pin_height = 3
panel_height = 4
hole_radius = 2
pin_radius = 1.75
hanger_hole_radius=10.0

clearance = 0.1

x_pins = 10
y_pins = 5

total_width = pin_width * x_pins
total_depth = pin_depth * y_pins
total_height= pin_height+panel_height

panel1 = Part.makeBox(total_width,total_depth,panel_height)

panel2 = Part.makeBox(total_width,total_depth,panel_height)

hanger = Part.makeCylinder(total_depth/2.0,panel_height)

hanger_hole = Part.makeCylinder(hanger_hole_radius,panel_height)
hanger=hanger.cut(hanger_hole)

hanger.translate(App.Vector(0,total_depth/2.0,0))

panel1 = panel1.fuse(hanger)
panel2 = panel2.fuse(hanger)


for x in range(x_pins):
	for y in range(y_pins):
		
		pos1 = App.Vector(x*pin_width+pin_width/2, y*pin_depth+pin_depth/2.0,panel_height)
	
		pos2 = App.Vector((x_pins-x-1)*pin_width+pin_width/2, y*pin_depth+pin_depth/2.0,panel_height)
		
		half_height = pin_height / 2.0
		
		random_height=random.uniform(-pin_height,pin_height)

		abs_height = abs(random_height)
		
	
		if random_height<0:
			hole = Part.makeCylinder(hole_radius,abs_height+clearance,pos1,App.Vector(0,0,-1))
			pin = Part.makeCylinder(pin_radius,abs_height,pos2)
			panel1=panel1.cut(hole)
			panel2=panel2.fuse(pin)
		else:
			hole = Part.makeCylinder(hole_radius,abs_height+clearance,pos2,App.Vector(0,0,-1))
			pin = Part.makeCylinder(pin_radius,abs_height,pos1)
			panel2=panel2.cut(hole)
			panel1=panel1.fuse(pin)
		

panel2.translate(App.Vector(pin_width*x_pins + total_depth/2.0 + 5,0,0))


panel1_obj = doc.addObject("Part::Feature", "Pendant 1")
panel1_obj.Shape = panel1

panel2_obj = doc.addObject("Part::Feature", "Pendant 2")
panel2_obj.Shape = panel2

Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)