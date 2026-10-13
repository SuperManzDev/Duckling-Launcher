"""Build a dimensional Snow Owl shoulder companion.

The Bedrock cuboid file remains the fallback. This mesh has a readable face,
folded feather volume, feet and tail from every viewing angle.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z


NIGHT = (29, 46, 62)
SLATE = (67, 88, 104)
BLUE = (103, 140, 166)
FROST = (176, 210, 220)
SHADOW = (155, 170, 177)
IVORY = (233, 229, 210)
WHITE = (251, 248, 231)
GOLD = (242, 181, 73)
AMBER = (255, 211, 103)
BLACK = (31, 37, 47)

CX = 7.6


def ring(cx, y, cz, rx, rz, bevel=0.5):
    b = min(bevel, rx * .65, rz * .65)
    return [
        (cx-rx+b,y,cz-rz), (cx+rx-b,y,cz-rz),
        (cx+rx,y,cz-rz+b), (cx+rx,y,cz+rz-b),
        (cx+rx-b,y,cz+rz), (cx-rx+b,y,cz+rz),
        (cx-rx,y,cz+rz-b), (cx-rx,y,cz-rz+b),
    ]


def tapered(mesh, levels, front=IVORY, side=SHADOW, back=WHITE, bevel=FROST):
    rings = [ring(*level) for level in levels]
    for lower, upper in zip(rings, rings[1:]):
        for i in range(8):
            j = (i+1) % 8
            color = front if i == 0 else back if i == 4 else side if i in (2,6) else bevel
            mesh.tri(lower[i],lower[j],upper[j],color)
            mesh.tri(lower[i],upper[j],upper[i],color)
    for points,color,reverse in ((rings[0],side,True),(rings[-1],back,False)):
        center = np.asarray(points).mean(axis=0)
        for i in range(8):
            j=(i+1)%8
            a,b=(points[j],points[i]) if reverse else (points[i],points[j])
            mesh.tri(center,a,b,color)


def polygon(mesh, points, color, edge=SLATE, thick=.15):
    contour=[np.asarray(p,dtype=float) for p in points]
    center=np.asarray(contour).mean(axis=0)
    for i,p in enumerate(contour):
        q=contour[(i+1)%len(contour)]
        mesh.tri(center,p,q,color)
        back=np.array((0,0,thick))
        mesh.tri(p,p+back,q+back,edge)
        mesh.tri(p,q+back,q,edge)


def feather(mesh, outline, front, rear, edge=SLATE, thick=.72):
    """A closed feather with its own back and sidewalls."""
    points=[np.asarray(p,dtype=float) for p in outline]
    center=np.asarray(points).mean(axis=0)
    back=[p+np.array((0,0,thick)) for p in points]
    rear_center=center+np.array((0,0,thick))
    for i,p in enumerate(points):
        j=(i+1)%len(points)
        mesh.tri(center,p,points[j],front)
        mesh.tri(rear_center,back[j],back[i],rear)
        mesh.tri(p,back[i],back[j],edge)
        mesh.tri(p,back[j],points[j],edge)


def face_disc(mesh, x, y, radius, z, color):
    pts=[(x+radius*math.cos(2*math.pi*i/8),
          y+radius*math.sin(2*math.pi*i/8),z) for i in range(8)]
    polygon(mesh,pts,color,edge=SHADOW,thick=.12)


def side_cheek(mesh, x, sign):
    """A side-facing feather mark without adding a third visible eye."""
    points=[(x,32.47,-1.44),(x,31.84,-2.23),(x,30.70,-2.31),
            (x,30.29,-1.39),(x,31.10,-.66)]
    center=(x+sign*.10,31.28,-1.54)
    for i,p in enumerate(points):
        mesh.tri(center,p,points[(i+1)%len(points)],FROST)


def perch_and_body():
    mesh=Sculpture()
    tapered(mesh,[(CX,23.48,.15,3.45,2.92,.54),
                  (CX,24.05,.15,3.55,3.02,.54),
                  (CX,24.38,.15,3.22,2.73,.52)],
            front=SLATE,side=NIGHT,back=BLUE,bevel=FROST)
    tapered(mesh,[(CX,24.38,.03,1.95,1.75,.54),
                  (CX,25.10,.03,2.62,2.15,.70),
                  (CX,28.14,.04,2.74,2.36,.72),
                  (CX,29.60,.04,2.15,2.03,.62)],
            front=IVORY,side=SHADOW,back=WHITE,bevel=FROST)
    # V-shaped layers turn a plain white block into a feathered chest.
    for y,width in ((28.75,1.68),(27.61,1.88),(26.49,1.59)):
        polygon(mesh,[(CX-width,y,-2.51),(CX,y-.72,-2.58),
                      (CX+width,y,-2.51),(CX,y-.32,-2.66)],
                WHITE,edge=FROST,thick=.13)
    # The reverse carries a blue feather emblem that remains visible from behind.
    polygon(mesh,[(CX,29.01,2.47),(CX+1.34,27.41,2.47),
                  (CX,25.85,2.47),(CX-1.34,27.41,2.47)],
            BLUE,edge=SLATE,thick=-.15)
    polygon(mesh,[(CX,28.45,2.66),(CX+.68,27.41,2.66),
                  (CX,26.42,2.66),(CX-.68,27.41,2.66)],
            WHITE,edge=FROST,thick=-.12)
    # Feet hook over the front lip, with separated gold talons.
    for x in (CX-1.23,CX+1.23):
        polygon(mesh,[(x-.40,24.76,-2.03),(x+.40,24.76,-2.03),
                      (x+.45,24.22,-2.77),(x-.45,24.22,-2.77)],
                GOLD,edge=SLATE,thick=.15)
        for dx in (-.34,0,.34):
            polygon(mesh,[(x+dx-.11,24.36,-2.88),(x+dx+.11,24.36,-2.88),
                          (x+dx,24.07,-3.26)],AMBER,edge=GOLD,thick=.1)
    return mesh


def head():
    mesh=Sculpture()
    tapered(mesh,[(CX,29.25,.04,2.18,1.94,.60),
                  (CX,29.88,.04,2.95,2.49,.73),
                  (CX,32.30,.04,3.02,2.55,.76),
                  (CX,33.15,.04,2.47,2.12,.62)],
            front=IVORY,side=IVORY,back=WHITE,bevel=FROST)
    # Layered nape feathers make the rear as intentional as the face.
    for y,width,color in ((32.75,1.91,IVORY),(31.91,2.12,FROST),
                          (31.02,1.94,IVORY),(30.25,1.55,WHITE)):
        polygon(mesh,[(CX-width,y,2.72),(CX,y-.73,2.78),
                      (CX+width,y,2.72),(CX,y-.30,2.86)],
                color,edge=BLUE,thick=-.12)
    # Two distinct facial discs and a dark V brow are the owl's main read.
    for x in (CX-1.34,CX+1.34):
        face_disc(mesh,x,31.22,1.36,-2.60,WHITE)
        face_disc(mesh,x,31.35,.68,-2.80,SLATE)
    polygon(mesh,[(CX-2.43,32.57,-2.65),(CX-1.35,32.24,-2.83),
                  (CX-.25,31.87,-2.93),(CX-.39,32.25,-2.83)],
            FROST,edge=SLATE,thick=.1)
    polygon(mesh,[(CX+2.43,32.57,-2.65),(CX+1.35,32.24,-2.83),
                  (CX+.25,31.87,-2.93),(CX+.39,32.25,-2.83)],
            FROST,edge=SLATE,thick=.1)
    # Raised ear tufts read from the front and side, rather than two flat pixels.
    for sign in (-1,1):
        feather(mesh,[(CX+sign*2.34,32.57,-.56),
                      (CX+sign*2.61,34.42,-.24),
                      (CX+sign*1.75,33.37,-.90),
                      (CX+sign*1.74,32.78,-1.03)],
                WHITE,SHADOW,edge=FROST,thick=1.1)
        side_cheek(mesh,CX+sign*3.05,sign)
    # Wedged beak projects far enough to remain visible in profile.
    a=(CX-.46,30.55,-2.90)
    b=(CX+.46,30.55,-2.90)
    c=(CX,29.79,-2.92)
    tip=(CX,30.17,-3.80)
    for p,q,color in ((a,b,AMBER),(b,c,GOLD),(c,a,GOLD)):
        mesh.tri(p,q,tip,color)
    mesh.tri(a,c,b,GOLD)
    return mesh


def wing(sign):
    mesh=Sculpture()
    # The folded panels overlap down the flank, but each has physical depth.
    for top,tip,width,z in ((29.06,26.37,1.75,.26),
                            (28.46,25.35,1.92,.62),
                            (27.69,24.77,1.69,.92)):
        x=CX+sign*2.53
        feather(mesh,[(x,top,z),(x+sign*1.38,top-.47,z+.15),
                      (x+sign*(1.68+width*.13),tip+.42,z+.43),
                      (x+sign*1.43,tip,z+.35),
                      (x+sign*.41,tip+.44,z+.06)],
                WHITE,IVORY,edge=SHADOW,thick=.84)
        polygon(mesh,[(x+sign*.29,top-.33,z-.10),
                      (x+sign*1.16,top-.67,z+.02),
                      (x+sign*1.39,tip+.66,z+.36),
                      (x+sign*.91,tip+.95,z+.25)],
                FROST,edge=BLUE,thick=.09)
    return mesh


def tail():
    mesh=Sculpture()
    for x,tip in ((CX-1.28,24.52),(CX,24.13),(CX+1.28,24.52)):
        feather(mesh,[(x-.49,26.52,2.13),(x+.49,26.52,2.13),
                      (x+.62,tip+.76,2.95),(x,tip,3.28),
                      (x-.62,tip+.76,2.95)],
                IVORY,WHITE,edge=BLUE,thick=.56)
    return mesh


def eye(x):
    mesh=Sculpture()
    face_disc(mesh,x,31.38,.49,-2.99,AMBER)
    face_disc(mesh,x,31.38,.26,-3.12,BLACK)
    face_disc(mesh,x-.12,31.55,.09,-3.25,WHITE)
    return mesh


def add_mesh(glb, sculpture, offset, name):
    part=sculpture.gltf()
    out=primitive(glb,part,offset,0)
    out['attributes']['NORMAL']=glb.add(part['normal'],'VEC3',5126)
    return {'name':name,'primitives':[out]}


def blink(t):
    phase=t%3.8
    distance=min(abs(phase-1.34),abs(phase-3.12))
    amount=max(.07,min(1.0,(distance-.024)/.09))
    return [1.0,amount,1.0]


def write():
    glb=Glb()
    head_pivot=[CX,30.12,.03]
    left_pivot=[CX-2.51,28.60,.27]
    right_pivot=[CX+2.51,28.60,.27]
    eye_left=[CX-1.34,31.38,-3.04]
    eye_right=[CX+1.34,31.38,-3.04]
    models=[perch_and_body(),head(),wing(-1),wing(1),tail(),
            eye(eye_left[0]),eye(eye_right[0])]
    offsets=[[0,0,0],head_pivot,left_pivot,right_pivot,[0,0,0],
             eye_left,eye_right]
    meshes=[add_mesh(glb,model,offset,name) for model,offset,name in zip(
        models,offsets,('perch_and_body','owl_head','left_wing','right_wing',
                        'tail','left_eye','right_eye'))]
    nodes=[
        {'name':'body','mesh':0,'children':[1,2,3,4]},
        {'name':'owl_head','mesh':1,'translation':head_pivot,'children':[5,6]},
        {'name':'left_wing','mesh':2,'translation':left_pivot},
        {'name':'right_wing','mesh':3,'translation':right_pivot},
        {'name':'tail','mesh':4},
        {'name':'left_eye','mesh':5,'translation':[eye_left[i]-head_pivot[i] for i in range(3)]},
        {'name':'right_eye','mesh':6,'translation':[eye_right[i]-head_pivot[i] for i in range(3)]},
    ]
    period=3.8
    tracks=[
        (1,'rotation',lambda t:mul(quat_y(.075*math.sin(2*math.pi*t/period)),
                                   quat_z(.038*math.sin(2*math.pi*t/period+.8)))),
        (2,'rotation',lambda t:quat_z(-.065*math.sin(2*math.pi*t/period+.4))),
        (3,'rotation',lambda t:quat_z(.065*math.sin(2*math.pi*t/period+.4))),
        (5,'scale',blink),(6,'scale',blink),
    ]
    doc={
        'asset':{'version':'2.0','generator':'Arctic Snow Owl sculpture'},
        'scene':0,'scenes':[{'nodes':[0]}],'nodes':nodes,'meshes':meshes,
        'materials':[{'name':'snowy_feathers','pbrMetallicRoughness':{
            'baseColorFactor':[1,1,1,1],'metallicFactor':.04,
            'roughnessFactor':.74},'doubleSided':True}],
        'animations':[animation_of(glb,period,76,tracks)],
    }
    glb.write(doc,os.path.join(ASSETS,'cosmetics','snow_owl.glb'))


if __name__=='__main__':
    write()
