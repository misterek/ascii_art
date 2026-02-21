#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow"]
# ///
"""Image to colored ASCII using half-block characters for 2x vertical resolution."""

import argparse
import io
import os
import sys
import urllib.request
from PIL import Image

RESET = "\x1b[0m"


def fg(r: int, g: int, b: int) -> str:
    return f"\x1b[38;2;{r};{g};{b}m"


def bg(r: int, g: int, b: int) -> str:
    return f"\x1b[48;2;{r};{g};{b}m"


def load_image(source: str) -> Image.Image:
    if source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req).read()
        return Image.open(io.BytesIO(data)).convert("RGBA")
    return Image.open(source).convert("RGBA")


def image_to_halfblock(source: str, width: int = 120) -> str:
    img = load_image(source)

    # Resize: height must be even (we consume 2 rows per character row)
    aspect = img.height / img.width
    height = int(width * aspect)
    if height % 2 != 0:
        height += 1

    img = img.resize((width, height), Image.LANCZOS)

    lines = []
    for y in range(0, height, 2):
        chars = []
        for x in range(width):
            # Top pixel = foreground (▀), bottom pixel = background
            r1, g1, b1, a1 = img.getpixel((x, y))
            if y + 1 < height:
                r2, g2, b2, a2 = img.getpixel((x, y + 1))
            else:
                r2, g2, b2, a2 = 0, 0, 0, 0
            top = a1 > 30
            bot = a2 > 30
            if not top and not bot:
                chars.append(" ")
            elif top and bot:
                chars.append(f"{fg(r1, g1, b1)}{bg(r2, g2, b2)}\u2580{RESET}")
            elif top:
                chars.append(f"{fg(r1, g1, b1)}\u2580{RESET}")
            else:
                chars.append(f"{fg(r2, g2, b2)}\u2584{RESET}")
        lines.append("".join(chars))

    return "\n".join(lines)


def parse_width(spec: str) -> int:
    try:
        term_cols = os.get_terminal_size().columns
    except OSError:
        term_cols = 120
    if spec.endswith("%"):
        return max(1, int(term_cols * float(spec[:-1]) / 100))
    return int(spec)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Image to colored ASCII using half-block characters.")
    p.add_argument("images", nargs="+", help="Image file paths or URLs")
    p.add_argument("-w", "--width", default="100%", help='Width: columns (e.g. "200") or percent of terminal (e.g. "50%%"). Default: 100%%')
    args = p.parse_args()

    width = parse_width(args.width)

    for path in args.images:
        if len(args.images) > 1:
            print(f"\n\x1b[1m--- {path} ---\x1b[0m\n")
        print(image_to_halfblock(path, width=width))
        if len(args.images) > 1:
            print()
