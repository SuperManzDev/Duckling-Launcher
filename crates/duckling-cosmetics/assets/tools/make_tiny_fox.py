"""Build a warm, sculpted Tiny Fox shoulder companion.

The old Bedrock cuboids remain the fallback. The fox sits on the shoulder with
a raised face, ears, paws and a thick curled tail that reads from behind.
"""

import math
import os

import numpy as np

from make_codex_meshes import animation_of
from make_dragon_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, mul, primitive, quat_y, quat_z
from make_snow_owl import feather, polygon, tapered


DARK = (48, 35, 41)
BROWN = (104, 57, 48)
RUST = (159, 65, 48)
ORANGE = (221, 91, 45)
SUN = (255, 146, 67)
GOLD = (255, 201, 105)
CREAM = (250, 224, 174)
WHITE = (255, 246, 217)
TEAL = (58, 186, 176)
PALE = (155, 235, 213)

CX = 7.6


def cuboid(mesh, center, size, colors):
    x,y,z=center
    w,h,d=(v/2 for v in size)
    corners=[(x-w,y-h,z-d),(x+w,y-h,z-d),(x+w,y+h,z-d),(x-w,y+h,z-d),
             (x-w,y-h,z+d),(x+w,y-h,z+d),(x+w,y+h,z+d),(x-w,y+h,z+d)]
    faces=((0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2))
    for i,face in enumerate(faces):
        color=colors[i] if isinstance(colors[0],tuple) else colors
        a,b,c,d=(corners[n] for n in face)
        mesh.tri(a,b,c,color)
        mesh.tri(a,c,d,color)


def perch_and_body():
    mesh=Sculpture()
    # Dark wooden shoulder plate with a bright enamel rim.
    tapered(mesh,[(CX,23.48,.04,3.36,2.80,.55),
                  (CX,23.93,.04,3.51,2.91,.55),
                  (CX,24.24,.04,3.24,2.64,.52)],
            front=BROWN,side=DARK,back=RUST,bevel=GOLD)
    cuboid(mesh,(CX,23.58,.04),(6.76,.20,5.46),GOLD)
    tapered(mesh,[(CX,24.29,.14,1.91,1.72,.58),
                  (CX,25.12,.14,2.55,2.19,.69),
                  (CX,28.17,.16,2.59,2.27,.71),
                  (CX,29.54,.14,2.07,1.91,.61)],
            front=ORANGE,side=RUST,back=SUN,bevel=SUN)
    # The white chest and throat wrap forward rather than lying on the body.
    polygon(mesh,[(CX-1.93,28.64,-2.30),(CX-1.59,29.08,-2.33),
                  (CX+1.59,29.08,-2.33),(CX+1.93,28.64,-2.30),
                  (CX+1.62,25.17,-2.31),(CX,24.76,-2.47),
                  (CX-1.62,25.17,-2.31)],CREAM,edge=BROWN,thick=.16)
    polygon(mesh,[(CX-1.45,28.62,-2.51),(CX+1.45,28.62,-2.51),
                  (CX+1.22,25.50,-2.52),(CX,25.11,-2.61),
                  (CX-1.22,25.50,-2.52)],WHITE,edge=CREAM,thick=.11)
    # A narrow Arctic-blue collar is the only non-natural accent.
    cuboid(mesh,(CX,29.17,-1.46),(4.80,.57,1.48),
           (PALE,TEAL,TEAL,PALE,TEAL,TEAL))
    polygon(mesh,[(CX-.37,29.12,-2.44),(CX+.37,29.12,-2.44),
                  (CX+.27,28.52,-2.48),(CX,28.34,-2.57),
                  (CX-.27,28.52,-2.48)],GOLD,edge=BROWN,thick=.14)
    # Two paws and individual toes sit over the front of the perch.
    for x in (CX-1.24,CX+1.24):
        cuboid(mesh,(x,24.67,-1.94),(1.34,.73,1.38),
               (BROWN,DARK,ORANGE,BROWN,DARK,RUST))
        for dx in (-.35,0,.35):
            cuboid(mesh,(x+dx,24.43,-2.74),(.25,.24,.56),DARK)
    return mesh


