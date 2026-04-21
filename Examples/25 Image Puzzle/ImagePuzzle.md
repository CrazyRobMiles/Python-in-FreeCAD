# Image Puzzle
![Freecad showing a mosaic of daffodils which have been split into tiles and displayed inside a frame](/Examples/25%20Image%20Puzzle/ImagePuzzle.png)


This program uses the Pillow library which is already installed within FreeCAD. The program produces several objects which should be combined and printed in the same way as the [tag with embedded text](/Examples/19%20Tag%20with%20embedded%20text/TagWithEmbeddedText.md) to produce a mosaic.

## Preparing the Image

![Four colour image of daffodils](/Examples/25%20Image%20Puzzle/procdaff.jpg)

You get the best results for the puzzle (and for mosaics too) by pre-processing your image before it is converted into a mosaic. The above daffodil image had its contrast enhanced and was converted into four colours using Photoshop.

## Control Values

These are the values that you can change to control the result:

* **INPUT_IMAGE** - the path to the image to be processed. This can be a jpeg or a png file of any size. The image will be downsampled to the specified grid dimensions. It is a good idea to pre-process your images with a view to being made into a mosaic. Remove distracting backgrounds and flatten the range of colours in the image. 
* **OUTPUT_FOLDER** - the path to the folder where the output files are to be written. 

* **ENABLE_PANELS** - set to **True** to enable panel output

* **PANELS_X** - number of panels across and down the finished picture. Each panel has the same aspect ratio as the picture. 

* **PANEL_PIXEL_WIDTH** - the width of one panel in mosaic pixels

* **PANEL_GAP_MM** - gap inserted between neighbouring panels in the print layout

## Tray settings

* **TRAY_CLEARANCE_XY_MM** - clearance around the tray
* **TRAY_CLEARANCE_Z_MM** - excess height so that the tray border is higher than the tiles
* **TRAY_FLOOR_THICKNESS_MM** - thickness of the tray floor
* **TRAY_FRAME_WIDTH_MM** - width of the frame
* **TRAY_BEVEL_INSET_MM** - inset of the bevelled element in the tray surround
* ** TRAY_MIN_WALL_HEIGHT_MM = 4.0



* **PICTURE_WIDTH_MM** and **PICTURE_DEPTH_MM** - the width and depth (height) of the output.
* **GRID_WIDTH** and **GRID_DEPTH** - the resolution in dots of the output. The size of each dot will be calculated by dividing the picture size by the size of the grid. Around 128 works well, although with certain subjects you can get good results with smaller values. 
* **NUM_COLOURS** - the number of different colours in your image. Set this to the match the number of filaments you can print. 
* **THICKNESS_MM** - the height of each pixel
* **BASE_THICKNESS_MM** - the thickness of the base layer. Set this to 0 if you don't want a base. 
* **BORDER_MM** - The size of the border around the print

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
    doc = App.newDocument("PanelMosaic")
    firstRun = True


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

INPUT_IMAGE = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-04-02 FreeCAD Python part 5\images\procdaff.jpg"
OUTPUT_FOLDER = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-04-02 FreeCAD Python part 5\stl"

# Final physical width of the finished picture
PICTURE_WIDTH_MM = 128.0

# Thicknesses
THICKNESS_MM = 1.2
BASE_THICKNESS_MM = 0.8
BORDER_MM = 0.0

# Colour reduction
NUM_COLOURS = 4
USE_DITHER = False

# ------------------------------------------------------------
# Panel-aware mosaic settings
# ------------------------------------------------------------

ENABLE_PANELS = True

# Number of panels across the finished picture
PANELS_X = 4

# Width of one panel in mosaic pixels
PANEL_PIXEL_WIDTH = 32

# Gap inserted between neighbouring panels in the print layout
PANEL_GAP_MM = 1.0

# ------------------------------------------------------------
# Tray settings
# ------------------------------------------------------------

TRAY_CLEARANCE_XY_MM = 1.0
TRAY_CLEARANCE_Z_MM = 0.8
TRAY_FLOOR_THICKNESS_MM = 1.2
TRAY_FRAME_WIDTH_MM = 8.0
TRAY_BEVEL_INSET_MM = 2.0
TRAY_MIN_WALL_HEIGHT_MM = 4.0


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)



