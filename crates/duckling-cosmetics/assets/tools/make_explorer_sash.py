"""Build an explorer sash that wraps the torso rather than lying on one face.

The original cuboid model remains the fallback for clients without meshes.
"""

import math
import os

from make_codex_meshes import rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive
from make_pocket_penguin import cuboid


INK = (31, 68, 103)
INDIGO = (139, 212, 233)
BLUE = (175, 232, 243)
PALE_BLUE = (207, 250, 250)
BRONZE = (117, 76, 47)
GOLD = (231, 166, 79)
IVORY = (255, 224, 145)
TEAL = (65, 200, 186)
CREAM = (255, 242, 198)


def corners(a, b, width, front):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    px, py = -dy/length*width/2, dx/length*width/2
    z_offset = -0.24 if front else 0.24
    outer = [(a[0]-px,a[1]-py,a[2]+z_offset),
             (a[0]+px,a[1]+py,a[2]+z_offset),
             (b[0]+px,b[1]+py,b[2]+z_offset),
             (b[0]-px,b[1]-py,b[2]+z_offset)]
    inner = [(x,y,z-z_offset*2) for x,y,z in outer]
    return outer,inner


def strap(model, points, front):
    colors = (BLUE, INDIGO, PALE_BLUE, BLUE)
    for i,(a,b) in enumerate(zip(points,points[1:])):
        outer,inner=corners(a,b,1.82,front)
        model.tri(outer[0],outer[1],outer[2],colors[i],
                  (0,0,-1 if front else 1))
        model.tri(outer[0],outer[2],outer[3],colors[i],
                  (0,0,-1 if front else 1))
        model.tri(inner[0],inner[2],inner[1],INK)
        model.tri(inner[0],inner[3],inner[2],INK)
        for side in (0,2):
            nxt=(side+1)%4
            model.tri(outer[side],inner[side],inner[nxt],INDIGO)
            model.tri(outer[side],inner[nxt],outer[nxt],INDIGO)
        # Continuous stitched borders give the sash a finished fabric edge.
        model.beam(outer[0],outer[3],0.105,0.105,
                   (IVORY,GOLD,BRONZE,GOLD,IVORY))
        model.beam(outer[1],outer[2],0.105,0.105,
                   (IVORY,GOLD,BRONZE,GOLD,IVORY))
        # One centered woven stripe gives the broad cloth a clear light
        # direction without filling it with visual noise.
        stripe_start=((outer[0][0]+outer[1][0])/2,
                      (outer[0][1]+outer[1][1])/2,
                      (outer[0][2]+outer[1][2])/2-0.06 if front else
                      (outer[0][2]+outer[1][2])/2+0.06)
        stripe_end=((outer[2][0]+outer[3][0])/2,
                    (outer[2][1]+outer[3][1])/2,
                    (outer[2][2]+outer[3][2])/2-0.06 if front else
                    (outer[2][2]+outer[3][2])/2+0.06)
        model.beam(stripe_start,stripe_end,0.105,0.105,
                   (PALE_BLUE,IVORY,BLUE,PALE_BLUE,IVORY))


def compass(model):
    cx,cy,z=-0.34,19.47,-3.17
    ring=[]
    for i in range(10):
        angle=2*math.pi*i/10
        ring.append((cx+0.85*math.cos(angle),
                     cy+0.85*math.sin(angle),z))
    for a,b in zip(ring,ring[1:]+ring[:1]):
        model.beam(a,b,0.14,0.14,
                   (IVORY,GOLD,BRONZE,GOLD,IVORY))
    for i in range(10):
        model.tri((cx,cy,z+0.07),ring[i],ring[(i+1)%10],INK,
                  (0,0,-1))
    points=[(cx,cy+0.62,z-0.10),(cx+0.26,cy,z-0.10),
            (cx,cy-0.62,z-0.10),(cx-0.26,cy,z-0.10)]
    tip=(cx,cy,z-0.27)
    for i,tone in enumerate((CREAM,TEAL,GOLD,TEAL)):
        model.tri(tip,points[i],points[(i+1)%4],tone,(0,0,-1))


def pouch(model):
    # A shallow front-mounted map pouch gives the hip end a purpose and a
    # clear side silhouette, without extending beyond the player's arm.
    cuboid(model,(2.75,14.10,-3.04),(1.78,2.12,0.85),
           (BRONZE,INK,BRONZE,GOLD,INDIGO,BRONZE))
    cuboid(model,(2.75,14.88,-3.53),(1.91,0.43,0.24),
           (IVORY,GOLD,BRONZE,GOLD,GOLD,GOLD))
    cuboid(model,(2.75,14.29,-3.59),(0.40,0.43,0.20),
           (TEAL,TEAL,INK,IVORY,TEAL,TEAL))


def write():
    model=Sculpture()
    front=[(-3.05,23.28,-2.39),(-1.48,20.82,-2.55),
           (0.50,17.70,-2.59),(2.83,14.13,-2.49)]
    back=[(x,y,-z) for x,y,z in front]
    strap(model,front,True)
    strap(model,back,False)
    # Shoulder and hip joins close the loop; the sash has no open card edge.
    for p,q in ((front[0],back[0]),(front[-1],back[-1])):
        model.beam(p,q,0.29,0.29,
                   (IVORY,GOLD,BRONZE,GOLD,IVORY))
    compass(model)
    pouch(model)
    glb=Glb()
    part=model.gltf()
    mesh=primitive(glb,part,[0,0,0],0)
    mesh['attributes']['NORMAL']=glb.add(part['normal'],'VEC3',5126)
    doc={
        'asset':{'version':'2.0','generator':'Arctic Explorer Sash sculpture'},
        'scene':0,
        'scenes':[{'nodes':[0],'extras':{'arctic':{'sheen':
            sheen(rgb(255,222,150),4.3,0.12,(0.02,-0.04,0.03),0.25,0)}}}],
        'nodes':[{'name':'body','mesh':0}],
        'meshes':[{'name':'explorer_sash','primitives':[mesh]}],
        'materials':[{'name':'canvas_brass_and_leather','pbrMetallicRoughness':{
            'baseColorFactor':[1,1,1,1],'metallicFactor':0.24,
            'roughnessFactor':0.57},'doubleSided':True}],
    }
    glb.write(doc,os.path.join(ASSETS,'cosmetics','explorer_sash.glb'))


if __name__=='__main__':
    write()
