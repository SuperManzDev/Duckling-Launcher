"""Build a dimensional celestial Star Sail with the old cuboid as fallback.

The sail is a curved, two-sided cloth surface on a real mast and yard, not a
flat texture card. Small constellation inlays and swinging crystal drops give
it a readable silhouette from the back and both sides.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of, rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


NAVY = (22, 48, 91)
BLUE = (38, 92, 151)
AZURE = (54, 144, 195)
CYAN = (105, 204, 223)
PALE = (175, 239, 236)
GOLD = (239, 182, 87)
IVORY = (255, 237, 177)
FRAME = (82, 62, 106)


def cloth_point(sign, u, v):
    """Billowing sail position, u=0 at the mast and v=1 at the yard."""
    # A broad yard and narrow lower point give it a proper mainsail profile.
    # The raised belly is apparent from the side.
    width = 1.0 + 7.2 * v ** 0.70
    x = sign * width * u
    y = 12.6 + 16.7 * v
    z = 5.3 + 1.35 * u + 2.25 * math.sin(math.pi * u) * math.sin(math.pi * v)
    return np.array((x, y, z), dtype=float)


def jewel(mesh, x, y, z, radius, colors=(CYAN, PALE, BLUE, IVORY)):
    ring = [(x, y + radius, z), (x + radius * 0.72, y, z),
            (x, y - radius * 1.35, z), (x - radius * 0.72, y, z)]
    rear = (x, y, z - radius * 0.65)
    front = (x, y, z + radius * 0.72)
    for i, color in enumerate(colors):
        nxt = (i + 1) % 4
        mesh.tri(front, ring[i], ring[nxt], color, (0, 0, 1))
        mesh.tri(rear, ring[nxt], ring[i], BLUE, (0, 0, -1))


def paint_sail_half(mesh, sign):
    back = np.array((0, 0, 0.30))
    for i in range(8):
        for j in range(8):
            u0, u1 = i / 8, (i + 1) / 8
            v0, v1 = j / 8, (j + 1) / 8
            p00 = cloth_point(sign, u0, v0)
            p10 = cloth_point(sign, u1, v0)
            p11 = cloth_point(sign, u1, v1)
            p01 = cloth_point(sign, u0, v1)
            # A restrained set of broad facets follows the curved fabric.
            tones = (NAVY, BLUE, AZURE, CYAN, PALE)
            tone = tones[min(4, max(0, round(1 + 2.5 * v0 + 0.7 * u0)))]
            shade = tones[max(0, min(4, round(0.5 + 2.4 * v0 + 0.5 * u0)))]
            mesh.tri(p00, p10, p11, tone, (0, 0, 1))
            mesh.tri(p00, p11, p01, shade, (0, 0, 1))
            mesh.tri(p00 - back, p11 - back, p10 - back, BLUE, (0, 0, -1))
            mesh.tri(p00 - back, p01 - back, p11 - back, NAVY, (0, 0, -1))

    # A closed perimeter and raised spar ensure the cloth has an actual side
    # profile, including when it is viewed edge-on in the player preview.
    for axis, fixed in (("v", 0.0), ("v", 1.0), ("u", 1.0)):
        for i in range(8):
            a, b = i / 8, (i + 1) / 8
            p = cloth_point(sign, a, fixed) if axis == "v" else cloth_point(sign, fixed, a)
            q = cloth_point(sign, b, fixed) if axis == "v" else cloth_point(sign, fixed, b)
            mesh.tri(p, q, q - back, FRAME)
            mesh.tri(p, q - back, p - back, NAVY)
            radius = 0.31 if fixed == 1.0 else 0.20
            mesh.beam(p + [0, 0, 0.20], q + [0, 0, 0.20], radius, radius,
                      (IVORY, GOLD, FRAME, GOLD, PALE))

    # Taut stitched ribs catch light on the curve without becoming bars.
    for u in (0.30, 0.62):
        for i in range(6):
            p = cloth_point(sign, u, i / 6) + [0, 0, 0.23]
            q = cloth_point(sign, u, (i + 1) / 6) + [0, 0, 0.23]
            mesh.beam(p, q, 0.13, 0.13, (PALE, GOLD, BLUE, GOLD, CYAN))

    # A constellation that follows the fabric rather than floating in front.
    stars = [(0.24, 0.73), (0.51, 0.52), (0.75, 0.77), (0.83, 0.33)]
    for (u, v) in stars:
        x, y, z = cloth_point(sign, u, v)
        jewel(mesh, x, y, z + 0.33, 0.28, (IVORY, GOLD, PALE, GOLD))
    for (u0, v0), (u1, v1) in zip(stars, stars[1:]):
        p = cloth_point(sign, u0, v0) + [0, 0, 0.29]
        q = cloth_point(sign, u1, v1) + [0, 0, 0.29]
        mesh.beam(p, q, 0.09, 0.09, (PALE, GOLD, BLUE, GOLD, PALE))


def sail():
    mesh = Sculpture()
    for sign in (-1, 1):
        paint_sail_half(mesh, sign)
    # Center seam is wrapped in a thin metal cord.
    mesh.beam(cloth_point(1, 0, 0), cloth_point(1, 0, 1),
              0.20, 0.20, (IVORY, GOLD, FRAME, GOLD, IVORY))
    return mesh


def harness():
    mesh = Sculpture()
    # Back plate, two shoulder brackets, mast and a curved raised yard.
    for sign in (-1, 1):
        mesh.beam((0, 21.7, 3.0), (sign * 2.8, 23.4, 4.1),
                  0.66, 0.38, (IVORY, GOLD, FRAME, GOLD, IVORY))
        mesh.beam((sign * 2.8, 23.4, 4.1), (sign * 4.1, 25.1, 5.5),
                  0.38, 0.22, (GOLD, PALE, FRAME, GOLD, IVORY))
    mast = [(0, 12.1, 3.9), (0, 20.2, 5.45), (0, 25.6, 6.0), (0, 29.8, 6.1)]
    for start, end in zip(mast, mast[1:]):
        mesh.beam(start, end, 0.58, 0.48,
                  (IVORY, GOLD, FRAME, GOLD, PALE))
    mesh.beam((0, 29.8, 6.1), (0, 31.0, 6.1), 0.48, 0.05,
              (IVORY, GOLD, FRAME, GOLD, IVORY))
    # Raised compass star acts as the focal point and mast fastener.
    cx, cy, cz = 0, 22.3, 7.45
    center = (cx, cy, cz + 0.62)
    for i in range(16):
        a = i * math.pi / 8
        b = (i + 1) * math.pi / 8
        ra = 2.0 if i % 2 == 0 else 0.98
        rb = 2.0 if (i + 1) % 2 == 0 else 0.98
        pa = (cx + ra * math.sin(a), cy + ra * math.cos(a), cz)
        pb = (cx + rb * math.sin(b), cy + rb * math.cos(b), cz)
        mesh.tri(center, pa, pb, IVORY if i % 4 == 0 else GOLD, (0, 0, 1))
        mesh.tri((cx, cy, cz - 0.30), pb, pa, FRAME, (0, 0, -1))
    jewel(mesh, cx, cy, cz + 0.72, 0.62)
    return mesh


def pendant(sign):
    mesh = Sculpture()
    x = sign * 8.2
    mesh.beam((x, 28.7, 6.8), (x, 27.2, 7.0), 0.14, 0.13,
              (IVORY, GOLD, FRAME, GOLD, IVORY))
    jewel(mesh, x, 26.5, 7.1, 0.75)
    return mesh


def add_mesh(glb, sculpture, pivot, name):
    part = sculpture.gltf()
    out = primitive(glb, part, pivot, 0)
    out["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    return {"name": name, "primitives": [out]}


def write():
    glb = Glb()
    pivots = [[0, 0, 0], [0, 22.0, 5.5], [-8.2, 28.7, 6.8], [8.2, 28.7, 6.8]]
    parts = [harness(), sail(), pendant(-1), pendant(1)]
    meshes = [add_mesh(glb, part, pivot, name) for part, pivot, name in
              zip(parts, pivots, ("mast_and_compass", "billowed_sail", "left_drop", "right_drop"))]
    nodes = [
        {"name": "body", "mesh": 0, "children": [1, 2, 3]},
        {"name": "sail", "mesh": 1, "translation": pivots[1]},
        {"name": "left_drop", "mesh": 2, "translation": pivots[2]},
        {"name": "right_drop", "mesh": 3, "translation": pivots[3]},
    ]
    period = 4.0
    def billow(t):
        phase = 2 * math.pi * t / period
        return mul(quat_y(math.radians(3.5) * math.sin(phase)),
                   quat_z(math.radians(1.5) * math.sin(phase + 0.6)))
    tracks = [(1, "rotation", billow)]
    for index, sign in ((2, -1), (3, 1)):
        tracks.append((index, "rotation",
                       lambda t, sign=sign: quat_z(sign * math.radians(9) *
                                                     math.sin(2 * math.pi * t / period + 0.45))))
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Star Sail sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
                    sheen(rgb(180, 250, 255), 4.0, 0.24,
                          (0.014, 0.009, 0), 0.47, 1 / 30)}}}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [{"name": "embroidered_sail", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.08,
            "roughnessFactor": 0.65}, "doubleSided": True}],
        "animations": [animation_of(glb, period, 40, tracks)],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "star_sail.glb"))


if __name__ == "__main__":
    write()