def get_object(doc, obj_type, name):
    obj = App.ActiveDocument.getObject(name)
    if obj is None:
        obj = doc.addObject(obj_type, name)
    return obj



def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])



def make_box(x, y, z, w, h, d):
    return Part.makeBox(w, h, d, App.Vector(x, y, z))



def make_compound(shapes):
    shapes = [s for s in shapes if s is not None]
    if not shapes:
        return None
    return Part.makeCompound(shapes)



def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b



def quantize_image(image, num_colours=4, use_dither=False):
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    q = image.convert("RGB").quantize(
        colors=num_colours,
        method=Image.MEDIANCUT,
        dither=dither_mode,
    )
    rgb = q.convert("RGB")
    palette = rgb.getcolors(maxcolors=256)
    if palette is None:
        raise RuntimeError("Too many colours found after quantization.")

    colours = [entry[1] for entry in palette]
    colours = sorted(colours, key=luminance)  # darkest first for easier filament mapping
    return rgb, colours



def resize_image_exact(image, target_w, target_h):
    return image.resize((target_w, target_h), Image.Resampling.LANCZOS)


# ------------------------------------------------------------
# Panel geometry
# ------------------------------------------------------------


def compute_panel_pixel_size_from_aspect(src_w, src_h, panel_pixel_width):
    """
    Compute a panel height in pixels that matches the source image aspect ratio
    as closely as possible while staying on whole-pixel boundaries.
    """
    if panel_pixel_width <= 0:
        raise RuntimeError("PANEL_PIXEL_WIDTH must be > 0")

    aspect = float(src_h) / float(src_w)
    panel_pixel_height = max(1, int(round(panel_pixel_width * aspect)))
    return panel_pixel_width, panel_pixel_height



def compute_resized_grid_for_panels(src_w, src_h, panels_x, panel_pixel_width):
    """
    Choose a resized image size that:
    - approximately matches the source image aspect ratio
    - is exactly divisible into whole panels
    """
    if panels_x <= 0:
        raise RuntimeError("PANELS_X must be > 0")

    panel_w_px, panel_h_px = compute_panel_pixel_size_from_aspect(
        src_w,
        src_h,
        panel_pixel_width,
    )

    image_w_px = panels_x * panel_w_px

    source_aspect = float(src_h) / float(src_w)
    estimated_image_h = image_w_px * source_aspect

    panels_y = max(1, int(round(estimated_image_h / panel_h_px)))
    image_h_px = panels_y * panel_h_px

    return {
        "panel_pixel_width": panel_w_px,
        "panel_pixel_height": panel_h_px,
        "panels_x": panels_x,
        "panels_y": panels_y,
        "image_width": image_w_px,
        "image_height": image_h_px,
    }



def compute_panel_layout(img_w, img_h, gap_mm, panel_pixel_width, panel_pixel_height):
    """
    Compute the panel rectangles in image-pixel coordinates and the extra
    translations needed to separate them on the print bed.
    """
    if panel_pixel_width <= 0 or panel_pixel_height <= 0:
        raise RuntimeError("Panel pixel dimensions must be > 0")

    if img_w % panel_pixel_width != 0:
        raise RuntimeError(
            f"Image width {img_w} is not divisible by panel width {panel_pixel_width}"
        )

    if img_h % panel_pixel_height != 0:
        raise RuntimeError(
            f"Image height {img_h} is not divisible by panel height {panel_pixel_height}"
        )

    panels_x = img_w // panel_pixel_width
    panels_y = img_h // panel_pixel_height

    panels = []

    for row_top in range(panels_y):
        row_from_bottom = panels_y - 1 - row_top
        for col in range(panels_x):
            x0 = col * panel_pixel_width
            x1 = x0 + panel_pixel_width

            y0 = row_top * panel_pixel_height
            y1 = y0 + panel_pixel_height

            tx = col * gap_mm
            ty = row_from_bottom * gap_mm

            panels.append({
                "col": col,
                "row_top": row_top,
                "x0": x0,
                "x1": x1,
                "y0": y0,
                "y1": y1,
                "tx": tx,
                "ty": ty,
            })

    return {
        "panel_pixel_width": panel_pixel_width,
        "panel_pixel_height": panel_pixel_height,
        "panels_x": panels_x,
        "panels_y": panels_y,
        "panels": panels,
    }


# ------------------------------------------------------------
# Shape builders
# ------------------------------------------------------------


