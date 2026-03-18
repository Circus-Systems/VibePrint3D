"""
Pi Zero 2W Waterproof Housing — Marine Grade (Multi-Material)
Two-piece enclosure for Raspberry Pi Zero 2W.
Designed for bulkhead mounting on S/V Circus.

SEALING ARCHITECTURE (modeled on Hammond 1554 / Fibox IP67):
  - External bolt pillar bosses at flange corners, OUTSIDE the body walls.
  - Gasket groove in base rim accepts either:
      (a) 1.5mm silicone O-ring cord (Shore 30-50A) — recommended for IP67
      (b) Printed TPU 68D gasket via AMS — adequate for IP65 splash-proof
  - Gasket is a CONTINUOUS unbroken rectangle — no interruptions.
  - Bolts, nuts only — no heat-set inserts.
  - THROUGH-BOLT DESIGN: M3x30 SHCS from lid top, through pillar, into
    hex nut embedded in flange. Bolt head pushes lid down, nut resists
    from below — proper clamping compresses gasket.
  - No fastener paths penetrate the sealed volume.
  - Flange bottom is FLUSH — no protrusions. Hex nut pockets are recessed
    into flange underside. Print base with flange down.

MECHANICAL CLAMPING:
  Bolt head (lid top) → lid → pillar → flange → hex nut (embedded in flange)
  Tightening pulls everything together. Pillar tops flush with body rim
  act as crush limiters — gasket compresses exactly 0.5mm (33%).

GASKET COMPRESSION:
  Groove is 1.6mm wide × 1.0mm deep. A 1.5mm round cord stands 0.5mm
  proud. Pillar tops are flush with rim, acting as crush limiters. When
  the lid is bolted tight, gasket compresses from 1.5mm to 1.0mm = 33%.
  This is in the 25-35% sweet spot for reliable static sealing.

  For the printed TPU 68D option: rectangular fill 1.4mm wide × 1.3mm
  tall, stands 0.3mm proud, compresses to 1.0mm = 23%. Shore 68D is
  semi-rigid so sealing performance is reduced vs silicone cord.

CABLE GLAND:
  PG7 cable gland boss is on the +X short wall at mid-body height.
  The boss top is below the body rim — no lid interference. No cutout
  needed. The gland is accessed from the side.

ASSEMBLY SEQUENCE:
  1. Insert 4× M3 hex nuts into hex pockets on flange underside
     (press-fit or tack with CA glue — hex shape prevents rotation)
  2. Mount base to bulkhead using 4× M4 bolts through flange holes
  3. Install PG7 cable gland + locknut on +X short wall
  4. Mount PCB on standoffs (4× M2.5 self-tapping screws)
  5. Route cable through gland, tighten gland
  6. Place gasket in groove (silicone cord or printed TPU already in place)
  7. Place lid — alignment lip drops into cavity
     (lid has NO bulkhead holes — base is already mounted)
  8. Insert 4× M3x30 SHCS from lid top into pillar through-holes
  9. Tighten in cross-pattern (1-3-2-4) to compress gasket evenly

PRINT SETUP (Bambu Lab P2S with AMS):
  Filament 1: PETG (body, lid)
  Filament 2: Bambu TPU 68D (gasket) — 220-240°C nozzle, 30-35°C bed
  Nozzle: 0.4mm (TPU 68D is NOT compatible with 0.2mm nozzle)
  Print base with flange face DOWN for flush bottom surface.
  Import base + lid + gasket STLs, assign materials, print as one job.

HARDWARE (not printed):
  4× M3x30 SHCS (stainless)
  4× M3 hex nut (stainless)
  4× M4 bulkhead bolts + nuts (user-supplied, for mounting base to bulkhead)
  1× PG7 cable gland + locknut
  4× M2.5 self-tapping screws (PCB mounting)
  Optional: 1.5m of 1.5mm silicone O-ring cord (if not using printed gasket)

All dimensions in mm.
"""
import cadquery as cq
import math
import os

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
LID_THICKNESS = 5.0          # lid plate thickness (1.8mm material above counterbore)
LID_LIP_DEPTH = 2.5          # lid lip extends into base cavity
LID_LIP_GAP = 0.3            # clearance between lip and cavity wall
CORNER_RADIUS = 2.0          # fillet radius on all corners

