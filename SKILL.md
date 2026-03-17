---
name: cadquery-3dprint
description: Design and generate 3D-printable parts using CadQuery. Use this skill whenever the user wants to design, model, create, or iterate on a physical part for 3D printing — enclosures, brackets, mounts, cases, holders, adapters, jigs, or any custom hardware. Triggers on mentions of STL, STEP, 3D print, CadQuery, OpenSCAD, enclosure, bracket, mount, case, holder, adapter, jig, fixture, or any description of a physical object the user wants to make. Also triggers when the user says things like "I need a box for", "design me a", "can you model", "make me a part", or describes dimensions and features of something they want to fabricate. Even if the user doesn't mention 3D printing explicitly, if they're describing a physical object with specific dimensions, this skill should activate.
---

# CadQuery 3D Print Designer

Turn conversational descriptions into printable STL files through an iterative design loop with visual checkpoints. Uses CadQuery (Python, backed by OpenCASCADE) for parametric modeling.

## Prerequisites

CadQuery runs in a conda environment. **Always prefix Python commands with the conda wrapper:**

```bash
# Run any CadQuery script:
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python your_script.py

# Run preview.py:
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/preview.py input.stl output.png

# Run viewer.py:
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/viewer.py part.stl --title "Part Name"
```

**Do NOT use system pip or system python** — CadQuery requires the conda `cadquery` environment (Python 3.11 + OCP bindings).

### Fallback Preview (if preview.py fails)

If the preview script isn't available or fails, use this inline matplotlib approach:

## Core Workflow: Three-Phase Design Loop

Every design follows three phases. At each phase, generate the model, render a multi-view preview, run the printability checklist, self-correct if needed, then show the user and ask for feedback BEFORE moving on.

### Phase 1: Base Shape
Build the fundamental geometry — outer shell, cavities, overall proportions. No detail features yet.

**What to do:**
1. Gather requirements conversationally (dimensions, purpose, mounting, materials)
2. Research reference dimensions if the design wraps around a known object (look up datasheets)
3. Write a CadQuery script with all dimensions as variables at the top
4. Run the script → STL
5. Run `scripts/preview.py` to render 4-view preview image
6. View the preview image and self-review against the checklist
7. If issues found, fix and re-render (up to 3 self-correction loops)
8. Show the preview to the user: "Here's the base shape. Any changes before I add features?"
9. Wait for feedback. Incorporate changes before moving on.

### Phase 2: Features
Add functional details — holes, bosses, grooves, chamfers, fillets, ribs, snap fits, mounting points, cable routes.

