import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("Box With Lid")
	
def makeOpenBox(width,depth,height,wall_thickness):
	inner_width = width - (2*wall_thickness)
	inner_depth = depth - (2*wall_thickness)
	inner_height = height - wall_thickness
	outer_box = Part.makeBox(width, depth, height)
	inner_box = Part.makeBox(inner_width, inner_depth, inner_height)
	move = App.Vector(wall_thickness,wall_thickness,wall_thickness)
	inner_box.translate(move)
	return outer_box.cut(inner_box)

box_width=100
box_depth=50
box_height=30
wall_thickness=3
lid_height=10

gap = 1.0

# Make the box

box = makeOpenBox(box_width,box_depth,box_height,wall_thickness)

# The lid needs to fit over the box

lid_width=box_width+(2*wall_thickness)+gap
lid_depth=box_depth+(2*wall_thickness)+gap

lid = makeOpenBox(lid_width,lid_depth,lid_height,wall_thickness)

# Move the lid where we can see it more easily
lid.translate(App.Vector(lid_width+10,0,0))

# Display everything 

box_obj = doc.addObject("Part::Feature", "Desk Tidy Box")
box_obj.Shape = box

lid_obj = doc.addObject("Part::Feature", "Desk Tidy Lid")
lid_obj.Shape = lid

Gui.ActiveDocument.ActiveView.fitAll()