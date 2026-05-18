# Jigsaw Puzzle
![FreeCAD showing a mosaic image cut into interlocking jigsaw pieces](/Examples/28%20Jigsaw%20Puzzle/jigsawpuzzle.png)

This program takes an image, converts it into a colour mosaic, and then cuts it into interlocking jigsaw pieces. It produces one STL file per filament colour. Each file contains all the pieces for that colour, already cut apart, so you print each colour separately and assemble the puzzle.

The jigsaw cuts are made using `makePipeShell`: a curved tab profile is swept along each cut line to create a solid cutter, which is then subtracted from the base plate and all colour layers simultaneously.

## Preparing the Image

You get the best results by pre-processing your image before conversion. Reduce the number of colours and increase contrast so the mosaic reads clearly at low resolution.

## Control Values

### Mosaic settings

* **INPUT_IMAGE** — path to the source image (JPEG or PNG)
* **OUTPUT_FOLDER** — folder where the STL files and preview image are written
* **GRID_WIDTH** — image resolution in pixels (width); height is calculated to preserve the aspect ratio
* **NUM_COLOURS** — number of filament colours; each colour becomes a separate STL file
* **PUZZLE_WIDTH_MM** — total width of the finished puzzle in mm
* **THICKNESS_MM** — height of the colour pixel layer in mm
* **BASE_THICKNESS_MM** — height of the base plate in mm; must be thick enough to give the jigsaw tabs mechanical strength
* **USE_DITHER** — set to `True` to use Floyd-Steinberg dithering when reducing colours

### Jigsaw settings

* **PIECE_WIDTH_MM** — nominal width of each jigsaw piece in mm
* **PIECE_HEIGHT_MM** — nominal height of each jigsaw piece in mm
* **KERF_MM** — gap between printed pieces in mm; should match your printer's tolerance
* **RANDOM_SEED** — controls which tabs point up and which point down; change for a different pattern

