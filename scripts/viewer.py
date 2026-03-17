#!/usr/bin/env python3
"""
Interactive 3D STL viewer — opens in the browser.

Generates a self-contained HTML file with Three.js that renders the STL
with orbit controls, grid, and dimension annotations. Opens automatically.

Usage:
    python viewer.py part.stl
    python viewer.py part.stl --title "Pi Zero Enclosure — Base"
    python viewer.py part.stl --no-open  # generate HTML without opening
    python viewer.py base.stl lid.stl    # multi-part view
"""

import sys
import os
import argparse
import json
import struct
import tempfile
import webbrowser
import base64


def read_binary_stl(path):
    """Read a binary STL file and return vertices and faces as lists."""
    with open(path, 'rb') as f:
        header = f.read(80)
        num_triangles = struct.unpack('<I', f.read(4))[0]
        
        vertices = []
        faces = []
        vertex_map = {}
        
        for i in range(num_triangles):
            normal = struct.unpack('<3f', f.read(12))
            v1 = struct.unpack('<3f', f.read(12))
            v2 = struct.unpack('<3f', f.read(12))
            v3 = struct.unpack('<3f', f.read(12))
            attr = struct.unpack('<H', f.read(2))
            
            face_indices = []
            for v in [v1, v2, v3]:
                key = (round(v[0], 6), round(v[1], 6), round(v[2], 6))
                if key not in vertex_map:
                    vertex_map[key] = len(vertices)
                    vertices.append(list(v))
                face_indices.append(vertex_map[key])
            faces.append(face_indices)
    
    return vertices, faces


def read_ascii_stl(path):
    """Read an ASCII STL file and return vertices and faces."""
    vertices = []
    faces = []
    vertex_map = {}
    
    with open(path, 'r') as f:
        current_face = []
        for line in f:
            line = line.strip()
            if line.startswith('vertex'):
                parts = line.split()
                v = (round(float(parts[1]), 6), round(float(parts[2]), 6), round(float(parts[3]), 6))
                if v not in vertex_map:
                    vertex_map[v] = len(vertices)
                    vertices.append(list(v))
                current_face.append(vertex_map[v])
            elif line.startswith('endfacet'):
                if len(current_face) == 3:
                    faces.append(current_face)
                current_face = []
    
    return vertices, faces


def read_stl(path):
    """Read STL file (auto-detect binary vs ASCII)."""
    with open(path, 'rb') as f:
        header = f.read(80)
    
    # Check if ASCII
    try:
        with open(path, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('solid') and not first_line.startswith('solid \x00'):
                return read_ascii_stl(path)
    except:
        pass
    
    return read_binary_stl(path)


def stl_to_data_url(path):
    """Convert STL file to base64 data URL for embedding."""
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    return f"data:application/octet-stream;base64,{b64}"


def generate_html(stl_paths, title=None):
    """Generate self-contained HTML with Three.js viewer."""
    
    # Prepare STL data URLs and colors
    colors = ['#4a90d9', '#d94a4a', '#4ad97a', '#d9a84a', '#9a4ad9', '#4ad9d9']
    parts_json = []
    filenames = []
    for i, path in enumerate(stl_paths):
        data_url = stl_to_data_url(path)
        name = os.path.splitext(os.path.basename(path))[0]
        color = colors[i % len(colors)]
        parts_json.append({"url": data_url, "name": name, "color": color})
        filenames.append(name)
    
    if not title:
        title = " + ".join(filenames)
    
    parts_js = json.dumps(parts_json)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ 
    background: #1a1a2e; 
    color: #e0e0e0; 
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif;
    overflow: hidden;
  }}
  #viewer {{ width: 100vw; height: 100vh; display: block; }}
  #hud {{
    position: fixed; top: 16px; left: 16px;
    background: rgba(10, 10, 30, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 13px;
    line-height: 1.7;
    max-width: 320px;
    z-index: 10;
  }}
  #hud h2 {{ 
    font-size: 15px; margin-bottom: 8px; 
    color: #fff; font-weight: 600;
  }}
  #hud .dim {{ color: #8ab4f8; }}
  #hud .warn {{ color: #f4a261; }}
  #hud .ok {{ color: #6bcf7f; }}
  #controls {{
    position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
    background: rgba(10, 10, 30, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 12px;
    color: #888;
    z-index: 10;
  }}
  #controls span {{ margin: 0 12px; }}
  button {{
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e0e0e0;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    margin: 0 4px;
  }}
  button:hover {{ background: rgba(255,255,255,0.2); }}
  button.active {{ background: rgba(74,144,217,0.4); border-color: #4a90d9; }}
</style>
</head>
<body>
<div id="viewer"></div>
<div id="hud">
  <h2>{title}</h2>
  <div id="dims">Loading...</div>
</div>
<div id="controls">
  <button onclick="setView('front')">Front</button>
  <button onclick="setView('right')">Right</button>
  <button onclick="setView('top')">Top</button>
  <button onclick="setView('iso')" class="active">Iso</button>
  <span>|</span>
  <button onclick="toggleWireframe()" id="btnWire">Wireframe</button>
  <button onclick="toggleGrid()" id="btnGrid">Grid</button>
  <span style="color:#555">Scroll=Zoom · Drag=Orbit · Shift+Drag=Pan</span>
</div>

<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/"
  }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ STLLoader }} from 'three/addons/loaders/STLLoader.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 10000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
