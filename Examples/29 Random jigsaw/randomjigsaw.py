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
    doc = App.newDocument("RandomJigsawPuzzle")
    firstRun = True


# ── Configuration ─────────────────────────────────────────────────────────────

INPUT_IMAGE = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-05-15 FreeCAD Python 6 Jigsaws\images\cube.png"
OUTPUT_FOLDER = r"C:\Users\robmi\OneDrive\Hackspace Magazine\2026-05-15 FreeCAD Python 6 Jigsaws\stl"

# Mosaic settings
GRID_WIDTH        = 128           # image resolution in pixels (width)
NUM_COLOURS       = 4            # number of filament colours
PUZZLE_WIDTH_MM   = 128.0        # total puzzle width in mm
THICKNESS_MM      = 1.2          # height of colour pixel layer
BASE_THICKNESS_MM = 3.0          # base layer height
USE_DITHER        = False

# Jigsaw settings
PIECE_WIDTH_MM    = 32.0         # nominal piece width in mm
PIECE_HEIGHT_MM   = 32.0         # nominal piece height in mm
KERF_MM           = 0.75         # gap between printed pieces (mm)
RANDOM_SEED       = 42           # change for a different pattern

# How far the tab can slide along a piece edge.
# lead_in is sampled uniformly in [MIN_LEAD_FRAC, 1 - 0.5 - MIN_LEAD_FRAC] * piece_span
# so the tab (width = piece_span/2) never runs off either end.
MIN_LEAD_FRAC = 0.12             # minimum straight track before and after each tab


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    """Build one Part compound per colour using horizontal run-length encoding."""
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
            world_y = (depth - 1 - y) * pixel_size
            solids_by_colour[run_colour].append(
                Part.makeBox(run_len * pixel_size, pixel_size, thickness,
                             App.Vector(world_x, world_y, z0))
            )

    return {
        c: Part.makeCompound(solids_by_colour[c]) if solids_by_colour[c] else None
        for c in colours
    }


# ── Tab path ──────────────────────────────────────────────────────────────────

def make_puzzle_tab_path(tab_width, tab_height, is_hole=False):
    """
    Return a two-edge wire tracing one jigsaw tab.

    Starts at (0, 0), ends at (tab_width, 0), rises to tab_height.
    The right half is built by reflecting the left half's computed BSpline poles
    around the centre in Python — no geometric transforms, so the junction
    between the two halves has no floating-point gap.
    """
    y_dir    = -1 if is_hole else 1
    centre_x = tab_width / 2.0

    neck_width_fraction   = 0.35
    bulge_width_fraction  = 0.45
    neck_height_fraction  = 0.25
    bulge_height_fraction = 0.50

    half_neck  = (tab_width * neck_width_fraction)  / 2.0
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

def make_cut_line_solid(piece_span, segments, total_thickness, kerf):
    """
    Build one continuous swept solid for a full cut line.

    segments  — list of (is_hole, lead_in) per piece along the line.
                is_hole: True makes the tab dip into -Y.
                lead_in: distance from the piece boundary to the start of the tab.

    The tab is always tag_width = piece_span/2 wide and proportionally tall.
    """
    tag_width  = piece_span / 2.0
    tab_height = tag_width * 0.43

    edges = []
    for i, (is_hole, lead_in) in enumerate(segments):
        seg_start   = i * piece_span
        tab_start_x = seg_start + lead_in
        tab_end_x   = tab_start_x + tag_width

        edges.append(Part.LineSegment(
            App.Vector(seg_start, 0, 0),
            App.Vector(tab_start_x, 0, 0),
        ).toShape())

        tab_wire = make_puzzle_tab_path(tag_width, tab_height, is_hole=is_hole)
        tab_wire.translate(App.Vector(tab_start_x, 0, 0))
        edges.extend(tab_wire.OrderedEdges)

        edges.append(Part.LineSegment(
            App.Vector(tab_end_x, 0, 0),
            App.Vector((i + 1) * piece_span, 0, 0),
        ).toShape())

    path_wire = Part.Wire(edges)

    half_k = kerf / 2.0
    profile_wire = Part.Wire(Part.makePolygon([
        App.Vector(0, -half_k, 0),
        App.Vector(0,  half_k, 0),
        App.Vector(0,  half_k, total_thickness),
        App.Vector(0, -half_k, total_thickness),
        App.Vector(0, -half_k, 0),
    ]))

    line_solid = path_wire.makePipeShell([profile_wire], True, False)
    return line_solid


