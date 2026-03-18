#!/usr/bin/env python3
"""
export_3mf.py — Package multiple STL parts into a single 3MF file with material assignments.

Each STL is imported as a named mesh object and assigned to a material (filament).
The resulting .3mf file can be opened directly in Bambu Studio / PrusaSlicer —
parts appear pre-named and color-coded by material. No manual filament assignment needed.

Usage:
    python export_3mf.py [options] part1.stl[:material] part2.stl[:material] ... -o output.3mf

    Each input is an STL file, optionally followed by :material_name to assign a filament.
    If no material is specified, the part is assigned to the first defined material.

Examples:
    # Auto-assign default material (PETG) to all parts:
    python export_3mf.py base.stl lid.stl gasket.stl -o housing.3mf

    # Assign specific materials:
    python export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o housing.3mf

    # Custom materials with colors:
    python export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o housing.3mf \
        --material "PETG=#646464" --material "TPU=#FF8C00"

    # With title metadata:
    python export_3mf.py base.stl:PETG lid.stl:PETG gasket.stl:TPU -o housing.3mf --title "Pi Zero Housing"

Built-in materials (used if no --material flags given):
    PETG  = dark grey  (#646464)
    TPU   = orange     (#FF8C00)
    PLA   = white      (#E0E0E0)
    ASA   = light grey (#A0A0A0)
    ABS   = black      (#303030)
    NYLON = cream      (#E8DCC8)
"""

import argparse
import os
import sys

import lib3mf
import trimesh


# Default material colors (sRGB hex)
DEFAULT_MATERIALS = {
    "PETG":  "#646464",
    "TPU":   "#FF8C00",
    "PLA":   "#E0E0E0",
    "ASA":   "#A0A0A0",
    "ABS":   "#303030",
    "NYLON": "#E8DCC8",
}


def hex_to_rgba(hex_color: str) -> tuple:
    """Convert '#RRGGBB' to (R, G, B, 255)."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def parse_input(spec: str) -> tuple:
    """Parse 'file.stl' or 'file.stl:MATERIAL' into (path, material_name)."""
    if ":" in spec:
        # Find last colon (handles Windows paths like C:\foo.stl:PETG)
        idx = spec.rfind(":")
        path = spec[:idx]
        material = spec[idx + 1:]
        # Sanity check — if 'path' doesn't look like a file, the colon was part of the path
        if not os.path.exists(path) and os.path.exists(spec):
            return spec, None
        return path, material.upper() if material else None
    return spec, None


def load_stl(path: str) -> trimesh.Trimesh:
    """Load an STL file via trimesh."""
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    mesh = trimesh.load(path)
    if not isinstance(mesh, trimesh.Trimesh):
        print(f"ERROR: {path} did not load as a single mesh", file=sys.stderr)
        sys.exit(1)
    return mesh


def add_mesh_to_model(model, wrapper, mesh: trimesh.Trimesh, name: str,
                      mat_group, mat_index: int):
    """Add a trimesh mesh to the lib3mf model with material assignment."""
    mesh_obj = model.AddMeshObject()
    mesh_obj.SetName(name)

    # Add vertices
    for v in mesh.vertices:
        pos = lib3mf.Position()
        pos.Coordinates[0] = float(v[0])
        pos.Coordinates[1] = float(v[1])
        pos.Coordinates[2] = float(v[2])
        mesh_obj.AddVertex(pos)

    # Add triangles
    for f in mesh.faces:
        tri = lib3mf.Triangle()
        tri.Indices[0] = int(f[0])
        tri.Indices[1] = int(f[1])
        tri.Indices[2] = int(f[2])
        mesh_obj.AddTriangle(tri)

    # Assign material at object level (all triangles get same material)
    mesh_obj.SetObjectLevelProperty(mat_group.GetResourceID(), mat_index)

    # Add to build
    transform = wrapper.GetIdentityTransform()
    model.AddBuildItem(mesh_obj, transform)

    return mesh_obj


def main():
    parser = argparse.ArgumentParser(
        description="Package STL parts into a multi-material 3MF file.",
        epilog="Example: python export_3mf.py base.stl:PETG gasket.stl:TPU -o housing.3mf",
    )
    parser.add_argument(
        "inputs", nargs="+", metavar="FILE.stl[:MATERIAL]",
        help="STL files to include. Append :MATERIAL to assign a filament (e.g., part.stl:PETG)."
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output .3mf file path."
    )
    parser.add_argument(
        "--material", action="append", default=[], metavar="NAME=#RRGGBB",
        help="Define a material with color (e.g., --material 'PETG=#646464'). "
             "Can be specified multiple times. Built-in defaults used if omitted."
    )
    parser.add_argument(
        "--title", default=None,
        help="Model title metadata (shown in slicer)."
    )
    parser.add_argument(
        "--default-material", default="PETG",
        help="Default material for parts without :MATERIAL suffix (default: PETG)."
    )
    args = parser.parse_args()

    # Build material registry
    materials = dict(DEFAULT_MATERIALS)
    for mat_spec in args.material:
        if "=" not in mat_spec:
            print(f"ERROR: Material spec must be NAME=#RRGGBB, got: {mat_spec}", file=sys.stderr)
            sys.exit(1)
        name, color = mat_spec.split("=", 1)
        materials[name.upper()] = color

    default_mat = args.default_material.upper()
    if default_mat not in materials:
        print(f"ERROR: Default material '{default_mat}' not defined. "
              f"Available: {', '.join(materials.keys())}", file=sys.stderr)
        sys.exit(1)

    # Parse inputs
    parts = []
    for spec in args.inputs:
        path, mat_name = parse_input(spec)
        if mat_name is None:
            mat_name = default_mat
        if mat_name not in materials:
            print(f"ERROR: Unknown material '{mat_name}' for {path}. "
                  f"Available: {', '.join(materials.keys())}", file=sys.stderr)
            sys.exit(1)
        base_name = os.path.splitext(os.path.basename(path))[0]
        parts.append((path, base_name, mat_name))

    # Create lib3mf model
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()

    # Set metadata
    if args.title:
        meta = model.GetMetaDataGroup()
        meta.AddMetaData("", "Title", args.title, "xs:string", True)

    # Create base material group with all materials used
    mat_group = model.AddBaseMaterialGroup()
    used_materials = sorted(set(mat for _, _, mat in parts))
    mat_indices = {}
    for mat_name in used_materials:
        color_hex = materials[mat_name]
        r, g, b, a = hex_to_rgba(color_hex)
        idx = mat_group.AddMaterial(mat_name, wrapper.RGBAToColor(r, g, b, a))
        mat_indices[mat_name] = idx

    # Load and add each part
    print(f"Packaging {len(parts)} parts into {args.output}:")
    for path, name, mat_name in parts:
        mesh = load_stl(path)
        add_mesh_to_model(model, wrapper, mesh, name, mat_group, mat_indices[mat_name])
        print(f"  {name:30s}  {mat_name:8s}  ({len(mesh.vertices)} verts, {len(mesh.faces)} tris)")

    # Write 3MF
    writer = model.QueryWriter("3mf")
    writer.WriteToFile(args.output)

    file_size = os.path.getsize(args.output)
    size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / 1024 / 1024:.1f} MB"
    print(f"\nExported: {args.output} ({size_str})")
    print(f"Materials: {', '.join(used_materials)}")
    print(f"\nOpen in Bambu Studio / PrusaSlicer — parts are pre-named and color-coded.")


if __name__ == "__main__":
    main()
