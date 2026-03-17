"""
Pi Zero 2W Waterproof Housing — Marine Grade (Multi-Material)
Two-piece enclosure for Raspberry Pi Zero 2W.
Designed for bulkhead mounting on S/V Circus.

SEALING: Crush-seal TPU gasket printed directly into the base rim using
multi-material (Bambu AMS). No silicone needed.

The gasket uses a RAISED RIDGE cross-section — a tall, narrow bead that
concentrates clamping force onto a small contact area. This is critical
because Bambu TPU 68D is Shore 68D (semi-rigid, like a hard skateboard
wheel), so a flat gasket would not deform enough to seal. The ridge
crushes ~0.3mm under bolt torque, creating high surface pressure for a
reliable seal despite the stiff material.

PRINT SETUP (Bambu Lab P2S with AMS):
  Filament 1: PETG (body, lid)
  Filament 2: Bambu TPU 68D (gasket) — 220-240°C nozzle, 30-35°C bed
  Nozzle: 0.4mm (TPU 68D is NOT compatible with 0.2mm nozzle)
  Import all 3 STLs into slicer, assign materials, print as one job.

All dimensions in mm.
"""
import cadquery as cq

# ============================================================
# PARAMETERS
# ============================================================
# Board dimensions (Pi Zero 2W)
BOARD_LENGTH = 65.0
BOARD_WIDTH = 30.0
BOARD_HEIGHT = 5.0

# Enclosure
WALL = 3.0                   # wall thickness (PETG, structural)
CLEARANCE = 3.0              # clearance around board each side
CAVITY_DEPTH = 20.0          # internal cavity depth
LID_THICKNESS = 4.0          # lid plate thickness
LID_LIP_DEPTH = 2.5          # lid lip extends into base cavity
LID_LIP_GAP = 0.3            # clearance between lip and cavity wall
CORNER_RADIUS = 2.0          # fillet radius on all corners

# TPU Crush-Seal Gasket (printed in-place via AMS multi-material)
# Bambu TPU 68D — Shore 68D (semi-rigid), 220-240°C nozzle, AMS compatible
# DESIGN NOTE: Shore 68D is very stiff for a seal. We use a raised-ridge
# cross-section (1.2mm wide base, 0.8mm proud) so the narrow contact line
# generates high surface pressure under M3 bolt clamping. The ridge crushes
# ~0.3mm to form the seal. A flat gasket at this hardness would NOT seal.
GASKET_WIDTH = 1.2           # ridge base width (narrow = higher pressure)
GASKET_GROOVE_W = 1.6        # groove width (0.2mm clearance each side)
GASKET_DEPTH = 1.2           # groove depth cut into base rim
GASKET_PROUD = 0.8           # ridge height above rim (crush zone)
GASKET_INSET = 1.5           # inset from outer wall edge (centers on rim)

# Mounting flange
FLANGE_EXT = 8.0             # extension beyond body each side
FLANGE_THICK = 4.0           # flange plate thickness

# Lid-to-base bolts (M3 × 4, corner bosses with heat-set inserts)
BOSS_OD = 8.0                # corner boss outer diameter
INSERT_DIA = 4.2             # M3 heat-set insert hole
INSERT_DEPTH = 6.0           # insert pocket depth
BOLT_CLEARANCE = 3.4         # M3 clearance through-hole
BOLT_HEAD_DIA = 6.0          # M3 socket head cap
BOLT_HEAD_DEPTH = 3.2        # counterbore depth in lid

# PCB mounting (Pi Zero 2W — 58×23mm pattern, M2.5)
PCB_PATTERN_L = 58.0
PCB_PATTERN_W = 23.0
STANDOFF_OD = 5.5
STANDOFF_HEIGHT = 4.0
STANDOFF_HOLE_DIA = 2.2      # undersized for M2.5 self-tap

# Cable gland (PG7 on +X short end)
GLAND_BOSS_OD = 18.0
GLAND_BOSS_LENGTH = 8.0
GLAND_HOLE_DIA = 12.0        # M12×1.5 thread for PG7

# Flange mounting (M4 × 4)
FLANGE_HOLE_DIA = 4.5        # M4 clearance

# Visualization
EXPLODE_GAP = 30.0           # vertical gap between base and lid

