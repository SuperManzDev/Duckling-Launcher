# Cosmetics server content

Everything here is loaded and checked when the server starts. A broken file
stops the server with a message naming it, so mistakes never reach players.

## Capes

`catalog.json` lists preset capes; each has `capes/<id>.png`. HD frames can be
up to 1024×512. Animated capes stack up to 32 frames vertically (strip height
at most 12,288 pixels), and each PNG must stay under 2 MiB. Every frame needs
its own cape and elytra art; animated presets can also have `<id>-still.png`.
The three Loading capes (`loading_circle`, `loading_text`, `loading_both`)
each use a 32-frame, 16 fps strip plus a painted still for the Animate toggle.
The generator is `tools/make_loading_capes.py`; see the
[visual review](../../../docs/requests/cape-art-pack/loading-capes/index.html).

## Skin gallery

`gallery.json` lists the 112 curated Arctic skins in `gallery/`. Each seed has
`file`, `name`, `model` (`classic` or `slim`), and `category`. The six curated
collections are `adventure`, `fantasy`, `gamer`, `animals`, `pvp`, and `casual`.
Player-shared skins enter `community` after moderation. The launcher browses
and searches these collections with server-side paging. Changing a seed's
category or repainting its PNG updates existing installations without resetting
its downloads. Keep each seed's file name stable: new gallery IDs use that file
stem, and older texture-derived IDs are retained during upgrades. Older
duplicate Arctic seeds with the same name are merged when the server starts.

## 3D cosmetics (Blockbench)

1. In Blockbench, create a **Bedrock Entity** model. Start from the player
   template (File → New → Bedrock Entity, then add the player's bones) or
   make your own bones.
2. Name each **root bone** after the player part it follows: `head`,
   `body`, `rightArm`, `leftArm`, `rightLeg` or `leftLeg` (anything else
   follows the body). Put your cubes in those bones or in child bones.
   Use the player template's pivots (head and body `0,24,0`) so the item
   lines up with the player.
3. Use box UV or per-face UV; both are supported.
4. Paint the texture; its sides must be powers of two, up to 1024.
5. Export: File → Export → Bedrock Geometry, and save the texture.
6. Optional idle motion (wings flapping, a tail swaying): Animate tab,
   make one looping animation of your bones, File → Export → Bedrock
   Animations. Rotation and position keyframes are used, blended linearly
   (expressions count as 0).
7. Put the files here and add an entry to `cosmetics.json`:

```
cosmetics/<id>.geo.json
cosmetics/<id>.png
cosmetics/<id>.animation.json   (optional)
```

```json
{ "id": "frost_wings", "name": "Frost Wings", "slot": "back" }
```

`id`: 1–32 of `a-z 0-9 _ -`. `slot`: `head`, `face`, `back`, `body` or
`shoulders`; a player wears one item per slot.

Limits: 128 bones, 512 cubes, coordinates within ±256, JSON files up to 512 KB.

The sculpted Frost Wings, Dragon Wings, Clockwork Wings, Star Sail, Pocket Penguin, Snow Owl, Tiny Fox, Halo, Crown, Party Hat, Ice Crown, Crystal Pendant, Copper Belt and Explorer Sash GLBs override their older cuboid
versions on mesh-capable clients; the cuboid files remain as fallbacks. Review major cosmetics from
back, front and both sides using `tools/preview_cosmetic.py` for cuboids and
the [multi-angle catalog audit](../../../docs/requests/cosmetic-art-pack/quality-audit.md)
before publishing. Software previews do not replace an in-game attachment check.

Brass Quiver, Honeybee Buddy, Fox Festival Mask, Prism Bracers, and Alchemist
Bandolier are new mesh-only pieces. They are listed only to mesh-capable clients;
see their [five-angle review](../../../docs/requests/cosmetic-art-pack/README.md).

## Emotes (Blockbench)

1. Open the player template as a Bedrock Entity (bone names `head`, `body`,
   `rightArm`, `leftArm`, `rightLeg`, `leftLeg`).
2. Animate tab: one animation, up to 15 seconds. Rotations replace the
   walking pose of the bones you animate; positions add to them.
   Set it to loop for emotes that last until the player moves.
   The expressive rig also accepts root, pelvis, chest, forearm, and shin
   tracks for authored motions; see [the emote format guide](../../../docs/content-guide.md).
3. File → Export → Bedrock Animations as `emotes/<id>.animation.json`, and
   add `{ "id": "wave", "name": "Wave" }` to `emotes.json`.

Players open the emote wheel with **B** (changeable in the Arctic menu,
Looks → Emotes). Moving stops an emote.
