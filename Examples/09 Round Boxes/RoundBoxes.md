# Round Boxes

![Lots of round boxes with matching lids](/Examples/09%20Round%20Boxes/RoundBoxes.png)

We can make round boxes as well as square ones. This code uses a loop to create a number of different sized boxes which will fit inside each other if you print them all....

```Python
import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("Round Boxes")

def makeOpenBox(width,depth,height,wall_thickness):
	inner_width = width - (2*wall_thickness)
	inner_depth = depth - (2*wall_thickness)
	inner_height = height -(wall_thickness)
	outer_box = Part.makeBox(width, depth, height)
	inner_box = Part.makeBox(inner_width, inner_depth, inner_height)
	move = App.Vector(wall_thickness,wall_thickness,wall_thickness)
	inner_box.translate(move)
	return outer_box.cut(inner_box)

def makeOpenRoundBox(diameter,height,wall_thickness):
	inner_diameter = diameter - (2*wall_thickness)
	inner_height = height -(wall_thickness)
	outer_box = Part.makeCylinder(diameter/2, height)
	inner_box = Part.makeCylinder(inner_diameter/2, inner_height)
	move = App.Vector(0,0,wall_thickness)
	inner_box.translate(move)
	return outer_box.cut(inner_box)

def makeRoundBoxAndLid(diameter,box_height,lid_height,wall_thickness):
	
	# Allow for the thickness of the lid
	box_height=box_height-wall_thickness

	# Make the box
	box = makeOpenRoundBox(diameter,box_height,wall_thickness)
	
	# Create the outer cutting box
	rim_cut = Part.makeCylinder(diameter/2.0,lid_height)
	# Now cut a hole in the rim cutter
	rim_hole = Part.makeCylinder((diameter-wall_thickness)/2.0,lid_height)
	# Cut a hole in the cutter
	rim_cut = rim_cut.cut(rim_hole)
	# Move the cutter to the right position
	rim_cut.translate(App.Vector(0,0,box_height-lid_height))
	# Cut the rim off the box
	box=box.cut(rim_cut)

	lid = makeOpenRoundBox(diameter,lid_height+wall_thickness,wall_thickness/2.0)
	
	# Move the lid where we can see it more easily
	lid.translate(App.Vector(diameter+10,0,0))
	
	return (box,lid)	

def makeBoxAndLid(width,depth,box_height,lid_height,wall_thickness):
	
	# Allow for the thickness of the lid
	box_height=box_height-wall_thickness

	# Make the box
	box = makeOpenBox(width,depth,box_height,wall_thickness)
	
	# Create the outer cutting box
	rim_cut = Part.makeBox(width,depth,lid_height)
	# Now cut a hole in the rim cutter
	rim_hole = Part.makeBox(width-wall_thickness,depth-wall_thickness,lid_height)
	# Move the rim hole cutter into the right position
	rim_hole.translate(App.Vector(wall_thickness/2.0,wall_thickness/2.0,0))
	# Cut a hole in the cutter
	rim_cut = rim_cut.cut(rim_hole)
	# Move the cutter to the right position
	rim_cut.translate(App.Vector(0,0,box_height-lid_height))
	# Cut the rim off the box
	box=box.cut(rim_cut)

	lid = makeOpenBox(width,depth,lid_height+wall_thickness,wall_thickness/2.0)
	
	# Move the lid where we can see it more easily
	lid.translate(App.Vector(width+10,0,0))
	
	return (box,lid)	
	

height=50
y=0
wall_thickness=2
clearance=1

for size in range(100,20,-10):

	lid_height = height * 0.2

	box,lid = makeRoundBoxAndLid(size,height,lid_height,wall_thickness)

	box.translate(App.Vector(0,y+size/2,0))
	lid.translate(App.Vector(0,y+size/2,0))

	frame_obj = doc.addObject("Part::Feature", f"Round Box{size}")
	frame_obj.Shape = box

	frame_obj = doc.addObject("Part::Feature", f"Round Lid {size}")
	frame_obj.Shape = lid

	y=y+size+10
	height=height-(2*wall_thickness) - clearance


Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)