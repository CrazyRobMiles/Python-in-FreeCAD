# Tag With Hole
![A line drawing of a path which contains a rounded element at one end. It also contains a hole cut in the rounded end of the tag ](/Examples/17%20Tag%20with%20hole/TagWithHole.png)

This shows how we can create paths and then subtract them from another path to create a hole. The circle is created and its drawing winding is reversed so that it will be subtracted from the rounded tag design.  
```python
# Extruded Panel
import FreeCAD as App
import FreeCADGui as Gui
import Part
import Draft


def make_label(text, pos, font_size=4):
    t = Draft.make_text(text, placement=App.Placement(pos, App.Rotation()))
    try:
        t.ViewObject.FontSize = font_size
        t.ViewObject.Justification = "Center"
        t.ViewObject.TextColor = (0.0, 0.0, 0.0) 
        t.Label=text
    except Exception:
        pass
    return t
    
if App.ActiveDocument:
    doc=App.ActiveDocument
else:
    doc=App.newDocument("Tag with hole")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

width = 100
depth = 50
height = 5
curve_radius = depth/2.0
curve_middle = App.Vector(width+curve_radius,curve_radius,0)

v1 = App.Vector(0, 0, 0)
v2 = App.Vector(width, 0, 0)
v3 = App.Vector(width, depth, 0)
v4 = App.Vector(0, depth, 0)

e1 = Part.makeLine(v1, v2)
e2 = Part.Arc(v2, curve_middle, v3).toShape()
e3 = Part.makeLine(v3, v4)
e4 = Part.makeLine(v4, v1)

tag_wire = Part.Wire([e1, e2, e3, e4])

hole_margin=5.0
hole_radius = curve_radius-hole_margin
hole_pos = App.Vector(width,curve_radius,0)

tag_hole = Part.makeCircle(hole_radius, hole_pos)
hole_wire = Part.Wire(tag_hole)
hole_wire.reverse()

panel_face = Part.Face([tag_wire,hole_wire])

# Extrude the face to make a solid panel
panel = panel_face.extrude(App.Vector(0, 0, height))

make_label("v1", v1 + App.Vector(-5, 0, 0), font_size=5)
make_label("v2", v2 + App.Vector(0, -5, 0), font_size=5)
make_label("v3", v3 + App.Vector(5, 0, 0), font_size=5)
make_label("v4", v4 + App.Vector(-5, 0, 0), font_size=5)

make_label("e4", App.Vector(-5, depth/2.0, 0), font_size=5)
make_label("e3", App.Vector(width/2, depth+2, 0), font_size=5)
make_label("e2", App.Vector(width+curve_radius+5, depth/2, 0), font_size=5)
make_label("e1", App.Vector(width/2, -5, 0), font_size=5)

# Show the result
panel_obj = doc.addObject("Part::Feature", "Tag")
panel_obj.Shape = panel

Gui.ActiveDocument.ActiveView.fitAll()

```

[Back](/README.md)