def build_base_plate(img_w, img_h, pixel_size, base_thickness, border=0.0):
    total_w = img_w * pixel_size + 2 * border
    total_h = img_h * pixel_size + 2 * border
    return make_box(0, 0, 0, total_w, total_h, base_thickness)



def build_panel_base_plates(panel_layout, pixel_size, base_thickness, border=0.0):
    """
    Build a set of separate base panels as a compound. The gaps remain because
    the panels do not touch.
    """
    shapes = []
    full_pixel_height = panel_layout["panels_y"] * panel_layout["panel_pixel_height"]

    for p in panel_layout["panels"]:
        panel_w_px = p["x1"] - p["x0"]
        panel_h_px = p["y1"] - p["y0"]

        world_x = border + p["x0"] * pixel_size + p["tx"]
        world_y = border + (full_pixel_height - p["y1"]) * pixel_size + p["ty"]

        shape = make_box(
            world_x,
            world_y,
            0.0,
            panel_w_px * pixel_size,
            panel_h_px * pixel_size,
            base_thickness,
        )
        shapes.append(shape)

    return make_compound(shapes)



def build_colour_shapes_single_pass(img, colours, pixel_size, thickness, border=0.0, z0=0.0):
    """
    Non-panel version. Scan the image once, merge horizontal runs, and return
    one compound per colour.
    """
    width, depth = img.size
    pixels = img.load()

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

            world_x = border + start_x * pixel_size
            world_y = border + (depth - 1 - y) * pixel_size

            solid = make_box(
                world_x,
                world_y,
                z0,
                run_len * pixel_size,
                pixel_size,
                thickness,
            )
            solids_by_colour[run_colour].append(solid)

    return {colour: make_compound(solids_by_colour[colour]) for colour in colours}



def build_panel_colour_shapes_single_pass(img, colours, pixel_size, thickness, panel_layout, border=0.0, z0=0.0):
    """
    Panel-aware version using the faster algorithm.
    Scan the mosaic once, split runs at panel boundaries, and append each strip
    directly to the correct colour layer. Shapes are grouped as compounds.
    """
    img_w, img_h = img.size
    pixels = img.load()

    panel_w = panel_layout["panel_pixel_width"]
    panel_h = panel_layout["panel_pixel_height"]
    panels_y = panel_layout["panels_y"]
    gap_mm = PANEL_GAP_MM

    solids_by_colour = {colour: [] for colour in colours}
    colour_set = set(colours)

    for y in range(img_h):
        row_top = y // panel_h
        row_from_bottom = panels_y - 1 - row_top
        ty = row_from_bottom * gap_mm

        x = 0
        while x < img_w:
            col = x // panel_w
            panel_x1 = min(img_w, (col + 1) * panel_w)
            tx = col * gap_mm

            run_colour = pixels[x, y]
            start_x = x

            while x < panel_x1 and pixels[x, y] == run_colour:
                x += 1

            run_len = x - start_x

            if run_colour not in colour_set:
                continue

            world_x = border + start_x * pixel_size + tx
            world_y = border + (img_h - 1 - y) * pixel_size + ty

            solid = make_box(
                world_x,
                world_y,
                z0,
                run_len * pixel_size,
                pixel_size,
                thickness,
            )
            solids_by_colour[run_colour].append(solid)

    return {colour: make_compound(solids_by_colour[colour]) for colour in colours}


# ------------------------------------------------------------
# Preview image helpers
# ------------------------------------------------------------


def save_preview_image(qimg, path, scale=20):
    preview = qimg.resize((qimg.size[0] * scale, qimg.size[1] * scale), Image.Resampling.NEAREST)
    preview.save(path)



def save_panel_preview(qimg, panel_layout, preview_path, scale=20):
    """
    Save a posterized preview with panel boundaries drawn in black.
    """
    img = qimg.copy()
    pixels = img.load()

    for p in panel_layout["panels"]:
        x0, x1 = p["x0"], p["x1"]
        y0, y1 = p["y0"], p["y1"]

        for x in range(x0, x1):
            pixels[x, y0] = (0, 0, 0)
            pixels[x, y1 - 1] = (0, 0, 0)

        for y in range(y0, y1):
            pixels[x0, y] = (0, 0, 0)
            pixels[x1 - 1, y] = (0, 0, 0)

    img = img.resize((img.size[0] * scale, img.size[1] * scale), Image.Resampling.NEAREST)
    img.save(preview_path)


