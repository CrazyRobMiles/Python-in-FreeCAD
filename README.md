# Python in FreeCAD
Sample Python programs which create interesting objects in FreeCAD. You can open these files as Python programs using **File>Open** in FreeCAD version 1.0.  

All the programs are in the code folder. If you want general tips on Running Python in FreeCAD and how to get started, go [here](https://github.com/CrazyRobMiles/freecad-tips)

## Simple Panel
When you run this program it creates a simple panel.
## Punched Card
When you run this program it creates a punched card with random holes in it. 
## Super Secret Encoder
![Picture of the Secret Encoder](/images/encoder.png)
```
# Enter the text that you want to encode - use newlines to add lines
secret_text = "Secret\nMessages"

# Select how many panels you want to produce
no_of_panels = 2

# Set the hole spacing on the decoder panel in mm
hole_x_spacing = 3.0
hole_y_spacing = 3.0

# Set the margin around each hole in mm
hole_margin = 0.5

# Set the thickness of each panel in mm
height = 2.0

```
You can configure the program by changing these values at the top of the program. If you want your secret code to contain more than one line of text you can use "\n" characters to split the lines:

```
secret_text="Hello\nWorld"
```

Have Fun!

Rob Miles