# ============================================================
# DERIVED DIMENSIONS
# ============================================================
CAVITY_L = BOARD_LENGTH + 2 * CLEARANCE     # 71
CAVITY_W = BOARD_WIDTH + 2 * CLEARANCE      # 36
EXT_L = CAVITY_L + 2 * WALL                 # 77
EXT_W = CAVITY_W + 2 * WALL                 # 42
BODY_H = CAVITY_DEPTH + WALL                # 23
TOTAL_BASE_H = FLANGE_THICK + BODY_H        # 27
FLOOR_Z = FLANGE_THICK + WALL               # 7 — cavity floor

LIP_L = CAVITY_L - 2 * LID_LIP_GAP
LIP_W = CAVITY_W - 2 * LID_LIP_GAP
LIP_WALL = 2.0

FLANGE_L = EXT_L + 2 * FLANGE_EXT           # 93
FLANGE_W = EXT_W + 2 * FLANGE_EXT           # 58

# Gasket groove rectangle (centered on wall rim)
GROOVE_OUTER_L = EXT_L - 2 * GASKET_INSET
GROOVE_OUTER_W = EXT_W - 2 * GASKET_INSET
GROOVE_INNER_L = GROOVE_OUTER_L - 2 * GASKET_GROOVE_W
GROOVE_INNER_W = GROOVE_OUTER_W - 2 * GASKET_GROOVE_W

# Gasket ridge (narrower than groove — sits centered in it)
RIDGE_OFFSET = (GASKET_GROOVE_W - GASKET_WIDTH) / 2  # 0.2mm each side
RIDGE_OUTER_L = GROOVE_OUTER_L - 2 * RIDGE_OFFSET
RIDGE_OUTER_W = GROOVE_OUTER_W - 2 * RIDGE_OFFSET
RIDGE_INNER_L = RIDGE_OUTER_L - 2 * GASKET_WIDTH
RIDGE_INNER_W = RIDGE_OUTER_W - 2 * GASKET_WIDTH

# Feature positions
BOSS_INSET = 1.0  # inset from cavity corner (bosses merge with walls)
BOLT_POSITIONS = [
    ( CAVITY_L/2 - BOSS_INSET,  CAVITY_W/2 - BOSS_INSET),
    ( CAVITY_L/2 - BOSS_INSET, -CAVITY_W/2 + BOSS_INSET),
    (-CAVITY_L/2 + BOSS_INSET,  CAVITY_W/2 - BOSS_INSET),
    (-CAVITY_L/2 + BOSS_INSET, -CAVITY_W/2 + BOSS_INSET),
]

PCB_POSITIONS = [
    ( PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    ( PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
]

CABLE_GLAND_Z = FLANGE_THICK + BODY_H / 2   # 15.5 — mid-body

FLANGE_MOUNT_POSITIONS = [
    ( EXT_L/2 + FLANGE_EXT/2,  EXT_W/2 + FLANGE_EXT/2),
    ( EXT_L/2 + FLANGE_EXT/2, -EXT_W/2 - FLANGE_EXT/2),
    (-EXT_L/2 - FLANGE_EXT/2,  EXT_W/2 + FLANGE_EXT/2),
    (-EXT_L/2 - FLANGE_EXT/2, -EXT_W/2 - FLANGE_EXT/2),
]

# ============================================================
# PART: Base (PETG)
# ============================================================
# Flange plate
flange = (
    cq.Workplane("XY")
    .rect(FLANGE_L, FLANGE_W)
    .extrude(FLANGE_THICK)
)

# Body on top of flange
body = (
    cq.Workplane("XY")
    .workplane(offset=FLANGE_THICK)
    .rect(EXT_L, EXT_W)
    .extrude(BODY_H)
)
base = flange.union(body)

# Cut cavity from top
base = (
    base.faces(">Z").workplane()
    .rect(CAVITY_L, CAVITY_W)
    .cutBlind(-CAVITY_DEPTH)
)

# --- Corner bosses (merge with cavity walls) ---
for bx, by in BOLT_POSITIONS:
    boss = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_Z)
        .center(bx, by)
        .circle(BOSS_OD / 2)
        .extrude(CAVITY_DEPTH)
    )
    base = base.union(boss)

# --- PCB standoffs ---
for px, py in PCB_POSITIONS:
    standoff = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_Z)
        .center(px, py)
        .circle(STANDOFF_OD / 2)
        .extrude(STANDOFF_HEIGHT)
    )
    base = base.union(standoff)

# --- PG7 cable gland boss on +X wall ---
gland_boss = (
    cq.Workplane("YZ")
    .workplane(offset=EXT_L / 2)
    .center(0, CABLE_GLAND_Z)
    .circle(GLAND_BOSS_OD / 2)
    .extrude(GLAND_BOSS_LENGTH)
)
base = base.union(gland_boss)

