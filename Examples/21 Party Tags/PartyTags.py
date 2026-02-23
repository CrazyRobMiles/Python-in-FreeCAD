# Party tags

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Draft

tag_text = ["NAMES","GO","HERE"]

depth = 15
height = 3
hole_margin=3.0

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

def make_tag(tag_text):

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
    
    hole_radius = curve_radius-hole_margin
    hole_pos = App.Vector(width,curve_radius,0)
    
    tag_hole = Part.makeCircle(hole_radius, hole_pos)
    hole_wire = Part.Wire(tag_hole)
    hole_wire.reverse()
    
    tag_face = Part.Face([tag_wire,hole_wire])
    
    # Extrude the face to make a solid panel
    tag = tag_face.extrude(App.Vector(0, 0, height))
    
    tag=tag.cut(text)
    
    return (tag,text,width+depth/2.0)

base_width=200
base_depth=180
tag_gap=2

tag_x=0
tag_y=0

tags = None
texts = None

for name in tag_text:

    tag,text,width = make_tag(name)

    final_x=tag_x + width + tag_gap
    
    if final_x>base_width:
        tag_x=0
        tag_y=tag_y+depth+tag_gap

    tag.translate(App.Vector(tag_x,tag_y,0))
    text.translate(App.Vector(tag_x,tag_y,0))
    
    if tags==None:
        tags=tag
        texts=text
    else:
        tags=tags.fuse(tag)
        texts=texts.fuse(text)

    tag_x=tag_x + width + tag_gap
        
# Show the result
panel_obj = doc.addObject("Part::Feature", "Base")
panel_obj.Shape = tags

panel_obj = doc.addObject("Part::Feature", "Text")
panel_obj.Shape = texts


Gui.ActiveDocument.ActiveView.fitAll()
