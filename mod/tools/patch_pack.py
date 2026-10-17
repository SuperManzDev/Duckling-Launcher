import struct
import lzma
import json
import hashlib
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 1. Extract 256x256 duck icon from target ico
ico_path = Path("target/release/build/duckling-app-01d85159e910d27e/out/duckling.ico")
ico_img = Image.open(ico_path)
ico_img.size = (256, 256)
ico_img.load()
duck_icon_bytes = io.BytesIO()
ico_img.save(duck_icon_bytes, format="PNG")
duck_icon_png = duck_icon_bytes.getvalue()

# Save to mod source assets as well
Path("mod/core/src/main/resources/assets/arctic/icon.png").write_bytes(duck_icon_png)

# 2. Generate wordmark 1..8
sizes = [
    (88, 18), (175, 37), (263, 55), (351, 74),
    (438, 92), (526, 111), (613, 129), (701, 147)
]
wordmark_pngs = {}
for idx, (w, h) in enumerate(sizes, 1):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = h
    while font_size > 5:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
        bbox = draw.textbbox((0, 0), "DUCKLING", font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if tw <= w * 0.95 and th <= h * 0.85:
            break
        font_size -= 1
    tx = (w - tw) // 2 - bbox[0]
    ty = (h - th) // 2 - bbox[1]
    draw.text((tx, ty), "DUCKLING", font=font, fill=(255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    wordmark_pngs[idx] = data
    Path(f"mod/core/src/main/resources/assets/arctic/wordmark-{idx}.png").write_bytes(data)

print("Wordmark and icon saved to mod/core/src/main/resources/assets/arctic/")

# 3. Patch classes
def patch_class(data, replacements, is_arctic_button=False):
    magic, minor, major, cp_count = struct.unpack(">IHHH", data[:10])
    if magic != 0xCAFEBABE:
        return data, False
    pos = 10
    idx = 1
    new_data = bytearray(data[:10])
    modified = False
    while idx < cp_count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            length = struct.unpack(">H", data[pos:pos+2])[0]
            pos += 2
            val = data[pos:pos+length]
            pos += length
            new_val = val
            for src, dst in replacements.items():
                if src in new_val:
                    new_val = new_val.replace(src, dst)
                    modified = True
            if is_arctic_button and val == b"Arctic":
                new_val = b"Duckling"
                modified = True
            new_data.append(1)
            new_data.extend(struct.pack(">H", len(new_val)))
            new_data.extend(new_val)
            idx += 1
        elif tag in (3, 4):
            new_data.append(tag)
            new_data.extend(data[pos:pos+4])
            pos += 4
            idx += 1
        elif tag in (5, 6):
            new_data.append(tag)
            new_data.extend(data[pos:pos+8])
            pos += 8
            idx += 2
        elif tag in (7, 8, 16, 19, 20):
            new_data.append(tag)
            new_data.extend(data[pos:pos+2])
            pos += 2
            idx += 1
        elif tag in (9, 10, 11, 12, 17, 18):
            new_data.append(tag)
            new_data.extend(data[pos:pos+4])
            pos += 4
            idx += 1
        elif tag == 15:
            new_data.append(tag)
            new_data.extend(data[pos:pos+3])
            pos += 3
            idx += 1
        else:
            raise ValueError(f"Unknown tag {tag} at pos {pos}")
    new_data.extend(data[pos:])
    return bytes(new_data), modified

# 4. Unpack arctic-client.pack, patch, and repack
pack_path = Path("mod/dist/arctic-client.pack")
raw = lzma.decompress(pack_path.read_bytes())
magic = b"ARCTICPACK1\n"
rest = raw[len(magic):]
idx_len = struct.unpack("<I", rest[:4])[0]
index = json.loads(rest[4:4+idx_len].decode("utf-8"))
start = len(magic) + 4 + idx_len
sizes = index["sizes"]
offsets = []
at = start
for s in sizes:
    offsets.append((at, s))
    at += s

files = [raw[off:off+s] for off, s in offsets]

entry_names = {}
for jar, entries in index["jars"].items():
    for name, num in entries:
        if num != -1:
            entry_names.setdefault(num, []).append(name)

str_replacements = {
    b"Arctic Client": b"Duckling Client",
    b"Arctic Launcher": b"Duckling Launcher",
    b"\xc2\xa7lArctic": b"\xc2\xa7lDuckling",
    b"Arctic servers": b"Duckling servers",
    b"Arctic disconnect": b"Duckling disconnect",
    b"Open Arctic Launcher": b"Open Duckling Launcher",
    b"Start the game from Arctic Launcher": b"Start the game from Duckling Launcher",
    b"No friends yet: add them in Arctic Launcher": b"No friends yet: add them in Duckling Launcher",
    b"Nobody else here uses Arctic voice yet.": b"Nobody else here uses Duckling voice yet.",
    b"They need the Arctic Client": b"They need the Duckling Client",
    b"\"Signed in\" must be yes: start the game from Arctic Launcher": b"\"Signed in\" must be yes: start the game from Duckling Launcher",
    b"Pick your look and emotes in Arctic Launcher": b"Pick your look and emotes in Duckling Launcher",
}

patched_count = 0
for i in range(len(files)):
    names = entry_names.get(i, [])
    # Check if icon
    if any(n.endswith("assets/arctic/icon.png") for n in names):
        files[i] = duck_icon_png
        patched_count += 1
        continue
    # Check if wordmark
    is_wordmark = False
    for w_idx in range(1, 9):
        if any(n.endswith(f"assets/arctic/wordmark-{w_idx}.png") for n in names):
            files[i] = wordmark_pngs[w_idx]
            patched_count += 1
            is_wordmark = True
            break
    if is_wordmark:
        continue
    # Check if fabric.mod.json
    if any(n.endswith("fabric.mod.json") for n in names):
        text = files[i].decode("utf-8", errors="ignore")
        text = text.replace("Arctic Client", "Duckling Client")
        text = text.replace("Arctic Launcher", "Duckling Launcher")
        text = text.replace("Arctic menus", "Duckling menus")
        text = text.replace("Arctic looks", "Duckling looks")
        text = text.replace("Arctic players", "Duckling players")
        files[i] = text.encode("utf-8")
        patched_count += 1
        continue
    # Check if class
    if any(n.endswith(".class") for n in names):
        is_btn = any("ArcticButton" in n for n in names)
        new_class, mod = patch_class(files[i], str_replacements, is_btn)
        if mod:
            files[i] = new_class
            patched_count += 1

print(f"Patched {patched_count} files in the pack!")

# Rebuild pack
new_sizes = [len(f) for f in files]
new_index_data = json.dumps({"jars": index["jars"], "sizes": new_sizes}, separators=(",", ":"), sort_keys=True).encode()
new_raw = magic + struct.pack("<I", len(new_index_data)) + new_index_data + b"".join(files)
new_packed = lzma.compress(new_raw, format=lzma.FORMAT_ALONE, preset=9 | lzma.PRESET_EXTREME)
pack_path.write_bytes(new_packed)
print(f"Repacked {pack_path}: {len(new_packed)} bytes")
