import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("PICO Box")

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

board_width=21.0
board_depth=51.0
x_hole_inset=4.8
y_hole_inset=2.0
x_spacing=11.4
y_spacing=47

wall_thickness=2.0
margin = 2.0
pillar_radius=2.0
pillar_height=4
hole_radius=0.9

usb_hole_width=15.0
usb_hole_height=8.0
usb_hole_margin=3.0

width=board_width+(2*margin)+(2*wall_thickness)
depth=board_depth+(2*margin)+(2*wall_thickness)
height=20.0
lid_height=5.0

box,lid=makeBoxAndLid(width,depth,height,lid_height,wall_thickness)

pillar = Part.makeCylinder(pillar_radius,pillar_height)
hole = Part.makeCylinder(hole_radius,pillar_height)
pillar=pillar.cut(hole)

x=wall_thickness+margin+x_hole_inset
y=wall_thickness+margin+y_hole_inset
z=wall_thickness

pillar.translate(App.Vector(x,y,z))
box = box.fuse(pillar)
pillar.translate(App.Vector(x_spacing,0,0))
box = box.fuse(pillar)
pillar.translate(App.Vector(0,y_spacing,0))
box = box.fuse(pillar)
pillar.translate(App.Vector(-x_spacing,0,0))
box = box.fuse(pillar)

x=(width-usb_hole_width)/2.0
y=depth-wall_thickness
z=wall_thickness+usb_hole_margin
pos=App.Vector(x,y,z)
usb_hole = Part.makeBox(usb_hole_width,wall_thickness,usb_hole_height,pos)
box=box.cut(usb_hole)

frame_obj = doc.addObject("Part::Feature", "box")
frame_obj.Shape = box

frame_obj = doc.addObject("Part::Feature", "lid")
frame_obj.Shape = lid


Gui.ActiveDocument.ActiveView.fitAll()