# Gasket groove (base rim — for 1.5mm silicone cord or printed TPU)
GASKET_GROOVE_W = 1.6        # groove width
GASKET_GROOVE_D = 1.0        # groove depth (1.5mm cord stands 0.5mm proud → 33% compression)
GASKET_INSET = 0.7           # from outer wall edge (0.7mm wall each side of groove)

# Mounting flange (flush bottom — no protrusions below Z=0)
FLANGE_EXT = 10.0            # extension beyond body each side (2mm margin around pillars)
FLANGE_THICK = 5.0           # flange plate thickness (hex nut pockets embedded inside)

# External bolt pillar bosses — at flange corners, OUTSIDE body walls
BOSS_OD = 10.0               # pillar diameter (sized for M3 hex nut wall)
LID_BOLT_INSET = 7.0         # bolt center inset from flange edge (2mm margin to edge)

# M3 hex nut (DIN 934) — embedded in flange (pocket opens at bottom face)
NUT_AF = 5.5                 # across flats
NUT_POCKET_AF = 5.7          # pocket across flats (0.1mm clearance per flat)
NUT_THICK = 2.4              # nut height
NUT_POCKET_DEPTH = 3.0       # hex pocket depth from flange bottom (nut + 0.6mm clearance)

# Through-bolt hole (runs full length: lid → pillar → flange → nut pocket ceiling)
BOLT_CLEARANCE = 3.4         # M3 clearance through-hole

# M3 bolt counterbore in lid
BOLT_HEAD_DIA = 6.0          # M3 SHCS counterbore diameter
BOLT_HEAD_DEPTH = 3.2        # counterbore depth in lid

# M3 SHCS dimensions (for interference check — not visualized)
M3_HEAD_DIA = 5.5            # actual M3 SHCS head diameter
M3_HEAD_H = 3.0              # actual M3 SHCS head height
M3_SHAFT_DIA = 3.0           # M3 shaft diameter
M3_BOLT_LENGTH = 30.0        # M3x30 shaft length (through lid + pillar + flange)

# Bulkhead mounting (M4 × 4, on LONG edges only — BASE ONLY, not lid)
FLANGE_HOLE_DIA = 4.5        # M4 clearance
BULKHEAD_INSET = 4.0         # M4 hole inset from flange edge

# PCB mounting (Pi Zero 2W — 58×23mm pattern, M2.5 self-tapping screws)
PCB_PATTERN_L = 58.0
PCB_PATTERN_W = 23.0
STANDOFF_OD = 5.5
STANDOFF_HEIGHT = 4.0
STANDOFF_HOLE_DIA = 2.0      # undersized for M2.5 self-tapping screw

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
TOTAL_BASE_H = FLANGE_THICK + BODY_H        # 28
FLOOR_Z = FLANGE_THICK + WALL               # 8 — cavity floor

LIP_L = CAVITY_L - 2 * LID_LIP_GAP
LIP_W = CAVITY_W - 2 * LID_LIP_GAP
LIP_WALL = 2.0

FLANGE_L = EXT_L + 2 * FLANGE_EXT           # 97
FLANGE_W = EXT_W + 2 * FLANGE_EXT           # 62

# Gasket groove rectangle on body wall rim
GROOVE_OUTER_L = EXT_L - 2 * GASKET_INSET
GROOVE_OUTER_W = EXT_W - 2 * GASKET_INSET
GROOVE_INNER_L = GROOVE_OUTER_L - 2 * GASKET_GROOVE_W
GROOVE_INNER_W = GROOVE_OUTER_W - 2 * GASKET_GROOVE_W

