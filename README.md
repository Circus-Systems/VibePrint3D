# VibePrint3D

A Claude Code skill that turns natural language descriptions of physical objects into 3D-printable STL files. Describe what you want — an enclosure, a bracket, a mount — and Claude designs it parametrically using CadQuery, reviews its own work visually, and iterates with you until it's right.

## How It Works

You talk. Claude designs. You review in 3D. Repeat until done.

```
You:    "I need a waterproof housing for a Raspberry Pi Zero 2W
         with a PG7 cable gland and M4 bulkhead mounting holes"

Claude: [writes CadQuery script] → [generates STL] → [renders 4-view preview]
        [self-reviews geometry] → [opens interactive 3D viewer in browser]

You:    "Make the walls thicker and add ventilation slots"

Claude: [modifies script] → [rebuilds] → [re-renders] → [shows you]
```

The output is a parametric Python script with all dimensions as variables at the top — change one number and regenerate. You get STL files ready for your slicer and an interactive Three.js viewer to inspect the model from any angle.

## Installation

### Prerequisites

CadQuery requires Python 3.11 and OpenCASCADE bindings, which don't work with newer Python versions. You need conda:

```bash
# Install miniforge (macOS)
brew install --cask miniforge

# Create the cadquery environment
conda create -n cadquery python=3.11 cadquery trimesh matplotlib pillow numpy -c conda-forge -y
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

## The Design Pipeline

Every design follows three phases. Claude generates the model, renders a preview, checks its own work against a printability checklist, self-corrects if needed, then shows you. You give feedback before it moves on.

### Phase 1: Base Shape

The fundamental geometry — outer shell, cavities, overall proportions. No detail features yet. Claude researches reference dimensions for known components (Pi boards, cable glands, standard fasteners) and builds the parametric skeleton.

### Phase 2: Features

Functional details — mounting holes, bosses, grooves, fillets, snap fits, cable routes, gasket grooves. Added to the existing script, not rewritten from scratch.

### Phase 3: Print Readiness

Final cleanup — fillet sharp edges, verify wall thickness, check print orientation, ensure flat bed surface. Exports STL (for slicer) and STEP (for CAD import).

At each phase, Claude shows you a 4-view static preview and an interactive 3D viewer. You approve or request changes before proceeding.

## Running Scripts

All CadQuery commands require the conda environment. Always prefix with:

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python <script>
```

### Design scripts

```bash
# Run a design script (generates STL files)
... && python examples/pizero_housing.py
```

### Static 4-view preview (Claude's self-review)

```bash
... && python scripts/preview.py part.stl preview.png --title "My Part"
```

Renders Front, Right, Top, and Isometric views in a 2×2 grid. Prints printability warnings (watertightness, thin dimensions).

### Interactive Three.js viewer (your inspection)

```bash
... && python scripts/viewer.py base.stl lid.stl gasket.stl --title "Assembly"
```

Generates a self-contained HTML file — no internet needed, all STL data embedded as base64. Multi-part support with distinct colors. Opens in browser automatically (`--no-open` to suppress).

## QA Pipeline

Run `/QA3DPrint` in Claude Code to execute a comprehensive quality check on any design:

1. **Interference check** — boolean intersection of all part pairs, clearance holes, counterbores, nut pockets
2. **Structural strength** — wall thicknesses, nut pocket walls, pillar walls, bolt force paths
3. **Assembly feasibility** — step-by-step sequence verification, tool access, clamping direction, serviceability
4. **Bambu P2S print check** — overhangs, bridging, orientation, thin walls, AMS multi-material compatibility, build volume

Returns a PASS / WARNING / ISSUE report with suggested changes. **Does not modify files without your approval.**

## Design Script Conventions

Every CadQuery script follows this structure:

