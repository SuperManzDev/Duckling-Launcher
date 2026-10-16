"""Draw twelve original Minecraft 64x64 skins on the actual cube UV islands."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parents[1]
GALLERY = ASSETS / "gallery"
MANIFEST = ASSETS / "gallery.json"

SKINS = [
    # name, file, model, category, head, body, dark, light, accent, trim, skin/hair
    ("Dune Cartographer", "dune_cartographer.png", "classic", "adventure", "human", "#b7a17a", "#51483e", "#d8c79e", "#e8a44e", "#665644", "#a76f50"),
    ("Reef Salvager", "reef_salvager.png", "slim", "adventure", "diver", "#326a76", "#173b51", "#60a3a2", "#e5ae59", "#23495b", "#986a4b"),
    ("Lantern Golem", "lantern_golem.png", "classic", "fantasy", "lantern", "#685849", "#332f3d", "#a88b62", "#ffd56b", "#af683f", "#efc077"),
    ("Mycelium Mage", "mycelium_mage.png", "slim", "fantasy", "mushroom", "#634569", "#342b48", "#aa77ae", "#f7d6a4", "#b8484e", "#eacb9a"),
    ("CRT Hero", "crt_hero.png", "classic", "gamer", "crt", "#243c5c", "#17243e", "#3e6687", "#63ebd5", "#e3559d", "#d8e3dc"),
    ("Synth Cat", "synth_cat.png", "slim", "gamer", "cat", "#553f79", "#29283c", "#8b6dbe", "#5febdf", "#f1bb6b", "#e3cba9"),
    ("Sunset Puffin", "sunset_puffin.png", "classic", "animals", "puffin", "#252f45", "#141e33", "#e8edf0", "#ff9e4f", "#427c92", "#f1e7d4"),
    ("Copper Capybara", "copper_capybara.png", "classic", "animals", "capybara", "#916645", "#493a36", "#c99561", "#91e0c5", "#e4b37a", "#b47c53"),
    ("Void Checkmate", "void_checkmate.png", "slim", "pvp", "visor", "#302b4f", "#18172d", "#62588d", "#e4dcf5", "#aa6bf1", "#dbc3af"),
    ("Sunburst Striker", "sunburst_striker.png", "classic", "pvp", "mask", "#a55034", "#342537", "#e99347", "#f9d167", "#4a3238", "#e7b88b"),
    ("Cherry Barista", "cherry_barista.png", "slim", "casual", "beanie", "#754c58", "#342d41", "#ba7890", "#efb1b8", "#bf684d", "#b67f5c"),
    ("Mint Pixel Hoodie", "mint_pixel_hoodie.png", "classic", "casual", "hoodie", "#579f91", "#243f4b", "#8bd4bd", "#e6f6ca", "#e9ac69", "#986e52"),
]


def shade(color: str, amount: float) -> tuple[int, int, int, int]:
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    return (*[max(0, min(255, round(c * amount))) for c in rgb], 255)


def box(d: ImageDraw.ImageDraw, kind: str, base: str, dark: str, light: str, slim: bool) -> None:
    """Fill all six base faces, including top/bottom and both limb backs."""
    if kind == "head":
        faces = [(8,0,16,8),(16,0,24,8),(0,8,8,16),(8,8,16,16),
                 (16,8,24,16),(24,8,32,16)]
    elif kind == "torso":
        faces = [(20,16,28,20),(28,16,36,20),(16,20,20,32),(20,20,28,32),
                 (28,20,32,32),(32,20,40,32)]
    elif kind == "right_arm":
        x, y, w, h = 40, 16, (3 if slim else 4), 12
        faces = [(x+4,y,x+4+w,y+4),(x+4+w,y,x+4+w*2,y+4),
                 (x,y+4,x+4,y+16),(x+4,y+4,x+4+w,y+16),
                 (x+4+w,y+4,x+8+w,y+16),(x+8+w,y+4,x+8+2*w,y+16)]
    elif kind == "left_arm":
        x, y, w = 32, 48, (3 if slim else 4)
        faces = [(x+4,y,x+4+w,y+4),(x+4+w,y,x+4+w*2,y+4),
                 (x,y+4,x+4,y+16),(x+4,y+4,x+4+w,y+16),
                 (x+4+w,y+4,x+8+w,y+16),(x+8+w,y+4,x+8+2*w,y+16)]
    elif kind == "right_leg":
        faces = [(4,16,8,20),(8,16,12,20),(0,20,4,32),(4,20,8,32),
                 (8,20,12,32),(12,20,16,32)]
    else:
        faces = [(20,48,24,52),(24,48,28,52),(16,52,20,64),(20,52,24,64),
                 (24,52,28,64),(28,52,32,64)]
    colors = (light, dark, dark, base, dark, shade(base, .77))
    for (x0, y0, x1, y1), color in zip(faces, colors):
        d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=color)


def face(d: ImageDraw.ImageDraw, head: str, skin: str, dark: str, light: str,
         accent: str, trim: str) -> None:
    """One strong face motif at real eight-pixel resolution, plus side/back cues."""
    r = lambda xy, c: d.rectangle(xy, fill=c)
    if head in {"human", "beanie", "hoodie", "diver", "visor", "mask"}:
        r((8,8,15,15), skin)
        r((0,8,7,15), shade(skin,.82)); r((16,8,23,15), shade(skin,.88))
        r((24,8,31,15), shade(skin,.78))
        r((8,8,15,10), dark); r((8,8,9,13), dark); r((14,8,15,12), dark)
        for x in (10, 13): d.point((x, 12), fill="#1d2731")
        r((11,14,12,14), shade(skin,.70))
        if head == "human":
            r((8,8,15,9), trim); r((9,10,13,10), trim)
            r((0,9,7,9), trim); r((24,9,31,9), trim)
        elif head == "beanie":
            r((8,8,15,10), accent); r((8,10,15,10), light)
            r((0,8,7,10), accent); r((24,8,31,10), accent)
            r((10,7,13,8), light)
        elif head == "hoodie":
            r((8,8,15,9), dark); r((8,8,9,15), dark); r((14,8,15,15), dark)
            r((0,8,7,10), dark); r((24,8,31,10), dark)
            r((40,8,47,9), light); r((40,9,40,15), light); r((47,9,47,15), light)
        elif head == "diver":
            r((8,8,15,9), accent); r((8,10,15,10), light)
            r((9,11,14,14), dark); r((10,11,13,13), "#77d5cf")
            r((9,11,9,14), accent); r((14,11,14,14), accent)
            r((0,9,7,11), accent); r((16,9,23,11), accent)
        elif head == "visor":
            r((8,10,15,13), dark); r((9,11,14,12), accent)
            r((10,11,13,11), light); r((0,10,7,12), accent)
        elif head == "mask":
            r((8,9,15,15), accent); r((8,10,15,13), dark)
            d.point((10,11), fill=light); d.point((13,11), fill=light)
            r((11,14,12,15), light)
    elif head == "lantern":
        r((8,8,15,15), trim); r((9,9,14,14), dark)
        r((10,10,11,12), light); r((13,10,13,12), light)
        r((10,14,13,14), accent)
        r((8,8,15,8), accent); r((0,8,7,9), trim); r((16,8,23,9), trim)
        r((24,8,31,15), trim); r((25,10,30,13), accent)
    elif head == "mushroom":
        r((8,8,15,15), skin); r((8,8,15,10), accent)
        r((9,8,10,9), light); d.point((13,9), fill=light)
        r((0,8,7,10), accent); r((16,8,23,10), accent)
        r((24,8,31,10), accent); r((24,11,31,15), trim)
        for x in (10,13): d.point((x,12), fill=dark)
        r((11,14,12,14), shade(skin,.72))
        r((40,8,47,10), accent); r((40,8,41,11), accent); r((46,8,47,11), accent)
        for x in (42,45): d.point((x,9), fill=light)
    elif head == "crt":
        r((8,8,15,15), dark); r((9,9,14,13), light)
        r((10,10,10,11), "#17243e"); r((13,10,13,11), "#17243e")
        r((11,12,12,12), accent); r((9,14,14,14), trim)
        r((0,8,7,15), trim); r((16,8,23,15), trim); r((24,8,31,15), dark)
        r((24,10,31,12), accent)
        r((40,8,47,8), accent); r((40,8,40,15), accent); r((47,8,47,15), accent)
    elif head == "cat":
        r((8,8,15,15), skin); r((8,8,15,9), dark)
        r((9,10,10,11), light); r((13,10,14,11), light)
        d.point((10,11), fill=dark); d.point((13,11), fill=dark)
        d.point((11,13), fill=accent); r((10,14,13,14), trim)
        r((0,8,7,15), shade(skin,.7)); r((16,8,23,15), shade(skin,.75))
        r((24,8,31,15), skin)
        r((40,8,41,10), dark); r((46,8,47,10), dark)
        d.point((41,9), fill=accent); d.point((46,9), fill=accent)
    elif head == "puffin":
        r((8,8,15,15), dark); r((10,10,13,15), skin)
        d.point((9,11), fill=light); d.point((14,11), fill=light)
        r((11,12,12,13), accent); r((10,13,13,13), shade(accent,.78))
        r((0,8,7,15), dark); r((16,8,23,15), dark); r((24,8,31,15), dark)
    elif head == "capybara":
        r((8,8,15,15), skin); r((8,8,15,9), trim)
        d.point((10,11), fill=dark); d.point((13,11), fill=dark)
        r((10,13,13,14), trim); r((11,13,12,13), dark)
        r((0,8,7,15), shade(skin,.8)); r((16,8,23,15), shade(skin,.8))
        r((24,8,31,15), skin)
        r((40,8,41,9), dark); r((46,8,47,9), dark)


def make_skin(spec: tuple[str, ...]) -> Image.Image:
    _, _, model, _, head, body, dark, light, accent, trim, skin = spec
    slim = model == "slim"
    im = Image.new("RGBA", (64, 64))
    d = ImageDraw.Draw(im)
    for part, color in (("head", skin),("torso", body),("right_arm", body),
                        ("left_arm", body),("right_leg", dark),("left_leg", dark)):
        box(d, part, color, dark, light, slim)
    # Torso front: raised shoulder panels, central emblem, visible belt.
    d.rectangle((20,20,27,21), fill=light)
    d.rectangle((20,29,27,30), fill=trim)
    d.rectangle((23,29,24,30), fill=accent)
    d.rectangle((32,29,39,30), fill=trim)
    for x in (21,26): d.line((x,22,x,27), fill=shade(body,.82))
    d.rectangle((23,23,24,25), fill=accent)
    d.point((23,23), fill=light)
    d.rectangle((22,27,25,27), fill=light)
    # Back icon and restrained sleeve/pant highlights.
    d.rectangle((35,23,36,26), fill=accent)
    d.rectangle((33,22,38,22), fill=light)
    for ax in (44,36):
        ay = 20 if ax == 44 else 52
        width = 3 if slim else 4
        d.rectangle((ax,ay+1,ax+width-1,ay+2), fill=light)
        d.rectangle((ax,ay+9,ax+width-1,ay+9), fill=trim)
    for lx,ly in ((4,20),(20,52)):
        d.rectangle((lx,ly+7,lx+3,ly+8), fill=shade(dark,1.27))
        d.rectangle((lx,ly+10,lx+3,ly+11), fill=trim)
    face(d, head, skin, dark, light, accent, trim)
    # Distinct costume signatures beyond palette changes.
    if head == "human":
        d.line((20,22,27,28), fill=accent, width=2)
        d.rectangle((23,23,25,25), fill=light)  # map pouch clasp
    elif head == "diver":
        d.rectangle((21,22,26,27), fill=dark)
        d.rectangle((22,23,25,26), fill=accent)
        d.rectangle((23,23,24,24), fill=light)
    elif head == "lantern":
        d.rectangle((22,23,25,27), fill=trim)
        d.rectangle((23,24,24,26), fill=accent)
        d.point((23,24), fill=light)
    elif head == "mushroom":
        d.rectangle((21,22,26,27), fill=trim)
        d.point((22,24), fill=light); d.point((25,26), fill=light)
        d.rectangle((23,21,24,21), fill=accent)
    elif head == "crt":
        d.rectangle((21,22,26,27), fill=dark)
        for x,y in ((22,23),(25,23),(23,25),(24,25)):
            d.rectangle((x,y,x,y), fill=accent if x%2 else light)
    elif head == "cat":
        d.rectangle((20,23,27,24), fill=accent)
        d.rectangle((22,25,25,26), fill=light)
    elif head == "puffin":
        d.rectangle((22,21,25,28), fill=skin)
        d.rectangle((22,24,25,25), fill=light)
        d.rectangle((4,29,7,31), fill=accent);d.rectangle((20,61,23,63), fill=accent)
    elif head == "capybara":
        d.rectangle((20,21,27,23), fill=accent)
        d.rectangle((23,22,24,23), fill=light)
    elif head == "visor":
        d.polygon([(21,22),(26,22),(26,25),(23,27),(21,25)], fill=accent)
        d.rectangle((23,23,24,24), fill=light)
    elif head == "mask":
        d.polygon([(21,22),(24,22),(27,25),(24,28),(21,25)], fill=accent)
        d.rectangle((23,24,24,25), fill=light)
    elif head == "beanie":
        d.rectangle((21,23,26,28), fill=trim)
        d.rectangle((22,24,25,27), fill=light)
        d.point((23,25), fill=accent)
    elif head == "hoodie":
        d.rectangle((22,22,25,26), fill=dark)
        d.rectangle((23,23,24,25), fill=light)
        d.rectangle((40,9,40,15), fill=light)
    # Opaque standard model islands; only intentional outer-layer accents are transparent.
    return im


def main() -> None:
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_files = {item["file"] for item in existing}
    for spec in SKINS:
        name, filename, model, category, *_ = spec
        make_skin(spec).save(GALLERY / filename)
        if filename not in existing_files:
            existing.append({"file": filename, "name": name, "model": model, "category": category})
    # Preserve the compact one-entry-per-line manifest convention.
    MANIFEST.write_text("[\n" + ",\n".join("  " + json.dumps(item, ensure_ascii=False) for item in existing) + "\n]\n", encoding="utf-8")
    print(f"Wrote {len(SKINS)} skin PNGs; gallery now has {len(existing)} entries")


if __name__ == "__main__":
    main()