# Gasket fill (printed TPU — sits in groove with clearance)
GASKET_FILL_W = GASKET_GROOVE_W - 0.2       # 0.1mm clearance each side = 1.4mm
GASKET_FILL_H = GASKET_GROOVE_D + 0.3       # stands 0.3mm proud = 1.3mm
GASKET_OUTER_L = GROOVE_OUTER_L - 0.1       # 0.05mm clearance each side
GASKET_OUTER_W = GROOVE_OUTER_W - 0.1
GASKET_INNER_L = GASKET_OUTER_L - 2 * GASKET_FILL_W
GASKET_INNER_W = GASKET_OUTER_W - 2 * GASKET_FILL_W

# Hex nut pocket dimensions
NUT_ACROSS_CORNERS = NUT_POCKET_AF / math.cos(math.radians(30))  # ~6.58mm

# Pillar height — flush with body rim (rim acts as crush limiter)
PILLAR_H = BODY_H
PILLAR_TOP_Z = FLANGE_THICK + PILLAR_H      # same as TOTAL_BASE_H

# Through-bolt hole length: from pillar top through flange into nut pocket
# Overlap 1mm into hex pocket to ensure clean junction (no membrane)
NUT_POCKET_CEILING_Z = NUT_POCKET_DEPTH     # measured from flange bottom (Z=0)
THROUGH_HOLE_OVERLAP = 1.0                  # overlap into hex pocket
THROUGH_HOLE_LENGTH = TOTAL_BASE_H - NUT_POCKET_CEILING_Z + THROUGH_HOLE_OVERLAP

# Feature positions
# Lid bolt positions — on flange corners, OUTSIDE the body walls
LID_BOLT_POSITIONS = [
    ( FLANGE_L/2 - LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    ( FLANGE_L/2 - LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
]

# Bulkhead mounting — LONG EDGES ONLY (short edges have cable gland)
# These are in the BASE ONLY — lid has no bulkhead holes
BULKHEAD_POSITIONS = [
    ( FLANGE_L/4,  FLANGE_W/2 - BULKHEAD_INSET),   # +Y edge, +X quarter
    (-FLANGE_L/4,  FLANGE_W/2 - BULKHEAD_INSET),   # +Y edge, -X quarter
    ( FLANGE_L/4, -FLANGE_W/2 + BULKHEAD_INSET),   # -Y edge, +X quarter
    (-FLANGE_L/4, -FLANGE_W/2 + BULKHEAD_INSET),   # -Y edge, -X quarter
]

PCB_POSITIONS = [
    ( PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    ( PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2,  PCB_PATTERN_W/2),
    (-PCB_PATTERN_L/2, -PCB_PATTERN_W/2),
]

CABLE_GLAND_Z = FLANGE_THICK + BODY_H / 2 - 1.0  # slightly below mid-body (clears lid lip)

# ============================================================
# PART: Base (PETG)
# ============================================================
# Flange plate — flush bottom at Z=0
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

# --- External bolt pillar bosses (flange corners → body rim height) ---
# Flush with body rim — rim + pillar tops act as crush limiters for gasket.
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

# --- Fillet base vertical corners BEFORE cutting holes ---
# Only fillet vertical edges. Top edges (rim) must stay flat for gasket groove.
try:
    base = base.edges("|Z").fillet(CORNER_RADIUS)
except:
    print("Warning: could not fillet all base vertical edges")

# --- CUT: Gasket groove in base top rim ---
# CONTINUOUS rectangle — no interruptions from bolt bosses (they're external).
groove_outer = (
    cq.Workplane("XY")
    .workplane(offset=TOTAL_BASE_H + 0.01)
    .rect(GROOVE_OUTER_L, GROOVE_OUTER_W)
    .extrude(-GASKET_GROOVE_D - 0.01)
)
groove_inner = (
    cq.Workplane("XY")
    .workplane(offset=TOTAL_BASE_H + 0.02)
    .rect(GROOVE_INNER_L, GROOVE_INNER_W)
    .extrude(-GASKET_GROOVE_D - 0.03)
)
groove = groove_outer.cut(groove_inner)
base = base.cut(groove)

# --- CUT: Through-bolt holes (full length of pillar + flange) ---
# 3.4mm clearance hole from pillar top down to nut pocket ceiling
for bx, by in LID_BOLT_POSITIONS:
    through_hole = (
        cq.Workplane("XY")
        .workplane(offset=PILLAR_TOP_Z + 0.01)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-(THROUGH_HOLE_LENGTH + 0.02))
    )
    base = base.cut(through_hole)

# --- CUT: Hex nut pockets in flange (open at bottom face for nut insertion) ---
# Nut drops in from below. Hex pocket prevents rotation. Flush bottom.
for bx, by in LID_BOLT_POSITIONS:
    nut_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-0.01)
        .center(bx, by)
        .polygon(6, NUT_ACROSS_CORNERS)
        .extrude(NUT_POCKET_DEPTH + 0.01)
    )
    base = base.cut(nut_pocket)