# --- CUT: Gasket groove in base top rim ---
# Wider groove with clearance for the narrower TPU ridge
groove_outer = (
    cq.Workplane("XY")
    .workplane(offset=TOTAL_BASE_H + 0.01)
    .rect(GROOVE_OUTER_L, GROOVE_OUTER_W)
    .extrude(-GASKET_DEPTH - 0.01)
)
groove_inner = (
    cq.Workplane("XY")
    .workplane(offset=TOTAL_BASE_H + 0.02)
    .rect(GROOVE_INNER_L, GROOVE_INNER_W)
    .extrude(-GASKET_DEPTH - 0.03)
)
groove = groove_outer.cut(groove_inner)
base = base.cut(groove)

# --- CUT: Heat-set insert pockets in corner bosses ---
for bx, by in BOLT_POSITIONS:
    insert_hole = (
        cq.Workplane("XY")
        .workplane(offset=TOTAL_BASE_H + 1)
        .center(bx, by)
        .circle(INSERT_DIA / 2)
        .extrude(-(INSERT_DEPTH + 1))
    )
    base = base.cut(insert_hole)

# --- CUT: PCB screw holes in standoffs ---
for px, py in PCB_POSITIONS:
    screw_hole = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_Z + STANDOFF_HEIGHT + 1)
        .center(px, py)
        .circle(STANDOFF_HOLE_DIA / 2)
        .extrude(-(STANDOFF_HEIGHT + 2))
    )
    base = base.cut(screw_hole)

# --- CUT: Cable gland M12 through-hole ---
gland_hole = (
    cq.Workplane("YZ")
    .workplane(offset=EXT_L / 2 + GLAND_BOSS_LENGTH + 1)
    .center(0, CABLE_GLAND_Z)
    .circle(GLAND_HOLE_DIA / 2)
    .extrude(-(GLAND_BOSS_LENGTH + WALL + 3))
)
base = base.cut(gland_hole)

# --- CUT: M4 flange mounting holes ---
for fx, fy in FLANGE_MOUNT_POSITIONS:
    flange_hole = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .center(fx, fy)
        .circle(FLANGE_HOLE_DIA / 2)
        .extrude(FLANGE_THICK + 2)
    )
    base = base.cut(flange_hole)

# --- Fillet base corners ---
try:
    base = base.edges("|Z").fillet(CORNER_RADIUS)
except:
    print("Warning: could not fillet all base vertical edges")

try:
    base = base.edges(">Z").fillet(CORNER_RADIUS * 0.5)
except:
    print("Warning: could not fillet base top edges")

# ============================================================
# PART: TPU Crush-Seal Gasket (Bambu TPU 68D — separate STL for AMS)
# ============================================================
# Narrow ridge cross-section: 1.2mm wide, sits in 1.6mm groove with 0.2mm
# clearance each side. Ridge stands 0.8mm proud of the rim — the lid
# crushes it ~0.3mm when bolts are tightened. Narrow contact line creates
# high surface pressure despite the stiff Shore 68D material.
#
# Export as separate STL — assign TPU filament in slicer.
GASKET_TOTAL_H = GASKET_DEPTH + GASKET_PROUD
GASKET_Z = TOTAL_BASE_H - GASKET_DEPTH  # bottom of groove

gasket_outer = (
    cq.Workplane("XY")
    .workplane(offset=GASKET_Z)
    .rect(RIDGE_OUTER_L, RIDGE_OUTER_W)
    .extrude(GASKET_TOTAL_H)
)
gasket_inner = (
    cq.Workplane("XY")
    .workplane(offset=GASKET_Z - 0.01)
    .rect(RIDGE_INNER_L, RIDGE_INNER_W)
    .extrude(GASKET_TOTAL_H + 0.02)
)
gasket = gasket_outer.cut(gasket_inner)

# Cut clearance around bolt bosses so gasket doesn't interfere
for bx, by in BOLT_POSITIONS:
    boss_clear = (
        cq.Workplane("XY")
        .workplane(offset=GASKET_Z - 0.1)
        .center(bx, by)
        .circle(BOSS_OD / 2 + 0.5)
        .extrude(GASKET_TOTAL_H + 0.2)
    )
    gasket = gasket.cut(boss_clear)

# ============================================================
# PART: Lid (PETG — exploded position for visualization)
# ============================================================
LID_BOTTOM_Z = TOTAL_BASE_H + EXPLODE_GAP

# Main lid plate
lid = (
    cq.Workplane("XY")
    .workplane(offset=LID_BOTTOM_Z)
    .rect(EXT_L, EXT_W)
    .extrude(LID_THICKNESS)
)

