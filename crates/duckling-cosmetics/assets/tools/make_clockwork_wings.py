"""Build articulated Clockwork Wings with the cuboid model as fallback.

Brass spars and separate enamel plates replace the old block bars. The two
gears rotate inside the shoulder hinges while each wing flexes slightly.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of, rgb, sheen
from make_dragon_wings import Sculpture as BaseSculpture
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


INK = (51, 38, 38)
IRON = (79, 65, 62)
COPPER = (143, 89, 55)
BRASS = (210, 151, 73)
GOLD = (246, 211, 121)
PALE = (255, 239, 185)
TEAL = (73, 195, 209)
ICE = (168, 242, 235)


class Sculpture(BaseSculpture):
    def diamond(self, x, y, z, radius):
        """A raised teal lens; the inherited dragon lens is purple."""
        corners = [(x, y + radius, z), (x + radius, y, z),
                   (x, y - radius, z), (x - radius, y, z)]
        front = (x, y, z + radius * 0.75)
        rear = (x, y, z - radius * 0.55)
        for index, color in enumerate((PALE, ICE, TEAL, ICE)):
            nxt = (index + 1) % 4
            self.tri(front, corners[index], corners[nxt], color, (0, 0, 1))
            self.tri(rear, corners[nxt], corners[index], IRON, (0, 0, -1))

    def plate(self, root, tip, width, colors, depth=0.95):
        """Closed six-corner armor vane, with a raised ridge and dark sides."""
        a = np.asarray(root, dtype=float)
        b = np.asarray(tip, dtype=float)
        along = b - a
        xy = along[:2]
        side = np.array((-xy[1], xy[0], 0.0))
        side /= max(np.linalg.norm(side), 1e-6)
        outline = [
            a - side * width * 0.34,
            a + side * width * 0.34,
            a + along * 0.35 + side * width * 0.62,
            b - along * 0.16 + side * width * 0.48,
            b,
            b - along * 0.16 - side * width * 0.48,
            a + along * 0.35 - side * width * 0.62,
        ]
        ridge = a + along * 0.58 + [0, 0, depth * 0.7]
        back = np.array((0, 0, depth))
        for i, (p, q) in enumerate(zip(outline, outline[1:] + outline[:1])):
            self.tri(ridge, p, q, colors[i % len(colors)], (0, 0, 1))
            self.tri(ridge - back * 1.45, q - back, p - back,
                     BRASS if i % 2 else COPPER, (0, 0, -1))
            self.tri(p, q, q - back, INK)
            self.tri(p, q - back, p - back, COPPER)
        # Two inlaid light strips run with the plate, never outside it.
        for factor in (0.32, 0.59):
            # Keep the glass visibly above the faceted front at both ends.
            p = a + along * factor + [0, 0, depth * 1.23]
            q = a + along * (factor + 0.16) + [0, 0, depth * 1.20]
            self.beam(p, q, 0.24, 0.19,
                      (ICE, TEAL, ICE, TEAL, PALE))
            p = a + along * factor - [0, 0, depth * 1.61]
            q = a + along * (factor + 0.16) - [0, 0, depth * 1.58]
            self.beam(p, q, 0.20, 0.16,
                      (ICE, TEAL, ICE, TEAL, PALE))

    def gear(self, center, outer=1.85):
        """A toothed annulus with a hole, hub and six exposed spokes."""
        cx, cy, cz = center
        teeth = 12
        inner = 0.88
        back_z = cz - 0.62
        for i in range(teeth * 2):
            a = i * math.pi / teeth
            b = (i + 1) * math.pi / teeth
            ra = outer * (1.12 if i % 2 else 0.94)
            rb = outer * (1.12 if (i + 1) % 2 else 0.94)
            oa = (cx + ra * math.cos(a), cy + ra * math.sin(a), cz)
            ob = (cx + rb * math.cos(b), cy + rb * math.sin(b), cz)
            ia = (cx + inner * math.cos(a), cy + inner * math.sin(a), cz)
            ib = (cx + inner * math.cos(b), cy + inner * math.sin(b), cz)
            self.tri(oa, ob, ib, GOLD if i % 4 == 0 else BRASS, (0, 0, 1))
            self.tri(oa, ib, ia, COPPER, (0, 0, 1))
            self.tri((oa[0], oa[1], back_z), (ib[0], ib[1], back_z),
                     (ob[0], ob[1], back_z), IRON, (0, 0, -1))
            self.tri((oa[0], oa[1], back_z), (ia[0], ia[1], back_z),
                     (ib[0], ib[1], back_z), COPPER, (0, 0, -1))
            self.tri(oa, (oa[0], oa[1], back_z), (ob[0], ob[1], back_z), INK)
            self.tri(oa, (ob[0], ob[1], back_z), ob, COPPER)
        for i in range(6):
            a = i * math.pi / 3
            p = (cx + 0.35 * math.cos(a), cy + 0.35 * math.sin(a), cz + 0.18)
            q = (cx + inner * math.cos(a), cy + inner * math.sin(a), cz + 0.18)
            self.beam(p, q, 0.20, 0.14,
                      (PALE, GOLD, COPPER, BRASS, GOLD))
        self.diamond(cx, cy, cz + 0.35, 0.56)


def wing(sign):
    mesh = Sculpture()
    def p(x, y, z):
        return (sign * x, y, z)

    root = p(3.4, 22.4, 4.7)
    # The primary spar rises from the shoulder, then sweeps backward. A
    # second lower linkage holds the vanes apart in depth.
    upper = [root, p(8.0, 25.2, 5.8), p(13.0, 27.1, 7.0), p(16.5, 27.6, 8.2)]
    lower = [p(4.3, 21.1, 5.0), p(8.6, 18.9, 6.2),
             p(13.3, 16.4, 7.2), p(16.2, 13.9, 7.9)]
    for route in (upper, lower):
        for i, (a, b) in enumerate(zip(route, route[1:])):
            mesh.beam(a, b, 0.83 - i * 0.16, 0.68 - i * 0.17,
                      (PALE, GOLD, COPPER, BRASS, GOLD))
    for a, b in ((upper[1], lower[1]), (upper[2], lower[2])):
        mesh.beam(a, b, 0.22, 0.19,
                  (GOLD, BRASS, IRON, COPPER, PALE))

    # Individually closed plates have gaps between them, rather than forming
    # one flat sheet. Their tips step down like a forged mechanical fan.
    blades = [
        (p(4.4, 23.0, 5.0), p(8.7, 28.4, 6.2), 1.95),
        (p(6.0, 23.4, 5.5), p(12.1, 29.3, 7.0), 2.20),
        (p(8.0, 23.6, 5.9), p(15.7, 28.8, 7.8), 2.42),
        (p(9.5, 22.3, 6.4), p(18.4, 25.1, 8.5), 2.65),
        (p(10.0, 20.6, 6.6), p(19.0, 20.7, 8.8), 2.70),
        (p(9.6, 19.0, 6.5), p(17.5, 15.7, 8.3), 2.48),
        (p(8.4, 18.3, 6.1), p(14.3, 12.8, 7.7), 2.16),
    ]
    for i, (base, tip, width) in enumerate(blades):
        palette = (GOLD, PALE, GOLD, BRASS, GOLD, COPPER, GOLD)
        if i % 2:
            palette = (BRASS, GOLD, PALE, GOLD, BRASS, COPPER, GOLD)
        mesh.plate(base, tip, width, palette, depth=0.9)
    for x, y, z in ((8.0, 25.2, 6.2), (13.0, 27.1, 7.4),
                    (8.6, 18.9, 6.5), (13.3, 16.4, 7.5)):
        mesh.diamond(sign * x, y, z, 0.35)
    return mesh


def housing():
    mesh = Sculpture()
    # The clock casing attaches at the mid-back, with visible shoulder arms.
    mesh.plate((-1.9, 19.1, 3.3), (1.9, 24.0, 4.15), 3.2,
               (INK, COPPER, BRASS, GOLD, COPPER, IRON, BRASS), 1.25)
    for sign in (-1, 1):
        mesh.beam((sign * 1.8, 22.0, 3.6), (sign * 3.5, 22.4, 4.7),
                  0.65, 0.58, (PALE, BRASS, IRON, COPPER, GOLD))
    # Dial and hands sit on the casing, not in front of the whole wearer.
    mesh.gear((0, 21.4, 5.2), outer=1.35)
    mesh.beam((0, 21.4, 5.6), (0.74, 22.15, 5.76), 0.16, 0.08,
              (ICE, GOLD, COPPER, GOLD, PALE))
    return mesh


def gear(sign):
    mesh = Sculpture()
    mesh.gear((sign * 5.4, 22.8, 6.0))
    return mesh


def add_mesh(glb, sculpture, pivot, name):
    part = sculpture.gltf()
    out = primitive(glb, part, pivot, 0)
    out["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    return {"name": name, "primitives": [out]}


def write():
    glb = Glb()
    pivots = [[0, 0, 0], [3.4, 22.4, 4.7], [-3.4, 22.4, 4.7],
              [5.4, 22.8, 6.0], [-5.4, 22.8, 6.0]]
    parts = [housing(), wing(1), wing(-1), gear(1), gear(-1)]
    meshes = [add_mesh(glb, part, pivot, name) for part, pivot, name in
              zip(parts, pivots, ("clock_housing", "left_vanes", "right_vanes",
                                  "left_gear", "right_gear"))]
    nodes = [
        {"name": "body", "mesh": 0, "children": [1, 2]},
        {"name": "wing_left", "mesh": 1, "translation": pivots[1], "children": [3]},
        {"name": "wing_right", "mesh": 2, "translation": pivots[2], "children": [4]},
        {"name": "gear_left", "mesh": 3,
         "translation": [pivots[3][i] - pivots[1][i] for i in range(3)]},
        {"name": "gear_right", "mesh": 4,
         "translation": [pivots[4][i] - pivots[2][i] for i in range(3)]},
    ]
    period = 8.0
    tracks = []
    for index, sign in ((1, 1), (2, -1)):
        def wing_pose(t, sign=sign):
            phase = 2 * math.pi * t / (period / 2)
            return mul(quat_z(sign * math.radians(5.0) * math.sin(phase)),
                       quat_y(-sign * math.radians(3.2) * math.sin(phase + 0.42)))
        tracks.append((index, "rotation", wing_pose))
    for index, sign in ((3, 1), (4, -1)):
        tracks.append((index, "rotation",
                       lambda t, sign=sign: quat_z(sign * 4 * math.pi * t / period)))
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Clockwork Wings sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
                    sheen(rgb(255, 224, 157), 4.0, 0.21,
                          (0.015, 0.007, 0), 0.48, 1 / 32)}}}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [{"name": "brushed_brass", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.34,
            "roughnessFactor": 0.49}, "doubleSided": True}],
        "animations": [animation_of(glb, period, 80, tracks)],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "clockwork_wings.glb"))


if __name__ == "__main__":
    write()
