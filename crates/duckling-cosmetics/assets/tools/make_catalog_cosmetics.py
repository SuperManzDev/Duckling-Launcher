"""Build five original, dimensional, non-wing Minecraft cosmetics."""

from __future__ import annotations

import json
from pathlib import Path

from make_frost_wings import Sculpture
from make_mesh_pilots import ASSETS, Glb, primitive

NIGHT=(28,35,47); INK=(39,43,51); BROWN=(94,59,48); LEATHER=(150,94,57)
COPPER=(200,125,70); GOLD=(247,189,91); CREAM=(255,229,169)
TEAL=(44,129,134); MINT=(109,222,191); WHITE=(229,249,234)
HONEY=(248,174,53); SUN=(255,212,91); ROSE=(203,80,67)
PLUM=(73,48,95); VIOLET=(153,103,208); ICE=(122,225,242)


def cuboid(m: Sculpture, center, size, front, side=None, top=None, back=None) -> None:
    x,y,z=center; sx,sy,sz=(v/2 for v in size)
    p=[(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
       (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)]
    sides=((0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2))
    colors=(front,back or front,side or front,side or front,top or front,side or front)
    for face,color in zip(sides,colors):
        a,b,c,d=(p[i] for i in face);m.tri(a,b,c,color);m.tri(a,c,d,color)


def plate(m: Sculpture, points, front, edge, thick=.22) -> None:
    """Closed raised polygon in the XY plane; negative Z faces the player front."""
    z=points[0][2]
    c=(sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points),z-.01)
    for i,p in enumerate(points):
        q=points[(i+1)%len(points)]
        m.tri(c,p,q,front)
        pb=(p[0],p[1],p[2]+thick);qb=(q[0],q[1],q[2]+thick)
        m.tri(p,pb,qb,edge);m.tri(p,qb,q,edge)


def diamond(m: Sculpture, x,y,z,rx,ry,front,side) -> None:
    plate(m,[(x,y+ry,z),(x+rx,y,z),(x,y-ry,z),(x-rx,y,z)],front,side,.33)


def brass_quiver() -> Sculpture:
    m=Sculpture()
    # Thick diagonal strap over the back and an offset, closed arrow case.
    plate(m,[(-3.4,23.9,2.58),(-2.0,24.2,2.58),(3.1,12.4,2.58),
             (1.8,12.1,2.58)],LEATHER,BROWN,.35)
    cuboid(m,(2.0,18.1,5.3),(6.0,12.2,4.2),BROWN,INK,LEATHER,LEATHER)
    cuboid(m,(2.0,18.3,7.53),(5.2,10.6,.44),LEATHER,BROWN,COPPER)
    cuboid(m,(2.0,23.9,5.3),(6.4,1.0,4.7),COPPER,BROWN,GOLD)
    cuboid(m,(2.0,12.2,5.3),(6.4,1.0,4.7),BROWN,INK,COPPER)
    # Long central compass-brass ornament reads from normal play distance.
    diamond(m,2.0,18.4,7.78,1.55,2.25,GOLD,BROWN)
    diamond(m,2.0,18.4,7.85,.48,.9,CREAM,COPPER)
    for x, color in ((-.1,MINT),(1.65,ROSE),(3.8,ICE)):
        cuboid(m,(x,26.1,5.2),(0.42,7.5,.45),BROWN,INK,CREAM)
        plate(m,[(x,30.2,5.0),(x+1.05,28.6,5.0),(x,29.0,5.0),
                 (x-1.05,28.6,5.0)],color,INK,.28)
        cuboid(m,(x,24.3,5.2),(.75,.55,.75),GOLD,COPPER)
    return m


