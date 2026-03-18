# VibePrint3D

A Claude Code skill that turns natural language descriptions of physical objects into 3D-printable files using CadQuery. Describe what you want — an enclosure, a bracket, a mount — and Claude designs it parametrically, reviews its own work visually, runs a QA pipeline, and iterates with you until it's print-ready.

## The Pipeline: Description to Printed Part

```
 Description          CadQuery Script        STL/3MF Files         Slicer            Print
┌─────────┐    ┌──────────────────┐    ┌───────────────┐    ┌──────────┐    ┌──────────┐
│ "I need  │───>│ Parametric Python │───>│ per-part STLs │───>│ Bambu    │───>│ Physical │
│ a box    │    │ with all dims as │    │ + multi-part  │    │ Studio / │    │ Part     │
│ for..."  │    │ named constants  │    │ 3MF assembly  │    │ OrcaSlicer│    │          │
└─────────┘    └──────────────────┘    └───────────────┘    └──────────┘    └──────────┘
                        │                       │
                   Self-review              QA Pipeline
                  (4-view render)         (/QA3DPrint)
                        │                       │
                   ┌─────────┐           ┌──────────────┐
                   │ preview │           │ Interference │
                   │ .png    │           │ Strength     │
                   └─────────┘           │ Assembly     │
                                         │ Printability │
                                         └──────────────┘
```

## Installation

### Prerequisites

CadQuery requires Python 3.11 and OpenCASCADE bindings. System Python (3.12+) is too new. You need conda:

```bash
# Install miniforge (macOS)
brew install --cask miniforge

# Create the cadquery environment
conda create -n cadquery python=3.11 cadquery trimesh matplotlib pillow numpy -c conda-forge -y

# Install 3MF export support
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery
pip install lib3mf
```

### Install the Skill

```bash
git clone https://github.com/Circus-Systems/VibePrint3D.git
cd VibePrint3D
bash install.sh
```

This copies the skill definition and scripts to `~/.claude/skills/cadquery-3dprint/`. Restart Claude Code after installing.

### Verify

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python -c "import cadquery; print('CadQuery OK')"
```

## How a New Agent Should Approach a Design

### Step 1: Understand What's Being Made

Before writing any code, establish:
- What is the part? What does it do?
- What components does it hold? (Get exact board dimensions, mounting patterns)
- What environment? (Indoor, outdoor, marine, IP67?)
- What printer and materials? (FDM/SLA, filament types, nozzle size)
- How will it be assembled? (Fastener types, access requirements)
- How will it be mounted? (Bulkhead, DIN rail, freestanding)

### Step 2: Write the Design Script

Every CadQuery script follows this structure:

```python
"""
Part Name — Brief description
Sealing architecture, assembly sequence, hardware list.
All dimensions in mm.
"""
import cadquery as cq

# PARAMETERS — every dimension is a named constant
WALL = 3.0
LENGTH = 70.0

# DERIVED DIMENSIONS — computed from parameters, never hardcoded
CAVITY_LENGTH = LENGTH - 2 * WALL

# PART: Base
base = cq.Workplane("XY").rect(LENGTH, WIDTH).extrude(HEIGHT)

# EXPORT
cq.exporters.export(base, "part_base.stl")
```

Rules:
- **No magic numbers in geometry code.** Every dimension is a named constant at the top.
- **Derived dimensions reference parameters.** `CAVITY_L = EXT_L - 2 * WALL`, not a hardcoded number.
- **Multi-part designs live in one script.** Shared parameters ensure parts fit together.
- **Each part exports as a separate STL.** One file per printable piece.
- **Docstring documents the full design.** Assembly sequence, sealing approach, hardware list, print setup.

### Step 3: Self-Review (4-View Render)

After generating STLs, Claude renders a 4-view orthographic preview (Front, Right, Top, Isometric) and checks:
- Is the geometry what was intended?
- Are features in the right place?
- Are proportions correct?

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery
python scripts/preview.py part.stl preview.png --title "My Part"
```

### Step 4: Run QA Pipeline

Use `/QA3DPrint` in Claude Code (or ask Claude to "run QA"). This checks:
1. **Interfaces / Interference** — Boolean intersection of all parts, clearance verification
2. **Structural Strength** — Wall thickness, pillar walls, nut pocket walls, force paths
3. **Assembly Feasibility** — Step-by-step sequence, tool access, clamping direction
4. **Bambu P2S Print Issues** — Overhangs, bridging, orientation, thin walls, AMS compatibility

Returns a report with PASS / WARNING / ISSUE items. **Does not make changes without user approval.**

### Step 5: Show the User

Open the interactive Three.js viewer so the user can orbit, zoom, and inspect:

```bash
python scripts/viewer.py base.stl lid.stl gasket.stl --title "Assembly"
```

