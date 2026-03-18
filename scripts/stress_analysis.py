#!/usr/bin/env python3
"""
stress_analysis.py — Linear elastic FEA stress analysis for 3D-printed parts.

Takes an STL file, volume-meshes it with Gmsh (tetrahedra), solves for
displacement and stress using scikit-fem, and outputs a von Mises stress
heatmap PNG plus a text report of hotspots and safety factors.

Usage:
    python stress_analysis.py input.stl [options]

Examples:
    # Basic analysis with defaults (PETG, 10N downward on top face):
    python stress_analysis.py housing_base.stl

    # Custom material and load:
    python stress_analysis.py bracket.stl --material ABS --force 50 --direction -z

    # Specify fixed and loaded faces by Z position:
    python stress_analysis.py part.stl --fix-face bottom --load-face top --force 25

    # Custom material properties:
    python stress_analysis.py part.stl --youngs-modulus 1200 --poisson 0.35 --yield-stress 40

    # Finer mesh for more accuracy:
    python stress_analysis.py part.stl --mesh-min 0.5 --mesh-max 2.0

Output:
    <input>_stress.png  — Von Mises heatmap (4-view: Front/Right/Top/Iso)
    Console report with max stress, safety factor, hotspot locations

Dependencies:
    pip install gmsh scikit-fem meshio trimesh matplotlib numpy

Limitations:
    - Linear elastic only (no creep, fatigue, or plastic deformation)
    - Isotropic material model (real FDM prints are anisotropic — weaker between layers)
    - Results are a useful approximation, not a certification tool
"""

import argparse
import os
import sys
import tempfile

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.cm as cm

import gmsh
import meshio
import trimesh

from skfem import *
from skfem.models.elasticity import linear_elasticity, lame_parameters


# ============================================================
# Material database (E in MPa, yield in MPa)
# ============================================================
MATERIALS = {
    "PETG":  {"E": 2100, "nu": 0.33, "yield": 50,  "name": "PETG"},
    "PLA":   {"E": 2300, "nu": 0.36, "yield": 60,  "name": "PLA"},
    "ABS":   {"E": 2100, "nu": 0.35, "yield": 40,  "name": "ABS"},
    "ASA":   {"E": 2000, "nu": 0.35, "yield": 42,  "name": "ASA"},
    "NYLON": {"E": 1700, "nu": 0.39, "yield": 70,  "name": "Nylon (PA)"},
    "TPU":   {"E": 100,  "nu": 0.48, "yield": 25,  "name": "TPU 68D"},
}


def repair_stl(path: str) -> str:
    """Repair STL if not watertight. Returns path to usable STL."""
    mesh = trimesh.load(path)
    if not mesh.is_watertight:
        print(f"  STL not watertight — repairing...")
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fill_holes(mesh)
        if not mesh.is_watertight:
            print(f"  WARNING: Could not fully repair. Meshing may fail.")
        tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        mesh.export(tmp.name)
        return tmp.name
    return path


