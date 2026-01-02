# First Panel
![Screenshot of FreeCAD showing the first panel](/Examples/01%20FirstPanel/FirstPanel.png)

Create a simple panel
```python
import FreeCAD as App
import FreeCADGui as Gui
import Part

doc = App.newDocument("First Panel")

width = 100
depth = 50
height = 5

panel = Part.makeBox(width, depth, height)

frame_obj = doc.addObject("Part::Feature", "Panel")
frame_obj.Shape = panel

Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)