# Inner lip frame
lip_outer = (
    cq.Workplane("XY")
    .workplane(offset=LID_BOTTOM_Z)
    .rect(LIP_L, LIP_W)
    .extrude(-LID_LIP_DEPTH)
)
lip_cutout = (
    cq.Workplane("XY")
    .workplane(offset=LID_BOTTOM_Z + 1)
    .rect(LIP_L - 2 * LIP_WALL, LIP_W - 2 * LIP_WALL)
    .extrude(-(LID_LIP_DEPTH + 2))
)
lid = lid.union(lip_outer.cut(lip_cutout))

# --- CUT: M3 counterbored bolt holes through lid ---
for bx, by in BOLT_POSITIONS:
    # Clearance hole through entire lid + lip
    bolt_hole = (
        cq.Workplane("XY")
        .workplane(offset=LID_BOTTOM_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-(LID_THICKNESS + LID_LIP_DEPTH + 2))
    )
    lid = lid.cut(bolt_hole)

    # Counterbore for bolt head (from lid top)
    cbore = (
        cq.Workplane("XY")
        .workplane(offset=LID_BOTTOM_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_HEAD_DIA / 2)
        .extrude(-(BOLT_HEAD_DEPTH + 1))
    )
    lid = lid.cut(cbore)

# --- Fillet lid corners ---
try:
    lid = lid.edges("|Z").fillet(CORNER_RADIUS)
except:
    print("Warning: could not fillet all lid vertical edges")

# ============================================================
# EXPORT
# ============================================================
import os
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
cq.exporters.export(base, os.path.join(OUT_DIR, "pizero_housing_base.stl"))
cq.exporters.export(lid, os.path.join(OUT_DIR, "pizero_housing_lid.stl"))
cq.exporters.export(gasket, os.path.join(OUT_DIR, "pizero_housing_gasket.stl"))

print(f"Base:    {FLANGE_L:.1f} × {FLANGE_W:.1f} × {TOTAL_BASE_H:.1f} mm")
print(f"Body:    {EXT_L:.1f} × {EXT_W:.1f} × {BODY_H:.1f} mm")
print(f"Lid:     {EXT_L:.1f} × {EXT_W:.1f} × {LID_THICKNESS:.1f} mm")
print(f"Cavity:  {CAVITY_L:.1f} × {CAVITY_W:.1f} × {CAVITY_DEPTH:.1f} mm")
print(f"Wall:    {WALL:.1f}mm  |  Corner R: {CORNER_RADIUS:.1f}mm")
print()
print("Crush-Seal Gasket (TPU 68D — Shore 68D semi-rigid):")
print(f"  Groove:  {GROOVE_OUTER_L:.1f} × {GROOVE_OUTER_W:.1f} mm (outer)")
print(f"           {GASKET_GROOVE_W:.1f}mm wide × {GASKET_DEPTH:.1f}mm deep")
print(f"  Ridge:   {GASKET_WIDTH:.1f}mm wide (in {GASKET_GROOVE_W:.1f}mm groove, {RIDGE_OFFSET:.1f}mm clearance)")
print(f"  Proud:   {GASKET_PROUD:.1f}mm above rim (crush zone, expect ~0.3mm compression)")
print(f"  Total H: {GASKET_TOTAL_H:.1f}mm")
print()
print("Features:")
print(f"  4× M3 corner bosses (OD {BOSS_OD:.0f}mm, heat-set inserts)")
print(f"  4× M2.5 PCB standoffs ({PCB_PATTERN_L:.0f}×{PCB_PATTERN_W:.0f}mm pattern, {STANDOFF_HEIGHT:.0f}mm tall)")
print(f"  1× PG7 cable gland boss (M12 hole, OD {GLAND_BOSS_OD:.0f}mm)")
print(f"  4× M4 flange mounting holes")
print(f"  4× M3 counterbored lid bolts")
print(f"  1× TPU crush-seal gasket ridge (printed in-place via AMS)")
print()
print("Multi-Material Print Setup (Bambu P2S + AMS):")
print("  1. Import all 3 STLs into Bambu Studio")
print("  2. Assign PETG to base + lid")
print("  3. Assign Bambu TPU 68D to gasket")
print("  4. Use 0.4mm nozzle (TPU 68D incompatible with 0.2mm)")
print("  5. TPU settings: 220-240°C nozzle, 30-35°C bed")
print()
print("Exported: pizero_housing_base.stl, pizero_housing_lid.stl, pizero_housing_gasket.stl")