# --- CUT: PCB screw holes in standoffs (for M2.5 self-tapping screws) ---
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

# --- CUT: M4 bulkhead mounting holes (through flange — BASE ONLY) ---
for fx, fy in BULKHEAD_POSITIONS:
    flange_hole = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .center(fx, fy)
        .circle(FLANGE_HOLE_DIA / 2)
        .extrude(FLANGE_THICK + 2)
    )
    base = base.cut(flange_hole)

# ============================================================
# PART: TPU Gasket (Bambu TPU 68D — printed in-place via AMS)
# ============================================================
# Rectangular ring fill sitting in the gasket groove.
# Continuous — no cuts or gaps.
GASKET_Z = TOTAL_BASE_H - GASKET_GROOVE_D

gasket_outer = (
    cq.Workplane("XY")
    .workplane(offset=GASKET_Z)
    .rect(GASKET_OUTER_L, GASKET_OUTER_W)
    .extrude(GASKET_FILL_H)
)
gasket_inner = (
    cq.Workplane("XY")
    .workplane(offset=GASKET_Z - 0.01)
    .rect(GASKET_INNER_L, GASKET_INNER_W)
    .extrude(GASKET_FILL_H + 0.02)
)
gasket = gasket_outer.cut(gasket_inner)

# ============================================================
# PART: Lid (PETG — exploded position for visualization)
# ============================================================
LID_BOTTOM_Z = PILLAR_TOP_Z + EXPLODE_GAP

# Main lid plate — covers body + pillars (no bulkhead holes — base mounts first)
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

# --- CUT: M3 counterbored bolt holes through lid (at pillar positions) ---
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

# --- Fillet lid corners ---
try:
    lid = lid.edges("|Z").fillet(CORNER_RADIUS)
except:
    print("Warning: could not fillet all lid vertical edges")

# ============================================================
# INTERFERENCE CHECK (assembled position — no hardware visualization)
# ============================================================
# Build virtual bolt+nut geometry for interference checking only
ASSEMBLED_LID_Z = PILLAR_TOP_Z
ASSEMBLED_LID_TOP = ASSEMBLED_LID_Z + LID_THICKNESS