def honeybee_buddy() -> Sculpture:
    m=Sculpture();cx=7.2
    # The platform is wide enough to meet the player's shoulder in profile.
    cuboid(m,(cx,23.9,0),(6.8,.65,5.9),GOLD,BROWN,CREAM)
    cuboid(m,(cx,24.28,0),(6.2,.22,5.3),HONEY,COPPER,GOLD)
    cuboid(m,(cx,27.3,.15),(4.9,4.1,4.25),HONEY,BROWN,SUN,SUN)
    for z in (-.45,1.12):
        cuboid(m,(cx,27.3,z),(5.02,4.17,.46),INK,NIGHT,INK)
    # Lift the front face again so eyes and smile stay visible over stripes.
    cuboid(m,(cx,28.5,-2.06),(4.2,1.95,.24),SUN,HONEY)
    for x in (cx-1.02,cx+1.02):
        cuboid(m,(x,28.65,-2.29),(.55,.75,.19),NIGHT,INK)
        cuboid(m,(x-.14,28.88,-2.4),(.17,.2,.08),WHITE)
    cuboid(m,(cx,27.45,-2.33),(.67,.37,.18),BROWN)
    # Short lateral wings read as a bee from the front, not as tall head horns.
    for sign in (-1,1):
        x=cx+sign*3.15
        cuboid(m,(x,29.6,1.18),(2.6,1.4,2.15),WHITE,ICE,MINT)
        cuboid(m,(x+sign*.42,29.9,1.13),(1.45,.4,2.25),MINT,ICE,WHITE)
        cuboid(m,(cx+sign*2.8,25.35,-.9),(1.2,.62,1.25),COPPER,BROWN)
        cuboid(m,(cx+sign*.9,30.15,-1.55),(.3,1.25,.32),INK,NIGHT)
    cuboid(m,(cx,25.3,2.65),(.9,1.45,1.25),INK,BROWN)
    return m


def fox_festival_mask() -> Sculpture:
    m=Sculpture()
    # Face plate follows the head rather than hovering in front of it.
    plate(m,[(-3.25,30.15,-4.83),(3.25,30.15,-4.83),(3.55,27.0,-4.83),
             (2.0,25.1,-4.83),(0,24.6,-4.83),(-2.0,25.1,-4.83),
             (-3.55,27.0,-4.83)],CREAM,BROWN,.38)
    plate(m,[(-3.05,29.95,-5.13),(3.05,29.95,-5.13),(3.18,28.0,-5.13),
             (1.7,27.0,-5.13),(0,27.7,-5.13),(-1.7,27.0,-5.13),
             (-3.18,28.0,-5.13)],ROSE,INK,.16)
    for sign in (-1,1):
        x=sign*2.55
        plate(m,[(x-sign*.9,30.0,-4.75),(x+sign*.9,30.0,-4.75),
                 (x+sign*.2,34.1,-4.75)],ROSE,BROWN,.56)
        plate(m,[(x-sign*.42,30.7,-5.14),(x+sign*.47,30.7,-5.14),
                 (x+sign*.17,32.7,-5.14)],CREAM,ROSE,.12)
        plate(m,[(x-sign*1.13,28.8,-5.36),(x+sign*.88,28.8,-5.36),
                 (x+sign*.3,27.85,-5.36)],INK,ROSE,.12)
        diamond(m,x,27.2,-5.38,.72,.55,GOLD,ROSE)
    diamond(m,0,26.0,-5.4,.56,.55,INK,BROWN)
    cuboid(m,(0,29.4,-5.45),(.6,.45,.27),GOLD,COPPER)
    return m


def prism_bracers() -> tuple[Sculpture,Sculpture]:
    out=[]
    for sign in (-1,1):
        m=Sculpture();cx=sign*6.0
        # Cuffs wrap around the arm, so the side views have actual thickness.
        cuboid(m,(cx,15.0,0),(4.8,5.9,5.15),PLUM,NIGHT,VIOLET,PLUM)
        cuboid(m,(cx,17.78,0),(5.1,.78,5.35),VIOLET,PLUM,ICE)
        cuboid(m,(cx,12.35,0),(4.9,.78,5.35),VIOLET,NIGHT,MINT)
        cuboid(m,(cx,15.1,-2.72),(3.6,3.6,.5),VIOLET,PLUM,ICE)
        diamond(m,cx,15.1,-3.07,1.3,1.48,ICE,PLUM)
        diamond(m,cx,15.1,-3.17,.46,.52,WHITE,VIOLET)
        for y in (13.1,17.05):
            cuboid(m,(cx,y,2.75),(3.3,.34,.35),MINT,VIOLET)
        out.append(m)
    return out[0],out[1]


