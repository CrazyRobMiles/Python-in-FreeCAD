# Line Scan from Image
![Freecad showing a mosaic of an old camera as an image made up of four differently coloured regions](/Examples/24%20LineScan%20from%20image/LineScanFromImage.png)


This program uses the Pillow library which is already installed within FreeCAD. The program produces several objects which should be combined and printed in the same way as the [tag with embedded text](/Examples/19%20Tag%20with%20embedded%20text/TagWithEmbeddedText.md) to produce a mosaic.

## Control Values

These are the values that you can change to control the result:

* **INPUT_IMAGE** - the path to the image to be processed. This can be a jpeg or a png file of any size. The image will be downsampled to the specified grid dimensions. It is a good idea to pre-process your images with a view to being made into a mosaic. Remove distracting backgrounds and flatten the range of colours in the image. 
* **OUTPUT_FOLDER** - the path to the folder where the output files are to be written. 
* **PICTURE_WIDTH_MM** and **PICTURE_DEPTH_MM** - the width and depth (height) of the output.
* **GRID_WIDTH** and **GRID_DEPTH** - the resolution in dots of the output. The size of each dot will be calculated by dividing the picture size by the size of the grid. Around 128 works well, although with certain subjects you can get good results with smaller values. 
* **PIXEL_MARGIN_MM** - this is the size of the margin around each line. This is calculated as 0.2 times the dot width. If you want thinner lines increase the value 0.2. If you want larger lines with a smaller margin, decrease the value 0.2
* **NUM_COLOURS** - the number of different colours in your image. Set this to the match the number of filaments you can print. 
* **THICKNESS_MM** - the height of each pixel
* **BASE_THICKNESS_MM** - the thickness of the base layer. Set this to 0 if you don't want a base. 
* **BORDER_MM** - the size of the border around the print
* **USE_ASPECT_RATIO** - preserve the aspect ratio of the original image (best left True)
* **USE_DITHER** - dither the colours to create shades in the output - only useable if you have high resolution (best left False)

