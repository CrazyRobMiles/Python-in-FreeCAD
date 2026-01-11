import FreeCAD as App
import FreeCADGui as Gui
import Part
import math

points = 12          # points in the star
r_outer = 40
r_inner = 25
height = 120

doc = App.ActiveDocument or App.newDocument("Extruded Star")

def make_extruded_star(points,r_outer,r_inner,height):

    vectors = []

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
    return solid

wall_thickness=1.5
outer = make_extruded_star(points,r_outer,r_inner,height)
inner = make_extruded_star(points,r_outer-wall_thickness,r_inner-wall_thickness,height)
inner.translate(App.Vector(0,0,wall_thickness))
vase = outer.cut(inner)

obj = doc.addObject("Part::Feature", "ExtrudedVase")
obj.Shape = vase	
doc.recompute()

Gui.ActiveDocument.ActiveView.fitAll()
