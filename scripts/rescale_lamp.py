#!/usr/bin/env python3
"""Zmniejsza lampę na wygenerowanym zdjęciu do właściwej skali.

Potrzebne dwa obrazy z tego samego kadru: z lampą i bez lampy (ten sam pokój
po usunięciu lampy w Runway). Lampę wycinamy z różnicy obu obrazów
w zadanym obrysie i wklejamy pomniejszoną w miejscu zawieszenia.
Użyte 25.10.2026 dla Iris Eclipse 95 (salon, v06 -> v08); obrys i parametry
dobrane do tamtego kadru.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

with_lamp, empty, out_path = sys.argv[1:4]
a = Image.open(with_lamp).convert("RGB")
b = Image.open(empty).convert("RGB")
k = a.width / 800  # obrys zaznaczony na podglądzie 800 px

outline = Image.new("L", a.size, 0)
draw = ImageDraw.Draw(outline)
draw.ellipse([(381 * k, 91 * k), (419 * k, 111 * k)], fill=255)  # podsufitka
draw.rectangle([(396 * k, 108 * k), (404 * k, 206 * k)], fill=255)  # trzonek
draw.polygon([(x * k, y * k) for x, y in [(266, 203), (534, 203), (534, 250), (470, 300), (428, 338),
                                           (414, 374), (386, 374), (372, 338), (330, 300), (266, 250)]], fill=255)

diff = np.abs(np.asarray(a).astype(int) - np.asarray(b).astype(int)).sum(2)
alpha = np.clip((diff - 25) * 6, 0, 255).astype(np.uint8)
alpha = np.minimum(alpha, np.asarray(outline.filter(ImageFilter.GaussianBlur(2))))
mask = Image.fromarray(alpha).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))

ys, xs = np.nonzero(np.asarray(mask) > 40)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
lamp, mask = a.crop(box), mask.crop(box)

scale = 0.57
size = (int(lamp.width * scale), int(lamp.height * scale))
lamp, mask = lamp.resize(size, Image.LANCZOS), mask.resize(size, Image.LANCZOS)

# skracamy trzonek: podsufitka zostaje, korpus podnosimy
canopy_h, body_from = 32, 140
x, top = (box[0] + box[2]) // 2 - size[0] // 2, box[1]
out = b.copy()
out.paste(lamp.crop((0, 0, size[0], canopy_h)), (x, top), mask.crop((0, 0, size[0], canopy_h)))
out.paste(lamp.crop((0, body_from, *size)), (x, top + canopy_h), mask.crop((0, body_from, *size)))
out.save(out_path)