```python
import math
import os
import random

import FreeCAD as App
import FreeCADGui as Gui
import Mesh
import Part
from PIL import Image


if App.ActiveDocument is not None:
    doc = App.ActiveDocument
    firstRun = False
else:
    doc = App.newDocument("JigsawMosaicPuzzle")
    firstRun = True

# ── Configuration ─────────────────────────────────────────────────────────────

INPUT_IMAGE = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-05-15 FreeCAD Python 6 Jigsaws\images\cube.png"
OUTPUT_FOLDER = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-05-15 FreeCAD Python 6 Jigsaws\stl"

# Mosaic settings (same meaning as in MosaicFromImage)
GRID_WIDTH        = 128           # image resolution in pixels (width)
NUM_COLOURS       = 4            # number of filament colours
PUZZLE_WIDTH_MM   = 128.0        # total puzzle width in mm
THICKNESS_MM      = 1.2          # height of colour pixel layer
BASE_THICKNESS_MM = 3.0          # base layer height — must be thick enough to
                                 # give the jigsaw tabs mechanical strength
USE_DITHER        = False

# Jigsaw settings
PIECE_WIDTH_MM    = 32.0         # width of each jigsaw piece
PIECE_HEIGHT_MM   = 32.0         # height of each jigsaw piece
KERF_MM           = 0.75         # gap between printed pieces (mm)
RANDOM_SEED       = 42           # change for a different random tab pattern

# ── Helpers ───────────────────────────────────────────────────────────────────

def vec(x, y, z=0.0):
    return App.Vector(float(x), float(y), float(z))


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_object(name, obj_type="Part::Feature"):
    obj = doc.getObject(name)
    if obj is None:
        obj = doc.addObject(obj_type, name)
    return obj


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


# ── Image processing ──────────────────────────────────────────────────────────

def load_and_quantize(path, grid_w, num_colours, use_dither=False):
    img = Image.open(path).convert("RGB")
    src_w, src_h = img.size
    grid_h = max(1, int(round(grid_w * src_h / src_w)))
    img = img.resize((grid_w, grid_h), Image.Resampling.LANCZOS)

    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    q = img.quantize(colors=num_colours, method=Image.MEDIANCUT, dither=dither_mode)
    rgb = q.convert("RGB")

    palette = rgb.getcolors(maxcolors=256)
    if palette is None:
        raise RuntimeError("Too many colours after quantization.")
    colours = sorted([e[1] for e in palette], key=luminance)
    return rgb, colours


def build_colour_shapes(img, colours, pixel_size, thickness, z0=0.0):
    """
    Build one Part compound per colour using horizontal run-length encoding,
    exactly as MosaicFromImage does.  Shapes start at z=z0.
    """
    width, depth = img.size
    pixels = img.load()
    colour_set = set(colours)
    solids_by_colour = {c: [] for c in colours}

    for y in range(depth):
        x = 0
        while x < width:
            run_colour = pixels[x, y]
            start_x = x
            while x < width and pixels[x, y] == run_colour:
                x += 1
            if run_colour not in colour_set:
                continue
            run_len = x - start_x
            world_x = start_x * pixel_size
            world_y = (depth - 1 - y) * pixel_size   # image Y → FreeCAD Y
            solids_by_colour[run_colour].append(
                Part.makeBox(run_len * pixel_size, pixel_size, thickness,
                             App.Vector(world_x, world_y, z0))
            )

    return {
        c: Part.makeCompound(solids_by_colour[c]) if solids_by_colour[c] else None
        for c in colours
    }

def make_puzzle_tab_path(tab_width, tab_height, is_hole=False):
    """
    Return a symmetrical jigsaw tab path.

    The path starts at (0, 0), ends at (tab_width, 0),
    and rises to tab_height.

    Only tab_width and tab_height define the bounding box.
    Internal proportions define the neck and curvature.
    """

    y_dir = -1 if is_hole else 1

    centre_x = tab_width / 2.0

    # Internal proportions
    neck_width_fraction = 0.35
    bulge_width_fraction = 0.45

    neck_height_fraction = 0.25
    bulge_height_fraction = 0.50

    half_neck = (tab_width * neck_width_fraction) / 2.0
    half_bulge = (tab_width * bulge_width_fraction) / 2.0

    left_curve = Part.BSplineCurve()
    left_curve.interpolate(
        [App.Vector(0, 0, 0),
         App.Vector(centre_x - half_neck,  tab_height * neck_height_fraction  * y_dir, 0),
         App.Vector(centre_x - half_bulge, tab_height * bulge_height_fraction * y_dir, 0),
         App.Vector(centre_x,              tab_height * y_dir,                         0)],
        InitialTangent=App.Vector(1, 0, 0),
        FinalTangent=App.Vector(1, 0, 0),
    )
    left_edge = left_curve.toShape()

    # mirror() is a single atomic operation around the plane at x=centre_x.
    # The junction point lies on that plane, so its coordinates are unchanged
    # by the reflection — no floating-point drift at the wire join.
    right_edge = left_edge.mirror(
        App.Vector(centre_x, 0, 0),
        App.Vector(1, 0, 0),
    ).reversed()

    return Part.Wire([left_edge, right_edge])


# ── Jigsaw cutter geometry ────────────────────────────────────────────────────

def make_puzzle_tab_cutter(piece_span, is_hole, segment_index):
    """
    Return the path edges for one piece segment of a cut line.

    Covers the full piece_span: a lead-in line, the tab curve (up or down
    depending on is_hole), and a lead-out line.  segment_index sets the X
    offset so the caller can concatenate segments directly.
    """
    tag_width   = piece_span / 2.0
    tab_height  = tag_width * 0.43
    seg_start   = segment_index * piece_span
    tab_start_x = seg_start + tag_width / 2.0

    tab_wire = make_puzzle_tab_path(tag_width, tab_height, is_hole=is_hole)
    tab_wire.translate(App.Vector(tab_start_x, 0, 0))

    return (
        [Part.LineSegment(
            App.Vector(seg_start, 0, 0),
            App.Vector(tab_start_x, 0, 0),
        ).toShape()]
        + list(tab_wire.OrderedEdges)
        + [Part.LineSegment(
            App.Vector(tab_start_x + tag_width, 0, 0),
            App.Vector(seg_start + piece_span, 0, 0),
        ).toShape()]
    )


def make_cut_line_solid(piece_span, flips, total_thickness, cut_size):
    """
    Build one continuous swept solid for a full cut line.

    Assembles the edges from make_puzzle_tab_cutter for each piece into a
    single wire, then sweeps it with a rectangular profile of width cut_size.
    """
    edges = []
    for i, flip in enumerate(flips):
        edges.extend(make_puzzle_tab_cutter(piece_span, flip, i))

    path_wire = Part.Wire(edges)

    half_c = cut_size / 2.0
    profile_wire = Part.Wire(Part.makePolygon([
        App.Vector(0, -half_c, 0),
        App.Vector(0,  half_c, 0),
        App.Vector(0,  half_c, total_thickness),
        App.Vector(0, -half_c, total_thickness),
        App.Vector(0, -half_c, 0),
    ]))

    line_solid = path_wire.makePipeShell([profile_wire], True, False)
    return line_solid

def build_jigsaw_cuts(puzzle_w, puzzle_h, piece_w, piece_h, total_thickness, kerf):
    """
    Build the cutter compound: one solid per cut line.

    Horizontal cuts run along X and are translated to each row boundary.
    Vertical cuts are built the same way then rotated 90 degrees CCW and
    translated to each column boundary.  The compound spans z=0 to
    z=total_thickness so it cuts through base plate and colour layers alike.
    """
    random.seed(RANDOM_SEED)

    cols = round(puzzle_w / piece_w)
    rows = round(puzzle_h / piece_h)

    solids = []

    for row in range(1, rows):
        flips = [random.choice([False, True]) for _ in range(cols)]
        solid = make_cut_line_solid(piece_w, flips, total_thickness, kerf)
        solid.translate(App.Vector(0, row * piece_h, 0))
        solids.append(solid)

    for col in range(1, cols):
        flips = [random.choice([False, True]) for _ in range(rows)]
        solid = make_cut_line_solid(piece_h, flips, total_thickness, kerf)
        mat = App.Matrix()
        mat.rotateZ(math.pi / 2.0)
        solid = solid.transformGeometry(mat)
        solid.translate(App.Vector(col * piece_w, 0, 0))
        solids.append(solid)

    return Part.makeCompound(solids)


# ── Main ──────────────────────────────────────────────────────────────────────

def build_jigsaw_mosaic_puzzle():
    ensure_folder(OUTPUT_FOLDER)

    print("Loading and quantizing image …")
    qimg, colours = load_and_quantize(INPUT_IMAGE, GRID_WIDTH, NUM_COLOURS, USE_DITHER)

    width, depth = qimg.size
    pixel_size      = PUZZLE_WIDTH_MM / float(width)
    puzzle_w        = width * pixel_size          # == PUZZLE_WIDTH_MM
    puzzle_h        = depth * pixel_size          # set by image aspect ratio
    total_thickness = BASE_THICKNESS_MM + THICKNESS_MM

    # Snap piece count to the nearest integer, then derive the actual piece
    # dimensions so cutters tile the puzzle exactly.  Using PIECE_WIDTH_MM /
    # PIECE_HEIGHT_MM directly would leave a gap at the far edge whenever
    # round() goes down and cols*piece_w < puzzle_w (or rows*piece_h < puzzle_h).
    cols = max(1, round(puzzle_w / PIECE_WIDTH_MM))
    rows = max(1, round(puzzle_h / PIECE_HEIGHT_MM))
    actual_piece_w = puzzle_w / cols
    actual_piece_h = puzzle_h / rows

    print(f"  Mosaic:   {width}×{depth} pixels at {pixel_size:.2f} mm/pixel")
    print(f"  Puzzle:   {puzzle_w:.1f}×{puzzle_h:.1f} mm, {total_thickness:.1f} mm thick")
    print(f"  Pieces:   {cols}×{rows} = {cols*rows} pieces "
          f"({actual_piece_w:.1f}×{actual_piece_h:.1f} mm each)")
    print(f"  Colours:  {', '.join(rgb_to_hex(c) for c in colours)}")

    # ── Build mosaic geometry ──────────────────────────────────────────────
    print("Building colour shapes …")
    colour_shapes = build_colour_shapes(
        qimg, colours, pixel_size, THICKNESS_MM, z0=BASE_THICKNESS_MM
    )
    base_shape = Part.makeBox(puzzle_w, puzzle_h, BASE_THICKNESS_MM)

    # ── Build jigsaw cutter compound (cuts through full thickness) ─────────
    print("Building jigsaw cutters …")
    jigsaw_cuts = build_jigsaw_cuts(
        puzzle_w, puzzle_h,
        actual_piece_w, actual_piece_h,
        total_thickness, KERF_MM,
    )

    # ── Cut base plate and each colour layer ───────────────────────────────
    # The same cutter compound is applied to every layer so all cuts align.
    print("Cutting base plate …")
    base_cut = base_shape.cut(jigsaw_cuts)
    jigsaw_obj = get_object("jigsaw")
    jigsaw_obj.Shape = jigsaw_cuts
    base_obj = get_object("Base")
    base_obj.Shape = base_cut
    try:
        base_obj.ViewObject.ShapeColor = (0.20, 0.15, 0.10)
    except Exception:
        pass
    base_stl = os.path.join(OUTPUT_FOLDER, "base_plate.stl")
    Mesh.export([base_obj], base_stl)
    print("  Wrote:", base_stl)

    for i, colour in enumerate(colours):
        shape = colour_shapes[colour]
        if shape is None:
            continue
        print(f"Cutting colour {i+1} {rgb_to_hex(colour)} …")
        cut_shape = shape.cut(jigsaw_cuts)
        hex_name  = rgb_to_hex(colour).replace("#", "")
        obj       = get_object("C" + hex_name)
        obj.Shape = cut_shape
        try:
            obj.ViewObject.ShapeColor = tuple(c / 255.0 for c in colour)
        except Exception:
            pass
        stl_file = os.path.join(OUTPUT_FOLDER, f"colour_{i+1}_{hex_name}.stl")
        Mesh.export([obj], stl_file)
        print("  Wrote:", stl_file)

    # ── Save preview image ─────────────────────────────────────────────────
    scale = max(1, 400 // max(width, depth))
    preview = qimg.resize((width * scale, depth * scale), Image.Resampling.NEAREST)
    preview_file = os.path.join(OUTPUT_FOLDER, "preview.png")
    preview.save(preview_file)
    print("Wrote:", preview_file)

    doc.recompute()
    print("Done.")


build_jigsaw_mosaic_puzzle()

doc.recompute()
if firstRun:
    Gui.ActiveDocument.ActiveView.fitAll()
```

[Back](/README.md)
