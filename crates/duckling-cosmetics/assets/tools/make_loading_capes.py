"""Draw three original animated 'Loading...' capes and matching elytra art.

Each 512x256 frame uses Minecraft's cape/elytra UV islands; 32 frames at
16 fps make a two-second loop. The last frame matches the first for a clean
seam. Single-frame stills support the per-cape Animate toggle.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1]
CAPES = ASSETS / "capes"
CATALOG = ASSETS / "catalog.json"
REVIEW = Path(__file__).resolve().parents[4] / "docs/requests/cape-art-pack/loading-capes"
FRAME_W, FRAME_H, FRAMES, FPS, SCALE = 512, 256, 32, 16, 8

STYLES = {
    "loading_circle": {
        "name": "Loading Circle", "base": "#171c23", "shadow": "#10151b",
        "border": "#49545f", "dim": "#66717b", "mid": "#9da7b0",
        "bright": "#d7dce0", "white": "#f6f7f8", "accent": "#e4e8ea",
    },
    "loading_text": {
        "name": "Loading Text", "base": "#211b31", "shadow": "#161426",
        "border": "#654b7e", "dim": "#665778", "mid": "#ba84ca",
        "bright": "#f0b9fa", "white": "#fff2ff", "accent": "#e782c8",
    },
    "loading_both": {
        "name": "Loading Combo", "base": "#162638", "shadow": "#0c1729",
        "border": "#576b80", "dim": "#756250", "mid": "#d69b52",
        "bright": "#ffd17b", "white": "#fff2d1", "accent": "#70dce4",
    },
}

# A deliberately small, readable Minecraft-scale pixel font. Dots get half
# letter spacing so LOADING... fits comfortably across the 80-pixel cape back.
GLYPHS = {
    "L": ("100", "100", "100", "100", "111"),
    "O": ("111", "101", "101", "101", "111"),
    "A": ("111", "101", "111", "101", "101"),
    "D": ("110", "101", "101", "101", "110"),
    "I": ("111", "010", "010", "010", "111"),
    "N": ("101", "111", "111", "111", "101"),
    "G": ("111", "100", "101", "101", "111"),
    ".": ("0", "0", "0", "0", "1"),
}


def text_pixels(draw: ImageDraw.ImageDraw, style: dict, y: int, phase: float, still: bool) -> None:
    letters = "LOADING..."
    scale = 2
    advances = [(4 if c != "." else 2) * scale for c in letters]
    x = (80 - sum(advances) + scale) // 2
    sweep = -12 + phase * 104
    dot_on = 3 if still else int(phase * 4) % 4
    for index, (char, advance) in enumerate(zip(letters, advances)):
        for row, bits in enumerate(GLYPHS[char]):
            for col, bit in enumerate(bits):
                if bit != "1":
                    continue
                px = x + col * scale
                if char == ".":
                    active = index - 7 < dot_on
                    color = style["bright"] if active else style["dim"]
                elif still:
                    color = style["white"]
                else:
                    distance = abs(px - sweep)
                    color = style["white"] if distance < 6 else (style["bright"] if distance < 13 else style["mid"])
                draw.rectangle((px, y + row * scale, px + scale - 1,
                                y + (row + 1) * scale - 1), fill=color)
        x += advance


def spinner(draw: ImageDraw.ImageDraw, style: dict, cx: int, cy: int,
            radius: int, phase: float, still: bool) -> None:
    # Twelve separated white-to-gray dots: the classic loading indicator.
    # The colors remain neutral even on the warm combined cape.
    head = 0.0 if still else phase * math.tau
    colors = ("#f6f7f8", "#e8eaec", "#d5d9dc", "#c1c7cc",
              "#adb5bc", "#98a3ac", "#85919b", "#73818b",
              "#62717d", "#53636f", "#465661", "#3d4b56")
    dot_radius = 3 if radius >= 22 else 2
    for i, color in enumerate(colors):
        angle = head - i * math.tau / 12 - math.pi / 2
        x=round(cx+math.cos(angle)*radius)
        y=round(cy+math.sin(angle)*radius)
        draw.ellipse((x-dot_radius,y-dot_radius,x+dot_radius,y+dot_radius),fill=color)


def panel(kind: str, size: tuple[int,int], frame: int, still=False, wing=False,
          inner=False) -> Image.Image:
    width,height=size
    style=STYLES[kind]
    im=Image.new("RGBA", size, style["shadow"])
    d=ImageDraw.Draw(im)
    d.rectangle((2,2,width-3,height-3),fill=style["base"],outline=style["border"],width=2)
    # Corner hardware stays away from the centered sign; no painterly noise.
    for xsign in (0,1):
        x=4 if xsign==0 else width-5
        d.line((x,7,x,15),fill=style["mid"],width=1)
        d.line((x-3 if xsign else x,7,x if xsign else x+3,7),fill=style["mid"],width=1)
        d.line((x,height-8,x,height-15),fill=style["mid"],width=1)
    phase=frame/(FRAMES-1)
    if kind=="loading_circle":
        spinner(d,style,width//2,height//2,24 if not wing else 23,phase,still)
    elif kind=="loading_text":
        text_pixels(d,style,height//2-5,phase,still)
    else:
        spinner(d,style,width//2,height//2-(22 if not wing else 28),19,phase,still)
        text_pixels(d,style,height//2+(16 if not wing else 11),phase,still)
    if inner:
        # Inner elytra face is deliberately darker but has its own readable art.
        overlay=Image.new("RGBA",size,(6,12,25,55))
        im=Image.alpha_composite(im,overlay)
        im.putalpha(255)
    return im


def paste_box(atlas: Image.Image, box: tuple[int,int,int,int], art: Image.Image) -> None:
    x,y,w,h=box
    assert art.size==(w,h)
    atlas.paste(art,(x,y))


def frame(kind: str, index: int, still=False) -> Image.Image:
    style=STYLES[kind]
    atlas=Image.new("RGBA",(FRAME_W,FRAME_H),(0,0,0,0))
    back=panel(kind,(80,128),index,still)
    paste_box(atlas,(8,8,80,128),back)
    # The inside is cloth, with a small matching seal; it never mirrors the
    # full back graphic through the player.
    inside=Image.new("RGBA",(80,128),style["shadow"])
    di=ImageDraw.Draw(inside)
    di.rectangle((3,3,76,124),outline=style["border"],width=2)
    di.rectangle((33,58,46,71),outline=style["mid"],width=2)
    paste_box(atlas,(96,8,80,128),inside)
    for rect,color in [((0,8,8,128),style["border"]),((88,8,8,128),style["border"]),
                       ((8,0,80,8),style["mid"]),((88,0,80,8),style["shadow"])]:
        paste_box(atlas,rect,Image.new("RGBA",(rect[2],rect[3]),color))
    outer=panel(kind,(80,160),index,still,wing=True)
    inner=panel(kind,(80,160),index,still,wing=True,inner=True)
    paste_box(atlas,(288,16,80,160),outer)
    paste_box(atlas,(192,16,80,160),inner.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
    for rect,color in [((176,16,16,160),style["border"]),((272,16,16,160),style["border"]),
                       ((192,0,80,16),style["mid"]),((272,0,80,16),style["shadow"])]:
        paste_box(atlas,rect,Image.new("RGBA",(rect[2],rect[3]),color))
    return atlas


def review_assets() -> None:
    REVIEW.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",18)
    stills=[]; animation=[]
    for kind,style in STYLES.items():
        still=frame(kind,0,True).crop((8,8,88,136)).resize((240,384),Image.Resampling.NEAREST)
        stills.append(still)
    for t in range(FRAMES):
        canvas=Image.new("RGB",(3*260,450),"#0d1725")
        d=ImageDraw.Draw(canvas)
        for col,(kind,style) in enumerate(STYLES.items()):
            im=frame(kind,t if t<FRAMES-1 else 0).crop((8,8,88,136)).resize((240,384),Image.Resampling.NEAREST)
            canvas.paste(im,(col*260+10,40))
            d.text((col*260+12,10),style["name"],font=font,fill="#edf6ff")
        animation.append(canvas)
    static=Image.new("RGB",(780,450),"#0d1725")
    draw=ImageDraw.Draw(static)
    for i,((kind,style),im) in enumerate(zip(STYLES.items(),stills)):
        static.paste(im,(i*260+10,40))
        draw.text((i*260+12,10),style["name"],font=font,fill="#edf6ff")
    static.save(REVIEW/"still-review.png",optimize=True)
    animation[0].save(REVIEW/"animated-review.gif",save_all=True,
                      append_images=animation[1:],duration=round(1000/FPS),loop=0,optimize=False)
    sample=Image.new("RGB",(780,450*4),"#0d1725")
    for row,index in enumerate((0,8,16,24)):
        sample.paste(animation[index],(0,row*450))
    sample.save(REVIEW/"motion-frames.png",optimize=True)
    wings=Image.new("RGB",(780,1020),"#0d1725")
    wd=ImageDraw.Draw(wings)
    for col,(kind,style) in enumerate(STYLES.items()):
        atlas=frame(kind,0,True)
        for row,(label,box) in enumerate((("Cape back",(8,8,88,136)),
                                          ("Elytra outer",(288,16,368,176)),
                                          ("Elytra inner",(192,16,272,176)))):
            y=(0,300,650)[row]
            wd.text((col*260+12,y+5),f"{style['name']} · {label}",font=font,fill="#edf6ff")
            part=atlas.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2),Image.Resampling.NEAREST)
            wings.paste(part,(col*260+48,y+32))
    wings.save(REVIEW/"elytra-review.png",optimize=True)
    (REVIEW/"index.html").write_text("""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loading... capes · Arctic</title><style>