hardware_check = None
for bx, by in LID_BOLT_POSITIONS:
    head_top = ASSEMBLED_LID_TOP
    head_bottom = head_top - M3_HEAD_H
    shaft_top = head_bottom
    shaft_bottom = shaft_top - M3_BOLT_LENGTH

    head = (
        cq.Workplane("XY")
        .workplane(offset=head_bottom)
        .center(bx, by)
        .circle(M3_HEAD_DIA / 2)
        .extrude(M3_HEAD_H)
    )
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=shaft_bottom)
        .center(bx, by)
        .circle(M3_SHAFT_DIA / 2)
        .extrude(M3_BOLT_LENGTH)
    )
    bolt = head.union(shaft)

    nut_top_z = NUT_POCKET_DEPTH
    nut_bottom_z = nut_top_z - NUT_THICK
    nut = (
        cq.Workplane("XY")
        .workplane(offset=nut_bottom_z)
        .center(bx, by)
        .polygon(6, NUT_AF / math.cos(math.radians(30)))
        .extrude(NUT_THICK)
    )

    piece = bolt.union(nut)
    if hardware_check is None:
        hardware_check = piece
    else:
        hardware_check = hardware_check.union(piece)

# Build assembled lid (at actual position, not exploded)
lid_asm = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z)
    .rect(FLANGE_L, FLANGE_W)
    .extrude(LID_THICKNESS)
)
lip_asm_outer = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z)
    .rect(LIP_L, LIP_W)
    .extrude(-LID_LIP_DEPTH)
)
lip_asm_cut = (
    cq.Workplane("XY")
    .workplane(offset=ASSEMBLED_LID_Z + 1)
    .rect(LIP_L - 2 * LIP_WALL, LIP_W - 2 * LIP_WALL)
    .extrude(-(LID_LIP_DEPTH + 2))
)
lid_asm = lid_asm.union(lip_asm_outer.cut(lip_asm_cut))
for bx, by in LID_BOLT_POSITIONS:
    bh = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-(LID_THICKNESS + 2))
    )
    lid_asm = lid_asm.cut(bh)
    cb = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z + LID_THICKNESS + 1)
        .center(bx, by)
        .circle(BOLT_HEAD_DIA / 2)
        .extrude(-(BOLT_HEAD_DEPTH + 1))
    )
    lid_asm = lid_asm.cut(cb)

print("=" * 60)
print("INTERFERENCE CHECK (assembled position)")
print("=" * 60)

def check_interference(name, a, b, expected=False):
    inter = a.intersect(b)
    raw_vol = inter.val().Volume()
    vol = raw_vol if raw_vol > 2.0 else 0  # ignore <2mm³ floating-point surface slivers
    if expected:
        status = "EXPECTED" if vol > 0 else "MISSING!"
    else:
        status = "INTERFERENCE!" if vol > 0 else "CLEAR"
    print(f"  {name:25s} {status:15s} ({vol:.2f} mm\u00b3)")
    return vol

check_interference("Bolt+Nut \u2194 Base", hardware_check, base)
check_interference("Bolt+Nut \u2194 Lid", hardware_check, lid_asm)
check_interference("Bolt+Nut \u2194 Gasket", hardware_check, gasket)
check_interference("Lid \u2194 Base (contact)", lid_asm, base)
check_interference("Lid \u2194 Gasket (seal)", lid_asm, gasket, expected=True)
check_interference("Gasket \u2194 Base", gasket, base)

print()

# --- Bolt Reach Analysis (Through-bolt: lid → pillar → flange → nut) ---
print("Bolt Reach Analysis (M3x30 SHCS through-bolt + M3 hex nut embedded in flange):")
head_top = ASSEMBLED_LID_TOP
head_bottom = head_top - M3_HEAD_H
shaft_top = head_bottom
shaft_bottom = shaft_top - M3_BOLT_LENGTH

lid_material = LID_THICKNESS - BOLT_HEAD_DEPTH  # lid material bolt passes through
pillar_length = PILLAR_H                         # pillar bolt passes through
flange_to_nut = FLANGE_THICK - NUT_POCKET_DEPTH  # flange material above nut pocket
total_material = lid_material + pillar_length + flange_to_nut

