"""Sculpt a faceted crystal crown that wraps the Minecraft player's head.

The existing ice_crown.geo.json remains the fallback for cuboid-only clients.
"""

import os

from make_codex_meshes import rgb, sheen
from make_crown import OCTAGON
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive


MIDNIGHT = (20, 55, 100)
COBALT = (32, 105, 161)
GLACIER = (47, 154, 205)
TURQUOISE = (77, 212, 232)
SKY = (129, 234, 247)
SNOW = (216, 252, 255)
LILAC = (155, 184, 234)


def band(model):
    """Closed, bevelled icy circlet: no card-like open sides."""
    profile = ((0.88, 31.78), (0.98, 31.78), (1.025, 32.12),
               (1.01, 32.61), (0.95, 32.75), (0.86, 32.61))
    for index, (x0, z0) in enumerate(OCTAGON):
        x1, z1 = OCTAGON[(index + 1) % len(OCTAGON)]
        outward = (x0 + x1, 0, z0 + z1)
        shades = (MIDNIGHT, COBALT, GLACIER,
                  SKY if index % 2 == 0 else TURQUOISE, COBALT, MIDNIGHT)
        for side, (s0, y0) in enumerate(profile):
            s1, y1 = profile[(side + 1) % len(profile)]
            a, b = (x0*s0, y0, z0*s0), (x1*s0, y0, z1*s0)
            c, d = (x1*s1, y1, z1*s1), (x0*s1, y1, z0*s1)
            normal = ((0, 1, 0) if side == 3 else
                      (-outward[0], 0, -outward[2]) if side in (4, 5) else
                      (0, -1, 0) if side == 0 else outward)
            model.tri(a, b, c, shades[side], normal)
            model.tri(a, c, d, shades[side], normal)


def crystal(model, x, z, tangent, outward, width, height, lean=0.0):
    """A four-sided solid shard with a broad root and narrow luminous ridge."""
    tx, tz = tangent
    ox, oz = outward
    depth = max(0.47, width*0.53)
    base = []
    shoulder = []
    for tangent_sign, outward_sign in ((-1, -1), (1, -1),
                                       (1, 1), (-1, 1)):
        base.append((x + tx*tangent_sign*width/2 + ox*outward_sign*depth/2,
                     32.50,
                     z + tz*tangent_sign*width/2 + oz*outward_sign*depth/2))
        shoulder.append((x + tx*tangent_sign*width*0.39 + ox*outward_sign*depth*0.40,
                         33.04,
                         z + tz*tangent_sign*width*0.39 + oz*outward_sign*depth*0.40))
    tip = (x + ox*(0.22+lean), height, z + oz*(0.22+lean))
    for side in range(4):
        nxt = (side+1) % 4
        model.tri(base[side], base[nxt], shoulder[nxt],
                  (COBALT, GLACIER, SKY, GLACIER)[side])
        model.tri(base[side], shoulder[nxt], shoulder[side],
                  (GLACIER, TURQUOISE, SNOW, TURQUOISE)[side])
        model.tri(shoulder[side], shoulder[nxt], tip,
                  (GLACIER, SKY, SNOW, LILAC)[side])
    model.tri(base[0], base[2], base[1], MIDNIGHT, (0, -1, 0))
    model.tri(base[0], base[3], base[2], MIDNIGHT, (0, -1, 0))


def frost_jewel(model, z, facing):
    """Large central snow-ice gem on both the front and rear of the band."""
    surface = z + facing*0.17
    ridge = z + facing*0.43
    center = (0, 32.36, ridge)
    corners = [(-0.69, 32.36, surface), (0, 32.91, surface),
               (0.69, 32.36, surface), (0, 31.98, surface)]
    for i, color in enumerate((SKY, SNOW, GLACIER, TURQUOISE)):
        model.tri(center, corners[i], corners[(i+1) % 4], color,
                  (0, 0, facing))
    model.tri((-0.12, 32.61, ridge+facing*0.01),
              (0.08, 32.76, ridge+facing*0.01),
              (0.20, 32.50, ridge+facing*0.01), SNOW,
              (0, 0, facing))


def sculpture():
    model = Sculpture()
    band(model)
    # Taller peaks face front and rear; stepped corner crystals make the
    # silhouette clear from the side rather than just a front-facing row.
    for z, outward in ((4.42, (0, 1)), (-4.42, (0, -1))):
        for x, height, width in ((-3.14, 33.88, 1.01),
                                 (-1.58, 34.69, 1.12),
                                 (0, 35.59, 1.46),
                                 (1.58, 34.69, 1.12),
                                 (3.14, 33.88, 1.01)):
            crystal(model, x, z, (1, 0), outward, width, height,
                    0.09 if x < 0 else -0.09)
        frost_jewel(model, z, outward[1])
    for x, outward in ((4.42, (1, 0)), (-4.42, (-1, 0))):
        for z, height in ((-2.64, 33.84), (0, 34.48), (2.64, 33.84)):
            crystal(model, x, z, (0, 1), outward, 1.07, height)
    return model


def write():
    glb = Glb()
    part = sculpture().gltf()
    mesh = primitive(glb, part, [0, 0, 0], 0)
    mesh["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Ice Crown sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
            sheen(rgb(177, 244, 255), 4.1, 0.22, (0.06, -0.02, 0.03), 0.30, 0)}}}],
        "nodes": [{"name": "head", "mesh": 0}],
        "meshes": [{"name": "ice_crown", "primitives": [mesh]}],
        "materials": [{"name": "carved_ice", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.12,
            "roughnessFactor": 0.35}, "doubleSided": True}],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "ice_crown.glb"))


if __name__ == "__main__":
    write()
