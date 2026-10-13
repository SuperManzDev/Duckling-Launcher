"""Build dimensional Dragon Wings while retaining the cuboid fallback.

The old dragon_wings.geo.json and texture remain for older clients. The GLB
uses a scalloped membrane, curved finger bones and an articulated shoulder
harness; every part has a colored underside and a side profile.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of, rgb, sheen
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


INK = (45, 23, 70)
SHADOW = (75, 34, 107)
VIOLET = (123, 55, 172)
ORCHID = (174, 81, 223)
PINK = (227, 124, 234)
LIGHT = (250, 184, 239)
GOLD = (252, 202, 106)
PALE_GOLD = (255, 237, 174)


class Sculpture:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.colors = []
        self.indices = []

    def tri(self, a, b, c, color, outward=None):
        a, b, c = (np.asarray(point, dtype=np.float32) for point in (a, b, c))
        normal = np.cross(b - a, c - a)
        if outward is not None and np.dot(normal, outward) < 0:
            b, c = c, b
            normal = -normal
        normal /= max(np.linalg.norm(normal), 1e-6)
        index = len(self.positions)
        self.positions.extend((a, b, c))
        self.normals.extend((normal, normal, normal))
        self.colors.extend(((*color, 255),) * 3)
        self.indices.extend((index, index + 1, index + 2))

    def beam(self, start, end, radius_start, radius_end, colors):
        """Closed five-sided tapered rib, with real depth at every camera angle."""
        start = np.asarray(start, dtype=float)
        end = np.asarray(end, dtype=float)
        along = end - start
        along /= max(np.linalg.norm(along), 1e-6)
        side = np.cross(along, [0, 0, 1])
        side /= max(np.linalg.norm(side), 1e-6)
        depth = np.cross(along, side)
        ring_start = []
        ring_end = []
        for index in range(5):
            angle = 2 * math.pi * index / 5
            offset = side * math.cos(angle) + depth * math.sin(angle)
            ring_start.append(start + offset * radius_start)
            ring_end.append(end + offset * radius_end)
        for index in range(5):
            nxt = (index + 1) % 5
            tone = colors[index % len(colors)]
            self.tri(ring_start[index], ring_end[index], ring_end[nxt], tone)
            self.tri(ring_start[index], ring_end[nxt], ring_start[nxt], tone)
        for index in range(1, 4):
            self.tri(ring_start[0], ring_start[index + 1], ring_start[index], INK)
            self.tri(ring_end[0], ring_end[index], ring_end[index + 1], colors[0])

    def diamond(self, x, y, z, radius):
        corners = [(x, y + radius, z), (x + radius, y, z),
                   (x, y - radius, z), (x - radius, y, z)]
        front = (x, y, z + radius * 0.75)
        rear = (x, y, z - radius * 0.55)
        for index, color in enumerate((PALE_GOLD, GOLD, ORCHID, GOLD)):
            nxt = (index + 1) % 4
            self.tri(front, corners[index], corners[nxt], color, (0, 0, 1))
            self.tri(rear, corners[nxt], corners[index], SHADOW, (0, 0, -1))

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
    def point(x, y, z):
        return (sign * x, y, z)

    root = point(3.3, 22.3, 4.15)
    # Alternating pointed finger tips and inset valleys form a dragon-wing
    # silhouette. Spread the fingers through depth, like a folded fan, so a
    # side view reveals separate spars instead of a single membrane card.
    edge = [
        point(18.2, 28.0, 8.8),
        point(14.1, 22.5, 6.3),
        point(20.2, 21.9, 12.0),
        point(15.2, 17.8, 7.6),
        point(17.9, 11.6, 13.0),
        point(10.9, 14.4, 7.5),
        point(9.8, 9.8, 9.8),
        point(3.5, 16.6, 4.35),
    ]
    # Each membrane sector is split at a raised ridge. Front and underside
    # are separately shaded, with a closed rim so the side isn't a card.
    tones = [
        (VIOLET, ORCHID, PINK),
        (ORCHID, PINK, LIGHT),
        (VIOLET, ORCHID, PINK),
        (ORCHID, PINK, LIGHT),
        (VIOLET, ORCHID, PINK),
        (VIOLET, ORCHID, LIGHT),
        (SHADOW, VIOLET, ORCHID),
    ]
    for index, (a, b) in enumerate(zip(edge, edge[1:])):
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        hub = np.asarray(root) * 0.35 + (a + b) * 0.325 + [0, 0, 1.15]
        dark, body, highlight = tones[index]
        mesh.tri(root, a, hub, dark, (0, 0, 1))
        mesh.tri(a, b, hub, highlight, (0, 0, 1))
        mesh.tri(b, root, hub, body, (0, 0, 1))
        back = np.array([0, 0, 0.78])
        mesh.tri(root - back, hub - back, a - back, SHADOW, (0, 0, -1))
        mesh.tri(a - back, hub - back, b - back, VIOLET, (0, 0, -1))
        mesh.tri(b - back, hub - back, root - back, SHADOW, (0, 0, -1))
        mesh.tri(a, b, b - back, SHADOW)
        mesh.tri(a, b - back, a - back, INK)

    # Curved spar and four skeletal fingers. The upper rib rises above the
    # head line; the lower fingers project behind the player without sinking
    # into the legs. The ribs supply the visible side volume.
    routes = [
        ([root, point(9.0, 26.0, 6.9), edge[0]], 0.90),
        ([root, point(10.8, 22.8, 8.3), edge[2]], 0.78),
        ([root, point(10.2, 19.0, 8.8), edge[4]], 0.70),
        ([root, point(7.6, 16.9, 6.6), edge[6]], 0.61),
    ]
    for route, width in routes:
        for i in range(2):
            mesh.beam(route[i], route[i + 1], width * (1 - i * 0.28),
                      width * (0.72 - i * 0.35),
                      (PALE_GOLD, GOLD, ORCHID, GOLD, PALE_GOLD))
    # The scalloped rim reads as a deliberate outline instead of a ragged
    # cutout. Short gold talons cap the wing fingers.
    for a, b in zip(edge, edge[1:]):
        mesh.beam(a, b, 0.16, 0.16, (PINK, ORCHID, SHADOW, VIOLET, LIGHT))
    talons = [point(19.5, 29.0, 9.4), point(21.8, 22.3, 12.7),
              point(18.5, 10.0, 13.5), point(10.1, 8.1, 10.3)]
    for tip, end in zip(edge[::2], talons):
        mesh.beam(tip, end, 0.36, 0.07,
                  (PALE_GOLD, GOLD, SHADOW, GOLD, PALE_GOLD))
    for x, y, z in ((5.5, 23.9, 5.25), (9.1, 26.0, 6.45), (11.0, 22.8, 6.75)):
        mesh.diamond(sign * x, y, z, 0.36)
    return mesh


def harness():
    mesh = Sculpture()
    for sign in (-1, 1):
        mesh.beam((sign * 2.0, 22.4, 3.25), (sign * 3.4, 22.3, 4.2),
                  0.86, 0.64, (GOLD, VIOLET, INK, SHADOW, PALE_GOLD))
        mesh.beam((sign * 2.0, 22.4, 3.25), (sign * 1.3, 18.7, 3.65),
                  0.50, 0.36, (SHADOW, VIOLET, INK, VIOLET, GOLD))
    mesh.diamond(0, 21.1, 4.15, 1.15)
    return mesh


def add_mesh(glb, sculpture, pivot, name):
    part = sculpture.gltf()
    out = primitive(glb, part, pivot, 0)
    out["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    return {"name": name, "primitives": [out]}


def write():
    glb = Glb()
    pivots = [[3.3, 22.3, 4.15], [-3.3, 22.3, 4.15], [0, 0, 0]]
    parts = [wing(1), wing(-1), harness()]
    meshes = [add_mesh(glb, part, pivot, name) for part, pivot, name in
              zip(parts, pivots, ("left_membrane", "right_membrane", "harness"))]
    nodes = [
        {"name": "body", "children": [1, 2, 3]},
        {"name": "wing_left", "mesh": 0, "translation": pivots[0]},
        {"name": "wing_right", "mesh": 1, "translation": pivots[1]},
        {"name": "harness", "mesh": 2},
    ]
    period = 3.6
    tracks = []
    for index, sign in ((1, 1), (2, -1)):
        def rotation(t, sign=sign):
            phase = 2 * math.pi * t / period
            return mul(quat_z(sign * math.radians(5.5) * math.sin(phase)),
                       quat_y(-sign * math.radians(4.0) * math.sin(phase + 0.4)))
        tracks.append((index, "rotation", rotation))
    animation = animation_of(glb, period, 36, tracks)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Dragon Wings sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
                    sheen(rgb(255, 198, 249), 3.6, 0.22,
                          (0.012, -0.014, 0), 0.51, 1 / 30)}}}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [{"name": "polished_amethyst", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.12,
            "roughnessFactor": 0.55}, "doubleSided": True}],
        "animations": [animation],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "dragon_wings.glb"))


if __name__ == "__main__":
    write()
