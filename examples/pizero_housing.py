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
  - Bolts, nuts, washers only — no heat-set inserts.
  - Hex nut pockets at pillar tops capture M3 nuts; bolts from lid side.
  - No fastener paths penetrate the sealed volume.

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
  The boss top (Z=24.5) is 2.5mm below the body rim (Z=27) — no lid
  interference. No cutout needed. The gland is accessed from the side.

PRINT SETUP (Bambu Lab P2S with AMS):
  Filament 1: PETG (body, lid)
  Filament 2: Bambu TPU 68D (gasket) — 220-240°C nozzle, 30-35°C bed
  Nozzle: 0.4mm (TPU 68D is NOT compatible with 0.2mm nozzle)
  Import base + lid + gasket STLs, assign materials, print as one job.
  Bolts STL is for visualization/interference check only.

HARDWARE (not printed):
  4× M3x6 SHCS (stainless)
  4× M3 hex nut (stainless)
  4× M4 bulkhead bolts + nuts (user-supplied, for mounting to bulkhead)
  1× PG7 cable gland + locknut
  Optional: 1.5m of 1.5mm silicone O-ring cord (if not using printed gasket)

All dimensions in mm.
"""
import cadquery as cq
import math

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

# Gasket groove (base rim — for 1.5mm silicone cord or printed TPU)
GASKET_GROOVE_W = 1.6        # groove width
GASKET_GROOVE_D = 1.0        # groove depth (1.5mm cord stands 0.5mm proud → 33% compression)
GASKET_INSET = 0.7           # from outer wall edge (0.7mm wall each side of groove)

# Mounting flange
FLANGE_EXT = 8.0             # extension beyond body each side
FLANGE_THICK = 4.0           # flange plate thickness

# External bolt pillar bosses — at flange corners, OUTSIDE body walls
BOSS_OD = 10.0               # pillar diameter (sized for M3 hex nut wall)
LID_BOLT_INSET = 5.0         # bolt center inset from flange edge

# M3 hex nut (DIN 934) — captive in pillar top pocket
NUT_AF = 5.5                 # across flats
NUT_POCKET_AF = 5.7          # pocket across flats (0.1mm clearance per flat)
NUT_THICK = 2.4              # nut height
NUT_POCKET_DEPTH = 2.5       # hex pocket depth (nut sits in pocket)
BOLT_TIP_BORE = 3.0          # bore depth below nut for bolt tip clearance

# M3 bolt through lid
BOLT_CLEARANCE = 3.4         # M3 clearance through-hole in lid
BOLT_HEAD_DIA = 6.0          # M3 SHCS counterbore diameter
BOLT_HEAD_DEPTH = 3.2        # counterbore depth in lid

# M3 SHCS dimensions (for visualization & interference check)
M3_HEAD_DIA = 5.5            # actual M3 SHCS head diameter
M3_HEAD_H = 3.0              # actual M3 SHCS head height
M3_SHAFT_DIA = 3.0           # M3 shaft diameter
M3_BOLT_LENGTH = 6.0         # M3x6 shaft length

# Bulkhead mounting (M4 × 4, on LONG edges only — short edges have cable gland)
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

# Feature positions
# Lid bolt positions — on flange corners, OUTSIDE the body walls
LID_BOLT_POSITIONS = [
    ( FLANGE_L/2 - LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    ( FLANGE_L/2 - LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET,  FLANGE_W/2 - LID_BOLT_INSET),
    (-FLANGE_L/2 + LID_BOLT_INSET, -FLANGE_W/2 + LID_BOLT_INSET),
]

# Bulkhead mounting — LONG EDGES ONLY (short edges have cable gland)
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

CABLE_GLAND_Z = FLANGE_THICK + BODY_H / 2   # mid-body height

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

# --- CUT: Hex nut pockets at pillar tops ---
# M3 hex nut sits in pocket. Bolt from lid threads into nut.
# Below nut: cylindrical bore for bolt tip clearance.
for bx, by in LID_BOLT_POSITIONS:
    # Hex pocket for nut
    nut_pocket = (
        cq.Workplane("XY")
        .workplane(offset=PILLAR_TOP_Z + 0.01)
        .center(bx, by)
        .polygon(6, NUT_ACROSS_CORNERS)
        .extrude(-(NUT_POCKET_DEPTH + 0.01))
    )
    base = base.cut(nut_pocket)

    # Cylindrical bore below nut for bolt tip
    tip_bore = (
        cq.Workplane("XY")
        .workplane(offset=PILLAR_TOP_Z - NUT_POCKET_DEPTH)
        .center(bx, by)
        .circle(BOLT_CLEARANCE / 2)
        .extrude(-BOLT_TIP_BORE)
    )
    base = base.cut(tip_bore)

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

# --- CUT: M4 bulkhead mounting holes (through flange only — long edges) ---
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
# PART: Hardware (M3 bolts + nuts — visualization only)
# ============================================================
# Assembled position: lid sits on pillar tops (flush with rim)
ASSEMBLED_LID_Z = PILLAR_TOP_Z
ASSEMBLED_LID_TOP = ASSEMBLED_LID_Z + LID_THICKNESS

hardware = None
for bx, by in LID_BOLT_POSITIONS:
    # --- M3 SHCS Bolt ---
    head_bottom = ASSEMBLED_LID_TOP - M3_HEAD_H
    shaft_bottom = head_bottom - M3_BOLT_LENGTH

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

    # --- M3 Hex Nut (in pocket at pillar top) ---
    nut_top = PILLAR_TOP_Z  # nut sits flush with pillar top
    nut = (
        cq.Workplane("XY")
        .workplane(offset=nut_top - NUT_THICK)
        .center(bx, by)
        .polygon(6, NUT_AF / math.cos(math.radians(30)))
        .extrude(NUT_THICK)
    )

    piece = bolt.union(nut)
    if hardware is None:
        hardware = piece
    else:
        hardware = hardware.union(piece)

# ============================================================
# INTERFERENCE CHECK (assembled position)
# ============================================================
import os

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
for fx, fy in BULKHEAD_POSITIONS:
    fh = (
        cq.Workplane("XY")
        .workplane(offset=ASSEMBLED_LID_Z - 1)
        .center(fx, fy)
        .circle(FLANGE_HOLE_DIA / 2)
        .extrude(LID_THICKNESS + 2)
    )
    lid_asm = lid_asm.cut(fh)

print("=" * 60)
print("INTERFERENCE CHECK (assembled position)")
print("=" * 60)

def check_interference(name, a, b, expected=False):
    inter = a.intersect(b)
    vol = inter.val().Volume() if inter.val().Volume() > 0.001 else 0
    if expected:
        status = "EXPECTED" if vol > 0 else "MISSING!"
    else:
        status = "INTERFERENCE!" if vol > 0 else "CLEAR"
    print(f"  {name:25s} {status:15s} ({vol:.2f} mm³)")
    return vol

check_interference("Bolt+Nut ↔ Base", hardware, base)
check_interference("Bolt+Nut ↔ Lid", hardware, lid_asm)
check_interference("Bolt+Nut ↔ Gasket", hardware, gasket)
check_interference("Lid ↔ Base", lid_asm, base)
check_interference("Lid ↔ Gasket (seal)", lid_asm, gasket, expected=True)
check_interference("Gasket ↔ Base (groove)", gasket, base, expected=True)

print()

# --- Bolt Reach Analysis ---
head_bottom = ASSEMBLED_LID_TOP - M3_HEAD_H
shaft_tip = head_bottom - M3_BOLT_LENGTH
lid_remaining = LID_THICKNESS - BOLT_HEAD_DEPTH
shaft_in_lid = lid_remaining
shaft_past_lid = M3_BOLT_LENGTH - shaft_in_lid
nut_top_z = PILLAR_TOP_Z
nut_bottom_z = nut_top_z - NUT_THICK
pocket_bottom_z = nut_top_z - NUT_POCKET_DEPTH
bore_bottom_z = pocket_bottom_z - BOLT_TIP_BORE

print("Bolt Reach Analysis (M3x6 SHCS + M3 hex nut):")
print(f"  Bolt head:       Z = {head_bottom:.1f}–{ASSEMBLED_LID_TOP:.1f} mm (in counterbore)")
cbore_msg = "OK recessed" if BOLT_HEAD_DEPTH >= M3_HEAD_H else f"PROTRUDES {M3_HEAD_H - BOLT_HEAD_DEPTH:.1f}mm!"
print(f"  Counterbore:     {BOLT_HEAD_DEPTH:.1f} mm deep, head {M3_HEAD_H:.1f} mm → {cbore_msg}")
print(f"  Shaft in lid:    {shaft_in_lid:.1f} mm (through {lid_remaining:.1f} mm material)")
print(f"  Shaft into nut:  {min(shaft_past_lid, NUT_THICK):.1f} mm thread engagement")
shaft_past_nut = shaft_past_lid - NUT_THICK
tip_z = nut_bottom_z - max(0, shaft_past_nut)
if shaft_past_nut > 0:
    fits = "OK" if shaft_past_nut <= BOLT_TIP_BORE else "BOTTOMS OUT!"
    print(f"  Bolt tip past nut: {shaft_past_nut:.1f} mm into bore ({BOLT_TIP_BORE:.1f} mm avail) → {fits}")
else:
    print(f"  Bolt tip past nut: NONE (tip inside nut)")
print()

# --- Cable Gland Clearance ---
GLAND_TOP_Z = CABLE_GLAND_Z + GLAND_BOSS_OD / 2
GLAND_OUTER_X = EXT_L / 2 + GLAND_BOSS_LENGTH
LID_LIP_BOTTOM_Z = ASSEMBLED_LID_Z - LID_LIP_DEPTH
print("Cable Gland Clearance:")
print(f"  Gland boss top:     Z = {GLAND_TOP_Z:.1f} mm")
print(f"  Body rim:           Z = {TOTAL_BASE_H:.1f} mm")
print(f"  Clearance to rim:   {TOTAL_BASE_H - GLAND_TOP_Z:.1f} mm → {'OK' if TOTAL_BASE_H > GLAND_TOP_Z else 'INTERFERENCE!'}")
print(f"  Lid bottom:         Z = {ASSEMBLED_LID_Z:.1f} mm")
print(f"  Lid lip bottom:     Z = {LID_LIP_BOTTOM_Z:.1f} mm")
print(f"  Lip ↔ gland gap:   {LID_LIP_BOTTOM_Z - GLAND_TOP_Z:.1f} mm → {'OK' if LID_LIP_BOTTOM_Z > GLAND_TOP_Z else 'INTERFERENCE!'}")
print(f"  Gland outer edge:   X = {GLAND_OUTER_X:.1f} mm")
print(f"  Flange edge:        X = {FLANGE_L/2:.1f} mm")
print(f"  Gland extends past flange: {'YES — ' + str(GLAND_OUTER_X - FLANGE_L/2) + 'mm' if GLAND_OUTER_X > FLANGE_L/2 else 'NO — flush or inside'}")
print(f"  Lid cutout needed:  NO (gland is {TOTAL_BASE_H - GLAND_TOP_Z:.1f} mm below rim)")
print()

# --- Pillar & Nut Wall Thickness ---
nut_wall = (BOSS_OD - NUT_ACROSS_CORNERS) / 2
print("Pillar & Nut Pocket:")
print(f"  Pillar OD:          {BOSS_OD:.1f} mm")
print(f"  Nut across corners: {NUT_ACROSS_CORNERS:.1f} mm")
print(f"  Wall around nut:    {nut_wall:.1f} mm → {'OK' if nut_wall >= 1.0 else 'THIN!'}")
print(f"  Nut pocket depth:   {NUT_POCKET_DEPTH:.1f} mm (nut {NUT_THICK:.1f} mm)")
print(f"  Bolt tip bore:      {BOLT_TIP_BORE:.1f} mm below nut")
print()

# --- Pillar Position Clearance ---
print("Pillar Position Clearance:")
for i, (bx, by) in enumerate(LID_BOLT_POSITIONS):
    dist_body_x = abs(bx) - EXT_L / 2
    dist_body_y = abs(by) - EXT_W / 2
    min_gap = min(dist_body_x, dist_body_y) - BOSS_OD / 2
    dist_flange_x = FLANGE_L / 2 - abs(bx) - BOSS_OD / 2
    dist_flange_y = FLANGE_W / 2 - abs(by) - BOSS_OD / 2
    min_flange = min(dist_flange_x, dist_flange_y)
    print(f"  Bolt {i+1} ({bx:+.1f}, {by:+.1f}): "
          f"body wall gap {min_gap:.1f}mm, flange edge {min_flange:.1f}mm")

print()

# --- Bulkhead ↔ Bolt/Gland Check ---
print("Bulkhead Hole Checks:")
for i, (fx, fy) in enumerate(BULKHEAD_POSITIONS):
    # vs bolt pillars
    for j, (bx, by) in enumerate(LID_BOLT_POSITIONS):
        dist = math.sqrt((fx - bx)**2 + (fy - by)**2)
        min_clear = (FLANGE_HOLE_DIA + BOSS_OD) / 2 + 1.0
        ok = dist >= min_clear
        if not ok:
            print(f"  BH{i+1} ↔ Bolt{j+1}: {dist:.1f}mm (need {min_clear:.1f}) → CONFLICT!")
    # vs cable gland
    gland_cx = EXT_L / 2 + GLAND_BOSS_LENGTH / 2
    gland_cy = 0
    dist_gland = math.sqrt((fx - gland_cx)**2 + (fy - gland_cy)**2)
    min_gland = (FLANGE_HOLE_DIA + GLAND_BOSS_OD) / 2 + 1.0
    if dist_gland < min_gland:
        print(f"  BH{i+1} ↔ CableGland: {dist_gland:.1f}mm (need {min_gland:.1f}) → CONFLICT!")
    else:
        print(f"  BH{i+1} ({fx:+.1f}, {fy:+.1f}): all clear")

print()

# --- M4 Hole Alignment Check ---
print("M4 Bulkhead Hole Alignment (base ↔ lid):")
print("  All M4 positions cut through BOTH base flange and lid — aligned ✓")
print()
print("=" * 60)

# ============================================================
# EXPORT
# ============================================================
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
cq.exporters.export(base, os.path.join(OUT_DIR, "pizero_housing_base.stl"))
cq.exporters.export(lid, os.path.join(OUT_DIR, "pizero_housing_lid.stl"))
cq.exporters.export(gasket, os.path.join(OUT_DIR, "pizero_housing_gasket.stl"))
cq.exporters.export(hardware, os.path.join(OUT_DIR, "pizero_housing_hardware.stl"))

print()
print(f"Enclosure Dimensions:")
print(f"  Base:    {FLANGE_L:.1f} × {FLANGE_W:.1f} × {TOTAL_BASE_H:.1f} mm (with flange)")
print(f"  Body:    {EXT_L:.1f} × {EXT_W:.1f} × {BODY_H:.1f} mm")
print(f"  Lid:     {FLANGE_L:.1f} × {FLANGE_W:.1f} × {LID_THICKNESS:.1f} mm (full flange)")
print(f"  Cavity:  {CAVITY_L:.1f} × {CAVITY_W:.1f} × {CAVITY_DEPTH:.1f} mm")
print(f"  Wall:    {WALL:.1f} mm  |  Corner R: {CORNER_RADIUS:.1f} mm")
print(f"  Pillars: {BOSS_OD:.1f} mm OD × {PILLAR_H:.1f} mm (4× external, hex nut pockets)")
print()
print(f"Gasket Groove (base rim):")
print(f"  {GASKET_GROOVE_W:.1f} mm wide × {GASKET_GROOVE_D:.1f} mm deep, inset {GASKET_INSET:.1f} mm")
print(f"  For 1.5mm silicone cord: 33% compression (recommended for IP67)")
print(f"  For printed TPU 68D:     23% compression (adequate for IP65)")
print()
print(f"Hardware (not printed):")
print(f"  4× M3x{M3_BOLT_LENGTH:.0f} SHCS + M3 hex nut (lid bolts)")
print(f"  4× M4 bolts + nuts (bulkhead mount, user-supplied)")
print(f"  1× PG7 cable gland + locknut")
print()
print("Exported: pizero_housing_base.stl, pizero_housing_lid.stl,")
print("          pizero_housing_gasket.stl, pizero_housing_hardware.stl")
print("(hardware.stl is for visualization only — do not print)")
