# Gursimran Singh Panesar

Minimal personal site for GitHub Pages. The site uses plain HTML and CSS with
serif text, native-style links, and a light dotted-paper background. Content
sits against the left edge of the page rather than in a centred column; the
experience page uses a wider column to make room for its logo gutter. On wide
screens the home page places the artwork to the right of the text, centred
about three quarters of the way across the page.

## Archived Artwork

These standalone assets are retained but are not referenced or loaded by the site:

```text
assets/golden-gate-ascii.svg
assets/cmu-ascii.svg
assets/statement/golden-gate-ascii.svg
assets/statement/golden-gate-converter-ascii.svg
assets/statement/golden-gate-aic.svg
assets/statement/golden-gate-aic-light.svg
assets/statement/bridge-denim-grain.png
assets/statement/golden-gate-field-notes.jpg
```

The home page shows two risograph-style halftone prints of the bridge:
`assets/statement/golden-gate-riso-light.webp` (the north tower in daytime
mist) in light mode and `assets/statement/golden-gate-riso-dark.webp` (the lit
bridge at night) in dark mode. Both are stacked in the page and cross-fade when
the colour scheme changes while the page is open; the fade is disabled for
visitors who prefer reduced motion. The field-notes poster described below,
the dithered denim rendering, and the earlier theme-specific
`ascii-image-converter` grids listed above, their plain character output at
`assets/statement/golden-gate-aic.txt` and
`assets/statement/golden-gate-aic-light.txt`, and the source photograph
`assets/source/bridge.jpg` are retained but not loaded by the page.

## Field Notes Poster

`assets/statement/golden-gate-field-notes.jpg` is a rubber-stamp travel
field-notes poster: a misty photo of the bridge on the left and, on warm aged
paper to the right, a small three-colour rubber stamp of the scene with a
typewriter caption. `scripts/generate_field_notes.py` generates it from
`assets/source/golden-gate-misty.jpg` (photo by Daryl Elliott via Unsplash,
CC0, from Wikimedia Commons). Regenerate with:

```text
python3 scripts/generate_field_notes.py \
  --source assets/source/golden-gate-misty.jpg \
  --out assets/statement/golden-gate-field-notes.jpg --out-width 1800
```

The script needs Pillow, NumPy, and SciPy, and uses the macOS American
Typewriter font. Drop `--out-width` and use a `.png` name for a full-size
2400x1800 master.

## Local Preview

Open `index.html` in a browser.

## GitHub Pages

For a root user site, the repository must be named exactly:

```text
Gursimran101.github.io
```

That publishes at:

```text
https://gursimran101.github.io/
```

The name `gursimran.github.io` would require control of the GitHub user or organization
named `gursimran`.
