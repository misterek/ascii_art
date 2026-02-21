#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyfiglet"]
# ///
"""Text to ASCII Art Generator with 24-bit color."""

import argparse
import math
import sys

import pyfiglet

# ============================================================
# Color helpers — 24-bit true color
# ============================================================

RESET = "\x1b[0m"


def fg(r: int, g: int, b: int) -> str:
    return f"\x1b[38;2;{r};{g};{b}m"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    h = h % 360
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return round((r + m) * 255), round((g + m) * 255), round((b + m) * 255)


def lerp_rgb(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


def multi_stop_lerp(
    colors: list[tuple[int, int, int]], t: float
) -> tuple[int, int, int]:
    if len(colors) == 1:
        return colors[0]
    t = max(0.0, min(1.0, t))
    segment = t * (len(colors) - 1)
    i = min(int(segment), len(colors) - 2)
    local = segment - i
    return lerp_rgb(colors[i], colors[i + 1], local)


# ============================================================
# Gradient engine
# ============================================================


def apply_gradient(
    text: str, colors: list[tuple[int, int, int]], direction: str
) -> str:
    lines = text.split("\n")
    rows = len(lines)
    cols = max((len(l) for l in lines), default=1) or 1
    out = []
    for row, line in enumerate(lines):
        chars = []
        for col, ch in enumerate(line):
            if ch == " ":
                chars.append(ch)
                continue
            if direction == "h":
                t = col / (cols - 1) if cols > 1 else 0
            elif direction == "v":
                t = row / (rows - 1) if rows > 1 else 0
            elif direction == "d":
                denom = cols + rows - 2
                t = (row + col) / denom if denom > 0 else 0
            elif direction == "r":
                cx, cy = (cols - 1) / 2, (rows - 1) / 2
                max_r = math.sqrt(cx * cx + cy * cy) or 1
                t = math.sqrt((col - cx) ** 2 + (row - cy) ** 2) / max_r
            else:
                t = col / (cols - 1) if cols > 1 else 0
            r, g, b = multi_stop_lerp(colors, t)
            chars.append(f"{fg(r, g, b)}{ch}{RESET}")
        out.append("".join(chars))
    return "\n".join(out)


# ============================================================
# Presets
# ============================================================

_rainbow36 = [hsl_to_rgb(i * 10, 1, 0.5) for i in range(36)]

PRESETS: dict[str, dict] = {
    "rainbow": {"colors": _rainbow36, "dir": "h"},
    "vrainbow": {"colors": _rainbow36, "dir": "v"},
    "drainbow": {"colors": _rainbow36, "dir": "d"},
    "fire": {
        "colors": [hex_to_rgb(c) for c in ["#3b0a00", "#8b1a00", "#cc3300", "#ff6600", "#ffaa00", "#ffdd44", "#ffffcc"]],
        "dir": "v",
    },
    "ice": {
        "colors": [hex_to_rgb(c) for c in ["#000033", "#0033aa", "#0088cc", "#00ccff", "#aaeeff", "#eeffff"]],
        "dir": "v",
    },
    "ocean": {
        "colors": [hex_to_rgb(c) for c in ["#001133", "#003366", "#006688", "#0099aa", "#22bbaa", "#66ddcc", "#aaffee"]],
        "dir": "d",
    },
    "sunset": {
        "colors": [hex_to_rgb(c) for c in ["#2d1b69", "#8b2fc9", "#d94f8e", "#f47a5b", "#f9a836", "#fdd835"]],
        "dir": "h",
    },
    "synthwave": {
        "colors": [hex_to_rgb(c) for c in ["#ff00ff", "#cc00ff", "#7700ff", "#3300ff", "#0044ff", "#00bbff", "#00ffff"]],
        "dir": "h",
    },
    "matrix": {
        "colors": [hex_to_rgb(c) for c in ["#001100", "#003300", "#006600", "#00aa00", "#00dd00", "#00ff00", "#aaffaa"]],
        "dir": "v",
    },
    "lava": {
        "colors": [hex_to_rgb(c) for c in ["#330000", "#881100", "#cc4400", "#ff8800", "#ffcc00", "#ff8800", "#cc4400", "#881100", "#330000"]],
        "dir": "r",
    },
    "pastel": {
        "colors": [hex_to_rgb(c) for c in ["#ffb3ba", "#ffdfba", "#ffffba", "#baffc9", "#bae1ff", "#d4baff"]],
        "dir": "h",
    },
    "neon": {
        "colors": [hex_to_rgb(c) for c in ["#ff0099", "#ff00ff", "#9900ff", "#0033ff", "#00ccff", "#00ff66"]],
        "dir": "h",
    },
    "gold": {
        "colors": [hex_to_rgb(c) for c in ["#5c4a00", "#8b7300", "#bfa200", "#e6c300", "#ffd700", "#ffe44d", "#fff5b3"]],
        "dir": "d",
    },
    "cyber": {
        "colors": [hex_to_rgb(c) for c in ["#39ff14", "#00ff88", "#00ffcc", "#00ccff", "#0088ff", "#7744ff", "#aa00ff"]],
        "dir": "h",
    },
    "autumn": {
        "colors": [hex_to_rgb(c) for c in ["#8B4513", "#D2691E", "#FF8C00", "#FF6347", "#DC143C", "#8B0000"]],
        "dir": "h",
    },
    "candy": {
        "colors": [hex_to_rgb(c) for c in ["#ff99cc", "#ff88dd", "#dd88ff", "#bb99ff", "#99bbff", "#88ddff"]],
        "dir": "h",
    },
    "toxic": {
        "colors": [hex_to_rgb(c) for c in ["#2a0033", "#440066", "#336600", "#66cc00", "#99ff00", "#ccff66"]],
        "dir": "v",
    },
    "frozen": {
        "colors": [hex_to_rgb(c) for c in ["#e0f7ff", "#80d4ff", "#40b0ff", "#0088dd", "#40b0ff", "#80d4ff", "#e0f7ff"]],
        "dir": "h",
    },
}

BASIC_COLORS = {
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "white": "\x1b[37m",
}


# ============================================================
# Per-letter coloring
# ============================================================


def _parse_letter_color(spec: str) -> dict:
    """Parse a single letter's color spec into a structured form for per-char coloring."""
    direction = "h"
    has_dir = False
    if len(spec) > 2 and spec[1] == ":" and spec[0] in "hvdr":
        direction = spec[0]
        spec = spec[2:]
        has_dir = True

    if spec in BASIC_COLORS:
        ansi_rgb = {
            "red": (255, 0, 0), "green": (0, 255, 0), "yellow": (255, 255, 0),
            "blue": (0, 0, 255), "magenta": (255, 0, 255), "cyan": (0, 255, 255),
            "white": (255, 255, 255),
        }
        return {"type": "solid", "rgb": ansi_rgb[spec]}

    if spec in PRESETS:
        preset = PRESETS[spec]
        d = direction if has_dir else preset["dir"]
        return {"type": "gradient", "colors": preset["colors"], "dir": d}

    import re

    if re.match(r"^#[0-9a-fA-F]{3,6}$", spec):
        return {"type": "solid", "rgb": hex_to_rgb(spec)}

    if "-" in spec and "#" in spec:
        stops = [hex_to_rgb(s.strip()) for s in spec.split("-")]
        return {"type": "gradient", "colors": stops, "dir": direction}

    return {"type": "solid", "rgb": (255, 255, 255)}


def _resolve_letter_color(
    lc: dict, row: int, local_col: int, total_rows: int, letter_cols: int
) -> tuple[int, int, int]:
    """Get RGB for a character at (row, local_col) within a letter's column span."""
    if lc["type"] == "solid":
        return lc["rgb"]

    colors = lc["colors"]
    direction = lc["dir"]

    if direction == "h":
        t = local_col / (letter_cols - 1) if letter_cols > 1 else 0
    elif direction == "v":
        t = row / (total_rows - 1) if total_rows > 1 else 0
    elif direction == "d":
        denom = letter_cols + total_rows - 2
        t = (row + local_col) / denom if denom > 0 else 0
    elif direction == "r":
        cx = (letter_cols - 1) / 2
        cy = (total_rows - 1) / 2
        max_r = math.sqrt(cx * cx + cy * cy) or 1
        t = math.sqrt((local_col - cx) ** 2 + (row - cy) ** 2) / max_r
    else:
        t = local_col / (letter_cols - 1) if letter_cols > 1 else 0

    return multi_stop_lerp(colors, t)


def apply_per_letter(
    rendered: str, input_text: str, specs_str: str, font: str, width: int
) -> str:
    """Color each input character's figlet columns with its own color spec."""
    specs_raw = [s.strip() for s in specs_str.split(",")]
    letter_colors = [_parse_letter_color(s) for s in specs_raw]

    # Compute column boundaries via progressive rendering
    boundaries = [0]
    for i in range(1, len(input_text) + 1):
        r = pyfiglet.figlet_format(input_text[:i], font=font, width=width)
        max_w = max((len(line) for line in r.rstrip("\n").split("\n")), default=0)
        boundaries.append(max_w)

    lines = rendered.split("\n")
    rows = len(lines)
    out = []

    for row, line in enumerate(lines):
        chars = []
        for col, ch in enumerate(line):
            if ch == " ":
                chars.append(ch)
                continue
            # Find which input letter this column belongs to
            letter_idx = len(boundaries) - 2
            for i in range(len(boundaries) - 1):
                if col < boundaries[i + 1]:
                    letter_idx = i
                    break
            lc = letter_colors[letter_idx % len(letter_colors)]
            start_col = boundaries[letter_idx]
            end_col = boundaries[min(letter_idx + 1, len(boundaries) - 1)]
            letter_w = end_col - start_col
            r, g, b = _resolve_letter_color(lc, row, col - start_col, rows, letter_w)
            chars.append(f"{fg(r, g, b)}{ch}{RESET}")
        out.append("".join(chars))

    return "\n".join(out)


# ============================================================
# Parse color spec into a callable
# ============================================================


def parse_color_spec(spec: str):
    if not spec or spec == "none":
        return lambda t: t

    # Per-letter coloring
    if spec.startswith("letter:"):
        return {"type": "letter", "specs": spec[7:]}

    # Direction prefix: h:, v:, d:, r:
    direction = "h"
    has_dir = False
    if len(spec) > 2 and spec[1] == ":" and spec[0] in "hvdr":
        direction = spec[0]
        spec = spec[2:]
        has_dir = True

    # Basic ANSI
    if spec in BASIC_COLORS:
        code = BASIC_COLORS[spec]
        return lambda t, c=code: f"{c}{t}{RESET}"

    # Preset
    if spec in PRESETS:
        preset = PRESETS[spec]
        d = direction if has_dir else preset["dir"]
        return lambda t, p=preset, dd=d: apply_gradient(t, p["colors"], dd)

    # Single hex
    import re

    if re.match(r"^#[0-9a-fA-F]{3,6}$", spec):
        r, g, b = hex_to_rgb(spec)
        return lambda t, r=r, g=g, b=b: f"{fg(r, g, b)}{t}{RESET}"

    # Hex gradient: #aaa-#bbb-#ccc
    if "-" in spec and "#" in spec:
        stops = [hex_to_rgb(s.strip()) for s in spec.split("-")]
        return lambda t, s=stops, d=direction: apply_gradient(t, s, d)

    print(f'Unknown color: "{spec}". Use --colors to list options.', file=sys.stderr)
    return lambda t: t


# ============================================================
# Font name normalization — pyfiglet uses underscores, TAAG uses spaces
# ============================================================


def normalize_font(name: str) -> str:
    """Try the name as-is first, then with spaces→underscores."""
    fonts = pyfiglet.FigletFont.getFonts()
    if name in fonts:
        return name
    alt = name.replace(" ", "_").lower()
    if alt in fonts:
        return alt
    # Fuzzy fallback — try case-insensitive
    lower = name.lower().replace(" ", "_")
    for f in fonts:
        if f.lower() == lower:
            return f
    return name  # let pyfiglet raise


# ============================================================
# --colors preview
# ============================================================


def show_colors():
    print("\x1b[1m--- Basic ANSI colors ---\x1b[0m\n")
    for name, code in BASIC_COLORS.items():
        print(f"  {code}{name}{RESET}")

    print(f"\n\x1b[1m--- Gradient presets (24-bit true color) ---\x1b[0m\n")
    sample = pyfiglet.figlet_format("Abc", font="standard").rstrip("\n")
    for name, preset in PRESETS.items():
        swatch = "".join(
            f"{fg(*multi_stop_lerp(preset['colors'], i / 39))}\u2588{RESET}"
            for i in range(40)
        )
        print(f"  \x1b[1m{name}\x1b[0m  {swatch}")
        colored = apply_gradient(sample, preset["colors"], preset["dir"])
        for line in colored.split("\n"):
            print(f"  {line}")
        print()

    print("\x1b[1m--- Custom gradients ---\x1b[0m\n")
    print('  Use hex colors:  -c "#ff0000-#0000ff"')
    print('  Multi-stop:      -c "#ff0000-#ffff00-#00ff00-#0000ff"')
    print('  With direction:  -c "v:#ff0000-#0000ff"   (v/h/d/r)')
    print('  Single color:    -c "#ff6600"')
    print()

    print("\x1b[1m--- Per-letter coloring ---\x1b[0m\n")
    print('  Each input character gets its own color (cycles if fewer colors than letters).')
    print('  Solid colors:    -c "letter:#ff0000,#00ff00,#0000ff"')
    print('  Named colors:    -c "letter:red,green,blue,yellow"')
    print('  Gradient presets:-c "letter:fire,ice,synthwave"')
    print('  Mix and match:   -c "letter:#ff0000,ocean,cyan"')
    print()


# ============================================================
# Main
# ============================================================

LAYOUT_CHOICES = {
    "0": "default",
    "1": "full",
    "2": "fitted",
    "3": "controlled smushing",
    "4": "universal smushing",
}


def main():
    p = argparse.ArgumentParser(
        description="Text to ASCII Art Generator — with 24-bit true color gradients.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Color specs:
  Basic:      red, green, yellow, blue, magenta, cyan, white
  Hex:        "#ff6600"
  Gradient:   "#ff0000-#0000ff"               (horizontal, 2+ stops)
  Multi-stop: "#ff0000-#ffff00-#00ff00"
  Direction:  "v:#ff0000-#0000ff"             (v/h/d/r)
  Presets:    fire, ice, ocean, sunset, synthwave, matrix, lava, neon,
              gold, cyber, autumn, candy, toxic, frozen, pastel,
              rainbow, vrainbow, drainbow
  Override:   "d:fire", "h:matrix"
  Per-letter: "letter:red,green,blue"         (one color per character, cycles)
              "letter:fire,ice,ocean"          (gradient presets per character)
              "letter:#ff0000,#00ff00,#0000ff" (hex colors per character)

Examples:
  %(prog)s "Hello World"
  %(prog)s -f "ANSI Shadow" -c rainbow "Thanos"
  %(prog)s -c fire "BURN"
  %(prog)s -c "d:#ff00ff-#00ffff" "Gradient"
  %(prog)s -c "letter:#ff0000,#00ff00,#0000ff" "RGB"
  %(prog)s -c "letter:fire,ice,ocean" "HOT"
""",
    )
    p.add_argument("text", nargs="*", help="Text to render")
    p.add_argument("-f", "--font", default="ANSI Shadow", help='Font name (default: "ANSI Shadow")')
    p.add_argument("-c", "--color", default="none", help="Color spec")
    p.add_argument("--hlayout", default="default", help="Horizontal layout (default/full/fitted/0-4)")
    p.add_argument("--vlayout", default="default", help="Vertical layout (default/full/fitted/0-4)")
    p.add_argument("-w", "--width", type=int, default=80, help="Max width (default: 80)")
    p.add_argument("-l", "--list", action="store_true", dest="list_fonts", help="List all fonts")
    p.add_argument("--colors", action="store_true", help="Show all colors with previews")
    p.add_argument("-t", "--test-all", action="store_true", help="Render text in every font")

    args = p.parse_args()

    if args.list_fonts:
        fonts = sorted(pyfiglet.FigletFont.getFonts())
        print(f"{len(fonts)} fonts available:\n")
        for f in fonts:
            print(f"  {f}")
        return

    if args.colors:
        show_colors()
        return

    text = " ".join(args.text) if args.text else None
    if not text:
        p.print_help()
        sys.exit(1)

    hlayout = LAYOUT_CHOICES.get(args.hlayout, args.hlayout)
    vlayout = LAYOUT_CHOICES.get(args.vlayout, args.vlayout)
    font = normalize_font(args.font)
    colorize = parse_color_spec(args.color)

    if args.test_all:
        for f in sorted(pyfiglet.FigletFont.getFonts()):
            try:
                result = pyfiglet.figlet_format(text, font=f, width=args.width).rstrip("\n")
                print(f"\x1b[1m--- {f} ---\x1b[0m")
                if isinstance(colorize, dict) and colorize.get("type") == "letter":
                    print(apply_per_letter(result, text, colorize["specs"], f, args.width))
                else:
                    print(colorize(result))
                print()
            except Exception:
                pass
        return

    try:
        result = pyfiglet.figlet_format(text, font=font, width=args.width).rstrip("\n")
        if isinstance(colorize, dict) and colorize.get("type") == "letter":
            print(apply_per_letter(result, text, colorize["specs"], font, args.width))
        else:
            print(colorize(result))
    except pyfiglet.FontNotFound:
        print(f'Error: Font "{args.font}" not found.', file=sys.stderr)
        fonts = pyfiglet.FigletFont.getFonts()
        lower = args.font.lower().replace(" ", "_")
        similar = [f for f in fonts if lower in f.lower()]
        if similar:
            print("\nDid you mean one of these?", file=sys.stderr)
            for f in similar:
                print(f"  {f}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