def random_segments(n, piece_span, rng):
    """Return n (is_hole, lead_in) pairs with randomly offset tabs."""
    tag_width = piece_span / 2.0
    min_lead  = MIN_LEAD_FRAC * piece_span
    max_lead  = piece_span - tag_width - min_lead
    return [
        (rng.choice([False, True]), rng.uniform(min_lead, max(min_lead, max_lead)))
        for _ in range(n)
    ]


def build_jigsaw_cuts(puzzle_w, puzzle_h, piece_w, piece_h, total_thickness, kerf):
    """Build the cutter compound: one solid per cut line with randomly offset tabs."""
    rng  = random.Random(RANDOM_SEED)
    cols = round(puzzle_w / piece_w)
    rows = round(puzzle_h / piece_h)

    solids = []

    for row in range(1, rows):
        segments  = random_segments(cols, piece_w, rng)
        solid = make_cut_line_solid(piece_w, segments, total_thickness, kerf)
        if solid.isNull():
            print(f"  Warning: null solid for horizontal cut at row {row} — skipping")
            continue
        solid.translate(App.Vector(0, row * piece_h, 0))
        solids.append(solid)

    for col in range(1, cols):
        segments  = random_segments(rows, piece_h, rng)
        solid = make_cut_line_solid(piece_h, segments, total_thickness, kerf)
        if solid.isNull():
            print(f"  Warning: null solid for vertical cut at col {col} — skipping")
            continue
        mat = App.Matrix()
        mat.rotateZ(math.pi / 2.0)
        solid = solid.transformGeometry(mat)
        solid.translate(App.Vector(col * piece_w, 0, 0))
        solids.append(solid)

    if not solids:
        raise RuntimeError("All cut-line solids failed — check geometry parameters.")
    return Part.makeCompound(solids)


# ── Main ──────────────────────────────────────────────────────────────────────

def build_jigsaw_mosaic_puzzle():
    ensure_folder(OUTPUT_FOLDER)

    print("Loading and quantizing image …")
    qimg, colours = load_and_quantize(INPUT_IMAGE, GRID_WIDTH, NUM_COLOURS, USE_DITHER)

    width, depth = qimg.size
    pixel_size      = PUZZLE_WIDTH_MM / float(width)
    puzzle_w        = width  * pixel_size
    puzzle_h        = depth  * pixel_size
    total_thickness = BASE_THICKNESS_MM + THICKNESS_MM

    cols = max(1, round(puzzle_w / PIECE_WIDTH_MM))
    rows = max(1, round(puzzle_h / PIECE_HEIGHT_MM))
    actual_piece_w = puzzle_w / cols
    actual_piece_h = puzzle_h / rows

    print(f"  Mosaic:   {width}×{depth} pixels at {pixel_size:.2f} mm/pixel")
    print(f"  Puzzle:   {puzzle_w:.1f}×{puzzle_h:.1f} mm, {total_thickness:.1f} mm thick")
    print(f"  Pieces:   {cols}×{rows} = {cols*rows} pieces "
          f"({actual_piece_w:.1f}×{actual_piece_h:.1f} mm each)")
    print(f"  Colours:  {', '.join(rgb_to_hex(c) for c in colours)}")

    print("Building colour shapes …")
    colour_shapes = build_colour_shapes(
        qimg, colours, pixel_size, THICKNESS_MM, z0=BASE_THICKNESS_MM
    )
    base_shape = Part.makeBox(puzzle_w, puzzle_h, BASE_THICKNESS_MM)

    print("Building jigsaw cutters …")
    jigsaw_cuts = build_jigsaw_cuts(
        puzzle_w, puzzle_h,
        actual_piece_w, actual_piece_h,
        total_thickness, KERF_MM,
    )

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
