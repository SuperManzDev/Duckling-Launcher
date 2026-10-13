"""Build a sculpted, animated Pocket Penguin for the shoulder slot.

The paired Bedrock model stays in the catalog as a fallback. Coordinates use
Minecraft player pixels: the broad perch rests on the player's left shoulder.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of
from make_frost_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


NIGHT = (17, 32, 60)
NAVY = (25, 52, 83)
COBALT = (37, 85, 121)
BLUE = (50, 124, 158)
ICE = (81, 192, 210)
PALE = (175, 232, 226)
WHITE = (241, 244, 232)
SNOW = (218, 228, 222)
GOLD = (231, 181, 88)
ORANGE = (255, 150, 63)
SHADOW = (20, 34, 43)

CX = 7.6


def ring(cx, y, cz, rx, rz, bevel=0.55):
    b = min(bevel, rx * 0.65, rz * 0.65)
    return [
        (cx - rx + b, y, cz - rz), (cx + rx - b, y, cz - rz),
        (cx + rx, y, cz - rz + b), (cx + rx, y, cz + rz - b),
        (cx + rx - b, y, cz + rz), (cx - rx + b, y, cz + rz),
        (cx - rx, y, cz + rz - b), (cx - rx, y, cz - rz + b),
    ]


def tapered_body(mesh, levels, front=NIGHT, side=NAVY, back=COBALT, top=NAVY):
    """A closed beveled block with changing width and depth at each height."""
    rings = [ring(*level) for level in levels]
    for lower, upper in zip(rings, rings[1:]):
        for i in range(8):
            j = (i + 1) % 8
            color = front if i == 0 else back if i == 4 else side if i in (2, 6) else COBALT
            mesh.tri(lower[i], lower[j], upper[j], color)
            mesh.tri(lower[i], upper[j], upper[i], color)
    for points, color, reverse in ((rings[0], side, True), (rings[-1], top, False)):
        center = np.asarray(points).mean(axis=0)
        for i in range(8):
            j = (i + 1) % 8
            a, b = (points[j], points[i]) if reverse else (points[i], points[j])
            mesh.tri(center, a, b, color)


def polygon(mesh, points, color, edge=NAVY, thick=0.16):
    """Raised, closed front-facing detail in the XY plane (negative Z faces out)."""
    arr = [np.asarray(p, dtype=float) for p in points]
    center = np.asarray(arr).mean(axis=0)
    for i in range(len(arr)):
        j = (i + 1) % len(arr)
        mesh.tri(center, arr[i], arr[j], color)
        a = arr[i] + np.array((0, 0, thick))
        b = arr[j] + np.array((0, 0, thick))
        mesh.tri(arr[i], a, b, edge)
        mesh.tri(arr[i], b, arr[j], edge)


def cuboid(mesh, center, size, colors):
    x, y, z = center
    w, h, d = [n / 2 for n in size]
    corners = [(x-w,y-h,z-d),(x+w,y-h,z-d),(x+w,y+h,z-d),(x-w,y+h,z-d),
               (x-w,y-h,z+d),(x+w,y-h,z+d),(x+w,y+h,z+d),(x-w,y+h,z+d)]
    quads = ((0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2))
    for i, q in enumerate(quads):
        col = colors[i] if isinstance(colors[0], tuple) else colors
        mesh.tri(corners[q[0]],corners[q[1]],corners[q[2]],col)
        mesh.tri(corners[q[0]],corners[q[2]],corners[q[3]],col)


def base_and_torso():
    model = Sculpture()
    # Icy shoulder perch, with a dark mounting pad and a bright gold edge.
    tapered_body(model, [(CX,23.55,0,3.45,3.18,0.68),
                         (CX,24.15,0,3.6,3.33,0.68),
                         (CX,24.43,0,3.32,3.07,0.60)],
                 front=BLUE, side=COBALT, back=BLUE, top=PALE)
    cuboid(model, (CX,23.68,0), (6.8,0.22,5.7), (GOLD,GOLD,GOLD,GOLD,GOLD,GOLD))
    tapered_body(model, [(CX,24.48,0.08,2.02,1.75,0.64),
                         (CX,25.10,0.08,2.55,2.13,0.72),
                         (CX,28.30,0.10,2.78,2.43,0.76),
                         (CX,29.74,0.12,2.20,2.05,0.72)],
                 front=NIGHT, side=NAVY, back=COBALT, top=NAVY)
    # Deep border and a raised snow-white bib: readable even on a dark skin.
    polygon(model, [(5.33,28.72,-2.62),(6.03,29.05,-2.62),(9.17,29.05,-2.62),
                    (9.86,28.72,-2.62),(9.68,26.12,-2.62),(8.85,25.15,-2.62),
                    (6.36,25.15,-2.62),(5.52,26.12,-2.62)], NAVY, thick=0.12)
    polygon(model, [(5.67,28.55,-2.80),(6.25,28.80,-2.80),(8.95,28.80,-2.80),
                    (9.52,28.55,-2.80),(9.33,26.28,-2.80),(8.66,25.47,-2.80),
                    (6.54,25.47,-2.80),(5.86,26.28,-2.80)], WHITE, edge=SNOW)
    # Back insignia gives the perch a second readable view. It is a raised
    # ice crystal, not a flat texture painted on the dark body.
    polygon(model, [(CX,29.10,2.66),(CX+1.55,27.68,2.66),
                    (CX,26.10,2.66),(CX-1.55,27.68,2.66)], BLUE, edge=NIGHT)
    polygon(model, [(CX,28.86,2.86),(CX+1.18,27.68,2.86),
                    (CX,26.42,2.86),(CX-1.18,27.68,2.86)], ICE, edge=PALE)
    polygon(model, [(CX,28.35,3.07),(CX+0.55,27.68,3.07),
                    (CX,26.95,3.07),(CX-0.55,27.68,3.07)], WHITE, edge=PALE)
    # Broad, separated webbed feet overhang the perch at the front.
    for x in (6.32, 8.88):
        cuboid(model, (x,24.66,-1.98), (1.65,0.58,2.30),
               (ORANGE,GOLD,ORANGE,GOLD,GOLD,ORANGE))
        cuboid(model, (x,24.55,-2.76), (1.86,0.27,0.55), ORANGE)
    # Scarf collar and a hanging strip add a clean cyan accent.
    cuboid(model, (CX,29.35,-2.21), (4.82,0.77,0.76),
           (PALE,BLUE,ICE,ICE,PALE,BLUE))
    cuboid(model, (CX,29.04,2.06), (4.55,0.44,0.63), BLUE)
    polygon(model, [(8.54,29.19,-2.93),(9.63,29.16,-2.93),
                    (9.40,26.83,-2.93),(8.72,26.52,-2.93)], ICE, edge=BLUE)
    polygon(model, [(8.71,26.82,-3.11),(9.42,26.90,-3.11),
                    (9.39,26.55,-3.11),(8.72,26.45,-3.11)], GOLD, edge=GOLD)
    return model


def penguin_head():
    model = Sculpture()
    tapered_body(model, [(CX,29.33,0.00,2.23,2.10,0.70),
                         (CX,30.04,-0.04,2.77,2.50,0.78),
                         (CX,32.45,0.00,2.78,2.54,0.75),
                         (CX,33.16,0.04,2.32,2.13,0.67)],
                 front=NIGHT, side=NAVY, back=COBALT, top=COBALT)
    # White cheek mask reaches around the front corners, so the face is not
    # mistaken for a featureless dark block at three-quarter angles.
    polygon(model, [(5.15,30.45,-2.62),(5.65,31.26,-2.62),
                    (9.55,31.26,-2.62),(10.05,30.45,-2.62),
                    (9.67,29.66,-2.62),(5.53,29.66,-2.62)], SNOW, edge=NAVY)
    for x in (5.02,10.18):
        cuboid(model,(x,30.43,-2.12),(0.40,1.38,1.24),SNOW)
    polygon(model, [(CX,32.55,2.66),(CX+0.70,31.69,2.66),
                    (CX,31.25,2.66),(CX-0.70,31.69,2.66)], ICE, edge=BLUE)
    # Beak is a small orange wedge that projects distinctly in profile.
    a,b,c,d = (7.08,30.48,-2.82),(8.12,30.48,-2.82),(8.0,29.94,-2.82),(7.20,29.94,-2.82)
    tip = (CX,30.06,-3.72)
    for p,q,col in ((a,b,ORANGE),(b,c,GOLD),(c,d,ORANGE),(d,a,GOLD)):
        model.tri(p,q,tip,col)
    model.tri(a,d,c,GOLD)
    model.tri(a,c,b,GOLD)
    # Two small ear/crest facets and a forehead gem catch light from behind.
    for x in (5.68,9.52):
        polygon(model, [(x-0.42,32.71,-2.36),(x+0.42,32.71,-2.36),
                        (x,33.28,-2.36)], BLUE, edge=COBALT)
    return model


def flipper(side):
    model = Sculpture()
    center = CX + side * 2.54
    tip = CX + side * 4.55
    polygon(model, [(center,29.27,0.40),(center+side*0.72,29.07,0.51),
                    (tip,26.32,0.76),(tip-side*0.32,25.96,0.76),
                    (center+side*0.34,26.54,0.43)], NAVY, edge=NIGHT, thick=1.24)
    polygon(model, [(center+side*0.15,28.39,-0.10),
                    (center+side*0.43,28.12,-0.10),
                    (tip-side*0.46,26.37,-0.10),
                    (center+side*0.18,27.01,-0.10)], COBALT, edge=NAVY, thick=0.12)
    return model


def eye(x):
    model = Sculpture()
    cuboid(model, (x,31.68,-2.86), (0.90,1.02,0.31),
           (WHITE,PALE,WHITE,PALE,WHITE,PALE))
    cuboid(model, (x+0.12,31.63,-3.08), (0.50,0.69,0.20), NIGHT)
    cuboid(model, (x+0.20,31.82,-3.20), (0.16,0.18,0.08), ICE)
    return model


def add_mesh(glb, model, offset, name):
    part = model.gltf()
    out = primitive(glb, part, offset, 0)
    out["attributes"]["NORMAL"] = glb.add(part["normal"], "VEC3", 5126)
    return {"name": name, "primitives": [out]}


def blink(t):
    phase = t % 3.2
    # Fast close, brief hold, fast open. The second blink keeps the loop alive.
    distance = min(abs(phase - 1.27), abs(phase - 2.95))
    amount = max(0.07, min(1.0, (distance - 0.025) / 0.095))
    return [1.0, amount, 1.0]


def write():
    glb = Glb()
    head_pivot = [CX,30.20,0.0]
    left_pivot = [CX-2.54,28.81,0.45]
    right_pivot = [CX+2.54,28.81,0.45]
    eye_left = [CX-1.16,31.68,-2.96]
    eye_right = [CX+1.16,31.68,-2.96]
    models = [base_and_torso(), penguin_head(), flipper(-1), flipper(1),
              eye(eye_left[0]), eye(eye_right[0])]
    offsets = [[0,0,0],head_pivot,left_pivot,right_pivot,eye_left,eye_right]
    meshes = [add_mesh(glb, model, offset, name) for model,offset,name in
              zip(models, offsets, ("perch_and_body","penguin_head","left_flipper",
                                    "right_flipper","left_eye","right_eye"))]
    nodes = [
        {"name":"body","mesh":0,"children":[1,2,3]},
        {"name":"penguin_head","mesh":1,"translation":head_pivot,"children":[4,5]},
        {"name":"left_flipper","mesh":2,"translation":left_pivot},
        {"name":"right_flipper","mesh":3,"translation":right_pivot},
        {"name":"left_eye","mesh":4,"translation":[eye_left[i]-head_pivot[i] for i in range(3)]},
        {"name":"right_eye","mesh":5,"translation":[eye_right[i]-head_pivot[i] for i in range(3)]},
    ]
    period = 3.2
    tracks = [
        (1,"rotation",lambda t: quat_z(0.060*math.sin(2*math.pi*t/period+0.35))),
        (2,"rotation",lambda t: mul(quat_z(-0.11*math.sin(4*math.pi*t/period)),
                                    quat_y(0.045*math.sin(2*math.pi*t/period)))),
        (3,"rotation",lambda t: mul(quat_z(0.11*math.sin(4*math.pi*t/period)),
                                    quat_y(-0.045*math.sin(2*math.pi*t/period)))),
        (4,"scale",blink),
        (5,"scale",blink),
    ]
    animation = animation_of(glb,period,64,tracks)
    doc = {
        "asset":{"version":"2.0","generator":"Arctic Pocket Penguin sculpture"},
        "scene":0,"scenes":[{"nodes":[0]}],"nodes":nodes,"meshes":meshes,
        "materials":[{"name":"painted_penguin","pbrMetallicRoughness":{
            "baseColorFactor":[1,1,1,1],"metallicFactor":0.08,"roughnessFactor":0.72},
            "doubleSided":True}],
        "animations":[animation],
    }
    glb.write(doc, os.path.join(ASSETS,"cosmetics","pocket_penguin.glb"))


if __name__ == "__main__":
    write()
