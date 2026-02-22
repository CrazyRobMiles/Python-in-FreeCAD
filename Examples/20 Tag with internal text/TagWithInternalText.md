# Tag with Internal Text
![A 3D view of a tag with no text on it.](/Examples/20%20Tag%20with%20internal%20text/TagWithInternalText.png)

This tag generator draws the text inside the tag as an internal layer. You can follow the same sequence as for the [tag with embedded text](/Examples/19%20Tag%20with%20embedded%20text/TagWithEmbeddedText.md) to slice and print this model. It works especially well if the tag base is printed with white or transparent filament. 

```python
# Tag with internal text
import FreeCAD as App
import FreeCADGui as Gui
import Part
import Draft

tag_text="DAVID"
depth = 30
height = 3


# ---------- Helper: pick a usable bold font ----------
def find_font(explicit_path=None):
    if explicit_path and os.path.exists(explicit_path):
        return explicit_path
    candidates = [
        # Windows
        r"C:\Windows\Fonts\arialbd.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Bold TTF not found. Set font_path explicitly.")

if App.ActiveDocument:
    doc=App.ActiveDocument
else:
    doc=App.newDocument("Tag with Text")

for obj in doc.Objects:
    doc.removeObject(obj.Name) 

font = find_font()
text_margin=1.0
text_height=1.0
text_inset=0.4
text_size = depth-(2*text_margin)

text_face = Draft.makeShapeString(String=tag_text, FontFile=font, Size=text_size, Tracking=0)
bb=text_face.Shape.BoundBox
width=bb.XLength +(depth/2)

text = text_face.Shape.extrude(App.Vector(0,0,text_height))
text.translate(App.Vector(0,text_margin,height-text_height-text_inset))
App.ActiveDocument.removeObject(text_face.Name)

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

tag_face = Part.Face([tag_wire,hole_wire])

# Extrude the face to make a solid panel
tag = tag_face.extrude(App.Vector(0, 0, height))

tag=tag.cut(text)

# Show the result
panel_obj = doc.addObject("Part::Feature", tag_text+" base")
panel_obj.Shape = tag

panel_obj = doc.addObject("Part::Feature", tag_text+" text")
panel_obj.Shape = text


Gui.ActiveDocument.ActiveView.fitAll()

```

[Back](/README.md)