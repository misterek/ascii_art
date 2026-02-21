#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow"]
# ///
"""Image to colored ASCII using quadrant block characters for 2x2 resolution per cell."""

import argparse
import io
import os
import sys
import urllib.request
from PIL import Image

RESET = "\x1b[0m"

# Indexed by bitmask: bit3=TL, bit2=TR, bit1=BL, bit0=BR
# 1 = foreground color, 0 = background color
QUADRANTS = " \u2597\u2596\u2584\u259d\u2590\u259e\u259f\u2598\u259a\u258c\u2599\u2580\u259c\u259b\u2588"


def ansi_fg(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"


def ansi_bg(r, g, b):
    return f"\x1b[48;2;{r};{g};{b}m"


def load_image(source):
    if source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req).read()
        return Image.open(io.BytesIO(data)).convert("RGB")
    return Image.open(source).convert("RGB")


def dist_sq(c1, c2):
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2


def avg_color(colors):
    n = len(colors)
    return tuple(sum(c[i] for c in colors) // n for i in range(3))


def image_to_quadblock(source, width=120):
    img = load_image(source)

    # Each character cell covers a 2x2 pixel block
    px_w = width * 2
    aspect = img.height / img.width
    # Terminal cells are ~2:1 (tall:wide). Since we consume 2x2 pixels per cell,
    # horizontal and vertical scaling cancel, but we still need the cell aspect fix.
    px_h = int(px_w * aspect * 0.5)
    if px_h % 2:
        px_h += 1

    img = img.resize((px_w, px_h), Image.LANCZOS)
    px = img.load()

    lines = []
    for y in range(0, px_h, 2):
        chars = []
        for x in range(0, px_w, 2):
            # Gather 2x2 block: TL(bit3), TR(bit2), BL(bit1), BR(bit0)
            x1 = min(x + 1, px_w - 1)
            y1 = min(y + 1, px_h - 1)
            block = [px[x, y], px[x1, y], px[x, y1], px[x1, y1]]

            # Find the two most distant colors as cluster seeds
            max_d = -1
            si, sj = 0, 1
            for i in range(4):
                for j in range(i + 1, 4):
                    d = dist_sq(block[i], block[j])
                    if d > max_d:
                        max_d, si, sj = d, i, j

            if max_d < 100:
                # Nearly uniform — single color full block
                c = avg_color(block)
                chars.append(f"{ansi_fg(*c)}\u2588{RESET}")
                continue

            # Mini k-means: 2 iterations to settle centroids
            ca, cb = list(block[si]), list(block[sj])
            for _ in range(2):
                ga, gb = [], []
                for p in block:
                    (ga if dist_sq(p, ca) <= dist_sq(p, cb) else gb).append(p)
                if ga:
                    ca = list(avg_color(ga))
                if gb:
                    cb = list(avg_color(gb))

            # Build bitmask: 1 = cluster A (foreground)
            mask = 0
            for i, p in enumerate(block):
                if dist_sq(p, ca) <= dist_sq(p, cb):
                    mask |= 1 << (3 - i)

            if mask == 0b1111:
                chars.append(f"{ansi_fg(*ca)}\u2588{RESET}")
            elif mask == 0:
                chars.append(f"{ansi_fg(*cb)}\u2588{RESET}")
            else:
                chars.append(f"{ansi_fg(*ca)}{ansi_bg(*cb)}{QUADRANTS[mask]}{RESET}")

        lines.append("".join(chars))

    return "\n".join(lines)


def parse_width(spec):
    try:
        term_cols = os.get_terminal_size().columns
    except OSError:
        term_cols = 120
    if spec.endswith("%"):
        return max(1, int(term_cols * float(spec[:-1]) / 100))
    return int(spec)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Image to colored ASCII using quadrant block characters.")
    p.add_argument("images", nargs="+", help="Image file paths or URLs")
    p.add_argument("-w", "--width", default="100%",
                   help='Width: columns (e.g. "200") or percent of terminal (e.g. "50%%"). Default: 100%%')
    args = p.parse_args()

    width = parse_width(args.width)

    for path in args.images:
        if len(args.images) > 1:
            print(f"\n\x1b[1m--- {path} ---\x1b[0m\n")
        print(image_to_quadblock(path, width=width))
        if len(args.images) > 1:
            print()
