# Tag with Embedded text
![A line drawing of a path which contains a rounded element at one end. The vertices and the edges are labeled.](/Examples/19%20Tag%20with%20embedded%20text/TagWithEmbeddedText.png)

This shows how we can embed text in a 3D printed tag. It must be printed on a 3D printer which supports multiple colour output. The program produces two documents when it runs:

![A FreeCAD model view containing to elements, a base and text](/Examples/19%20Tag%20with%20embedded%20text/tag%20model.png)

You need to export both of these to separate files and then import them into your slicer (Bambu lab slicer example shown). Select both of the STL files and drag them into the slicer and you will see the following dialogue:

![Bambu slicer dialog asking "Load this files as a single object with multiple parts?"](/Examples/19%20Tag%20with%20embedded%20text/Object%20with%20multiple%20parts.png)

Click Yes. Now switch to the Object view in the slicer, right click one of the parts and select Filament from the pop up dialogue as shown:

![Bambu slicer showing the Object view and the filament selection dialogue](/Examples/19%20Tag%20with%20embedded%20text/Object%20filament%20selection.png)

I selected yellow filament for the text so the object would be produced with yellow text on a blue background. If you want a really smooth finish for the tag face and you are using a smooth print plage you can use the slicer to rotate the object to printed 180 degrees so that the text is face down on the build plate. 

```python
# Tag with embedded text

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Draft

tag_text="IMMY"
depth = 30
height = 3

def find_font():
    candidates = [
        # Windows
        r"C:\Windows\Fonts\arialbd.ttf",
        # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        # Flatpak
        "/usr/share/fonts/liberation-fonts/LiberationSans-Bold.ttf"]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Font not found")

if App.ActiveDocument:
    doc=App.ActiveDocument
else:
    doc=App.newDocument("Tag with Text")

for obj in doc.Objects:
    doc.removeObject(obj.Name) 

font = find_font()
text_margin=1.0
text_height=1.0
text_size = depth-(2*text_margin)

shape_string = Draft.makeShapeString(String=tag_text, FontFile=font, Size=text_size, Tracking=0)
bb=shape_string.Shape.BoundBox
width=bb.XLength +(depth/2)

text = shape_string.Shape.extrude(App.Vector(0,0,text_height))
text.translate(App.Vector(0,text_margin,height-text_height))
App.ActiveDocument.removeObject(shape_string.Name)

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
panel_obj = doc.addObject("Part::Feature", tag_text+"Base")
panel_obj.Shape = tag

panel_obj = doc.addObject("Part::Feature", tag_text+"Text")
panel_obj.Shape = text


Gui.ActiveDocument.ActiveView.fitAll()

```

[Back](/README.md)