# ------------------------------------------------------------
# Tray builders
# ------------------------------------------------------------


def make_picture_frame_tray(
    inner_width,
    inner_height,
    piece_stack_thickness,
    clearance_xy=1.0,
    clearance_z=0.8,
    floor_thickness=1.2,
    wall_height=4.0,
    frame_width=8.0,
    bevel_inset=2.0,
    z0=0.0,
):
    """
    Create a shallow tray that looks like a picture frame.
    """
    cavity_w = inner_width + clearance_xy
    cavity_h = inner_height + clearance_xy

    # Ensure the pieces fit below the frame rim.
    usable_wall_height = max(wall_height, piece_stack_thickness + clearance_z)
    total_height = floor_thickness + usable_wall_height

    # The visible top opening is larger than the bottom cavity so the bevel
    # flares outward instead of inward.
    top_opening_w = cavity_w + 2.0 * bevel_inset
    top_opening_h = cavity_h + 2.0 * bevel_inset

    outer_w = top_opening_w + 2.0 * frame_width
    outer_h = top_opening_h + 2.0 * frame_width

    outer = Part.makeBox(
        outer_w,
        outer_h,
        total_height,
        App.Vector(0, 0, z0),
    )

    x_bottom = frame_width + bevel_inset
    y_bottom = frame_width + bevel_inset
    z_bottom = z0 + floor_thickness

    x_top = frame_width
    y_top = frame_width
    z_top = z0 + total_height

    p0 = App.Vector(x_bottom, y_bottom, z_bottom)
    p1 = App.Vector(x_bottom + cavity_w, y_bottom, z_bottom)
    p2 = App.Vector(x_bottom + cavity_w, y_bottom + cavity_h, z_bottom)
    p3 = App.Vector(x_bottom, y_bottom + cavity_h, z_bottom)
    bottom_wire = Part.makePolygon([p0, p1, p2, p3, p0])

    q0 = App.Vector(x_top, y_top, z_top)
    q1 = App.Vector(x_top + top_opening_w, y_top, z_top)
    q2 = App.Vector(x_top + top_opening_w, y_top + top_opening_h, z_top)
    q3 = App.Vector(x_top, y_top + top_opening_h, z_top)
    top_wire = Part.makePolygon([q0, q1, q2, q3, q0])

    cavity_solid = Part.makeLoft([bottom_wire, top_wire], True)
    tray = outer.cut(cavity_solid)
    
    tray.translate(App.Vector(-x_bottom,-y_bottom,0))
    
    return tray