```python
"""
Part Name — Brief description
Assembly sequence and sealing architecture documented here.
All dimensions in mm.
"""
import cadquery as cq

# ============================================================
# PARAMETERS — all dimensions as named constants
# ============================================================
WALL = 3.0
LENGTH = 70.0

# ============================================================
# DERIVED DIMENSIONS — computed from parameters
# ============================================================
CAVITY_LENGTH = LENGTH - 2 * WALL

# ============================================================
# PART: Base
# ============================================================
base = cq.Workplane("XY").rect(LENGTH, WIDTH).extrude(HEIGHT)

# ============================================================
# EXPORT
# ============================================================
cq.exporters.export(base, "part_base.stl")
```

Rules:
- **No magic numbers in geometry code.** Every dimension is a named constant at the top.
- **Derived dimensions reference parameters.** `CAVITY_L = EXT_L - 2 * WALL`, not a hardcoded number.
- **Multi-part designs live in one script.** Shared parameters ensure parts fit together.
- **Each part exports as a separate STL.** One file per printable piece.
- **Docstring documents the full design.** Assembly sequence, sealing approach, hardware list, print setup.

## CadQuery Gotchas

- **`fillet()` fails on some edge configurations.** Always wrap in `try/except`.
- **`shell()` fails on complex geometry.** Prefer manual cavity cutting (`cutBlind`) for reliability.
- **Boolean cut cylinders must be longer than the boss.** Short cuts leave membranes. Add 1–2mm overlap.
- **Clearance holes must be oversized for FDM.** M3 → 3.4mm, M4 → 4.5mm. Nominal holes print too tight.
- **Hex nut pockets need ~0.1mm clearance per flat** vs nominal across-flats dimension.

## Waterproof Enclosure Design (IP67)

When a design is described as "waterproof", the project targets **IP67** per IEC 60529:

| Rating | Meaning |
|--------|---------|
| IP6x (dust) | Dust-tight — zero ingress after 8-hour test |
| IPx7 (water) | Survives immersion at 1m depth for 30 minutes |

Key design rules enforced during QA:

- **Gasket compression 25–35%** of free height. Crush limiters (pillar tops) control this.
- **Gasket must be continuous.** No bolt bosses or features breaking the seal perimeter.
- **No fastener paths through the sealed volume.** Water wicks down threads. Bolts go outside.
- **Through-bolt clamping direction matters.** Bolt head on lid → shaft through pillar → nut at flange base. Not the other way around.
- **Tongue-and-groove or stepped mating surfaces.** Never flat-to-flat.
- **All cable entries use IP67-rated glands.** One unsealed hole defeats the enclosure.
- **Always write out the full assembly sequence.** If any step is physically impossible, redesign.

See `CLAUDE.md` for the complete IP67 specification and the design mistakes registry.

## Reference Dimensions

### Raspberry Pi Boards

| Board | L×W×H (mm) | Mount pattern | Mount hole |
|-------|-----------|---------------|------------|
| Pi Zero 2W | 65×30×5 | 58×23 | M2.5 |
| Pi 4B / Pi 5 | 85×56×17 | 58×49 | M2.75 |
| Pi Pico | 51×21×1 | 47×11.4 | M2 |

### Cable Glands

| Type | Thread | Cable range | Boss OD |
|------|--------|-------------|---------|
| PG7 | M12×1.5 | 3–6.5mm | 18mm |
| PG9 | M16×1.5 | 4–8mm | 22mm |
| PG11 | M18×1.5 | 5–10mm | 24mm |
| PG13.5 | M20×1.5 | 6–12mm | 26mm |

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
| **TPU** | Gaskets, vibration damping | Shore hardness matters — 68D is semi-rigid, 95A is flexible. |
| **Nylon (PA)** | High strength, wear parts | Absorbs moisture — dry filament before printing. |

## Repository Structure

```
VibePrint3D/
├── SKILL.md          # Claude Code skill definition (installed to ~/.claude/skills/)
├── CLAUDE.md         # Project rules, IP67 spec, design mistakes registry
├── install.sh        # One-command skill installer
├── scripts/
│   ├── preview.py    # 4-view static PNG renderer (matplotlib + trimesh)
│   └── viewer.py     # Interactive Three.js HTML viewer
└── examples/
    └── *.py          # Working design scripts (reference implementations)
```

Generated files (STL, STEP, PNG, HTML) are gitignored — only source scripts are committed.

## License

MIT