def head():
    mesh=Sculpture()
    tapered(mesh,[(CX,29.22,.08,2.11,1.97,.61),
                  (CX,29.82,.08,2.79,2.47,.73),
                  (CX,32.34,.07,2.85,2.47,.73),
                  (CX,33.10,.07,2.28,2.01,.63)],
            front=SUN,side=RUST,back=ORANGE,bevel=GOLD)
    # The nape has raised fur layers, visible when the pet faces away.
    for y,width,color in ((32.72,1.79,SUN),(31.89,2.00,RUST),
                          (31.06,1.81,SUN),(30.34,1.38,GOLD)):
        polygon(mesh,[(CX-width,y,2.68),(CX,y-.66,2.75),
                      (CX+width,y,2.68),(CX,y-.25,2.83)],
                color,edge=BROWN,thick=-.14)
    # White cheeks, a tapered muzzle and a dark nose create the fox silhouette.
    for sign in (-1,1):
        x=CX+sign*1.45
        feather(mesh,[(x-sign*.22,31.05,-2.56),
                      (x+sign*1.14,30.97,-2.39),
                      (x+sign*.53,29.87,-2.79),
                      (x-sign*.44,29.76,-2.84)],
                WHITE,CREAM,edge=BROWN,thick=.49)
        polygon(mesh,[(x-sign*.70,32.38,-2.56),(x+sign*.38,32.45,-2.53),
                      (x+sign*.54,32.13,-2.61),(x-sign*.64,32.14,-2.67)],
                RUST,edge=BROWN,thick=.13)
    # Tapered cream snout, with a nose that genuinely protrudes in profile.
    snout=[(CX-1.06,30.27,-2.62),(CX+1.06,30.27,-2.62),
           (CX+.83,29.66,-2.84),(CX,29.52,-3.45),
           (CX-.83,29.66,-2.84)]
    tip=(CX,29.91,-3.85)
    for i,p in enumerate(snout):
        mesh.tri(p,snout[(i+1)%len(snout)],tip,
                 WHITE if i in (0,1,4) else CREAM)
    polygon(mesh,[(CX-.43,30.16,-3.79),(CX+.43,30.16,-3.79),
                  (CX,29.79,-3.97)],DARK,edge=BROWN,thick=.12)
    # A small white neck blaze is visible even with the head tilted.
    polygon(mesh,[(CX-1.01,29.71,-2.52),(CX,28.85,-2.68),
                  (CX+1.01,29.71,-2.52)],WHITE,edge=CREAM,thick=.11)
    return mesh


def ear(sign):
    mesh=Sculpture()
    x=CX+sign*1.99
    feather(mesh,[(x-sign*.72,32.44,-.78),
                  (x+sign*.22,34.85,-.52),
                  (x+sign*.93,32.60,-.96),
                  (x+sign*.37,32.43,-1.00)],
            SUN,RUST,edge=DARK,thick=1.28)
    feather(mesh,[(x-sign*.31,32.75,-1.02),
                  (x+sign*.19,34.15,-.80),
                  (x+sign*.48,32.80,-1.13)],
            CREAM,BROWN,edge=GOLD,thick=.12)
    return mesh


def eye(x):
    mesh=Sculpture()
    polygon(mesh,[(x-.39,31.64,-2.64),(x+.39,31.64,-2.64),
                  (x+.39,30.89,-2.70),(x-.39,30.89,-2.70)],
            DARK,edge=BROWN,thick=.11)
    cuboid(mesh,(x+.11,31.47,-2.81),(.17,.18,.10),WHITE)
    return mesh


