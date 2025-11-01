# Enter the text that you want to encode
secret_text = "Secret\nMessages"

# Select how many panels you want to produce
no_of_panels = 2

# Set the hole spacing on the decoder panel in mm
hole_x_spacing = 3.0
hole_y_spacing = 3.0

# Set the margin around each hole
hole_margin = 0.5

# Set the thickness of each panel in mm
height = 2.0

import FreeCAD as App
import FreeCADGui as Gui
import Part
import random

class SquareText():

    def __init__(self):
        print("SquareText created")

    font_5x3 = (
        (0, 0),         # 32 - 'Space'
        (23,),          # 33 - '!'
        (3, 0, 3),      # 34 - '"'
        (31, 10, 31),   # 35 - '#'
        (22, 31, 13),   # 36 - '$'
        (9, 4, 18),     # 37 - '%'
        (10, 21, 26),   # 38 - '&'
        (3,),           # 39
        (14, 17),       # 40 - '('
        (17, 14),       # 41 - ')'
        (10, 4, 10),    # 42 - '*'
        (4, 14, 4),     # 43 - '+'
        (16, 8),        # 44 - ','
        (4, 4, 4),      # 45 - '-'
        (16,),          # 46 - '.'
        (8, 4, 2),      # 47 - '/'
        (31, 17, 31),   # 48 - '0'
        (0, 31),        # 49 - '1'
        (29, 21, 23),   # 50 - '2'
        (17, 21, 31),   # 51 - '3'
        (7, 4, 31),     # 52 - '4'
        (23, 21, 29),   # 53 - '5'
        (31, 21, 29),   # 54 - '6'
        (1, 1, 31),     # 55 - '7'
        (31, 21, 31),   # 56 - '8'
        (23, 21, 31),   # 57 - '9'
        (10,),          # 58 - ':'
        (16, 10),       # 59 - ';'
        (4, 10, 17),    # 60 - '<'
        (10, 10, 10),   # 61 - '='
        (17, 10, 4),    # 62 - '>'
        (1, 21, 3),     # 63 - '?'
        (14, 21, 22),   # 64 - '@'
        (30, 5, 30),    # 65 - 'A'
        (31, 21, 10),   # 66 - 'B'
        (14, 17, 17),   # 67 - 'C'
        (31, 17, 14),   # 68 - 'D'
        (31, 21, 17),   # 69 - 'E'
        (31, 5, 1),     # 70 - 'F'
        (14, 17, 29),   # 71 - 'G'
        (31, 4, 31),    # 72 - 'H'
        (17, 31, 17),   # 73 - 'I'
        (8, 16, 15),    # 74 - 'J'
        (31, 4, 27),    # 75 - 'K'
        (31, 16, 16),   # 76 - 'L'
        (31, 2, 31),    # 77 - 'M'
        (31, 14, 31),   # 78 - 'N'
        (14, 17, 14),   # 79 - 'O'
        (31, 5, 2),     # 80 - 'P'
        (14, 25, 30),   # 81 - 'Q'
        (31, 5, 26),    # 82 - 'R'
        (18, 21, 9),    # 83 - 'S'
        (1, 31, 1),     # 84 - 'T'
        (31, 16, 31),   # 85 - 'U'
        (7, 24, 7),     # 86 - 'V'
        (15, 28, 15),   # 87 - 'W'
        (27, 4, 27),    # 88 - 'X'
        (3, 28, 3),     # 89 - 'Y'
        (25, 21, 19),   # 90 - 'Z'
        (31, 17),       # 91 - '['
        (2, 4, 8),      # 92 - '\'
        (17, 31),       # 93 - ']'
        (2, 1, 2),      # 94 - '^'
        (16, 16, 16),   # 95 - '_'
        (1, 2),         # 96 - '`'
        (12, 18, 28),   # 97 - 'a'
        (31, 18, 12),   # 98 - 'b'
        (12, 18, 18),   # 99 - 'c'
        (12, 18, 31),   # 100 - 'd'
        (12, 26, 20),   # 101 - 'e'
        (4, 31, 5),     # 102 - 'f'
        (20, 26, 12),   # 103 - 'g'
        (31, 2, 28),    # 104 - 'h'
        (29,),          # 105 - 'i'
        (16, 13),       # 106 - 'j'
        (31, 8, 20),    # 107 - 'k'
        (31,),          # 108 - 'l'
        (30, 6, 30),    # 109 - 'm'
        (30, 2, 28),    # 110 - 'n'
        (12, 18, 12),   # 111 - 'o'
        (30, 10, 4),    # 112 - 'p'
        (4, 10, 30),    # 113 - 'q'
        (30, 4),        # 114 - 'r'
        (20, 30, 10),   # 115 - 's'
        (4, 30, 4),     # 116 - 't'
        (14, 16, 30),   # 117 - 'u'
        (14, 16, 14),   # 118 - 'v'
        (14, 24, 14),   # 119 - 'w'
        (18, 12, 18),   # 120 - 'x'
        (22, 24, 14),   # 121 - 'y'
        (26, 30, 22),   # 122 - 'z'
        (4, 27, 17),    # 123 - '{'
        (27,),          # 124 - '|'
        (17, 27, 4),    # 125 - '}'
        (6, 2, 3),      # 126 - '~'
        (31, 31, 31) # 127 - 'Full Block'
    )

    def get_char_design(self,ch):
        ch_offset = ord(ch) - ord(' ')
        if ch_offset<0 or ch_offset>len(self.font_5x3):
            return None
        return self.font_5x3[ch_offset]

    def text_dimensions_in_dots(self,text):

        print("Measuring:",text)

        width=0
        height=6

        widths = []

        if text == '':
            return (width,height)

        ch_pos = 0

        while(True):
            if ch_pos == len(text):
	            widths.append(width)
	            break

            ch = text[ch_pos]

            if ch=='\n':
                print("newline")
                height=height+6
                widths.append(width)
                width=0
            else:

                print(ch)

                char_design = self.get_char_design(ch)

                if char_design != None:
                    width = width + len(char_design) + 1
    
            ch_pos = ch_pos + 1

        return (max(widths), height)
		
    def draw_text(self,text="Hello World", x=0,y=0,z=0,width=10,depth=10,height=10,margin=0):

        print("Building:",text)

        result = None

        if text == '':
            return

        ch_pos = 0

        while ch_pos < len(text):

            ch = text[ch_pos]

            print(ch)

            char_design = self.get_char_design(ch)

            if char_design == None:
                return

            char_design_length = len(char_design)
            column = 0

            while column < char_design_length:
                # display the character raster
                font_column =char_design[column]
                bit = 1
                yp = y + (5*depth)
                while(bit<32):
                    if font_column & bit:
                        pos = App.Vector(x+margin,yp+margin,z)
                        dot = Part.makeBox(width-(2*margin),depth-(2*margin),height,pos)
                        if result==None:
                            result = dot
                        else:  
                            result=result.fuse(dot)

                    # move on to the next bit in the column
                    bit = bit + bit
                    # move onto the next pixel to draw
                    yp=yp-depth
                x = x + width
                column = column + 1

            # reached the end of displaying a character - move to the next one
            x = x + width
            ch_pos = ch_pos + 1
        return result

    def secret_message(self,text="Hello World", x=0,y=0,z=0,width=10,depth=10,height=10,margin=0,no_of_panels=2):

        print("Building:",text)

        dot_width,dot_height=self.text_dimensions_in_dots(text)

        y=y+((dot_height-6)*depth)

        if text == '':
            return None

        results = []

        for p in range(no_of_panels):
	        results.append(None)

        ch_pos = 0

        while ch_pos < len(text):

            ch = text[ch_pos]

            if ch == "\n":
                while x < dot_width*width:
                    for ystep in range(1,5):
                        block_panel_no = random.randint(0,no_of_panels-1)
                        pos = App.Vector(x+margin,y+(ystep*depth)+margin,z)
                        dot = Part.makeBox(width-(2*margin),depth-(2*margin),height,pos)
                        for p in range(no_of_panels):
                          if p!=block_panel_no:
                            if results[p]==None:
                                results[p]=dot
                            else:       
                                results[p]=results[p].fuse(dot)
                    x=x+width
                x=0
                y=y-(6*depth)
                ch_pos = ch_pos+1
                continue

            print(ch)

            char_design = self.get_char_design(ch)

            if char_design == None:
                return

            char_design_length = len(char_design)
            column = 0

            while column < char_design_length:
                # display the character raster
                font_column =char_design[column]
                bit = 1
                yp = y + (5*depth)
                while(bit<32):
                    pos = App.Vector(x+margin,yp+margin,z)
                    dot = Part.makeBox(width-(2*margin),depth-(2*margin),height,pos)
                    if font_column & bit:
                        for p in range(no_of_panels):
                            if results[p]==None:
                                results[p]=dot
                            else:       
                                results[p]=results[p].fuse(dot)
                    else:
                        # make holes in some of the panels to hide the text
                        # need to make sure that one of them is not a hole
                        block_panel_no = random.randint(0,no_of_panels-1)
                        for p in range(no_of_panels):
                          if p!=block_panel_no:
                            if results[p]==None:
                                results[p]=dot
                            else:       
                                results[p]=results[p].fuse(dot)

                    # move on to the next bit in the column
                    bit = bit + bit
                    # move onto the next pixel to draw
                    yp=yp-depth
                x = x + width
                column = column + 1

            # reached the end of displaying a character - move to the next one
            for ystep in range(1,5):
                block_panel_no = random.randint(0,no_of_panels-1)
                pos = App.Vector(x+margin,y+(ystep*depth)+margin,z)
                dot = Part.makeBox(width-(2*margin),depth-(2*margin),height,pos)
                for p in range(no_of_panels):
                  if p!=block_panel_no:
                    if results[p]==None:
                        results[p]=dot
                    else:       
                        results[p]=results[p].fuse(dot)
            x = x + width
            ch_pos = ch_pos + 1
        while x < dot_width*width:
            for ystep in range(1,5):
                block_panel_no = random.randint(0,no_of_panels-1)
                pos = App.Vector(x+margin,y+(ystep*depth)+margin,z)
                dot = Part.makeBox(width-(2*margin),depth-(2*margin),height,pos)
                for p in range(no_of_panels):
                  if p!=block_panel_no:
                    if results[p]==None:
                        results[p]=dot
                    else:       
                        results[p]=results[p].fuse(dot)
            x=x+width
        return results