def mesh_stl(stl_path: str, mesh_min: float, mesh_max: float, msh_path: str) -> dict:
    """Volume-mesh an STL into tetrahedra using Gmsh. Returns mesh stats."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("fea")
    gmsh.merge(stl_path)

    surfaces = gmsh.model.getEntities(2)
    sl = gmsh.model.geo.addSurfaceLoop([s[1] for s in surfaces])
    gmsh.model.geo.addVolume([sl])
    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_min)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_max)
    gmsh.option.setNumber("Mesh.ElementOrder", 1)  # Linear tets
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)    # Delaunay
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    gmsh.model.mesh.generate(3)

    # Stats
    node_tags, _, _ = gmsh.model.mesh.getNodes()
    _, elem_tags, _ = gmsh.model.mesh.getElements(3)
    n_nodes = len(node_tags)
    n_tets = len(elem_tags[0]) if len(elem_tags) > 0 else 0

    gmsh.write(msh_path)
    gmsh.finalize()

    return {"nodes": n_nodes, "tets": n_tets}


def load_tet_mesh(msh_path: str):
    """Load a Gmsh MSH file and return scikit-fem MeshTet."""
    mio = meshio.read(msh_path)
    tet_cells = None
    for c in mio.cells:
        if c.type == "tetra":
            tet_cells = c.data
            break
    if tet_cells is None:
        print("ERROR: No tetrahedral elements found in mesh.", file=sys.stderr)
        sys.exit(1)
    return MeshTet(mio.points.T, tet_cells.T), mio.points, tet_cells


def select_face_nodes(points: np.ndarray, face: str, tolerance: float = 0.5) -> np.ndarray:
    """Select nodes on a face of the bounding box."""
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    if face == "bottom":
        return np.where(z < z.min() + tolerance)[0]
    elif face == "top":
        return np.where(z > z.max() - tolerance)[0]
    elif face == "left":
        return np.where(x < x.min() + tolerance)[0]
    elif face == "right":
        return np.where(x > x.max() - tolerance)[0]
    elif face == "front":
        return np.where(y < y.min() + tolerance)[0]
    elif face == "back":
        return np.where(y > y.max() - tolerance)[0]
    else:
        print(f"ERROR: Unknown face '{face}'. Use: bottom/top/left/right/front/back", file=sys.stderr)
        sys.exit(1)


def solve_fea(mesh, basis, lam, mu, fixed_nodes, loaded_nodes, force, direction):
    """Solve linear elastic FEA. Returns displacement vector."""
    # Assemble stiffness
    K = asm(linear_elasticity(lam, mu), basis)

    # Fixed DOFs (all 3 components)
    fixed_dofs = np.concatenate([
        basis.nodal_dofs[0][fixed_nodes],
        basis.nodal_dofs[1][fixed_nodes],
        basis.nodal_dofs[2][fixed_nodes],
    ])

    # Load vector
    f = np.zeros(basis.N)
    dir_map = {
        "+x": 0, "-x": 0, "+y": 1, "-y": 1, "+z": 2, "-z": 2,
        "x": 0, "y": 1, "z": 2,
    }
    sign_map = {
        "+x": 1, "-x": -1, "+y": 1, "-y": -1, "+z": 1, "-z": -1,
        "x": 1, "y": 1, "z": -1,  # default: negative (downward/inward)
    }
    axis = dir_map.get(direction, 2)
    sign = sign_map.get(direction, -1)

    force_per_node = (force * sign) / max(len(loaded_nodes), 1)
    for n in loaded_nodes:
        f[basis.nodal_dofs[axis][n]] = force_per_node

    # Solve
    u = solve(*condense(K, f, D=fixed_dofs))
    return u


def compute_von_mises(basis, u, lam, mu):
    """Compute von Mises stress per element."""
    from skfem.helpers import sym_grad

    @Functional
    def vm_func(w):
        eps = sym_grad(w["disp"])
        trace_eps = eps[0, 0] + eps[1, 1] + eps[2, 2]
        # Stress tensor (Hooke's law, isotropic)
        sig = np.zeros_like(eps)
        for i in range(3):
            for j in range(3):
                sig[i, j] = lam * trace_eps * (1 if i == j else 0) + 2 * mu * eps[i, j]
        # Deviatoric stress
        tr_sig = sig[0, 0] + sig[1, 1] + sig[2, 2]
        s = np.zeros_like(sig)
        for i in range(3):
            for j in range(3):
                s[i, j] = sig[i, j] - (tr_sig / 3.0) * (1 if i == j else 0)
        # Von Mises
        vm_sq = 1.5 * sum(s[i, j] * s[i, j] for i in range(3) for j in range(3))
        return np.sqrt(np.maximum(vm_sq, 0))

    uh = basis.interpolate(u)
    return vm_func.elemental(basis, disp=uh)


def render_stress_heatmap(points, cells, vm_stress, output_path, title, yield_stress):
    """Render 4-view von Mises stress heatmap on the surface."""
    # Extract surface triangles from tets (faces on the boundary)
    tri_mesh = trimesh.Trimesh(vertices=points, faces=[], process=False)

    # Build all tet faces and find boundary faces (shared by only 1 tet)
    face_combos = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    face_to_tets = {}
    for tet_idx, tet in enumerate(cells):
        for combo in face_combos:
            face = tuple(sorted([tet[combo[0]], tet[combo[1]], tet[combo[2]]]))
            if face not in face_to_tets:
                face_to_tets[face] = []
            face_to_tets[face].append(tet_idx)

    # Boundary faces: shared by exactly 1 tet
    boundary_faces = []
    boundary_stress = []
    for face, tet_indices in face_to_tets.items():
        if len(tet_indices) == 1:
            boundary_faces.append(face)
            boundary_stress.append(vm_stress[tet_indices[0]])

    boundary_faces = np.array(boundary_faces)
    boundary_stress = np.array(boundary_stress)

    # Normalize stress for colormap
    vmin = 0
    vmax = max(vm_stress.max(), yield_stress * 0.5)  # Scale to show detail
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.colormaps.get_cmap("RdYlGn_r")  # Red = high stress, Green = low

    # 4-view layout: Front, Right, Top, Isometric
    views = [
        ("Front (-Y)", 0, 0),
        ("Right (+X)", 0, 90),
        ("Top (+Z)", 90, 0),
        ("Iso", 30, -45),
    ]

    fig = plt.figure(figsize=(14, 14))
    fig.suptitle(f"{title}\nVon Mises Stress (MPa) — Yield: {yield_stress} MPa",
                 fontsize=12, fontweight="bold")

    for idx, (label, elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, idx + 1, projection="3d")

        # Create colored polygon collection
        verts = points[boundary_faces]
        colors = cmap(norm(boundary_stress))

        poly = Poly3DCollection(verts, alpha=0.9)
        poly.set_facecolor(colors)
        poly.set_edgecolor("none")
        ax.add_collection3d(poly)

        # Set axis limits
        max_range = np.ptp(points, axis=0).max() / 2
        mid = points.mean(axis=0)
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

    # Colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=fig.axes, shrink=0.5, pad=0.08, label="Von Mises Stress (MPa)")

    # Add yield line annotation
    if yield_stress <= vmax:
        cbar.ax.axhline(y=yield_stress, color="red", linewidth=2, linestyle="--")
        cbar.ax.text(1.5, yield_stress, f" Yield ({yield_stress})", color="red",
                     fontsize=8, va="center", transform=cbar.ax.get_yaxis_transform())

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="FEA stress analysis for 3D-printed parts.")
    parser.add_argument("stl", help="Input STL file")
    parser.add_argument("--material", default="PETG", choices=list(MATERIALS.keys()),
                        help="Material preset (default: PETG)")
    parser.add_argument("--youngs-modulus", type=float, default=None,
                        help="Override Young's modulus (MPa)")
    parser.add_argument("--poisson", type=float, default=None,
                        help="Override Poisson's ratio")
    parser.add_argument("--yield-stress", type=float, default=None,
                        help="Override yield stress (MPa)")
    parser.add_argument("--fix-face", default="bottom",
                        help="Face to fix: bottom/top/left/right/front/back (default: bottom)")
    parser.add_argument("--load-face", default="top",
                        help="Face to load: bottom/top/left/right/front/back (default: top)")
    parser.add_argument("--force", type=float, default=10.0,
                        help="Total applied force in Newtons (default: 10)")
    parser.add_argument("--direction", default="-z",
                        help="Force direction: +x/-x/+y/-y/+z/-z (default: -z)")
    parser.add_argument("--mesh-min", type=float, default=1.0,
                        help="Minimum mesh element size in mm (default: 1.0)")
    parser.add_argument("--mesh-max", type=float, default=3.0,
                        help="Maximum mesh element size in mm (default: 3.0)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output PNG path (default: <input>_stress.png)")
    parser.add_argument("--title", default=None,
                        help="Plot title (default: filename)")
    args = parser.parse_args()

    # Resolve paths
    stl_path = os.path.abspath(args.stl)
    base_name = os.path.splitext(os.path.basename(stl_path))[0]
    output_path = args.output or os.path.join(os.path.dirname(stl_path), f"{base_name}_stress.png")
    title = args.title or base_name

    # Material
    mat = MATERIALS[args.material]
    E = args.youngs_modulus or mat["E"]
    nu = args.poisson or mat["nu"]
    yield_stress = args.yield_stress or mat["yield"]
    lam, mu = lame_parameters(E, nu)

    print("=" * 60)
    print(f"FEA Stress Analysis — {title}")
    print("=" * 60)
    print(f"  Material:    {mat['name']} (E={E} MPa, ν={nu}, σ_y={yield_stress} MPa)")
    print(f"  Force:       {args.force} N in {args.direction} direction")
    print(f"  Fixed face:  {args.fix_face}")
    print(f"  Loaded face: {args.load_face}")
    print(f"  Mesh size:   {args.mesh_min}–{args.mesh_max} mm")
    print()

    # Step 1: Repair STL if needed
    print("Step 1: Checking STL...")
    clean_path = repair_stl(stl_path)
    src_mesh = trimesh.load(clean_path)
    print(f"  Vertices: {len(src_mesh.vertices)}, Faces: {len(src_mesh.faces)}")
    print(f"  Watertight: {src_mesh.is_watertight}")
    print(f"  Bounding box: {src_mesh.bounds[0]} to {src_mesh.bounds[1]}")
    print()

    # Step 2: Tet mesh
    print("Step 2: Volume meshing (Gmsh)...")
    msh_path = tempfile.NamedTemporaryFile(suffix=".msh", delete=False).name
    stats = mesh_stl(clean_path, args.mesh_min, args.mesh_max, msh_path)
    print(f"  Nodes: {stats['nodes']}, Tets: {stats['tets']}")
    print()

    # Step 3: Load mesh into scikit-fem
    print("Step 3: Setting up FEA...")
    m, points, cells = load_tet_mesh(msh_path)
    e = ElementVector(ElementTetP1())
    ib = Basis(m, e)
    print(f"  DOFs: {ib.N}")

    # Select faces
    fixed_nodes = select_face_nodes(points, args.fix_face)
    loaded_nodes = select_face_nodes(points, args.load_face)
    print(f"  Fixed nodes ({args.fix_face}): {len(fixed_nodes)}")
    print(f"  Loaded nodes ({args.load_face}): {len(loaded_nodes)}")
    print()

    # Step 4: Solve
    print("Step 4: Solving...")
    u = solve_fea(m, ib, lam, mu, fixed_nodes, loaded_nodes, args.force, args.direction)
    max_disp = np.max(np.abs(u))
    print(f"  Max displacement: {max_disp:.6f} mm")
    print()

    # Step 5: Von Mises stress
    print("Step 5: Computing von Mises stress...")
    vm = compute_von_mises(ib, u, lam, mu)
    print(f"  Stress range: {vm.min():.2f} – {vm.max():.2f} MPa")
    print(f"  Mean stress:  {vm.mean():.2f} MPa")
    print(f"  95th %%ile:    {np.percentile(vm, 95):.2f} MPa")
    print()

    # Step 6: Safety factor
    safety = yield_stress / max(vm.max(), 1e-10)
    print("Step 6: Results")
    print(f"  Max von Mises:   {vm.max():.2f} MPa")
    print(f"  Yield stress:    {yield_stress:.0f} MPa ({mat['name']})")
    print(f"  Safety factor:   {safety:.1f}x", end="")
    if safety >= 3.0:
        print(" ✅ (good)")
    elif safety >= 1.5:
        print(" ⚠️  (marginal)")
    elif safety >= 1.0:
        print(" ⚠️  (risky — near yield)")
    else:
        print(" ❌ (EXCEEDS YIELD — will fail)")
    print()

    # Hotspot locations (top 5 elements by stress)
    top_indices = np.argsort(vm)[-5:][::-1]
    print("  Stress hotspots (top 5 elements):")
    for rank, idx in enumerate(top_indices, 1):
        centroid = points[cells[idx]].mean(axis=0)
        print(f"    {rank}. {vm[idx]:.2f} MPa at ({centroid[0]:.1f}, {centroid[1]:.1f}, {centroid[2]:.1f})")
    print()

    # Step 7: Render heatmap
    print("Step 7: Rendering heatmap...")
    render_stress_heatmap(points, cells, vm, output_path, title, yield_stress)
    print(f"  Saved: {output_path}")
    print()
    print("=" * 60)

    # Cleanup
    os.unlink(msh_path)
    if clean_path != stl_path:
        os.unlink(clean_path)


if __name__ == "__main__":
    main()
