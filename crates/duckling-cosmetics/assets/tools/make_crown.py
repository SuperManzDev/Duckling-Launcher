"""Build a faceted royal crown with a head-following mesh.

The older Blockbench crown remains available as the cuboid fallback.
"""

import os

from make_codex_meshes import rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive
from make_pocket_penguin import cuboid


BRONZE = (118, 62, 36)
COPPER = (201, 111, 44)
GOLD = (255, 188, 56)
SUN = (255, 218, 92)
IVORY = (255, 242, 163)
CRIMSON = (159, 31, 57)
RUBY = (223, 48, 70)
ROSE = (255, 117, 115)
GLINT = (255, 217, 179)

# Chamfered square: unlike a flat crown card, every facet has a side face.
OCTAGON = [(-3.2, -4.5), (3.2, -4.5), (4.5, -3.2), (4.5, 3.2),
           (3.2, 4.5), (-3.2, 4.5), (-4.5, 3.2), (-4.5, -3.2)]


def band(model):
    # The profile has an outward lip, a polished top bevel, a dark inner
    # wall, and a real underside. It wraps the head rather than crossing it.
    profile = ((0.97, 31.0), (1.015, 31.25), (1.015, 31.88),
               (0.97, 32.19), (0.905, 32.19), (0.885, 31.88),
               (0.885, 31.25))
    for index, (x0, z0) in enumerate(OCTAGON):
        x1, z1 = OCTAGON[(index + 1) % len(OCTAGON)]
        outward = (x0 + x1, 0, z0 + z1)
        colors = (COPPER, GOLD, SUN,
                  IVORY if index % 2 == 0 else SUN,
                  GOLD, BRONZE, BRONZE)
        for face, (scale_a, y_a) in enumerate(profile):
            scale_b, y_b = profile[(face + 1) % len(profile)]
            a = (x0 * scale_a, y_a, z0 * scale_a)
            b = (x1 * scale_a, y_a, z1 * scale_a)
            c = (x1 * scale_b, y_b, z1 * scale_b)
            d = (x0 * scale_b, y_b, z0 * scale_b)
            direction = ((0, 1, 0) if face == 3 else
                         (-outward[0], 0, -outward[2]) if face in (4, 5) else
                         (0, -1, 0) if face == 6 else outward)
            model.tri(a, b, c, colors[face], direction)
            model.tri(a, c, d, colors[face], direction)


def point(model, x, z, width, depth, height):
    """Solid four-facet golden crest, tapering to a precise high point."""
    bottom = 32.05
    corners = [(x-width/2, bottom, z-depth/2),
               (x+width/2, bottom, z-depth/2),
               (x+width/2, bottom, z+depth/2),
               (x-width/2, bottom, z+depth/2)]
    shoulder = [(a, 32.53, c) for a, _, c in corners]
    tip = (x, height, z)
    for i in range(4):
        nxt = (i + 1) % 4
        face = (SUN, IVORY, GOLD, IVORY)[i]
        model.tri(corners[i], corners[nxt], shoulder[nxt], GOLD)
        model.tri(corners[i], shoulder[nxt], shoulder[i], face)
        model.tri(shoulder[i], shoulder[nxt], tip, face)
    model.tri(corners[0], corners[2], corners[1], BRONZE, (0, -1, 0))
    model.tri(corners[0], corners[3], corners[2], BRONZE, (0, -1, 0))


def jewel(model, x, y, z, facing):
    """Inset ruby with raised facets, visible on both front and rear."""
    tip = (x, y, z + facing * 0.38)
    back = (x, y, z - facing * 0.06)
    corners = [(x, y+0.78, z), (x+0.66, y, z),
               (x, y-0.78, z), (x-0.66, y, z)]
    for i, tone in enumerate((ROSE, RUBY, CRIMSON, RUBY)):
        nxt = (i+1) % 4
        model.tri(tip, corners[i], corners[nxt], tone, (0, 0, facing))
        model.tri(back, corners[nxt], corners[i], CRIMSON, (0, 0, -facing))
    # A tiny pale facet makes the red stone legible at normal player scale.
    model.tri((x-0.24, y+0.24, z+facing*0.41),
              (x-0.05, y+0.44, z+facing*0.41),
              (x+0.03, y+0.14, z+facing*0.41), GLINT, (0, 0, facing))


def sculpture():
    model = Sculpture()
    band(model)
    for z in (-4.48, 4.48):
        point(model, 0, z, 1.42, 0.82, 34.27)
        for x in (-3.18, 3.18):
            point(model, x, z, 1.05, 0.72, 33.64)
        jewel(model, 0, 32.36, z + (-0.35 if z < 0 else 0.35), -1 if z < 0 else 1)
    for x in (-4.48, 4.48):
        point(model, x, 0, 0.72, 1.04, 33.60)
    # Raised gold studs and brighter rim cuts make the side profile coherent.
    for x in (-2.15, 2.15):
        for z in (-4.61, 4.61):
            cuboid(model, (x, 31.61, z), (0.40, 0.40, 0.15), SUN)
    for z in (-2.1, 2.1):
        for x in (-4.61, 4.61):
            cuboid(model, (x, 31.61, z), (0.15, 0.40, 0.40), SUN)
    return model


def write():
    glb = Glb()
    part = sculpture().gltf()
    mesh = primitive(glb, part, [0, 0, 0], 0)
    mesh["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Royal Crown sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
            sheen(rgb(255, 241, 174), 5.0, 0.25, (0.05, 0.02, -0.05), 0.23, 0)}}}],
        "nodes": [{"name": "head", "mesh": 0}],
        "meshes": [{"name": "royal_crown", "primitives": [mesh]}],
        "materials": [{"name": "hammered_gold_and_rubies", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.58,
            "roughnessFactor": 0.42}, "doubleSided": True}],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "crown.glb"))


if __name__ == "__main__":
    write()