doc = App.ActiveDocument or App.newDocument("Secret Encoder")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

text=SquareText()

text_width_in_dots,text_height_in_dots=text.text_dimensions_in_dots(secret_text)

print("Dot width:",text_width_in_dots,"Dot height:",text_height_in_dots)

width=text_width_in_dots*hole_x_spacing
depth=text_height_in_dots*hole_y_spacing

hole_width = hole_x_spacing-(2*hole_margin)
hole_depth = hole_y_spacing-(2*hole_margin)

secret_messages=text.secret_message(text=secret_text,x=0,y=0,z=0,width=hole_x_spacing,depth=hole_y_spacing,height=height,margin=hole_margin,no_of_panels=no_of_panels)

colours = [(0.0,.5,0.0),(.5,0.0,.5),(.5,0.0,0.0),(0.0,0.0,.5)]

for p in range(no_of_panels):
    panel = Part.makeBox(width, depth, height)
    panel = panel.cut(secret_messages[p])
    panel.translate(App.Vector(width+5, p*(depth+5),0))
    frame_obj = doc.addObject("Part::Feature", "Card"+str(p))
    frame_obj.Shape = panel
    frame_obj.ViewObject.ShapeColor = colours[p]


    panel = Part.makeBox(width, depth, height)
    panel = panel.cut(secret_messages[p])
    panel.translate(App.Vector(0,0,height*p))
    frame_obj = doc.addObject("Part::Feature", "Result"+str(p))
    frame_obj.Shape = panel
    frame_obj.ViewObject.ShapeColor = colours[p]

Gui.ActiveDocument.ActiveView.fitAll()


