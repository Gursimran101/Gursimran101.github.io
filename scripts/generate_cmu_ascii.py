#!/usr/bin/env python3

import argparse
import html
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


COLS = 200
ROWS = 120
CELL_WIDTH = 0.6
CHAR_RAMP = "@B#9SGHMh352ir;:,. "


def line_points(x0, y0, x1, y1):
    steps = max(abs(x1 - x0), abs(y1 - y0)) + 1
    for x, y in zip(
        np.linspace(x0, x1, steps).round().astype(int),
        np.linspace(y0, y1, steps).round().astype(int),
    ):
        yield x, y


def set_cell(chars, colors, x, y, glyph, color):
    if 0 <= x < COLS and 0 <= y < ROWS:
        chars[y, x] = glyph
        colors[y, x] = color


def draw_line(chars, colors, start, end, glyph, color, thickness=1):
    for x, y in line_points(*start, *end):
        for offset in range(thickness):
            set_cell(chars, colors, x, y + offset, glyph, color)


def draw_arch(chars, colors, center_x, base_y, radius_x, radius_y, color, thickness=1):
    for angle in np.linspace(np.pi, 0, 180):
        x = int(round(center_x + radius_x * np.cos(angle)))
        y = int(round(base_y - radius_y * np.sin(angle)))
        glyph = "/" if x < center_x else "\\" if x > center_x else "^"
        for offset in range(thickness):
            set_cell(chars, colors, x, y + offset, glyph, color)


def semantic_color(rgb, x, y):
    r, g, b = [int(value) for value in rgb]
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    is_sky = y < 78 and b > r * 1.08 and b > g * 1.02
    is_green = g > r * 1.05 and g > b * 0.83
    is_roof = 43 <= y <= 72 and g >= r * 1.04 and g >= b * 0.82 and luminance < 0.58
    is_brick = r > g * 1.16 and r > b * 1.2 and 58 <= y <= 105

    is_side_facade = 62 <= y <= 106 and (x < 67 or x > 133)

    if is_roof:
        return "#274f46" if luminance < 0.34 else "#3a6254"
    if is_green:
        return "#476d35" if luminance < 0.45 else "#76914d"
    if is_sky:
        return "#436f98" if luminance < 0.64 else "#7199bd"
    if is_side_facade:
        return "#655f57" if luminance < 0.5 else "#8c8478"
    if is_brick:
        return "#74645b" if luminance < 0.5 else "#96877a"
    if luminance < 0.2:
        return "#202626"
    if luminance < 0.34:
        return "#494944"
    if luminance < 0.5:
        return "#6e685c"
    if luminance < 0.66:
        return "#918778"
    return "#a69b8c"


def reinforce_architecture(chars, colors):
    dark_green = "#214e44"
    roof_green = "#315f50"
    deep_shadow = "#252927"
    arch_shadow = "#594d43"
    arch_mid = "#817567"
    stone_light = "#a99d8c"
    stair_dark = "#5e544b"
    stair_light = "#897b6c"

    # Double green roof edge, including the low side eaves.
    draw_line(chars, colors, (42, 64), (100, 45), "/", dark_green, 2)
    draw_line(chars, colors, (100, 45), (169, 65), "\\", dark_green, 2)
    draw_line(chars, colors, (42, 66), (100, 47), "#", roof_green, 2)
    draw_line(chars, colors, (100, 47), (169, 67), "#", roof_green, 2)
    draw_line(chars, colors, (18, 69), (55, 69), "=", roof_green, 2)
    draw_line(chars, colors, (150, 69), (187, 69), "=", roof_green, 2)

    # Gable relief and layered stonework create depth above the entrance.
    draw_line(chars, colors, (54, 64), (100, 49), "/", stone_light)
    draw_line(chars, colors, (100, 49), (156, 65), "\\", stone_light)
    draw_line(chars, colors, (61, 66), (100, 53), "/", arch_mid)
    draw_line(chars, colors, (100, 53), (149, 67), "\\", arch_mid)
    for x in range(72, 136, 6):
        draw_line(chars, colors, (x, 62), (x, 70), "|", arch_shadow)

    # Nested entrance arches and a recessed doorway.
    draw_arch(chars, colors, 100, 84, 27, 21, arch_shadow, 2)
    draw_arch(chars, colors, 100, 84, 23, 18, arch_mid, 2)
    draw_arch(chars, colors, 100, 84, 19, 15, stone_light)
    for y in range(82, 103):
        for x in range(91, 110):
            set_cell(chars, colors, x, y, "@" if (x + y) % 3 else "#", deep_shadow)
    draw_line(chars, colors, (89, 82), (89, 103), "|", arch_shadow, 2)
    draw_line(chars, colors, (111, 82), (111, 103), "|", arch_shadow, 2)
    draw_line(chars, colors, (89, 82), (111, 82), "=", arch_mid, 2)
    draw_line(chars, colors, (94, 88), (94, 101), "|", stone_light)
    draw_line(chars, colors, (106, 88), (106, 101), "|", stone_light)

    # Front columns and panel shadows frame the central recess.
    for left, right in ((49, 66), (135, 152)):
        draw_line(chars, colors, (left, 70), (left, 102), "|", arch_shadow, 2)
        draw_line(chars, colors, (right, 70), (right, 102), "|", stone_light, 2)
        for x in range(left + 4, right - 2, 5):
            draw_line(chars, colors, (x, 73), (x, 99), ":", arch_mid)
        draw_line(chars, colors, (left - 2, 101), (right + 2, 101), "=", stair_dark, 2)

    # Layered stairs widen toward the foreground.
    for index, y in enumerate(range(103, 113, 2)):
        half_width = 19 + index * 5
        color = stair_light if index % 2 == 0 else stair_dark
        draw_line(chars, colors, (100 - half_width, y), (100 + half_width, y), "=", color, 2)
    draw_line(chars, colors, (99, 103), (99, 116), "|", deep_shadow)
    draw_line(chars, colors, (101, 103), (101, 116), "|", deep_shadow)