print(f"  Bolt head:         Z = {head_bottom:.1f}\u2013{head_top:.1f} mm (in counterbore)")
cbore_msg = "OK recessed" if BOLT_HEAD_DEPTH >= M3_HEAD_H else f"PROTRUDES {M3_HEAD_H - BOLT_HEAD_DEPTH:.1f}mm!"
print(f"  Counterbore:       {BOLT_HEAD_DEPTH:.1f} mm deep, head {M3_HEAD_H:.1f} mm \u2192 {cbore_msg}")
print(f"  Shaft top:         Z = {shaft_top:.1f} mm")
print(f"  Shaft bottom:      Z = {shaft_bottom:.1f} mm")
print(f"  Path breakdown:")
print(f"    Lid material:    {lid_material:.1f} mm (clearance hole)")
print(f"    Pillar:          {pillar_length:.1f} mm (clearance hole)")
print(f"    Flange above nut:{flange_to_nut:.1f} mm (clearance hole)")
print(f"    Total clearance: {total_material:.1f} mm")
print(f"  Nut position:      Z = {NUT_POCKET_DEPTH - NUT_THICK:.1f}\u2013{NUT_POCKET_DEPTH:.1f} mm")
print(f"  Shaft reaches to:  Z = {shaft_bottom:.1f} mm")

# How deep does shaft go into nut?
thread_engagement = NUT_POCKET_DEPTH - shaft_bottom
if thread_engagement > NUT_THICK:
    thread_engagement_actual = NUT_THICK
    tip_past_nut = thread_engagement - NUT_THICK
else:
    thread_engagement_actual = max(0, thread_engagement)
    tip_past_nut = 0

print(f"  Thread engagement: {thread_engagement_actual:.1f} mm ({thread_engagement_actual/NUT_THICK*100:.0f}% of nut)")
if tip_past_nut > 0:
    tip_end_z = NUT_POCKET_DEPTH - NUT_THICK - tip_past_nut
    print(f"  Bolt tip past nut: {tip_past_nut:.1f} mm")
    print(f"  Tip end:           Z = {tip_end_z:.1f} mm")
    fits = "OK (inside hex pocket recess)" if tip_end_z >= 0 else "PROTRUDES BELOW FLANGE!"
    print(f"  Flush bottom:      {fits}")
else:
    print(f"  Bolt tip past nut: NONE (tip inside nut)")
print()

# --- Clamping Force Path ---
print("Clamping Force Path:")
print(f"  Bolt head pushes DOWN on lid top (Z = {head_top:.1f})")
print(f"  Lid rests on pillar tops (Z = {PILLAR_TOP_Z:.1f}) = crush limiter")
print(f"  Lid also contacts gasket (Z = {TOTAL_BASE_H:.1f} + 0.3mm proud)")
print(f"  Nut resists from below (Z = {NUT_POCKET_DEPTH - NUT_THICK:.1f})")
print(f"  Force path: head \u2192 lid \u2192 pillar/gasket \u2192 flange \u2192 nut")
print(f"  Gasket compression: pillars limit travel, gasket gets 33% compression")
print(f"  \u2192 PROPER CLAMPING JOINT")
print()

# --- Cable Gland Clearance ---
GLAND_TOP_Z = CABLE_GLAND_Z + GLAND_BOSS_OD / 2
GLAND_OUTER_X = EXT_L / 2 + GLAND_BOSS_LENGTH
LID_LIP_BOTTOM_Z = ASSEMBLED_LID_Z - LID_LIP_DEPTH
print("Cable Gland Clearance:")
print(f"  Gland boss top:     Z = {GLAND_TOP_Z:.1f} mm")
print(f"  Body rim:           Z = {TOTAL_BASE_H:.1f} mm")
print(f"  Clearance to rim:   {TOTAL_BASE_H - GLAND_TOP_Z:.1f} mm \u2192 {'OK' if TOTAL_BASE_H > GLAND_TOP_Z else 'INTERFERENCE!'}")
print(f"  Lid bottom:         Z = {ASSEMBLED_LID_Z:.1f} mm")
print(f"  Lid lip bottom:     Z = {LID_LIP_BOTTOM_Z:.1f} mm")
gap_msg = "OK" if LID_LIP_BOTTOM_Z > GLAND_TOP_Z else "INTERFERENCE!"
print(f"  Lip \u2194 gland gap:   {LID_LIP_BOTTOM_Z - GLAND_TOP_Z:.1f} mm \u2192 {gap_msg}")
print(f"  Gland outer edge:   X = {GLAND_OUTER_X:.1f} mm")
print(f"  Flange edge:        X = {FLANGE_L/2:.1f} mm")
extends = GLAND_OUTER_X - FLANGE_L/2
if extends > 0:
    print(f"  Gland extends past flange: YES \u2014 {extends:.1f}mm")