body{margin:0;background:#0b1321;color:#f0f7ff;font:16px/1.5 system-ui}
main{max-width:900px;margin:auto;padding:28px 20px 60px}h1{margin:0 0 8px}
p{color:#b8c8dc}img{max-width:100%;height:auto;border:1px solid #344864;border-radius:8px}
a{color:#78dce9}.card{background:#17263b;border:1px solid #30445d;border-radius:12px;padding:16px;margin:16px 0}
</style><main><h1>Loading... capes</h1><p>Three original Minecraft cape designs. The animation loops every two seconds at 16 fps; each has a still fallback for the Animate toggle. Every frame includes matching elytra art.</p>
<div class="card"><h2>Animated</h2><img src="animated-review.gif" alt="Three animated Loading capes"></div>
<div class="card"><h2>Still fallbacks</h2><img src="still-review.png" alt="Three still Loading capes"></div>
<div class="card"><h2>Matching elytra art</h2><img src="elytra-review.png" alt="Cape backs and both elytra faces"></div>
<p><a href="../../content-catalog/index.html">Return to full Arctic catalog</a></p></main></html>""",encoding="utf-8")


def main() -> None:
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    known={item["id"]:item for item in catalog}
    for kind,style in STYLES.items():
        strip=Image.new("RGBA",(FRAME_W,FRAME_H*FRAMES))
        for i in range(FRAMES):
            strip.paste(frame(kind,i if i<FRAMES-1 else 0),(0,i*FRAME_H))
        path=CAPES/f"{kind}.png"
        strip.save(path,optimize=True)
        frame(kind,0,True).save(CAPES/f"{kind}-still.png",optimize=True)
        assert path.stat().st_size<2*1024*1024,path
        if kind not in known:
            catalog.append({"id":kind,"name":style["name"],"free":True,"fps":FPS})
        else:
            known[kind]["name"]=style["name"]
        print(kind,strip.size,path.stat().st_size)
    CATALOG.write_text("[\n"+",\n".join("  "+json.dumps(item,ensure_ascii=False) for item in catalog)+"\n]\n",encoding="utf-8")
    review_assets()
    print(f"Wrote {len(STYLES)} capes; catalog has {len(catalog)} entries")


if __name__=="__main__":
    main()
