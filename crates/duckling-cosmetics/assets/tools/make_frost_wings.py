"""Build the sculpted Frost Wings replacement as an animated Arctic GLB.

The old cuboid geometry remains beside it for clients without mesh support.
This model uses faceted, thick ice feathers and a raised spine so it reads
from both sides as well as from behind.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of, rgb, sheen
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


INK = (20, 55, 86)
EDGE = (40, 112, 158)
DEEP_ICE = (32, 138, 188)
ICE = (77, 195, 224)
PALE = (163, 235, 242)
SNOW = (237, 252, 249)
SILVER = (141, 178, 194)


class Sculpture:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.colors = []
        self.indices = []

    def tri(self, a, b, c, color):
        a, b, c = (np.asarray(p, dtype=np.float32) for p in (a, b, c))
        normal = np.cross(b - a, c - a)
        normal /= max(np.linalg.norm(normal), 1e-6)
        start = len(self.positions)
        self.positions.extend((a, b, c))
        self.normals.extend((normal, normal, normal))
        self.colors.extend(((*color, 255),) * 3)
        self.indices.extend((start, start + 1, start + 2))

    def faceted_blade(self, base, tip, width, z, colors, thick=0.75):
        """A closed seven-sided feather with a raised central ridge and dark sidewalls."""
        start = np.asarray(base, dtype=float)
        end = np.asarray(tip, dtype=float)
        along = end - start
        perp = np.array([-along[1], along[0]]) / max(np.linalg.norm(along), 1e-6)
        xy = [
            start - perp * width * 0.32,
            start + perp * width * 0.32,
            start + along * 0.31 + perp * width * 0.58,
            end - along * 0.20 + perp * width * 0.37,
            end,
            end - along * 0.20 - perp * width * 0.37,
            start + along * 0.31 - perp * width * 0.58,
        ]
        # Root sits close to the back; the tips fan out in depth, giving a
        # readable profile from the side instead of a flat plane.
        zs = [z, z, z + 0.58, z + 1.30, z + 2.35, z + 1.30, z + 0.58]
        contour = [np.array([*p, depth], dtype=float) for p, depth in zip(xy, zs)]
        area = sum(xy[i][0] * xy[(i + 1) % len(xy)][1] - xy[(i + 1) % len(xy)][0] * xy[i][1] for i in range(len(xy)))
        if area < 0:
            contour.reverse()
        ridge = np.array([*(start + along * 0.57), z + 1.88])
        for i, color in enumerate(colors):
            self.tri(ridge, contour[i], contour[(i + 1) % len(contour)], color)
        back = [p - np.array([0, 0, thick]) for p in contour]
        back_center = ridge - np.array([0, 0, thick + 0.42])
        for i in range(len(contour)):
            j = (i + 1) % len(contour)
            self.tri(back_center, back[j], back[i], ICE if i % 2 else DEEP_ICE)
            self.tri(contour[i], back[i], back[j], INK)
            self.tri(contour[i], back[j], contour[j], EDGE)

    def jewel(self, x, y, z, radius=1):
        diamond = [(x, y + radius, z), (x + radius, y, z),
                   (x, y - radius, z), (x - radius, y, z)]
        high = (x, y, z + radius * 0.55)
        low = (x, y, z - radius * 0.45)
        for i, color in enumerate((SNOW, PALE, ICE, PALE)):
            self.tri(high, diamond[i], diamond[(i + 1) % 4], color)
            self.tri(low, diamond[(i + 1) % 4], diamond[i], EDGE)

    def gltf(self):
        return {
            "pos": np.asarray(self.positions, dtype=np.float32),
            "normal": np.asarray(self.normals, dtype=np.float32),
            "col": np.asarray(self.colors, dtype=np.float32) / 255.0,
            "uv": None,
            "idx": np.asarray(self.indices, dtype=np.uint32),
            "material": True,
        }


def wing(sign):
    mesh = Sculpture()
    def mirror(point):
        return (sign * point[0], point[1])

    # Primary feathers radiate from a rising shoulder line; the outer
    # primaries turn outward and upward, unlike the Heron's long down fan.
    feathers = [
        ((3.5, 22.5), (6.5, 15.2), 1.55, 4.65),
        ((5.2, 23.6), (9.2, 13.5), 1.67, 4.82),
        ((7.1, 24.8), (12.3, 13.0), 1.78, 5.14),
        ((9.2, 25.6), (15.4, 14.1), 1.79, 5.45),
        ((11.4, 25.8), (18.6, 16.5), 1.62, 5.78),
        ((13.8, 25.3), (20.2, 19.5), 1.43, 6.13),
        ((15.7, 24.2), (20.6, 22.5), 1.17, 6.41),
    ]
    for index, (base, tip, width, z) in enumerate(feathers):
        palette = (PALE, ICE, SNOW, PALE, ICE, DEEP_ICE, PALE)
        if index % 3 == 1:
            palette = (ICE, PALE, SNOW, ICE, PALE, DEEP_ICE, ICE)
        mesh.faceted_blade(mirror(base), mirror(tip), width, z, palette)

    # Short crown feathers fill the upper contour without making a flat card.
    for base, tip, width, z in [
        ((5.0, 23.6), (8.1, 27.4), 1.15, 4.95),
        ((8.0, 24.8), (12.4, 28.1), 1.22, 5.12),
        ((11.4, 25.6), (16.0, 27.1), 1.10, 5.35),
    ]:
        mesh.faceted_blade(mirror(base), mirror(tip), width, z,
                           (PALE, SNOW, ICE, PALE, SNOW, ICE, PALE), thick=0.65)

    # The raised spine connects every feather root and carries small ice
    # rivets so the form reads as a wearable item attached to the shoulders.
    spine = [(3.0, 22.2), (5.5, 23.7), (8.3, 25.2), (11.3, 26.0),
             (14.2, 25.7), (17.2, 24.2)]
    for a, b in zip(spine, spine[1:]):
        mesh.faceted_blade(mirror(a), mirror(b), 0.60, 6.36,
                           (SILVER, SNOW, PALE, SILVER, PALE, EDGE, SILVER), thick=0.85)
    for x, y in ((5.5, 23.7), (11.3, 26.0), (17.2, 24.2)):
        mesh.jewel(sign * x, y, 7.54, 0.34)
    return mesh


def harness():
    mesh = Sculpture()
    mesh.faceted_blade((-2.25, 23.3), (-1.2, 17.9), 0.80, 3.13,
                       (INK, EDGE, SILVER, EDGE, INK, INK, EDGE), thick=0.95)
    mesh.faceted_blade((2.25, 23.3), (1.2, 17.9), 0.80, 3.13,
                       (INK, EDGE, SILVER, EDGE, INK, INK, EDGE), thick=0.95)
    mesh.jewel(0, 21.6, 4.75, 1.23)
    return mesh


def write():
    glb = Glb()
    parts = [wing(1), wing(-1), harness()]
    pivots = [[3.2, 22.3, 4.6], [-3.2, 22.3, 4.6], [0, 0, 0]]
    meshes = []
    for i, part in enumerate(parts):
        primitive_doc = primitive(glb, part.gltf(), pivots[i], 0)
        primitive_doc["attributes"]["NORMAL"] = glb.add(part.gltf()["normal"], "VEC3", 5126)
        meshes.append({"name": ("left", "right", "harness")[i], "primitives": [primitive_doc]})
    nodes = [
        {"name": "body", "children": [1, 2, 3]},
        {"name": "wing_left", "mesh": 0, "translation": pivots[0]},
        {"name": "wing_right", "mesh": 1, "translation": pivots[1]},
        {"name": "harness", "mesh": 2},
    ]
    period = 3.4
    tracks = []
    for index, sign in ((1, 1), (2, -1)):
        def rotation(t, sign=sign):
            phase = 2 * math.pi * t / period
            return mul(quat_z(sign * math.radians(5.2) * math.sin(phase)),
                       quat_y(-sign * math.radians(3.0) * math.sin(phase + 0.75)))
        tracks.append((index, "rotation", rotation))
    animation = animation_of(glb, period, 24, tracks)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Frost Wings sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen": sheen(rgb(228, 255, 250), 3.4, 0.24,
                                                           (0.015, 0.011, 0), 0.54, 1 / 28)}}}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [{"name": "polished_ice", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.14,
            "roughnessFactor": 0.46}, "doubleSided": True}],
        "animations": [animation],
    }
    path = os.path.join(ASSETS, "cosmetics", "frost_wings.glb")
    glb.write(doc, path)


if __name__ == "__main__":
    write()
