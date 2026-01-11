import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("Extruded Panel")

width = 100
depth = 50
height = 5

v1 = App.Vector(0, 0, 0)
v2 = App.Vector(width, 0, 0)
v3 = App.Vector(width, depth, 0)
v4 = App.Vector(0, depth, 0)

e1 = Part.makeLine(v1, v2)
e2 = Part.makeLine(v2, v3)
e3 = Part.makeLine(v3, v4)
e4 = Part.makeLine(v4, v1)

wire = Part.Wire([e1, e2, e3, e4])
panel_face = Part.Face(wire)

# Extrude the face to make a solid panel
panel = panel_face.extrude(App.Vector(0, 0, height))

# Show the result
panel_obj = doc.addObject("Part::Feature", "Extruded Panel")
panel_obj.Shape = panel

Gui.ActiveDocument.ActiveView.fitAll()