**What to do:**
1. Add features to the existing script (don't rewrite from scratch)
2. Run → STL → preview → self-review → show user
3. "Here are the features added. Anything to adjust?"
4. Wait for feedback.

### Phase 3: Print Readiness
Final cleanup for printability — fillet sharp edges, check wall thickness, verify flat print surface, add draft angles if needed.

**What to do:**
1. Apply final fillets, verify printability
2. Run → STL → STEP → preview → self-review → show user
3. Export both STL (for slicer) and STEP (for CAD import) as final deliverables
4. "Here's the final part, ready to slice. The STL and STEP files are attached."

## Preview Pipeline

After generating any STL, ALWAYS render a preview before showing the user anything.

### Static 4-View Preview (for self-review)

Use this to check your own work before showing the user:

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/preview.py input.stl output_preview.png --title "Part Name — Phase N"
```

This renders a 2x2 grid: front, right, top, and isometric views. After rendering, use the `view` tool to look at the preview image yourself. You are reviewing your own work.

### Interactive 3D Viewer (for the user)

After self-review passes, generate an interactive viewer the user can orbit, zoom, and inspect:

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/viewer.py part_base.stl part_lid.stl --title "My Enclosure"
```

This creates a self-contained HTML file (no internet required after loading) with:
- Three.js WebGL rendering with orbit controls
- Preset view buttons (Front, Right, Top, Iso)
- Wireframe toggle
- Grid toggle
- Bounding box dimensions in a HUD overlay
- Multi-part support with distinct colors

The viewer opens automatically in the user's browser. Use `--no-open` if generating in a headless environment, and tell the user where the HTML file is so they can open it.

At each phase checkpoint, deliver BOTH the static preview (for quick inline review) and the interactive viewer (for detailed inspection).

```python
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

mesh = trimesh.load("part.stl")
fig = plt.figure(figsize=(16, 16))

views = [
    ("Front",  0,   0),    # XZ plane
    ("Right",  0,  90),    # YZ plane  
    ("Top",   90,   0),    # XY plane
    ("Iso",   30, -45),    # Isometric
]

for i, (name, elev, azim) in enumerate(views):
    ax = fig.add_subplot(2, 2, i+1, projection='3d')
    verts = mesh.vertices
    faces = mesh.faces
    poly = Poly3DCollection(verts[faces], alpha=0.7, facecolor='#4a90d9', edgecolor='#2a5a95', linewidth=0.1)
    ax.add_collection3d(poly)
    
    scale = verts.max(axis=0) - verts.min(axis=0)
    center = verts.mean(axis=0)
    max_range = scale.max() / 2
    ax.set_xlim(center[0]-max_range, center[0]+max_range)
    ax.set_ylim(center[1]-max_range, center[1]+max_range)
    ax.set_zlim(center[2]-max_range, center[2]+max_range)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(name, fontsize=14, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

plt.tight_layout()
plt.savefig("preview.png", dpi=150, bbox_inches='tight')
```

After rendering, use the `view` tool to look at the preview image yourself. You are reviewing your own work.

## Self-Review Checklist

After viewing every preview, check ALL of these before showing the user. If any fail, fix the script and re-render.

### Geometry
- [ ] Overall shape matches the user's description
- [ ] Proportions look correct (not squished, stretched, or lopsided)
- [ ] All requested features are visible
- [ ] No obviously missing geometry (holes going nowhere, floating parts)
- [ ] Boolean operations succeeded (no weird artifacts or missing cuts)

### Printability (FDM)
- [ ] Flat bottom surface for bed adhesion
- [ ] Wall thickness ≥ 1.2mm everywhere (≥ 2mm for structural parts)
- [ ] No unsupported overhangs > 45° (or design is oriented to avoid them)
- [ ] No features smaller than 0.4mm (typical nozzle diameter)
- [ ] Holes are oriented vertically where possible (print cleaner)
- [ ] Clearance holes are slightly oversized (+0.2mm for press fit, +0.4mm for loose)

### Parametric Design
- [ ] All dimensions are variables at the top of the script (not magic numbers in the geometry code)
- [ ] Variables are named descriptively (WALL_THICKNESS not W)
- [ ] Related dimensions reference each other (cavity = external - 2*wall)
- [ ] Units are consistent (all mm, clearly commented)

## CadQuery Best Practices

### Script Structure
Every script should follow this layout:

```python
"""
Part Name — Brief description
Designed for [purpose]
All dimensions in mm.
"""
import cadquery as cq

# ============================================================
# PARAMETERS
# ============================================================
WALL = 3.0              # wall thickness
LENGTH = 70.0           # overall length
# ... all dimensions here as named constants

# ============================================================
# DERIVED DIMENSIONS
# ============================================================
CAVITY_LENGTH = LENGTH - 2 * WALL
# ... computed values

# ============================================================
# PART: Base
# ============================================================
base = (
    cq.Workplane("XY")
    .box(LENGTH, WIDTH, HEIGHT)
    # ... operations
)

# ============================================================
# EXPORT
# ============================================================
cq.exporters.export(base, "part_base.stl")
cq.exporters.export(base, "part_base.step")
print("Exported: part_base.stl, part_base.step")
```

### Common Operations Cheat Sheet

**Shell (hollow out):**
```python
result = box.faces(">Z").shell(-WALL)  # negative = shell inward
```

**O-ring groove (rectangular channel):**
```python
# Cut groove into mating face using two concentric rects
result = (
    part.faces(">Z").workplane()
    .rect(outer_w, outer_h)
    .rect(inner_w, inner_h)  # creates annular region
    .cutBlind(-groove_depth)
)
```

**Counterbored bolt hole:**
```python
result = part.faces(">Z").workplane().pushPoints(positions).cboreHole(
    bolt_clearance_dia, head_dia, head_depth
)
```

**Heat-set insert pocket:**
```python
result = part.faces("<Z").workplane().pushPoints(positions).hole(
    insert_dia, insert_depth
)
```

**Standoffs / bosses:**
```python
standoff = (
    cq.Workplane("XY").workplane(offset=floor_z)
    .pushPoints(positions)
    .circle(boss_od / 2).extrude(boss_height)
)
standoff = standoff.faces(">Z").workplane().pushPoints(positions).hole(screw_dia, depth)
part = part.union(standoff)
```

**Cable gland boss (PG7/M12):**
```python
boss = (
    cq.Workplane("YZ").workplane(offset=wall_x)
    .circle(boss_od / 2).extrude(boss_length)
)
part = part.union(boss)
part = part.faces(">X").workplane().hole(thread_dia, boss_length + wall + 1)
```

**Fillet (round edges):**
```python
result = part.edges("|Z").fillet(radius)        # all vertical edges
result = part.edges(">Z").fillet(radius)         # top edges only
# Use try/except — some edge selections fail on complex geometry
try:
    result = part.edges("|Z").fillet(2.0)
except:
    pass  # skip if filleting fails on this geometry
```

**Mounting ears / flanges:**
```python
ear = cq.Workplane("XY").box(ear_w, ear_h, ear_thick).translate((x, y, z))
ear = ear.faces(">X").workplane().hole(mount_hole_dia)
part = part.union(ear)
```

### Gotchas
- Always `try/except` around fillets — they fail on some edge configurations
- When cutting holes through bosses, make the cut cylinder longer than the boss to ensure full penetration
- For two-piece enclosures, build base and lid as separate CadQuery objects in the same script
- `shell()` can fail on complex geometry — prefer manual cavity cutting (box + cutBlind) for reliability
- Print orientation matters: the mating face of an enclosure should be printed face-down for best surface finish

## Reference Dimensions for Common Components

When designing enclosures for known hardware, always research exact dimensions. Here are frequently used ones:

**Raspberry Pi boards:**
| Board | L×W×H (mm) | Mount pattern | Mount hole |
|-------|-----------|---------------|------------|
| Pi Zero 2W | 65×30×5 | 58×23 | M2.5 |
| Pi 4B | 85×56×17 | 58×49 | M2.75 |
| Pi 5 | 85×56×17 | 58×49 | M2.75 |
| Pi Pico | 51×21×1 | 47×11.4 | M2 |

**Cable glands:**
| Type | Thread | Cable range | Boss OD |
|------|--------|-------------|---------|
| PG7 | M12×1.5 | 3–6.5mm | 18mm |
| PG9 | M16×1.5 | 4–8mm | 22mm |
| PG11 | M18×1.5 | 5–10mm | 24mm |
| PG13.5 | M20×1.5 | 6–12mm | 26mm |

**Fasteners (clearance holes for 3D printing):**
| Bolt | Clearance hole | Head dia | Heat-set insert hole |
|------|---------------|----------|---------------------|
| M2.5 | 2.8mm | 5mm | 3.5mm |
| M3 | 3.4mm | 6mm | 4.2mm |
| M4 | 4.5mm | 8mm | 5.6mm |
| M5 | 5.5mm | 10mm | 6.8mm |

## Multi-Part Designs

For enclosures and assemblies with multiple parts:

1. Build all parts in the same script for dimensional consistency
2. Use shared parameters (wall thickness, bolt pattern, etc.)
3. Export each part as a separate STL
4. Export an assembly STEP with parts offset for visualization:
```python
assembly = cq.Assembly()
assembly.add(base, name="base", color=cq.Color(0.2, 0.2, 0.8, 1.0))
assembly.add(lid, name="lid", loc=cq.Location((0, 0, 10)), color=cq.Color(0.8, 0.2, 0.2, 0.8))
assembly.save("assembly.step")
```

## Material Guidance

When the user asks about material choice, recommend based on application:
- **PLA**: General purpose, easy to print. Not UV/heat resistant. Indoor use.
- **PETG**: Marine, outdoor, structural. UV resistant, doesn't absorb water. Go-to for functional parts.
- **ABS/ASA**: High temp, automotive, outdoor. ASA has better UV resistance. Needs enclosed printer.
- **TPU**: Flexible parts, gaskets, vibration damping.
- **Nylon (PA)**: High strength, wear resistant. Absorbs moisture — dry before printing.

## Delivering Files

Always export and present:
1. **STL files** — one per printable part (ready for slicer)
2. **STEP files** — one per part + assembly (for CAD import and inspection)
3. **The Python script** — so the user can tweak parameters and regenerate

Present all files to the user with a brief summary of dimensions and key features. Don't over-explain — the user can inspect the files themselves.
