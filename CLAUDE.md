# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

VibePrint3D is a Claude Code skill that turns natural language descriptions of physical objects into 3D-printable STL files using CadQuery (Python, backed by OpenCASCADE). It follows a three-phase iterative design workflow: Base Shape → Features → Print Readiness, with visual self-review at each checkpoint.

## Critical: Conda Environment Required

CadQuery requires OpenCASCADE (OCP) bindings which only work with Python 3.11. **Always activate the conda env before running any CadQuery or preview script:**

```bash
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python your_script.py
```

Do NOT use system Python — it's too new for OCP wheels.

## Running Scripts

```bash
# Run a CadQuery design script (generates STL files)
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python examples/pizero_housing.py

# Generate 4-view static preview (for self-review)
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/preview.py input.stl output.png --title "Part Name"

# Generate interactive Three.js viewer (for user inspection, opens in browser)
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/viewer.py part1.stl part2.stl --title "Assembly Name"

# Package STLs into a single 3MF with material assignments (for slicer import)
eval "$(/opt/homebrew/Caskroom/miniforge/base/bin/conda shell.bash hook)" && conda activate cadquery && python scripts/export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o output.3mf --title "Part Name"
```

## Architecture

- **`SKILL.md`** — The Claude Code skill definition. Contains the three-phase workflow, self-review checklist, CadQuery cheat sheet, and reference dimensions for common components (Pi boards, cable glands, fasteners). This is what gets installed to `~/.claude/skills/cadquery-3dprint/`.

- **`scripts/preview.py`** — Renders a 2x2 grid of orthographic views (Front/Right/Top/Iso) from an STL using matplotlib+trimesh. Headless (no GPU). Claude uses this to self-review geometry before showing the user. Prints printability warnings (watertightness, thin dimensions).

- **`scripts/viewer.py`** — Generates a self-contained HTML file with Three.js WebGL viewer. Embeds STL data as base64 data URLs (no server needed). Supports multi-part viewing with distinct colors, orbit controls, wireframe toggle, grid, dimension HUD. Opens in browser automatically (`--no-open` to suppress).

- **`examples/`** — Working design scripts. `pizero_housing.py` is the reference example demonstrating multi-material enclosure design with through-bolt clamping, gasket grooves, cable glands, and interference checking.

- **`scripts/export_3mf.py`** — Packages multiple STL parts into a single `.3mf` file with material (filament) assignments. Uses `lib3mf` to create proper 3MF with named mesh objects, base material groups, and display colors. Parts appear pre-named and color-coded when opened in Bambu Studio / PrusaSlicer. Supports `file.stl:MATERIAL` syntax (e.g., `base.stl:PETG gasket.stl:TPU`). Built-in materials: PETG, TPU, PLA, ASA, ABS, NYLON.

- **`install.sh`** — Copies SKILL.md and scripts into `~/.claude/skills/cadquery-3dprint/`. Checks for conda/cadquery env.

## Design Script Conventions

All CadQuery design scripts must follow this structure:
1. Docstring explaining the design architecture and assembly sequence
2. All dimensions as named constants at the top (WALL, LENGTH, etc.)
3. Derived dimensions computed from parameters (CAVITY_LENGTH = LENGTH - 2*WALL)
4. Parts built as separate CadQuery objects in the same script for dimensional consistency
5. Each part exported as a separate STL
6. After STL export, run `export_3mf.py` to package all parts into a single `.3mf` with material assignments
7. Print confirmation of exported files

## Key CadQuery Gotchas

- Always `try/except` around `fillet()` — it fails on some edge configurations
- `shell()` can fail on complex geometry — prefer manual cavity cutting for reliability
- Cut cylinders must be longer than the boss to ensure full penetration through boolean ops
- Clearance holes for 3D printing are oversized: M3 → 3.4mm, M4 → 4.5mm
- Hex nut pockets need ~0.3mm clearance per side vs nominal across-flats dimension

## IP67 Waterproof Standard

When the user says "waterproof", they mean **IP67** per IEC 60529. Design every sealed enclosure to meet this standard.