```python

import os

import FreeCAD as App
import Part
import Mesh
import FreeCADGui as Gui

from PIL import Image


if App.ActiveDocument is not None:
    doc = App.ActiveDocument
    firstRun = False
else:
    print("First Run - creating document")
    doc = App.newDocument("DotImage")
    firstRun = True

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

INPUT_IMAGE = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-04-02 FreeCAD Python part 5\images\camera.jpg"
OUTPUT_FOLDER = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-04-02 FreeCAD Python part 5\stl"

PICTURE_WIDTH_MM = 125
PICTURE_DEPTH_MM = 125

GRID_WIDTH = 128
GRID_DEPTH = 128
NUM_COLOURS = 4

PIXEL_SIZE_MM = PICTURE_WIDTH_MM / GRID_WIDTH
PIXEL_MARGIN = PIXEL_SIZE_MM * 0.2
PIXEL_WRITE_SIZE = PIXEL_SIZE_MM - (PIXEL_MARGIN * 2)

THICKNESS_MM = 1.2
BASE_THICKNESS_MM = 0.8
BORDER_MM = 0.0

USE_ASPECT_RATIO = True
USE_DITHER = False

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_object(doc, obj_type, name):
    obj = doc.getObject(name)
    if obj is None:
        obj = doc.addObject(obj_type, name)
    return obj


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])


def make_box(x, y, z, w, h, d):
    return Part.makeBox(w, h, d, App.Vector(x, y, z))


def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def quantize_image(image, num_colours=4, use_dither=False):
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    q = image.convert("RGB").quantize(
        colors=num_colours,
        method=Image.MEDIANCUT,
        dither=dither_mode
    )
    rgb = q.convert("RGB")

    palette = rgb.getcolors(maxcolors=256)
    if palette is None:
        raise RuntimeError("Too many colours found after quantization.")

    colours = [entry[1] for entry in palette]

    # Sort darkest -> lightest, as in MosaicFromImage.py
    colours = sorted(colours, key=luminance)

    return rgb, colours


def resize_image(image, target_w, target_h, keep_aspect=True):
    if keep_aspect:
        src_w, src_h = image.size
        aspect = float(src_h) / float(src_w)
        target_h = max(1, int(round(target_w * aspect)))
    return image.resize((target_w, target_h), Image.Resampling.LANCZOS)


def build_colour_dot_shapes(img, colours, dot_size, margin_size, thickness, border=0.0, z0=0.0):
    """
    Build one compound shape per colour in a single pass through the image.

    Adjacent same-colour pixels on each row are merged into horizontal strips
    of dots. The strip width preserves the dot gaps, so this does not create
    solid mosaic strips; it creates strips whose ends align with the outer
    edges of the first and last dots in the run.

    No Boolean fusion is performed because the generated solids do not overlap.
    """
    width, depth = img.size
    pixels = img.load()

    pitch = dot_size + (2 * margin_size)

    solids_by_colour = {colour: [] for colour in colours}
    colour_set = set(colours)

    for y in range(depth):
        x = 0
        while x < width:
            run_colour = pixels[x, y]
            start_x = x

            while x < width and pixels[x, y] == run_colour:
                x += 1

            run_len = x - start_x

            if run_colour not in colour_set:
                continue

            world_x = border + margin_size + (start_x * pitch)
            world_y = border + margin_size + ((depth - 1 - y) * pitch)

            strip_width = ((run_len - 1) * pitch) + dot_size

            solid = make_box(
                world_x,
                world_y,
                z0,
                strip_width,
                dot_size,
                thickness
            )
            solids_by_colour[run_colour].append(solid)

    colour_shapes = {}
    for colour in colours:
        solids = solids_by_colour[colour]
        colour_shapes[colour] = Part.makeCompound(solids) if solids else None

    return colour_shapes


def build_base_plate(img_w, img_h, pixel_pitch, base_thickness, border=0.0):
    total_w = img_w * pixel_pitch + 2 * border
    total_h = img_h * pixel_pitch + 2 * border
    return make_box(0, 0, 0, total_w, total_h, base_thickness)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def create_dot_stls():
    ensure_folder(OUTPUT_FOLDER)

    img = Image.open(INPUT_IMAGE).convert("RGB")
    img = resize_image(img, GRID_WIDTH, GRID_DEPTH, keep_aspect=USE_ASPECT_RATIO)

    qimg, colours = quantize_image(img, NUM_COLOURS, use_dither=USE_DITHER)

    width, depth = qimg.size
    print("Resized image:", width, "x", depth)
    print("Quantized colours (darkest to lightest):")
    for i, c in enumerate(colours):
        print(" ", i, c, rgb_to_hex(c))

    z0 = BASE_THICKNESS_MM if BASE_THICKNESS_MM > 0 else 0.0

    if BASE_THICKNESS_MM > 0:
        base = build_base_plate(width, depth, PIXEL_SIZE_MM, BASE_THICKNESS_MM, BORDER_MM)
        base_file = os.path.join(OUTPUT_FOLDER, "base_plate.stl")

        base_obj = get_object(doc, "Part::Feature", "Base")
        base_obj.Shape = base
        base_obj.ViewObject.ShapeColor = (0.10, 0.10, 0.10)

        Mesh.export([base_obj], base_file)
        print("Wrote:", base_file)

    colour_shapes = build_colour_dot_shapes(
        qimg,
        colours,
        PIXEL_WRITE_SIZE,
        PIXEL_MARGIN,
        THICKNESS_MM,
        border=BORDER_MM,
        z0=z0
    )

    preview_file = os.path.join(OUTPUT_FOLDER, "posterized_preview.png")
    preview_img = qimg.resize((width * 20, depth * 20), Image.Resampling.NEAREST)
    preview_img.save(preview_file)
    print("Wrote:", preview_file)

    for i, colour in enumerate(colours):
        shape = colour_shapes[colour]
        if shape is None:
            continue

        hex_name = rgb_to_hex(colour).replace("#", "")
        stl_name = f"colour_{i + 1}_{hex_name}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_name)
        feature_name = "C" + hex_name

        layer_obj = get_object(doc, "Part::Feature", feature_name)
        layer_obj.Shape = shape
        layer_obj.ViewObject.ShapeColor = (
            colour[0] / 255.0,
            colour[1] / 255.0,
            colour[2] / 255.0
        )

        Mesh.export([layer_obj], stl_path)
        print("Wrote:", stl_path)

    doc.recompute()


create_dot_stls()

if firstRun:
    Gui.ActiveDocument.ActiveView.fitAll()

print("Done.")

```

[Back](/README.md)