def create_puzzle_tray(
    mosaic_width_px,
    mosaic_height_px,
    pixel_size_mm,
    base_thickness_mm,
    layer_thickness_mm,
    doc,
    object_name="PuzzleTray",
):
    assembled_width_mm = mosaic_width_px * pixel_size_mm
    assembled_height_mm = mosaic_height_px * pixel_size_mm

    total_piece_thickness = base_thickness_mm + layer_thickness_mm

    tray = make_picture_frame_tray(
        inner_width=assembled_width_mm,
        inner_height=assembled_height_mm,
        piece_stack_thickness=total_piece_thickness,
        clearance_xy=TRAY_CLEARANCE_XY_MM,
        clearance_z=TRAY_CLEARANCE_Z_MM,
        floor_thickness=TRAY_FLOOR_THICKNESS_MM,
        wall_height=TRAY_MIN_WALL_HEIGHT_MM,
        frame_width=TRAY_FRAME_WIDTH_MM,
        bevel_inset=TRAY_BEVEL_INSET_MM,
        z0=0.0,
    )

    tray_obj = get_object(doc, "Part::Feature", object_name)
    tray_obj.Shape = tray

    try:
        tray_obj.ViewObject.ShapeColor = (0.65, 0.55, 0.40)
    except Exception:
        pass

    return tray_obj


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def create_mosaic_stls():
    ensure_folder(OUTPUT_FOLDER)

    src_img = Image.open(INPUT_IMAGE).convert("RGB")
    src_w, src_h = src_img.size

    resize_info = compute_resized_grid_for_panels(
        src_w,
        src_h,
        PANELS_X,
        PANEL_PIXEL_WIDTH,
    )

    grid_width = resize_info["image_width"]
    grid_height = resize_info["image_height"]
    panel_pixel_width = resize_info["panel_pixel_width"]
    panel_pixel_height = resize_info["panel_pixel_height"]
    panels_x = resize_info["panels_x"]
    panels_y = resize_info["panels_y"]

    print("Source image:", src_w, "x", src_h)
    print("Resized mosaic:", grid_width, "x", grid_height)
    print("Panel size:", panel_pixel_width, "x", panel_pixel_height, "pixels")
    print("Panel count:", panels_x, "x", panels_y)

    img = resize_image_exact(src_img, grid_width, grid_height)

    panel_layout = compute_panel_layout(
        grid_width,
        grid_height,
        PANEL_GAP_MM,
        panel_pixel_width,
        panel_pixel_height,
    )

    qimg, colours = quantize_image(img, NUM_COLOURS, use_dither=USE_DITHER)

    width, height = qimg.size
    pixel_size_mm = PICTURE_WIDTH_MM / float(width)

    print("Pixel size mm:", pixel_size_mm)
    print("Quantized colours (dark to light):")
    for i, c in enumerate(colours):
        print(" ", i + 1, c, rgb_to_hex(c), "brightness={:.1f}".format(luminance(c)))

    z0 = BASE_THICKNESS_MM if BASE_THICKNESS_MM > 0 else 0.0

    if BASE_THICKNESS_MM > 0:
        if ENABLE_PANELS:
            base = build_panel_base_plates(
                panel_layout,
                pixel_size_mm,
                BASE_THICKNESS_MM,
                BORDER_MM,
            )
        else:
            base = build_base_plate(width, height, pixel_size_mm, BASE_THICKNESS_MM, BORDER_MM)

        base_file = os.path.join(OUTPUT_FOLDER, "base_plate.stl")
        base_obj = get_object(doc, "Part::Feature", "Base")
        base_obj.Shape = base
        try:
            base_obj.ViewObject.ShapeColor = (0.10, 0.10, 0.10)
        except Exception:
            pass
        Mesh.export([base_obj], base_file)
        print("Wrote:", base_file)

    tray_obj = create_puzzle_tray(
        mosaic_width_px=width,
        mosaic_height_px=height,
        pixel_size_mm=pixel_size_mm,
        base_thickness_mm=BASE_THICKNESS_MM,
        layer_thickness_mm=THICKNESS_MM,
        doc=doc,
        object_name="PuzzleTray",
    )

    tray_file = os.path.join(OUTPUT_FOLDER, "puzzle_tray.stl")
    Mesh.export([tray_obj], tray_file)
    print("Wrote:", tray_file)

    if ENABLE_PANELS:
        colour_shapes = build_panel_colour_shapes_single_pass(
            qimg,
            colours,
            pixel_size_mm,
            THICKNESS_MM,
            panel_layout,
            border=BORDER_MM,
            z0=z0,
        )
    else:
        colour_shapes = build_colour_shapes_single_pass(
            qimg,
            colours,
            pixel_size_mm,
            THICKNESS_MM,
            border=BORDER_MM,
            z0=z0,
        )

    preview_file = os.path.join(OUTPUT_FOLDER, "posterized_preview.png")
    save_preview_image(qimg, preview_file, scale=20)
    print("Wrote:", preview_file)

    panel_preview_file = os.path.join(OUTPUT_FOLDER, "posterized_preview_with_panels.png")
    save_panel_preview(qimg, panel_layout, panel_preview_file, scale=20)
    print("Wrote:", panel_preview_file)

    for i, colour in enumerate(colours):
        shape = colour_shapes[colour]
        if shape is None:
            continue

        hex_name = rgb_to_hex(colour).replace("#", "")
        stl_name = f"colour_{i+1}_{hex_name}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_name)

        feature_name = "C" + hex_name
        layer_obj = get_object(doc, "Part::Feature", feature_name)
        layer_obj.Shape = shape

        try:
            layer_obj.ViewObject.ShapeColor = (
                colour[0] / 255.0,
                colour[1] / 255.0,
                colour[2] / 255.0,
            )
        except Exception:
            pass

        Mesh.export([layer_obj], stl_path)
        print("Wrote:", stl_path)


create_mosaic_stls()

doc.recompute()

if firstRun:
    Gui.ActiveDocument.ActiveView.fitAll()

print("Done.")
```

[Back](/README.md)