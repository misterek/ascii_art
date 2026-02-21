# ascii_art

Terminal ASCII art tools with 24-bit true color support.

# Caution 
Everything here was written by Claude, with little to no review from me (both the readme and the actual scripts)

I think it works fine, but user beware.

Also, for the love of all that's holy, running it directly from github is super easy, and I don't plan to change this or do anything bad,
but if you're going to run it directly from here, **use the sha in the URL**.


## Run directly from GitHub

These are standalone [uv scripts](https://docs.astral.sh/uv/guides/scripts/) — no install needed. uv will fetch dependencies automatically.

```bash
# Text to ASCII art
uv run https://raw.githubusercontent.com/misterek/ascii_art/<SHA>/ascii_art.py "Hello World" -c rainbow

# Image to ASCII (half-block)
uv run https://raw.githubusercontent.com/misterek/ascii_art/<SHA>/img2ascii.py photo.png

# Image to ASCII (quadrant-block, higher detail)
uv run https://raw.githubusercontent.com/misterek/ascii_art/<SHA>/img2ascii_2x.py photo.png
```

> **Caution:** Always pin to a specific commit SHA rather than a branch name like `main`. This ensures the code you run doesn't change out from under you. Find the latest commit SHA on the [commits page](https://github.com/misterek/ascii_art/commits/main) and replace `<SHA>` above.
>
> For example, using commit `3f7c687`:
> ```bash
> uv run https://raw.githubusercontent.com/misterek/ascii_art/3f7c687/ascii_art.py "Hello" -c fire
> ```

## Scripts

### ascii_art.py

Text to ASCII art using [pyfiglet](https://github.com/pwaller/pyfiglet) with 24-bit color gradients.

```bash
./ascii_art.py "Hello World"                       # default font
./ascii_art.py -f standard -c rainbow "Colorful"   # pick a font + color
./ascii_art.py -c fire "BURN"                      # gradient preset
./ascii_art.py -c "v:#ff00ff-#00ffff" "Gradient"   # custom gradient with direction
./ascii_art.py -c "letter:red,green,blue" "RGB"    # per-letter coloring
./ascii_art.py --colors                            # show all color presets
./ascii_art.py -l                                  # list all fonts
./ascii_art.py -t "Test"                           # preview text in every font
```

**Color options:**

| Syntax | Example | Description |
|---|---|---|
| Named | `-c red` | Basic ANSI color |
| Hex | `-c "#ff6600"` | Single 24-bit color |
| Gradient | `-c "#ff0000-#0000ff"` | Multi-stop gradient |
| Direction | `-c "v:#ff0000-#0000ff"` | `h`orizontal, `v`ertical, `d`iagonal, `r`adial |
| Preset | `-c fire` | Built-in gradient preset |
| Per-letter | `-c "letter:fire,ice,ocean"` | Different color per character |

**Presets:** rainbow, fire, ice, ocean, sunset, synthwave, matrix, lava, neon, gold, cyber, autumn, candy, toxic, frozen, pastel

### img2ascii.py

Image to colored ASCII using Unicode half-block characters (`▀▄`), giving 2x vertical resolution.

```bash
./img2ascii.py photo.png
./img2ascii.py -w 80 photo.png          # set width in columns
./img2ascii.py -w 50% photo.png         # percentage of terminal width
./img2ascii.py https://example.com/image.png  # works with URLs
```

### img2ascii_2x.py

Image to colored ASCII using Unicode quadrant block characters (`▘▝▖▗▚▞` etc.), giving 2x2 resolution per cell — noticeably sharper than half-block.

```bash
./img2ascii_2x.py photo.png
./img2ascii_2x.py -w 80 photo.png
./img2ascii_2x.py -w 50% photo.png
```

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (handles dependencies automatically)
- A terminal with 24-bit true color and Unicode support
