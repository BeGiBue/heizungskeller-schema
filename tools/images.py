#!/usr/bin/env python3
"""Gerätebilder aus der Karte herausziehen bzw. wieder einbetten.

  python3 tools/images.py extract   -> assets/devices/<name>.webp (boiler, tank, gas, wm, soft)
  python3 tools/images.py embed     -> schreibt die WebP-Dateien aus assets/devices/ wieder in `const IMG`

Die Bilder sind als Data-URI in dist/heizungsanlage-card.js eingebettet (keine externen Dateien).
Beim Tauschen die Seitenverhältnisse beibehalten, da Positionen und Overlays (Flammenfenster, Speicherfenster)
auf den Bildproportionen beruhen. Benötigt: pip install pillow
"""
import base64
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(ROOT, "dist", "heizungsanlage-card.js")
DEV = os.path.join(ROOT, "assets", "devices")
BLOCK = re.compile(r"(const IMG = \{\n)(.*?)(\n\};)", re.S)
ENTRY = re.compile(r"  (\w+): \{ w: (\d+), h: (\d+), d: 'data:image/webp;base64,([^']*)' \},?")


def extract():
    s = open(CARD, encoding="utf8").read()
    m = BLOCK.search(s)
    os.makedirs(DEV, exist_ok=True)
    for e in ENTRY.finditer(m.group(2)):
        path = os.path.join(DEV, e.group(1) + ".webp")
        open(path, "wb").write(base64.b64decode(e.group(4)))
        print(f"{path}  {e.group(2)}x{e.group(3)}")


def embed():
    from PIL import Image

    s = open(CARD, encoding="utf8").read()
    m = BLOCK.search(s)
    order = [e.group(1) for e in ENTRY.finditer(m.group(2))]
    lines = []
    for key in order:
        path = os.path.join(DEV, key + ".webp")
        data = open(path, "rb").read()
        w, h = Image.open(io.BytesIO(data)).size
        lines.append(f"  {key}: {{ w: {w}, h: {h}, d: 'data:image/webp;base64,{base64.b64encode(data).decode()}' }},")
        print(f"{key}: {w}x{h}, {len(data)//1024} KB")
    s = s[: m.start(2)] + "\n".join(lines) + s[m.end(2):]
    open(CARD, "w", encoding="utf8").write(s)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "extract":
        extract()
    elif cmd == "embed":
        embed()
    else:
        print(__doc__)
        sys.exit(2)