def make_ascii(source_path):
    image = ImageOps.exif_transpose(Image.open(source_path).convert("RGB"))
    image = ImageEnhance.Contrast(image).enhance(1.28)
    image = ImageEnhance.Color(image).enhance(1.18)
    image = ImageEnhance.Sharpness(image).enhance(2.2)
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    pixels = np.asarray(image)
    luminance = (
        0.2126 * pixels[:, :, 0]
        + 0.7152 * pixels[:, :, 1]
        + 0.0722 * pixels[:, :, 2]
    ) / 255
    blurred = np.asarray(
        Image.fromarray((luminance * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(radius=1.1)
        )
    ) / 255
    gradient_y, gradient_x = np.gradient(luminance)
    edge = np.hypot(gradient_x, gradient_y)
    edge /= max(np.percentile(edge, 97), 1e-6)
    edge = np.clip(edge, 0, 1)
    local_detail = np.clip(np.abs(luminance - blurred) * 4.5, 0, 1)

    darkness = np.clip(1 - luminance + edge * 0.42 + local_detail * 0.25, 0, 1)
    sky_mask = (
        (np.indices((ROWS, COLS))[0] < 78)
        & (pixels[:, :, 2] > pixels[:, :, 0] * 1.08)
        & (pixels[:, :, 2] > pixels[:, :, 1] * 1.02)
    )
    darkness[sky_mask] = np.maximum(darkness[sky_mask], 0.36 + edge[sky_mask] * 0.22)

    indices = np.rint((1 - darkness) * (len(CHAR_RAMP) - 1)).astype(int)
    chars = np.array([[CHAR_RAMP[index] for index in row] for row in indices], dtype="<U1")
    facade_rows = np.indices((ROWS, COLS))[0]
    chars[(chars == " ") & (facade_rows >= 60) & (facade_rows <= 108)] = "."
    colors = np.empty((ROWS, COLS), dtype=object)
    for y in range(ROWS):
        for x in range(COLS):
            colors[y, x] = semantic_color(pixels[y, x], x, y)

    reinforce_architecture(chars, colors)
    return chars, colors


def write_svg(chars, colors, output_path):
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-labelledby="title desc">',
        '  <title id="title">Carnegie Mellon architecture in colored ASCII characters</title>',
        '  <desc id="desc">The College of Fine Arts building with a green roofline, layered entrance arches, doorway, columns, stairs, lawn, and the Cathedral of Learning rendered as a detailed grid of text glyphs.</desc>',
        '  <g font-family="Courier New, Courier, monospace" font-size="1" font-weight="700" letter-spacing="0" style="font-variant-ligatures:none">',
    ]

    for y in range(ROWS):
        x = 0
        while x < COLS:
            if chars[y, x] == " ":
                x += 1
                continue
            start = x
            color = colors[y, x]
            run = []
            while x < COLS and chars[y, x] != " " and colors[y, x] == color:
                run.append(chars[y, x])
                x += 1
            text = html.escape("".join(run))
            lines.append(
                f'    <text x="{start * CELL_WIDTH:.1f}" y="{y + 0.85:.2f}" fill="{color}">{text}</text>'
            )
    lines.extend(["  </g>", "</svg>", ""])
    output_path.write_text("\n".join(lines), encoding="ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    chars, colors = make_ascii(args.source)
    write_svg(chars, colors, args.output)


if __name__ == "__main__":
    main()