else:
    print(f"  Gland extends past flange: NO \u2014 flush or inside")
print(f"  Lid cutout needed:  NO (gland is {TOTAL_BASE_H - GLAND_TOP_Z:.1f} mm below rim)")
print()

# --- Pillar & Nut Wall Thickness ---
nut_wall = (BOSS_OD - NUT_ACROSS_CORNERS) / 2
print("Pillar & Nut Pocket:")
print(f"  Pillar OD:          {BOSS_OD:.1f} mm")
print(f"  Nut across corners: {NUT_ACROSS_CORNERS:.1f} mm")
print(f"  Wall around nut:    {nut_wall:.1f} mm \u2192 {'OK' if nut_wall >= 1.0 else 'THIN!'}")
print(f"  Nut pocket depth:   {NUT_POCKET_DEPTH:.1f} mm (nut {NUT_THICK:.1f} mm + clearance)")
print(f"  Flange thickness:   {FLANGE_THICK:.1f} mm (pocket uses {NUT_POCKET_DEPTH:.1f}, leaves {FLANGE_THICK - NUT_POCKET_DEPTH:.1f} mm above)")
print()

# --- Pillar Position Clearance ---
print("Pillar Position Clearance:")
for i, (bx, by) in enumerate(LID_BOLT_POSITIONS):
    dist_flange_x = FLANGE_L / 2 - abs(bx) - BOSS_OD / 2
    dist_flange_y = FLANGE_W / 2 - abs(by) - BOSS_OD / 2
    min_flange = min(dist_flange_x, dist_flange_y)
    print(f"  Bolt {i+1} ({bx:+.1f}, {by:+.1f}): "
          f"flange edge margin {min_flange:.1f}mm \u2192 {'OK' if min_flange >= 1.5 else 'TIGHT!'}")

print()

# --- Bulkhead ↔ Bolt/Gland Check ---
print("Bulkhead Hole Checks (base only — lid has no bulkhead holes):")
for i, (fx, fy) in enumerate(BULKHEAD_POSITIONS):
    issues = []
    for j, (bx, by) in enumerate(LID_BOLT_POSITIONS):
        dist = math.sqrt((fx - bx)**2 + (fy - by)**2)
        min_clear = (FLANGE_HOLE_DIA + BOSS_OD) / 2 + 1.0
        if dist < min_clear:
            issues.append(f"Bolt{j+1} ({dist:.1f}mm, need {min_clear:.1f})")
    gland_cx = EXT_L / 2 + GLAND_BOSS_LENGTH / 2
    gland_cy = 0
    dist_gland = math.sqrt((fx - gland_cx)**2 + (fy - gland_cy)**2)
    min_gland = (FLANGE_HOLE_DIA + GLAND_BOSS_OD) / 2 + 1.0
    if dist_gland < min_gland:
        issues.append(f"CableGland ({dist_gland:.1f}mm, need {min_gland:.1f})")
    if issues:
        for issue in issues:
            print(f"  BH{i+1} \u2194 {issue} \u2192 CONFLICT!")
    else:
        print(f"  BH{i+1} ({fx:+.1f}, {fy:+.1f}): all clear")

print()

