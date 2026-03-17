"""
Pi Zero 2W Waterproof Housing — Marine Grade (Multi-Material)
Two-piece enclosure for Raspberry Pi Zero 2W.
Designed for bulkhead mounting on S/V Circus.

SEALING ARCHITECTURE:
  - Lid bolts are on EXTERNAL PILLAR BOSSES at the flange corners,
    OUTSIDE the sealed body walls.
  - TPU gasket is a CONTINUOUS unbroken rectangle on the body rim.
  - No bolt holes penetrate the sealed volume — zero leak paths.
  - This matches how real IP67 enclosures work: fasteners outside the seal.

GASKET DESIGN:
  Bambu TPU 68D is Shore 68D (semi-rigid). A flat gasket would not deform
  enough to seal. The gasket uses a raised-ridge cross-section — a narrow
  1.2mm bead standing 0.8mm proud — that concentrates bolt clamping force
  onto a small contact area for high surface pressure despite the stiff
  material. The ridge crushes ~0.3mm under bolt torque to form the seal.

PRINT SETUP (Bambu Lab P2S with AMS):
  Filament 1: PETG (body, lid)
  Filament 2: Bambu TPU 68D (gasket) — 220-240°C nozzle, 30-35°C bed
  Nozzle: 0.4mm (TPU 68D is NOT compatible with 0.2mm nozzle)
  Import all 3 STLs into slicer, assign materials, print as one job.
  (Bolts STL is for visualization only — not printed.)

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
# Ridge cross-section concentrates clamping force for high surface pressure.
GASKET_WIDTH = 1.2           # ridge base width (narrow = higher pressure)
GASKET_GROOVE_W = 1.6        # groove width (0.2mm clearance each side)
GASKET_DEPTH = 1.2           # groove depth cut into base rim
GASKET_PROUD = 0.8           # ridge height above rim (crush zone)
GASKET_INSET = 1.5           # inset from outer wall edge (centers on rim)

# Mounting flange
FLANGE_EXT = 8.0             # extension beyond body each side
FLANGE_THICK = 4.0           # flange plate thickness

# External bolt pillar bosses — rise from flange to body rim at each corner
# These are OUTSIDE the body walls, on the flange corners
BOSS_OD = 8.0                # pillar outer diameter
BOSS_FLAT = 1.0              # flat width where boss meets body wall

# Lid-to-base bolts — M3 SHCS into heat-set inserts in pillar tops
LID_BOLT_INSET = 4.0         # bolt center inset from flange edge
INSERT_DIA = 4.2             # M3 heat-set insert hole
INSERT_DEPTH = 6.0           # insert pocket depth (into pillar top)
BOLT_CLEARANCE = 3.4         # M3 clearance through-hole in lid
BOLT_HEAD_DIA = 6.0          # M3 socket head counterbore dia
BOLT_HEAD_DEPTH = 3.2        # counterbore depth in lid

# M3 SHCS bolt dimensions (for visualization & interference check)
M3_HEAD_DIA = 5.5            # actual M3 SHCS head diameter
M3_HEAD_H = 3.0              # actual M3 SHCS head height
M3_SHAFT_DIA = 3.0           # M3 shaft diameter
M3_BOLT_LENGTH = 6.0         # M3x6 shaft length

# Gasket crush control
GASKET_CRUSH = 0.3           # desired gasket compression (mm)

# Bulkhead mounting (M4 × 4, also on flange)
FLANGE_HOLE_DIA = 4.5        # M4 clearance
BULKHEAD_INSET = 4.0         # M4 hole inset from flange edge

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

# Gasket groove — continuous rectangle on body wall rim (no interruptions)
GROOVE_OUTER_L = EXT_L - 2 * GASKET_INSET
GROOVE_OUTER_W = EXT_W - 2 * GASKET_INSET
GROOVE_INNER_L = GROOVE_OUTER_L - 2 * GASKET_GROOVE_W
GROOVE_INNER_W = GROOVE_OUTER_W - 2 * GASKET_GROOVE_W

# Gasket ridge (narrower than groove — sits centered in it)
RIDGE_OFFSET = (GASKET_GROOVE_W - GASKET_WIDTH) / 2
RIDGE_OUTER_L = GROOVE_OUTER_L - 2 * RIDGE_OFFSET
RIDGE_OUTER_W = GROOVE_OUTER_W - 2 * RIDGE_OFFSET
RIDGE_INNER_L = RIDGE_OUTER_L - 2 * GASKET_WIDTH
RIDGE_INNER_W = RIDGE_OUTER_W - 2 * GASKET_WIDTH

# Feature positions
# Lid bolt positions — on flange corners, OUTSIDE the body walls
LID_BOLT_POSITIONS = [
    ( FLANGE_L/2 - LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    ( FLANGE_L/2 - LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
]

# Bulkhead mounting — centered on each flange edge
BULKHEAD_POSITIONS = [
    ( 0,  FLANGE_W/2 - BULKHEAD_INSET),
    ( 0, -FLANGE_W/2 + BULKHEAD_INSET),
    ( FLANGE_L/2 - BULKHEAD_INSET, 0),
    (-FLANGE_L/2 + BULKHEAD_INSET, 0),
]

PCB_POSITIONS = [
    ( PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    ( PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
]

CABLE_GLAND_Z = FLANGE_THICK + BODY_H / 2   # mid-body

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

# --- External bolt pillar bosses (flange corners → above body rim) ---
# Pillars are TALLER than body walls by (GASKET_PROUD - GASKET_CRUSH).
# This makes them act as crush limiters: when the lid is fully bolted
# down against the pillar tops, there's a controlled gap between lid
# and body rim, compressing the gasket exactly GASKET_CRUSH (0.3mm).
PILLAR_STANDOFF = GASKET_PROUD - GASKET_CRUSH  # 0.5mm above rim
PILLAR_H = BODY_H + PILLAR_STANDOFF
for bx, by in LID_BOLT_POSITIONS:
    pillar = (
        cq.Workplane("XY")
        .workplane(offset=FLANGE_THICK)
        .center(bx, by)
        .circle(BOSS_OD / 2)
        .extrude(PILLAR_H)
    )
    base = base.union(pillar)

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
# CONTINUOUS rectangle — no interruptions. Bolts are outside on pillar bosses.
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

# --- CUT: Heat-set insert pockets in pillar TOPS ---
PILLAR_TOP_Z = FLANGE_THICK + PILLAR_H
for bx, by in LID_BOLT_POSITIONS:
    insert_hole = (
        cq.Workplane("XY")
        .workplane(offset=PILLAR_TOP_Z + 0.01)
        .center(bx, by)
        .circle(INSERT_DIA / 2)
        .extrude(-(INSERT_DEPTH + 0.01))
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

# --- CUT: M4 bulkhead mounting holes (through flange) ---
for fx, fy in BULKHEAD_POSITIONS:
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
# CONTINUOUS unbroken rectangle — no cuts, no gaps.
# 1.2mm wide ridge in 1.6mm groove, 0.8mm proud of rim.
# Crush zone compresses ~0.3mm under bolt torque.
GASKET_TOTAL_H = GASKET_DEPTH + GASKET_PROUD
GASKET_Z = TOTAL_BASE_H - GASKET_DEPTH

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

# ============================================================
# PART: Lid (PETG — exploded position for visualization)
# ============================================================
# Lid covers the FULL FLANGE so bolts go through flange area into pillars.
# Lid sits on pillar tops (which are PILLAR_STANDOFF above body rim).
LID_BOTTOM_Z = PILLAR_TOP_Z + EXPLODE_GAP

# Main lid plate — full flange size
lid = (
    cq.Workplane("XY")
    .workplane(offset=LID_BOTTOM_Z)
    .rect(FLANGE_L, FLANGE_W)
    .extrude(LID_THICKNESS)
)

# Inner lip frame — drops into cavity for alignment
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

# --- CUT: M3 counterbored bolt holes through lid (on flange, outside seal) ---
for bx, by in LID_BOLT_POSITIONS:
    bolt_hole = (
        cq.Workplane("XY")
        .workplane(offset=LID_BOTTOM_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-(LID_THICKNESS + 2))
    )
    lid = lid.cut(bolt_hole)

    cbore = (
        cq.Workplane("XY")
        .workplane(offset=LID_BOTTOM_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_HEAD_DIA / 2)
        .extrude(-(BOLT_HEAD_DEPTH + 1))
    )
    lid = lid.cut(cbore)

# --- CUT: M4 bulkhead holes through lid (matching base flange) ---
for fx, fy in BULKHEAD_POSITIONS:
    flange_hole = (
        cq.Workplane("XY")
        .workplane(offset=LID_BOTTOM_Z - 1)
        .center(fx, fy)
        .circle(FLANGE_HOLE_DIA / 2)
        .extrude(LID_THICKNESS + 2)
    )
    lid = lid.cut(flange_hole)

# --- Fillet lid corners ---
try:
    lid = lid.edges("|Z").fillet(CORNER_RADIUS)
except:
    print("Warning: could not fillet all lid vertical edges")

# ============================================================
# PART: Bolts (visualization only — M3x10 SHCS in assembled position)
# ============================================================
# Bolts are shown in ASSEMBLED position (not exploded) to check interference
# with base, lid, gasket, and pillars.
bolts = None
for bx, by in LID_BOLT_POSITIONS:
    # Bolt head top is flush with lid top surface (in assembled position)
    ASSEMBLED_LID_TOP = PILLAR_TOP_Z + LID_THICKNESS
    BOLT_TOP_Z = ASSEMBLED_LID_TOP
    HEAD_BOTTOM_Z = BOLT_TOP_Z - M3_HEAD_H
    SHAFT_BOTTOM_Z = HEAD_BOTTOM_Z - M3_BOLT_LENGTH

    # Head
    head = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_BOTTOM_Z)
        .center(bx, by)
        .circle(M3_HEAD_DIA / 2)
        .extrude(M3_HEAD_H)
    )
    # Shaft
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=SHAFT_BOTTOM_Z)
        .center(bx, by)
        .circle(M3_SHAFT_DIA / 2)
        .extrude(M3_BOLT_LENGTH)
    )
    bolt = head.union(shaft)
    if bolts is None:
        bolts = bolt
    else:
        bolts = bolts.union(bolt)

# ============================================================
# INTERFERENCE CHECK (assembled position)
# ============================================================
import os

# Create assembled versions (lid sits on pillar tops, not body rim)
ASSEMBLED_LID_Z = PILLAR_TOP_Z  # lid bottom rests on pillar tops
lid_assembled = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z)
    .rect(FLANGE_L, FLANGE_W)
    .extrude(LID_THICKNESS)
)
lip_assembled_outer = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z)
    .rect(LIP_L, LIP_W)
    .extrude(-LID_LIP_DEPTH)
)
lip_assembled_cut = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z + 1)
    .rect(LIP_L - 2 * LIP_WALL, LIP_W - 2 * LIP_WALL)
    .extrude(-(LID_LIP_DEPTH + 2))
)
lid_assembled = lid_assembled.union(lip_assembled_outer.cut(lip_assembled_cut))
for bx, by in LID_BOLT_POSITIONS:
    bh = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-(LID_THICKNESS + 2))
    )
    lid_assembled = lid_assembled.cut(bh)
    cb = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_HEAD_DIA / 2)
        .extrude(-(BOLT_HEAD_DEPTH + 1))
    )
    lid_assembled = lid_assembled.cut(cb)
for fx, fy in BULKHEAD_POSITIONS:
    fh = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z - 1)
        .center(fx, fy)
        .circle(FLANGE_HOLE_DIA / 2)
        .extrude(LID_THICKNESS + 2)
    )
    lid_assembled = lid_assembled.cut(fh)

print("=" * 60)
print("INTERFERENCE CHECK (assembled position)")
print("=" * 60)

# Check bolt-to-base interference
bolt_base_int = bolts.intersect(base)
vol_bb = bolt_base_int.val().Volume() if bolt_base_int.val().Volume() > 0.001 else 0
print(f"Bolt ↔ Base:   {'INTERFERENCE' if vol_bb > 0 else 'CLEAR'} ({vol_bb:.2f} mm³)")

# Check bolt-to-lid interference (assembled)
bolt_lid_int = bolts.intersect(lid_assembled)
vol_bl = bolt_lid_int.val().Volume() if bolt_lid_int.val().Volume() > 0.001 else 0
print(f"Bolt ↔ Lid:    {'INTERFERENCE' if vol_bl > 0 else 'CLEAR'} ({vol_bl:.2f} mm³)")

# Check bolt-to-gasket interference
bolt_gasket_int = bolts.intersect(gasket)
vol_bg = bolt_gasket_int.val().Volume() if bolt_gasket_int.val().Volume() > 0.001 else 0
print(f"Bolt ↔ Gasket: {'INTERFERENCE' if vol_bg > 0 else 'CLEAR'} ({vol_bg:.2f} mm³)")

# Check lid-to-base interference (assembled, excluding gasket crush zone)
lid_base_int = lid_assembled.intersect(base)
vol_lb = lid_base_int.val().Volume() if lid_base_int.val().Volume() > 0.001 else 0
print(f"Lid ↔ Base:    {'INTERFERENCE' if vol_lb > 0 else 'CLEAR'} ({vol_lb:.2f} mm³)")

# Check lid-to-gasket interference (expected — gasket proud zone)
lid_gasket_int = lid_assembled.intersect(gasket)
vol_lg = lid_gasket_int.val().Volume() if lid_gasket_int.val().Volume() > 0.001 else 0
no_seal_msg = "NO CONTACT — GASKET WON'T SEAL!"
print(f"Lid ↔ Gasket:  {'EXPECTED CONTACT' if vol_lg > 0 else no_seal_msg} ({vol_lg:.2f} mm³)")

# Check gasket-to-base interference (expected — gasket sits in groove)
gasket_base_int = gasket.intersect(base)
vol_gb = gasket_base_int.val().Volume() if gasket_base_int.val().Volume() > 0.001 else 0
print(f"Gasket ↔ Base: {'EXPECTED OVERLAP (groove)' if vol_gb > 0 else 'NO OVERLAP — GASKET FLOATING!'} ({vol_gb:.2f} mm³)")

print()

# Bolt reach analysis
ASSEMBLED_LID_TOP_Z = PILLAR_TOP_Z + LID_THICKNESS
HEAD_BOTTOM = ASSEMBLED_LID_TOP_Z - M3_HEAD_H
SHAFT_TIP = HEAD_BOTTOM - M3_BOLT_LENGTH
INSERT_BOTTOM = PILLAR_TOP_Z - INSERT_DEPTH
LID_BOTTOM_ASSEMBLED = PILLAR_TOP_Z

print("Bolt Reach Analysis (per bolt):")
print(f"  Bolt head top:     Z = {ASSEMBLED_LID_TOP_Z:.1f} mm (flush with lid top)")
print(f"  Bolt head bottom:  Z = {HEAD_BOTTOM:.1f} mm")
print(f"  Counterbore depth: {BOLT_HEAD_DEPTH:.1f} mm (head height {M3_HEAD_H:.1f} mm) → {'OK head recessed' if BOLT_HEAD_DEPTH >= M3_HEAD_H else 'WARNING: head protrudes ' + str(M3_HEAD_H - BOLT_HEAD_DEPTH) + 'mm!'}")
print(f"  Lid bottom:        Z = {LID_BOTTOM_ASSEMBLED:.1f} mm (on pillar tops)")
print(f"  Shaft in lid:      {HEAD_BOTTOM - LID_BOTTOM_ASSEMBLED:.1f} mm (through {LID_THICKNESS - BOLT_HEAD_DEPTH:.1f} mm lid material)")
print(f"  Pillar top:        Z = {PILLAR_TOP_Z:.1f} mm ({PILLAR_STANDOFF:.1f} mm above body rim)")
print(f"  Body rim:          Z = {TOTAL_BASE_H:.1f} mm (gasket crush gap: {PILLAR_STANDOFF:.1f} mm)")
print(f"  Insert pocket:     Z = {INSERT_BOTTOM:.1f} to {PILLAR_TOP_Z:.1f} mm ({INSERT_DEPTH:.1f} mm deep)")
print(f"  Shaft tip:         Z = {SHAFT_TIP:.1f} mm")
print(f"  Shaft into insert: {PILLAR_TOP_Z - max(SHAFT_TIP, INSERT_BOTTOM):.1f} mm thread engagement")
print(f"  Shaft past insert: {'NONE — OK' if SHAFT_TIP >= INSERT_BOTTOM else f'{INSERT_BOTTOM - SHAFT_TIP:.1f} mm — BOTTOMS OUT!'}")
print()

# Clearance analysis
for i, (bx, by) in enumerate(LID_BOLT_POSITIONS):
    dist_to_body_l = abs(bx) - EXT_L / 2
    dist_to_body_w = abs(by) - EXT_W / 2
    min_dist = min(dist_to_body_l, dist_to_body_w)
    wall_clearance = min_dist - BOSS_OD / 2
    print(f"  Bolt {i+1} ({bx:+.1f}, {by:+.1f}): {min_dist:.1f} mm from body wall, pillar edge {wall_clearance:.1f} mm from wall")

print()

# Material around insert
FLANGE_AT_BOLT = FLANGE_THICK  # flange is solid at bolt position
PILLAR_WALL = (BOSS_OD - INSERT_DIA) / 2
print(f"  Pillar wall around insert: {PILLAR_WALL:.1f} mm")
print(f"  Min printable wall: 1.2 mm → {'OK' if PILLAR_WALL >= 1.2 else 'TOO THIN!'}")

# Check bulkhead vs bolt position interference
print()
print("Bulkhead ↔ Bolt Position Check:")
for i, (fx, fy) in enumerate(BULKHEAD_POSITIONS):
    for j, (bx, by) in enumerate(LID_BOLT_POSITIONS):
        dist = ((fx - bx)**2 + (fy - by)**2) ** 0.5
        min_clear = (FLANGE_HOLE_DIA + BOSS_OD) / 2 + 1.0  # 1mm min between
        if dist < min_clear:
            print(f"  WARNING: Bulkhead {i+1} ↔ Bolt {j+1}: {dist:.1f} mm (need {min_clear:.1f} mm)")
        else:
            print(f"  Bulkhead {i+1} ↔ Bolt {j+1}: {dist:.1f} mm — OK")

print()
print("=" * 60)

# ============================================================
# EXPORT
# ============================================================
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
cq.exporters.export(base, os.path.join(OUT_DIR, "pizero_housing_base.stl"))
cq.exporters.export(lid, os.path.join(OUT_DIR, "pizero_housing_lid.stl"))
cq.exporters.export(gasket, os.path.join(OUT_DIR, "pizero_housing_gasket.stl"))
cq.exporters.export(bolts, os.path.join(OUT_DIR, "pizero_housing_bolts.stl"))

print()
print(f"Base:    {FLANGE_L:.1f} × {FLANGE_W:.1f} × {TOTAL_BASE_H:.1f} mm")
print(f"Body:    {EXT_L:.1f} × {EXT_W:.1f} × {BODY_H:.1f} mm")
print(f"Lid:     {FLANGE_L:.1f} × {FLANGE_W:.1f} × {LID_THICKNESS:.1f} mm (full flange)")
print(f"Cavity:  {CAVITY_L:.1f} × {CAVITY_W:.1f} × {CAVITY_DEPTH:.1f} mm")
print(f"Wall:    {WALL:.1f}mm  |  Corner R: {CORNER_RADIUS:.1f}mm")
print(f"Pillars: {BOSS_OD:.1f}mm OD × {PILLAR_H:.1f}mm tall (4× external, {PILLAR_STANDOFF:.1f}mm above rim as crush limiters)")
print()
print("Exported: pizero_housing_base.stl, pizero_housing_lid.stl,")
print("          pizero_housing_gasket.stl, pizero_housing_bolts.stl")
print()
print("(bolts.stl is for visualization only — do not print)")
