"""Sculpt a dimensional Halo that follows the player's head.

The cuboid halo remains the fallback for clients without mesh cosmetics.
Run from this directory with Python, NumPy, and the existing mesh kit.
"""

import math
import os

from make_codex_meshes import animation_of, rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive, quat_y


BRONZE = (94, 52, 40)
AMBER = (169, 96, 48)
GOLD = (239, 173, 65)
SUNLIGHT = (255, 210, 111)
IVORY = (255, 239, 184)
DEEP_TEAL = (28, 124, 139)
TURQUOISE = (66, 216, 215)
ICE = (186, 255, 247)

SEGMENTS = 32
HEIGHT = 33.5
PIVOT = [0.0, HEIGHT, 0.0]


def ring_point(angle, rx, rz, rise):
    x = rx * math.cos(angle)
    z = rz * math.sin(angle)
    # The forward edge sits lower than the rear so the aperture is visible
    # from the front instead of reading as a horizontal line.
    return (x, HEIGHT + 0.24 * z + rise, z)


def gem(model, angle):
    center = ring_point(angle, 4.87, 4.17, 0.52)
    x, y, z = center
    tangent = (-math.sin(angle), 0, math.cos(angle))
    radial = (math.cos(angle), 0, math.sin(angle))
    top = (x, y + 0.68, z)
    bottom = (x, y - 0.15, z)
    rim = []
    for tx, rz in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        rim.append((x + 0.31 * (tx * tangent[0] + rz * radial[0]),
                    y + 0.20,
                    z + 0.31 * (tx * tangent[2] + rz * radial[2])))
    for index in range(4):
        nxt = (index + 1) % 4
        model.tri(top, rim[index], rim[nxt], (ICE, TURQUOISE, ICE, DEEP_TEAL)[index], (0, 1, 0))
        model.tri(bottom, rim[nxt], rim[index], DEEP_TEAL, (0, -1, 0))


def sculpture():
    model = Sculpture()
    # This seven-sided cross-section closes all four sides of the ring. The
    # raised bevel and wider underside give the halo visible side volume.
    section = (
        (5.27, 4.52, -0.26),
        (5.53, 4.76, -0.04),
        (5.40, 4.65, 0.17),
        (5.11, 4.37, 0.40),
        (4.55, 3.83, 0.40),
        (4.32, 3.64, 0.14),
        (4.40, 3.72, -0.26),
    )
    for segment in range(SEGMENTS):
        a = 2 * math.pi * segment / SEGMENTS
        b = 2 * math.pi * (segment + 1) / SEGMENTS
        mid = (a + b) * 0.5
        radial = (math.cos(mid), 0, math.sin(mid))
        is_light = segment % 8 in (0, 1, 2, 3)
        colors = (
            BRONZE, AMBER, GOLD, SUNLIGHT if is_light else GOLD,
            IVORY if is_light else SUNLIGHT, AMBER, BRONZE,
        )
        directions = (
            radial, radial, (radial[0], 1, radial[2]), (0, 1, 0),
            (-radial[0], 1, -radial[2]), (-radial[0], 0, -radial[2]), (0, -1, 0),
        )
        for face in range(len(section)):
            next_face = (face + 1) % len(section)
            v00 = ring_point(a, *section[face])
            v10 = ring_point(b, *section[face])
            v11 = ring_point(b, *section[next_face])
            v01 = ring_point(a, *section[next_face])
            model.tri(v00, v10, v11, colors[face], directions[face])
            model.tri(v00, v11, v01, colors[face], directions[face])
        # Four short inset enamel arcs catch the light without turning the
        # entire ring into a neon outline.
        if segment % 8 in (5, 6):
            p = [ring_point(theta, radius_x, radius_z, 0.418)
                 for theta, radius_x, radius_z in
                 ((a, 4.88, 4.15), (b, 4.88, 4.15),
                  (b, 4.71, 3.99), (a, 4.71, 3.99))]
            model.tri(p[0], p[1], p[2], TURQUOISE, (0, 1, 0))
            model.tri(p[0], p[2], p[3], TURQUOISE, (0, 1, 0))
    for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        gem(model, angle)
    return model


def write():
    glb = Glb()
    part = sculpture().gltf()
    shape = primitive(glb, part, PIVOT, 0)
    shape["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    period = 4.0
    animation = animation_of(glb, period, 48, [
        (1, "translation", lambda t: [0.0, HEIGHT + 0.12 * math.sin(2 * math.pi * t / period), 0.0]),
        (1, "rotation", lambda t: quat_y(0.065 * math.sin(2 * math.pi * t / period))),
    ])
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Halo sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
            sheen(rgb(255, 247, 206), 4.0, 0.22, (0.07, 0.018, -0.04), 0.3, 0.0)}}}],
        "nodes": [
            {"name": "head", "children": [1]},
            {"name": "halo_ring", "mesh": 0, "translation": PIVOT},
        ],
        "meshes": [{"name": "faceted_halo", "primitives": [shape]}],
        "materials": [{"name": "gold_and_enamel", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.62,
            "roughnessFactor": 0.34}, "doubleSided": True}],
        "animations": [animation],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "halo.glb"))


if __name__ == "__main__":
    write()
