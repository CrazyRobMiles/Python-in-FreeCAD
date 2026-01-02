# Box with a Flush Lid

![Box and lid. Box has a cutout on top for the lid to fit into](/Examples/08%20Box%20with%20Flush%20Lid/BoxFlushLid.png)

This box has a push fit lid. This version prints the lid and the box at exactly the same size which on most printers gives a tight push fit. 

```Python
doc = App.newDocument("Box With Lid")

gap = 1.0
			
def makeOpenBox(width,depth,height,wall_thickness):
	inner_width = width - (2*wall_thickness)
	inner_depth = depth - (2*wall_thickness)
	inner_height = height -(wall_thickness)
	outer_box = Part.makeBox(width, depth, height)
	inner_box = Part.makeBox(inner_width, inner_depth, inner_height)
	move = App.Vector(wall_thickness,wall_thickness,wall_thickness)
	inner_box.translate(move)
	return outer_box.cut(inner_box)

# Make the box

def makeBoxAndLid(width,depth,box_height,lid_height,wall_thickness):
	
	# Allow for the thickness of the lid
	box_height=box_height-wall_thickness

	# Make the box
	box = makeBox(width,depth,box_height,wall_thickness)
	
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

	lid = makeBox(width,depth,lid_height+wall_thickness,wall_thickness/2.0)
	
	# Move the lid where we can see it more easily
	lid.translate(App.Vector(width+10,0,0))
	
	return (box,lid)	

width=50
depth=50
height=20
wall_thickness=2
lid_height=5

box,lid=makeBoxAndLid(width,depth,height,lid_height,wall_thickness)
	
# Display everything 

box_obj = doc.addObject("Part::Feature", "Desk Tidy Box")
box_obj.Shape = box

lid_obj = doc.addObject("Part::Feature", "Desk Tidy Lid")
lid_obj.Shape = lid

Gui.ActiveDocument.ActiveView.fitAll()
```

The `makeOpenBox` function will make a box with the specified dimensions. It returns the box created. The `makeBoxAndLid` function creates a box and a lid and returns them as a tuple. 


[Back](/README.md)