import FreeCAD as App
import FreeCADGui as Gui
import Part
import math
import random

### Random ranges

# Number of stars
number_of_stars=5

# Number of points in the star - The example uses a four pointed star
points_range=(4,10)

# Range of valeus for the outer radius of the stars
outer_range=(30,30)

# Range of values for the inner raduis of the stars
# This can intersect with the outer range, but the program will never generate a star with an outer radius which is less than the inner one
inner_range=(28,28)

# range of heights of each star
height_range=(50,120)

# range of x spacing
x_space_range=(5,20)

# range of y spacing
y_space_range=(0,0)


doc = App.ActiveDocument or App.newDocument("Mutli Stars")

def make_extruded_solid_and_cut(points,r_outer,r_inner,height,wall_thickness):

    vectors = []
    vectors_cut = []

    r_outer_cut = r_outer-wall_thickness
    r_inner_cut = r_inner-wall_thickness

    half_step = (2 * math.pi / points) / 2
    angle=0
    
    for i in range(points):
        s = math.sin(angle)
        c = math.cos(angle)

        # Outer point (tip)
        vectors.append(App.Vector(
            r_outer * s,
            r_outer * c,
            0
        ))

        vectors_cut.append(App.Vector(
            r_outer_cut * s,
            r_outer_cut * c,
            0
        ))

        angle=angle+half_step

        s = math.sin(angle)
        c = math.cos(angle)

        # Inner point (valley)
        vectors.append(App.Vector(
            r_inner * s,
            r_inner * c,
            0
        ))

        vectors_cut.append(App.Vector(
            r_inner_cut * s,
            r_inner_cut * c,
            0
        ))

        angle=angle+half_step

    # Close polygon
    vectors.append(vectors[0])
    vectors_cut.append(vectors_cut[0])

    wire = Part.makePolygon(vectors)
    face = Part.Face(wire)
    solid = face.extrude(App.Vector(0, 0, height))

    wire_cut = Part.makePolygon(vectors_cut)
    face_cut = Part.Face(wire_cut)
    cut = face_cut.extrude(App.Vector(0, 0, height_range[1]))
    cut.translate(App.Vector(0,0,wall_thickness))

    return solid,cut

def make_extruded_vase(points,r_outer,r_inner,height,wall_thickness):
    print(f"Making vase points:{points} outer:{r_outer} inner:{r_inner} height:{height} wall_thickness:{wall_thickness}")
    outer = make_extruded_star(points,r_outer,r_inner,height)
    inner = make_extruded_star(points,r_outer-wall_thickness,r_inner-wall_thickness,height)
    inner.translate(App.Vector(0,0,wall_thickness))
    vase = outer.cut(inner)
    return (vase,inner)

def make_random_vase_and_cut(wall_thickness):
    points=random.randint(*points_range)
    r_outer=random.randint(*outer_range)
    while True:
        r_inner=random.randint(*inner_range)
        if r_outer-r_inner>wall_thickness:
	        break
    height=random.randint(*height_range)
    return make_extruded_solid_and_cut(points,r_outer,r_inner,height,wall_thickness)


wall_thickness=1.5
result = None
result_cut = None
pos=App.Vector(0,0,0)

for i in range(number_of_stars):
    vase,cut = make_random_vase_and_cut(wall_thickness)
    if result==None:
        result=vase
        result_cut=cut
    else:
        x_offset=random.randint(*x_space_range)
        y_offset=random.randint(*y_space_range)
        pos.x=pos.x+x_offset
        pos.y=pos.y+y_offset
        vase.translate(pos)
        cut.translate(pos)
        result=result.fuse(vase)
        result_cut=result_cut.fuse(cut)

vase=result.cut(result_cut)

obj = doc.addObject("Part::Feature", "ExtrudedVase")
obj.Shape = vase
doc.recompute()

Gui.ActiveDocument.ActiveView.fitAll()