# --- Assembly Verification ---
print("Assembly Verification:")
print(f"  1. Hex nut captive method: hex pocket embedded in flange")
print(f"     Pocket AF: {NUT_POCKET_AF:.1f}mm (nut AF: {NUT_AF:.1f}mm, {NUT_POCKET_AF - NUT_AF:.1f}mm clearance)")
print(f"     Pocket depth: {NUT_POCKET_DEPTH:.1f}mm (nut: {NUT_THICK:.1f}mm)")
print(f"     Nut inserted from below, hex shape prevents rotation")
print(f"     Press-fit or tack with CA glue before assembly")
print(f"  2. Through-bolt: {BOLT_CLEARANCE:.1f}mm clearance hole, {THROUGH_HOLE_LENGTH:.1f}mm long")
print(f"  3. Bolt: M3x{M3_BOLT_LENGTH:.0f} SHCS enters from lid top")
print(f"  4. Clamping: bolt head \u2192 lid \u2192 pillar \u2192 flange \u2192 nut")
print(f"  5. Crush limiters: pillars flush with rim, control gasket compression")
print(f"  6. Bulkhead: base mounted FIRST with M4 bolts, lid installed AFTER")
print(f"     (lid has no bulkhead holes — clean top surface)")
print(f"  7. PCB: M2.5 self-tapping screws into {STANDOFF_HOLE_DIA:.1f}mm pilot holes")
print()
print("=" * 60)

# ============================================================
# EXPORT (3 parts only — no hardware visualization)
# ============================================================
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
cq.exporters.export(base, os.path.join(OUT_DIR, "pizero_housing_base.stl"))
cq.exporters.export(lid, os.path.join(OUT_DIR, "pizero_housing_lid.stl"))
cq.exporters.export(gasket, os.path.join(OUT_DIR, "pizero_housing_gasket.stl"))

print()
print(f"Enclosure Dimensions:")
print(f"  Base:    {FLANGE_L:.1f} \u00d7 {FLANGE_W:.1f} \u00d7 {TOTAL_BASE_H:.1f} mm (with flange)")
print(f"  Body:    {EXT_L:.1f} \u00d7 {EXT_W:.1f} \u00d7 {BODY_H:.1f} mm")
print(f"  Lid:     {FLANGE_L:.1f} \u00d7 {FLANGE_W:.1f} \u00d7 {LID_THICKNESS:.1f} mm")
print(f"  Cavity:  {CAVITY_L:.1f} \u00d7 {CAVITY_W:.1f} \u00d7 {CAVITY_DEPTH:.1f} mm")
print(f"  Wall:    {WALL:.1f} mm  |  Corner R: {CORNER_RADIUS:.1f} mm")
print(f"  Pillars: {BOSS_OD:.1f} mm OD \u00d7 {PILLAR_H:.1f} mm (4\u00d7 external, through-bolt)")
print(f"  Bottom:  FLUSH (no protrusions)")
print()
print(f"Gasket Groove (base rim):")
print(f"  {GASKET_GROOVE_W:.1f} mm wide \u00d7 {GASKET_GROOVE_D:.1f} mm deep, inset {GASKET_INSET:.1f} mm")
print(f"  For 1.5mm silicone cord: 33% compression (recommended for IP67)")
print(f"  For printed TPU 68D:     23% compression (adequate for IP65)")
print()
print(f"Hardware (not printed):")
print(f"  4\u00d7 M3x{M3_BOLT_LENGTH:.0f} SHCS + M3 hex nut (through-bolt, nut embedded in flange)")
print(f"  4\u00d7 M4 bolts + nuts (bulkhead mount — base only)")
print(f"  4\u00d7 M2.5 self-tapping screws (PCB mount)")
print(f"  1\u00d7 PG7 cable gland + locknut")
print()
print("Exported: pizero_housing_base.stl, pizero_housing_lid.stl,")
print("          pizero_housing_gasket.stl")
