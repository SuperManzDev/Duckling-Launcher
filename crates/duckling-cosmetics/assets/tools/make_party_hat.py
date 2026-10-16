"""Build a bright, faceted party hat for the live cosmetics catalog.

Its older stepped-cube model remains the fallback on clients without meshes.
"""

import math
import os

from make_codex_meshes import animation_of, rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive, quat_z


INK = (69, 26, 87)
ORCHID = (171, 62, 174)
PINK = (224, 66, 157)
LIGHT_PINK = (255, 133, 193)
TEAL = (51, 209, 199)
ICE = (171, 255, 240)
GOLD = (251, 184, 69)
PALE_GOLD = (255, 233, 142)

SIDES = 16
BASE_Y = 32.10
TIP_Y = 36.65


def center(y):
    t = (y - BASE_Y) / (TIP_Y - BASE_Y)
    return (0.45 + 0.65 * t, -0.15 - 0.23 * t)


def radius(y):
    t = max(0.0, min(1.0, (y - BASE_Y) / (TIP_Y - BASE_Y)))
    return 3.66 * (1.0 - t) + 0.11 * t


def point(angle, y, extra=0.0):
    x, z = center(y)
    r = radius(y) + extra
    return (x + r * math.cos(angle), y, z + r * math.sin(angle))


def conical_body(model):
    rings = (BASE_Y, 34.25, TIP_Y)
    for index in range(SIDES):
        a = index * 2 * math.pi / SIDES
        b = (index + 1) * 2 * math.pi / SIDES
        main = (PINK, ORCHID, PINK, LIGHT_PINK)[(index // 2) % 4]
        for y0, y1 in zip(rings, rings[1:]):
            p = point(a, y0), point(b, y0), point(b, y1), point(a, y1)
            model.tri(p[0], p[1], p[2], main)
            model.tri(p[0], p[2], p[3], main)
        # An enclosed underside keeps the brim from looking like a paper cap.
        base_x, base_z = center(BASE_Y)
        model.tri((base_x, BASE_Y, base_z), point(b, BASE_Y), point(a, BASE_Y), INK,
                  (0, -1, 0))

    # One continuous gold ribbon winds up and around the cone. Its geometry
    # follows the taper, so the design reads from the front and both sides.
    steps = 48
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        y0, y1 = 32.62 + 3.55 * t0, 32.62 + 3.55 * t1
        a0 = -1.8 + 3.5 * math.pi * t0
        a1 = -1.8 + 3.5 * math.pi * t1
        p = (point(a0 - 0.10, y0, 0.045), point(a0 + 0.10, y0, 0.045),
             point(a1 + 0.10, y1, 0.045), point(a1 - 0.10, y1, 0.045))
        model.tri(p[0], p[1], p[2], GOLD)
        model.tri(p[0], p[2], p[3], PALE_GOLD)

    # Small raised enamel diamonds catch the light independently of the
    # spiral, making the party motif legible at Minecraft's normal scale.
    for index in range(8):
        angle = (index + 0.5) * math.pi / 4
        height = 33.58 if index % 2 else 34.05
        top = point(angle, height + 0.29, 0.075)
        bottom = point(angle, height - 0.29, 0.075)
        left = point(angle - 0.105, height, 0.075)
        right = point(angle + 0.105, height, 0.075)
        model.tri(top, left, bottom, TEAL)
        model.tri(top, bottom, right, ICE)


def brim(model):
    cx, cz = center(BASE_Y)
    profile = ((3.55, 32.04), (4.26, 32.04), (4.38, 32.28),
               (4.12, 32.48), (3.54, 32.48))
    for index in range(SIDES):
        a = index * 2 * math.pi / SIDES
        b = (index + 1) * 2 * math.pi / SIDES
        for face, (r0, y0) in enumerate(profile):
            r1, y1 = profile[(face + 1) % len(profile)]
            q = ((cx+r0*math.cos(a), y0, cz+r0*math.sin(a)),
                 (cx+r0*math.cos(b), y0, cz+r0*math.sin(b)),
                 (cx+r1*math.cos(b), y1, cz+r1*math.sin(b)),
                 (cx+r1*math.cos(a), y1, cz+r1*math.sin(a)))
            tone = (INK, ORCHID, GOLD, PALE_GOLD, ORCHID)[face]
            model.tri(q[0], q[1], q[2], tone)
            model.tri(q[0], q[2], q[3], tone)
    # Four small enamel mounts give the lip deliberate front, rear, and side
    # details rather than a plain flat color band.
    for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        x, z = cx+4.22*math.cos(angle), cz+4.22*math.sin(angle)
        top = (x, 32.61, z)
        a = (x+0.38*math.cos(angle+0.4), 32.20, z+0.38*math.sin(angle+0.4))
        b = (x+0.38*math.cos(angle-0.4), 32.20, z+0.38*math.sin(angle-0.4))
        model.tri(top, a, b, ICE)


def pom():
    model = Sculpture()
    x, z = center(TIP_Y)
    y = 36.78
    top, bottom = (x, y+0.62, z), (x, y-0.31, z)
    ring = [(x+0.59*math.cos(i*math.pi/4), y+0.06,
             z+0.59*math.sin(i*math.pi/4)) for i in range(8)]
    for i in range(8):
        j = (i+1) % 8
        model.tri(top, ring[i], ring[j], ICE if i % 2 else PALE_GOLD)
        model.tri(bottom, ring[j], ring[i], TEAL if i % 2 else GOLD)
    return model


def write():
    glb = Glb()
    hat = Sculpture()
    conical_body(hat)
    brim(hat)
    parts = [hat.gltf(), pom().gltf()]
    tip_x, tip_z = center(TIP_Y)
    pivot = [tip_x, 36.78, tip_z]
    offsets = ([0, 0, 0], pivot)
    meshes = []
    for name, part, offset in zip(("conical_hat", "pom"), parts, offsets):
        mesh = primitive(glb, part, offset, 0)
        mesh["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
        meshes.append({"name": name, "primitives": [mesh]})
    period = 3.0
    animation = animation_of(glb, period, 36, [
        (1, "rotation", lambda t: quat_z(0.12 * math.sin(2 * math.pi * t / period))),
    ])
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Party Hat sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
            sheen(rgb(255, 244, 189), 3.0, 0.17, (0.08, -0.04, 0.05), 0.37, 0)}}}],
        "nodes": [
            {"name": "head", "mesh": 0, "children": [1]},
            {"name": "pom", "mesh": 1, "translation": pivot},
        ],
        "meshes": meshes,
        "materials": [{"name": "festival_satin", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.14,
            "roughnessFactor": 0.58}, "doubleSided": True}],
        "animations": [animation],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "party_hat.glb"))


if __name__ == "__main__":
    write()
