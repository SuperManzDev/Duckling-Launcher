"""Build a dimensional, ice-edged Winter Mustache for the head slot.

The original textured Bedrock model stays as the fallback on older clients.
"""

import os

from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive


NIGHT = (25, 57, 79)
DEEP = (39, 105, 135)
BLUE = (75, 178, 205)
ICE = (153, 230, 238)
WHITE = (245, 255, 247)


def face():
    mesh = Sculpture()
    for sign in (-1, 1):
        points = [
            (sign * 0.23, 26.38, -5.08),
            (sign * 1.12, 25.91, -5.55),
            (sign * 2.36, 25.75, -5.61),
            (sign * 3.30, 26.12, -5.50),
            (sign * 3.62, 27.08, -5.37),
        ]
        sizes = (0.58, 0.76, 0.68, 0.41, 0.10)
        # The dark lower ridge outlines the ice against both light and dark
        # skins. The raised pale ridge gives the full length a snowy face.
        for index, (a, b) in enumerate(zip(points, points[1:])):
            mesh.beam(a, b, sizes[index], sizes[index + 1],
                      (NIGHT, DEEP, BLUE, NIGHT, DEEP))
            front_a = (a[0], a[1] + 0.14, a[2] - 0.25)
            front_b = (b[0], b[1] + 0.14, b[2] - 0.25)
            mesh.beam(front_a, front_b,
                      sizes[index] * 0.57, sizes[index + 1] * 0.57,
                      (ICE, WHITE, ICE, BLUE, WHITE))
        # One crystalline lower tuft makes each half read like curled fur
        # rather than a plain metal line.
        root = (sign * 2.17, 25.56, -5.59)
        mesh.beam(root, (sign * 2.68, 24.93, -5.72),
                  0.41, 0.05, (DEEP, ICE, WHITE, BLUE, ICE))
    return mesh


def write():
    glb = Glb()
    part = face().gltf()
    out = primitive(glb, part, (0, 24, 0), 0)
    out["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    doc = {
        "asset": {"version": "2.0", "generator": "Arctic Winter Mustache sculpture"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "head", "mesh": 0, "translation": [0, 24, 0]}],
        "meshes": [{"name": "winter_mustache", "primitives": [out]}],
        "materials": [{"name": "frosted_fur", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
            "roughnessFactor": 0.8}, "doubleSided": True}],
    }
    glb.write(doc, os.path.join(ASSETS, "cosmetics", "winter_mustache.glb"))


if __name__ == "__main__":
    write()