document.getElementById('viewer').appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

// Lighting
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambient);
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(100, 200, 150);
dirLight.castShadow = true;
scene.add(dirLight);
const dirLight2 = new THREE.DirectionalLight(0x8ab4f8, 0.4);
dirLight2.position.set(-100, -50, -100);
scene.add(dirLight2);

// Grid
const grid = new THREE.GridHelper(200, 20, 0x444466, 0x333355);
grid.rotation.x = 0;  // XY plane
scene.add(grid);
let gridVisible = true;

// Load parts
const parts = {parts_js};
const loader = new STLLoader();
const meshes = [];
let globalBox = new THREE.Box3();

let loaded = 0;
parts.forEach((part, idx) => {{
  loader.load(part.url, (geometry) => {{
    geometry.computeVertexNormals();
    const material = new THREE.MeshPhysicalMaterial({{
      color: new THREE.Color(part.color),
      metalness: 0.1,
      roughness: 0.5,
      clearcoat: 0.3,
      side: THREE.DoubleSide,
    }});
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = part.name;
    scene.add(mesh);
    meshes.push(mesh);
    
    const box = new THREE.Box3().setFromObject(mesh);
    globalBox.union(box);
    
    loaded++;
    if (loaded === parts.length) {{
      fitCamera();
      updateHUD();
    }}
  }});
}});

function fitCamera() {{
  const center = new THREE.Vector3();
  globalBox.getCenter(center);
  const size = new THREE.Vector3();
  globalBox.getSize(size);
  const maxDim = Math.max(size.x, size.y, size.z);
  
  controls.target.copy(center);
  camera.position.set(
    center.x + maxDim * 0.8,
    center.y + maxDim * 0.6,
    center.z + maxDim * 1.0
  );
  controls.update();
  
  // Position grid at bottom of model
  grid.position.y = globalBox.min.z;
  grid.position.x = center.x;
  grid.position.z = center.y;
  
  // Scale grid to fit
  const gridScale = maxDim / 100;
  grid.scale.set(gridScale, gridScale, gridScale);
}}

function updateHUD() {{
  const size = new THREE.Vector3();
  globalBox.getSize(size);
  const dimsEl = document.getElementById('dims');
  
  let html = `<span class="dim">Bounding box: ${{size.x.toFixed(1)}} × ${{size.y.toFixed(1)}} × ${{size.z.toFixed(1)}} mm</span><br>`;
  html += `Parts: ${{meshes.length}}`;
  meshes.forEach(m => {{
    html += `<br>&nbsp;&nbsp;· ${{m.name}}`;
  }});
  dimsEl.innerHTML = html;
}}

// View presets
window.setView = function(view) {{
  const center = new THREE.Vector3();
  globalBox.getCenter(center);
  const size = new THREE.Vector3();
  globalBox.getSize(size);
  const d = Math.max(size.x, size.y, size.z) * 1.5;
  
  document.querySelectorAll('#controls button').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  
  switch(view) {{
    case 'front':
      camera.position.set(center.x, center.y - d, center.z);
      break;
    case 'right':
      camera.position.set(center.x + d, center.y, center.z);
      break;
    case 'top':
      camera.position.set(center.x, center.y, center.z + d);
      break;
    case 'iso':
      camera.position.set(center.x + d*0.6, center.y - d*0.6, center.z + d*0.5);
      break;
  }}
  controls.target.copy(center);
  controls.update();
}};

window.toggleWireframe = function() {{
  const btn = document.getElementById('btnWire');
  meshes.forEach(m => {{ m.material.wireframe = !m.material.wireframe; }});
  btn.classList.toggle('active');
}};

window.toggleGrid = function() {{
  gridVisible = !gridVisible;
  grid.visible = gridVisible;
  document.getElementById('btnGrid').classList.toggle('active');
}};

// Resize
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});

// Animate
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Interactive 3D STL viewer")
    parser.add_argument("stl_files", nargs='+', help="STL file(s) to view")
    parser.add_argument("--title", help="Title for the viewer", default=None)
    parser.add_argument("--no-open", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--output", "-o", help="Output HTML path (default: auto-generated temp file)")
    args = parser.parse_args()
    
    # Verify files exist
    for path in args.stl_files:
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}")
            sys.exit(1)
    
    html = generate_html(args.stl_files, title=args.title)
    
    if args.output:
        out_path = args.output
    else:
        out_path = os.path.join(
            os.path.dirname(args.stl_files[0]),
            "viewer.html"
        )
    
    with open(out_path, 'w') as f:
        f.write(html)
    
    print(f"Viewer saved: {out_path}")
    
    if not args.no_open:
        webbrowser.open(f"file://{os.path.abspath(out_path)}")
        print("Opened in browser.")
    else:
        print("Use --no-open was set. Open the HTML file manually.")


if __name__ == "__main__":
    main()
