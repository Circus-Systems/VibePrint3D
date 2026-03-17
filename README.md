# VibePrint3D

Turn plain-language descriptions of physical objects into 3D-printable STL files using Claude Code. Describe what you need — *"a waterproof case for a Pi Zero with a cable gland and bulkhead mount"* — and Claude designs it step by step, showing you the model at each stage and incorporating your feedback before moving on.

## How It Works

VibePrint3D is a **Claude Code skill** that follows a three-phase design workflow:

```
You describe a part
        │
        ▼
┌─────────────────────────────┐
│  Phase 1: Base Shape        │  Outer shell, cavities, proportions
│  → Preview → Your feedback  │
├─────────────────────────────┤
│  Phase 2: Features          │  Holes, bosses, mounts, cable entries
│  → Preview → Your feedback  │
├─────────────────────────────┤
│  Phase 3: Print Readiness   │  Fillets, checks, final STL + STEP
│  → Preview → Your feedback  │
└─────────────────────────────┘
        │
        ▼
  STL files ready for your slicer
```

At each phase, Claude:
1. Writes a parametric CadQuery (Python) script
2. Generates the 3D model
3. Renders a 4-view preview and self-reviews it against a printability checklist
4. Opens an interactive 3D viewer in your browser
5. **Waits for your feedback** before moving on

You can say things like *"make it 5mm taller"*, *"move the cable gland to the other end"*, or *"add two more mounting holes"* at any checkpoint.

## What You Get

Every design produces:
- **STL files** — one per printable part, ready for your slicer (PrusaSlicer, OrcaSlicer, Cura)
- **STEP files** — for import into Onshape, Fusion 360, or any CAD tool
- **Python script** — fully parametric; change any dimension at the top and re-run to regenerate
- **Interactive HTML viewer** — self-contained Three.js viewer you can open anytime

## Prerequisites

