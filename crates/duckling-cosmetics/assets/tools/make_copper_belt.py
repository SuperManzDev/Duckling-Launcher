"""Build a closed copper-trimmed belt with a readable front buckle.

The old Blockbench cuboids remain as the fallback on clients without meshes.
"""

import os

from make_codex_meshes import rgb, sheen
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive


INK = (48, 36, 43)
LEATHER = (94, 54, 42)
BRONZE = (124, 67, 42)
COPPER = (191, 105, 53)
GOLD = (242, 165, 79)
LIGHT = (255, 218, 129)
TEAL = (56, 185, 176)
ICE = (161, 246, 224)


PERIMETER = [(-3.62, -2.50), (3.62, -2.50), (4.23, -1.91),
             (4.23, 1.91), (3.62, 2.50), (-3.62, 2.50),
             (-4.23, 1.91), (-4.23, -1.91)]


def belt(model):
    # An actual closed band, including bevels, inner wall and underside.
    profile = ((0.87, 13.64), (0.98, 13.64), (1.03, 13.89),
               (1.03, 15.11), (0.98, 15.38), (0.87, 15.38))
    for i, (x0, z0) in enumerate(PERIMETER):
        x1, z1 = PERIMETER[(i+1) % len(PERIMETER)]
        direction = (x0+x1, 0, z0+z1)
        colors = (INK, BRONZE, LEATHER, COPPER, GOLD, INK)
        for j, (s0, y0) in enumerate(profile):
            s1, y1 = profile[(j+1) % len(profile)]
            a, b = (x0*s0,y0,z0*s0), (x1*s0,y0,z1*s0)
            c, d = (x1*s1,y1,z1*s1), (x0*s1,y1,z0*s1)
            outward = ((0,1,0) if j == 4 else
                       (-direction[0],0,-direction[2]) if j == 5 else
                       (0,-1,0) if j == 0 else direction)
            model.tri(a,b,c,colors[j],outward)
            model.tri(a,c,d,colors[j],outward)


def buckle(model):
    z = -2.91
    # Raised copper frame and dark enamel opening give the belt a clear
    # readable center at a normal player-camera distance.
    model.tri((-1.26,13.54,z+0.07),(1.26,13.54,z+0.07),
              (1.26,15.50,z+0.07),INK,(0,0,-1))
    model.tri((-1.26,13.54,z+0.07),(1.26,15.50,z+0.07),
              (-1.26,15.50,z+0.07),INK,(0,0,-1))
    frame = [(-1.31,13.49,z), (1.31,13.49,z),
             (1.31,15.57,z), (-1.31,15.57,z)]
    for a,b in zip(frame,frame[1:]+frame[:1]):
        model.beam(a,b,0.22,0.22,(LIGHT,GOLD,BRONZE,GOLD,LIGHT))
    # Small raised mint compass rose marks Arctic's explorer styling.
    tip = (0,14.53,z-0.38)
    ring = [(0,15.17,z-0.09), (0.57,14.53,z-0.09),
            (0,13.90,z-0.09), (-0.57,14.53,z-0.09)]
    for i,tone in enumerate((ICE,TEAL,GOLD,TEAL)):
        model.tri(tip,ring[i],ring[(i+1)%4],tone,(0,0,-1))

    # Two side keepers have real thickness when the player turns.
    for x in (-3.30,3.30):
        model.beam((x,13.58,-2.71),(x,15.44,-2.71),
                   0.21,0.21,(LIGHT,GOLD,BRONZE,GOLD,LIGHT))


def write():
    model=Sculpture()
    belt(model)
    buckle(model)
    glb=Glb()
    part=model.gltf()
    mesh=primitive(glb,part,[0,0,0],0)
    mesh['attributes']['NORMAL']=glb.add(part['normal'],'VEC3',5126)
    doc={
        'asset': {'version':'2.0','generator':'Arctic Copper Belt sculpture'},
        'scene':0,
        'scenes':[{'nodes':[0],'extras':{'arctic':{'sheen':
            sheen(rgb(255,214,126),4.8,0.16,(0.03,0.02,-0.02),0.28,0)}}}],
        'nodes':[{'name':'body','mesh':0}],
        'meshes':[{'name':'copper_belt','primitives':[mesh]}],
        'materials':[{'name':'copper_and_leather','pbrMetallicRoughness':{
            'baseColorFactor':[1,1,1,1],'metallicFactor':0.45,
            'roughnessFactor':0.48},'doubleSided':True}],
    }
    glb.write(doc,os.path.join(ASSETS,'cosmetics','copper_belt.glb'))


if __name__=='__main__':
    write()