### What IP67 Requires

| Digit | Rating | Meaning |
|-------|--------|---------|
| **6** (dust) | Dust-tight | Complete protection against dust ingress. Tested 8 hours in talcum powder chamber under negative pressure. Zero dust inside. |
| **7** (water) | Immersion 1m / 30min | Enclosure submerged with bottom at 1m depth and top at least 15cm below surface, for 30 minutes. No harmful water ingress. Tested with fresh water. |

### Key Rules

- **IP67 is NOT cumulative with IP65/IP66.** Passing immersion (IPx7) does not guarantee passing water jets (IPx5/IPx6). If both jet and immersion protection are needed, the device must be rated IP65/IP67 or IP66/IP67 (dual-rated).
- **Fresh water only.** IP67 does not cover salt water, chemicals, oils, or UV exposure. For marine use, material selection (PETG, ASA) and additional conformal coating may be needed.
- **Any design change invalidates the rating.** Changed a gasket, wall thickness, bolt pattern, or material? The IP67 claim needs re-verification.

### Design Requirements for IP67

1. **Gasket compression 25–35%** of free height. Under-compression leaks; over-compression causes permanent set and eventual failure.
2. **Even clamping force across the entire gasket perimeter.** The #1 cause of IP67 failure is uneven compression — water bypasses the seal where it's not fully compressed. Distribute bolt positions evenly around the perimeter.
3. **Tongue-and-groove or stepped mating surfaces.** Creates a controlled sealing path that prevents water from bypassing the gasket. Never rely on flat-to-flat mating alone.
4. **All connectors and cable entries must be IP67-rated themselves.** Use IP67 cable glands (PG7, PG9, etc.) with proper torque. An unsealed connector hole defeats the entire enclosure rating.
5. **Flat, smooth sealing surfaces.** FDM layer lines on mating faces can create leak paths. Print mating faces face-down for best surface finish, or sand/machine them flat.
6. **No through-holes into the sealed volume.** Every hole (bolt, screw, wire) that penetrates the enclosure wall is a potential leak path. Fasteners go outside the seal; wires go through glands.

## Enclosure Design Mistakes (Do Not Repeat)

These were caught during real design reviews. Apply these rules to ANY waterproof or sealed enclosure design:

1. **Gasket must be continuous.** Never place bolt bosses, standoffs, or features inside the gasket perimeter that break the seal into segments. Bolts go OUTSIDE the sealed area (external flange pillars), gasket stays an unbroken loop inside.

2. **No fastener paths through the sealed volume.** Bolt holes, nut pockets, and insert bores must never penetrate into the cavity interior. Water wicks down threads. All fastener paths must be entirely outside the body walls.

3. **Verify bolt length against the full stack-up.** Calculate: bolt head + lid thickness + pillar height + flange thickness + nut. If the shaft is longer than the stack, it will interfere with solid material or protrude where it shouldn't. Run an interference check with boolean intersection.

4. **Gasket compression needs crush limiters.** Without hard stops, the gasket will be crushed flat and fail. Pillar tops (or standoff shoulders) must be slightly taller than the body rim to limit gasket compression to 25–35% of its free height.

5. **Bulkhead holes must not conflict with cable glands.** Check that mounting holes on the same wall as a cable gland boss don't overlap. Move bulkhead holes to walls without cable entries.

6. **Through-bolt clamping direction matters.** The nut must be on the OPPOSITE side from the bolt head, with the entire clamped stack (lid + pillar + flange) in between. Nut-at-pillar-top creates a squeeze joint that doesn't compress the gasket. Correct: bolt head on lid top → shaft through pillar → nut captured on flange underside.

7. **Always think through the full assembly sequence.** Before finalizing any design, write out the step-by-step mechanical assembly: what goes in first, what orientation is the enclosure in, how are nuts held captive, what order are fasteners tightened. If any step is physically impossible, redesign.

## GitHub

- **Remote**: `Circus-Systems/VibePrint3D`
- **Branch**: `main`
- STL, STEP, PNG, and HTML files are gitignored — only source scripts are committed