- **Claude Code** (the CLI tool) — [install guide](https://docs.anthropic.com/en/docs/claude-code)
- **Python 3.10–3.12** with CadQuery installed (see below)
- **A 3D printer** and slicer software

### Installing CadQuery

CadQuery requires the OpenCASCADE (OCP) kernel, which needs specific Python versions. The easiest method is conda/miniforge:

```bash
# Install miniforge (macOS)
brew install --cask miniforge

# Create a dedicated environment
conda create -n cadquery python=3.11 cadquery trimesh matplotlib pillow numpy -c conda-forge -y

# Verify it works
conda activate cadquery
python -c "import cadquery as cq; print('CadQuery', cq.__version__, '— OK')"
```

> **Why conda?** CadQuery depends on OpenCASCADE Python bindings (OCP) which only ship pre-built wheels for Python 3.10–3.12. If your system Python is newer (3.13+), pip install will fail. The conda environment handles this cleanly.

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/Circus-Systems/VibePrint3D.git
```

### 2. Install the skill into Claude Code

Copy the skill directory into Claude Code's skills folder:

```bash
mkdir -p ~/.claude/skills/cadquery-3dprint/scripts
cp VibePrint3D/SKILL.md ~/.claude/skills/cadquery-3dprint/
cp VibePrint3D/scripts/preview.py ~/.claude/skills/cadquery-3dprint/scripts/
cp VibePrint3D/scripts/viewer.py ~/.claude/skills/cadquery-3dprint/scripts/
```

### 3. Configure the conda environment path

The SKILL.md file contains commands that activate the conda environment before running Python. If your miniforge is installed somewhere other than `/opt/homebrew/Caskroom/miniforge/base/`, edit the paths in `SKILL.md`:

```bash
# Find your conda path
which conda
# Update the eval lines in SKILL.md to match
```

### 4. Verify

Open Claude Code and say:

> "Design me a simple test cube — 30mm with 2mm walls, shelled, with M3 mounting holes in each corner."

Claude should write a CadQuery script, generate STLs, render previews, and open an interactive viewer.

## Usage

Just describe what you need in natural language. The skill activates automatically when you mention physical objects, dimensions, 3D printing, STL files, enclosures, brackets, mounts, or any description of something you want to fabricate.

### Example prompts

```
"I need a waterproof enclosure for a Raspberry Pi Zero 2W with a PG7 cable
gland for USB-C power, bulkhead mount, PETG for marine use"

"Design a GoPro mount bracket for a 25mm tube — needs to handle vibration"

"Make me a cable entry plate with 6 PG7 glands in a 2×3 grid, 150mm × 100mm,
5mm thick, countersunk M4 mounting holes in the corners"

"I need a DIN rail mount adapter for this PCB — it's 80×50mm with M3 holes
at 72×42mm pattern"
```

### Giving feedback

At each checkpoint, you can request changes:

```
"Make the walls thicker — 4mm instead of 3"
"Move the cable gland to the short end"
"The cavity needs to be 5mm deeper"
"Add standoffs for the PCB — M2.5 at 58×23mm pattern"
"Can you add a DIN rail clip instead of the mounting ears?"
```

### Tweaking after delivery

Every generated script has all dimensions as named variables at the top:

```python
WALL = 3.0              # wall thickness
CLEARANCE = 3.0         # clearance around board
CAVITY_DEPTH = 20.0     # internal cavity depth
STANDOFF_HEIGHT = 4.0   # PCB standoff height
```

Change any value, re-run the script, and get updated STL files instantly.

## Project Structure

```
VibePrint3D/
├── README.md              # This file
├── SKILL.md               # The Claude Code skill definition
├── scripts/
│   ├── preview.py         # 4-view static PNG renderer (Claude self-reviews these)
│   └── viewer.py          # Interactive Three.js HTML viewer (you inspect these)
└── examples/
    └── pizero_housing.py  # Complete example: Pi Zero 2W waterproof housing
```

## Example: Pi Zero 2W Waterproof Housing

The `examples/pizero_housing.py` file is a complete, working design generated by this skill. It demonstrates all the key features:

**What it is:** A two-piece waterproof enclosure for a Raspberry Pi Zero 2W, designed for marine bulkhead mounting.

**Key specs:**
| Feature | Detail |
|---------|--------|
| External (with flange) | 93 × 58 × 27 mm |
| Body | 77 × 42 × 23 mm |
| Internal cavity | 71 × 36 × 20 mm |
| Wall thickness | 3mm PETG |
| Lid-to-base bolts | 4× M3 with heat-set inserts (OD 8mm corner bosses) |
| PCB mounting | 4× M2.5 standoffs (58×23mm Pi Zero 2W pattern) |
| Cable entry | PG7 cable gland boss (M12 thread, 18mm OD) |
| Bulkhead mount | 4× M4 clearance holes in perimeter flange |
| Corner radius | 2mm on all edges |
| Sealing | Marine silicone between mating faces + lid lip alignment |

**Generate the STL files:**

```bash
conda activate cadquery
cd VibePrint3D/examples
python pizero_housing.py
```

This produces `pizero_housing_base.stl` and `pizero_housing_lid.stl`.

**View the result:**

```bash
python ../scripts/viewer.py pizero_housing_base.stl pizero_housing_lid.stl --title "Pi Zero 2W Housing"
```

**Preview (static 4-view):**

```bash
python ../scripts/preview.py pizero_housing_base.stl preview.png --title "Pi Zero Housing — Base"
```

## How the Skill Works Under the Hood

### CadQuery + OpenCASCADE

[CadQuery](https://cadquery.readthedocs.io/) is a Python CAD library backed by the OpenCASCADE kernel — the same kernel used by FreeCAD and commercial CAD tools. It handles fillets, chamfers, booleans, and shells reliably, and produces scripts that are just Python.

### Two Preview Systems

| System | File | Who uses it | Purpose |
|--------|------|-------------|---------|
| `preview.py` | Static 4-view PNG | Claude (self-review) | Front/Right/Top/Iso views rendered with matplotlib |
| `viewer.py` | Interactive HTML | You (inspection) | Three.js scene with orbit, zoom, wireframe, grid |

Claude generates the static preview, examines it using vision, and checks it against a printability checklist (wall thickness, overhangs, watertightness, proportions). If something is wrong, Claude fixes the script and re-renders before showing you.

The interactive viewer is for you — orbit the model, toggle wireframe, check dimensions in the HUD overlay.

### Printability Checklist

After every render, Claude checks:

- **Geometry:** Shape matches description, proportions correct, booleans clean
- **Printability:** Flat bottom, walls ≥ 1.2mm (≥ 2mm structural), no overhangs > 45°, no features < 0.4mm
- **Parametric:** All dimensions as named variables, descriptive names, consistent units

### Built-in Reference Data

The skill includes dimension tables for common components:

- **Raspberry Pi boards** (Zero 2W, 4B, 5, Pico) — board dims and mount patterns
- **Cable glands** (PG7 through PG13.5) — thread spec, cable range, boss OD
- **Fasteners** (M2.5 through M5) — clearance holes, head diameters, heat-set insert holes

## Material Guide

| Material | Best for | Notes |
|----------|----------|-------|
| **PLA** | Indoor, prototyping | Easy to print. Not UV/heat resistant. |
| **PETG** | Marine, outdoor, structural | UV resistant, doesn't absorb water. Go-to for functional parts. |
| **ABS/ASA** | High temp, automotive | ASA has better UV resistance. Needs enclosed printer. |
| **TPU** | Gaskets, vibration damping | Flexible. |
| **Nylon** | High strength, wear parts | Absorbs moisture — dry before printing. |

## Limitations

- **Prismatic geometry only.** CadQuery excels at boxes, cylinders, chamfers, fillets. Not for organic/sculpted shapes.
- **No assembly simulation.** Static geometry — no moving parts, interference checks, or stress analysis.
- **FDM-focused.** Printability checks assume FDM (0.4mm nozzle). SLA/SLS users may need different tolerances.
- **Boolean edge cases.** Complex intersections occasionally produce non-manifold geometry. The watertight check catches this.

## License

MIT