def tail():
    """A four-ring fur loft, curled out and up behind the fox."""
    mesh=Sculpture()
    centers=[(CX+2.12,25.36,1.61),(CX+4.14,26.05,2.82),
             (CX+4.63,27.91,3.72),(CX+3.48,30.04,4.03)]
    radii=[.53,1.26,1.48,.54]
    rings=[]
    for i,(center,radius) in enumerate(zip(centers,radii)):
        center=np.asarray(center,dtype=float)
        tangent=np.asarray(centers[min(i+1,3)],dtype=float)-np.asarray(centers[max(i-1,0)],dtype=float)
        tangent/=np.linalg.norm(tangent)
        side=np.cross(tangent,[0,0,1.0])
        side/=np.linalg.norm(side)
        depth=np.cross(tangent,side)
        rings.append([center+radius*(math.cos(k*math.pi/4)*side+
                                     math.sin(k*math.pi/4)*depth) for k in range(8)])
    for j,(lower,upper) in enumerate(zip(rings,rings[1:])):
        for i in range(8):
            k=(i+1)%8
            color=(RUST if i in (2,3,4) else SUN) if j<2 else (WHITE if i in (1,2,3,4,5) else CREAM)
            mesh.tri(lower[i],upper[i],upper[k],color)
            mesh.tri(lower[i],upper[k],lower[k],color)
    for points,color,reverse in ((rings[0],BROWN,True),(rings[-1],WHITE,False)):
        center=np.asarray(points).mean(axis=0)
        for i in range(8):
            k=(i+1)%8
            a,b=(points[k],points[i]) if reverse else (points[i],points[k])
            mesh.tri(center,a,b,color)
    # Short overlapping tips break the tube silhouette into fur tufts.
    for dx,dy in ((-.46,-.10),(.36,-.22),(.02,.31)):
        feather(mesh,[(CX+3.46+dx,29.17+dy,4.10),
                      (CX+3.48+dx,30.65+dy,4.22),
                      (CX+3.01+dx,30.12+dy,4.36)],
                WHITE,CREAM,edge=GOLD,thick=.22)
    return mesh


def add_mesh(glb, model, offset, name):
    part=model.gltf()
    out=primitive(glb,part,offset,0)
    out['attributes']['NORMAL']=glb.add(part['normal'],'VEC3',5126)
    return {'name':name,'primitives':[out]}


def blink(t):
    phase=t%3.6
    distance=min(abs(phase-1.08),abs(phase-3.05))
    amount=max(.07,min(1.0,(distance-.023)/.085))
    return [1.0,amount,1.0]


def write():
    glb=Glb()
    head_pivot=[CX,30.05,.08]
    ear_l=[CX-1.99,32.65,-.75]
    ear_r=[CX+1.99,32.65,-.75]
    eye_l=[CX-1.15,31.29,-2.68]
    eye_r=[CX+1.15,31.29,-2.68]
    tail_pivot=[CX+2.12,25.36,1.61]
    models=[perch_and_body(),head(),ear(-1),ear(1),eye(eye_l[0]),
            eye(eye_r[0]),tail()]
    offsets=[[0,0,0],head_pivot,ear_l,ear_r,eye_l,eye_r,tail_pivot]
    meshes=[add_mesh(glb,model,offset,name) for model,offset,name in zip(
        models,offsets,('perch_and_body','fox_head','left_ear','right_ear',
                        'left_eye','right_eye','curled_tail'))]
    nodes=[
        {'name':'body','mesh':0,'children':[1,6]},
        {'name':'fox_head','mesh':1,'translation':head_pivot,'children':[2,3,4,5]},
        {'name':'left_ear','mesh':2,'translation':[ear_l[i]-head_pivot[i] for i in range(3)]},
        {'name':'right_ear','mesh':3,'translation':[ear_r[i]-head_pivot[i] for i in range(3)]},
        {'name':'left_eye','mesh':4,'translation':[eye_l[i]-head_pivot[i] for i in range(3)]},
        {'name':'right_eye','mesh':5,'translation':[eye_r[i]-head_pivot[i] for i in range(3)]},
        {'name':'curled_tail','mesh':6,'translation':tail_pivot},
    ]
    period=3.6
    tracks=[
        (1,'rotation',lambda t:mul(quat_y(.085*math.sin(2*math.pi*t/period)),
                                   quat_z(.034*math.sin(2*math.pi*t/period+.45)))),
        (2,'rotation',lambda t:quat_z(-.07*math.sin(4*math.pi*t/period+.42))),
        (3,'rotation',lambda t:quat_z(.07*math.sin(4*math.pi*t/period+.42))),
        (4,'scale',blink),(5,'scale',blink),
        (6,'rotation',lambda t:quat_y(.11*math.sin(4*math.pi*t/period))),
    ]
    doc={
        'asset':{'version':'2.0','generator':'Arctic Tiny Fox sculpture'},
        'scene':0,'scenes':[{'nodes':[0]}],'nodes':nodes,'meshes':meshes,
        'materials':[{'name':'painted_fur','pbrMetallicRoughness':{
            'baseColorFactor':[1,1,1,1],'metallicFactor':.03,
            'roughnessFactor':.78},'doubleSided':True}],
        'animations':[animation_of(glb,period,72,tracks)],
    }
    glb.write(doc,os.path.join(ASSETS,'cosmetics','tiny_fox.glb'))


if __name__=='__main__':
    write()
