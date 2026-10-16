"""Sculpt a readable, dimensional Crystal Pendant for the body slot.

The existing cuboid model and texture remain the fallback for older clients.
"""

import os

from make_codex_meshes import rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive


DEEP = (21, 59, 99)
COBALT = (37, 112, 166)
BLUE = (49, 167, 209)
CYAN = (87, 219, 228)
ICE = (176, 249, 250)
WHITE = (239, 255, 249)
BRONZE = (113, 75, 42)
GOLD = (231, 173, 80)
SUN = (255, 222, 130)


def gem(model):
    """Closed six-facet crystal, cut into a broad diamond silhouette."""
    contour = [(0, 20.63, -3.16), (1.12, 19.57, -3.16),
               (0.87, 18.33, -3.16), (0, 16.94, -3.16),
               (-0.87, 18.33, -3.16), (-1.12, 19.57, -3.16)]
    front = (0, 19.04, -4.19)
    rear = (0, 19.04, -2.91)
    front_colors = (WHITE, ICE, CYAN, BLUE, COBALT, ICE)
    back_colors = (COBALT, DEEP, BLUE, COBALT, DEEP, BLUE)
    for i in range(len(contour)):
        j = (i + 1) % len(contour)
        model.tri(front, contour[i], contour[j], front_colors[i], (0, 0, -1))
        model.tri(rear, contour[j], contour[i], back_colors[i], (0, 0, 1))
    # A narrow raised internal facet makes the crystal read as cut glass
    # rather than a single flat colored diamond.
    model.tri((-0.33, 19.93, -4.21), (0.05, 20.28, -4.21),
              (0.15, 19.24, -4.21), WHITE, (0, 0, -1))


def jewelry(model):
    # Chain follows the front of the torso instead of floating as a card.
    left = [(-2.82, 23.12, -2.30), (-2.40, 22.39, -2.49),
            (-1.46, 21.45, -2.73), (-0.32, 20.82, -3.02)]
    right = [(-x, y, z) for x, y, z in left]
    for chain in (left, right):
        for a, b in zip(chain, chain[1:]):
            model.beam(a, b, 0.13, 0.15,
                       (SUN, GOLD, BRONZE, GOLD, SUN))

    # The raised frame is a real thick rim around the stone. The small top
    # bail connects the two chain ends to the pendant.
    ring = [(0, 20.82, -3.23), (1.43, 19.55, -3.23),
            (1.10, 18.15, -3.23), (0, 16.58, -3.23),
            (-1.10, 18.15, -3.23), (-1.43, 19.55, -3.23)]
    for a, b in zip(ring, ring[1:] + ring[:1]):
        model.beam(a, b, 0.22, 0.22,
                   (SUN, GOLD, BRONZE, GOLD, SUN))
    model.beam((-0.32, 20.82, -3.02), (0.32, 20.82, -3.02),
               0.25, 0.25, (SUN, GOLD, BRONZE, GOLD, SUN))
    for x in (-1.26, 1.26):
        model.beam((x, 19.66, -3.27), (x * 0.82, 19.31, -3.70),
                   0.20, 0.14, (SUN, GOLD, BRONZE, GOLD, SUN))


def write():
    model = Sculpture()
    jewelry(model)
    gem(model)
    glb = Glb()
    part = model.gltf()
    mesh = primitive(glb, part, [0, 0, 0], 0)
    mesh["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Crystal Pendant sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0], "extras": {"arctic": {"sheen":
            sheen(rgb(186, 255, 247), 3.6, 0.19, (0.02, 0.05, -0.05), 0.29, 0)}}}],
        "nodes": [{"name": "body", "mesh": 0}],
        "meshes": [{"name": "crystal_pendant", "primitives": [mesh]}],
        "materials": [{"name": "gold_and_cut_crystal", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.24,
            "roughnessFactor": 0.38}, "doubleSided": True}],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "crystal_pendant.glb"))


if __name__ == "__main__":
    write()