Self-contained HTML — no internet needed, all STL data embedded as base64. Multi-part support with distinct colors.

### Step 6: Export 3MF for Slicer

Use `/ConvertToPrintFile` in Claude Code. This automatically:
1. Finds the design script and its STL outputs
2. Reads the docstring to determine material assignments
3. Packages everything into a single `.3mf` with named materials and colors
4. Reports the result

Or run manually:
```bash
python scripts/export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o assembly.3mf --title "My Part"
```

See the [3MF section](#3mf-multi-part-assembly) below for full documentation.

### Step 7: Stress Analysis (Optional)

Use `/StressAnalysis` to run finite element analysis on any part. This:
1. Volume-meshes the STL into tetrahedra (Gmsh)
2. Solves linear elastic FEA (scikit-fem)
3. Computes von Mises stress per element
4. Renders a 4-view heatmap showing stress concentrations
5. Reports safety factor vs material yield strength

Target safety factor ≥ 2.0 for 3D-printed parts (FDM layer adhesion is weaker than bulk material).

### Step 8: Iterate

User gives feedback. Modify the script, rebuild, re-render, re-QA. Repeat until approved.

## Running Scripts

All CadQuery commands require the conda environment:

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python <script>
```

## Output Formats

### STL (per-part)
Standard triangle mesh. One file per printable part. Import into any slicer. Generated by every CadQuery design script via `cq.exporters.export()`.

### 3MF (multi-part assembly)
The 3MF format packages multiple parts into one file with material names and colors. This is the preferred format for multi-material prints — and the final output of the VibePrint pipeline.

**Quick start — use the slash command:**
```
/ConvertToPrintFile
```
This automatically finds the design script, identifies STL outputs, assigns materials, and generates the `.3mf`. No manual steps needed.

**Manual usage:**
```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery
python scripts/export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o housing.3mf --title "My Housing"
```

**How `export_3mf.py` works internally:**
1. Loads each STL file via `trimesh` — extracts vertices and face indices
2. Creates a `lib3mf` model (the official 3MF Consortium C++ library with Python bindings)
3. For each STL, creates a named `MeshObject` and populates it with the vertex/triangle data
4. Creates a `BaseMaterialGroup` with entries for each filament (name + display color)
5. Assigns each mesh object to its material via `SetObjectLevelProperty()`
6. Writes the model as a `.3mf` file (a ZIP archive containing `3D/3dmodel.model` in XML)

**The `:MATERIAL` syntax:**
Each input STL can have a material suffix after a colon. If omitted, defaults to PETG.
```
base.stl:PETG     → assigned to PETG (dark grey)
gasket.stl:TPU    → assigned to TPU (orange)
bracket.stl       → assigned to PETG (default)
```

**Built-in materials:**

| Material | Display Color | Hex | Typical use |
|----------|--------------|-----|-------------|
| PETG | Dark grey | `#646464` | Structural, marine, outdoor |
| TPU | Orange | `#FF8C00` | Gaskets, flexible parts |
| PLA | White | `#E0E0E0` | Prototypes, indoor |
| ASA | Light grey | `#A0A0A0` | UV-resistant outdoor |
| ABS | Black | `#303030` | High temp |
| NYLON | Cream | `#E8DCC8` | High strength, wear |

Custom materials: `--material "CARBONFIBER=#1A1A1A"`

**CLI reference:**
```
python scripts/export_3mf.py [options] file1.stl[:MAT] file2.stl[:MAT] ... -o output.3mf

Options:
  -o, --output          Output .3mf file path (required)
  --title               Model title metadata shown in slicer
  --material NAME=#HEX  Define custom material (repeatable)
  --default-material    Default material for untagged STLs (default: PETG)
```

**What goes in, what stays out:**
- Include all **printable** parts (base, lid, gasket, bracket, mount, etc.)
- Exclude **visualization-only** parts (bolt geometry, nut models, interference check bodies)
- If a part name contains "hardware", "bolt", "nut", or "screw" — it's probably not for printing

**Slicer compatibility:**
- **OrcaSlicer** — correctly preserves per-object material assignments from standard 3MF
- **PrusaSlicer / Cura** — standard 3MF import, separate objects with colors
- **Bambu Studio** — imports parts as separate colored objects; filament assignment may need manual confirmation depending on version

**Why 3MF over STL:**
- Units are explicit (millimeters, no ambiguity)
- Multi-part assemblies in one file
- Material/color metadata embedded
- Enforced manifold geometry (no flipped normals)
- Smaller files (ZIP compressed)
- Industry standard endorsed by Microsoft, HP, Autodesk, Bambu Lab, Prusa

**Dependencies:**
- `lib3mf` — `pip install lib3mf` in the cadquery conda env
- `trimesh` — already installed in the cadquery env (used for STL loading)

## CadQuery Gotchas

- **`fillet()` fails on some edge configurations.** Always wrap in `try/except`.
- **`shell()` fails on complex geometry.** Prefer manual cavity cutting (`cutBlind`).
- **Boolean cut cylinders must be longer than the boss.** Short cuts leave membranes. Add 1-2mm overlap.
- **Clearance holes must be oversized for FDM.** M3 → 3.4mm, M4 → 4.5mm.
- **Hex nut pockets need ~0.1mm clearance per flat** vs nominal across-flats dimension.

## Waterproof Enclosure Design (IP67)

When a design is described as "waterproof", the project targets **IP67** per IEC 60529:

| Rating | Meaning |
|--------|---------|
| IP6x (dust) | Dust-tight — zero ingress after 8-hour test |
| IPx7 (water) | Survives immersion at 1m depth for 30 minutes |

Design rules enforced during QA:

- **Gasket compression 25-35%** of free height. Crush limiters (pillar tops) control this.
- **Gasket must be continuous.** No bolt bosses or features breaking the seal perimeter.
- **No fastener paths through the sealed volume.** Water wicks down threads. Bolts go outside.
- **Through-bolt clamping direction matters.** Bolt head on lid, nut at flange base. Not reversed.
- **Tongue-and-groove or stepped mating surfaces.** Never flat-to-flat.
- **All cable entries use IP67-rated glands.** One unsealed hole defeats the enclosure.
- **Always write out the full assembly sequence.** If any step is physically impossible, redesign.

See `CLAUDE.md` for the complete IP67 specification and the design mistakes registry.

## Reference Dimensions

### Raspberry Pi Boards

| Board | L x W x H (mm) | Mount pattern | Mount hole |
|-------|-----------------|---------------|------------|
| Pi Zero 2W | 65 x 30 x 5 | 58 x 23 | M2.5 |
| Pi 4B / Pi 5 | 85 x 56 x 17 | 58 x 49 | M2.75 |
| Pi Pico | 51 x 21 x 1 | 47 x 11.4 | M2 |

### Cable Glands

| Type | Thread | Cable range | Boss OD |
|------|--------|-------------|---------|
| PG7 | M12x1.5 | 3-6.5mm | 18mm |
| PG9 | M16x1.5 | 4-8mm | 22mm |
| PG11 | M18x1.5 | 5-10mm | 24mm |
| PG13.5 | M20x1.5 | 6-12mm | 26mm |

### Fasteners (FDM clearance holes)

| Bolt | Clearance hole | SHCS head dia | Hex nut AF |
|------|---------------|---------------|------------|
| M2.5 | 2.8mm | 5mm | 5.0mm |
| M3 | 3.4mm | 6mm | 5.5mm |
| M4 | 4.5mm | 8mm | 7.0mm |
| M5 | 5.5mm | 10mm | 8.0mm |

## Material Guide

| Material | Use case | Notes |
|----------|----------|-------|
| **PLA** | Prototypes, indoor | Easy to print. Not UV/heat resistant. |
| **PETG** | Marine, outdoor, structural | UV resistant, low water absorption. Go-to for functional parts. |
| **ABS/ASA** | High temp, automotive | ASA better UV resistance. Needs enclosed printer. |
| **TPU** | Gaskets, vibration damping | Shore hardness matters: 68D is semi-rigid (AMS compatible), 95A is flexible (not AMS compatible). |
| **Nylon (PA)** | High strength, wear parts | Absorbs moisture. Dry filament before printing. |

### Bambu Lab P2S + AMS Notes

- TPU 68D is AMS-compatible. Standard TPU 95A is NOT.
- TPU 68D is NOT compatible with 0.2mm nozzle. Use 0.4mm.
- Multi-material prints: import parts as separate objects in slicer, assign filament per object.
- Build volume: 256 x 256 x 256 mm.

## Repository Structure

```
VibePrint3D/
├── SKILL.md          # Claude Code skill definition (installed to ~/.claude/skills/)
├── CLAUDE.md         # Project rules, IP67 spec, design mistakes registry
├── install.sh        # One-command skill installer
├── scripts/
│   ├── preview.py    # 4-view static PNG renderer (matplotlib + trimesh)
│   ├── viewer.py     # Interactive Three.js HTML viewer
│   ├── export_3mf.py # STL → 3MF packager with material assignments (lib3mf)
│   └── stress_analysis.py # FEA stress analysis (Gmsh + scikit-fem → von Mises heatmap)
└── examples/
    └── *.py          # Working design scripts (reference implementations)
```

Generated files (STL, STEP, 3MF, PNG, HTML) are gitignored — only source scripts are committed.

## License

MIT