def alchemist_bandolier() -> Sculpture:
    m=Sculpture()
    # Broad diagonal band and side wrap keep a coherent 3D silhouette.
    plate(m,[(-3.6,23.9,-2.44),(-2.0,24.0,-2.44),(3.45,12.4,-2.44),
             (1.65,12.2,-2.44)],LEATHER,BROWN,.42)
    plate(m,[(3.6,23.9,2.43),(2.0,24.0,2.43),(-3.45,12.4,2.43),
             (-1.65,12.2,2.43)],BROWN,INK,.38)
    cuboid(m,(0,14.05,-2.55),(8.5,1.1,.9),BROWN,INK,GOLD)
    diamond(m,2.6,14.05,-3.12,.77,.64,GOLD,LEATHER)
    for x,y,color in ((-1.8,20.8,TEAL),(.1,17.6,ROSE),(2.0,15.5,VIOLET)):
        cuboid(m,(x,y,-3.1),(1.65,2.1,1.3),color,INK,WHITE)
        cuboid(m,(x,y+1.22,-3.1),(1.18,.53,1.1),GOLD,COPPER,CREAM)
        cuboid(m,(x,y-.68,-3.82),(1.0,.32,.12),WHITE,color)
    for x,z in ((-3.9,-.15),(3.9,.2)):
        cuboid(m,(x,20.5,z),(1.1,2.2,4.8),LEATHER,BROWN)
    return m


def write_mesh(name: str, nodes: list[tuple[str,Sculpture]]) -> None:
    glb=Glb(); meshes=[]; scene_nodes=[]
    for bone,model in nodes:
        part=model.gltf();prim=primitive(glb,part,[0,0,0],0)
        prim["attributes"]["NORMAL"]=glb.add(part["normal"],"VEC3",5126)
        meshes.append({"name":name+"_"+bone,"primitives":[prim]})
        scene_nodes.append({"name":bone,"mesh":len(meshes)-1})
    doc={"asset":{"version":"2.0","generator":"Arctic catalog cosmetics"},
         "scene":0,"scenes":[{"nodes":list(range(len(scene_nodes)))}],
         "nodes":scene_nodes,"meshes":meshes,
         "materials":[{"name":"faceted voxel enamel","pbrMetallicRoughness":{
             "baseColorFactor":[1,1,1,1],"metallicFactor":.12,"roughnessFactor":.72},
             "doubleSided":True}]}
    glb.write(doc,str(Path(ASSETS)/"cosmetics"/(name+".glb")))


def main() -> None:
    designs=[("brass_quiver","Brass Quiver","back",[("body",brass_quiver())]),
             ("honeybee_buddy","Honeybee Buddy","shoulders",[("body",honeybee_buddy())]),
             ("fox_festival_mask","Fox Festival Mask","face",[("head",fox_festival_mask())]),
             ("prism_bracers","Prism Bracers","arms",list(zip(("rightArm","leftArm"),prism_bracers()))),
             ("alchemist_bandolier","Alchemist Bandolier","body",[("body",alchemist_bandolier())])]
    path=Path(ASSETS)/"cosmetics.json"
    entries=json.loads(path.read_text(encoding="utf-8")); ids={item["id"] for item in entries}
    for item_id,name,slot,nodes in designs:
        write_mesh(item_id,nodes)
        if item_id not in ids: entries.append({"id":item_id,"name":name,"slot":slot})
    path.write_text("[\n"+",\n".join("  "+json.dumps(item,ensure_ascii=False) for item in entries)+"\n]\n",encoding="utf-8")
    print(f"Wrote {len(designs)} sculpted GLBs; cosmetics now has {len(entries)} entries")


if __name__ == "__main__":
    main()
