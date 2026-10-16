#!/usr/bin/env bash
# Build the macOS downloads from the Apple Silicon and Intel release builds
# (run on a Mac, after `cargo build --release --target aarch64-apple-darwin`
# and `--target x86_64-apple-darwin` for arctic-app and arctic-cli):
#
#   dist/duckling-launcher-macos.zip   Duckling Launcher.app (what people download)
#   dist/duckling-launcher-macos       the launcher program alone (what updates replace)
#   dist/duckling-macos                the command line tool
#
# Everything is universal (both kinds of Mac) and ad-hoc signed; without a
# paid Apple Developer ID, macOS asks once before opening it.
#
# Usage: packaging/macos/make-app.sh <version>
set -euo pipefail

VERSION="${1:?version, like 0.2.0}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$ROOT/dist"
APP="$OUT/Duckling Launcher.app"
ARM="$ROOT/target/aarch64-apple-darwin/release"
INTEL="$ROOT/target/x86_64-apple-darwin/release"

mkdir -p "$OUT"
rm -rf "$APP"
lipo -create "$ARM/duckling-launcher" "$INTEL/duckling-launcher" -output "$OUT/duckling-launcher-macos"
lipo -create "$ARM/duckling" "$INTEL/duckling" -output "$OUT/duckling-macos"
codesign --force --sign - "$OUT/duckling-launcher-macos"
codesign --force --sign - "$OUT/duckling-macos"

mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$OUT/duckling-launcher-macos" "$APP/Contents/MacOS/duckling-launcher"
sed "s/@VERSION@/$VERSION/g" "$HERE/Info.plist" > "$APP/Contents/Info.plist"

# The icon, drawn by the launcher itself at every size macOS wants.
ICONSET="$(mktemp -d)/AppIcon.iconset"
mkdir -p "$ICONSET"
for size in 16 32 128 256 512; do
  "$OUT/duckling-launcher-macos" --write-icon "$ICONSET/icon_${size}x${size}.png" "$size"
  "$OUT/duckling-launcher-macos" --write-icon "$ICONSET/icon_${size}x${size}@2x.png" "$((size * 2))"
done
iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/AppIcon.icns"

codesign --force --deep --sign - "$APP"
(cd "$OUT" && rm -f duckling-launcher-macos.zip && ditto -c -k --keepParent "Duckling Launcher.app" duckling-launcher-macos.zip)
echo "Built $OUT/duckling-launcher-macos.zip"
