#!/usr/bin/env python3
"""
Multi-view STL preview renderer for cadquery-3dprint skill.

Renders a 2x2 grid of orthographic + isometric views from an STL file.
Uses matplotlib's 3D plotting (no OpenGL/GPU required).

Usage:
    python preview.py input.stl output.png
    python preview.py input.stl output.png --title "My Part - Phase 1"
"""

import sys
import argparse
import numpy as np

try:
    import trimesh
except ImportError:
    print("ERROR: trimesh not installed. Run: pip install trimesh")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')  # headless rendering
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError:
    print("ERROR: matplotlib not installed. Run: pip install matplotlib")
    sys.exit(1)


def load_mesh(stl_path):
    """Load STL and return trimesh object."""
    mesh = trimesh.load(stl_path)
    if isinstance(mesh, trimesh.Scene):
        # If it's a scene, combine all meshes
        mesh = trimesh.util.concatenate(
            [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        )
    return mesh


def render_view(ax, mesh, elev, azim, title, show_axes=True):
    """Render a single view of the mesh on a matplotlib 3D axis."""
    verts = mesh.vertices
    faces = mesh.faces

    # Create polygon collection
    poly = Poly3DCollection(
        verts[faces],
        alpha=0.75,
        facecolor='#4a90d9',
        edgecolor='#1a3a6a',
        linewidth=0.05,
    )
    ax.add_collection3d(poly)

    # Set axis limits based on mesh extents
    center = verts.mean(axis=0)
    scale = verts.max(axis=0) - verts.min(axis=0)
    max_range = scale.max() / 2 * 1.15  # 15% padding

    ax.set_xlim(center[0] - max_range, center[0] + max_range)
    ax.set_ylim(center[1] - max_range, center[1] + max_range)
    ax.set_zlim(center[2] - max_range, center[2] + max_range)

    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=8)

    if show_axes:
        ax.set_xlabel('X', fontsize=9, labelpad=2)
        ax.set_ylabel('Y', fontsize=9, labelpad=2)
        ax.set_zlabel('Z', fontsize=9, labelpad=2)
        ax.tick_params(labelsize=7)
    else:
        ax.set_axis_off()

    # Match aspect ratio
    ax.set_box_aspect(scale if scale.min() > 0 else [1, 1, 1])


def render_dimensions_text(mesh):
    """Return a dimensions summary string."""
    bb = mesh.bounding_box.extents
    vol = mesh.volume
    return (
        f"Bounding box: {bb[0]:.1f} × {bb[1]:.1f} × {bb[2]:.1f} mm\n"
        f"Volume: {vol:.0f} mm³  |  "
        f"Triangles: {len(mesh.faces):,}  |  "
        f"Watertight: {'Yes' if mesh.is_watertight else 'NO'}"
    )


def render_preview(stl_path, output_path, title=None):
    """Render 4-view preview and save as PNG."""
    mesh = load_mesh(stl_path)

    fig = plt.figure(figsize=(16, 16), facecolor='white')

    # Title
    if title:
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Define views: (name, elevation, azimuth)
    views = [
        ("Front (XZ)",    0,    0),
        ("Right (YZ)",    0,   90),
        ("Top (XY)",     90,    0),
        ("Isometric",    25,  -45),
    ]

    for i, (name, elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, i + 1, projection='3d')
        render_view(ax, mesh, elev, azim, name)

    # Add dimensions text at bottom
    dims_text = render_dimensions_text(mesh)
    fig.text(0.5, 0.01, dims_text, ha='center', fontsize=11,
             fontfamily='monospace', color='#444444',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Preview saved: {output_path}")
    print(dims_text)

    # Printability warnings
    warnings = []
    if not mesh.is_watertight:
        warnings.append("⚠ Mesh is NOT watertight — may have holes or non-manifold edges")

    bb = mesh.bounding_box.extents
    if min(bb) < 1.2:
        warnings.append(f"⚠ Thinnest dimension is {min(bb):.1f}mm — may be too thin to print")

    if warnings:
        print("\nPrintability warnings:")
        for w in warnings:
            print(f"  {w}")

    return mesh


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render multi-view STL preview")
    parser.add_argument("input", help="Input STL file path")
    parser.add_argument("output", help="Output PNG file path")
    parser.add_argument("--title", help="Title text for the preview", default=None)
    args = parser.parse_args()

    render_preview(args.input, args.output, args.title)
